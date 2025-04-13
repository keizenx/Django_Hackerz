from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from .models import Post, Category, Tag, Comment, PostView, CommentLike
from django import forms
import markdown
import re
import json
import html
import bleach
import traceback


def convert_markdown(content):
    """
    Convertit le contenu Markdown en HTML avec un formatage amélioré pour les titres, les listes, les blocs de code, etc.
    """
    # Ajuster le contenu pour améliorer la mise en page
    content = preprocess_markdown(content)
    
    # Configuration du parser Markdown avec les extensions
    md = markdown.Markdown(extensions=[
        'markdown.extensions.fenced_code',  # Pour les blocs de code avec ```
        'markdown.extensions.codehilite',   # Pour la coloration syntaxique
        'markdown.extensions.tables',       # Pour les tableaux
        'markdown.extensions.nl2br',        # Convertir les retours à la ligne en <br>
        'markdown.extensions.extra',        # Fonctionnalités supplémentaires comme les footnotes
    ])
    
    # Convertir Markdown en HTML
    html = md.convert(content)
    
    # Améliorer le style des blocs de code
    html = re.sub(r'<pre><code>(.*?)</code></pre>', r'<pre class="code-block"><code>\1</code></pre>', html, flags=re.DOTALL)
    
    # Améliorer les listes à puces
    html = re.sub(r'<ul>\s*<li>', r'<ul class="styled-list">\n<li>', html)
    
    # Améliorer les listes numérotées
    html = re.sub(r'<ol>\s*<li>', r'<ol class="styled-list">\n<li>', html)
    
    return html


def preprocess_markdown(content):
    """
    Prétraite le contenu Markdown pour améliorer le formatage
    """
    # Vérifier s'il commence par un titre, sinon ajouter un titre h1 ou h2 basé sur le premier paragraphe
    if not content.startswith('# ') and not content.startswith('## '):
        # Trouver le premier paragraphe substantiel pour en faire un titre
        paragraphs = content.split('\n\n')
        if paragraphs and len(paragraphs[0]) > 10:
            # Extraire le premier paragraphe comme introduction
            intro = paragraphs[0]
            
            # Essayer de trouver une phrase complète pour le titre
            sentences = re.split(r'(?<=[.!?])\s+', intro)
            if sentences and len(sentences[0]) > 5:
                # Utiliser la première phrase comme titre si elle est assez longue
                title = sentences[0].strip()
                if len(title) > 80:
                    # Si trop long, prendre seulement le début
                    title = title[:80] + '...'
                
                # Insérer un titre h1 au début
                content = f"# {title}\n\n{content}"
    
    # Ajouter un espacement cohérent avant chaque titre
    content = re.sub(r'([^\n])\n(#{1,4}\s)', r'\1\n\n\2', content)
    
    # Améliorer les listes en ajoutant des espaces entre les éléments si nécessaire
    content = re.sub(r'(\n- [^\n]+)(\n- )', r'\1\n\2', content)
    content = re.sub(r'(\n\d+\. [^\n]+)(\n\d+\. )', r'\1\n\2', content)
    
    # Améliorer les blocs de code en s'assurant qu'ils ont un langage spécifié
    content = re.sub(r'```\n', r'```text\n', content)
    
    return content


def post_list(request, category_slug=None):
    category = None
    posts = Post.objects.filter(status='published')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    # Pagination
    paginator = Paginator(posts, 4)  # 4 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-publish')[:3]
    tags = Tag.objects.all()
    
    context = {
        'posts': posts,
        'category': category,
        'categories': categories,
        'recent_posts': recent_posts,
        'tags': tags,
        'page': page,
    }
    
    return render(request, 'blog/blog.html', context)


