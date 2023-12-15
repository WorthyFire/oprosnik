from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, Comment, Post

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    class Meta:
        fields = ['username', 'password']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'avatar', 'bio']
        labels = {
            'name': 'Имя',
            'avatar': 'Аватар',
            'bio': 'Информация о себе',
        }

        def clean_avatar(self):
            avatar = self.cleaned_data.get('avatar', False)
            if avatar:

                if avatar.size > 2 * 1024 * 1024:
                    raise ValidationError(('Размер файла должен быть не более 2 МБ.'))
            return avatar

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        labels = {
        'content': 'Что у вас нового?:'
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'photo']
        labels = {
            'content': 'Комментарий:'
        }

class UserSearchForm(forms.Form):
    username = forms.CharField(label='Никнейм пользователя:', max_length=150, required=False)

