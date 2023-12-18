from datetime import timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Поле для связи с пользователем
    question = models.TextField()
    poll_avatar = models.ImageField(upload_to='media/')
    full_description = models.TextField(max_length=254)
    short_description = models.CharField(max_length=30)

    begin_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)
    voting_duration = models.DurationField(default=timedelta(hours=2))

    def is_expired(self):
        return timezone.now() > self.end_date

    def __str__(self):
        return self.question

    def total_votes(self):
        return sum(choice.votes for choice in self.choice_set.all())

class Choice(models.Model):
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    admin_voted = models.BooleanField(default=False)

    def get_percentage(self):
        total_votes = self.poll.total_votes()
        return (self.votes / total_votes)* 100 if total_votes > 0 else 0
class Voter(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)