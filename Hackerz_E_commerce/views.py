from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review
from django.core.exceptions import ObjectDoesNotExist
import uuid
from django.contrib import messages
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .forms import ReviewForm, ProductForm
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from Hackerz_blog.models import Post, Comment as BlogComment
from decimal import Decimal
from django.urls import reverse


def _cart_id(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart_id = get_random_string(length=32)
        request.session['cart_id'] = cart_id
        print(f"Nouveau cart_id généré: {cart_id}")
    else:
        print(f"Cart_id existant trouvé: {cart_id}")
    
    # S'assurer que le cart_id est associé à un objet Cart
    try:
        Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        # Si le panier n'existe pas dans la base de données, le créer
        Cart.objects.create(cart_id=cart_id)
        print(f"Nouveau Cart créé en base de données pour cart_id: {cart_id}")
    
    return cart_id


def shop(request, category_slug=None):
    category = None
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Filtering
    if 'q' in request.GET:
        query = request.GET.get('q')
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Sorting
    if 'sort' in request.GET:
        sort_by = request.GET.get('sort')
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'newest':
            products = products.order_by('-created')
    
    # Pagination
    paginator = Paginator(products, 6)  # 6 products per page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        products = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    featured_products = Product.objects.filter(featured=True, available=True)[:4]
    
    context = {
        'products': products,
        'category': category,
        'categories': categories,
        'featured_products': featured_products,
        'page': page,
    }
    
    return render(request, 'shop/shop.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, available=True)
    categories = Category.objects.all()
    
    # Get related products
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Get reviews
    reviews = product.reviews.filter(active=True)
    
    # Review form handling
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Votre avis a été ajouté avec succès!')
            return redirect('shop:product_detail', product_slug=product.slug)
    else:
        review_form = ReviewForm()
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    
    context = {
        'product': product,
        'categories': categories,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'shop/product_detail.html', context)


def add_to_cart(request, product_id):
    """Ajouter un produit au panier."""
    # Vérifier si l'utilisateur est connecté
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': "Veuillez vous connecter pour ajouter des produits au panier.",
                'redirect': '/login/'
            }, status=401)
        else:
            messages.warning(request, "Veuillez vous connecter pour ajouter des produits au panier.")
            return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    cart_id = _cart_id(request)
    
    try:
        # Vérifier si le produit est déjà dans le panier
        cart_item = CartItem.objects.get(product=product, cart_id=cart_id)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        # Si le produit n'est pas dans le panier, l'ajouter
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart_id=cart_id
        )
    
    # Préparer la réponse pour AJAX ou redirection normale
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Calculer le nombre total d'articles dans le panier
        cart_items = CartItem.objects.filter(cart_id=cart_id)
        cart_count = sum(item.quantity for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'message': f"{product.name} a été ajouté à votre panier.",
            'cart_count': cart_count
        })
    else:
        return redirect('shop:cart_detail')


def cart(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
            
    except ObjectDoesNotExist:
        pass
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'counter': counter,
    }
    
    return render(request, 'shop/cart.html', context)


def remove_from_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        
    return redirect('shop:cart')


def delete_from_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    
    return redirect('shop:cart')


def checkout(request, total=0, counter=0, cart_items=None):
    """Vue pour afficher la page de paiement."""
    # Initialiser shipping_info par défaut
    shipping_info = {}
    
    try:
        # Récupérer le cart_id correctement
        cart_id = _cart_id(request)
        # Vérifier si le panier existe
        cart = Cart.objects.get(cart_id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        
        # Vérifier si le panier contient des articles
        if not cart_items.exists():
            return render(request, 'shop/checkout.html', {
                'cart_items': None,
                'total': 0,
                'counter': 0,
                'shipping_info': shipping_info
            })
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
        
        # Récupérer les informations d'adresse de livraison de l'utilisateur
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                shipping_info = {
                    'address': profile.address or '',
                    'city': profile.city or '',
                    'postal_code': profile.postal_code or '',
                    'country': profile.country or 'france'
                }
            except:
                shipping_info = {}
            
            # Si l'utilisateur n'a pas d'adresse dans son profil, essayer de récupérer depuis la session
            if not shipping_info.get('address') and 'shipping_address' in request.session:
                session_address = request.session.get('shipping_address', {})
                shipping_info = {
                    'address': session_address.get('address', ''),
                    'city': session_address.get('city', ''),
                    'postal_code': session_address.get('postal_code', ''),
                    'country': session_address.get('country', 'france')
                }
    
    except (Cart.DoesNotExist, Exception) as e:
        # En cas d'erreur, afficher une page vide avec les informations par défaut
        print(f"Erreur lors du chargement du checkout: {str(e)}")
        cart_items = None
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'counter': counter,
        'shipping_info': shipping_info
    }
    
    # Debug pour voir ce qui est passé au template
    print(f"Checkout context: cart_items={cart_items is not None}, total={total}, counter={counter}")
    
    return render(request, 'shop/checkout.html', context)


