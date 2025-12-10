from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, RepartidorProfile


@receiver(post_save, sender=User)
def crear_perfil_repartidor(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil de repartidor cuando se crea un usuario con rol 'repartidor'
    Solo si no existe ya un perfil (para evitar conflictos con registro manual)
    """
    if created and instance.rol == 'repartidor':
        # Verificar si ya existe un perfil para este usuario
        if not RepartidorProfile.objects.filter(user=instance).exists():
            # Generar un número de identificación único
            numero_id = f"REP-{instance.id:06d}"
            RepartidorProfile.objects.create(
                user=instance,
                numero_identificacion=numero_id
            )
