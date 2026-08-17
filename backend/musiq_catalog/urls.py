from django.urls import path

from . import views

urlpatterns = [
    # Artists
    path("artists/", views.ArtistListCreate.as_view(), name="artist-list"),
    path("artists/<int:pk>/", views.ArtistDetail.as_view(), name="artist-detail"),
    path(
        "artists/<int:pk>/albums/",
        views.ArtistAlbumsList.as_view(),
        name="artist-albums",
    ),
    # Albums
    path("albums/", views.AlbumListCreate.as_view(), name="album-list"),
    path("albums/<int:pk>/", views.AlbumDetail.as_view(), name="album-detail"),
    # Album <-> Song management (through model)
    path(
        "albums/<int:pk>/songs/",
        views.AlbumSongListCreate.as_view(),
        name="album-song-list",
    ),
    path(
        "albums/<int:pk>/songs/<int:song_pk>/",
        views.AlbumSongDetail.as_view(),
        name="album-song-detail",
    ),
    # Songs
    path("songs/", views.SongListCreate.as_view(), name="song-list"),
    path("songs/<int:pk>/", views.SongDetail.as_view(), name="song-detail"),
]
