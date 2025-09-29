Async Yacut

Веб-приложение на Flask для сокращения ссылок и загрузки файлов в Яндекс.Диск с выдачей прямых ссылок.
Поддерживает работу через веб-интерфейс и REST API.

Возможности

Создание коротких ссылок для произвольных URL.

Проверка и задание собственного идентификатора (до 16 символов).

Загрузка файлов на Яндекс.Диск и получение короткой ссылки на прямую скачку.

REST API (/api/id/ и /api/id/<short_id>/).

Обработка ошибок (валидация, отсутствующие поля).

Асинхронная работа с API Яндекс.Диска через aiohttp.

Технологии

Python 3.10+

Flask

Flask-SQLAlchemy

Flask-Migrate

Flask-WTF

WTForms

aiohttp

SQLite (по умолчанию)

Установка

git clone <repo_url>
cd async-yacut
python -m venv venv
source venv/bin/activate (Windows: venv\Scripts\activate)
pip install -r requirements.txt

Переменные окружения

Создайте файл .env и укажите:
SECRET_KEY=секретный_ключ
DATABASE_URI=sqlite:///db.sqlite3
DISK_TOKEN=токен_от_яндекс_диска

Запуск

flask run
По умолчанию приложение будет доступно на http://127.0.0.1:5000

Использование API

Создание короткой ссылки:
POST /api/id/
Content-Type: application/json

{ "url": "https://example.com
", "custom_id": "myshort" }

Ответ:
{ "url": "https://example.com
", "short_link": "http://127.0.0.1:5000/myshort
" }

Получение оригинальной ссылки:
GET /api/id/myshort/
Ответ:
{ "url": "https://example.com
" }

Запуск миграций

flask db init
flask db migrate
flask db upgrade

Структура проекта

async-yacut/
├── init.py фабрика приложения Flask
├── api_views.py API-роуты
├── forms.py формы Flask-WTF
├── models.py модель URLMap
├── utils.py генератор коротких id
├── views.py основные маршруты
├── templates/ HTML-шаблоны
└── static/ статика