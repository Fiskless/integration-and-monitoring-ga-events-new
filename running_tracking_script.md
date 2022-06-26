# Инструкция по запуску и настройке скриптов

## Как запустить local-версию

Для запуска скрипта у вас уже должен быть установлен Python 3.

- Скачайте код
- Установите зависимости командой 
    ```shell-session
    $ pip install -r requirements.txt
    ```
- Запустите оба скрипта:
    ```shell-session
    $ python3 tracking.py
    $ python3 monitoring.py
    ```

## Переменные окружения

Часть настроек проекта берётся из переменных окружения. 
Чтобы их определить, создайте файл `.env` рядом с `main.py` 
и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Используются следующие переменные окружения:
1) `API_SECRET` - секретный ключ MEASUREMENT PROTOCOL API вашего аккаунта GA4. 
Секретный ключ генерируется в интерфейсе Google Analytics. Получить его можно следующим образом:

   * Перейдите в раздел **Администратор - Потоки данных**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic1.png)

   * Выберите свой веб-поток. Затем откройте раздел **О Mesurement Protocol API**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic2.png)

   * В открывшемся окне нажмите кнопку **Создать**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic3.png)

   * После ввода псевдонима нажмите кнопку **Создать**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic8.png)

   * После создания ключа он отобразится в списке доступных в столбце **Значение секретного ключа**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic4.png)

2) `MEASUREMENT_ID` - идентификатор потока данных в GA4. Чтобы найти идентификатор потока данных Google Analytics 4:

   * Перейдите в раздел **Администратор - Потоки данных**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic5.png)

   * Выберите свой веб-поток данных:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic6.png)

   * В открывшемся окне скопируйте значение, указанное в правом верхнем углу в 
поле **Идентификатор потока данных**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic7.png)
      
      Это и есть ваш идентификатор отслеживания Google Analytics 4

3) `TID` - идентификатор отслеживания в GAU
Чтобы найти идентификатор отслеживания Google Analytics Universal:

   * Перейдите в раздел **Отслеживание - Код отслеживания**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic22.png)

   * В открывшемся окне в графе **Идентификатор отслеживания** и есть ваш 
идентификатор отслеживания Google Analytics Universal:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic23.png)

4) `SPREADSHEET_ID` - id Google-таблицы, берется прямо из url-ссылки на таблицу:

      ![Image alt](screenshots/tracking_running_instructions_pics/picid.png)

5) `CREDENTIALS_FILE` - переменная, в которой указан путь к json-файлу. 
В этом файле лежат данные сервисного аккаунта, через который идет 
взаимодействие с Google Drive API. Для его получения: 

   * Перейдите по [ссылке](https://console.cloud.google.com/cloud-resource-manager)

   * Нажмите **Create Project**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic9.png)

   * Введите название проекта и нажмите **Create**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic10.png)

   * Перейдите в **Dashboard** созданного проекта:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic11.png)

   * В разделе APIs нажмите **Go to APIs overview**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic12.png)

   * Нажмите **ENABLE APIS AND SERVICES**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic13.png)

   * Необходимо подключить 2 АПИ: **Google Sheets API**  и **Google Drive API**.
В поисковом окне напишите **Google Sheets API**, после чего нажмите на **ENABLE**

   * Затем вернитесь в это же поисковое окно, и напишите **Google Drive API**, после чего нажмите на **ENABLE**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic14.png)

   * Далее необходимо создать сервисный аккаунт. В открывшемся окне нажмите **CREATE CREDENTIALS**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic15.png)

   * Заполните данные как на картинке, после чего нажмите **NEXT**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic16.png)

   * Напишите имя сервисного аккаунта, после чего нажмите **CREATE AND CONTINUE**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic17.png)

   * Добавьте роль, нажмите **Role-Project-Editor**:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic18.png)

      Далее нажмите **DONE**

   * В открывшемся окне нажмите на ваш только что созданный сервисный аккаунт:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic19.png)

   * Далее перейдите во вкладку **KEYS**, далее **ADD KEY - Create new key**.  В открывшемся окне выберите JSON и нажмите CREATE. Далее загрузите себе этот файл.

      ![Image alt](screenshots/tracking_running_instructions_pics/pic21.png)

   * В скачанном json файле в ключе **client_email** будет аккаунт, которому нужно будет предоставить доступ в вашей Google-таблице:

      ![Image alt](screenshots/tracking_running_instructions_pics/pic20.png)


6) `ROLLBAR_ACCESS_TOKEN` - токен для доступа к [Rollbar](https://rollbar.com/)
7) `ENVIRONMENT` - настройка для Rollbar, группирует события по названию окружения local/dev/production/etc. При 
разработке на своей машине поставьте значение `local`, на боевом сервере - `production`.