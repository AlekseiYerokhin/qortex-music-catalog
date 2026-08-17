import { defineStore } from 'pinia'
import {
  getArtists,
  getArtist,
  createArtist,
  updateArtist,
  deleteArtist,
} from '../api'

export const useArtistStore = defineStore('artist', {
  state: () => ({
    artists: [],
    currentArtist: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchArtists(params) {
      this.loading = true
      this.error = null
      try {
        const { data } = await getArtists(params)
        this.artists = data.results || []
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchArtist(id) {
      this.loading = true
      this.error = null
      try {
        const { data } = await getArtist(id)
        this.currentArtist = data
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async createArtist(payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await createArtist(payload)
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async updateArtist(id, payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await updateArtist(id, payload)
        this.currentArtist = data
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async deleteArtist(id) {
      this.loading = true
      this.error = null
      try {
        await deleteArtist(id)
        if (this.currentArtist?.id === id) this.currentArtist = null
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
  },
})
