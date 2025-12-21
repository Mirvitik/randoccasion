## Проект "Встречалки", разработанный в рамках обучения в Яндекс Лицее

[![pipeline status](https://gitlab.crja72.ru/django/2025/autumn/course/projects/team-8/badges/main/pipeline.svg?key_text=Django%20Project%20Tests&key_width=150)](https://gitlab.crja72.ru/django/2025/autumn/course/projects/team-8/-/pipelines)

Перед запуском убедитесь, что у вас установлены:

- [Python релизные версии от 3.10 до 3.12 включительно](https://www.python.org/downloads/)
- [Последняя версия git](https://git-scm.com/install/???Download??git)
- pip (устанавливается вместе с питоном)
- virtualenv (устанавливается вместе с питоном)

## Клонирование репозитория

Для клонирования репозитория на свой компьютер воспользуйтесь следующей командой:

```bash
git clone https://gitlab.crja72.ru/django/2025/autumn/course/projects/team-8
```

И перейдите в папку с проектом:

```bash
cd team-8
```

## Установка

**Создание виртуального окружения**

Linux/MacOS

```bash
python3 -m venv venv
```

Windows

```bash
python -m venv venv
```

Активировать среду на Linux/MacOS

```bash
source venv/bin/activate
```

Или на Windows

```bash
venv\Scripts\activate
```

Установите зависимости (для разработки)

```bash
pip install -r requirements/dev.txt
```

**Для тестирования**

```bash
pip install -r requirements/test.txt
```

**Для продакшена**

```bash
pip install -r requirements/prod.txt
```

Перед запуском следует настроить ```.env``` файл. Создайте его и
создайте в нём переменную ```DJANGO_SECRET_KEY``` со значением вашего секретного ключа.

Также создайте в нём переменную ```TELEGRAM_BOT_TOKEN``` со значением вашего токена
для телеграм-бота. Это нужно для рассылки уведомлений.

```DJANGO_MAIL``` переименуйте на почту, с которой ваш сайт будет отправлять письма,
```DJANGO_EMAIL_HOST```-ваш smtp-сервер, ```DJANGO_EMAIL_PORT```-порт для отправки
писем, ```DJANGO_EMAIL_PASSWORD```-пароль для отправки писем

Переименуйте папку media_example в media, а в файле .env
поменяйте значение ```DJANGO_MEDIA``` на ```media```, а ```DJANGO_DB_NAME``` поменяйте на ```db.sqlite3```

**Для linux/MacOS**

```bash
cp example.env .env
```

**Для Windows**

```bash
copy example.env .env
```

**ВНМАНИЕ! Измените значение переменной DJANGO_SECRET_KEY в появившемся .env файле**

**Переход в папку randoccasion на Windows/Linux/MacOS**

```bash
cd randoccasion
```

**Загрузка фикстуры в базу данных**
Linux/MacOS

```bash
python3 manage.py loaddata fixtures/data.json
```

Windows

```bash
python manage.py loaddata fixtures/data.json
```

**Создание суперпользователя**

Для создания аккаунта администратора воспользуйтесь следующей командой:

Linux/MacOS

```bash
python3 manage.py createsuperuser
```

Windows

```bash
python manage.py createsuperuser
```

[Админка](http://127.0.0.1:8000/admin/)

Укажите логин, почту и пароль для аккаунта администратора

## Настройка динамических переводов

В файле ```.env``` в переменной ```DJANGO_LANGUAGE_CODE``` укажите код языка,
который вы хотите установить в проекте по умолчанию.

Если вашего языка нет в списке ```LANGUAGES``` в ```settings.py```, то добавьте в переменную кортеж
с кодом вашего языка и названием языка на английском так, как это сделано с остальными
языками.
Затем в консоли введите команду:

```bash
django-admin makemessages -l <код вашего языка>
```

Затем зайдите в директорию ```randoccasion/locale/<код вашего языка>/LC_MESSAGES```
Затем в файле ```django.mo``` вбейте в пустые строки рядом с msgstr перевод строк,
которые находятся рядом с msgid.

Затем вернитесь в папку ```randoccasion``` и выполните команду:

```bash
django-admin compilemessages 
```

Готов, теперь сайт переведён на ваш язык!

## Запуск сервера

Linux/MacOS

```bash
python3 manage.py runserver
```

Windows

```bash
python manage.py runserver
```

Также мы рекомендуем Вам открыть второй
терминал и запустить телеграм-бота для
связки аккаунтов пользователей. Это можно сделать через:

Linux/MacOS

```bash
python3 runbot.py
```

Windows

```bash
python runbot.py
```

[Ссылка на главную страницу сайта](http://127.0.0.1:8000/)

## Устройство API

Работа API осуществляется через API-ключ. Для его генерации
нужно зайти на страницу ```/api/v1/apikey-create/``` по логину и паролю
администратора.

Для использования API-ключа укажите в headers в ключе Authorization ```Api-Key <ВАШ-API-ключ>```

Пример использования нашего API на локальном хосте с помощью Python через библиотеку requests

```
import requests

s = requests.Session()
s.headers.update({'Authorization': 'API-key <ВАШ-API-ключ>'})
print(s.get('http://127.0.0.1:8000/api/v1/events/').json())
```

Пути для работы с API:

```/api/v1/users/``` GET-запрос, возвращает информацию о пользователях

```/api/v1/users/<int:pk>/```  GET-запрос, получение информации о пользователе

```/api/v1/events/``` GET. Возвращает события, которые доступны для просмотра всем
создаёт новое событие

```/api/v1/events/<int:pk>/``` GET-запрос, возвращает событие по id

```/api/v1/interests/``` GET-запрос, возвращает все интересы

```/api/v1/interests/<int:pk>/``` GET-запрос, возвращает интерес по id

### Основные параметры поиска

| Параметр | Тип | Описание | Пример | Обязательный |
|----------|-----|----------|---------|-----------|
| `q` | String | Поисковый запрос (можно указать несколько значений) | `?q=концерт` | Нет       |
| `date_from` | Date (YYYY-MM-DD) | События, созданные с указанной даты (включительно) | `?date_from=2024-01-01` | Нет          |
| `date_to` | Date (YYYY-MM-DD) | События, созданные до указанной даты (включительно) | `?date_to=2024-12-31` | Нет          |

### Фильтры статуса и видимости

| Параметр | Тип | Допустимые значения | Описание |
|----------|-----|---------------------|----------|
| `only_active` | Boolean | `true`, `false`     | Только активные события |
| `interest` | Integer | ID интереса (число) | Фильтрация по интересам |

### Параметры сортировки

| Параметр | Допустимые значения | Сортировка по | Направление |
|----------|---------------------|---------------|-------------|
| `sort_published` | `asc`, `desc` | Дате создания события | `asc` - старые сначала<br>`desc` - новые сначала |
| `sort_expiry` | `asc`, `desc` | Дате истечения события | `asc` - раньше истекают<br>`desc` - позже истекают |
| `sort_alpha` | `asc`, `desc` | Названию события (алфавит) | `asc` - A→Z<br>`desc` - Z→A |

## Примеры использования

### Пример 1: Поиск активных событий
```
GET /api/v1/events/search/?only_active=true&sort_published=desc
```

## Архитектура базы данных проекта

![alt text](ER.jpg)