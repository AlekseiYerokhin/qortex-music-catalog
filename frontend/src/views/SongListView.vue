<template>
  <q-page class="p-6 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-grey-9">Songs</h1>
      <q-btn color="primary" icon="add" label="New Song" :to="{ name: 'song-new' }" no-caps />
    </div>

    <q-input
      v-model="search"
      dense
      outlined
      placeholder="Search songs..."
      class="mb-4 q-mb-md"
      clearable
      @update:model-value="onSearch"
    >
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>

    <q-table
      :rows="songStore.songs"
      :columns="columns"
      row-key="id"
      :loading="songStore.loading"
      v-model:pagination="pagination"
      :rows-per-page-options="[5, 10, 20, 50]"
      @request="onRequest"
      flat
      bordered
    >
      <template #body-cell-albums="props">
        <q-td :props="props">
          <q-badge v-if="props.row.albums?.length" color="secondary" :label="props.row.albums.length" />
          <span v-else class="text-grey-5">—</span>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props" class="text-right">
          <q-btn flat dense round icon="visibility" :to="{ name: 'song-detail', params: { id: props.row.id } }">
            <q-tooltip>View</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="edit" :to="{ name: 'song-edit', params: { id: props.row.id } }">
            <q-tooltip>Edit</q-tooltip>
          </q-btn>
          <q-btn flat dense round icon="delete" color="negative" @click="confirmDelete(props.row)">
            <q-tooltip>Delete</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { useSongStore } from '../stores/song'

const $q = useQuasar()
const songStore = useSongStore()

const search = ref('')
const pagination = ref({
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0,
  sortBy: 'title',
  descending: false,
})

const columns = [
  { name: 'title', label: 'Title', field: 'title', align: 'left', sortable: true },
  { name: 'albums', label: 'Albums', field: 'albums', align: 'left', sortable: false },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right', sortable: false },
]

async function fetchTable() {
  const params = {
    page: pagination.value.page,
    page_size: pagination.value.rowsPerPage,
  }
  if (search.value) params.search = search.value
  if (pagination.value.sortBy) {
    params.ordering = pagination.value.descending
      ? `-${pagination.value.sortBy}`
      : pagination.value.sortBy
  }
  const data = await songStore.fetchSongs(params)
  pagination.value.rowsNumber = data.count
}

function onRequest(props) {
  pagination.value.page = props.pagination.page
  pagination.value.rowsPerPage = props.pagination.rowsPerPage
  pagination.value.sortBy = props.pagination.sortBy
  pagination.value.descending = props.pagination.descending
  fetchTable()
}

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.value.page = 1
    fetchTable()
  }, 300)
}

function confirmDelete(song) {
  $q.dialog({
    title: 'Delete Song',
    message: `Are you sure you want to delete "${song.title}"? This removes it from all albums.`,
    cancel: true,
    persistent: true,
    ok: { label: 'Delete', color: 'negative', unelevated: true },
  }).onOk(async () => {
    try {
      await songStore.deleteSong(song.id)
      $q.notify({ type: 'positive', message: 'Song deleted' })
      const remaining = pagination.value.rowsNumber - 1
      const maxPage = Math.max(1, Math.ceil(remaining / pagination.value.rowsPerPage))
      if (pagination.value.page > maxPage) {
        pagination.value.page = maxPage
      }
      fetchTable()
    } catch {
      /* handled by interceptor */
    }
  })
}

onMounted(fetchTable)
</script>
