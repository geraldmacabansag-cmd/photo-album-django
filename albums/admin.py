from django.contrib import admin
from .models import Album, Photo


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'photo_count', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'uploader', 'uploaded_at')
    list_filter = ('album', 'uploader')
    search_fields = ('title', 'description', 'album__name')
    readonly_fields = ('uploaded_at',)