def cart_detail(request):
    total = 0
    counter = 0
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        
        for cart_item in cart_items:
            cart_item.sub_total = cart_item.product.price * cart_item.quantity
            total += cart_item.sub_total
            counter += cart_item.quantity
            
    except Cart.DoesNotExist:
        cart_items = []
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'cart_total': total,
        'counter': counter
    })


def cart_add(request, product_id):
    """Ajoute un produit au panier via AJAX."""
    # Vérifier si l'utilisateur est connecté
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': "Veuillez vous connecter pour ajouter des produits au panier.",
            'redirect': '/login/'
        }, status=401)
        
    # Vérifier si la requête est AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Récupérer le produit et les données
    product = get_object_or_404(Product, id=product_id)
    
    # Déterminer la quantité à ajouter
    if is_ajax:
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except:
            quantity = 1
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    # S'assurer que la quantité est valide
    if quantity < 1:
        quantity = 1
    
    # Récupérer ou créer le panier
    cart_id = _cart_id(request)
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=cart_id)
    
    # Vérifier si le produit est déjà dans le panier
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=quantity
        )
    
    # Calculer le total du panier
    cart_items = CartItem.objects.filter(cart=cart)
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    # Préparer la réponse
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f"{product.name} a été ajouté à votre panier.",
            'total_items': total_items,
            'total_price': str(total_price),
            'cart_count': total_items
        })
    else:
        messages.success(request, f"{product.name} a été ajouté à votre panier.")
        return redirect('shop:cart')


def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Produit retiré du panier',
            'cart_items_count': sum(item.quantity for item in CartItem.objects.filter(cart=cart, active=True))
        })
    
    return redirect('shop:cart_detail')


def cart_update(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0 and quantity <= product.stock:
        cart_item.quantity = quantity
        cart_item.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Quantité mise à jour',
            'cart_items_count': sum(item.quantity for item in CartItem.objects.filter(cart=cart, active=True))
        })
    
    return redirect('shop:cart_detail')


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, available=True)
    
    # Pagination
    paginator = Paginator(products, 6)  # 6 products per page
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': products,
        'categories': Category.objects.all(),
    }
    
    return render(request, 'shop/shop.html', context)


