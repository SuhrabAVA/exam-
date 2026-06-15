"""REST API эндпоинты HeadHunter mini. Сервер отдаёт только JSON."""
import json

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.static import serve

from .models import User, Vacancy, Application
from .auth import issue_token, login_required

CATEGORIES = {1: 'IT', 2: 'Продажи', 3: 'Маркетинг'}


def _body(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


def _exp_label(years):
    if years == 0:
        return 'Без опыта'
    return f'От {years} ' + ('года' if years < 5 else 'лет')


def _vacancy_dict(v):
    return {
        'id': v.id,
        'title': v.title,
        'category': v.category,
        'category_name': CATEGORIES.get(v.category, 'Другое'),
        'salary': v.salary,
        'experience_required': v.experience_required,
        'experience_label': _exp_label(v.experience_required),
        'description': v.description,
        'company_logo_path': v.company_logo_path,
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


# ---------- Вакансии ----------

def vacancies(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    qs = Vacancy.objects.all()
    category = request.GET.get('category')
    experience = request.GET.get('experience')
    search = request.GET.get('q')
    sort = request.GET.get('sort')
    if category:
        qs = qs.filter(category=category)
    if experience is not None and experience != '':
        if experience == '0':
            qs = qs.filter(experience_required=0)
        else:
            qs = qs.filter(experience_required__gte=experience)
    if search:
        qs = qs.filter(title__icontains=search)
    if sort == 'salary_asc':
        qs = qs.order_by('salary')
    elif sort == 'salary_desc':
        qs = qs.order_by('-salary')
    else:
        qs = qs.order_by('id')
    return JsonResponse([_vacancy_dict(v) for v in qs], safe=False)


# ---------- Отклики ----------

@login_required
def applications(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    data = _body(request)
    vacancy = Vacancy.objects.filter(id=data.get('vacancy_id')).first()
    if not vacancy:
        return JsonResponse({'error': 'Вакансия не найдена'}, status=404)
    cover_letter = (data.get('cover_letter') or '').strip()
    if not cover_letter:
        return JsonResponse({'error': 'Введите сопроводительное письмо'}, status=400)
    app = Application.objects.create(
        user=request.current_user, vacancy=vacancy,
        cover_letter=cover_letter, status='active',
    )
    return JsonResponse({'id': app.id}, status=201)


@login_required
def withdraw(request, application_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    app = Application.objects.filter(id=application_id, user=request.current_user).first()
    if not app:
        return JsonResponse({'error': 'Отклик не найден'}, status=404)
    app.status = 'withdrawn'
    app.save(update_fields=['status'])
    return JsonResponse({'id': app.id, 'status': app.status})


# ---------- Профиль ----------

@login_required
def profile(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)
    user = request.current_user
    items = Application.objects.filter(user=user).select_related('vacancy').order_by('-id')
    return JsonResponse({
        'user': {'id': user.id, 'username': user.username, 'full_name': user.full_name},
        'applications': [{
            'id': a.id,
            'vacancy_title': a.vacancy.title,
            'company_logo_path': a.vacancy.company_logo_path,
            'category_name': CATEGORIES.get(a.vacancy.category, 'Другое'),
            'salary': a.vacancy.salary,
            'cover_letter': a.cover_letter,
            'apply_date': a.apply_date.strftime('%Y-%m-%d') if a.apply_date else '',
            'status': a.status,
        } for a in items],
    })


def frontend_index(request):
    return serve(request, 'vacancies.html', document_root=settings.FRONTEND_DIR)
