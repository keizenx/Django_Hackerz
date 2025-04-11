from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, Post, Comment, Tag
from django.utils.safestring import mark_safe
from django import forms


class CommentAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour les commentaires dans l'admin"""
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        required=False,
        label="Utilisateur",
        help_text="Sélectionnez un utilisateur existant ou laissez vide pour 'Anonyme'"
    )
    
    class Meta:
        model = Comment
        fields = ['post', 'user', 'body', 'active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        # Si c'est un commentaire existant, essayer de trouver l'utilisateur correspondant
        if instance and instance.pk:
            try:
                user = User.objects.get(username=instance.name)
                self.initial['user'] = user.id
            except User.DoesNotExist:
                pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', '-publish']
    autocomplete_fields = ['category', 'tags']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm
    list_display = ['name', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'body']
    
    # Utiliser autocomplete_fields pour le champ post
    autocomplete_fields = ['post']
    
    # Liste des champs à afficher dans le formulaire (sans name ni email)
    fields = ['post', 'user', 'body', 'active']
    
    def save_model(self, request, obj, form, change):
        # Récupérer l'utilisateur sélectionné dans le formulaire
        user = form.cleaned_data.get('user')
        
        if user:
            # Si un utilisateur est sélectionné, utiliser son nom d'utilisateur et son email
            obj.name = user.username
            obj.email = user.email
        else:
            # Si aucun utilisateur n'est sélectionné, utiliser "Anonyme"
            obj.name = 'Anonyme'
            obj.email = 'anonyme@example.com'
        
        super().save_model(request, obj, form, change) 