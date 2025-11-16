from django.db import models


class CbrApiDataRequest(models.Model):
    class RateType(models.TextChoices):
        CREDIT = 'credit', 'Кредитные ставки'
        DEPOSIT = 'deposit', 'Депозитные ставки'
        PARAMS_CHECK = 'params_check', 'Проверка параметров'

    rate_type = models.CharField(max_length=15, choices=RateType, db_index=True,
                                 help_text='Тип запроса к API ЦБ РФ')
    publication_id = models.IntegerField(db_index=True,
                                         help_text='ID публикации в API ЦБ РФ', null=True, )
    dataset_id = models.IntegerField(db_index=True,
                                     help_text='ID набора данных в API ЦБ РФ', null=True, )
    measure_id = models.IntegerField(db_index=True,
                                     help_text='ID разреза (measure) в API ЦБ РФ', null=True, )
    from_year = models.IntegerField(help_text='Начальный год периода запроса', null=True, )
    to_year = models.IntegerField(help_text='Конечный год периода запроса', null=True, )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'CbrApiDataRequest:{self.rate_type} ({self.publication_id}-{self.dataset_id}-{self.measure_id})'

    class Meta:
        ordering = ('-created_at',)
        unique_together = (
            ('rate_type', 'publication_id', 'dataset_id', 'measure_id', 'from_year', 'to_year'),
            ('rate_type', 'publication_id', 'dataset_id', 'measure_id',),
        )
        indexes = [
            models.Index(fields=['rate_type', 'publication_id', 'dataset_id', 'measure_id', 'from_year', 'to_year']),
            models.Index(fields=['rate_type', 'publication_id', 'dataset_id', 'measure_id']),
        ]


class CbrApiDataResponse(models.Model):
    request = models.OneToOneField(CbrApiDataRequest, on_delete=models.CASCADE,
                                   related_name='response', help_text='FK -> CbrApiDataRequest')
    processed_data = models.JSONField(help_text='Обработанные и нормализованные данные для аналитики',
                                      null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f'CbrApiDataResponse:{self.request.rate_type} '
                f'({self.request.publication_id}-{self.request.dataset_id}-{self.request.measure_id})')

    class Meta:
        ordering = ('-created_at',)
