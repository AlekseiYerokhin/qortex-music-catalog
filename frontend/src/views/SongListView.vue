<template>
  <q-page class="p-6 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-grey-9">
        Songs
      </h1>
      <q-btn
        color="primary"
        icon="add"
        label="New Song"
        :to="{ name: 'song-new' }"
        no-caps
      />
    </div>

    <q-input
      v-model="search"
      dense
      outlined
      placeholder="Search songs..."
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
      :rows="songStore.items"
      :columns="columns"
      row-key="id"
      :loading="songStore.loading"
      :rows-per-page-options="[5, 10, 20, 50]"
      flat
      bordered
      @request="onRequest"
    >
      <template #body-cell-albums="props">
        <q-td :props="props">
          <q-badge
            v-if="props.row.albums?.length"
            color="secondary"
            :label="props.row.albums.length"
          />
          <span
            v-else
            class="text-grey-5"
          >—</span>
        </q-td>
      </template>
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
            aria-label="View song"
            :to="{ name: 'song-detail', params: { id: props.row.id } }"
          >
            <q-tooltip>View</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="edit"
            aria-label="Edit song"
            :to="{ name: 'song-edit', params: { id: props.row.id } }"
          >
            <q-tooltip>Edit</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="delete"
            color="negative"
            aria-label="Delete song"
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
import { useSongStore } from '../stores/song'
import { useResourceTable } from '../composables/useResourceTable'

const songStore = useSongStore()

const columns = [
  { name: 'title', label: 'Title', field: 'title', align: 'left', sortable: true },
  { name: 'albums', label: 'Albums', field: 'albums', align: 'left', sortable: false },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right', sortable: false },
]

const { search, pagination, onRequest, onSearch, confirmDelete } = useResourceTable(songStore, {
  defaultSort: 'title',
  entityName: 'Song',
  deleteMessage: (song) =>
    `Are you sure you want to delete "${song.title}"? This removes it from all albums.`,
})
</script>
