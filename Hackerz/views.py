from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ContactForm, UserRegistrationForm, LoginForm, UserUpdateForm, ProfileUpdateForm, VendorForm
from Hackerz_E_commerce.models import Product, Category, Order
from Hackerz_blog.models import Post, PostView
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Profile, Wishlist, EmailConfirmationToken
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from Hackerz_blog.models import Tag


def home_view(request):
    featured_products = Product.objects.filter(featured=True, available=True)[:4]
    recent_posts = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags').order_by('-created')[:3]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'recent_posts': recent_posts,
        'categories': categories,
    }
    
    return render(request, 'index.html', context)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Formez le corps du message
            email_message = f"Nom: {name}\nEmail: {email}\nSujet: {subject}\nMessage: {message}"
            
            # Envoi d'email désactivé en mode développement
            # send_mail(subject, email_message, email, [settings.DEFAULT_FROM_EMAIL])
            
            # Ajoutez un message de succès
            messages.success(request, 'Votre message a été envoyé avec succès! Nous vous répondrons bientôt.')
            return redirect('contact')
    else:
        form = ContactForm()
        
    return render(request, 'contact.html', {'form': form})


def login_view(request):
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        # Log pour déboguer
        print(f"Données du formulaire: {request.POST}")
        print(f"Formulaire valide: {form.is_valid()}")
        if not form.is_valid():
            print(f"Erreurs: {form.errors}")
        
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                # Vérifier si l'utilisateur est actif
                if user.is_active:
                    login(request, user)
                    
                    if is_ajax:
                        return JsonResponse({
                            'success': True,
                            'message': f"Bienvenue, {user.username}! Vous êtes maintenant connecté.",
                            'redirect_url': reverse('home')
                        })
                    else:
                        messages.success(request, f"Bienvenue, {user.username}! Vous êtes maintenant connecté.")
                return redirect('home')
            else:
                    # L'utilisateur n'est pas actif, proposer de renvoyer l'email de confirmation
                    error_message = "Votre compte n'est pas activé. Veuillez confirmer votre adresse email pour vous connecter."
                    
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': error_message,
                            'inactive_account': True,
                            'redirect_url': reverse('resend_confirmation')
                        }, status=400)
                    else:
                        messages.error(request, error_message)
                        return redirect('resend_confirmation')
        else:
            if is_ajax:
                errors = []
                for field, error_list in form.errors.items():
                    errors.extend(error_list)
                return JsonResponse({
                    'success': False,
                    'message': errors[0] if errors else "Formulaire invalide."
                }, status=400)
            else:
                # Afficher toutes les erreurs
                for error in form.non_field_errors():
                    messages.error(request, error)
    else:
        form = LoginForm()
    
    if is_ajax:
        # Si c'est une requête AJAX GET, retourner le formulaire en HTML
        from django.template.loader import render_to_string
        html = render_to_string('includes/login_form.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    
    return render(request, "login.html", {"form": form})


def register_view(request):
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        # Ajouter du débogage pour voir les données du formulaire
        print(f"Données brutes du formulaire d'inscription: {request.POST}")
        
        form = UserRegistrationForm(request.POST)
        # Vérifier si le formulaire est valide et afficher les erreurs
        print(f"Formulaire d'inscription valide: {form.is_valid()}")
        if not form.is_valid():
            print(f"Erreurs détaillées du formulaire: {form.errors}")
            
        if form.is_valid():
            try:
                # Créer l'utilisateur mais ne pas l'activer
                user = form.save(commit=False)
                user.is_active = False  # L'utilisateur ne pourra pas se connecter tant que l'email n'est pas confirmé
                user.save()
                
                # Créer un token de confirmation
                token = EmailConfirmationToken.objects.create(user=user)
                
                # Obtenir le domaine du site
                current_site = get_current_site(request)
                site_domain = current_site.domain
                
                # Préparer l'email de confirmation
                from django.template.loader import render_to_string
                subject = 'Confirmation de votre inscription sur Hackerz'
                
                # Créer l'URL de confirmation avec le token
                confirm_url = f"http://{site_domain}{reverse('confirm_email', kwargs={'token': token.token})}"
                
                # Rendre le template d'email
                html_message = render_to_string('email/confirm_email.html', {
                    'user': user,
                    'site_domain': site_domain,
                    'confirm_url': confirm_url
                })
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = user.email
                
                try:
                    send_mail(
                        subject,
                        plain_message,
                        from_email,
                        [to_email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi de l'email: {str(e)}")
                
                # Ne pas connecter l'utilisateur automatiquement
                # login(request, user)  # Commenté car l'utilisateur n'est pas encore activé
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': "Inscription réussie! Un email de confirmation a été envoyé à votre adresse email. Veuillez confirmer votre email pour activer votre compte.",
                        'redirect_url': reverse('registration_success')
                    })
                else:
                    messages.success(request, "Inscription réussie! Un email de confirmation a été envoyé à votre adresse email.")
                    return redirect('registration_success')
            except Exception as e:
                # Capturer toute autre exception qui pourrait survenir
                print(f"Erreur lors de l'inscription: {str(e)}")
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': f"Erreur lors de l'inscription: {str(e)}"
                    }, status=500)
                else:
                    messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
                    return redirect('register')
        else:
            if is_ajax:
                errors = []
                for field, error_list in form.errors.items():
                    errors.extend(error_list)
                print(f"Erreurs pour la réponse AJAX: {errors}")
                return JsonResponse({
                    'success': False,
                    'message': errors[0] if errors else "Formulaire invalide."
                }, status=400)
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserRegistrationForm()
        
    if is_ajax:
        # Si c'est une requête AJAX GET, retourner le formulaire en HTML
        from django.template.loader import render_to_string
        html = render_to_string('includes/register_form.html', {'form': form}, request=request)
        return JsonResponse({'html': html})
    
    return render(request, "register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès!")
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    
    # Obtenir les groupes de l'utilisateur
    user_groups = user.groups.all()
    
    is_admin = user.is_superuser or user.groups.filter(name='Administrateurs').exists()
    is_vendor = user.groups.filter(name='Vendeurs').exists() or profile.is_vendor
    is_client = user.groups.filter(name='Clients').exists()
    
    # Récupérer les articles de blog de l'utilisateur
    user_posts = Post.objects.filter(author=user).order_by('-created')
    
    # Récupérer les catégories pour le formulaire de création d'article
    categories = Category.objects.all()
    all_tags = Tag.objects.all()
    
    # Récupérer l'historique des commandes
    user_orders = Order.objects.filter(user=user).order_by('-created')[:5]  # 5 dernières commandes
    
    # Récupérer les tutoriels lus (posts consultés)
    read_tutorials = PostView.objects.filter(user=user).order_by('-timestamp')[:5]  # 5 derniers tutoriels lus
    
    try:
        # Récupérer la liste de souhaits de l'utilisateur
        wishlist = Wishlist.objects.get(user=user)
        wishlist_products = wishlist.products.all()
    except Wishlist.DoesNotExist:
        wishlist_products = []
    
    # Si c'est un vendeur, récupérer les informations de vendeur
    vendor_info = None
    if is_vendor:
        try:
            vendor_info = profile.vendor
        except:
            pass
    
    # Combiner les activités récentes (commandes et tutoriels lus)
    recent_activities = []
    
    # Ajouter les commandes à l'activité récente
    for order in user_orders:
        recent_activities.append({
            'type': 'order',
            'date': order.created,
            'content': order
        })
    
    # Ajouter les tutoriels lus à l'activité récente
    for view in read_tutorials:
        recent_activities.append({
            'type': 'tutorial',
            'date': view.timestamp,
            'content': view.post
        })
    
    # Trier toutes les activités par date
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    
    context = {
        'user': user,
        'profile': profile,
        'posts': user_posts,
        'categories': categories,
        'all_tags': all_tags,
        'wishlist_products': wishlist_products,
        'is_admin': is_admin,
        'is_vendor': is_vendor,
        'is_client': is_client,
        'user_groups': user_groups,
        'vendor_info': vendor_info,
        'recent_activities': recent_activities[:5]  # Limiter à 5 activités les plus récentes
    }
    
    return render(request, 'profile.html', context)