def post_detail(request, post_slug):
    """Vue pour afficher le détail d'un post de blog et gérer les commentaires"""
    
    # Récupérer l'article
    post = get_object_or_404(Post, slug=post_slug)
    
    # Enregistrer la vue si l'utilisateur est connecté
    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)
    
    # Récupérer les commentaires actifs (commentaires parents uniquement)
    comments = post.comments.filter(active=True, parent=None).order_by('-created')
    
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Débogage détaillé
    print(f"\n{'='*50}")
    print(f"DÉTAIL DE LA REQUÊTE - {timezone.now()}")
    print(f"{'='*50}")
    print(f"Méthode: {request.method}")
    print(f"Est AJAX: {is_ajax}")
    print(f"URL: {request.path}")
    print(f"Utilisateur: {request.user.username if request.user.is_authenticated else 'Anonyme'}")
    
    # Afficher les en-têtes
    print("\nEN-TÊTES:")
    for header, value in request.headers.items():
        print(f"  {header}: {value}")
    
    # Afficher les cookies
    print("\nCOOKIES:")
    for key, value in request.COOKIES.items():
        print(f"  {key}: {value}")
    
    # Afficher les données POST si applicable
    if request.method == 'POST':
        print("\nDONNÉES POST:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        # Afficher les fichiers si présents
        if request.FILES:
            print("\nFICHIERS:")
            for key, value in request.FILES.items():
                print(f"  {key}: {value}")
    
    # Gérer la soumission de commentaire
    if request.method == 'POST':
        action = request.POST.get('action', '')
        print(f"\nAction demandée: {action}")
        
        # Traitement AJAX
        if is_ajax:
            print("Traitement AJAX du commentaire")
            # Code existant pour AJAX...
            pass
        
        # Traitement standard de formulaire (non-AJAX)
        elif action == 'add_comment':
            print("Traitement standard du commentaire")
            
            try:
                # Récupérer les données du formulaire
                if request.user.is_authenticated:
                    name = request.user.username
                    email = request.user.email
                    print(f"Utilisateur authentifié: {name} ({email})")
                else:
                    name = request.POST.get('name', 'Anonyme').strip()
                    email = request.POST.get('email', 'anonyme@example.com').strip()
                    print(f"Utilisateur anonyme: {name} ({email})")
                
                body = request.POST.get('body', '').strip()
                parent_id = request.POST.get('parent_id')
                print(f"Contenu du commentaire: {body}")
                if parent_id:
                    print(f"En réponse au commentaire: {parent_id}")
                
                # Vérifier que le corps du message n'est pas vide
                if not body:
                    print("ERREUR: Corps du commentaire vide")
                    messages.error(request, "Le commentaire ne peut pas être vide")
                    return redirect('blog:post_detail', post_slug=post_slug)
                
                # Gérer le commentaire parent si spécifié
                parent = None
                if parent_id:
                    try:
                        parent = Comment.objects.get(id=parent_id, post=post)
                    except Comment.DoesNotExist:
                        messages.error(request, "Commentaire parent introuvable")
                        return redirect('blog:post_detail', post_slug=post_slug)
                
                # Créer le commentaire
                comment = Comment.objects.create(
                    post=post,
                    name=name,
                    email=email,
                    body=body,
                    parent=parent,
                    active=True
                )
                
                print(f"SUCCÈS: Commentaire créé avec ID {comment.id}")
                messages.success(request, "Votre commentaire a été ajouté avec succès!")
                
                # Réserver le traitement AJAX pour la version future et rediriger 
                # directement pour la version standard
                return redirect('blog:post_detail', post_slug=post_slug)
                
            except Exception as e:
                print(f"EXCEPTION: {str(e)}")
                print("Traceback complet:")
                traceback.print_exc()
                
                messages.error(request, f"Erreur lors de l'ajout du commentaire: {str(e)}")
                return redirect('blog:post_detail', post_slug=post_slug)
    
    # Convertir le contenu Markdown en HTML
    post_content_html = convert_markdown(post.content)
    
    # Trouver des articles similaires
    similar_posts = Post.objects.filter(status='published', category=post.category).exclude(id=post.id)[:3]
    
    # Rendu de la page
    return render(request,
                'blog/post_detail.html',
                {'post': post,
                'post_content_html': post_content_html,
                'comments': comments,
                'similar_posts': similar_posts})


def tag_view(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag, status='published')
    
    # Pagination
    paginator = Paginator(posts, 4)  # 4 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-publish')[:3]
    tags = Tag.objects.all()
    
    context = {
        'tag': tag,
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
        'tags': tags,
        'page': page,
    }
    
    return render(request, 'blog/blog.html', context)


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(category=category, status='published')
    
    # Pagination
    paginator = Paginator(posts, 4)  # 4 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-publish')[:3]
    tags = Tag.objects.all()
    
    context = {
        'category': category,
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
        'tags': tags,
        'page': page,
    }
    
    return render(request, 'blog/blog.html', context)


def add_comment(request, post_slug):
    """
    Ajouter un commentaire à un article (endpoint spécifique)
    """
    # Vérifier si l'utilisateur est connecté
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Veuillez vous connecter pour laisser un commentaire.',
                'redirect': '/login/'
            }, status=401)
        else:
            messages.warning(request, "Veuillez vous connecter pour laisser un commentaire.")
            return redirect('login')
            
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
    
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Récupérer l'article
    post = get_object_or_404(Post, slug=post_slug, status='published')
    
    # Récupérer les données du commentaire
    if is_ajax and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            name = data.get('name', request.user.username).strip()
            email = data.get('email', request.user.email).strip()
            body = data.get('body', '').strip()
            parent_id = data.get('parent_id')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Format JSON invalide'}, status=400)
    else:
        # Utiliser request.POST pour les formulaires
        name = request.POST.get('name', request.user.username).strip()
        email = request.POST.get('email', request.user.email).strip()
        body = request.POST.get('body', '').strip()
        parent_id = request.POST.get('parent_id')
    
    # Vérifier que le corps du message n'est pas vide
    if not body:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Le commentaire ne peut pas être vide'}, status=400)
        else:
            messages.error(request, "Le commentaire ne peut pas être vide")
            return redirect('blog:post_detail', post_slug=post_slug)
    
    # Créer le commentaire
    try:
        # Trouver le commentaire parent si nécessaire
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': 'Commentaire parent introuvable'}, status=404)
                else:
                    messages.error(request, "Commentaire parent introuvable")
                    return redirect('blog:post_detail', post_slug=post_slug)
        
        comment = Comment.objects.create(
            post=post,
            name=name,
            email=email,
            body=body,
            parent=parent,
            active=True
        )
        
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': 'Commentaire ajouté avec succès',
                'comment': {
                    'id': comment.id,
                    'name': comment.name,
                    'body': comment.body,
                    'created': comment.created.strftime('%d/%m/%Y %H:%M'),
                    'is_owner': True,
                    'is_reply': parent is not None,
                    'parent_id': parent.id if parent else None
                },
                'post_id': post.id
            })
        else:
            messages.success(request, "Votre commentaire a été ajouté avec succès!")
            return redirect('blog:post_detail', post_slug=post_slug)
    except Exception as e:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            messages.error(request, f"Erreur lors de l'ajout du commentaire: {str(e)}")
            return redirect('blog:post_detail', post_slug=post_slug)


