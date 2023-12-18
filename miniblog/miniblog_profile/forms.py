from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import UserProfile, Poll


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

class PollForm(forms.ModelForm):
    question = forms.CharField(max_length=255, label='Вопрос')
    choices = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'placeholder': 'Введите варианты ответов, разделенные запятой'}),
        required=True,
        label='Варианты ответов',
    )
    poll_avatar = forms.ImageField(required=False, label='Изображение опроса')
    full_description = forms.CharField(widget=forms.Textarea, required=True, label='Полное описание')
    short_description = forms.CharField(max_length=30, required=True, label='Краткое описание')
    voting_duration = forms.DurationField(label='Время жизни голосования (в днях)', initial=timedelta(days=7))

    class Meta:
        model = Poll
        fields = ['question', 'choices', 'poll_avatar', 'full_description', 'short_description', 'voting_duration']
