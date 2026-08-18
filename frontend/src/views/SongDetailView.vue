<template>
  <q-page class="p-6 max-w-5xl mx-auto">
    <q-breadcrumbs class="mb-4">
      <q-breadcrumbs-el label="Songs" :to="{ name: 'song-list' }" icon="music_note" />
      <q-breadcrumbs-el :label="song?.title || '...'" />
    </q-breadcrumbs>

    <q-inner-loading :showing="songStore.loading && !song">
      <q-spinner size="40px" color="primary" />
    </q-inner-loading>

    <template v-if="song">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <q-avatar size="56px" color="accent" text-color="white" icon="music_note" />
          <div>
            <h1 class="text-2xl font-bold text-grey-9">{{ song.title }}</h1>
            <p class="text-grey-6">{{ song.albums?.length || 0 }} album{{ song.albums?.length === 1 ? '' : 's' }}</p>
          </div>
        </div>
        <div class="flex gap-2">
          <q-btn outline color="primary" icon="edit" label="Edit" no-caps :to="{ name: 'song-edit', params: { id: song.id } }" />
          <q-btn outline color="negative" icon="delete" label="Delete" no-caps @click="confirmDelete" />
        </div>
      </div>

      <h2 class="text-xl font-semibold text-grey-8 mb-4">Appears In</h2>

      <div v-if="song.albums?.length === 0" class="text-grey-6 text-center py-12">
        <q-icon name="album" size="48px" class="block mx-auto mb-2 opacity-40" />
        This song is not in any album yet.
      </div>

      <q-table
        v-else
        :rows="song.albums"
        :columns="columns"
        row-key="id"
        flat
        bordered
      >
        <template #body-cell-track_number="props">
          <q-td :props="props" auto-width>
            <q-badge color="primary" :label="props.row.track_number" />
          </q-td>
        </template>
        <template #body-cell-title="props">
          <q-td :props="props">
            <router-link :to="{ name: 'album-detail', params: { id: props.row.id } }" class="text-primary no-underline">
              {{ props.row.title }}
            </router-link>
          </q-td>
        </template>
      </q-table>
    </template>
  </q-page>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useSongStore } from '../stores/song'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const songStore = useSongStore()

const song = computed(() => songStore.currentSong)

const columns = [
  { name: 'track_number', label: '#', field: 'track_number', align: 'left' },
  { name: 'title', label: 'Album', field: 'title', align: 'left' },
  { name: 'artist', label: 'Artist', field: 'artist', align: 'left' },
  { name: 'release_year', label: 'Year', field: 'release_year', align: 'left' },
]

function confirmDelete() {
  $q.dialog({
    title: 'Delete Song',
    message: `Delete "${song.value.title}"? It will be removed from all albums.`,
    cancel: true,
    persistent: true,
    ok: { label: 'Delete', color: 'negative', unelevated: true },
  }).onOk(async () => {
    try {
      await songStore.deleteSong(song.value.id)
      $q.notify({ type: 'positive', message: 'Song deleted' })
      router.push({ name: 'song-list' })
    } catch {
      /* handled by interceptor */
    }
  })
}

watch(() => route.params.id, (newId) => {
  if (newId) songStore.fetchSong(newId)
})

onMounted(() => {
  songStore.fetchSong(route.params.id)
})
</script>
