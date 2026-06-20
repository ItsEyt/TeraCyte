import { ref, onUnmounted } from "vue";
import api from "../api/client";

export interface CurrentImage {
	image_id: string;
	timestamp: string;
	image_data_base64: string;
	processed_data_base64: string | null;
}

export interface CurrentResults {
	image_id: string;
	intensity_average: number;
	focus_score: number;
	classification_label: string;
	histogram: number[];
}

export interface HistoryItem {
	image_id: string;
	timestamp: string;
	intensity_average: number | null;
	focus_score: number | null;
	classification_label: string | null;
	histogram: number[];
	image_data_base64: string | null;
	processed_data_base64: string | null;
}

export interface Stats {
	total_snapshots: number;
	avg_intensity: number;
	avg_focus: number;
	label_counts: Record<string, number>;
}

export function useDashboard() {
	const currentImage = ref<CurrentImage | null>(null);
	const currentResults = ref<CurrentResults | null>(null);
	// const processedBase64 = ref<string | null>(null);
	const history = ref<HistoryItem[]>([]);
	const stats = ref<Stats | null>(null);
	const lastUpdated = ref<Date | null>(null);
	const error = ref<string | null>(null);
	const isLive = ref(true);

	let lastImageId = "";
	let pollInterval: ReturnType<typeof setInterval> | null = null;

	async function poll() {
        if (!isLive.value) return;
		try {
			const res = await api.get("/api/poll");
			if (res.status === 204) return; // image_id unchanged

			const { image, results } = res.data as { image: CurrentImage; results: CurrentResults };
			currentImage.value = image;
			currentResults.value = results;
			lastUpdated.value = new Date();
			error.value = null;

			if (image.image_id !== lastImageId) {
				lastImageId = image.image_id;
				await loadHistory();
			}
		} catch (e: any) {
			if (e.response?.status !== 401) {
				error.value = "Connection error. Retrying...";
			}
		}
	}

	async function loadHistory() {
		try {
				const res = await api.get("/api/history?limit=50");
				history.value = res.data as HistoryItem[];
		} catch {
			/* non-fatal */
		}
		await loadStats();
	}

	async function loadStats() {
		try {
			const res = await api.get("/api/stats");
			stats.value = res.data as Stats;
		} catch {
			/* non-fatal */
		}
	}

	function viewHistoryItem(item: HistoryItem) {
		currentImage.value = {
			image_id: item.image_id,
			timestamp: item.timestamp,
			image_data_base64: item.image_data_base64 ?? "",
            processed_data_base64: item.processed_data_base64 ?? null,
		};
		currentResults.value = {
			image_id: item.image_id,
			intensity_average: item.intensity_average ?? 0,
			focus_score: item.focus_score ?? 0,
			classification_label: item.classification_label ?? "—",
			histogram: item.histogram,
		};
		// processedBase64.value = item.processed_data_base64;
		isLive.value = false;
	}

	function resumeLive() {
		isLive.value = true;
		lastImageId = "";
		poll();
	}

	function startPolling() {
		poll();
		pollInterval = setInterval(poll, 5000);
	}

	function stopPolling() {
		if (pollInterval) clearInterval(pollInterval);
	}

	onUnmounted(stopPolling);

	return {
		currentImage,
		currentResults,
		// processedBase64,
		history,
		stats,
		lastUpdated,
		error,
		isLive,
		startPolling,
		stopPolling,
		loadHistory,
		viewHistoryItem,
		resumeLive,
	};
}
