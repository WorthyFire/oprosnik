from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Post, Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm, UserProfileForm, PostForm, CommentForm, UserSearchForm


def index(request):
    return render(request, 'index.html')

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

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    posts = Post.objects.filter(user_profile=user_profile)
    post_form = PostForm()
    user_search_form = UserSearchForm()

    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            new_post = post_form.save(commit=False)
            new_post.user_profile = user_profile
            new_post.save()
            return redirect('profile')

    user_to_view = None
    error_message = None
    is_self_profile = False  # Флаг для проверки, является ли это профилем текущего пользователя

    if request.method == 'GET':
        user_search_form = UserSearchForm(request.GET)
        if user_search_form.is_valid():
            username = user_search_form.cleaned_data['username']
            try:
                user_to_view = User.objects.get(username=username)

                # Проверяем, является ли найденный пользователь текущим пользователем
                is_self_profile = user_to_view == request.user

                if is_self_profile:
                    return render(request, 'logined/profile.html',
                                  {'user_profile': user_profile, 'posts': posts, 'post_form': post_form,
                                   'user_search_form': user_search_form, 'is_self_profile': is_self_profile})
                else:
                    return redirect('view_profile', username=username)
            except User.DoesNotExist:
                error_message = 'Пользователь не найден.'

    return render(request, 'logined/profile.html',
                  {'user_profile': user_profile, 'posts': posts, 'post_form': post_form,
                   'user_search_form': user_search_form, 'user_to_view': user_to_view, 'error_message': error_message,
                   'is_self_profile': is_self_profile})
@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
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
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user_profile = user_profile
            new_comment.post = post
            new_comment.save()
            return redirect('profile')

    return redirect('profile')

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user_profile__user=request.user)
    post.delete()
    return redirect('profile')

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user_profile__user=request.user)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES, instance=comment)
        if comment_form.is_valid():
            comment_form.save()
            return redirect('profile')

    return redirect('profile')  # В случае ошибки
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user_profile__user=request.user)
    comment.delete()
    return redirect('profile')


def view_profile(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)
    posts = Post.objects.filter(user_profile=user_profile)
    current_user = request.user if request.user.is_authenticated else None

    return render(request, 'logined/view_profile.html',
                  {'user_profile': user_profile, 'posts': posts, 'current_user': current_user})