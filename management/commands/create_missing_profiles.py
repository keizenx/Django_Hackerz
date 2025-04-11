from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Hackerz.models import Profile

class Command(BaseCommand):
    help = 'Crée des profils pour tous les utilisateurs qui n\'en ont pas encore'

    def handle(self, *args, **options):
        users_without_profile = []
        users = User.objects.all()
        
        self.stdout.write(self.style.NOTICE(f'Vérification de {users.count()} utilisateurs...'))
        
        for user in users:
            try:
                # Essayer d'accéder au profil pour voir s'il existe
                profile = user.profile
            except Profile.DoesNotExist:
                # Si le profil n'existe pas, ajouter l'utilisateur à la liste
                users_without_profile.append(user)
        
        if not users_without_profile:
            self.stdout.write(self.style.SUCCESS('Tous les utilisateurs ont déjà un profil.'))
            return
        
        self.stdout.write(self.style.NOTICE(f'Création de profils pour {len(users_without_profile)} utilisateurs...'))
        
        # Créer les profils manquants
        for user in users_without_profile:
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Profil créé pour l\'utilisateur {user.username}'))
        
        self.stdout.write(self.style.SUCCESS(f'{len(users_without_profile)} profils ont été créés avec succès!')) 