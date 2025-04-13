from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
import markdown


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag_view', args=[self.slug])


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_view', args=[self.slug])


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    )
    
    title = models.CharField(max_length=250, verbose_name='Titre')
    slug = models.SlugField(max_length=250, unique_for_date='publish', verbose_name='Slug')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='Auteur')
    content = models.TextField(verbose_name='Contenu')
    image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True, null=True, verbose_name='Image')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name='Catégorie')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name='Tags')
    publish = models.DateTimeField(default=timezone.now, verbose_name='Date de publication')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Statut')
    
    class Meta:
        ordering = ('-publish',)
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])
    
    def formatted_content(self):
        """
        Retourne le contenu formaté en HTML à partir du Markdown
        """
        # Configuration du parser Markdown avec les extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',  # Pour les blocs de code avec ```
            'markdown.extensions.codehilite',   # Pour la coloration syntaxique
            'markdown.extensions.tables',       # Pour les tableaux
            'markdown.extensions.nl2br',        # Convertir les retours à la ligne en <br>
            'markdown.extensions.extra',        # Fonctionnalités supplémentaires
        ])
        
        # Amélioration du formatage pour les titres
        content = self.content
        
        # Structurer le contenu avec des espaces autour des titres
        content = content.replace("\n##", "\n\n##")
        content = content.replace("\n#", "\n\n#")
        
        # Convertir Markdown en HTML
        return md.convert(content)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('created',)
    
    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
    
    def likes_count(self):
        return self.likes.count()


class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
        
    def __str__(self):
        return f'{self.user.username} likes comment {self.comment.id}'


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} a lu {self.post.title}" 