def add_review(request, product_id):
    """Ajoute un avis sur un produit."""
    # Vérifier si l'utilisateur est connecté
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': 'Veuillez vous connecter pour laisser un avis.',
                'redirect': '/login/'
            }, status=401)
        else:
            messages.warning(request, "Veuillez vous connecter pour laisser un avis.")
            return redirect('login')
    
    # Vérifier si c'est une requête AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        if is_ajax:
            try:
                data = json.loads(request.body)
                rating = int(data.get('rating', 0))
                title = data.get('title', '').strip()
                comment = data.get('comment', '').strip()
            except:
                return JsonResponse({'success': False, 'message': 'Données invalides'}, status=400)
        else:
            rating = int(request.POST.get('rating', 0))
            title = request.POST.get('title', '').strip()
            comment = request.POST.get('comment', '').strip()
        
        # Validation des données
        if rating < 1 or rating > 5:
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'message': 'La note doit être comprise entre 1 et 5'
                }, status=400)
            else:
                messages.error(request, "La note doit être comprise entre 1 et 5")
                return redirect('shop:product_detail', product_slug=product.slug)
        
        if not title:
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'message': 'Le titre ne peut pas être vide'
                }, status=400)
            else:
                messages.error(request, "Le titre ne peut pas être vide")
                return redirect('shop:product_detail', product_slug=product.slug)
        
        if not comment:
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'message': 'Le commentaire ne peut pas être vide'
                }, status=400)
            else:
                messages.error(request, "Le commentaire ne peut pas être vide")
                return redirect('shop:product_detail', product_slug=product.slug)
        
        # Vérifier si l'utilisateur a déjà laissé un avis pour ce produit
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        
        if existing_review:
            # Mettre à jour l'avis existant
            existing_review.rating = rating
            existing_review.title = title
            existing_review.comment = comment
            existing_review.updated = timezone.now()
            existing_review.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Votre avis a été mis à jour avec succès',
                    'review': {
                        'id': existing_review.id,
                        'rating': existing_review.rating,
                        'title': existing_review.title,
                        'comment': existing_review.comment,
                        'created': existing_review.created.strftime('%d/%m/%Y'),
                        'updated': existing_review.updated.strftime('%d/%m/%Y'),
                    }
                })
            else:
                messages.success(request, "Votre avis a été mis à jour avec succès")
                return redirect('shop:product_detail', product_slug=product.slug)
        else:
            # Créer un nouvel avis
            new_review = Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                title=title,
                comment=comment,
                active=True
            )
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Votre avis a été ajouté avec succès',
                    'review': {
                        'id': new_review.id,
                        'rating': new_review.rating,
                        'title': new_review.title,
                        'comment': new_review.comment,
                        'created': new_review.created.strftime('%d/%m/%Y'),
                    }
                })
            else:
                messages.success(request, "Votre avis a été ajouté avec succès")
                return redirect('shop:product_detail', product_slug=product.slug)
    
    # Si ce n'est pas une requête POST, rediriger vers la page du produit
    return redirect('shop:product_detail', product_slug=product.slug)


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        # Debug
        print(f"buy_now: POST request received for product {product_id} with quantity {quantity}")
        
        # S'assurer que la quantité est valide
        if quantity <= 0 or quantity > product.stock:
            messages.error(request, f'Quantité non valide. Stock disponible: {product.stock}')
            return redirect('shop:product_detail', product_slug=product.slug)
        
        # Créer un panier temporaire pour la session
        # Si un panier existe déjà, on le vide pour ne garder que le produit en cours
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            # Supprimer tous les articles existants
            CartItem.objects.filter(cart=cart).delete()
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        
        # Ajouter le produit au panier
        cart_item = CartItem.objects.create(
            product=product,
            quantity=quantity,
            cart=cart
        )
        
        # Debug
        print(f"buy_now: Product added to cart, redirecting to checkout")
        
        # Rediriger vers la page de checkout
        return redirect('shop:checkout')
    
    # Debug
    print(f"buy_now: Request method was {request.method}, not POST")
    
    # Si la méthode n'est pas POST, rediriger vers la page de détail du produit
    return redirect('shop:product_detail', product_slug=product.slug)


def process_payment(request):
    """Vue pour traiter le paiement."""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        shipping_data = {
            'address': request.POST.get('address', ''),
            'city': request.POST.get('city', ''),
            'postal_code': request.POST.get('postal_code', ''),
            'country': request.POST.get('country', 'france')
        }
        
        # Enregistrer l'adresse dans la session pour une utilisation future
        request.session['shipping_address'] = shipping_data
        
        # Si l'utilisateur est connecté, mettre à jour son profil
        if request.user.is_authenticated:
            try:
                from Hackerz.models import Profile
                profile, created = Profile.objects.get_or_create(user=request.user)
                profile.address = shipping_data['address']
                profile.city = shipping_data['city']
                profile.postal_code = shipping_data['postal_code']
                profile.country = shipping_data['country']
                profile.save()
                print(f"Profil utilisateur mis à jour avec adresse: {shipping_data}")
            except Exception as e:
                print(f"Erreur lors de la mise à jour du profil: {str(e)}")
        
        # Simuler le traitement du paiement
        
        try:
            # Récupérer les articles du panier
            cart_id = _cart_id(request)
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart, active=True)
            
            if not cart_items.exists():
                messages.error(request, "Votre panier est vide. Impossible de finaliser la commande.")
                return redirect('shop:checkout')
            
            # Calculer le total
            total = 0
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
            
            # Ajouter la TVA
            total_with_tax = total * Decimal('1.2')
            
            # Créer une commande avec les champs corrects selon le modèle
            order = Order.objects.create(
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                email=request.POST.get('email', ''),
                address=shipping_data['address'],
                postal_code=shipping_data['postal_code'],
                city=shipping_data['city'],
                paid=True,  # Puisque nous simulons un paiement réussi
                status='processing'
            )
            
            # Créer les articles de la commande
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Mettre à jour le stock du produit
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # Vider le panier
            cart_items.delete()
            
            # Debug log pour la commande
            print(f"Commande #{order.id} créée avec succès: {order.first_name} {order.last_name}, {order.email}, {order.status}")
            
            # Retourner une réponse JSON pour AJAX
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'message': 'Votre commande a été passée avec succès!'
            })
        
        except Exception as e:
            print(f"Erreur lors du traitement du paiement: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f"Une erreur est survenue lors du traitement de votre commande: {str(e)}"
            })
    
    # Si la méthode n'est pas POST, rediriger vers la page de checkout
    return redirect('shop:checkout')


