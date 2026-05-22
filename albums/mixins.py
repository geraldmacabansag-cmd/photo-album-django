"""
Custom RBAC mixins.

Roles:
  - Anonymous  : can only view the login / register pages.
  - Authenticated user : can create albums & upload photos to their own albums.
  - Album owner : full CRUD on their own albums and photos inside them.
  - Staff / Superuser (Album Admin) : full CRUD on every album and photo.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Album, Photo


class AlbumOwnerOrAdminMixin(LoginRequiredMixin):
    """
    Allow access only if the logged-in user owns the album (or is staff).
    Attach the album to self.album for convenience.
    """
    def dispatch(self, request, *args, **kwargs):
        album = get_object_or_404(Album, pk=self.kwargs.get('pk') or self.kwargs.get('album_pk'))
        if not (request.user.is_staff or album.owner == request.user):
            raise PermissionDenied
        self.album = album
        return super().dispatch(request, *args, **kwargs)


class PhotoOwnerOrAdminMixin(LoginRequiredMixin):
    """
    Allow access only if the logged-in user uploaded the photo (or is staff).
    Attach the photo to self.photo for convenience.
    """
    def dispatch(self, request, *args, **kwargs):
        photo = get_object_or_404(Photo, pk=self.kwargs['pk'])
        if not (request.user.is_staff or photo.uploader == request.user):
            raise PermissionDenied
        self.photo = photo
        return super().dispatch(request, *args, **kwargs)
