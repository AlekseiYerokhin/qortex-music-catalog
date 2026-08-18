import {
  getArtists,
  getArtist,
  createArtist,
  updateArtist,
  deleteArtist,
} from '../api'
import { createCrudStore } from './createCrudStore'

export const useArtistStore = createCrudStore('artist', {
  list: getArtists,
  retrieve: getArtist,
  create: createArtist,
  update: updateArtist,
  delete: deleteArtist,
})
