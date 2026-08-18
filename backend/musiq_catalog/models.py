from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


def validate_release_year(value):
    if value < 1860:
        raise ValidationError("Year must be 1860 or later.")
    if value > timezone.now().year:
        raise ValidationError("Year cannot be in the future.")


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="albums",
    )
    release_year = models.IntegerField(validators=[validate_release_year])
    songs = models.ManyToManyField(
        "Song",
        through="AlbumSong",
        related_name="albums",
    )

    class Meta:
        ordering = ["title"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(release_year__gte=1860),
                name="ck_album_release_year_gte_1860",
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class Song(models.Model):
    title = models.CharField(max_length=200, db_index=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class AlbumSong(models.Model):
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="album_songs",
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="album_songs",
    )
    track_number = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["album", "track_number"],
                name="uq_album_track_number",
            ),
            models.UniqueConstraint(
                fields=["album", "song"],
                name="uq_album_song",
            ),
            models.CheckConstraint(
                check=models.Q(track_number__gte=1),
                name="ck_albumsong_track_number_gte_1",
            ),
        ]
        ordering = ["album", "track_number"]

    def __str__(self):
        return f"{self.album} - track {self.track_number}: {self.song}"
