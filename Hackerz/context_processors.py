from Hackerz_E_commerce.models import Category, Cart, CartItem
from Hackerz_blog.models import Post

def global_context(request):
    """
    Ajoute des variables globales au contexte de tous les templates.
    """
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
    
    return {
        'categories': Category.objects.all(),
        'recent_posts': Post.objects.filter(status='published').order_by('-created')[:3],
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
    } 