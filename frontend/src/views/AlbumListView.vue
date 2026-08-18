<template>
  <q-page class="p-6 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-grey-9">
        Albums
      </h1>
      <q-btn
        color="primary"
        icon="add"
        label="New Album"
        :to="{ name: 'album-new' }"
        no-caps
      />
    </div>

    <q-input
      v-model="search"
      dense
      outlined
      placeholder="Search albums by title or artist..."
      class="mb-4"
      clearable
      @update:model-value="onSearch"
    >
      <template #prepend>
        <q-icon name="search" />
      </template>
    </q-input>

    <q-table
      v-model:pagination="pagination"
      :rows="albumStore.items"
      :columns="columns"
      row-key="id"
      :loading="albumStore.loading"
      :rows-per-page-options="[5, 10, 20, 50]"
      flat
      bordered
      @request="onRequest"
    >
      <template #body-cell-actions="props">
        <q-td
          :props="props"
          class="text-right"
        >
          <q-btn
            flat
            dense
            round
            icon="visibility"
            aria-label="View album"
            :to="{ name: 'album-detail', params: { id: props.row.id } }"
          >
            <q-tooltip>View</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="edit"
            aria-label="Edit album"
            :to="{ name: 'album-edit', params: { id: props.row.id } }"
          >
            <q-tooltip>Edit</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="delete"
            color="negative"
            aria-label="Delete album"
            @click="confirmDelete(props.row)"
          >
            <q-tooltip>Delete</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { useAlbumStore } from '../stores/album'
import { useResourceTable } from '../composables/useResourceTable'

const albumStore = useAlbumStore()

const columns = [
  { name: 'title', label: 'Title', field: 'title', align: 'left', sortable: true },
  { name: 'artist_name', label: 'Artist', field: 'artist_name', align: 'left', sortable: false },
  { name: 'release_year', label: 'Release Year', field: 'release_year', align: 'left', sortable: true },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right', sortable: false },
]

const { search, pagination, onRequest, onSearch, confirmDelete } = useResourceTable(albumStore, {
  defaultSort: 'title',
  entityName: 'Album',
  deleteMessage: (album) => `Are you sure you want to delete "${album.title}"?`,
})
</script>
