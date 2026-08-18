import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../api', () => ({
  getArtists: vi.fn(() => Promise.resolve({ data: { count: 3, results: [{ id: 1, name: 'A' }] } })),
  getArtist: vi.fn(() => Promise.resolve({ data: { id: 1, name: 'A', albums_count: 2 } })),
  createArtist: vi.fn(() => Promise.resolve({ data: { id: 2, name: 'New', albums_count: 0 } })),
  updateArtist: vi.fn(() => Promise.resolve({ data: { id: 1, name: 'Updated', albums_count: 2 } })),
  deleteArtist: vi.fn(() => Promise.resolve({})),
  getArtistAlbums: vi.fn(),
}))

import { useArtistStore } from '../../stores/artist'
import { getArtists, getArtist, createArtist, updateArtist, deleteArtist } from '../../api'

describe('useArtistStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchList populates items and returns data', async () => {
    const store = useArtistStore()
    const data = await store.fetchList({ page: 1 })
    expect(getArtists).toHaveBeenCalledWith({ page: 1 })
    expect(store.items).toEqual([{ id: 1, name: 'A' }])
    expect(data.count).toBe(3)
    expect(store.loading).toBe(false)
  })

  it('fetchDetail sets currentItem', async () => {
    const store = useArtistStore()
    const data = await store.fetchDetail(1)
    expect(getArtist).toHaveBeenCalledWith(1, { signal: undefined })
    expect(store.currentItem).toEqual({ id: 1, name: 'A', albums_count: 2 })
    expect(data.name).toBe('A')
  })

  it('create calls createArtist and returns data', async () => {
    const store = useArtistStore()
    const data = await store.create({ name: 'New' })
    expect(createArtist).toHaveBeenCalledWith({ name: 'New' })
    expect(data.id).toBe(2)
  })

  it('update calls updateArtist and sets currentItem', async () => {
    const store = useArtistStore()
    const data = await store.update(1, { name: 'Updated' })
    expect(updateArtist).toHaveBeenCalledWith(1, { name: 'Updated' })
    expect(store.currentItem).toEqual({ id: 1, name: 'Updated', albums_count: 2 })
    expect(data.name).toBe('Updated')
  })

  it('remove calls deleteArtist', async () => {
    const store = useArtistStore()
    store.currentItem = { id: 1, name: 'A' }
    await store.remove(1)
    expect(deleteArtist).toHaveBeenCalledWith(1)
    expect(store.currentItem).toBeNull()
  })

  it('fetchCount returns count without populating items', async () => {
    const store = useArtistStore()
    store.items = [{ id: 99, name: 'existing' }]
    const count = await store.fetchCount()
    expect(getArtists).toHaveBeenCalledWith({ page_size: 1 })
    expect(count).toBe(3)
    expect(store.items).toEqual([{ id: 99, name: 'existing' }])
  })

  it('sets error on fetch failure', async () => {
    const store = useArtistStore()
    getArtists.mockRejectedValueOnce(new Error('Request failed with status code 500'))
    await expect(store.fetchList({})).rejects.toThrow()
    expect(store.error).toBe('Request failed with status code 500')
    expect(store.loading).toBe(false)
  })
})