def cart_count(request):
    """Retourne le nombre d'articles dans le panier au format JSON"""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        count = sum(item.quantity for item in cart_items)
    except (Cart.DoesNotExist, ObjectDoesNotExist):
        count = 0
    
    return JsonResponse({
        'count': count
    })


@login_required
def profile_view(request):
    # Récupérer le nombre de commandes
    orders_count = Order.objects.filter(email=request.user.email).count()
    
    # Récupérer le nombre d'articles dans la liste de souhaits
    # Note: Ajustez selon votre modèle de liste de souhaits
    wishlist_count = 0
    try:
        if hasattr(request.user, 'wishlist'):
            wishlist_count = request.user.wishlist.products.count()
    except Exception as e:
        print(f"Erreur lors de la récupération de la liste de souhaits: {str(e)}")
    
    # Récupérer le nombre de posts lus (via commentaires ou autre interaction)
    blog_interactions = BlogComment.objects.filter(name=request.user.username).values('post').distinct().count()
    
    # Récupérer les activités récentes
    recent_activities = []
    
    # Commandes récentes
    recent_orders = Order.objects.filter(email=request.user.email).order_by('-created')[:3]
    for order in recent_orders:
        days_ago = (timezone.now().date() - order.created.date()).days
        recent_activities.append({
            'type': 'order',
            'description': f'Commande #{order.id} effectuée',
            'days_ago': days_ago,
            'date': order.created,
            'order': order  # Ajouter une référence à la commande
        })
    
    # Commentaires récents sur le blog
    recent_comments = BlogComment.objects.filter(name=request.user.username).order_by('-created')[:3]
    for comment in recent_comments:
        days_ago = (timezone.now().date() - comment.created.date()).days
        recent_activities.append({
            'type': 'blog',
            'description': f'Article "{comment.post.title}" commenté',
            'days_ago': days_ago,
            'date': comment.created
        })
    
    # Trier toutes les activités par date
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:5]  # Prendre les 5 plus récentes
    
    # Récupérer les commandes pour l'onglet "Mes commandes"
    orders = Order.objects.filter(email=request.user.email).order_by('-created')
    
    # Debug
    print(f"Profile view: orders_count={orders_count}, recent_activities={len(recent_activities)}")
    for activity in recent_activities:
        print(f"Activity: {activity['type']} - {activity['description']} - {activity['date']}")
    
    # Contexte
    context = {
        'orders_count': orders_count,
        'wishlist_count': wishlist_count,
        'blog_interactions': blog_interactions,
        'recent_activities': recent_activities,
        'orders': orders,
    }
    
    return render(request, 'profile.html', context)


@login_required
def update_account(request):
    if request.method == 'POST':
        # Vérifier quel formulaire a été soumis
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal_info':
            # Mise à jour des informations personnelles
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            display_name = request.POST.get('display_name', '')
            email = request.POST.get('email', '')
            
            # Mettre à jour l'utilisateur
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            
            # Si le modèle a un champ display_name, le mettre à jour
            if hasattr(user, 'display_name'):
                user.display_name = display_name
            
            # Vérifier si l'email a changé et s'il n'est pas déjà utilisé
            if email != user.email:
                # Vérifier si l'email est déjà utilisé
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    messages.error(request, 'Cet email est déjà utilisé par un autre compte.')
                    return redirect('profile')
                
                user.email = email
            
            user.save()
            messages.success(request, 'Vos informations personnelles ont été mises à jour avec succès.')
        
        elif form_type == 'shipping_address':
            # Mise à jour de l'adresse de livraison
            address = request.POST.get('address', '')
            city = request.POST.get('city', '')
            postal_code = request.POST.get('postal_code', '')
            country = request.POST.get('country', '')
            
            # Si l'utilisateur a un profil avec une adresse, le mettre à jour
            # Sinon, créer un modèle ShippingAddress lié à l'utilisateur
            from django.db import models
            
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                profile.address = address
                profile.city = city
                profile.postal_code = postal_code
                profile.country = country
                profile.save()
            elif hasattr(request.user, 'shipping_address'):
                shipping_address = request.user.shipping_address
                shipping_address.address = address
                shipping_address.city = city
                shipping_address.postal_code = postal_code
                shipping_address.country = country
                shipping_address.save()
            else:
                # Créer un modèle temporaire pour stocker l'adresse en session
                request.session['shipping_address'] = {
                    'address': address,
                    'city': city,
                    'postal_code': postal_code,
                    'country': country
                }
            
            messages.success(request, 'Votre adresse de livraison a été mise à jour avec succès.')
        
        return redirect('profile')
    
    # Si la méthode n'est pas POST, rediriger vers la page de profil
    return redirect('profile')


