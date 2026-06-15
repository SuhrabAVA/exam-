"""REST API эндпоинты Krisha App. Сервер отдаёт только JSON."""
import json
import os

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.static import serve

from .models import Category, User, Ad, Favorite
from .auth import issue_token, login_required


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


def _fields(request):
    if request.content_type and 'application/json' in request.content_type:
        return _body(request)
    return request.POST


def _img(path):
    if not path:
        return ''
    return path if path.startswith('/') else '/static/' + path


def _ad_dict(a, favorite_ids=None):
    return {
        'id': a.id,
        'title': a.title,
        'description': a.description,
        'price': a.price,
        'rooms': a.rooms,
        'area': float(a.area) if a.area is not None else None,
        'city': a.city,
        'category': a.category.name,
        'category_id': a.category_id,
        'image_path': _img(a.image_path),
        'status': a.status,
        'created_at': a.created_at.strftime('%Y-%m-%d') if a.created_at else '',
        'seller_name': a.user.full_name,
        'is_favorite': (favorite_ids is not None and a.id in favorite_ids),
    }


# ---------- Авторизация ----------

def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    full_name = (data.get('full_name') or '').strip()
    phone = (data.get('phone') or '').strip()
    if not username or not password or not full_name or not phone:
        return JsonResponse({'error': 'Все поля обязательны'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Пользователь с таким логином уже существует'}, status=400)
    user = User.objects.create(
        username=username, password_hash=make_password(password),
        full_name=full_name, phone=phone,
    )
    token = issue_token(user)
    return JsonResponse({
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'full_name': user.full_name},
    }, status=201)


def login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    user = User.objects.filter(username=(data.get('username') or '').strip()).first()
    if not user or not check_password(data.get('password') or '', user.password_hash):
        return JsonResponse({'error': 'Неверный логин или пароль'}, status=401)
    token = issue_token(user)
    return JsonResponse({
        'token': token,
        'user': {'id': user.id, 'username': user.username, 'full_name': user.full_name},
    })


# ---------- Справочники ----------

def categories(request):
    return JsonResponse([{'id': c.id, 'name': c.name} for c in Category.objects.all().order_by('id')], safe=False)


def cities(request):
    vals = Ad.objects.values_list('city', flat=True).distinct().order_by('city')
    return JsonResponse(list(vals), safe=False)


# ---------- Лента объявлений ----------

def ads(request):
    if request.method == 'POST':
        return _create_ad(request)
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    qs = Ad.objects.filter(status='active').select_related('user', 'category')
    g = request.GET
    if g.get('city'):
        qs = qs.filter(city=g['city'])
    if g.get('category'):
        qs = qs.filter(category_id=g['category'])
    if g.get('price_from'):
        qs = qs.filter(price__gte=g['price_from'])
    if g.get('price_to'):
        qs = qs.filter(price__lte=g['price_to'])
    rooms = g.get('rooms')
    if rooms not in (None, '', 'all'):
        if rooms == '4':
            qs = qs.filter(rooms__gte=4)
        else:
            qs = qs.filter(rooms=rooms)
    if g.get('q'):
        qs = qs.filter(title__icontains=g['q'])
    sort = g.get('sort')
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    else:
        qs = qs.order_by('-created_at', '-id')
    return JsonResponse([_ad_dict(a) for a in qs], safe=False)


def _create_ad(request):
    from .auth import get_user
    user = get_user(request)
    if not user:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    f = _fields(request)
    title = (f.get('title') or '').strip()
    city = (f.get('city') or '').strip()
    description = (f.get('description') or '').strip()
    try:
        category_id = int(f.get('category_id'))
        price = int(f.get('price'))
        rooms = int(f.get('rooms') or 0)
        area = float(f.get('area'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Категория, цена, комнаты и площадь должны быть числами'}, status=400)
    if not title:
        return JsonResponse({'error': 'Заголовок не может быть пустым'}, status=400)
    if not city:
        return JsonResponse({'error': 'Город не может быть пустым'}, status=400)
    if price <= 0:
        return JsonResponse({'error': 'Цена должна быть больше 0'}, status=400)
    if rooms < 0:
        return JsonResponse({'error': 'Количество комнат не может быть отрицательным'}, status=400)
    if area <= 0:
        return JsonResponse({'error': 'Площадь должна быть больше 0'}, status=400)
    if not Category.objects.filter(id=category_id).exists():
        return JsonResponse({'error': 'Категория не найдена'}, status=400)

    ad = Ad.objects.create(
        user=user, category_id=category_id, title=title, description=description,
        price=price, rooms=rooms, area=area, city=city, status='active',
    )
    file = request.FILES.get('image')
    if file:
        ext = os.path.splitext(file.name)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png'):
            folder = os.path.join(settings.MEDIA_ROOT, 'ads')
            os.makedirs(folder, exist_ok=True)
            filename = f'ad_{ad.id}{ext}'
            with open(os.path.join(folder, filename), 'wb') as dst:
                for chunk in file.chunks():
                    dst.write(chunk)
            ad.image_path = f'/media/ads/{filename}'
            ad.save(update_fields=['image_path'])
    return JsonResponse({'id': ad.id}, status=201)


@login_required
def my_ads(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    qs = Ad.objects.filter(user=request.current_user).select_related('user', 'category').order_by('-created_at', '-id')
    return JsonResponse([_ad_dict(a) for a in qs], safe=False)


@login_required
def ad_close(request, ad_id):
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    ad = Ad.objects.filter(id=ad_id, user=request.current_user).first()
    if not ad:
        return JsonResponse({'error': 'Объявление не найдено'}, status=404)
    ad.status = 'sold'
    ad.save(update_fields=['status'])
    return JsonResponse({'id': ad.id, 'status': ad.status})


@login_required
def ad_delete(request, ad_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    ad = Ad.objects.filter(id=ad_id, user=request.current_user).first()
    if not ad:
        return JsonResponse({'error': 'Объявление не найдено'}, status=404)
    ad.delete()
    return JsonResponse({'ok': True})


# ---------- Избранное ----------

@login_required
def favorites(request):
    if request.method == 'POST':
        data = _body(request)
        ad = Ad.objects.filter(id=data.get('ad_id')).first()
        if not ad:
            return JsonResponse({'error': 'Объявление не найдено'}, status=404)
        Favorite.objects.get_or_create(user=request.current_user, ad=ad)
        return JsonResponse({'ok': True}, status=201)
    if request.method == 'GET':
        favs = Favorite.objects.filter(user=request.current_user).select_related('ad', 'ad__user', 'ad__category')
        return JsonResponse([_ad_dict(f.ad) for f in favs], safe=False)
    return JsonResponse({'error': 'Метод не разрешён'}, status=405)


@login_required
def favorite_delete(request, ad_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    Favorite.objects.filter(user=request.current_user, ad_id=ad_id).delete()
    return JsonResponse({'ok': True})


# ---------- Профиль ----------

@login_required
def profile(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    user = request.current_user
    return JsonResponse({'user': {
        'id': user.id, 'username': user.username, 'full_name': user.full_name,
        'phone': user.phone, 'avatar_path': user.avatar_path,
    }})


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
    return serve(request, 'ads.html', document_root=settings.FRONTEND_DIR)
