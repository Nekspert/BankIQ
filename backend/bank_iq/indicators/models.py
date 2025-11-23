from django.db import models


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


class BankIndicatorsRequest(models.Model):
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, help_text='FK -> Bank',
                             related_name='indicators_requests')
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

    data_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True,
                                 help_text='sha256 хэш представления indicators')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'IndicatorsResponse:{self.request.form_type.title} ({self.request.reg_number})'

    class Meta:
        ordering = ('-created_at',)


class BankIndicatorDataRequest(models.Model):
    bank = models.ForeignKey('banks.Bank', on_delete=models.CASCADE, related_name='indicator_data_requests',
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

    data_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True,
                                 help_text='sha256 хэш представления bank_indicator_data')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'IndicatorDataResponse:{self.request.ind_code}_{self.request.form_type.title} ({self.request.reg_number})'

    class Meta:
        ordering = ('-created_at',)
