from django.contrib.auth import get_user_model
from django.db import models


class Export(models.Model):
    user = models.ForeignKey(get_user_model(), db_index=True, on_delete=models.CASCADE,
                             help_text='FK -> User')

    form_type = models.ForeignKey('indicators.FormType', null=True, on_delete=models.SET_NULL,
                                  help_text='FK -> FormType, nullable для общих/непривязанных данных')

    class FileType(models.TextChoices):
        XLSX = 'xlsx', 'Excel (.xlsx)'
        CSV = 'csv', 'CSV'
        PDF = 'pdf', 'PDF'
        PNG = 'png', 'PNG image'

    file_type = models.CharField(max_length=5, choices=FileType.choices, default=FileType.XLSX,
                                 help_text='тип результирующего файла')
    file_path = models.FileField(upload_to='exports/export_files/%Y/%m/%d/', null=True, blank=True,
                                 help_text='Файл экспорта (S3 URL)')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'export:{self.user.username}:{self.form_type.title}'

    class Meta:
        ordering = ('-created_at',)