def add_comment_direct(request, post_slug):
    """
    Ajoute directement un commentaire et redirige vers l'article
    """
    # Accepter les commentaires anonymes si le site le permet
    if request.method != 'POST':
        return redirect('blog:post_detail', post_slug=post_slug)
    
    # Récupérer l'article
    post = get_object_or_404(Post, slug=post_slug, status='published')
    
    # Récupérer les données du formulaire
    if request.user.is_authenticated:
        name = request.user.username
        email = request.user.email
    else:
        name = request.POST.get('name', 'Anonyme').strip()
        email = request.POST.get('email', 'anonyme@example.com').strip()
    
    body = request.POST.get('body', '').strip()
    
    # Vérifier que le corps du message n'est pas vide
    if not body:
        messages.error(request, "Le commentaire ne peut pas être vide")
        return redirect('blog:post_detail', post_slug=post_slug)
    
    # Créer le commentaire
    try:
        Comment.objects.create(
            post=post,
            name=name,
            email=email,
            body=body,
            active=True
        )
        messages.success(request, "Votre commentaire a été ajouté avec succès!")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'ajout du commentaire: {str(e)}")
    
    return redirect('blog:post_detail', post_slug=post_slug)


def auto_add_comment(request, post_slug):
    """
    Ajoute automatiquement un commentaire anonyme avec un texte généré
    """
    try:
        # Récupérer le post
        post = get_object_or_404(Post, slug=post_slug, status='published')
        
        # Créer directement un commentaire avec horodatage
        comment = Comment.objects.create(
            post=post,
            name="Visiteur Anonyme",
            email="anonyme@example.com",
            body="Ceci est un commentaire automatique généré le " + timezone.now().strftime("%d/%m/%Y à %H:%M:%S"),
            active=True
        )
        
        # Rediriger vers la page du post
        return redirect('blog:post_detail', post_slug=post_slug)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


