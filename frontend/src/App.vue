<template>
  <RouterView />
  <Analytics />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { Analytics } from '@vercel/analytics/vue'
</script>
