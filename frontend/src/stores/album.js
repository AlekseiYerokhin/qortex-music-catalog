import { defineStore } from 'pinia'
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

export const useAlbumStore = defineStore('album', {
  state: () => ({
    albums: [],
    currentAlbum: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchAlbums(params) {
      this.loading = true
      this.error = null
      try {
        const { data } = await getAlbums(params)
        this.albums = data.results || []
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchAlbum(id) {
      this.loading = true
      this.error = null
      try {
        const { data } = await getAlbum(id)
        this.currentAlbum = data
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async createAlbum(payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await createAlbum(payload)
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async updateAlbum(id, payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await updateAlbum(id, payload)
        this.currentAlbum = data
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async deleteAlbum(id) {
      this.loading = true
      this.error = null
      try {
        await deleteAlbum(id)
        if (this.currentAlbum?.id === id) this.currentAlbum = null
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchAlbumsByArtist(artistId) {
      this.loading = true
      this.error = null
      try {
        const { data } = await getArtistAlbums(artistId)
        return data.results || []
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
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
})
