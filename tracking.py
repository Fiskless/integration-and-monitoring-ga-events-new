import requests
import httplib2
import apiclient.discovery
import rollbar
import sys

from contextlib import suppress
from environs import Env
from oauth2client.service_account import ServiceAccountCredentials


TG_ACCOUNT_COLUMN_INDEX = 0
GA4_COLUMN_INDEX = 25
GA4_COLUMN_SYMBOL = 'Z'
GAU_COLUMN_INDEX = 26
GAU_COLUMN_SYMBOL = 'AA'
SESSION_ID_COLUMN_INDEX = 27


def create_event_to_ga4(session_id, api_secret, measurement_id):

    payload = {
        'client_id': session_id,
        'events': [
            {
                'name': 'freeweek_login',
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    }

    params = {
        'measurement_id': measurement_id,
        'api_secret': api_secret
    }

    response = requests.post('https://www.google-analytics.com/mp/collect',
                             headers=headers,
                             params=params,
                             json=payload)

    response.raise_for_status()

    return response


def create_event_to_gau(tid, session_id):

    payload = {
        'v': '1',
        't': 'event',
        'tid': tid,
        'cid': session_id,
        'ec': 'course',
        'ea': 'freeweek',
        'el': 'signup',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }

    response = requests.post('https://www.google-analytics.com/collect',
                             headers=headers,
                             data=payload)

    response.raise_for_status()

    return response


def collect_data_to_update_table(credentials_file,
                                 spreadsheet_id,
                                 platform_name,
                                 ga_column_number,
                                 ga_column_symbol,
                                 api_secret = None,
                                 measurement_id = None,
                                 tid = None):

    row_number_to_session_id, _ = get_session_ids_to_create_event(
        credentials_file,
        spreadsheet_id,
        ga_column_number,
        ga_column_symbol
    )
    row_numbers_for_updating_table = row_number_to_session_id.keys()

    unsuccessful_requests = []

    for row_number, session_id in row_number_to_session_id.items():
        if platform_name == "GA4":
            response = create_event_to_ga4(session_id, api_secret, measurement_id)
        elif platform_name == "GAU":
            response = create_event_to_gau(tid, session_id)
        if not response.ok:
            unsuccessful_requests.append(
                {"range": f"{ga_column_symbol}{row_number}",
                 "values": [['Ошибка при создании события, обратитесь к программисту']]
                 }
            )
    return unsuccessful_requests, row_numbers_for_updating_table


def connect_to_sheets_api(credentials_file):

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    return service


def get_sheet_data(service, spreadsheet_id):
    row_values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='A2:AB',
        majorDimension='ROWS'
    ).execute()
    return row_values['values']


def update_sheet_data(service, spreadsheet_id, body):
    return service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body,
    ).execute()


def get_session_ids_to_create_event(credentials_file, spreadsheet_id,
                                    ga_column_number, ga_column_symbol):
    service = connect_to_sheets_api(credentials_file)
    row_values = get_sheet_data(service, spreadsheet_id)
    row_number_to_session_id = {}
    updating_rows_without_yes_values = []
    for row_number, students_data in enumerate(row_values, start=2):
        with suppress(IndexError):
            if students_data[TG_ACCOUNT_COLUMN_INDEX] and students_data[SESSION_ID_COLUMN_INDEX]:
                if students_data[ga_column_number] == 'нет':
                    row_number_to_session_id[row_number] = students_data[SESSION_ID_COLUMN_INDEX]
                elif students_data[ga_column_number] == 'да':
                    pass
                elif students_data[ga_column_number] == '':
                    updating_rows_without_yes_values.append(
                        {"range": f"{ga_column_symbol}{row_number}",
                         "values": [['нет']]
                         }
                    )
                    row_number_to_session_id[row_number] = students_data[
                        SESSION_ID_COLUMN_INDEX]
                else:
                    updating_rows_without_yes_values.append(
                        {"range": f"{ga_column_symbol}{row_number}",
                         "values": [['Некорректное значение для ячейки, должно быть да или нет']]
                         }
                    )

    body = {
        "valueInputOption": "USER_ENTERED",
        "data": updating_rows_without_yes_values
    }
    update_sheet_data(service, spreadsheet_id, body)
    return row_number_to_session_id, updating_rows_without_yes_values


def update_column_after_creating_events(
    credentials_file,
    spreadsheet_id,
    platform_name,
    ga_column_number,
    ga_column_symbol,
    api_secret=None,
    measurement_id=None,
    tid=None
):

    service = connect_to_sheets_api(credentials_file)

    unsuccessful_requests_data, row_number_to_update = \
        collect_data_to_update_table(credentials_file,
                                     spreadsheet_id,
                                     platform_name,
                                     ga_column_number,
                                     ga_column_symbol,
                                     api_secret,
                                     measurement_id,
                                     tid)

    updating_row_values = []
    for row in row_number_to_update:
        updating_row_values.append({"range": f"{ga_column_symbol}{row}", "values": [['да']]})
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": updating_row_values + unsuccessful_requests_data
    }
    update_sheet_data(service, spreadsheet_id, body)


def update_ga4_and_gau_columns(
    credentials_file, spreadsheet_id, api_secret,
    measurement_id, tid
):
    update_column_after_creating_events(credentials_file,
                                        spreadsheet_id,
                                        'GAU',
                                        GAU_COLUMN_INDEX,
                                        GAU_COLUMN_SYMBOL,
                                        None,
                                        None,
                                        tid)

    update_column_after_creating_events(credentials_file,
                                        spreadsheet_id,
                                        'GA4',
                                        GA4_COLUMN_INDEX,
                                        GA4_COLUMN_SYMBOL,
                                        api_secret,
                                        measurement_id)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    api_secret = env('API_SECRET')
    measurement_id = env('MEASUREMENT_ID')
    tid = env('TID')
    credentials_file = env('CREDENTIALS_FILE', '/etc/google-api/gdrive_key.json')
    spreadsheet_id = env('SPREADSHEET_ID')
    rollbar_access_token = env('ROLLBAR_ACCESS_TOKEN')
    environment = env('ENVIRONMENT', 'production')

    if not rollbar_access_token:
        update_ga4_and_gau_columns(
            credentials_file, spreadsheet_id, api_secret,
            measurement_id, tid
        )
        exit()

    rollbar.init(rollbar_access_token, environment=environment)
    try:
        update_ga4_and_gau_columns(
            credentials_file, spreadsheet_id, api_secret,
            measurement_id, tid
        )
    except:  # noqa
        rollbar.report_exc_info(sys.exc_info())
        raise
