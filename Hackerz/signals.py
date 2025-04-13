from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

from Hackerz.models import Profile, Vendor
from Hackerz_E_commerce.models import Order
from Hackerz_blog.models import Post

# Déplacer la création des groupes dans une fonction pour éviter l'accès à la base de données à l'import
def ensure_groups_exist():
    admin_group, _ = Group.objects.get_or_create(name='Administrateurs')
    seller_group, _ = Group.objects.get_or_create(name='Vendeurs')
    client_group, _ = Group.objects.get_or_create(name='Clients')
    return admin_group, seller_group, client_group

# Fonction pour ajouter un utilisateur au groupe Admin
def make_admin(user):
    admin_group, _, _ = ensure_groups_exist()
    user.is_staff = True
    user.is_superuser = True
    user.save()
    admin_group.user_set.add(user)

# Fonction pour ajouter un utilisateur au groupe Vendeur quand sa demande est approuvée
@receiver(post_save, sender='Hackerz.Vendor')
def vendor_approval_handler(sender, instance, **kwargs):
    if instance.is_approved:
        _, seller_group, _ = ensure_groups_exist()
        user = instance.profile.user
        seller_group.user_set.add(user)
        # S'assurer que l'utilisateur a également le flag is_vendor
        profile = user.profile
        profile.is_vendor = True
        profile.save()

# Fonction pour ajouter un utilisateur au groupe Client quand il passe une commande
@receiver(post_save, sender='Hackerz_E_commerce.Order')
def order_creation_handler(sender, instance, created, **kwargs):
    if created:
        # Utiliser une fonction pour obtenir le groupe client
        _, _, client_group = ensure_groups_exist()
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