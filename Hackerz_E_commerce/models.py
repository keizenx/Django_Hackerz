from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import markdown
import re


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:category_view', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    vendor = models.ForeignKey('Hackerz.Vendor', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    description = models.TextField(blank=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def formatted_description(self):
        """
        Retourne la description formatée en HTML à partir du Markdown
        """
        # Si la description est vide, retourner une chaîne vide
        if not self.description:
            return ''
        
        # Configuration du parser Markdown avec les extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',  # Pour les blocs de code avec ```
            'markdown.extensions.codehilite',   # Pour la coloration syntaxique
            'markdown.extensions.tables',       # Pour les tableaux
            'markdown.extensions.nl2br',        # Convertir les retours à la ligne en <br>
            'markdown.extensions.extra',        # Fonctionnalités supplémentaires
        ])
        
        # Amélioration du formatage pour les titres
        content = self.description
        
        # Structurer le contenu avec des espaces autour des titres
        content = content.replace("\n##", "\n\n##")
        content = content.replace("\n#", "\n\n#")
        
        # Améliorer les listes en ajoutant des espaces entre les éléments si nécessaire
        content = re.sub(r'(\n- [^\n]+)(\n- )', r'\1\n\2', content)
        content = re.sub(r'(\n\d+\. [^\n]+)(\n\d+\. )', r'\1\n\2', content)
        
        # Améliorer les blocs de code
        content = re.sub(r'```\n', r'```text\n', content)
        
        # Convertir Markdown en HTML
        html = md.convert(content)
        
        # Améliorer le style des blocs de code
        html = re.sub(r'<pre><code>(.*?)</code></pre>', r'<pre class="code-block"><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # Améliorer les listes à puces
        html = re.sub(r'<ul>\s*<li>', r'<ul class="styled-list">\n<li>', html)
        
        # Améliorer les listes numérotées
        html = re.sub(r'<ol>\s*<li>', r'<ol class="styled-list">\n<li>', html)
        
        return html


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return f'Avis de {self.user.username} sur {self.product.name}'


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date_added']
    
    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)
    
    def sub_total(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.product.name


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.id}'
    
    def get_cost(self):
        return self.price * self.quantity 