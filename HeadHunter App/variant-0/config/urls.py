from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve

from api import views

urlpatterns = [
    path('api/register', views.register),
    path('api/login', views.login),
    path('api/vacancies', views.vacancies),
    path('api/applications', views.applications),
    path('api/applications/<int:application_id>/withdraw', views.withdraw),
    path('api/profile', views.profile),

    # Логотипы компаний раздаются по пути /images/... (как в seed.sql)
    re_path(r'^images/(?P<path>.*)$', serve, {'document_root': settings.STATIC_DIR / 'images'}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_DIR}),

    path('', views.frontend_index),
    re_path(r'^(?P<path>.+\.(?:html|css|js))$', serve, {'document_root': settings.FRONTEND_DIR}),
]
