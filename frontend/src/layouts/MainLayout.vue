<template>
  <q-layout view="hHh LpR fFf" class="bg-grey-1">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar class="flex items-center">
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleDrawer" />
        <q-icon name="library_music" size="28px" class="q-mr-sm" />
        <q-toolbar-title class="text-weight-bold">Qortex</q-toolbar-title>
        <span class="text-caption text-white-7 hidden-sm-and-down">Music Catalog Manager</span>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="drawer" show-if-above bordered class="bg-white">
      <q-list padding>
        <q-item-label header class="text-grey-8 text-weight-medium">Navigation</q-item-label>
        <q-item
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          clickable
          v-ripple
          exact
          active-class="text-primary bg-blue-1"
        >
          <q-item-section avatar>
            <q-icon :name="link.icon" />
          </q-item-section>
          <q-item-section>{{ link.label }}</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'

const drawer = ref(true)

const navLinks = [
  { label: 'Dashboard', icon: 'dashboard', to: '/' },
  { label: 'Artists', icon: 'person', to: '/artists' },
  { label: 'Albums', icon: 'album', to: '/albums' },
  { label: 'Songs', icon: 'music_note', to: '/songs' },
]

function toggleDrawer() {
  drawer.value = !drawer.value
}
</script>
