from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="albums",
    )
    release_year = models.IntegerField(
        validators=[
            MinValueValidator(1860),
            MaxValueValidator(datetime.now().year),
        ]
    )
    songs = models.ManyToManyField(
        "Song",
        through="AlbumSong",
        related_name="albums",
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class Song(models.Model):
    title = models.CharField(max_length=200)

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
    track_number = models.PositiveIntegerField()

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
        ]
        ordering = ["album", "track_number"]

    def __str__(self):
        return f"{self.album} - track {self.track_number}: {self.song}"
