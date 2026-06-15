"""REST API эндпоинты Kolesa App. Сервер отдаёт только JSON."""
import json
import os

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.static import serve

from .models import User, Ad
from .auth import issue_token, login_required


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


def _fields(request):
    """Поддержка и JSON, и multipart/form-data (для формы с фото)."""
    if request.content_type and 'application/json' in request.content_type:
        return _body(request)
    return request.POST


def _img(path):
    if not path:
        return ''
    return path if path.startswith('/') else '/static/' + path


def _ad_dict(a):
    return {
        'id': a.id,
        'brand': a.brand,
        'model': a.model,
        'year': a.year,
        'price': a.price,
        'description': a.description,
        'image_path': _img(a.image_path),
        'status': a.status,
        'seller_name': a.user.full_name,
        'seller_phone': a.user.phone_number,
    }


# ---------- Авторизация ----------

def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    full_name = (data.get('full_name') or '').strip()
    phone = (data.get('phone_number') or '').strip()
    if not username or not password or not full_name or not phone:
        return JsonResponse({'error': 'Все поля обязательны (включая телефон)'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Пользователь с таким логином уже существует'}, status=400)
    user = User.objects.create(
        username=username, password_hash=make_password(password),
        full_name=full_name, phone_number=phone,
    )
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


# ---------- Доска объявлений ----------

def cars(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    qs = Ad.objects.filter(status='active').select_related('user')
    brand = request.GET.get('brand')
    year_from = request.GET.get('year_from')
    year_to = request.GET.get('year_to')
    sort = request.GET.get('sort')
    if brand:
        qs = qs.filter(brand__icontains=brand)
    if year_from:
        qs = qs.filter(year__gte=year_from)
    if year_to:
        qs = qs.filter(year__lte=year_to)
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    else:
        qs = qs.order_by('-id')
    return JsonResponse([_ad_dict(a) for a in qs], safe=False)


# ---------- Создание / снятие объявления ----------

@login_required
def ads(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    f = _fields(request)
    brand = (f.get('brand') or '').strip()
    model = (f.get('model') or '').strip()
    description = (f.get('description') or '').strip()
    try:
        year = int(f.get('year'))
        price = int(f.get('price'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Год и цена должны быть числами'}, status=400)
    if not brand or not model:
        return JsonResponse({'error': 'Марка и модель обязательны'}, status=400)
    if price <= 0:
        return JsonResponse({'error': 'Цена должна быть больше 0'}, status=400)

    ad = Ad.objects.create(
        user=request.current_user, brand=brand, model=model, year=year,
        price=price, description=description, status='active',
    )
    # Опциональная загрузка фото авто
    file = request.FILES.get('image')
    if file:
        ext = os.path.splitext(file.name)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png'):
            folder = os.path.join(settings.MEDIA_ROOT, 'cars')
            os.makedirs(folder, exist_ok=True)
            filename = f'ad_{ad.id}{ext}'
            with open(os.path.join(folder, filename), 'wb') as dst:
                for chunk in file.chunks():
                    dst.write(chunk)
            ad.image_path = f'/media/cars/{filename}'
            ad.save(update_fields=['image_path'])
    return JsonResponse({'id': ad.id}, status=201)


@login_required
def mark_sold(request, ad_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    ad = Ad.objects.filter(id=ad_id, user=request.current_user).first()
    if not ad:
        return JsonResponse({'error': 'Объявление не найдено'}, status=404)
    ad.status = 'sold'
    ad.save(update_fields=['status'])
    return JsonResponse({'id': ad.id, 'status': ad.status})


# ---------- Профиль ----------

@login_required
def profile(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    user = request.current_user
    my_ads = Ad.objects.filter(user=user).select_related('user').order_by('-id')
    return JsonResponse({
        'user': {
            'id': user.id, 'username': user.username, 'full_name': user.full_name,
            'phone_number': user.phone_number, 'avatar_path': user.avatar_path,
        },
        'ads': [_ad_dict(a) for a in my_ads],
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
    return serve(request, 'cars.html', document_root=settings.FRONTEND_DIR)
