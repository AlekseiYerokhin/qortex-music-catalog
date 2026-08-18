import {
  getSongs,
  getSong,
  createSong,
  updateSong,
  deleteSong,
} from '../api'
import { createCrudStore } from './createCrudStore'

export const useSongStore = createCrudStore('song', {
  list: getSongs,
  retrieve: getSong,
  create: createSong,
  update: updateSong,
  delete: deleteSong,
})
