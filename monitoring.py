import datetime
import pytz
import asyncio

from aiohttp import web
from contextlib import suppress
from dateutil import parser
from environs import Env
from tracking import connect_to_sheets_api, \
    get_sheet_data, \
    SESSION_ID_COLUMN_INDEX,\
    TG_ACCOUNT_COLUMN_INDEX, \
    GA4_COLUMN_INDEX, \
    GAU_COLUMN_INDEX

SENT_TIME_COLUMN_INDEX = 4
IS_HEALTHY = None


def check_tracking_working_via_send_time(credentials_file, spreadsheet_id):
    service = connect_to_sheets_api(credentials_file)
    row_values = get_sheet_data(service, spreadsheet_id)
    is_healthy = {
        'is_healthy': True,
        'explanation': 'tracking script is working'
    }
    for row_number, students_data in enumerate(row_values, start=2):
        with suppress(IndexError):
            if students_data[TG_ACCOUNT_COLUMN_INDEX] and students_data[SESSION_ID_COLUMN_INDEX]:
                tilda_time_table_str = students_data[SENT_TIME_COLUMN_INDEX]
                current_moscow_time = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
                time_to_test_script = current_moscow_time + datetime.timedelta(hours=1, minutes=10)
                if time_to_test_script.timestamp() > parser.parse(tilda_time_table_str).timestamp():
                    if students_data[GA4_COLUMN_INDEX] == 'Ошибка при создании события, обратитесь к программисту' or \
                            students_data[GAU_COLUMN_INDEX] == 'Ошибка при создании события, обратитесь к программисту':
                        is_healthy = {
                            'is_healthy': False,
                            'explanation': 'tracking script is not working',
                        }
                    if students_data[GA4_COLUMN_INDEX] == 'нет' or \
                            students_data[GA4_COLUMN_INDEX] == '' or \
                            students_data[GAU_COLUMN_INDEX] == 'нет' or \
                            students_data[GAU_COLUMN_INDEX] == '':
                        is_healthy = {
                            'is_healthy': False,
                            'explanation': 'tracking script is not working',
                        }
    return is_healthy


async def check_healthy(request):
    return web.json_response(IS_HEALTHY)


async def get_tracking_script_status():
    return check_tracking_working_via_send_time(credentials_file,
                                                spreadsheet_id)


async def get_tracking_script_status_infinitely():

    while True:
        status_page_data = await get_tracking_script_status()
        global IS_HEALTHY
        IS_HEALTHY = status_page_data
        await asyncio.sleep(5*60)


async def create_background_task_tracking_script_status(app):

    asyncio.create_task(get_tracking_script_status_infinitely())


async def make_app():

    app = web.Application()
    app.add_routes([web.get('/', check_healthy)])
    app.on_startup.append(create_background_task_tracking_script_status)
    return app


if __name__ == '__main__':
    env = Env()
    env.read_env()

    credentials_file = env('CREDENTIALS_FILE',
                           '/etc/google-api/gdrive_key.json')
    spreadsheet_id = env('SPREADSHEET_ID')
    web.run_app(make_app(), host='0.0.0.0', port=8080)
