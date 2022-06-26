# Трекинг событий в GA пробной недели

## Описание

Продукт состоит из 2 частей.

Скрипт `tracking.py` создаёт события в `Google Analytics 4`
и `Google Analytics Universal` каждый раз, когда в Google таблице появляется запись о новом лиде. Скрипт запускается по таймеру. Он использует 
[Google Sheets API](https://developers.google.com/sheets/api?hl=ru),
[Google Drive API](https://developers.google.com/drive/api?hl=ru),
[Google Ananlytics API](https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py?hl=ru).
В качестве импровизированной CRM-системы выступает Google-таблица такого [вида](https://docs.google.com/spreadsheets/d/1PYgz15M0hC6jN49fUKNluTacNkbuqmwdUF-2gYfnx5A/edit#gid=0).
Развернут в кластере `Kubernetes`. Запускается каждый час.

Микросервис `monitoring.py` проверяет, работает ли скрипт с указанным интервалом времени. 
Он проверяет данные в [таблице](https://docs.google.com/spreadsheets/d/1PYgz15M0hC6jN49fUKNluTacNkbuqmwdUF-2gYfnx5A/edit#gid=0). 
Ищет данные, которые выглядят необработанными и, если найдёт, сообщает о проблеме в HTTP-ответе. Получается, что микросервис
`monitoring.py` выполняет функцию healthpage.

## Как развернуть скрипт по трекингу событий

Все этапы по развёртыванию в local-окружении описаны в [инструкции](running_tracking_script.md).

[Как проверить создаются ли события в GA4 и GAU после запуска скрипта](events_creating_test.md).

### Как запустить prod-версию в кластере:

Загрузите deployment, который будет запускаться 1 раз в час:

```shell-session
$ kubectl apply -f monitoring-deployment.yaml
```

## Как запустить prod-версию в кластере:

В k8s namespace должны быть уже созданы секреты:

- `google-analytics4`
- `google-universal-analytics`
- `google-spreadsheets`
- `rollbar`


`kubectl` должен быть установлен локально.

Запустите деплойный скрипт:

```
./k8s-prod/deploy.sh
```

Страница healthpage будет доступна по адресу [dvmn-tilda-spreadsheet-plus-ga.sirius-k8s.levelupdev.ru](https://dvmn-tilda-spreadsheet-plus-ga.sirius-k8s.levelupdev.ru/):

```json
{"is_healthy": true, "explanation": "tracking script is working"}
```

## Тестирование

Скрипт трекинга покрыт unit-тестами в файле `test.py`.
Для запуска необходимо ввести команду в терминале:

```shell-session
$ python -m unittest test.py
```
