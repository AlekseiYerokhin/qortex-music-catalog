<template>
  <q-page class="p-6 max-w-2xl mx-auto">
    <q-card
      flat
      bordered
      class="rounded-lg"
    >
      <q-card-section>
        <div class="text-h6 text-grey-9">
          {{ isEdit ? 'Edit Album' : 'New Album' }}
        </div>
      </q-card-section>

      <q-inner-loading :showing="albumStore.loading && isEdit">
        <q-spinner
          size="40px"
          color="primary"
        />
      </q-inner-loading>

      <q-form
        class="q-gutter-md q-pa-md"
        @submit.prevent="onSave"
      >
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
              <q-item-section class="text-grey-6">
                No artists found
              </q-item-section>
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
          <q-btn
            flat
            label="Cancel"
            no-caps
            @click="$router.push({ name: 'album-list' })"
          />
          <q-btn
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            type="submit"
            unelevated
            no-caps
            :loading="albumStore.loading"
          />
        </div>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useAlbumStore } from '../stores/album'
import { getArtist, getArtists } from '../api'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
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
      filteredArtistOptions.value = artistOptions.value.map((a) => ({ label: a.name, value: a.id }))
    })
    return
  }
  const { data } = await getArtists({ search: val, page_size: 50 })
  update(() => {
    filteredArtistOptions.value = data.results.map((a) => ({ label: a.name, value: a.id }))
  })
}

const artistOptions = ref([])

async function loadAlbum() {
  if (!isEdit.value) return
  const data = await albumStore.fetchDetail(route.params.id)
  form.title = data.title
  form.artist = data.artist
  form.release_year = data.release_year
  if (data.artist && !filteredArtistOptions.value.some((a) => a.value === data.artist)) {
    const { data: artistData } = await getArtist(data.artist)
    filteredArtistOptions.value = [
      { label: artistData.name, value: artistData.id },
      ...filteredArtistOptions.value,
    ]
  }
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
      saved = await albumStore.update(route.params.id, payload)
      $q.notify({ type: 'positive', message: 'Album updated' })
    } else {
      saved = await albumStore.create(payload)
      $q.notify({ type: 'positive', message: 'Album created' })
    }
    router.push({ name: 'album-detail', params: { id: saved.id } })
  } catch {
    /* handled by interceptor */
  }
}

async function loadPage() {
  const { data } = await getArtists({ page_size: 100 })
  artistOptions.value = data.results || []
  filteredArtistOptions.value = artistOptions.value.map((a) => ({ label: a.name, value: a.id }))
  await loadAlbum()
}

watch(() => route.params.id, async (newId) => {
  if (newId) {
    await loadAlbum()
  } else {
    form.title = ''
    form.artist = null
    form.release_year = null
    filteredArtistOptions.value = artistOptions.value.map((a) => ({ label: a.name, value: a.id }))
  }
})

onMounted(loadPage)
</script>
