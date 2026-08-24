<script setup>
import Plaza from './components/Plaza.vue'

// The app IS the plaza (spec §2) — one place, four directions.
// The legacy onboarding → theater → composed-page flow now lives inside the
// north wing (AI Corner); dev mock mode survives via ?fixture=.
</script>

<template>
  <Plaza />
</template>
