from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Crea cuentas de prueba (admin, encargado y socio) con una contraseña indicada.'

    def add_arguments(self, parser):
        parser.add_argument('--password', required=True, help='Contraseña de desarrollo para las cuentas demo.')

    def handle(self, *args, **options):
        password = options['password']
        if len(password) < 8:
            raise CommandError('La contraseña debe tener al menos 8 caracteres.')

        user_model = get_user_model()
        accounts = (
            ('admin', True, True),
            ('encargado', True, False),
            ('socio', False, False),
        )
        for username, is_staff, is_superuser in accounts:
            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={'is_staff': is_staff, 'is_superuser': is_superuser},
            )
            if not created:
                user.is_staff = is_staff
                user.is_superuser = is_superuser
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(f'Cuenta {username}: {"creada" if created else "actualizada"}')
