# CWE-208 Example (Observable Timing Discrepancy)

![Python 3.6, 3.7, 3.8](https://img.shields.io/pypi/pyversions/clubhouse?color=blueviolet)

**CWE-208: Observable Timing Discrepancy** - CWE-208:  Раскрытие информации в результате атак по времени  — это тип уязвимости, который возникает, когда в программе присутствует разное время выполнения определенных операций или ответов.

Данная уязвимость может присутствовать в  разных системах, включая веб-приложения, сетевые протоколы и криптографические алгоритмы.

**Основным последствием использования уязвимости CWE-208** является то, что она позволяет злоумышленнику получить информацию о внутренней работе системы. В частности, злоумышленник может использовать эту уязвимость для получения информации о состоянии системы, включая информацию о ее входах, выходах и внутренних процессах. В некоторых случаях эта информация может быть использована для проведения более целенаправленных атак на систему.
___

## Description of this application

При авторизации пользователя - происходит сравнение введенного пароля с паролем в БД. Поскольку, для обеспечения безопасности в БД хранится только hash паролей, то в случае существования пользователя - происходит сравнение пароля с его хешем в БД (что занимает в среднем 0.02 секунды). Если пользователя не существует, то проверка не производится, из за чего сервер отвечает быстрее (в среднем за 0.0002 секунды). 
Т.е. возникла - CWE-208: Observable Timing Discrepancy, благодаря чему злоумышленник может узнать конфиденциальные данные пользователей.


![Example ](https://github.com/NerdzzyDev/CWE-208-example-Observable-Timing-Discrepancy-/blob/main/README.gif)

___

## Files of this application
```bash
├── attack CWE-208
│   ├── main.py # Файл запуска атаки
│   └── utils
│       ├── data.py
│
└── website with vulnerability
    ├── app 
    │   ├── auth
    |   ├── forms.py
    |   ├── models.py
    |   ├── routes.py
    |   └── templates 
    |   |   ├── home.html
    |   |   ├── login.html
    |   |   ├── login_sec.html
    |   |   └── profile.html
    │   └── static
    ├── config
    │   ├── dev.py
    │   └── prod.py
    ├── instance
    │   └── flask-login.db
    ├── Procfile
    └── run.py # Файл запуска сайта-примера
```


## Installation


- Создайте и активируйте виртуальное окружение
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- Клонируйте данный репозиторий
   ```bash
  git clone ...
  ```
- Установите зависимости

   ```bash
  pip3 install -r requirements.txt
  ```
- Запустите приложение
  ```bash
  cd website\ with\ vulnerability/
  python3 run.py
  ```
  Note: Сервер доступен на 127.0.0.1:5000

- Запуск атаки
    ```bash
  cd attack\ CWE-208/
  python3 main.py
  ```
- После чего, заполните csrf-токен и cookie из POST запроса. 

___

## Fixes


```python
@authentication.route('/login', methods=['GET','POST'])
@csrf.exempt
def log_in_user():

    form = LoginForm()
    if form.validate_on_submit():
        start_time = datetime.now()
        user = User.query.filter_by(user_name=form.username.data).first()
        if not user:
            flash(f'Пользователя не существует или пароль не верный', category='danger')
            flash(f'Responce time: {(datetime.now() - start_time)}', category='info')
            return redirect(url_for('authentication.log_in_user'), 301)
        else:
            check = user.check_password(form.password.data)
            if check is True:
                login_user(user)
                return (redirect(url_for('authentication.homepage')))
            else:
                time.sleep(0.5)
                return '404'
    return render_template('login.html', form=form)
```
## ↓ DIFT
```python

@authentication.route('/login_sec', methods=['GET', 'POST'])
def log_in_user_sec():
    form = LoginForm()
    if form.validate_on_submit():
        start_time = datetime.now()
        user = User.query.filter_by(user_name=form.username.data).first()
        logger.debug(user)
        if user:
            if user.auth_count == 0:
                flash(f'Слишком частые попытки входа, поппробуйте через 24 часа', category='danger')
                return redirect(url_for('authentication.log_in_user_sec'))
        if not user or user.check_password(form.password.data) == False:
            if user:
                    wrong_auth = user.auth_count - 1
                    user.wrong_auth(id=user.id,auth_count=wrong_auth)
            # flash(f'Responce time: {(datetime.now() - start_time)}', category='info')
            flash(f'Пользователя не существует или пароль не верный', category='danger')
            return redirect(url_for('authentication.log_in_user_sec'))

        login_user(user)
        return (redirect(url_for('authentication.homepage')))

    return render_template('login_sec.html', form=form)
```

**CWE-208** — это тип уязвимости, который позволяет злоумышленнику различать конфиденциальную информацию по различиям во времени отклика. Существует несколько методов и подходов, которые можно использовать для устранения этой уязвимости в исходном коде приложения. Некоторые из этих методов включают в себя:

**Внедрение фиксированной или случайной задержки.** Один из самых простых способов устранить CWE-208 — добавить фиксированную или случайную задержку ко всем ответам. Добавляя задержку, ответы системы становятся однородными, что затрудняет злоумышленнику определение правильности угаданного ввода или нет.

**Внедрение ограничения скорости.** Ограничение скорости — это метод, который ограничивает количество запросов, которые клиент может отправить серверу в заданный период времени. Реализуя ограничение скорости, система может предотвратить повторные попытки злоумышленника угадать конфиденциальную информацию в течение короткого периода времени.

**Внедрение согласованного времени отклика.** Постоянное время отклика важно для предотвращения CWE-208. Если приложение всегда отвечает в течение согласованного промежутка времени, злоумышленнику становится сложнее выделить конфиденциальную информацию на основе времени отклика.

**Внедрение проверки на стороне сервера.** Выполнение проверки на стороне сервера, а не на стороне клиента — еще один эффективный способ предотвращения CWE-208. Проверка на стороне сервера гарантирует, что логика проверки выполняется на доверенном и безопасном сервере, а не на стороне клиента, где злоумышленник может ею манипулировать.

**Использование безопасных криптографических алгоритмов.** Важно использовать безопасные криптографические алгоритмы при обработке конфиденциальной информации в приложении. Криптографические алгоритмы, которые устарели или имеют известные уязвимости, могут облегчить злоумышленнику обнаружение конфиденциальной информации.

___

Реализация комбинации этих методов и подходов может помочь устранить CWE-208 в исходном коде приложения. Эти подходы повышают безопасность программных приложений и снижают риск кибератак, использующих уязвимости Observable Timing Disrepancy.
