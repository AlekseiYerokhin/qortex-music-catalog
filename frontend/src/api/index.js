import axios from 'axios'
import { Notify } from 'quasar'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred'
    if (error.response) {
      const data = error.response.data
      if (data?.detail) {
        message = data.detail
      } else if (typeof data === 'object' && data !== null) {
        const parts = []
        for (const [field, errors] of Object.entries(data)) {
          const value = Array.isArray(errors) ? errors.join(', ') : String(errors)
          parts.push(`${field}: ${value}`)
        }
        message = parts.join(' | ')
      }
    } else if (error.request) {
      message = 'No response from server. Is the backend running?'
    }
    Notify.create({ type: 'negative', message })
    return Promise.reject(error)
  }
)

export const getArtists = (params) => api.get('/artists/', { params })
export const getArtist = (id) => api.get(`/artists/${id}/`)
export const createArtist = (data) => api.post('/artists/', data)
export const updateArtist = (id, data) => api.put(`/artists/${id}/`, data)
export const deleteArtist = (id) => api.delete(`/artists/${id}/`)
export const getArtistAlbums = (id, params) =>
  api.get(`/artists/${id}/albums/`, { params })

export const getAlbums = (params) => api.get('/albums/', { params })
export const getAlbum = (id) => api.get(`/albums/${id}/`)
export const createAlbum = (data) => api.post('/albums/', data)
export const updateAlbum = (id, data) => api.put(`/albums/${id}/`, data)
export const deleteAlbum = (id) => api.delete(`/albums/${id}/`)
export const addSongToAlbum = (albumId, data) =>
  api.post(`/albums/${albumId}/songs/`, data)
export const removeSongFromAlbum = (albumId, songId) =>
  api.delete(`/albums/${albumId}/songs/${songId}/`)

export const getSongs = (params) => api.get('/songs/', { params })
export const getSong = (id) => api.get(`/songs/${id}/`)
export const createSong = (data) => api.post('/songs/', data)
export const updateSong = (id, data) => api.put(`/songs/${id}/`, data)
export const deleteSong = (id) => api.delete(`/songs/${id}/`)

export default api
