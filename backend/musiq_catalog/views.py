from django.db import IntegrityError, transaction
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Album, AlbumSong, Artist, Song
from .serializers import (
    AlbumSerializer,
    AlbumSongCreateSerializer,
    AlbumSongSerializer,
    ArtistSerializer,
    SongSerializer,
)

# --- Shared prefetch constants (avoid duplication across views) ---

_album_songs_prefetch = Prefetch(
    "album_songs",
    queryset=AlbumSong.objects.select_related("song").order_by("track_number"),
)
_song_album_songs_prefetch = Prefetch(
    "album_songs",
    queryset=AlbumSong.objects.select_related("album__artist"),
)


class ArtistListCreate(generics.ListCreateAPIView):
    serializer_class = ArtistSerializer
    search_fields = ["name"]
    ordering_fields = ["id", "name"]

    def get_queryset(self):
        return Artist.objects.annotate(albums_count=Count("albums")).order_by("name")


class ArtistDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArtistSerializer

    def get_queryset(self):
        return Artist.objects.annotate(albums_count=Count("albums"))


class ArtistAlbumsList(generics.ListAPIView):
    """Bonus endpoint: list albums for a given artist."""

    serializer_class = AlbumSerializer
    search_fields = ["title"]
    ordering_fields = ["id", "title", "release_year"]

    def get_queryset(self):
        artist = get_object_or_404(Artist, pk=self.kwargs["pk"])
        return Album.objects.filter(artist=artist).select_related("artist").prefetch_related(_album_songs_prefetch)


class AlbumListCreate(generics.ListCreateAPIView):
    serializer_class = AlbumSerializer
    search_fields = ["title", "artist__name"]
    ordering_fields = ["id", "title", "release_year"]

    def get_queryset(self):
        return Album.objects.select_related("artist").prefetch_related(_album_songs_prefetch)


class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Album.objects.select_related("artist").prefetch_related(_album_songs_prefetch)
    serializer_class = AlbumSerializer


class AlbumSongListCreate(generics.ListCreateAPIView):
    """
    GET  /api/albums/<pk>/songs/   -> list AlbumSong entries for the album.
    POST /api/albums/<pk>/songs/   -> add a song to the album with a track number.
    """

    search_fields = ["song__title"]
    ordering_fields = ["id", "track_number", "song__title"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AlbumSongCreateSerializer
        return AlbumSongSerializer

    def get_queryset(self):
        get_object_or_404(Album, pk=self.kwargs["pk"])
        return AlbumSong.objects.filter(album_id=self.kwargs["pk"]).select_related("song")

    def create(self, request, *args, **kwargs):
        album = get_object_or_404(Album, pk=self.kwargs["pk"])
        serializer = AlbumSongCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        song = serializer.validated_data["song"]
        track_number = serializer.validated_data["track_number"]
        try:
            with transaction.atomic():
                link = AlbumSong.objects.create(
                    album=album,
                    song=song,
                    track_number=track_number,
                )
        except IntegrityError:
            if AlbumSong.objects.filter(album=album, song=song).exists():
                msg = "This song is already on this album."
            else:
                msg = f"Track number {track_number} is already taken on this album."
            return Response(
                {"non_field_errors": [msg]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            AlbumSongSerializer(link).data,
            status=status.HTTP_201_CREATED,
        )


class AlbumSongDetail(generics.DestroyAPIView):
    """
    DELETE /api/albums/<pk>/songs/<song_pk>/
    Removes a song from an album (deletes the AlbumSong link).
    """

    def get_object(self):
        return get_object_or_404(
            AlbumSong,
            album_id=self.kwargs["pk"],
            song_id=self.kwargs["song_pk"],
        )


class SongListCreate(generics.ListCreateAPIView):
    serializer_class = SongSerializer
    search_fields = ["title"]
    ordering_fields = ["id", "title"]

    def get_queryset(self):
        return Song.objects.prefetch_related(_song_album_songs_prefetch)


class SongDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Song.objects.prefetch_related(_song_album_songs_prefetch)
    serializer_class = SongSerializer
