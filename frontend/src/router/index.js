import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('../views/DashboardView.vue'),
      },
      {
        path: 'artists',
        name: 'artist-list',
        component: () => import('../views/ArtistListView.vue'),
      },
      {
        path: 'artists/new',
        name: 'artist-new',
        component: () => import('../views/ArtistFormView.vue'),
      },
      {
        path: 'artists/:id(\\d+)',
        name: 'artist-detail',
        component: () => import('../views/ArtistDetailView.vue'),
      },
      {
        path: 'artists/:id(\\d+)/edit',
        name: 'artist-edit',
        component: () => import('../views/ArtistFormView.vue'),
      },
      {
        path: 'albums',
        name: 'album-list',
        component: () => import('../views/AlbumListView.vue'),
      },
      {
        path: 'albums/new',
        name: 'album-new',
        component: () => import('../views/AlbumFormView.vue'),
      },
      {
        path: 'albums/:id(\\d+)',
        name: 'album-detail',
        component: () => import('../views/AlbumDetailView.vue'),
      },
      {
        path: 'albums/:id(\\d+)/edit',
        name: 'album-edit',
        component: () => import('../views/AlbumFormView.vue'),
      },
      {
        path: 'songs',
        name: 'song-list',
        component: () => import('../views/SongListView.vue'),
      },
      {
        path: 'songs/new',
        name: 'song-new',
        component: () => import('../views/SongFormView.vue'),
      },
      {
        path: 'songs/:id(\\d+)',
        name: 'song-detail',
        component: () => import('../views/SongDetailView.vue'),
      },
      {
        path: 'songs/:id(\\d+)/edit',
        name: 'song-edit',
        component: () => import('../views/SongFormView.vue'),
      },
      {
        path: ':pathMatch(.*)*',
        name: 'not-found',
        component: () => import('../views/NotFoundView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
