<template>
  <q-page class="p-6 max-w-2xl mx-auto">
    <q-card flat bordered class="rounded-lg">
      <q-card-section>
        <div class="text-h6 text-grey-9">{{ isEdit ? 'Edit Album' : 'New Album' }}</div>
      </q-card-section>

      <q-inner-loading :showing="albumStore.loading && isEdit">
        <q-spinner size="40px" color="primary" />
      </q-inner-loading>

      <q-form @submit.prevent="onSave" class="q-gutter-md q-pa-md">
        <q-input
          v-model="form.title"
          label="Album Title *"
          outlined
          dense
          :rules="[val => !!val || 'Title is required']"
          lazy-rules
        />

        <q-select
          v-model="form.artist"
          :options="filteredArtistOptions"
          label="Artist *"
          outlined
          dense
          emit-value
          map-options
          use-input
          input-debounce="300"
          :rules="[val => !!val || 'Artist is required']"
          lazy-rules
          @filter="onFilterArtist"
        >
          <template #no-option>
            <q-item>
              <q-item-section class="text-grey-6">No artists found</q-item-section>
            </q-item>
          </template>
        </q-select>

        <q-input
          v-model.number="form.release_year"
          type="number"
          label="Release Year *"
          outlined
          dense
          :rules="[
            val => !!val || 'Release year is required',
            val => val >= 1860 || 'Year must be 1860 or later',
            val => val <= new Date().getFullYear() || 'Year cannot be in the future'
          ]"
          lazy-rules
        />

        <div class="flex justify-end gap-3 mt-4">
          <q-btn flat label="Cancel" no-caps @click="$router.push({ name: 'album-list' })" />
          <q-btn color="primary" :label="isEdit ? 'Update' : 'Create'" type="submit" unelevated no-caps :loading="albumStore.loading" />
        </div>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useArtistStore } from '../stores/artist'
import { useAlbumStore } from '../stores/album'
import { getArtists } from '../api'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const artistStore = useArtistStore()
const albumStore = useAlbumStore()

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  artist: null,
  release_year: null,
})

const filteredArtistOptions = ref([])

async function onFilterArtist(val, update) {
  if (!val) {
    update(() => {
      filteredArtistOptions.value = artistStore.artists.map((a) => ({ label: a.name, value: a.id }))
    })
    return
  }
  update(async () => {
    const { data } = await getArtists({ search: val, page_size: 50 })
    filteredArtistOptions.value = data.results.map((a) => ({ label: a.name, value: a.id }))
  })
}

async function loadAlbum() {
  if (!isEdit.value) return
  const data = await albumStore.fetchAlbum(route.params.id)
  form.title = data.title
  form.artist = data.artist
  form.release_year = data.release_year
}

async function onSave() {
  try {
    const payload = {
      title: form.title,
      artist: form.artist,
      release_year: form.release_year,
    }
    let saved
    if (isEdit.value) {
      saved = await albumStore.updateAlbum(route.params.id, payload)
      $q.notify({ type: 'positive', message: 'Album updated' })
    } else {
      saved = await albumStore.createAlbum(payload)
      $q.notify({ type: 'positive', message: 'Album created' })
    }
    router.push({ name: 'album-detail', params: { id: saved.id } })
  } catch {
    /* handled by interceptor */
  }
}

onMounted(async () => {
  await artistStore.fetchArtists({ page_size: 100 })
  filteredArtistOptions.value = artistStore.artists.map((a) => ({ label: a.name, value: a.id }))
  await loadAlbum()
})
</script>
