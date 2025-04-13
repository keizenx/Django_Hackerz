"""
URL configuration for hackerz_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.tag_view, name='tag_view'),
    path('category/<slug:category_slug>/', views.category_view, name='category_view'),
    path('post/<slug:post_slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:post_slug>/comment/', views.add_comment, name='add_comment'),
    path('post/<slug:post_slug>/comment/direct/', views.add_comment_direct, name='add_comment_direct'),
    path('post/<slug:post_slug>/comment/auto/', views.auto_add_comment, name='auto_add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/action/', views.comment_action, name='comment_action'),
    
    # Correction des URLs pour la gestion des articles
    path('create/', views.create_post, name='create_post'),
    path('post/edit/<slug:post_slug>/', views.edit_post, name='edit_post'),
    path('post/publish/<int:post_id>/', views.publish_post, name='publish_post'),
]

