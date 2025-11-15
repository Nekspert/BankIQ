from django.db import models


class Bank(models.Model):
    reg_number = models.IntegerField(unique=True, db_index=True,
                                     help_text='Регистрационный номер банка в базе ЦБ (рег. номер). '
                                               'Уникальный строковый идентификатор, например "1481".')
    bic = models.CharField(
            help_text='БИК (Bank Identification Code) — банковский идентификатор. Пример: "044525225".')
    name = models.CharField(unique=True, db_index=True,
                            help_text='Полное наименование кредитной организации. Уникально в справочнике.')
    internal_code = models.CharField(
            help_text='Внутренний код/идентификатор банка в источнике данных (если доступен).')
    registration_date = models.DateTimeField(
            help_text='Дата регистрации организации (ISO-8601). Может содержать информацию о времени и часовом поясе.')
    region_code = models.CharField(
            help_text='Код региона (региональный номер/код). Используется для региональных срезов и агрегатов.')
    tax_id = models.CharField(unique=True, db_index=True,
                              help_text='Идентификатор налогоплательщика (ИНН) или другой налоговый идентификатор. '
                                        'Уникален для организации.')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Bank:{self.name} ({self.reg_number})'

    class Meta:
        ordering = ('-created_at',)


class FormType(models.Model):
    title = models.CharField(db_index=True, unique=True,
                             help_text='Код/название формы отчётности (например "F101", "F123").')
    description = models.TextField(
            help_text='Подробное описание формы: структура, используемые поля, примечания по парсингу и версиям схемы.')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'FormType:{self.title}'

    class Meta:
        ordering = ('-created_at',)
        unique_together = (('title', 'description'),)


class BankDatesRequest(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, db_index=True, help_text='FK -> Bank',
                             related_name='dates_requests')
    form_type = models.ForeignKey(FormType, on_delete=models.SET_NULL, db_index=True, help_text='FK -> FormType',
                                  null=True)
    reg_number = models.IntegerField(help_text='Регистрационный номер банка в базе ЦБ')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'DatesRequest:{self.form_type.title} ({self.reg_number})'

    class Meta:
        ordering = ('-created_at',)
        unique_together = (('bank', 'form_type'),)


class BankDatesResponse(models.Model):
    request = models.OneToOneField(BankDatesRequest, on_delete=models.CASCADE, help_text='Ответ',
                                   related_name='response')
    datetimes = models.JSONField(help_text='Список доступных дат')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'DatesResponse:{self.request.form_type.title} ({self.request.reg_number})'

    class Meta:
        ordering = ('-created_at',)


class BankIndicatorsRequest(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, help_text='FK -> Bank', related_name='indicators_requests')
    form_type = models.ForeignKey(FormType, on_delete=models.SET_NULL, null=True, help_text='FK -> FormType')
    reg_number = models.IntegerField(help_text='Регистрационный номер банка в базе ЦБ')
    dt = models.DateTimeField(help_text='Целевая дата')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'IndicatorsRequest:{self.form_type.title} ({self.reg_number})'

    class Meta:
        ordering = ('-created_at',)
        unique_together = (('bank', 'form_type', 'reg_number', 'dt'),)


class BankIndicatorsResponse(models.Model):
    request = models.OneToOneField(BankIndicatorsRequest, on_delete=models.CASCADE, related_name='response',
                                   help_text='Ответ')
    indicators = models.JSONField(help_text='Список индикаторов')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'IndicatorsResponse:{self.request.form_type.title} ({self.request.reg_number})'

    class Meta:
        ordering = ('-created_at',)


class BankIndicatorDataRequest(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='indicator_data_requests',
                             help_text='FK -> Bank')
    form_type = models.ForeignKey(FormType, on_delete=models.SET_NULL, null=True, help_text='FK -> FormType')
    reg_number = models.IntegerField(help_text='Регистрационный номер банка в базе ЦБ')
    ind_code = models.CharField(null=True, help_text='Код индикатора')
    date_from = models.DateTimeField(null=True, help_text='Дата с')
    date_to = models.DateTimeField(null=True, help_text='Дата по')
    dt = models.DateTimeField(null=True, help_text='Целевая дата')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'IndicatorDataRequest:{self.ind_code}_{self.form_type.title} ({self.reg_number})'

    class Meta:
        ordering = ('-created_at',)
        unique_together = (('bank', 'form_type', 'reg_number', 'ind_code', 'date_from', 'date_to', 'dt'),)


class BankIndicatorDataResponse(models.Model):
    request = models.OneToOneField(BankIndicatorDataRequest, on_delete=models.CASCADE, related_name='response',
                                   help_text='Ответ')
    bank_indicator_data = models.JSONField(help_text='Список данных индикатора')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'IndicatorDataResponse:{self.request.ind_code}_{self.request.form_type.title} ({self.request.reg_number})'

    class Meta:
        ordering = ('-created_at',)
