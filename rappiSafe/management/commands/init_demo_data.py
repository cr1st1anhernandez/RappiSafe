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

        # Crear zonas de riesgo REALES basadas en datos de criminalidad de CDMX (escala 1-10)
        # Coordenadas reales de zonas con diferentes niveles de riesgo
        zonas_data = [
            # ====== ZONAS DE ALTO RIESGO (7.5 - 9.0) ======
            {
                'nombre': 'Tepito (Cuauhtémoc)',
                'lat': 19.4486,
                'lng': -99.1236,
                'radio_km': 1.5,
                'puntuacion': 8.7,
                'total': 28,
                'panico': 18,
                'accidente': 10
            },
            {
                'nombre': 'La Merced (Cuauhtémoc)',
                'lat': 19.4242,
                'lng': -99.1231,
                'radio_km': 1.2,
                'puntuacion': 8.2,
                'total': 24,
                'panico': 16,
                'accidente': 8
            },
            {
                'nombre': 'Iztapalapa Centro',
                'lat': 19.3568,
                'lng': -99.0557,
                'radio_km': 2.0,
                'puntuacion': 7.9,
                'total': 32,
                'panico': 20,
                'accidente': 12
            },
            {
                'nombre': 'Doctores (Cuauhtémoc)',
                'lat': 19.4208,
                'lng': -99.1458,
                'radio_km': 1.0,
                'puntuacion': 7.5,
                'total': 21,
                'panico': 13,
                'accidente': 8
            },

            # ====== ZONAS DE RIESGO MEDIO-ALTO (6.0 - 7.4) ======
            {
                'nombre': 'Centro Histórico (Cuauhtémoc)',
                'lat': 19.4326,
                'lng': -99.1332,
                'radio_km': 1.5,
                'puntuacion': 6.8,
                'total': 18,
                'panico': 10,
                'accidente': 8
            },
            {
                'nombre': 'Aragón (Gustavo A. Madero)',
                'lat': 19.4753,
                'lng': -99.0892,
                'radio_km': 1.3,
                'puntuacion': 6.5,
                'total': 16,
                'panico': 9,
                'accidente': 7
            },
            {
                'nombre': 'Zona Rosa (Cuauhtémoc)',
                'lat': 19.4267,
                'lng': -99.1628,
                'radio_km': 0.8,
                'puntuacion': 6.2,
                'total': 14,
                'panico': 8,
                'accidente': 6
            },

            # ====== ZONAS DE RIESGO MEDIO (4.5 - 5.9) ======
            {
                'nombre': 'Coyoacán Centro',
                'lat': 19.3467,
                'lng': -99.1619,
                'radio_km': 1.0,
                'puntuacion': 5.3,
                'total': 11,
                'panico': 5,
                'accidente': 6
            },
            {
                'nombre': 'Del Valle (Benito Juárez)',
                'lat': 19.3764,
                'lng': -99.1647,
                'radio_km': 1.2,
                'puntuacion': 4.8,
                'total': 9,
                'panico': 4,
                'accidente': 5
            },

            # ====== ZONAS DE BAJO RIESGO (2.5 - 4.4) ======
            {
                'nombre': 'Polanco (Miguel Hidalgo)',
                'lat': 19.4338,
                'lng': -99.1925,
                'radio_km': 1.5,
                'puntuacion': 3.8,
                'total': 6,
                'panico': 2,
                'accidente': 4
            },
            {
                'nombre': 'Roma Norte (Cuauhtémoc)',
                'lat': 19.4178,
                'lng': -99.1626,
                'radio_km': 1.0,
                'puntuacion': 4.2,
                'total': 8,
                'panico': 3,
                'accidente': 5
            },
            {
                'nombre': 'Condesa (Cuauhtémoc)',
                'lat': 19.4110,
                'lng': -99.1728,
                'radio_km': 1.0,
                'puntuacion': 4.0,
                'total': 7,
                'panico': 3,
                'accidente': 4
            },
            {
                'nombre': 'Santa Fe (Álvaro Obregón)',
                'lat': 19.3598,
                'lng': -99.2681,
                'radio_km': 2.0,
                'puntuacion': 3.2,
                'total': 5,
                'panico': 1,
                'accidente': 4
            },
        ]

        self.stdout.write('')
        self.stdout.write('[*] Creando zonas de riesgo con coordenadas reales de CDMX...')

        for zona in zonas_data:
            if not EstadisticaRiesgo.objects.filter(nombre_zona=zona['nombre']).exists():
                # Crear coordenadas en formato correcto para el cálculo de riesgo
                coordenadas_zona = {
                    'center': {
                        'lat': zona['lat'],
                        'lng': zona['lng']
                    },
                    'radio_km': zona['radio_km'],
                    'type': 'circle'
                }

                EstadisticaRiesgo.objects.create(
                    nombre_zona=zona['nombre'],
                    coordenadas_zona=coordenadas_zona,
                    puntuacion_riesgo=zona['puntuacion'],
                    total_alertas=zona['total'],
                    alertas_panico=zona['panico'],
                    alertas_accidente=zona['accidente'],
                    periodo_inicio=date.today() - timedelta(days=30),
                    periodo_fin=date.today()
                )

                # Indicador según nivel de riesgo
                if zona['puntuacion'] >= 7.5:
                    indicador = '[ALTO]'
                elif zona['puntuacion'] >= 6.0:
                    indicador = '[MED-ALTO]'
                elif zona['puntuacion'] >= 4.5:
                    indicador = '[MEDIO]'
                else:
                    indicador = '[BAJO]'

                self.stdout.write(self.style.SUCCESS(
                    f'{indicador} [OK] Zona creada: {zona["nombre"]} '
                    f'(Riesgo: {zona["puntuacion"]}/10, Radio: {zona["radio_km"]}km)'
                ))
            else:
                # Actualizar zona existente con nuevas coordenadas
                zona_obj = EstadisticaRiesgo.objects.get(nombre_zona=zona['nombre'])
                coordenadas_zona = {
                    'center': {
                        'lat': zona['lat'],
                        'lng': zona['lng']
                    },
                    'radio_km': zona['radio_km'],
                    'type': 'circle'
                }
                zona_obj.coordenadas_zona = coordenadas_zona
                zona_obj.puntuacion_riesgo = zona['puntuacion']
                zona_obj.total_alertas = zona['total']
                zona_obj.alertas_panico = zona['panico']
                zona_obj.alertas_accidente = zona['accidente']
                zona_obj.save()

                self.stdout.write(self.style.WARNING(
                    f'[!] Zona actualizada: {zona["nombre"]} (Riesgo: {zona["puntuacion"]}/10)'
                ))

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
