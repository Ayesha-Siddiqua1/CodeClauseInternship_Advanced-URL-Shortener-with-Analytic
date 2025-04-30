from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string
import random

class ShortenedURL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_alias = models.CharField(max_length=10, unique=True, db_index=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.short_alias} -> {self.original_url[:50]}"

    @classmethod
    def create_short_url(cls, original_url, owner=None):
        """Create a new shortened URL with a random unique alias"""
        chars = string.ascii_letters + string.digits
        short_alias = ''.join(random.choice(chars) for _ in range(6))
        
        # Ensure the alias is unique
        while cls.objects.filter(short_alias=short_alias).exists():
            short_alias = ''.join(random.choice(chars) for _ in range(6))
        
        return cls.objects.create(
            original_url=original_url,
            short_alias=short_alias,
            owner=owner
        )

class ClickAnalytics(models.Model):
    shortened_url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE, related_name='clicks')
    click_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Click on {self.shortened_url.short_alias} at {self.click_timestamp}"


