# API Contract — Qortex Music Catalog

Base URL: `http://localhost:8000/api`
No authentication required. All endpoints accept/return JSON.

## Conventions

- All list endpoints support **pagination** (DRF PageNumberPagination):
  - `?page=2` — page number
  - `?page_size=10` — items per page (default 20, max 100)
- All list endpoints support **search** and **ordering**:
  - `?search=foo` — full-text search on configured fields
  - `?ordering=title` — sort ascending; `-title` for descending
- Error responses use DRF's default format:
  ```json
  {"detail": "Not found."}
  ```
  or for validation:
  ```json
  {"field_name": ["This field is required."]}
  ```
- All IDs are integers.

---

## Artists

### `GET /api/artists/`
List artists.

**Query params:** `search` (searches `name`), `ordering` (`id`, `name`)

**200 Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Pink Floyd",
      "albums_count": 2
    }
  ]
}
```

### `POST /api/artists/`
Create an artist.

**Request:**
```json
{"name": "New Artist"}
```

**201 Response:**
```json
{"id": 4, "name": "New Artist", "albums_count": 0}
```

**400** if `name` missing or not unique.

### `GET /api/artists/<id>/`
Retrieve a single artist.

**200 Response:**
```json
{"id": 1, "name": "Pink Floyd", "albums_count": 2}
```

### `PUT /api/artists/<id>/`
Update an artist (full update).

**Request:**
```json
{"name": "Renamed Artist"}
```

**200 Response:**
```json
{"id": 1, "name": "Renamed Artist", "albums_count": 2}
```

### `DELETE /api/artists/<id>/`
Delete an artist. Cascades to their albums and album-song links.

**204 No Content**

### `GET /api/artists/<id>/albums/` *(bonus)*
List albums belonging to a specific artist.

**200 Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Dark Side of the Moon",
      "artist": 1,
      "artist_name": "Pink Floyd",
      "release_year": 1973,
      "songs": [
        {"id": 1, "title": "Speak to Me", "track_number": 1},
        {"id": 2, "title": "Breathe", "track_number": 2}
      ]
    }
  ]
}
```

---

## Albums

### `GET /api/albums/`
List albums.

**Query params:** `search` (searches `title`, `artist__name`), `ordering` (`id`, `title`, `release_year`)

**200 Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Dark Side of the Moon",
      "artist": 1,
      "artist_name": "Pink Floyd",
      "release_year": 1973,
      "songs": [
        {"id": 1, "title": "Speak to Me", "track_number": 1},
        {"id": 2, "title": "Breathe", "track_number": 2}
      ]
    }
  ]
}
```

### `POST /api/albums/`
Create an album. `artist` is the artist ID.

**Request:**
```json
{"title": "New Album", "artist": 1, "release_year": 2024}
```

**201 Response:**
```json
{
  "id": 6,
  "title": "New Album",
  "artist": 1,
  "artist_name": "Pink Floyd",
  "release_year": 2024,
  "songs": []
}
```

**400** if required fields missing or artist doesn't exist.

### `GET /api/albums/<id>/`
Retrieve a single album with its songs (ordered by track number).

### `PUT /api/albums/<id>/`
Update an album (full update).

**Request:**
```json
{"title": "Renamed Album", "artist": 1, "release_year": 2024}
```

### `PATCH /api/albums/<id>/`
Partial update (not required by spec but supported by DRF generics).

### `DELETE /api/albums/<id>/`
Delete an album. Cascades to its album-song links (songs themselves survive).

**204 No Content**

---

## Album ↔ Song Management (Through Model)

These endpoints manage the `AlbumSong` through model — adding a song to an
album with a specific track number, and removing it.

### `GET /api/albums/<id>/songs/`
List the AlbumSong links for an album (with song details).

**200 Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {"id": 1, "album": 1, "song": 1, "track_number": 1},
    {"id": 2, "album": 1, "song": 2, "track_number": 2}
  ]
}
```

### `POST /api/albums/<id>/songs/`
Add a song to an album with a track number. The album is inferred from the URL.

**Request:**
```json
{"song": 3, "track_number": 3}
```

**201 Response:**
```json
{"id": 9, "album": 1, "song": 3, "track_number": 3}
```

**400** if `track_number` already exists for this album (unique constraint),
or if `song` doesn't exist, or fields missing.

### `DELETE /api/albums/<id>/songs/<song_id>/`
Remove a song from an album (deletes the AlbumSong link). The song itself
is not deleted.

**204 No Content**

---

## Songs

### `GET /api/songs/`
List songs.

**Query params:** `search` (searches `title`), `ordering` (`id`, `title`)

**200 Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Speak to Me",
      "albums": [
        {
          "id": 1,
          "title": "The Dark Side of the Moon",
          "release_year": 1973,
          "artist": "Pink Floyd",
          "track_number": 1
        }
      ]
    }
  ]
}
```

### `POST /api/songs/`
Create a song.

**Request:**
```json
{"title": "New Song"}
```

**201 Response:**
```json
{"id": 11, "title": "New Song", "albums": []}
```

### `GET /api/songs/<id>/`
Retrieve a single song with the albums it appears in.

### `PUT /api/songs/<id>/`
Update a song.

**Request:**
```json
{"title": "Renamed Song"}
```

### `DELETE /api/songs/<id>/`
Delete a song. Cascades to any album-song links that reference it.

**204 No Content**

---

## Summary Table

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/artists/` | List artists |
| POST | `/api/artists/` | Create artist |
| GET | `/api/artists/<id>/` | Retrieve artist |
| PUT | `/api/artists/<id>/` | Update artist |
| DELETE | `/api/artists/<id>/` | Delete artist |
| GET | `/api/artists/<id>/albums/` | List albums by artist |
| GET | `/api/albums/` | List albums |
| POST | `/api/albums/` | Create album |
| GET | `/api/albums/<id>/` | Retrieve album |
| PUT | `/api/albums/<id>/` | Update album |
| DELETE | `/api/albums/<id>/` | Delete album |
| GET | `/api/albums/<id>/songs/` | List songs in album |
| POST | `/api/albums/<id>/songs/` | Add song to album |
| DELETE | `/api/albums/<id>/songs/<song_id>/` | Remove song from album |
| GET | `/api/songs/` | List songs |
| POST | `/api/songs/` | Create song |
| GET | `/api/songs/<id>/` | Retrieve song |
| PUT | `/api/songs/<id>/` | Update song |
| DELETE | `/api/songs/<id>/` | Delete song |

## Admin Panel
Available at `http://localhost:8000/admin/` — all models registered with
search and inlines for manual testing.
