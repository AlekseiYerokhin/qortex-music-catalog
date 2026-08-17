from django.contrib import admin

from .models import Album, AlbumSong, Artist, Song


class AlbumSongInline(admin.TabularInline):
    model = AlbumSong
    extra = 1
    autocomplete_fields = ["song"]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "artist", "release_year"]
    list_filter = ["artist"]
    search_fields = ["title", "artist__name"]
    autocomplete_fields = ["artist"]
    inlines = [AlbumSongInline]


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
    search_fields = ["title"]


@admin.register(AlbumSong)
class AlbumSongAdmin(admin.ModelAdmin):
    list_display = ["id", "album", "song", "track_number"]
    list_filter = ["album"]
    search_fields = ["album__title", "song__title"]
    autocomplete_fields = ["album", "song"]