@login_required
def create_post(request):
    """
    Permet à un utilisateur authentifié de créer un nouvel article de blog
    """
    # Ajouter du logging pour diagnotiquer les problèmes
    print("=" * 80)
    print(f"Fonction create_post appelée")
    print(f"Méthode: {request.method}")
    print(f"Authentifié: {request.user.is_authenticated}")
    print(f"Headers: {request.headers}")
    
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    print(f"Est AJAX: {is_ajax}")
    
    if request.method == 'POST':
        print("Données POST reçues:")
        for key, value in request.POST.items():
            if key != 'content':  # Pour éviter d'imprimer tout le contenu
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value[:100]}...")  # Imprimer seulement le début du contenu
        
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        status = request.POST.get('status', 'draft')
        tags_input = request.POST.get('tags', '')
        
        # Validation de base
        if not title or not content or not category_id:
            print(f"Validation échouée: title={bool(title)}, content={bool(content)}, category_id={bool(category_id)}")
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Veuillez remplir tous les champs obligatoires'
                }, status=400)
            else:
                messages.error(request, 'Veuillez remplir tous les champs obligatoires')
                return redirect('profile')
        
        # Récupération de la catégorie
        try:
            category = Category.objects.get(id=category_id)
            print(f"Catégorie trouvée: {category.name}")
        except Category.DoesNotExist:
            print(f"Catégorie non trouvée pour l'ID: {category_id}")
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Catégorie invalide'
                }, status=400)
            else:
                messages.error(request, 'Catégorie invalide')
                return redirect('profile')
        
        try:
            # Création du slug
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            
            # Vérifier que le slug est unique
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Création de l'article
            post = Post.objects.create(
                title=title,
                slug=slug,
                author=request.user,
                category=category,
                content=content,
                status=status
            )
            
            print(f"Article créé avec succès: id={post.id}, slug={post.slug}")
            
            # Ajout de l'image si présente
            if 'image' in request.FILES:
                post.image = request.FILES['image']
                post.save()
                print("Image ajoutée à l'article")
            
            # Traitement des tags
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',')]
                for tag_name in tag_names:
                    if tag_name:
                        # Création du slug du tag
                        tag_slug = slugify(tag_name)
                        
                        # Récupération ou création du tag
                        tag, created = Tag.objects.get_or_create(
                            slug=tag_slug,
                            defaults={'name': tag_name}
                        )
                        
                        # Association du tag à l'article
                        post.tags.add(tag)
                
                print(f"Tags ajoutés: {tags_input}")
            
            # Réponse différente selon le type de requête
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Article créé avec succès',
                    'post_id': post.id,
                    'post_slug': post.slug,
                    'post_url': post.get_absolute_url()
                })
            else:
                messages.success(request, 'Article créé avec succès')
                
                # Redirection vers l'article si publié, sinon vers le profil
                if status == 'published':
                    return redirect('blog:post_detail', post_slug=post.slug)
                else:
                    return redirect(reverse('profile') + '#blog-posts')
                    
        except Exception as e:
            print(f"Erreur lors de la création de l'article: {str(e)}")
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Une erreur est survenue: {str(e)}'
                }, status=500)
            else:
                messages.error(request, f'Une erreur est survenue: {str(e)}')
                return redirect('profile')
    
    # Si ce n'est pas une requête POST
    print("Requête non-POST reçue")
    if is_ajax:
        return JsonResponse({
            'status': 'error',
            'message': 'Méthode non autorisée'
        }, status=405)
    else:
        return redirect('profile')


