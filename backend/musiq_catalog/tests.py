from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from musiq_catalog.models import Album, AlbumSong, Artist, Song

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
        response = self.client.get("/api/artists/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Artist")
        self.assertEqual(response.data["results"][0]["albums_count"], 1)

    def test_create_artist(self):
        response = self.client.post("/api/artists/", {"name": "New Artist"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Artist.objects.filter(name="New Artist").exists())

    def test_artist_detail(self):
        response = self.client.get(f"/api/artists/{self.artist.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Artist")

    def test_update_artist(self):
        response = self.client.put(f"/api/artists/{self.artist.id}/", {"name": "Renamed"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.artist.refresh_from_db()
        self.assertEqual(self.artist.name, "Renamed")

    def test_delete_artist(self):
        response = self.client.delete(f"/api/artists/{self.artist.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Artist.objects.filter(id=self.artist.id).exists())

    def test_artist_albums_bonus(self):
        response = self.client.get(f"/api/artists/{self.artist.id}/albums/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Album")


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class AlbumAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artist, self.album, self.song1, self.song2 = _setup_catalog()

    def test_list_albums(self):
        response = self.client.get("/api/albums/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_album(self):
        response = self.client.post(
            "/api/albums/",
            {"title": "New Album", "artist": self.artist.id, "release_year": 2024},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Album.objects.filter(title="New Album").exists())

    def test_album_detail_includes_songs(self):
        response = self.client.get(f"/api/albums/{self.album.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["songs"]), 2)
        self.assertEqual(response.data["songs"][0]["track_number"], 1)
        self.assertEqual(response.data["songs"][0]["title"], "Test Song A")

    def test_delete_album_cascades_links(self):
        album_id = self.album.id
        self.client.delete(f"/api/albums/{album_id}/")
        self.assertEqual(AlbumSong.objects.filter(album_id=album_id).count(), 0)


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class SongAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artist, self.album, self.song1, self.song2 = _setup_catalog()

    def test_list_songs(self):
        response = self.client.get("/api/songs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_create_song(self):
        response = self.client.post("/api/songs/", {"title": "New Song"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Song.objects.filter(title="New Song").exists())

    def test_song_detail_includes_albums(self):
        response = self.client.get(f"/api/songs/{self.song1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["albums"]), 1)
        self.assertEqual(response.data["albums"][0]["track_number"], 1)

    def test_delete_song(self):
        response = self.client.delete(f"/api/songs/{self.song1.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Song.objects.filter(id=self.song1.id).exists())


@override_settings(REST_FRAMEWORK=_NO_THROTTLE)
class AlbumSongAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.artist, self.album, self.song1, self.song2 = _setup_catalog()
        self.song3 = Song.objects.create(title="Test Song C")

    def test_add_song_to_album(self):
        response = self.client.post(
            f"/api/albums/{self.album.id}/songs/",
            {"song": self.song3.id, "track_number": 3},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(AlbumSong.objects.filter(album=self.album, song=self.song3, track_number=3).exists())

    def test_duplicate_track_number_rejected(self):
        response = self.client.post(
            f"/api/albums/{self.album.id}/songs/",
            {"song": self.song3.id, "track_number": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_remove_song_from_album(self):
        response = self.client.delete(f"/api/albums/{self.album.id}/songs/{self.song1.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(AlbumSong.objects.filter(album=self.album, song=self.song1).exists())
