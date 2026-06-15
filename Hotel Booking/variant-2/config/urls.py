from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

from api import views

urlpatterns = [
    path('api/register', views.register),
    path('api/login', views.login),
    path('api/rooms', views.rooms),
    path('api/bookings', views.bookings),
    path('api/bookings/<int:booking_id>/cancel', views.cancel),
    path('api/profile', views.profile),
    path('api/profile/avatar', views.avatar),

    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_DIR}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    path('', views.frontend_index),
    re_path(r'^(?P<path>.+\.(?:html|css|js))$', serve, {'document_root': settings.FRONTEND_DIR}),
]