@login_required
def vendor_products(request):
    """Liste des produits du vendeur."""
    # Vérifier si l'utilisateur est un vendeur approuvé
    if not hasattr(request.user.profile, 'vendor') or not request.user.profile.vendor.is_approved:
        messages.error(request, "Vous devez être un vendeur approuvé pour accéder à cette page.")
        return redirect('profile')
    
    # Récupérer les produits du vendeur
    products = Product.objects.filter(vendor=request.user.profile.vendor)
    
    # Calculer les statistiques
    products_in_stock = products.filter(stock__gt=0).count()
    products_out_of_stock = products.filter(stock=0).count()
    
    # Récupérer toutes les catégories pour le filtre
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'products_in_stock': products_in_stock,
        'products_out_of_stock': products_out_of_stock,
        'categories': categories,
    }
    
    return render(request, 'shop/vendor/products.html', context)


@login_required
def add_product(request):
    if not request.user.profile.is_vendor:
        messages.error(request, "Vous devez être vendeur pour ajouter des produits.")
        return redirect('become_vendor')
        
    if not request.user.profile.vendor.is_approved:
        messages.warning(request, "Votre compte vendeur n'est pas encore approuvé.")
        return redirect('profile')
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Récupération des données du formulaire
                name = request.POST.get('name')
                category_id = request.POST.get('category')
                price = request.POST.get('price')
                regular_price = request.POST.get('regular_price') or price
                stock = request.POST.get('stock', 0)
                description = request.POST.get('description')
                available = request.POST.get('available') == 'on'
                featured = request.POST.get('featured') == 'on'
                image = request.FILES.get('image')
                
                # Validation des données
                if not all([name, category_id, price, description, image]):
                    return JsonResponse({
                        'success': False,
                        'message': 'Veuillez remplir tous les champs obligatoires.'
                    })
                
                # Création du produit
                product = Product.objects.create(
                    vendor=request.user.profile.vendor,
                    name=name,
                    category_id=category_id,
                    price=price,
                    regular_price=regular_price,
                    stock=stock,
                    description=description,
                    available=available,
                    featured=featured,
                    image=image
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Produit ajouté avec succès!',
                    'redirect_url': reverse('shop:vendor_products')
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
    
    # GET request
    categories = Category.objects.all()
    return render(request, 'shop/add_product.html', {
        'categories': categories
    })


@login_required
def edit_product(request, product_id):
    """Modifier un produit existant."""
    # Vérifier si l'utilisateur est un vendeur approuvé
    if not hasattr(request.user.profile, 'vendor') or not request.user.profile.vendor.is_approved:
        messages.error(request, "Vous devez être un vendeur approuvé pour modifier des produits.")
        return redirect('profile')
    
    product = get_object_or_404(Product, pk=product_id, vendor=request.user.profile.vendor)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Le produit a été modifié avec succès.")
            return redirect('shop:vendor_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'shop/vendor/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Modifier le produit'
    })


@login_required
def delete_product(request, pk):
    """Supprimer un produit."""
    # Vérifier si l'utilisateur est un vendeur approuvé
    if not hasattr(request.user.profile, 'vendor') or not request.user.profile.vendor.is_approved:
        messages.error(request, "Vous devez être un vendeur approuvé pour supprimer des produits.")
        return redirect('profile')
    
    product = get_object_or_404(Product, pk=pk, vendor=request.user.profile.vendor)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Le produit a été supprimé avec succès.")
        return redirect('shop:vendor_products')
    
    return render(request, 'shop/vendor/product_confirm_delete.html', {
        'product': product
    })


@login_required
def vendor_product_detail(request, product_id):
    if not request.user.profile.is_vendor:
        messages.error(request, "Vous devez être vendeur pour accéder à cette page.")
        return redirect('become_vendor')
        
    if not request.user.profile.vendor.is_approved:
        messages.warning(request, "Votre compte vendeur n'est pas encore approuvé.")
        return redirect('profile')
    
    product = get_object_or_404(Product, id=product_id, vendor=request.user.profile.vendor)
    
    # Calculer les statistiques
    total_sales = OrderItem.objects.filter(product=product).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    average_rating = Review.objects.filter(product=product).aggregate(
        avg=Avg('rating')
    )['avg'] or 0
    
    context = {
        'product': product,
        'total_sales': total_sales,
        'average_rating': round(average_rating, 1)
    }
    
    return render(request, 'shop/vendor_product_detail.html', context) 