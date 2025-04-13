from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Vendor, Wishlist, EmailConfirmationToken, NewsletterSubscriber
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'city', 'is_vendor']
    search_fields = ['user__username', 'user__email', 'city']
    list_filter = ['is_vendor', 'country']

class VendorAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'profile_user', 'has_identity_document', 'is_approved', 'approval_actions']
    search_fields = ['shop_name', 'profile__user__username', 'profile__user__email']
    list_filter = ['is_approved', 'created']
    readonly_fields = ['created', 'updated', 'view_identity_document']
    actions = ['approve_vendors']
    fieldsets = [
        ('Informations du vendeur', {
            'fields': ('profile', 'shop_name', 'description', 'logo', 'phone')
        }),
        ('Documents', {
            'fields': ('view_identity_document',)
        }),
        ('Statut', {
            'fields': ('is_approved', 'created', 'updated')
        }),
    ]
    
    def profile_user(self, obj):
        return obj.profile.user.username
    profile_user.short_description = 'Utilisateur'
    
    def has_identity_document(self, obj):
        if obj.identity_document:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_identity_document.short_description = 'Pièce d\'identité'
    
    def view_identity_document(self, obj):
        if obj.identity_document:
            return format_html('<a href="{}" target="_blank">Voir le document</a>', obj.identity_document.url)
        return "Aucun document"
    view_identity_document.short_description = 'Voir la pièce d\'identité'
    
    def approval_actions(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green;">Approuvé</span>')
        return format_html(
            '<a class="button" href="{}">Approuver</a>',
            f"/admin/Hackerz/vendor/{obj.id}/approve/"
        )
    approval_actions.short_description = 'Actions'
    
    def approve_vendors(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(
            request,
            f"{count} vendeur{'s' if count > 1 else ''} {'ont' if count > 1 else 'a'} été approuvé{'s' if count > 1 else ''}."
        )
    approve_vendors.short_description = "Approuver les vendeurs sélectionnés"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:vendor_id>/approve/',
                self.admin_site.admin_view(self.approve_vendor),
                name='vendor-approve',
            ),
        ]
        return custom_urls + urls
    
    def approve_vendor(self, request, vendor_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        
        vendor = get_object_or_404(Vendor, id=vendor_id)
        vendor.is_approved = True
        vendor.save()
        
        messages.success(request, f"Le vendeur {vendor.shop_name} a été approuvé avec succès.")
        return redirect('admin:Hackerz_vendor_changelist')

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_count', 'created']
    search_fields = ['user__username', 'user__email']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Nombre de produits'

class EmailConfirmationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created', 'is_valid']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'created']

class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'created', 'updated']
    list_filter = ['is_active', 'created', 'updated']
    search_fields = ['email']
    date_hierarchy = 'created'
    readonly_fields = ['created', 'updated']
    actions = ['activate_subscribers', 'deactivate_subscribers', 'send_test_email']
    
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} abonnés ont été activés.")
    activate_subscribers.short_description = "Activer les abonnés sélectionnés"
    
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} abonnés ont été désactivés.")
    deactivate_subscribers.short_description = "Désactiver les abonnés sélectionnés"
    
    def send_test_email(self, request, queryset):
        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils.html import strip_tags
        
        subject = "Test de newsletter Hackerz"
        html_message = """
        <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { text-align: center; padding: 20px 0; }
                    .header h1 { color: #00ff41; margin: 0; }
                    .content { padding: 20px 0; }
                    .footer { text-align: center; font-size: 12px; color: #999; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Hackerz Newsletter</h1>
                    </div>
                    <div class="content">
                        <p>Bonjour,</p>
                        <p>Ceci est un message de test de la newsletter Hackerz.</p>
                        <p>Merci de vous être inscrit à notre newsletter.</p>
                        <p>Cordialement,<br>L'équipe Hackerz</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 Hackerz. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        count = 0
        for subscriber in queryset:
            if subscriber.is_active:
                try:
                    send_mail(
                        subject,
                        strip_tags(html_message),
                        settings.DEFAULT_FROM_EMAIL,
                        [subscriber.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    count += 1
                except Exception as e:
                    self.message_user(request, f"Erreur lors de l'envoi à {subscriber.email}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"E-mail de test envoyé à {count} abonnés actifs.")
    send_test_email.short_description = "Envoyer un e-mail de test aux abonnés sélectionnés"

# Réenregistrer le modèle User avec notre configuration personnalisée
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(EmailConfirmationToken, EmailConfirmationTokenAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin) 