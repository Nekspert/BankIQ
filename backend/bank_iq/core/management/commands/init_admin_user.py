from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


User = get_user_model()


class Command(BaseCommand):
    help = "Create or ensure existence of superuser 'root' with password '1234'"

    def handle(self, *args, **options):
        username = "root"
        email = "root@email.com"
        password = "1234"

        try:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                        username=username,
                        defaults={"email": email,
                                  "is_staff": True,
                                  "is_superuser": True})

                if not created:
                    updated = False

                    if not user.is_staff or not user.is_superuser:
                        user.is_staff = True
                        user.is_superuser = True
                        updated = True

                    if not user.check_password(password):
                        user.set_password(password)
                        updated = True

                    if updated:
                        user.save()
                        self.stdout.write(
                                self.style.SUCCESS(f"Superuser '{username}' обновлён (права или пароль исправлены)"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' уже существует и актуален"))
                else:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' успешно создан"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при создании/обновлении superuser: {e}"))
            raise
