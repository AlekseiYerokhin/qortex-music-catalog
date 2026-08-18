<template>
  <q-page class="p-6 max-w-2xl mx-auto">
    <q-card
      flat
      bordered
      class="rounded-lg"
    >
      <q-card-section>
        <div class="text-h6 text-grey-9">
          {{ isEdit ? 'Edit Song' : 'New Song' }}
        </div>
      </q-card-section>

      <q-inner-loading :showing="songStore.loading && isEdit">
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
          label="Song Title *"
          outlined
          dense
          :rules="[val => !!val || 'Title is required']"
          lazy-rules
        />

        <div class="flex justify-end gap-3 mt-4">
          <q-btn
            flat
            label="Cancel"
            no-caps
            @click="$router.push({ name: 'song-list' })"
          />
          <q-btn
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            type="submit"
            unelevated
            no-caps
            :loading="songStore.loading"
          />
        </div>
      </q-form>
    </q-card>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuasar } from 'quasar'
import { useSongStore } from '../stores/song'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const songStore = useSongStore()

const isEdit = computed(() => !!route.params.id)

const form = reactive({ title: '' })

async function loadSong() {
  if (!isEdit.value) return
  const data = await songStore.fetchDetail(route.params.id)
  form.title = data.title
}

async function onSave() {
  try {
    let saved
    if (isEdit.value) {
      saved = await songStore.update(route.params.id, { title: form.title })
      $q.notify({ type: 'positive', message: 'Song updated' })
    } else {
      saved = await songStore.create({ title: form.title })
      $q.notify({ type: 'positive', message: 'Song created' })
    }
    router.push({ name: 'song-detail', params: { id: saved.id } })
  } catch {
    /* handled by interceptor */
  }
}

watch(() => route.params.id, async (newId) => {
  if (newId) {
    await loadSong()
  } else {
    form.title = ''
  }
})

onMounted(loadSong)
</script>
