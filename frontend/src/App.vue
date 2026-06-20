<script setup lang="ts">
import { useAuth } from "./composables/useAuth";
import Login from "./components/Login.vue";
import Dashboard from "./components/Dashboard.vue";

const { isLoggedIn, isRestoring } = useAuth();
</script>

<template>
	<div v-if="isRestoring" class="restoring" />
	<Login v-else-if="!isLoggedIn" />
	<Dashboard v-else />
</template>

<style scoped>
.restoring {
	height: 100vh;
	background: var(--bg);
}
</style>
