import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, AnonymousUser
from django.core.files import File
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse

from .models import UserProfile, Poll, Choice, Voter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, UserProfileForm, PollForm


def index(request):
    all_polls = Poll.objects.all()

    # Проверяем, аутентифицирован ли пользователь перед фильтрацией
    if isinstance(request.user, AnonymousUser):
        user_polls = None
    else:
        user_polls = Poll.objects.filter(~Q(user=request.user) & Q(user__isnull=False))

    return render(request, 'index.html', {'all_polls': all_polls, 'user_polls': user_polls})
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})\


from django.shortcuts import get_object_or_404

@login_required
def profile(request):
    # Попробуем получить профиль пользователя
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Если профиль не существует, создадим его
        user_profile = UserProfile.objects.create(user=request.user)

    # Получаем все опросы, созданные текущим пользователем
    user_polls = Poll.objects.filter(user=request.user)

    if request.method == 'POST':
        poll_form = PollForm(request.POST, request.FILES)
        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.user = request.user
            poll.save()

            # Обработка вариантов ответа
            choices_text = request.POST.get('choices', '')
            choices_list = [choice.strip() for choice in choices_text.split(',') if choice.strip()]
            for choice_text in choices_list:
                Choice.objects.create(poll=poll, choice_text=choice_text, votes=0)

            return redirect('profile')
    else:
        poll_form = PollForm()

    return render(request, 'logined/profile.html', {'user_profile': user_profile, 'poll_form': poll_form, 'user_polls': user_polls})




@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()


            if not user_profile.avatar:
                default_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars', 'default_avatar.jpg')
                with open(default_avatar_path, 'rb') as f:
                    user_profile.avatar.save('default_avatar.jpg', File(f))

            return redirect('profile')

    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'logined/edit_profile.html', {'form': form})

@login_required
def confirm_delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(request, username=request.user.username, password=password)

        if user is not None:
            request.user.userprofile.delete()
            user.delete()
            logout(request)
            return redirect('index')
        else:
            return render(request, 'logined/confirm_delete_account.html', {'error': 'Неправильный пароль'})

    return render(request, 'logined/confirm_delete_account.html')

@login_required
def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    user_can_delete = request.user == poll.user
    total_votes = sum(choice.votes for choice in poll.choice_set.all())

    # Проверяем, проголосовал ли администратор
    admin_choice = poll.choice_set.filter(admin_voted=True).first()

    if request.method == 'POST':
        # Проверяем, является ли пользователь владельцем опроса
        if user_can_delete:
            poll.delete()
            return redirect('profile')
        else:
            # Если не владелец, возвращаем ошибку доступа
            return HttpResponseForbidden("You don't have permission to delete this poll.")

    return render(request, 'logined/poll_detail.html', {'poll': poll, 'user_can_delete': user_can_delete, 'total_votes': total_votes})

def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    selected_choice_id = request.POST.get('choice')

    if selected_choice_id:
        selected_choice = get_object_or_404(Choice, id=selected_choice_id)

        # Проверяем, проголосовал ли пользователь ранее
        if not Voter.objects.filter(user=request.user, poll=poll).exists():
            selected_choice.votes += 1
            selected_choice.save()

            # Записываем, что пользователь проголосовал за этот опрос
            Voter.objects.create(user=request.user, poll=poll)

    return redirect('poll_detail', poll_id=poll_id)