@login_required
def edit_post(request, post_slug):
    """
    Permet à un utilisateur d'éditer son propre article
    """
    post = get_object_or_404(Post, slug=post_slug)
    
    # Vérifier que l'utilisateur est l'auteur
    if post.author != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cet article")
        return redirect('blog:post_detail', post_slug=post_slug)
    
    # Récupérer toutes les catégories et tous les tags pour le formulaire
    categories = Category.objects.all()
    all_tags = Tag.objects.all()
    
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        status = request.POST.get('status', post.status)
        tags_input = request.POST.get('tags', '')
        
        # Validation de base
        if not title or not content or not category_id:
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Veuillez remplir tous les champs obligatoires'
                }, status=400)
            else:
                messages.error(request, 'Veuillez remplir tous les champs obligatoires')
                return render(request, 'blog/edit_post.html', {'post': post, 'categories': categories, 'all_tags': all_tags})
        
        # Vérifier si le titre a changé
        title_changed = post.title != title
        
        # Mise à jour des champs de base
        post.title = title
        post.content = content
        old_status = post.status
        post.status = status
        
        # Si le statut passe de brouillon à publié, mettre à jour la date de publication
        if old_status == 'draft' and status == 'published':
            post.publish = timezone.now()
        
        # Si le titre a changé, mettre à jour le slug
        if title_changed:
            # Création du slug basé sur le nouveau titre
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            
            # Vérifier que le slug est unique (en excluant l'article actuel)
            while Post.objects.filter(slug=slug).exclude(id=post.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            post.slug = slug
            
            # Mettre à jour la date de publication pour éviter les conflits avec unique_for_date
            post.publish = timezone.now()
        
        # Mise à jour de la catégorie
        try:
            post.category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Catégorie invalide'
                }, status=400)
            else:
                messages.error(request, 'Catégorie invalide')
                return render(request, 'blog/edit_post.html', {'post': post, 'categories': categories, 'all_tags': all_tags})
        
        # Mise à jour de l'image si nécessaire
        if 'image' in request.FILES:
            post.image = request.FILES['image']
            # Mettre à jour la date de publication si une nouvelle image est ajoutée
            post.publish = timezone.now()
        
        try:
            # Enregistrement des modifications
            post.save()
            
            # Mise à jour des tags
            post.tags.clear()
            
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',')]
                for tag_name in tag_names:
                    if tag_name:
                        tag_slug = slugify(tag_name)
                        tag, created = Tag.objects.get_or_create(
                            slug=tag_slug,
                            defaults={'name': tag_name}
                        )
                        post.tags.add(tag)
            
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Article mis à jour avec succès',
                    'post_slug': post.slug,
                    'redirect_url': reverse('blog:post_detail', args=[post.slug])
                })
            else:
                messages.success(request, 'Article mis à jour avec succès')
                return redirect('blog:post_detail', post_slug=post.slug)
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erreur lors de la mise à jour: {str(e)}'
                }, status=500)
            else:
                messages.error(request, f'Erreur lors de la mise à jour: {str(e)}')
                return render(request, 'blog/edit_post.html', {'post': post, 'categories': categories, 'all_tags': all_tags})
    
    # Préparer la liste des tags pour l'affichage
    post_tags = ', '.join([tag.name for tag in post.tags.all()])
    
    return render(request, 'blog/edit_post.html', {
        'post': post,
        'categories': categories,
        'all_tags': all_tags,
        'post_tags': post_tags
    })


@login_required
def publish_post(request, post_id):
    """
    Permet à un utilisateur de publier un article en brouillon
    """
    post = get_object_or_404(Post, id=post_id)
    
    # Vérifier que l'utilisateur est l'auteur
    if post.author != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à publier cet article")
        return redirect('profile')
    
    # Vérifier que l'article est en brouillon
    if post.status != 'draft':
        messages.info(request, "Cet article est déjà publié")
        return redirect('blog:post_detail', post_slug=post.slug)
    
    # Publier l'article
    post.status = 'published'
    post.publish = timezone.now()
    post.save()
    
    messages.success(request, "Article publié avec succès")
    return redirect('blog:post_detail', post_slug=post.slug)


