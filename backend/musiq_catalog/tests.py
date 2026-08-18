from django.conf import settings
from django.test import TestCase, override_settings
from musiq_catalog.models import Album, AlbumSong, Artist, Song
from rest_framework.test import APIClient

_NO_THROTTLE = {
    **settings.REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
}


def _setup_catalog():
    artist = Artist.objects.create(name="Test Artist")
    album = Album.objects.create(title="Test Album", artist=artist, release_year=2020)
    song1 = Song.objects.create(title="Test Song A")
    song2 = Song.objects.create(title="Test Song B")
    AlbumSong.objects.create(album=album, song=song1, track_number=1)
    AlbumSong.objects.create(album=album, song=song2, track_number=2)
    return artist, album, song1, song2


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class ArtistAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artist, self.album, self.song1, self.song2 = _setup_catalog()

    def test_list_artists(self):
        response = self.client.get("/api/v1/artists/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Artist")
        self.assertEqual(response.data["results"][0]["albums_count"], 1)

    def test_create_artist(self):
        response = self.client.post("/api/v1/artists/", {"name": "New Artist"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Artist.objects.filter(name="New Artist").exists())

    def test_create_artist_blank_name(self):
        response = self.client.post("/api/v1/artists/", {"name": "   "}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_create_artist_duplicate_name(self):
        response = self.client.post("/api/v1/artists/", {"name": "Test Artist"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)
        self.assertIn("already exists", str(response.data["name"]))

    def test_create_artist_missing_name(self):
        response = self.client.post("/api/v1/artists/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.data)

    def test_artist_detail(self):
        response = self.client.get(f"/api/v1/artists/{self.artist.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Artist")

    def test_artist_detail_not_found(self):
        response = self.client.get("/api/v1/artists/9999/")
        self.assertEqual(response.status_code, 404)

    def test_update_artist(self):
        response = self.client.put(f"/api/v1/artists/{self.artist.id}/", {"name": "Renamed"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.artist.refresh_from_db()
        self.assertEqual(self.artist.name, "Renamed")

    def test_delete_artist(self):
        response = self.client.delete(f"/api/v1/artists/{self.artist.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Artist.objects.filter(id=self.artist.id).exists())

    def test_artist_albums_bonus(self):
        response = self.client.get(f"/api/v1/artists/{self.artist.id}/albums/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Album")

    def test_artist_search(self):
        Artist.objects.create(name="Another Artist")
        response = self.client.get("/api/v1/artists/?search=Another")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Another Artist")

    def test_artist_ordering_desc(self):
        Artist.objects.create(name="AAA Artist")
        response = self.client.get("/api/v1/artists/?ordering=-name")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["name"], "Test Artist")


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class AlbumAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artist, self.album, self.song1, self.song2 = _setup_catalog()

    def test_list_albums(self):
        response = self.client.get("/api/v1/albums/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_album(self):
        response = self.client.post(
            "/api/v1/albums/",
            {"title": "New Album", "artist": self.artist.id, "release_year": 2024},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Album.objects.filter(title="New Album").exists())

    def test_create_album_future_year(self):
        response = self.client.post(
            "/api/v1/albums/",
            {"title": "Future Album", "artist": self.artist.id, "release_year": 3000},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("release_year", response.data)
        self.assertIn("future", str(response.data["release_year"]))

    def test_create_album_year_too_old(self):
        response = self.client.post(
            "/api/v1/albums/",
            {"title": "Old Album", "artist": self.artist.id, "release_year": 1000},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("release_year", response.data)
        self.assertIn("1860", str(response.data["release_year"]))

    def test_create_album_missing_year(self):
        response = self.client.post(
            "/api/v1/albums/",
            {"title": "No Year", "artist": self.artist.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("release_year", response.data)

    def test_create_album_invalid_artist(self):
        response = self.client.post(
            "/api/v1/albums/",
            {"title": "Bad Album", "artist": 9999, "release_year": 2024},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("artist", response.data)

    def test_album_detail_includes_songs(self):
        response = self.client.get(f"/api/v1/albums/{self.album.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["songs"]), 2)
        self.assertEqual(response.data["songs"][0]["track_number"], 1)
        self.assertEqual(response.data["songs"][0]["title"], "Test Song A")

    def test_album_partial_update(self):
        response = self.client.patch(f"/api/v1/albums/{self.album.id}/", {"title": "Patched Title"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.album.refresh_from_db()
        self.assertEqual(self.album.title, "Patched Title")

    def test_delete_album_cascades_links(self):
        album_id = self.album.id
        self.client.delete(f"/api/v1/albums/{album_id}/")
        self.assertEqual(AlbumSong.objects.filter(album_id=album_id).count(), 0)

    def test_album_search_by_artist(self):
        response = self.client.get("/api/v1/albums/?search=Test%20Artist")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_album_ordering_by_year(self):
        artist2 = Artist.objects.create(name="Other Artist")
        Album.objects.create(title="Zzz Album", artist=artist2, release_year=1990)
        response = self.client.get("/api/v1/albums/?ordering=release_year")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["release_year"], 1990)


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class SongAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artist, self.album, self.song1, self.song2 = _setup_catalog()

    def test_list_songs(self):
        response = self.client.get("/api/v1/songs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_song(self):
        response = self.client.post("/api/v1/songs/", {"title": "New Song"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Song.objects.filter(title="New Song").exists())

    def test_create_song_missing_title(self):
        response = self.client.post("/api/v1/songs/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)

    def test_song_detail_includes_albums(self):
        response = self.client.get(f"/api/v1/songs/{self.song1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["albums"]), 1)
        self.assertEqual(response.data["albums"][0]["track_number"], 1)

    def test_song_detail_not_found(self):
        response = self.client.get("/api/v1/songs/9999/")
        self.assertEqual(response.status_code, 404)

    def test_delete_song(self):
        response = self.client.delete(f"/api/v1/songs/{self.song1.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Song.objects.filter(id=self.song1.id).exists())

    def test_song_search(self):
        response = self.client.get("/api/v1/songs/?search=Song%20A")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Song A")


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class AlbumSongAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artist, self.album, self.song1, self.song2 = _setup_catalog()
        self.song3 = Song.objects.create(title="Test Song C")

    def test_list_album_songs(self):
        response = self.client.get(f"/api/v1/albums/{self.album.id}/songs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["song_title"], "Test Song A")

    def test_add_song_to_album(self):
        response = self.client.post(
            f"/api/v1/albums/{self.album.id}/songs/",
            {"song": self.song3.id, "track_number": 3},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(AlbumSong.objects.filter(album=self.album, song=self.song3, track_number=3).exists())

    def test_duplicate_track_number_rejected(self):
        response = self.client.post(
            f"/api/v1/albums/{self.album.id}/songs/",
            {"song": self.song3.id, "track_number": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("Track number 1", str(response.data["non_field_errors"]))

    def test_duplicate_song_rejected(self):
        response = self.client.post(
            f"/api/v1/albums/{self.album.id}/songs/",
            {"song": self.song1.id, "track_number": 3},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("already on this album", str(response.data["non_field_errors"]))

    def test_add_song_track_zero_rejected(self):
        response = self.client.post(
            f"/api/v1/albums/{self.album.id}/songs/",
            {"song": self.song3.id, "track_number": 0},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("track_number", response.data)

    def test_add_song_missing_fields(self):
        response = self.client.post(
            f"/api/v1/albums/{self.album.id}/songs/",
            {"song": self.song3.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("track_number", response.data)

    def test_remove_song_from_album(self):
        response = self.client.delete(f"/api/v1/albums/{self.album.id}/songs/{self.song1.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(AlbumSong.objects.filter(album=self.album, song=self.song1).exists())

    def test_remove_unlinked_song_404(self):
        response = self.client.delete(f"/api/v1/albums/{self.album.id}/songs/{self.song3.id}/")
        self.assertEqual(response.status_code, 404)

    def test_add_song_to_missing_album_404(self):
        response = self.client.post(
            "/api/v1/albums/9999/songs/",
            {"song": self.song3.id, "track_number": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 404)


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class PaginationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        Artist.objects.create(name="Test Artist")
        for i in range(25):
            Song.objects.create(title=f"Song {i:02d}")

    def test_default_page_size(self):
        response = self.client.get("/api/v1/songs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertEqual(response.data["count"], 25)
        self.assertIsNotNone(response.data["next"])

    def test_custom_page_size(self):
        response = self.client.get("/api/v1/songs/?page_size=5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)

    def test_page_size_capped_at_100(self):
        response = self.client.get("/api/v1/songs/?page_size=1000")
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.data["results"]), 100)

    def test_invalid_page_404(self):
        response = self.client.get("/api/v1/songs/?page=0")
        self.assertEqual(response.status_code, 404)

    def test_page_two(self):
        response = self.client.get("/api/v1/songs/?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["previous"])


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class QueryCountTests(TestCase):
    """Regression tests: list endpoints must not N+1 as data grows."""

    def setUp(self):
        self.client = APIClient()
        artist = Artist.objects.create(name="Test Artist")
        for i in range(5):
            album = Album.objects.create(title=f"Album {i}", artist=artist, release_year=2000 + i)
            for j in range(5):
                song = Song.objects.create(title=f"Song {i}-{j}")
                AlbumSong.objects.create(album=album, song=song, track_number=j + 1)

    def test_artist_list_no_n_plus_1(self):
        with self.assertNumQueries(2):
            self.client.get("/api/v1/artists/")

    def test_album_list_no_n_plus_1(self):
        with self.assertNumQueries(3):
            self.client.get("/api/v1/albums/")

    def test_song_list_no_n_plus_1(self):
        with self.assertNumQueries(3):
            self.client.get("/api/v1/songs/")
