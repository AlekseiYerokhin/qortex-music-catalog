<template>
  <q-page class="p-6 max-w-5xl mx-auto">
    <q-breadcrumbs class="mb-4">
      <q-breadcrumbs-el label="Artists" :to="{ name: 'artist-list' }" icon="person" />
      <q-breadcrumbs-el :label="artist?.name || '...'" />
    </q-breadcrumbs>

    <q-inner-loading :showing="artistStore.loading && !artist">
      <q-spinner size="40px" color="primary" />
    </q-inner-loading>

    <template v-if="artist">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <q-avatar size="56px" color="primary" text-color="white" icon="person" />
          <div>
            <h1 class="text-2xl font-bold text-grey-9">{{ artist.name }}</h1>
            <p class="text-grey-6">{{ artist.albums_count }} album{{ artist.albums_count === 1 ? '' : 's' }}</p>
          </div>
        </div>
        <div class="flex gap-2">
          <q-btn outline color="primary" icon="edit" label="Edit" no-caps :to="{ name: 'artist-edit', params: { id: artist.id } }" />
          <q-btn outline color="negative" icon="delete" label="Delete" no-caps @click="confirmDelete" />
        </div>
      </div>

      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-grey-8">Albums</h2>
        <q-btn color="secondary" icon="add" label="New Album" no-caps :to="{ name: 'album-new' }" />
      </div>

      <q-inner-loading :showing="albumsLoading">
        <q-spinner size="32px" color="primary" />
      </q-inner-loading>

      <div v-if="!albumsLoading && albums.length === 0" class="text-grey-6 text-center py-12">
        <q-icon name="album" size="48px" class="block mx-auto mb-2 opacity-40" />
        No albums yet.
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <q-card
          v-for="album in albums"
          :key="album.id"
          flat
          bordered
          class="cursor-pointer q-hoverable rounded-lg"
          @click="$router.push({ name: 'album-detail', params: { id: album.id } })"
        >
          <q-card-section>
            <div class="text-h6 text-grey-9">{{ album.title }}</div>
            <div class="text-caption text-grey-6">{{ album.release_year || '—' }}</div>
            <div class="text-caption text-grey-6 mt-1">
              {{ album.songs?.length || 0 }} song{{ album.songs?.length === 1 ? '' : 's' }}
            </div>
          </q-card-section>
        </q-card>
      </div>
    </template>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useArtistStore } from '../stores/artist'
import { useAlbumStore } from '../stores/album'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const artistStore = useArtistStore()
const albumStore = useAlbumStore()

const albums = ref([])
const albumsLoading = ref(false)

const artist = ref(null)

async function loadAlbums() {
  albumsLoading.value = true
  try {
    albums.value = await albumStore.fetchAlbumsByArtist(route.params.id)
  } catch {
    /* handled by interceptor */
  } finally {
    albumsLoading.value = false
  }
}

function confirmDelete() {
  $q.dialog({
    title: 'Delete Artist',
    message: `Delete "${artist.value.name}" and all their albums?`,
    cancel: true,
    persistent: true,
    ok: { label: 'Delete', color: 'negative', unelevated: true },
  }).onOk(async () => {
    await artistStore.deleteArtist(artist.value.id)
    $q.notify({ type: 'positive', message: 'Artist deleted' })
    router.push({ name: 'artist-list' })
  })
}

onMounted(async () => {
  try {
    artist.value = await artistStore.fetchArtist(route.params.id)
    await loadAlbums()
  } catch {
    /* handled by interceptor */
  }
})
</script>
