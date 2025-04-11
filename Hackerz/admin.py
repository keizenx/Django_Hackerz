from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Vendor, Wishlist, EmailConfirmationToken
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

# Réenregistrer le modèle User avec notre configuration personnalisée
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(EmailConfirmationToken, EmailConfirmationTokenAdmin) 