<template>
  <q-page class="flex flex-center text-center">
    <div>
      <q-icon name="sentiment_dissatisfied" size="64px" color="grey-5" class="mb-4" />
      <h1 class="text-3xl font-bold text-grey-8">404</h1>
      <p class="text-grey-6 mb-6">The page you're looking for doesn't exist.</p>
      <q-btn color="primary" label="Go Home" no-caps unelevated :to="{ name: 'dashboard' }" />
    </div>
  </q-page>
</template>

<script setup>
</script>
