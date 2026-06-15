from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

from api import views

urlpatterns = [
    path('api/register', views.register),
    path('api/login', views.login),
    path('api/categories', views.categories),
    path('api/cities', views.cities),

    path('api/ads', views.ads),                            # GET список / POST создание
    path('api/users/me/ads', views.my_ads),
    path('api/ads/<int:ad_id>/close', views.ad_close),     # PATCH -> sold
    path('api/ads/<int:ad_id>', views.ad_delete),          # DELETE

    path('api/favorites', views.favorites),                # GET / POST
    path('api/favorites/<int:ad_id>', views.favorite_delete),  # DELETE

    path('api/profile', views.profile),
    path('api/profile/avatar', views.avatar),

    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_DIR}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    path('', views.frontend_index),
    re_path(r'^(?P<path>.+\.(?:html|css|js))$', serve, {'document_root': settings.FRONTEND_DIR}),
]
