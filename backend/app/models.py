from django.db import models
from rest_framework.authtoken.models import Token as DefaultTokenModel
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets



class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='songs')
    audio_file = models.FileField(upload_to='songs/')

    def __str__(self):
        return self.title


class Like(models.Model):
    song = models.OneToOneField(Song, on_delete=models.CASCADE, related_name='like')
    count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.count} likes for {self.song.title}"

    @classmethod
    def increment_like(cls, song):
        like, created = cls.objects.get_or_create(song=song)
        like.count += 1
        like.save()
        return like
    
class CustomToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    key = models.CharField(max_length=300, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return self.expiry_date is not None and self.expiry_date <= timezone.now()

    def refresh(self):
        self.expiry_date = timezone.now() + timedelta(days=300)
        self.save()

    @classmethod
    def get_or_create_token(cls, user):
        try:
            token = cls.objects.get(user=user)
            if token.is_expired() or (timezone.now() - token.created).days >= 1:
                token.refresh()
        except cls.DoesNotExist:
            token = cls.objects.create(
                user=user,
                key=secrets.token_hex(60),
                expiry_date=timezone.now() + timedelta(days=300)
            )
        return token
