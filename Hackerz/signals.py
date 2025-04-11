from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from Hackerz.models import Profile, Vendor
from Hackerz_E_commerce.models import Order
from Hackerz_blog.models import Post

# Assurer que les groupes existent
admin_group, _ = Group.objects.get_or_create(name='Administrateurs')
seller_group, _ = Group.objects.get_or_create(name='Vendeurs')
client_group, _ = Group.objects.get_or_create(name='Clients')

# Fonction pour ajouter un utilisateur au groupe Admin
def make_admin(user):
    user.is_staff = True
    user.is_superuser = True
    user.save()
    admin_group.user_set.add(user)

# Fonction pour ajouter un utilisateur au groupe Vendeur quand sa demande est approuvée
@receiver(post_save, sender=Vendor)
def vendor_approval_handler(sender, instance, **kwargs):
    if instance.is_approved:
        user = instance.profile.user
        seller_group.user_set.add(user)
        # S'assurer que l'utilisateur a également le flag is_vendor
        profile = user.profile
        profile.is_vendor = True
        profile.save()

# Fonction pour ajouter un utilisateur au groupe Client quand il passe une commande
@receiver(post_save, sender=Order)
def order_creation_handler(sender, instance, created, **kwargs):
    if created:
        # Supposons que l'ordre a un champ email qui peut être utilisé pour identifier l'utilisateur
        try:
            user = User.objects.get(email=instance.email)
            client_group.user_set.add(user)
        except User.DoesNotExist:
            pass

# Par défaut, chaque nouvel utilisateur est créateur de blog
@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    if created:
        # Aucun groupe particulier n'est nécessaire pour être créateur de blog
        # car tout utilisateur peut créer des posts dans la logique actuelle
        pass 