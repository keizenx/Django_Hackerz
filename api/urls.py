from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

# Configuration de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Hackerz API",
        default_version='v1',
        description="API pour l'application Hackerz - eCommerce et Blog",
        terms_of_service="https://www.hackerz.com/terms/",
        contact=openapi.Contact(email="contact@hackerz.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Configuration du routeur pour l'API RESTful
router = DefaultRouter()

# Routes pour les utilisateurs
router.register(r'users', views.UserViewSet)

# Routes pour l'e-commerce
router.register(r'shop/categories', views.ShopCategoryViewSet, basename='shop-category')
router.register(r'shop/products', views.ProductViewSet)
router.register(r'shop/reviews', views.ReviewViewSet)
router.register(r'shop/orders', views.OrderViewSet, basename='order')

# Routes pour le blog
router.register(r'blog/tags', views.TagViewSet)
router.register(r'blog/categories', views.BlogCategoryViewSet, basename='blog-category')
router.register(r'blog/posts', views.PostViewSet, basename='post')
router.register(r'blog/comments', views.CommentViewSet)

urlpatterns = [
    # API Root
    path('', include(router.urls)),
    
    # Authentication
    path('auth/', include('rest_framework.urls')),
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    
    # Documentation de l'API
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 