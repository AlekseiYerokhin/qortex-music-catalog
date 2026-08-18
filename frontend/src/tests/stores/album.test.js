import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../api', () => ({
  getAlbums: vi.fn(() => Promise.resolve({ data: { count: 2, results: [{ id: 1, title: 'A' }] } })),
  getAlbum: vi.fn(() => Promise.resolve({ data: { id: 1, title: 'A', artist: 1, artist_name: 'X', release_year: 2020, songs: [] } })),
  createAlbum: vi.fn(() => Promise.resolve({ data: { id: 2, title: 'New', artist: 1, artist_name: 'X', release_year: 2024, songs: [] } })),
  updateAlbum: vi.fn(() => Promise.resolve({ data: { id: 1, title: 'Updated', artist: 1, artist_name: 'X', release_year: 2020, songs: [] } })),
  deleteAlbum: vi.fn(() => Promise.resolve({})),
  getArtistAlbums: vi.fn(() => Promise.resolve({ data: { results: [{ id: 1, title: 'A' }] } })),
  addSongToAlbum: vi.fn(() => Promise.resolve({ data: { id: 1, album: 1, song: 2, track_number: 3 } })),
  removeSongFromAlbum: vi.fn(() => Promise.resolve({})),
}))

import { useAlbumStore } from '../../stores/album'
import { getAlbums, getAlbum, createAlbum, deleteAlbum, getArtistAlbums, addSongToAlbum, removeSongFromAlbum } from '../../api'

describe('useAlbumStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchList populates items', async () => {
    const store = useAlbumStore()
    await store.fetchList({ page: 1 })
    expect(getAlbums).toHaveBeenCalledWith({ page: 1 })
    expect(store.items).toEqual([{ id: 1, title: 'A' }])
  })

  it('fetchDetail sets currentItem', async () => {
    const store = useAlbumStore()
    await store.fetchDetail(1)
    expect(getAlbum).toHaveBeenCalledWith(1, { signal: undefined })
    expect(store.currentItem).toEqual({ id: 1, title: 'A', artist: 1, artist_name: 'X', release_year: 2020, songs: [] })
  })

  it('create calls createAlbum', async () => {
    const store = useAlbumStore()
    const data = await store.create({ title: 'New', artist: 1, release_year: 2024 })
    expect(createAlbum).toHaveBeenCalledWith({ title: 'New', artist: 1, release_year: 2024 })
    expect(data.id).toBe(2)
  })

  it('remove calls deleteAlbum', async () => {
    const store = useAlbumStore()
    await store.remove(1)
    expect(deleteAlbum).toHaveBeenCalledWith(1)
  })

  it('fetchAlbumsByArtist calls getArtistAlbums', async () => {
    const store = useAlbumStore()
    const result = await store.fetchAlbumsByArtist(1)
    expect(getArtistAlbums).toHaveBeenCalledWith(1, {}, { signal: undefined })
    expect(result).toEqual([{ id: 1, title: 'A' }])
  })

  it('addSongToAlbum calls addSongToAlbum API', async () => {
    const store = useAlbumStore()
    const data = await store.addSongToAlbum(1, { song: 2, track_number: 3 })
    expect(addSongToAlbum).toHaveBeenCalledWith(1, { song: 2, track_number: 3 })
    expect(data.track_number).toBe(3)
  })

  it('removeSongFromAlbum calls removeSongFromAlbum API', async () => {
    const store = useAlbumStore()
    await store.removeSongFromAlbum(1, 2)
    expect(removeSongFromAlbum).toHaveBeenCalledWith(1, 2)
  })
})