def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Ici, vous pouvez ajouter la logique pour sauvegarder l'email dans votre base de données
            # ou l'envoyer à votre service de newsletter
            messages.success(request, "Merci de votre inscription à notre newsletter!")
        else:
            messages.error(request, "Veuillez fournir une adresse email valide.")
    return redirect('home') 


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # TODO: Implémenter la logique d'inscription à la newsletter
            messages.success(request, 'Merci de votre inscription à notre newsletter !')
        else:
            messages.error(request, 'Veuillez fournir une adresse email valide.')
    return redirect('home')


def terms_view(request):
    """Vue pour afficher les conditions d'utilisation."""
    return render(request, 'terms.html')

def privacy_view(request):
    """Vue pour afficher la politique de confidentialité."""
    return render(request, 'privacy.html')

@login_required
def update_account(request):
    """Mise à jour des informations du compte."""
    # Vérifier si l'utilisateur a un profil, sinon en créer un
    try:
        profile = request.user.profile
    except:
        # Créer un profil s'il n'existe pas
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre compte a été mis à jour avec succès.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': user_form,
        'p_form': profile_form
    }

    return render(request, 'update_account.html', context)

@login_required
def become_vendor(request):
    """Permet à un utilisateur de demander à devenir vendeur."""
    # Vérifier si l'utilisateur a un profil, sinon en créer un
    try:
        profile = request.user.profile
    except:
        # Créer un profil s'il n'existe pas
        profile = Profile.objects.create(user=request.user)
    
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if profile.is_vendor:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Vous êtes déjà enregistré comme vendeur.'
            })
        messages.info(request, 'Vous êtes déjà enregistré comme vendeur.')
        return redirect('profile')
    
    if request.method == 'POST':
        vendor_form = VendorForm(request.POST, request.FILES)
        if vendor_form.is_valid():
            vendor = vendor_form.save(commit=False)
            vendor.profile = profile
            vendor.save()
            profile.is_vendor = True
            profile.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Votre demande pour devenir vendeur a été soumise et est en attente d\'approbation.'
                })
            
            messages.success(request, 'Votre demande pour devenir vendeur a été soumise et est en attente d\'approbation.')
            return redirect('profile')
        else:
            # Formulaire invalide
            if is_ajax:
                errors = []
                for field, error_list in vendor_form.errors.items():
                    errors.extend(error_list)
                return JsonResponse({
                    'success': False,
                    'message': errors[0] if errors else "Le formulaire contient des erreurs. Veuillez vérifier les champs."
                }, status=400)
    else:
        vendor_form = VendorForm()
    
    context = {
        'vendor_form': vendor_form
    }
    
    return render(request, 'become_vendor.html', context)

