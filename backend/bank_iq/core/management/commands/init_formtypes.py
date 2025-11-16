from importlib import import_module

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Init or update FormType instances from core.one_time_tasks.REGISTRY'

    def handle(self, *args, **options):
        try:
            mod = import_module('core.one_time_tasks')
        except Exception as ex:
            self.stderr.write(self.style.ERROR(f'Не удалось импортировать core.one_time_tasks: {ex}'))
            return

        registry = getattr(mod, 'REGISTRY', [])
        if not registry:
            self.stdout.write('REGISTRY пуст. Нечего создавать.')
            return

        from indicators.models import FormType

        created = 0
        updated = 0

        for item in registry:
            if callable(item):
                payload = item()
            else:
                payload = item

            title = payload.get('title')
            description = payload.get('description', '')

            if not title:
                self.stderr.write(self.style.WARNING('Пропускаю запись без title'))
                continue

            with transaction.atomic():
                obj, was_created = FormType.objects.update_or_create(
                        title=title,
                        defaults={'description': description}
                )
                if was_created:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f'Создан FormType: {title}'))
                else:
                    updated += 1
                    self.stdout.write(self.style.NOTICE(f'Обновлён FormType: {title}'))

        self.stdout.write(self.style.SUCCESS(f'Готово. Создано: {created}, Обновлено: {updated}'))
