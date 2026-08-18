import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../api', () => ({
  getSongs: vi.fn(() => Promise.resolve({ data: { count: 5, results: [{ id: 1, title: 'A' }] } })),
  getSong: vi.fn(() => Promise.resolve({ data: { id: 1, title: 'A', albums: [] } })),
  createSong: vi.fn(() => Promise.resolve({ data: { id: 2, title: 'New', albums: [] } })),
  updateSong: vi.fn(() => Promise.resolve({ data: { id: 1, title: 'Updated', albums: [] } })),
  deleteSong: vi.fn(() => Promise.resolve({})),
}))

import { useSongStore } from '../../stores/song'
import { getSongs, getSong, createSong, updateSong, deleteSong } from '../../api'

describe('useSongStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchList populates items', async () => {
    const store = useSongStore()
    await store.fetchList({ page: 1 })
    expect(getSongs).toHaveBeenCalledWith({ page: 1 })
    expect(store.items).toEqual([{ id: 1, title: 'A' }])
  })

  it('fetchDetail sets currentItem', async () => {
    const store = useSongStore()
    await store.fetchDetail(1)
    expect(getSong).toHaveBeenCalledWith(1)
    expect(store.currentItem).toEqual({ id: 1, title: 'A', albums: [] })
  })

  it('create calls createSong', async () => {
    const store = useSongStore()
    const data = await store.create({ title: 'New' })
    expect(createSong).toHaveBeenCalledWith({ title: 'New' })
    expect(data.id).toBe(2)
  })

  it('update calls updateSong and sets currentItem', async () => {
    const store = useSongStore()
    await store.update(1, { title: 'Updated' })
    expect(updateSong).toHaveBeenCalledWith(1, { title: 'Updated' })
    expect(store.currentItem.title).toBe('Updated')
  })

  it('remove calls deleteSong', async () => {
    const store = useSongStore()
    await store.remove(1)
    expect(deleteSong).toHaveBeenCalledWith(1)
  })
})