@login_required
def add_to_wishlist(request):
    """Ajouter un produit à la liste de souhaits."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        response_data = {'success': False, 'message': ''}
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                wishlist, created = Wishlist.objects.get_or_create(user=request.user)
                
                if product in wishlist.products.all():
                    wishlist.products.remove(product)
                    response_data['success'] = True
                    response_data['message'] = f"{product.name} a été retiré de votre liste de souhaits."
                    response_data['action'] = 'removed'
                else:
                    wishlist.products.add(product)
                    response_data['success'] = True
                    response_data['message'] = f"{product.name} a été ajouté à votre liste de souhaits."
                    response_data['action'] = 'added'
                
                response_data['wishlist_count'] = wishlist.products.count()
                
            except Product.DoesNotExist:
                response_data['message'] = "Ce produit n'existe pas."
        else:
            response_data['message'] = "ID de produit non fourni."
        
        return JsonResponse(response_data)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})

@login_required
def remove_from_wishlist(request, product_id):
    """Retirer un produit de la liste de souhaits."""
    response_data = {'success': False, 'message': ''}
    
    try:
        product = Product.objects.get(id=product_id)
        wishlist = Wishlist.objects.get(user=request.user)
        
        if product in wishlist.products.all():
            wishlist.products.remove(product)
            response_data['success'] = True
            response_data['message'] = f"{product.name} a été retiré de votre liste de souhaits."
        else:
            response_data['message'] = "Ce produit n'est pas dans votre liste de souhaits."
        
        response_data['wishlist_count'] = wishlist.products.count()
        
    except (Product.DoesNotExist, Wishlist.DoesNotExist):
        response_data['message'] = "Produit ou liste de souhaits introuvable."
    
    return JsonResponse(response_data)

@login_required
def get_wishlist(request):
    """Récupérer la liste de souhaits de l'utilisateur."""
    try:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        products = wishlist.products.all()
        
        context = {
            'wishlist_products': products,
            'wishlist_count': products.count(),
        }
        
        return render(request, 'shop/wishlist.html', context)
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite: {str(e)}")
        return redirect('profile')

class AjaxPasswordResetView(PasswordResetView):
    """Vue personnalisée pour la réinitialisation de mot de passe qui gère les requêtes AJAX."""
    
    def form_valid(self, form):
        # Si c'est une requête AJAX, retourner une réponse JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Traiter le formulaire normalement
            response = super().form_valid(form)
            
            # Retourner une réponse JSON
            return JsonResponse({
                'success': True,
                'message': 'Un email de réinitialisation a été envoyé à l\'adresse indiquée.',
                'redirect_url': self.get_success_url()
            })
        else:
            # Comportement normal pour les requêtes non-AJAX
            return super().form_valid(form)
    
    def form_invalid(self, form):
        # Si c'est une requête AJAX, retourner une réponse JSON avec les erreurs
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, error_list in form.errors.items():
                errors.extend(error_list)
            
            return JsonResponse({
                'success': False,
                'message': errors[0] if errors else "Une erreur s'est produite."
            }, status=400)
        else:
            # Comportement normal pour les requêtes non-AJAX
            return super().form_invalid(form)