@login_required
def profile_view(request):
    """
    Affiche le profil utilisateur avec ses commandes, liste de souhaits et articles
    """
    # Récupérer les articles de l'utilisateur
    user_posts = Post.objects.filter(author=request.user).order_by('-publish')
    
    # Récupérer les catégories pour le formulaire de création d'article
    categories = Category.objects.all()
    
    # Ajouter ces éléments au contexte
    context = {
        'user_posts': user_posts,
        'categories': categories,
    }
    
    return render(request, 'profile.html', context)


def edit_comment(request, comment_id):
    """
    Vue pour éditer un commentaire existant
    """
    comment = get_object_or_404(Comment, id=comment_id, active=True)
    post = comment.post
    
    # Vérifier si l'utilisateur a le droit de modifier ce commentaire
    if request.user.is_authenticated:
        is_owner = request.user.username == comment.name
        is_staff = request.user.is_staff
    else:
        is_owner = False
        is_staff = False
    
    if not (is_owner or is_staff):
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce commentaire.")
        return redirect('blog:post_detail', post_slug=post.slug)
    
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        
        if not body:
            messages.error(request, "Le commentaire ne peut pas être vide.")
            return render(request, 'blog/edit_comment.html', {'comment': comment})
        
        try:
            # Mettre à jour le commentaire
            comment.body = body
            comment.updated = timezone.now()
            comment.save()
            
            messages.success(request, "Votre commentaire a été modifié avec succès.")
            return redirect('blog:post_detail', post_slug=post.slug)
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    
    # Si méthode GET ou erreur lors de la modification
    return render(request, 'blog/edit_comment.html', {'comment': comment})


