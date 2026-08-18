import {
  getAlbums,
  getAlbum,
  createAlbum,
  updateAlbum,
  deleteAlbum,
  getArtistAlbums,
  addSongToAlbum,
  removeSongFromAlbum,
} from '../api'
import { createCrudStore } from './createCrudStore'

export const useAlbumStore = createCrudStore(
  'album',
  {
    list: getAlbums,
    retrieve: getAlbum,
    create: createAlbum,
    update: updateAlbum,
    delete: deleteAlbum,
  },
  {
    extraActions: {
      async fetchAlbumsByArtist(artistId, options = {}) {
        this.loading = true
        this.error = null
        let cancelled = false
        try {
          const { data } = await getArtistAlbums(artistId, {}, { signal: options.signal })
          return data.results || []
        } catch (e) {
          if (e.code === 'ERR_CANCELED') {
            cancelled = true
            return []
          }
          this.error = e.message
          throw e
        } finally {
          if (!cancelled) this.loading = false
        }
      },

      async addSongToAlbum(albumId, payload) {
        this.loading = true
        this.error = null
        try {
          const { data } = await addSongToAlbum(albumId, payload)
          return data
        } catch (e) {
          this.error = e.message
          throw e
        } finally {
          this.loading = false
        }
      },

      async removeSongFromAlbum(albumId, songId) {
        this.loading = true
        this.error = null
        try {
          await removeSongFromAlbum(albumId, songId)
        } catch (e) {
          this.error = e.message
          throw e
        } finally {
          this.loading = false
        }
      },
    },
  }
)
