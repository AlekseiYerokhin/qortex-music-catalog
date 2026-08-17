<template>
  <q-page class="p-6 max-w-5xl mx-auto">
    <q-breadcrumbs class="mb-4">
      <q-breadcrumbs-el label="Artists" :to="{ name: 'artist-list' }" icon="person" />
      <q-breadcrumbs-el v-if="album?.artist_name" :label="album.artist_name" :to="{ name: 'artist-detail', params: { id: album.artist } }" />
      <q-breadcrumbs-el label="Albums" :to="{ name: 'album-list' }" icon="album" />
      <q-breadcrumbs-el :label="album?.title || '...'" />
    </q-breadcrumbs>

    <q-inner-loading :showing="albumStore.loading && !album">
      <q-spinner size="40px" color="primary" />
    </q-inner-loading>

    <template v-if="album">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <q-avatar size="56px" color="secondary" text-color="white" icon="album" />
          <div>
            <h1 class="text-2xl font-bold text-grey-9">{{ album.title }}</h1>
            <p class="text-grey-6">
              <span>{{ album.artist_name }}</span>
              <span v-if="album.release_year"> • {{ album.release_year }}</span>
            </p>
          </div>
        </div>
        <div class="flex gap-2">
          <q-btn outline color="primary" icon="edit" label="Edit" no-caps :to="{ name: 'album-edit', params: { id: album.id } }" />
          <q-btn outline color="negative" icon="delete" label="Delete" no-caps @click="confirmDeleteAlbum" />
        </div>
      </div>

      <q-card flat bordered class="rounded-lg mb-6">
        <q-card-section>
          <div class="text-h6 text-grey-8 mb-4">Songs in this Album</div>

          <q-table
            :rows="albumSongs"
            :columns="songColumns"
            row-key="id"
            flat
            :loading="albumStore.loading"
          >
            <template #body-cell-track_number="props">
              <q-td :props="props" auto-width>
                <q-badge color="primary" :label="props.row.track_number" />
              </q-td>
            </template>
            <template #body-cell-actions="props">
              <q-td :props="props" class="text-right">
                <q-btn flat dense round icon="remove_circle_outline" color="negative" @click="confirmRemoveSong(props.row)">
                  <q-tooltip>Remove from album</q-tooltip>
                </q-btn>
              </q-td>
            </template>
          </q-table>

          <div v-if="albumSongs.length === 0 && !albumStore.loading" class="text-grey-6 text-center py-6">
            No songs assigned to this album yet.
          </div>
        </q-card-section>
      </q-card>

      <q-card flat bordered class="rounded-lg">
        <q-card-section>
          <div class="text-h6 text-grey-8 mb-4">Add Song to Album</div>
          <div class="flex flex-col sm:flex-row gap-3 items-end">
            <q-select
              v-model="addForm.song"
              :options="songOptions"
              label="Select Song"
              outlined
              dense
              emit-value
              map-options
              class="flex-1 w-full"
            />
            <q-input
              v-model.number="addForm.track_number"
              type="number"
              label="Track #"
              outlined
              dense
              style="min-width: 120px"
            />
            <q-btn color="primary" icon="add" label="Add" unelevated no-caps :loading="albumStore.loading" @click="onAddSong" />
          </div>
        </q-card-section>
      </q-card>
    </template>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAlbumStore } from '../stores/album'
import { useSongStore } from '../stores/song'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const albumStore = useAlbumStore()
const songStore = useSongStore()

const album = computed(() => albumStore.currentAlbum)

const albumSongs = computed(() => {
  const songs = album.value?.songs || []
  return [...songs].sort((a, b) => a.track_number - b.track_number)
})

const songOptions = computed(() =>
  songStore.songs.map((s) => ({ label: s.title, value: s.id }))
)

const addForm = reactive({
  song: null,
  track_number: null,
})

const songColumns = [
  { name: 'track_number', label: '#', field: 'track_number', align: 'left', sortable: true },
  { name: 'title', label: 'Title', field: 'title', align: 'left', sortable: true },
  { name: 'actions', label: '', field: 'actions', align: 'right', sortable: false },
]

async function reloadAlbum() {
  await albumStore.fetchAlbum(route.params.id)
}

async function onAddSong() {
  if (!addForm.song || !addForm.track_number) {
    $q.notify({ type: 'warning', message: 'Please select a song and track number' })
    return
  }
  try {
    await albumStore.addSongToAlbum(route.params.id, {
      song: addForm.song,
      track_number: addForm.track_number,
    })
    $q.notify({ type: 'positive', message: 'Song added to album' })
    addForm.song = null
    addForm.track_number = null
    await reloadAlbum()
  } catch {
    /* handled by interceptor */
  }
}

function confirmRemoveSong(song) {
  $q.dialog({
    title: 'Remove Song',
    message: `Remove "${song.title}" from this album? The song itself will not be deleted.`,
    cancel: true,
    persistent: true,
    ok: { label: 'Remove', color: 'negative', unelevated: true },
  }).onOk(async () => {
    await albumStore.removeSongFromAlbum(route.params.id, song.id)
    $q.notify({ type: 'positive', message: 'Song removed from album' })
    await reloadAlbum()
  })
}

function confirmDeleteAlbum() {
  $q.dialog({
    title: 'Delete Album',
    message: `Delete "${album.value.title}"? Song links will be removed but songs survive.`,
    cancel: true,
    persistent: true,
    ok: { label: 'Delete', color: 'negative', unelevated: true },
  }).onOk(async () => {
    await albumStore.deleteAlbum(album.value.id)
    $q.notify({ type: 'positive', message: 'Album deleted' })
    router.push({ name: 'album-list' })
  })
}

onMounted(async () => {
  await songStore.fetchSongs({ page_size: 100 })
  await reloadAlbum()
})
</script>