class AjaxPasswordResetConfirmView(PasswordResetConfirmView):
    """Vue personnalisée pour la confirmation de réinitialisation de mot de passe qui gère les requêtes AJAX."""
    
    def form_valid(self, form):
        # Si c'est une requête AJAX, retourner une réponse JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Traiter le formulaire normalement
            response = super().form_valid(form)
            
            # Retourner une réponse JSON
            return JsonResponse({
                'success': True,
                'message': 'Votre mot de passe a été réinitialisé avec succès.',
                'redirect_url': self.get_success_url()
            })
        else:
            # Comportement normal pour les requêtes non-AJAX
            return super().form_valid(form)
    
    def form_invalid(self, form):
        # Si c'est une requête AJAX, retourner une réponse JSON avec les erreurs
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, error_list in form.errors.items():
                errors.extend(error_list)
            
            return JsonResponse({
                'success': False,
                'message': errors[0] if errors else "Une erreur s'est produite."
            }, status=400)
        else:
            # Comportement normal pour les requêtes non-AJAX
            return super().form_invalid(form)

def confirm_email(request, token):
    """Vue pour confirmer l'adresse email de l'utilisateur"""
    try:
        email_token = get_object_or_404(EmailConfirmationToken, token=token)
        
        # Vérifier si le token est encore valide
        if email_token.is_valid:
            # Activer l'utilisateur
            user = email_token.user
            user.is_active = True
            user.save()
            
            # Supprimer le token
            email_token.delete()
            
            # Connecter l'utilisateur
            login(request, user)
            
            messages.success(request, "Votre compte a été activé avec succès! Vous êtes maintenant connecté.")
            return redirect('home')
        else:
            # Le token a expiré
            messages.error(request, "Le lien de confirmation a expiré. Veuillez demander un nouveau lien.")
            return redirect('resend_confirmation')
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de la confirmation de votre email: {str(e)}")
        return redirect('home')

def registration_success(request):
    """Page de succès après inscription"""
    return render(request, 'registration_success.html')

def resend_confirmation(request):
    """Vue pour renvoyer l'email de confirmation"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if email:
            try:
                # Chercher l'utilisateur par son email
                user = User.objects.get(email=email, is_active=False)
                
                # Vérifier si un token existe déjà
                try:
                    old_token = EmailConfirmationToken.objects.get(user=user)
                    old_token.delete()
                except EmailConfirmationToken.DoesNotExist:
                    pass
                
                # Créer un nouveau token
                token = EmailConfirmationToken.objects.create(user=user)
                
                # Obtenir le domaine du site
                current_site = get_current_site(request)
                site_domain = current_site.domain
                
                # Préparer l'email de confirmation
                subject = 'Confirmation de votre inscription sur Hackerz'
                
                # Créer l'URL de confirmation avec le token
                confirm_url = f"http://{site_domain}{reverse('confirm_email', kwargs={'token': token.token})}"
                
                # Rendre le template d'email
                html_message = render_to_string('email/confirm_email.html', {
                    'user': user,
                    'site_domain': site_domain,
                    'confirm_url': confirm_url
                })
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                
                # Envoyer l'email
                send_mail(
                    subject,
                    plain_message,
                    from_email,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                messages.success(request, "Un nouvel email de confirmation a été envoyé. Veuillez vérifier votre boîte de réception.")
                
            except User.DoesNotExist:
                # Ne pas révéler que l'utilisateur n'existe pas pour des raisons de sécurité
                messages.success(request, "Si cette adresse email est associée à un compte non activé, un nouvel email de confirmation a été envoyé.")
            except Exception as e:
                messages.error(request, f"Une erreur s'est produite: {str(e)}")
        else:
            messages.error(request, "Veuillez fournir une adresse email valide.")
            
    return render(request, 'resend_confirmation.html')

def resend_confirmation_email(request):
    """Renvoie un email de confirmation à l'utilisateur."""
    # ... existing code ... 

@login_required
def group_users_view(request, group_name):
    """Vue pour afficher les utilisateurs d'un groupe spécifique."""
    # Vérifier si l'utilisateur est administrateur
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrateurs').exists():
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('home')
    
    # Obtenir le groupe
    group = get_object_or_404(Group, name=group_name)
    
    # Obtenir les utilisateurs du groupe
    users = group.user_set.all()
    
    context = {
        'group': group,
        'users': users,
    }
    
    return render(request, 'admin/group_users.html', context) 