"""REST API эндпоинты Hotel Booking App. Сервер отдаёт только JSON."""
import json
import os
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.static import serve

from .models import User, Room, Booking
from .auth import issue_token, login_required

TYPES = {1: 'Стандарт', 2: 'Делюкс', 3: 'Люкс'}


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


def _room_dict(r):
    return {
        'id': r.id,
        'room_number': r.room_number,
        'type': r.type,
        'type_name': TYPES.get(r.type, 'Номер'),
        'price_per_night': r.price_per_night,
        'capacity': r.capacity,
        'description': r.description,
        'image_path': '/static/' + (r.image_path or ''),
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
    user = User.objects.create(username=username, password_hash=make_password(password), full_name=full_name)
    return JsonResponse({'id': user.id, 'username': user.username, 'full_name': user.full_name}, status=201)


def login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    user = User.objects.filter(username=(data.get('username') or '').strip()).first()
    if not user or not check_password(data.get('password') or '', user.password_hash):
        return JsonResponse({'error': 'Неверный логин или пароль'}, status=401)
    token = issue_token(user)
    return JsonResponse({'token': token, 'user': {'id': user.id, 'username': user.username, 'full_name': user.full_name}})


# ---------- Номера ----------

def rooms(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    qs = Room.objects.all()
    rtype = request.GET.get('type')
    capacity = request.GET.get('capacity')
    sort = request.GET.get('sort')
    if rtype:
        qs = qs.filter(type=rtype)
    if capacity:
        qs = qs.filter(capacity=capacity)
    if sort == 'price_asc':
        qs = qs.order_by('price_per_night')
    elif sort == 'price_desc':
        qs = qs.order_by('-price_per_night')
    else:
        qs = qs.order_by('id')
    return JsonResponse([_room_dict(r) for r in qs], safe=False)


# ---------- Бронирование ----------

@login_required
def bookings(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    room = Room.objects.filter(id=data.get('room_id')).first()
    if not room:
        return JsonResponse({'error': 'Номер не найден'}, status=404)
    try:
        check_in = datetime.strptime(data.get('check_in_date'), '%Y-%m-%d').date()
        check_out = datetime.strptime(data.get('check_out_date'), '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Некорректные даты'}, status=400)
    if check_in < date.today():
        return JsonResponse({'error': 'Дата заезда не может быть в прошлом'}, status=400)
    if check_out <= check_in:
        return JsonResponse({'error': 'Дата выезда должна быть позже даты заезда'}, status=400)
    nights = (check_out - check_in).days
    booking = Booking.objects.create(
        user=request.current_user, room=room,
        check_in_date=check_in, check_out_date=check_out,
        total_price=nights * room.price_per_night, status='active',
    )
    return JsonResponse({'id': booking.id, 'nights': nights, 'total_price': booking.total_price}, status=201)


@login_required
def cancel(request, booking_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    booking = Booking.objects.filter(id=booking_id, user=request.current_user).first()
    if not booking:
        return JsonResponse({'error': 'Бронирование не найдено'}, status=404)
    booking.status = 'cancelled'
    booking.save(update_fields=['status'])
    return JsonResponse({'id': booking.id, 'status': booking.status})


# ---------- Профиль ----------

@login_required
def profile(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    user = request.current_user
    items = Booking.objects.filter(user=user).select_related('room').order_by('-id')
    return JsonResponse({
        'user': {'id': user.id, 'username': user.username, 'full_name': user.full_name, 'avatar_path': user.avatar_path},
        'bookings': [{
            'id': b.id,
            'room_number': b.room.room_number,
            'type_name': TYPES.get(b.room.type, 'Номер'),
            'image_path': '/static/' + (b.room.image_path or ''),
            'check_in_date': b.check_in_date.strftime('%Y-%m-%d'),
            'check_out_date': b.check_out_date.strftime('%Y-%m-%d'),
            'total_price': b.total_price,
            'status': b.status,
        } for b in items],
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


def frontend_index(request):
    return serve(request, 'rooms.html', document_root=settings.FRONTEND_DIR)
