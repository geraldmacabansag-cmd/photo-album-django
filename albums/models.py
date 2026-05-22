from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Album(models.Model):
    """A collection of photos owned by a user."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (by {self.owner.username})"

    def photo_count(self):
        return self.photos.count()

    def cover_photo(self):
        return self.photos.order_by('-uploaded_at').first()


class Photo(models.Model):
    """An individual photo belonging to an album."""
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_photos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = CloudinaryField('image', folder='photo_album')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} in {self.album.name}"
