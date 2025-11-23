from django.db import models


class Bank(models.Model):
    reg_number = models.IntegerField(unique=True, db_index=True,
                                     help_text='Регистрационный номер банка в базе ЦБ (рег. номер). '
                                               'Уникальный строковый идентификатор, например "1481".')
    bic = models.CharField(
            help_text='БИК (Bank Identification Code) — банковский идентификатор. Пример: "044525225".')
    name = models.CharField(db_index=True,
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
        unique_together = (('name', 'reg_number'),)


class BankDatesRequest(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, db_index=True, help_text='FK -> Bank',
                             related_name='dates_requests')
    form_type = models.ForeignKey('indicators.FormType', on_delete=models.SET_NULL, db_index=True,
                                  help_text='FK -> FormType',
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

    data_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True,
                                 help_text='sha256 хэш представления datetimes')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'DatesResponse:{self.request.form_type.title} ({self.request.reg_number})'

    class Meta:
        ordering = ('-created_at',)
