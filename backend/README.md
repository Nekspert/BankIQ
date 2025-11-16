# BankIQ — Backend (Django + DRF)

**Коротко:** аналитический бекенд для портала BankIQ — превращает открытую отчетность банков в нормализованные данные, показатели, рейтинги и экспортируемые отчёты.

---

## Содержание

* [Что внутри](#что-внутри)
* [Структура проекта (коротко)](#структура-проекта-коротко)
* [Быстрый старт (локально)](#быстрый-старт-локально)
* [Переменные окружения (пример .env)](#переменные-окружения-пример-env)
* [Запуск фоновых задач (Celery)](#запуск-фоновых-задач-celery)
* [Docker / Production (кратко)](#docker--production-кратко)

---

## Что внутри

Проект — только **backend** на Django + Django REST Framework (DRF). В репозитории уже есть sqlite (db.sqlite3) для быстрого запуска, но для production рекомендуется PostgreSQL (опционально TimescaleDB для временных рядов).

Ключевые технологии и сервисы, которые проект предполагает использовать:

* Django 5.x
* Django REST Framework
* Celery + Redis (фоновые задачи, парсинг, экспорт, оповещения)
* PostgreSQL
* S3-compatible storage для файлов (отчёты/экспорты)
* Docker / docker-compose

В django из коробки идёт SQLITE3! Для этой субд ничего конфигурировать НЕ НАДО!
---

## Структура проекта (коротко)

Ниже — обзор папок и основных файлов (см. фактическую структуру репозитория):

```
manage.py                # стандартный Django CLI
db.sqlite3               # локальная БД (в репозитории сейчас)
requirements.txt         # зависимости

bank_iq/                 # Django project settings (asgi, wsgi, settings.py, urls.py)
core/                    # обязательный пакет: общие расширения и утилиты
api_payloads             # заготовленные ответы для API
accounts/                # регистрация, профили, роли, авторизация
banks/                   # справочник банков и метаданные
reports/                 # загрузка и хранение raw-отчётности, парсеры
indicators/              # предопределённые и пользовательские показатели
exports/                 # экспорт таблиц/графиков (xlsx, csv, png, pdf)
```

Каждое приложение содержит стандартные для Django файлы: `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `apps.py` и папку `migrations/`.

---

## Пакет `core` — что и зачем

Пакет `core` — центральная точка для общих компонентов. Он должен содержать (или быть расширяемым для):

* базовые абстрактные модели (BaseModel, TimestampMixin, SoftDeleteMixin), общие менеджеры;
* общие сериализаторы и поля (например MoneyField, PercentField);
* `BaseViewSet`, `BaseSerializer` и общие DRF-миксины (логирование, транзакции);
* общие permissions и роль-менеджмент (IsAnalyst, IsReadOnly и т.п.);
* исключения/формат ответа API (единый формат ошибок);
* валидаторы и утилиты (включая безопасный парсер формул для конструктора показателей);
* интеграционные клиенты и адаптеры (в `core/integrations/`) и общие парсеры/утилиты (`core/parsers`, `core/utils`).

`core` помогает избегать дублирования и централизует поведение фреймворка, которое проект переопределяет.

---

## Быстрый старт (локально)

> Пример ниже — общие шаги. Подставьте свои значения и секреты.

1. Клонировать репозиторий и перейти в папку `backend/bank_iq` (или в корень проекта):

```bash
git clone https://github.com/Nekspert/BankIQ.git
cd bankiq/backend/bank_iq  # или путь к вашему репозиторию
```

2. Создать виртуальное окружение и установить зависимости:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Unix / macOS
source .venv/bin/activate

pip install --upgrade pip
pip install -r ../requirements.txt
```

> В текущей репо есть `db.sqlite3` — можно использовать для dev без доп. настроек.

3. Создать файл с переменными окружения (.env) или передать их и выполнить миграции и создать суперпользователя:

```bash
# применить миграции
python manage.py migrate

# создать суперпользователя
python manage.py createsuperuser

# запустить dev-сервер
python manage.py runserver
```

4. Откройте `http://127.0.0.1:8000/admin` для доступа к админке и `http://127.0.0.1:8000/api/` для API (если настроено в urls).

---

## Переменные окружения (пример `.env`)

Ниже — пример минимального набора переменных. Значения и набор могут отличаться в зависимости от окружения.

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3  # или postgres://user:pass@db:5432/bankiq
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/1
```

---

## Запуск фоновых задач (Celery)

В проекте используется Celery, запустите worker и opcional beat (periodic tasks):

```bash
# worker
celery -A bank_iq worker -l info

# scheduler (если есть периодические задачи)
celery -A bank_iq beat -l info
```

В настройках укажите `CELERY_BROKER_URL` (Redis / RabbitMQ) и `CELERY_RESULT_BACKEND` при необходимости.

---

## Docker / Production (кратко)

Рекомендуется запускать в контейнерах:

* Django app (gunicorn)
* PostgreSQL
* Redis
* Celery workers + beat

Пример (локально):

```bash
# запустить контейнеры через docker-compose (если есть docker-compose.yml)
docker-compose up --build
```

Для production рекомендуется: collectstatic, миграции при деплое, healthchecks, мониторинг (Sentry, Prometheus) и HTTPS.