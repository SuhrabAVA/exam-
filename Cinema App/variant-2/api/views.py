"""REST API эндпоинты Cinema App. Сервер отдаёт только JSON."""
import json
import os
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.static import serve

from .models import User, Movie, Ticket
from .auth import issue_token, login_required

GENRES = {1: 'Боевик', 2: 'Комедия', 3: 'Драма'}


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


def _movie_dict(m):
    return {
        'id': m.id,
        'title': m.title,
        'genre': m.genre,
        'genre_name': GENRES.get(m.genre, 'Другое'),
        'ticket_price': m.ticket_price,
        'age_rating': m.age_rating,
        'description': m.description,
        'poster_path': '/static/' + (m.poster_path or ''),
    }


# ---------- Авторизация ----------

def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    full_name = (data.get('full_name') or '').strip()
    if not username or not password or not full_name:
        return JsonResponse({'error': 'Все поля обязательны'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Пользователь с таким логином уже существует'}, status=400)
    user = User.objects.create(
        username=username,
        password_hash=make_password(password),
        full_name=full_name,
    )
    return JsonResponse({'id': user.id, 'username': user.username, 'full_name': user.full_name}, status=201)


def login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    user = User.objects.filter(username=username).first()
    if not user or not check_password(password, user.password_hash):
        return JsonResponse({'error': 'Неверный логин или пароль'}, status=401)
    token = issue_token(user)
    return JsonResponse({
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'full_name': user.full_name},
    })


# ---------- Афиша ----------

def movies(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    qs = Movie.objects.all()
    genre = request.GET.get('genre')
    age = request.GET.get('age_rating')
    search = request.GET.get('q')
    sort = request.GET.get('sort')
    if genre:
        qs = qs.filter(genre=genre)
    if age:
        qs = qs.filter(age_rating=age)
    if search:
        qs = qs.filter(title__icontains=search)
    if sort == 'price_asc':
        qs = qs.order_by('ticket_price')
    elif sort == 'price_desc':
        qs = qs.order_by('-ticket_price')
    else:
        qs = qs.order_by('id')
    return JsonResponse([_movie_dict(m) for m in qs], safe=False)


# ---------- Покупка билетов ----------

@login_required
def tickets(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    movie = Movie.objects.filter(id=data.get('movie_id')).first()
    if not movie:
        return JsonResponse({'error': 'Фильм не найден'}, status=404)
    try:
        quantity = int(data.get('quantity'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Некорректное количество билетов'}, status=400)
    if quantity < 1:
        return JsonResponse({'error': 'Количество билетов должно быть не меньше 1'}, status=400)
    try:
        show_date = datetime.strptime(data.get('show_date'), '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Некорректная дата сеанса'}, status=400)
    if show_date < date.today():
        return JsonResponse({'error': 'Дата сеанса не может быть в прошлом'}, status=400)
    ticket = Ticket.objects.create(
        user=request.current_user,
        movie=movie,
        show_date=show_date,
        quantity=quantity,
        total_price=movie.ticket_price * quantity,
        status='active',
    )
    return JsonResponse({'id': ticket.id, 'total_price': ticket.total_price}, status=201)


@login_required
def refund(request, ticket_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    ticket = Ticket.objects.filter(id=ticket_id, user=request.current_user).first()
    if not ticket:
        return JsonResponse({'error': 'Билет не найден'}, status=404)
    ticket.status = 'refunded'
    ticket.save(update_fields=['status'])
    return JsonResponse({'id': ticket.id, 'status': ticket.status})


# ---------- Профиль ----------

@login_required
def profile(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    user = request.current_user
    items = (Ticket.objects.filter(user=user).select_related('movie').order_by('-id'))
    return JsonResponse({
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'avatar_path': user.avatar_path,
        },
        'tickets': [{
            'id': t.id,
            'movie_title': t.movie.title,
            'poster_path': '/static/' + (t.movie.poster_path or ''),
            'show_date': t.show_date.strftime('%Y-%m-%d'),
            'quantity': t.quantity,
            'total_price': t.total_price,
            'status': t.status,
        } for t in items],
    })


@login_required
def avatar(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    file = request.FILES.get('avatar')
    if not file:
        return JsonResponse({'error': 'Файл не передан'}, status=400)
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png'):
        return JsonResponse({'error': 'Допустимы только JPG/PNG'}, status=400)
    user = request.current_user
    folder = os.path.join(settings.MEDIA_ROOT, 'avatars')
    os.makedirs(folder, exist_ok=True)
    filename = f'user_{user.id}{ext}'
    with open(os.path.join(folder, filename), 'wb') as dst:
        for chunk in file.chunks():
            dst.write(chunk)
    user.avatar_path = f'/media/avatars/{filename}'
    user.save(update_fields=['avatar_path'])
    return JsonResponse({'avatar_path': user.avatar_path})


# ---------- Раздача фронтенда ----------

def frontend_index(request):
    return serve(request, 'movies.html', document_root=settings.FRONTEND_DIR)
