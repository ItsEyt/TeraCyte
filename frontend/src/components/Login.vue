<template>
	<div class="login-wrap">
		<div class="login-card">
			<h1>TeraCyte</h1>
			<p class="login-subtitle">Live Image Dashboard</p>

			<form @submit.prevent="handleLogin">
				<div class="field">
					<label for="username">Username</label>
					<input id="username" v-model="username" type="text" autocomplete="username" required :disabled="loading" />
				</div>

				<div class="field">
					<label for="password">Password</label>
					<input id="password" v-model="password" type="password" autocomplete="current-password" required :disabled="loading" />
				</div>

				<button type="submit" :disabled="loading">
					<span v-if="loading" class="spinner-sm" />
					{{ loading ? "Signing in…" : "Sign in" }}
				</button>
			</form>

			<p v-if="error" class="error-msg">{{ error }}</p>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useAuth } from "../composables/useAuth";

const { login } = useAuth();

const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

async function handleLogin() {
	error.value = "";
	loading.value = true;
	try {
		await login(username.value, password.value);
	} catch (e: any) {
		if (e.response?.data?.detail) {
			error.value = JSON.parse(e.response.data.detail).detail ?? "Login failed";
		} else {
			error.value = e.response?.data?.error ?? "Login failed";
		}
	} finally {
		loading.value = false;
	}
}
</script>

<style scoped>
.login-wrap {
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 100vh;
	background: var(--bg);
}

.login-card {
	width: 360px;
	padding: 40px 36px;
	border: 1px solid var(--border);
	border-radius: 12px;
	text-align: center;
	box-shadow: var(--shadow);
	background: var(--bg);
}

.login-logo {
	font-size: 40px;
	margin-bottom: 8px;
}

h1 {
	font-size: 24px;
	margin: 0 0 4px;
	color: var(--text-h);
}

.login-subtitle {
	font-size: 14px;
	color: var(--text);
	margin: 0 0 28px;
}

.field {
	display: flex;
	flex-direction: column;
	text-align: left;
	margin-bottom: 16px;
}

label {
	font-size: 13px;
	font-weight: 600;
	color: var(--text);
	margin-bottom: 6px;
}

input {
	padding: 10px 12px;
	border: 1px solid var(--border);
	border-radius: 6px;
	font-size: 14px;
	background: var(--bg);
	color: var(--text-h);
	transition: border-color 0.15s;
	outline: none;
}

input:focus {
	border-color: var(--accent);
}
input:disabled {
	opacity: 0.6;
}

button[type="submit"] {
	width: 100%;
	padding: 11px;
	border: none;
	border-radius: 6px;
	background: var(--accent);
	color: #fff;
	font-size: 14px;
	font-weight: 600;
	cursor: pointer;
	margin-top: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	transition: opacity 0.15s;
}

button[type="submit"]:disabled {
	opacity: 0.7;
	cursor: not-allowed;
}
button[type="submit"]:not(:disabled):hover {
	opacity: 0.9;
}

.error-msg {
	margin-top: 16px;
	font-size: 13px;
	color: #dc2626;
}

.spinner-sm {
	width: 14px;
	height: 14px;
	border: 2px solid rgba(255, 255, 255, 0.4);
	border-top-color: #fff;
	border-radius: 50%;
	animation: spin 0.7s linear infinite;
	flex-shrink: 0;
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}
</style>
