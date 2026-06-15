from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

from api import views

urlpatterns = [
    # REST API
    path('api/register', views.register),
    path('api/login', views.login),
    path('api/movies', views.movies),
    path('api/tickets', views.tickets),
    path('api/tickets/<int:ticket_id>/refund', views.refund),
    path('api/profile', views.profile),
    path('api/profile/avatar', views.avatar),

    # Статика (постеры) и загруженные файлы (аватары)
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_DIR}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # Фронтенд (отдельные статические HTML-страницы)
    path('', views.frontend_index),
    re_path(r'^(?P<path>.+\.(?:html|css|js))$', serve, {'document_root': settings.FRONTEND_DIR}),
]
