from rest_framework import serializers

from .models import Album, AlbumSong, Artist, Song


class AlbumSongSerializer(serializers.ModelSerializer):
    """
    Serializer for the through model. Used for write operations that need
    to set the track number of a song within an album.
    """

    class Meta:
        model = AlbumSong
        fields = ["id", "album", "song", "track_number"]


class ArtistSerializer(serializers.ModelSerializer):
    albums_count = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ["id", "name", "albums_count"]

    def get_albums_count(self, obj):
        return obj.albums.count()


class SongSerializer(serializers.ModelSerializer):
    """
    Read: nests the albums the song appears in (with track numbers).
    Write: only needs `title`.
    """

    albums = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ["id", "title", "albums"]

    def get_albums(self, obj):
        return [
            {
                "id": link.album_id,
                "title": link.album.title,
                "release_year": link.album.release_year,
                "artist": link.album.artist.name,
                "track_number": link.track_number,
            }
            for link in obj.album_songs.select_related("album__artist")
        ]


class AlbumSerializer(serializers.ModelSerializer):
    """
    Read: nests the artist name and the list of songs with track numbers.
    Write: accepts `artist` (artist id) and the basic album fields.
    """

    artist = serializers.PrimaryKeyRelatedField(queryset=Artist.objects.all())
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    songs = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ["id", "title", "artist", "artist_name", "release_year", "songs"]

    def get_songs(self, obj):
        return [
            {
                "id": link.song_id,
                "title": link.song.title,
                "track_number": link.track_number,
            }
            for link in obj.album_songs.select_related("song").order_by("track_number")
        ]


class AlbumSongCreateSerializer(serializers.Serializer):
    """
    Helper serializer for adding a song to an album with a track number.
    Accepts a song id and a track number; the album is inferred from the URL.
    """

    song = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all())
    track_number = serializers.IntegerField(min_value=1)
