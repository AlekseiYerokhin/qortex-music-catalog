<template>
  <q-page class="p-6 max-w-5xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-grey-9">Welcome to Qortex</h1>
      <p class="text-grey-7 mt-1">Manage your music catalog — artists, albums, and songs.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <q-card
        v-for="card in cards"
        :key="card.to"
        flat
        bordered
        class="cursor-pointer q-hoverable transition-shadow hover:shadow-lg rounded-lg"
        @click="$router.push(card.to)"
      >
        <q-card-section class="flex flex-col items-center text-center py-8">
          <q-icon :name="card.icon" size="56px" color="primary" />
          <div class="text-h6 mt-4 text-grey-9">{{ card.label }}</div>
          <div class="text-subtitle2 text-grey-6 mt-1">
            <q-spinner v-if="counts[card.key] === null" size="20px" />
            <span v-else>{{ counts[card.key] }} total</span>
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useArtistStore } from '../stores/artist'
import { useAlbumStore } from '../stores/album'
import { useSongStore } from '../stores/song'

const artistStore = useArtistStore()
const albumStore = useAlbumStore()
const songStore = useSongStore()

const counts = ref({ artists: null, albums: null, songs: null })

const cards = [
  { label: 'Artists', icon: 'person', to: '/artists', key: 'artists' },
  { label: 'Albums', icon: 'album', to: '/albums', key: 'albums' },
  { label: 'Songs', icon: 'music_note', to: '/songs', key: 'songs' },
]

onMounted(async () => {
  try {
    const artistData = await artistStore.fetchArtists({ page_size: 1 })
    counts.value.artists = artistData.count
  } catch {
    counts.value.artists = 0
  }
  try {
    const albumData = await albumStore.fetchAlbums({ page_size: 1 })
    counts.value.albums = albumData.count
  } catch {
    counts.value.albums = 0
  }
  try {
    const songData = await songStore.fetchSongs({ page_size: 1 })
    counts.value.songs = songData.count
  } catch {
    counts.value.songs = 0
  }
})
</script>
