import cloudinary.uploader
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView, FormView,
)

from .forms import AlbumForm, PhotoForm, RegisterForm
from .mixins import AlbumOwnerOrAdminMixin, PhotoOwnerOrAdminMixin
from .models import Album, Photo


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('album_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome, {user.username}! Your account is ready.")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('album_list')
        return super().dispatch(request, *args, **kwargs)


# ─── Albums ──────────────────────────────────────────────────────────────────

class AlbumListView(LoginRequiredMixin, ListView):
    """
    Staff see all albums; regular users see only their own.
    """
    model = Album
    template_name = 'albums/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        qs = Album.objects.select_related('owner')
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'
    success_url = reverse_lazy('album_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Album '{form.instance.name}' created!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Create'
        return ctx


class AlbumDetailView(LoginRequiredMixin, DetailView):
    model = Album
    template_name = 'albums/album_detail.html'
    context_object_name = 'album'

    def get_queryset(self):
        qs = Album.objects.prefetch_related('photos')
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['photo_form'] = PhotoForm()
        ctx['is_owner'] = (
            self.request.user.is_staff or self.object.owner == self.request.user
        )
        return ctx


class AlbumUpdateView(AlbumOwnerOrAdminMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Album '{form.instance.name}' updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Update'
        return ctx


class AlbumDeleteView(AlbumOwnerOrAdminMixin, DeleteView):
    model = Album
    template_name = 'albums/album_confirm_delete.html'
    success_url = reverse_lazy('album_list')
    context_object_name = 'album'

    def form_valid(self, form):
        # Delete all Cloudinary images in this album
        for photo in self.object.photos.all():
            if photo.image and photo.image.public_id:
                try:
                    cloudinary.uploader.destroy(photo.image.public_id)
                except Exception:
                    pass
        messages.success(self.request, f"Album '{self.object.name}' deleted.")
        return super().form_valid(form)


# ─── Photos ──────────────────────────────────────────────────────────────────

class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'albums/photo_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.album = get_object_or_404(
            Album, pk=self.kwargs['album_pk'],
            **({} if request.user.is_staff else {'owner': request.user})
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.album = self.album
        form.instance.uploader = self.request.user
        messages.success(self.request, f"Photo '{form.instance.title}' uploaded!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.album.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['album'] = self.album
        ctx['action'] = 'Upload'
        return ctx


class PhotoUpdateView(PhotoOwnerOrAdminMixin, UpdateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'albums/photo_form.html'

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.object.album.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Photo '{form.instance.title}' updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['album'] = self.object.album
        ctx['action'] = 'Edit'
        return ctx


class PhotoDeleteView(PhotoOwnerOrAdminMixin, DeleteView):
    model = Photo
    template_name = 'albums/photo_confirm_delete.html'
    context_object_name = 'photo'

    def get_success_url(self):
        return reverse('album_detail', kwargs={'pk': self.object.album.pk})

    def form_valid(self, form):
        if self.object.image and self.object.image.public_id:
            try:
                cloudinary.uploader.destroy(self.object.image.public_id)
            except Exception:
                pass
        messages.success(self.request, f"Photo '{self.object.title}' deleted.")
        return super().form_valid(form)
