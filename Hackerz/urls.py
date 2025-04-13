from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from .views import (
    contact_view, login_view, register_view, logout_view, profile_view,
    newsletter_signup, home_view, newsletter_subscribe, terms_view, privacy_view,
    update_account, add_to_wishlist, remove_from_wishlist, get_wishlist,
    AjaxPasswordResetView, AjaxPasswordResetConfirmView, confirm_email, registration_success,
    resend_confirmation, become_vendor, group_users_view
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('Hackerz_blog.urls', namespace='blog')),
    path('shop/', include('Hackerz_E_commerce.urls', namespace='shop')),
    
    # API URLs
    path('api/v1/', include('api.urls')),
    
    path('', home_view, name='home'),
    path('contact/', contact_view, name='contact'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('newsletter-signup/', newsletter_signup, name='newsletter_signup'),
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico')),
    # path('ckeditor/', include('ckeditor_uploader.urls')),  # Commenté car le module n'est pas installé
    # path('accounts/', include('allauth.urls')),  # Commenté car le module n'est pas installé
    path('update-account/', update_account, name='update_account'),
    path('become-vendor/', become_vendor, name='become_vendor'),
    path('wishlist/add/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', get_wishlist, name='wishlist'),
    
    # URLs pour les emails de confirmation
    path('confirm-email/<uuid:token>/', confirm_email, name='confirm_email'),
    path('registration-success/', registration_success, name='registration_success'),
    path('resend-confirmation/', resend_confirmation, name='resend_confirmation'),
    
    # URLs pour la réinitialisation de mot de passe
    path('password-reset/', AjaxPasswordResetView.as_view(
        template_name='password/password_reset.html',
        email_template_name='password/password_reset_email.html',
        subject_template_name='password/password_reset_subject.txt'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', AjaxPasswordResetConfirmView.as_view(
        template_name='password/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # URLs pour les groupes d'utilisateurs
    path('admin/group/<str:group_name>/', group_users_view, name='group_users'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)