def delete_comment(request, comment_id):
    """
    Vue pour supprimer un commentaire
    """
    comment = get_object_or_404(Comment, id=comment_id, active=True)
    post = comment.post
    
    # Vérifier si l'utilisateur a le droit de supprimer ce commentaire
    if request.user.is_authenticated:
        is_owner = request.user.username == comment.name
        is_staff = request.user.is_staff
    else:
        is_owner = False
        is_staff = False
    
    if not (is_owner or is_staff):
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce commentaire.")
        return redirect('blog:post_detail', post_slug=post.slug)
    
    if request.method == 'POST':
        try:
            comment.delete()
            messages.success(request, "Le commentaire a été supprimé avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
    
    return redirect('blog:post_detail', post_slug=post.slug)


def comment_action(request):
    """
    Point d'entrée central pour les actions sur les commentaires via AJAX:
    - add: Ajoute un commentaire
    - edit: Modifie un commentaire existant
    - delete: Supprime un commentaire existant
    - reply: Répond à un commentaire existant
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
    
    # Vérifier si la requête est AJAX
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Requête AJAX attendue'}, status=400)
    
    # Vérifier si l'utilisateur est authentifié
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'message': 'Veuillez vous connecter pour cette action',
            'redirect': '/login/'
        }, status=401)
    
    # Récupérer les données JSON
    try:
        data = json.loads(request.body)
        action = data.get('action')
        post_id = data.get('post_id')
        post_slug = data.get('post_slug')
        comment_id = data.get('comment_id')
        content = data.get('content')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Format JSON invalide'}, status=400)
    
    # Traiter l'action
    try:
        if action == 'add':
            # Récupérer l'article
            post = get_object_or_404(Post, id=post_id)
            
            # Vérifier si l'utilisateur est authentifié ou anonyme
            if request.user.is_authenticated:
                name = request.user.username
                email = request.user.email
            else:
                name = data.get('name', 'Anonyme')
                email = data.get('email', 'anonyme@example.com')
            
            # Vérifier le contenu
            if not content or content.strip() == '':
                return JsonResponse({'success': False, 'message': 'Le commentaire ne peut pas être vide'}, status=400)
            
            # Créer le commentaire
            comment = Comment.objects.create(
                post=post,
                name=name,
                email=email,
                body=content,
                active=True
            )
            
            # Retourner les informations du commentaire
            return JsonResponse({
                'success': True,
                'message': 'Commentaire ajouté avec succès',
                'comment': {
                    'id': comment.id,
                    'name': comment.name,
                    'body': comment.body,
                    'created': comment.created.strftime('%d %b %Y'),
                    'is_owner': request.user.is_authenticated and request.user.username == comment.name
                }
            })
        
        elif action == 'edit':
            # Récupérer le commentaire
            comment = get_object_or_404(Comment, id=comment_id)
            
            # Vérifier les permissions
            if request.user.is_authenticated and request.user.username != comment.name and not request.user.is_staff:
                return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à modifier ce commentaire'}, status=403)
            
            # Vérifier le contenu
            if not content or content.strip() == '':
                return JsonResponse({'success': False, 'message': 'Le commentaire ne peut pas être vide'}, status=400)
            
            # Mettre à jour le commentaire
            comment.body = content
            comment.updated = timezone.now()
            comment.save()
            
            # Retourner le commentaire mis à jour
            return JsonResponse({
                'success': True,
                'message': 'Commentaire mis à jour avec succès',
                'comment': {
                    'id': comment.id,
                    'body': comment.body,
                    'updated': comment.updated.strftime('%d %b %Y')
                }
            })
        
        elif action == 'delete':
            # Récupérer le commentaire
            comment = get_object_or_404(Comment, id=comment_id)
            
            # Vérifier les permissions
            if request.user.is_authenticated and request.user.username != comment.name and not request.user.is_staff:
                return JsonResponse({'success': False, 'message': 'Vous n\'êtes pas autorisé à supprimer ce commentaire'}, status=403)
            
            # Supprimer le commentaire
            comment.delete()
            
            # Retourner un message de succès
            return JsonResponse({
                'success': True,
                'message': 'Commentaire supprimé avec succès'
            })
            
        elif action == 'reply':
            # Récupérer le commentaire parent
            parent_comment = get_object_or_404(Comment, id=comment_id)
            post = parent_comment.post
            
            # Vérifier les permissions
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'message': 'Vous devez être connecté pour répondre à un commentaire'}, status=403)
            
            # Vérifier le contenu
            if not content or content.strip() == '':
                return JsonResponse({'success': False, 'message': 'La réponse ne peut pas être vide'}, status=400)
            
            # Créer la réponse comme un commentaire enfant
            reply = Comment.objects.create(
                post=post,
                name=request.user.username,
                email=request.user.email,
                body=content,
                parent=parent_comment,
                active=True
            )
            
            # Retourner les informations de la réponse
            return JsonResponse({
                'success': True,
                'message': 'Réponse ajoutée avec succès',
                'comment': {
                    'id': reply.id,
                    'name': reply.name,
                    'body': reply.body,
                    'created': reply.created.strftime('%d/%m/%Y %H:%M'),
                    'is_owner': True
                }
            })
            
        elif action == 'like':
            # Récupérer le commentaire
            comment = get_object_or_404(Comment, id=comment_id)
            
            # Vérifier si l'utilisateur a déjà liké ce commentaire
            like, created = CommentLike.objects.get_or_create(
                user=request.user,
                comment=comment
            )
            
            # Si le like existait déjà, on le supprime (unlike)
            if not created:
                like.delete()
                liked = False
                message = 'Like retiré avec succès'
            else:
                liked = True
                message = 'Commentaire liké avec succès'
            
            # Récupérer le nombre total de likes
            likes_count = comment.likes_count()
            
            # Retourner les informations sur le like
            return JsonResponse({
                'success': True,
                'message': message,
                'liked': liked,
                'likes_count': likes_count,
                'comment_id': comment.id
            })
            
        else:
            return JsonResponse({'success': False, 'message': 'Action inconnue'}, status=400)
    
    except Exception as e:
        print(f"Erreur dans comment_action: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'message': f'Erreur serveur: {str(e)}'}, status=500)