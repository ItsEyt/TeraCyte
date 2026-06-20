import { ref } from "vue";
import api from "../api/client";

const STORAGE_KEY = "tc_authed";

const isLoggedIn = ref(false);
const isRestoring = ref(true); // true while we're checking the stored session

window.addEventListener("auth:expired", () => {
	isLoggedIn.value = false;
	localStorage.removeItem(STORAGE_KEY);
});

// On page load, if we have a stored flag, verify the session is still valid
async function restoreSession() {
	if (!localStorage.getItem(STORAGE_KEY)) {
		isRestoring.value = false;
		return;
	}
	try {
		await api.get("/api/auth/me");
		isLoggedIn.value = true;
	} catch {
		localStorage.removeItem(STORAGE_KEY);
	} finally {
		isRestoring.value = false;
	}
}

restoreSession();

export function useAuth() {
	async function login(username: string, password: string): Promise<void> {
		await api.post("/api/auth/login", { username, password });
		localStorage.setItem(STORAGE_KEY, "1");
		isLoggedIn.value = true;
	}

	async function logout(): Promise<void> {
		try {
			await api.post("/api/auth/logout");
		} catch {
			/* ignore */
		}
		localStorage.removeItem(STORAGE_KEY);
		isLoggedIn.value = false;
	}

	return { isLoggedIn, isRestoring, login, logout };
}
