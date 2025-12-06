def form_f101():
    return {
        'title': 'F101',
        'description': 'Форма 101 — подробная ежемесячная отчетность банка.'
    }


def form_f123():
    return {
        'title': 'F123',
        'description': 'Форма 123 — информация о собственных средствах и капитале.'
    }


def form_f810():
    return {
        'title': 'F810',
        'description': 'Форма 810 — отчёт об изменениях в капитале кредитной организации'
    }


REGISTRY = [
    form_f101,
    form_f123,
    form_f810,
]


def clear_database():
    import psycopg
    import logging
    from environs import Env

    env = Env()
    env.read_env()
    conn = psycopg.connect(dbname='postgres', user='postgres', password='1234', host='db')
    conn.autocommit = True

    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS bankiq;")
    cur.execute("CREATE DATABASE bankiq;")
    cur.close()
    conn.close()

    logger = logging.getLogger(__name__)
    logger.info("[INFO] Database 'bankiq' has been dropped and recreated successfully. [INFO]")
