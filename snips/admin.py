from datetime import date
from django.contrib import admin
from django.urls import reverse
from simple_history.admin import SimpleHistoryAdmin

from .models import Snip, SnipLog, Vote, PostMetrics, Referer, Category, Message

admin.site.register(Snip)
admin.site.register(Category)


@admin.register(SnipLog)
class SnipLogAdmin(SimpleHistoryAdmin):
    list_display = [field.name for field in SnipLog._meta.fields if field.name != "id"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.fields if field.name != "id"]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Vote._meta.fields if field.name != "id"]


@admin.register(PostMetrics)
class PostMetricsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostMetrics._meta.fields if field.name != "id"]


@admin.register(Referer)
class RefererAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Referer._meta.fields if field.name != "id"]