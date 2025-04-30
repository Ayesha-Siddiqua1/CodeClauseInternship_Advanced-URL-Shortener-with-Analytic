from django.contrib import admin
from .models import ShortenedURL, ClickAnalytics

# Register your models here.

@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ('short_alias', 'original_url', 'creation_date', 'owner')
    search_fields = ('short_alias', 'original_url')
    list_filter = ('creation_date', 'owner')

@admin.register(ClickAnalytics)
class ClickAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('shortened_url', 'click_timestamp')
    list_filter = ('click_timestamp',)