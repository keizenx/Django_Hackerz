from Hackerz_E_commerce.models import Category, Cart, CartItem
from Hackerz_blog.models import Post

def global_context(request):
    """
    Fournit le contexte global pour tous les templates
    """
    context = {}
    
    # Information de l'entreprise pour les factures et autres documents
    context['company_name'] = 'Hackerz E-Commerce'
    context['company_address'] = 'Abidjan, Côte d\'Ivoire'
    context['company_phone'] = '+225 07 50 23 77 10'
    context['company_email'] = 'contact@hackerz-ecommerce.com'
    context['company_website'] = 'www.hackerz-ecommerce.com'
    context['company_siret'] = '123 456 789 00012'
    context['company_tva'] = 'FR 12 345678900'
    
    cart_items_count = 0
    cart_total = 0
    
    if 'cart_id' in request.session:
        try:
            cart = Cart.objects.get(cart_id=request.session['cart_id'])
            cart_items = CartItem.objects.filter(cart=cart, active=True)
            cart_items_count = sum(item.quantity for item in cart_items)
            cart_total = sum(item.sub_total() for item in cart_items)
        except Cart.DoesNotExist:
            pass
    
    context['categories'] = Category.objects.all()
    context['recent_posts'] = Post.objects.filter(status='published').order_by('-created')[:3]
    context['cart_items_count'] = cart_items_count
    context['cart_total'] = cart_total
    
    return context 