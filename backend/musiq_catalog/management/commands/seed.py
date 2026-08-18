from django.core.management.base import BaseCommand
from django.db import transaction

from musiq_catalog.models import Album, AlbumSong, Artist, Song

SEED_DATA = [
    {
        "name": "Pink Floyd",
        "albums": [
            {
                "title": "The Dark Side of the Moon",
                "release_year": 1973,
                "tracks": [
                    (1, "Speak to Me"),
                    (2, "Breathe"),
                    (3, "On the Run"),
                    (4, "Time"),
                    (5, "The Great Gig in the Sky"),
                    (6, "Money"),
                    (7, "Us and Them"),
                    (8, "Any Colour You Like"),
                    (9, "Brain Damage"),
                    (10, "Eclipse"),
                ],
            },
            {
                "title": "The Wall",
                "release_year": 1979,
                "tracks": [
                    (1, "In the Flesh?"),
                    (2, "The Thin Ice"),
                    (3, "Another Brick in the Wall, Part 2"),
                    (4, "Mother"),
                    (5, "Comfortably Numb"),
                    (6, "Hey You"),
                    (7, "Run Like Hell"),
                    (8, "The Trial"),
                ],
            },
        ],
    },
    {
        "name": "Daft Punk",
        "albums": [
            {
                "title": "Discovery",
                "release_year": 2001,
                "tracks": [
                    (1, "One More Time"),
                    (2, "Aerodynamic"),
                    (3, "Digital Love"),
                    (4, "Harder, Better, Faster, Stronger"),
                    (5, "Something About Us"),
                    (6, "Face to Face"),
                ],
            },
            {
                "title": "Random Access Memories",
                "release_year": 2013,
                "tracks": [
                    (1, "Give Life Back to Music"),
                    (2, "The Game of Love"),
                    (3, "Giorgio by Moroder"),
                    (4, "Instant Crush"),
                    (5, "Get Lucky"),
                    (6, "Contact"),
                ],
            },
        ],
    },
    {
        "name": "Radiohead",
        "albums": [
            {
                "title": "OK Computer",
                "release_year": 1997,
                "tracks": [
                    (1, "Airbag"),
                    (2, "Paranoid Android"),
                    (3, "Subterranean Homesick Alien"),
                    (4, "Exit Music (For a Film)"),
                    (5, "Let Down"),
                    (6, "Karma Police"),
                    (7, "No Surprises"),
                    (8, "Lucky"),
                ],
            },
            {
                "title": "Kid A",
                "release_year": 2000,
                "tracks": [
                    (1, "Everything in Its Right Place"),
                    (2, "Kid A"),
                    (3, "The National Anthem"),
                    (4, "How to Disappear Completely"),
                    (5, "Optimistic"),
                    (6, "Idioteque"),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the music catalog with sample artists, albums, and songs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Wipe existing catalog data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options.get("force", False)

        if Artist.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    "Catalog already has data. Use --force to wipe and re-seed."
                )
            )
            return

        if force:
            self.stdout.write("Wiping existing catalog data...")
            AlbumSong.objects.all().delete()
            Album.objects.all().delete()
            Song.objects.all().delete()
            Artist.objects.all().delete()

        artist_count = album_count = song_count = link_count = 0
        song_cache = {}

        for artist_data in SEED_DATA:
            artist = Artist.objects.create(name=artist_data["name"])
            artist_count += 1
            for album_data in artist_data["albums"]:
                album = Album.objects.create(
                    title=album_data["title"],
                    artist=artist,
                    release_year=album_data["release_year"],
                )
                album_count += 1
                for track_number, song_title in album_data["tracks"]:
                    # Reuse a Song with the same title if it already exists
                    # (the same song can appear in different albums).
                    song = song_cache.get(song_title)
                    if song is None:
                        song = Song.objects.create(title=song_title)
                        song_cache[song_title] = song
                        song_count += 1
                    AlbumSong.objects.create(
                        album=album,
                        song=song,
                        track_number=track_number,
                    )
                    link_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded catalog: {artist_count} artists, {album_count} albums, "
                f"{song_count} songs, {link_count} album-song links."
            )
        )
