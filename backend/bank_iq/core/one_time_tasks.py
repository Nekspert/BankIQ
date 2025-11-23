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
