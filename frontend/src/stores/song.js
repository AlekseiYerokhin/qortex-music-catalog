import { defineStore } from 'pinia'
import {
  getSongs,
  getSong,
  createSong,
  updateSong,
  deleteSong,
} from '../api'

export const useSongStore = defineStore('song', {
  state: () => ({
    songs: [],
    currentSong: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchSongs(params) {
      this.loading = true
      this.error = null
      try {
        const { data } = await getSongs(params)
        this.songs = data.results
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchSong(id) {
      this.loading = true
      this.error = null
      try {
        const { data } = await getSong(id)
        this.currentSong = data
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async createSong(payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await createSong(payload)
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async updateSong(id, payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await updateSong(id, payload)
        this.currentSong = data
        return data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
    async deleteSong(id) {
      this.loading = true
      this.error = null
      try {
        await deleteSong(id)
        if (this.currentSong?.id === id) this.currentSong = null
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },
  },
})
