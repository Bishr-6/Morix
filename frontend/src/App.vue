<template>
  <SpeedInsights />
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { SpeedInsights } from '@vercel/speed-insights/vue'
</script>
