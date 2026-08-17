from django.db import IntegrityError
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


class ArtistListCreate(generics.ListCreateAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    search_fields = ["name"]
    ordering_fields = ["id", "name"]


class ArtistDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


class ArtistAlbumsList(generics.ListAPIView):
    """Bonus endpoint: list albums for a given artist."""

    serializer_class = AlbumSerializer

    def get_queryset(self):
        return Album.objects.filter(artist_id=self.kwargs["pk"])


class AlbumListCreate(generics.ListCreateAPIView):
    queryset = Album.objects.select_related("artist").all()
    serializer_class = AlbumSerializer
    search_fields = ["title", "artist__name"]
    ordering_fields = ["id", "title", "release_year"]


class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Album.objects.select_related("artist").all()
    serializer_class = AlbumSerializer


class AlbumSongListCreate(generics.ListCreateAPIView):
    """
    GET  /api/albums/<pk>/songs/   -> list AlbumSong entries for the album.
    POST /api/albums/<pk>/songs/   -> add a song to the album with a track number.
    """

    serializer_class = AlbumSongSerializer

    def get_queryset(self):
        return AlbumSong.objects.filter(album_id=self.kwargs["pk"])

    def create(self, request, *args, **kwargs):
        album = get_object_or_404(Album, pk=self.kwargs["pk"])
        serializer = AlbumSongCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            link = AlbumSong.objects.create(
                album=album,
                song=serializer.validated_data["song"],
                track_number=serializer.validated_data["track_number"],
            )
        except IntegrityError:
            return Response(
                {
                    "track_number": [
                        "A song with this track number already exists for this album."
                    ]
                },
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

    serializer_class = AlbumSongSerializer

    def get_queryset(self):
        return AlbumSong.objects.filter(
            album_id=self.kwargs["pk"],
            song_id=self.kwargs["song_pk"],
        )

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset)


class SongListCreate(generics.ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    search_fields = ["title"]
    ordering_fields = ["id", "title"]


class SongDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
