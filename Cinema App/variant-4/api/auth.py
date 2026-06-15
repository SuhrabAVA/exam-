"""Простая авторизация по токену."""
import secrets
from django.http import JsonResponse
from .models import Token


def issue_token(user):
    # генерируем случайный токен и сохраняем в таблицу tokens
    key = secrets.token_hex(16)
    Token.objects.create(key=key, user=user)
    return key


def get_user(request):
    # достаём пользователя по токену из заголовка Authorization
    header = request.headers.get('Authorization', '')
    if header.startswith('Bearer '):
        key = header.replace('Bearer ', '')
        token = Token.objects.filter(key=key).first()
        if token:
            return token.user
    return None


def login_required(view):
    # проверяем токен перед тем как пустить в эндпоинт
    def wrapper(request, *args, **kwargs):
        user = get_user(request)
        if user is None:
            return JsonResponse({'error': 'Сначала войдите в систему'}, status=401)
        request.current_user = user
        return view(request, *args, **kwargs)
    return wrapper
