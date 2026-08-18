<template>
  <q-page class="p-6 max-w-2xl mx-auto">
    <q-card
      flat
      bordered
      class="rounded-lg"
    >
      <q-card-section>
        <div class="text-h6 text-grey-9">
          {{ isEdit ? 'Edit Artist' : 'New Artist' }}
        </div>
      </q-card-section>

      <q-inner-loading :showing="artistStore.loading && isEdit">
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
          v-model="form.name"
          label="Artist Name *"
          outlined
          dense
          :rules="[val => !!val || 'Name is required']"
          lazy-rules
        />

        <div class="flex justify-end gap-3 mt-4">
          <q-btn
            flat
            label="Cancel"
            no-caps
            @click="$router.push({ name: 'artist-list' })"
          />
          <q-btn
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            type="submit"
            unelevated
            no-caps
            :loading="artistStore.loading"
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
import { useArtistStore } from '../stores/artist'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const artistStore = useArtistStore()

const isEdit = computed(() => !!route.params.id)

const form = reactive({ name: '' })

async function loadArtist() {
  if (!isEdit.value) return
  const data = await artistStore.fetchDetail(route.params.id)
  form.name = data.name
}

async function onSave() {
  try {
    let saved
    if (isEdit.value) {
      saved = await artistStore.update(route.params.id, { name: form.name })
      $q.notify({ type: 'positive', message: 'Artist updated' })
    } else {
      saved = await artistStore.create({ name: form.name })
      $q.notify({ type: 'positive', message: 'Artist created' })
    }
    router.push({ name: 'artist-detail', params: { id: saved.id } })
  } catch {
    /* handled by interceptor */
  }
}

watch(() => route.params.id, async (newId) => {
  if (newId) {
    await loadArtist()
  } else {
    form.name = ''
  }
})

onMounted(loadArtist)
</script>
