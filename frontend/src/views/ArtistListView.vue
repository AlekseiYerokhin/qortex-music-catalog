<template>
  <q-page class="p-6 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-grey-9">
        Artists
      </h1>
      <q-btn
        color="primary"
        icon="add"
        label="New Artist"
        :to="{ name: 'artist-new' }"
        no-caps
      />
    </div>

    <q-input
      v-model="search"
      dense
      outlined
      placeholder="Search artists..."
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
      :rows="artistStore.items"
      :columns="columns"
      row-key="id"
      :loading="artistStore.loading"
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
            aria-label="View artist"
            :to="{ name: 'artist-detail', params: { id: props.row.id } }"
          >
            <q-tooltip>View</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="edit"
            aria-label="Edit artist"
            :to="{ name: 'artist-edit', params: { id: props.row.id } }"
          >
            <q-tooltip>Edit</q-tooltip>
          </q-btn>
          <q-btn
            flat
            dense
            round
            icon="delete"
            color="negative"
            aria-label="Delete artist"
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
import { useArtistStore } from '../stores/artist'
import { useResourceTable } from '../composables/useResourceTable'

const artistStore = useArtistStore()

const columns = [
  { name: 'name', label: 'Name', field: 'name', align: 'left', sortable: true },
  { name: 'albums_count', label: 'Albums', field: 'albums_count', align: 'left', sortable: false },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right', sortable: false },
]

const { search, pagination, onRequest, onSearch, confirmDelete } = useResourceTable(artistStore, {
  defaultSort: 'name',
  entityName: 'Artist',
  deleteMessage: (artist) =>
    `Are you sure you want to delete "${artist.name}"? This will also delete their albums.`,
})
</script>
