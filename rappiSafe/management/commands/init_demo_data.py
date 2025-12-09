from django.core.management.base import BaseCommand
from django.utils import timezone
from rappiSafe.models import (
    User, RepartidorProfile, ContactoConfianza,
    Alerta, EstadisticaRiesgo
)
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Inicializa la base de datos con datos de demostración'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando creación de datos de demostración...')

        # Crear superusuario si no existe
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@rappisafe.com',
                password='admin123',
                first_name='Super',
                last_name='Admin',
                rol='administrador',
                telefono='+5215500000000'
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Superusuario creado: admin/admin123'))
        else:
            self.stdout.write('[!] Superusuario ya existe')

        # Crear repartidores de prueba
        repartidores_data = [
            {
                'username': 'repartidor1',
                'email': 'juan.perez@rappisafe.com',
                'password': 'test123',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'telefono': '+5215512345678'
            },
            {
                'username': 'repartidor2',
                'email': 'maria.lopez@rappisafe.com',
                'password': 'test123',
                'first_name': 'María',
                'last_name': 'López',
                'telefono': '+5215512345679'
            },
            {
                'username': 'repartidor3',
                'email': 'carlos.garcia@rappisafe.com',
                'password': 'test123',
                'first_name': 'Carlos',
                'last_name': 'García',
                'telefono': '+5215512345680'
            },
        ]

        repartidores = []
        for data in repartidores_data:
            if not User.objects.filter(username=data['username']).exists():
                rep = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    rol='repartidor',
                    telefono=data['telefono']
                )
                repartidores.append(rep)
                self.stdout.write(self.style.SUCCESS(f'[OK] Repartidor creado: {data["username"]}/test123'))

                # Crear contactos de confianza
                ContactoConfianza.objects.create(
                    repartidor=rep,
                    nombre=f'Contacto 1 de {rep.first_name}',
                    telefono='+5215500000001',
                    relacion='Familiar',
                    validado=True
                )
                ContactoConfianza.objects.create(
                    repartidor=rep,
                    nombre=f'Contacto 2 de {rep.first_name}',
                    telefono='+5215500000002',
                    relacion='Amigo',
                    validado=False
                )
            else:
                self.stdout.write(f'[!] Repartidor {data["username"]} ya existe')
                repartidores.append(User.objects.get(username=data['username']))

        # Crear operadores de prueba
        operadores_data = [
            {
                'username': 'operador1',
                'email': 'ana.martinez@rappisafe.com',
                'password': 'test123',
                'first_name': 'Ana',
                'last_name': 'Martínez',
            },
            {
                'username': 'operador2',
                'email': 'luis.rodriguez@rappisafe.com',
                'password': 'test123',
                'first_name': 'Luis',
                'last_name': 'Rodríguez',
            },
        ]

        for data in operadores_data:
            if not User.objects.filter(username=data['username']).exists():
                User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    rol='operador'
                )
                self.stdout.write(self.style.SUCCESS(f'[OK] Operador creado: {data["username"]}/test123'))
            else:
                self.stdout.write(f'[!] Operador {data["username"]} ya existe')

        # Crear administrador adicional
        if not User.objects.filter(username='admin1').exists():
            User.objects.create_user(
                username='admin1',
                email='admin1@rappisafe.com',
                password='test123',
                first_name='Carlos',
                last_name='Admin',
                rol='administrador',
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS('[OK] Administrador creado: admin1/test123'))
        else:
            self.stdout.write('[!] Administrador admin1 ya existe')

        # Crear zonas de riesgo de ejemplo
        zonas_data = [
            {
                'nombre': 'Centro Histórico',
                'puntuacion': 75.5,
                'total': 15,
                'panico': 10,
                'accidente': 5
            },
            {
                'nombre': 'Zona Industrial',
                'puntuacion': 62.3,
                'total': 12,
                'panico': 7,
                'accidente': 5
            },
            {
                'nombre': 'Residencial Norte',
                'puntuacion': 35.8,
                'total': 8,
                'panico': 3,
                'accidente': 5
            },
        ]

        for zona in zonas_data:
            if not EstadisticaRiesgo.objects.filter(nombre_zona=zona['nombre']).exists():
                EstadisticaRiesgo.objects.create(
                    nombre_zona=zona['nombre'],
                    coordenadas_zona={'type': 'Polygon', 'coordinates': []},
                    puntuacion_riesgo=zona['puntuacion'],
                    total_alertas=zona['total'],
                    alertas_panico=zona['panico'],
                    alertas_accidente=zona['accidente'],
                    periodo_inicio=date.today() - timedelta(days=30),
                    periodo_fin=date.today()
                )
                self.stdout.write(self.style.SUCCESS(f'[OK] Zona de riesgo creada: {zona["nombre"]}'))
            else:
                self.stdout.write(f'[!] Zona {zona["nombre"]} ya existe')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('[OK] Datos de demostracion creados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('Usuarios creados:')
        self.stdout.write('  Superusuario: admin / admin123')
        self.stdout.write('  Repartidores: repartidor1, repartidor2, repartidor3 / test123')
        self.stdout.write('  Operadores: operador1, operador2 / test123')
        self.stdout.write('  Admin: admin1 / test123')
        self.stdout.write('')
        self.stdout.write('Puedes acceder a:')
        self.stdout.write('  - Django Admin: http://localhost:8000/admin/')
        self.stdout.write('  - Aplicación: http://localhost:8000/')
        self.stdout.write('')
