from django.db import models
from django.contrib.auth.models import User
from Hackerz_E_commerce.models import Product
import uuid
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """Modèle pour les informations supplémentaires de l'utilisateur."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='france')
    is_vendor = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

# Signal pour créer automatiquement un profil lorsqu'un utilisateur est créé
@receiver(post_save, sender='auth.User')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender='auth.User')
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

class Vendor(models.Model):
    """Modèle pour les vendeurs sur la plateforme."""
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='vendor')
    shop_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='vendors/logos/', blank=True, null=True)
    identity_document = models.FileField(upload_to='vendors/documents/', blank=True, null=True)
    siret = models.CharField(max_length=14, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shop_name


class Wishlist(models.Model):
    """Modèle pour la liste de souhaits d'un utilisateur."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='in_wishlists', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Liste de souhaits de {self.user.username}"


class EmailConfirmationToken(models.Model):
    """Modèle pour les tokens de confirmation d'email."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_token')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_valid(self):
        """Vérifie si le token est encore valide (moins de 24 heures)."""
        return self.created + timedelta(hours=24) > timezone.now()
    
    def __str__(self):
        return f"Token de confirmation pour {self.user.email}"

class NewsletterSubscriber(models.Model):
    """Modèle pour les abonnés à la newsletter."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Abonné à la newsletter"
        verbose_name_plural = "Abonnés à la newsletter" 