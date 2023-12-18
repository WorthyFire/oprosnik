from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import index, register, login_view, profile, edit_profile, confirm_delete_account, poll_detail, vote
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('confirm_delete_account/', confirm_delete_account, name='confirm_delete_account'),
    path('poll_detail/<int:poll_id>/', poll_detail, name='poll_detail'),
    path('vote/<int:poll_id>/', vote, name='vote'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
