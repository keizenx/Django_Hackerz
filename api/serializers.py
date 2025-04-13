from rest_framework import serializers
from django.contrib.auth.models import User
from Hackerz_E_commerce.models import Product, Category as ShopCategory, Review, Order, OrderItem
from Hackerz_blog.models import Post, Category as BlogCategory, Comment, Tag


# Sérialiseurs pour les utilisateurs
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# Sérialiseurs pour l'e-commerce
class ShopCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCategory
        fields = ['id', 'name', 'slug', 'image', 'description']


class ProductSerializer(serializers.ModelSerializer):
    category = ShopCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    vendor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'image', 'description', 'regular_price', 'price',
            'stock', 'available', 'created', 'updated', 'featured', 'category', 'category_id',
            'vendor_name'
        ]
    
    def get_vendor_name(self, obj):
        if obj.vendor:
            return obj.vendor.shop_name
        return None


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'product_id', 'user', 'rating', 'title', 'comment', 'created', 'updated', 'active']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'address',
            'postal_code', 'city', 'created', 'updated', 'paid', 'status',
            'items', 'total_cost'
        ]
    
    def get_total_cost(self, obj):
        return obj.get_total_cost()


# Sérialiseurs pour le blog
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    post_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'post_id', 'name', 'email', 'body', 'created', 'updated', 'active']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'content', 'image', 'category', 'category_id',
            'tags', 'tag_ids', 'publish', 'created', 'updated', 'status', 'comments_count'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.filter(active=True).count() 