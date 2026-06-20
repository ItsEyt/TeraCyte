<template>
	<div class="dashboard">
		<!-- Navbar -->
		<header class="navbar">
			<div class="navbar-left">
				<span class="logo">TeraCyte</span>
				<span v-if="lastUpdated" class="last-updated">
					{{ formatTime(lastUpdated) }}
				</span>
				<span v-if="error" class="error-msg">{{ error }}</span>
			</div>
			<div class="navbar-right">
				<button v-if="!isLive" class="btn btn-outline" @click="resumeLive">↩ Resume Live</button>
				<button class="btn btn-outline" @click="historyOpen = true">History</button>
				<button class="btn btn-danger" @click="logout">Logout</button>
			</div>
		</header>

		<!-- Main content -->
		<main class="main-grid">
			<!-- Image -->
			<section class="image-section">
				<div class="section-title">
					<span>Microscope Image</span>
					<div v-if="currentImage?.processed_data_base64" class="toggle-group">
						<button class="toggle-btn" :class="{ active: !showProcessed }" @click="showProcessed = false">Original</button>
						<button class="toggle-btn" :class="{ active: showProcessed }" @click="showProcessed = true">Processed</button>
					</div>
				</div>

				<div class="image-frame">
					<template v-if="currentImage">
						<img
							v-if="showProcessed && currentImage.processed_data_base64"
							:src="'data:image/png;base64,' + currentImage.processed_data_base64"
							alt="Processed microscope image"
							class="microscope-img" />
						<img v-else :src="'data:image/png;base64,' + currentImage.image_data_base64" alt="Microscope image" class="microscope-img" />
					</template>
					<div v-else class="image-placeholder">
						<div class="spinner"></div>
						<p>Waiting for image…</p>
					</div>
				</div>

				<div v-if="currentImage" class="image-meta">
					<code>{{ currentImage.image_id }}</code>
					<span>{{ formatTs(currentImage.timestamp) }}</span>
				</div>
			</section>

			<!-- Metrics -->
			<section class="metrics-section">
				<div class="section-title">Metrics</div>

				<template v-if="currentResults">
					<div class="metric-card">
						<div class="metric-label">Intensity Average</div>
						<div class="metric-value">{{ currentResults.intensity_average.toFixed(2) }}</div>
						<div class="metric-bar">
							<div class="metric-fill" :style="{ width: (currentResults.intensity_average / 255) * 100 + '%' }"></div>
						</div>
					</div>

					<div class="metric-card">
						<div class="metric-label">Focus Score</div>
						<div class="metric-value">{{ currentResults.focus_score.toFixed(3) }}</div>
						<div class="metric-bar">
							<div class="metric-fill focus" :style="{ width: currentResults.focus_score * 100 + '%' }"></div>
						</div>
					</div>

					<div class="metric-card classification">
						<div class="metric-label">Classification</div>
						<div class="classification-badge" :class="labelClass(currentResults.classification_label)">
							{{ currentResults.classification_label }}
						</div>
					</div>
				</template>

				<div v-else class="metrics-placeholder">
					<div class="spinner"></div>
					<p>Waiting for results…</p>
				</div>
			</section>
		</main>

		<!-- Histogram -->
		<section class="histogram-section" v-if="currentResults?.histogram?.length">
			<div class="section-title">Pixel Intensity Histogram (256 bins)</div>
			<Histogram :data="currentResults.histogram" />
		</section>

		<!-- History Panel -->
		<HistoryPanel
			:open="historyOpen"
			:history="history"
			:stats="stats"
			:activeImageId="currentImage?.image_id ?? ''"
			@close="historyOpen = false"
			@select="onSelectHistory" />
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Histogram from "./Histogram.vue";
import HistoryPanel from "./HistoryPanel.vue";
import { useDashboard, type HistoryItem } from "../composables/useDashboard";
import { useAuth } from "../composables/useAuth";

const { logout } = useAuth();

const { currentImage, currentResults, history, stats, lastUpdated, error, isLive, startPolling, loadHistory, viewHistoryItem, resumeLive } =
	useDashboard();

const showProcessed = ref(false);
const historyOpen = ref(false);

onMounted(() => {
	startPolling();
	loadHistory();
});

function onSelectHistory(item: HistoryItem) {
	viewHistoryItem(item);
	historyOpen.value = false;
	showProcessed.value = false;
}

function formatTime(d: Date) {
	return d.toLocaleTimeString();
}

function formatTs(ts: string) {
	try {
		return new Date(ts).toLocaleString();
	} catch {
		return ts;
	}
}

function labelClass(label: string) {
	const l = label.toLowerCase();
	if (l.includes("healthy")) return "label-healthy";
	if (l.includes("anomaly")) return "label-anomaly";
	return "label-unknown";
}
</script>

<style scoped>
.dashboard {
	display: flex;
	flex-direction: column;
	height: 100vh;
	overflow: hidden;
}

/* Navbar */
.navbar {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 0 24px;
	height: 56px;
	border-bottom: 1px solid var(--border);
	flex-shrink: 0;
	gap: 16px;
}

.navbar-left,
.navbar-right {
	display: flex;
	align-items: center;
	gap: 12px;
}

.logo {
	font-size: 18px;
	font-weight: 600;
	color: var(--text-h);
	letter-spacing: -0.3px;
}

.last-updated {
	font-size: 12px;
	color: var(--text);
}

.error-msg {
	font-size: 12px;
	color: #dc2626;
}

/* Buttons */
.btn {
	padding: 6px 14px;
	border-radius: 6px;
	font-size: 13px;
	font-weight: 500;
	cursor: pointer;
	border: 1px solid transparent;
	transition:
		background 0.15s,
		border-color 0.15s;
}

.btn-outline {
	background: transparent;
	border-color: var(--border);
	color: var(--text-h);
}

.btn-outline:hover {
	background: var(--accent-bg);
	border-color: var(--accent);
	color: var(--accent);
}

.btn-danger {
	background: transparent;
	border-color: #fca5a5;
	color: #dc2626;
}

.btn-danger:hover {
	background: #fee2e2;
}

/* Main grid */
.main-grid {
	display: grid;
	grid-template-columns: 1fr 280px;
	gap: 0;
	flex: 1;
	overflow: hidden;
	border-bottom: 1px solid var(--border);
}

/* Image section */
.image-section {
	display: flex;
	flex-direction: column;
	padding: 20px;
	border-right: 1px solid var(--border);
	overflow: hidden;
}

.section-title {
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-size: 13px;
	font-weight: 600;
	color: var(--text);
	text-transform: uppercase;
	letter-spacing: 0.5px;
	margin-bottom: 12px;
}

.toggle-group {
	display: flex;
	border: 1px solid var(--border);
	border-radius: 6px;
	overflow: hidden;
}

.toggle-btn {
	padding: 4px 12px;
	font-size: 12px;
	font-weight: 500;
	border: none;
	background: transparent;
	cursor: pointer;
	color: var(--text);
	transition:
		background 0.15s,
		color 0.15s;
}

.toggle-btn.active {
	background: var(--accent);
	color: #fff;
}

.image-frame {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	background: var(--code-bg);
	border-radius: 8px;
	overflow: hidden;
	min-height: 0;
}

.microscope-img {
	max-width: 100%;
	max-height: 100%;
	object-fit: contain;
	display: block;
}

.image-placeholder,
.metrics-placeholder {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 12px;
	color: var(--text);
	font-size: 14px;
}

.image-placeholder p,
.metrics-placeholder p {
	margin: 0;
}

.image-meta {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-top: 10px;
	font-size: 12px;
	color: var(--text);
}

/* Metrics */
.metrics-section {
	display: flex;
	flex-direction: column;
	padding: 20px;
	gap: 16px;
	overflow-y: auto;
}

.metric-card {
	background: var(--code-bg);
	border-radius: 8px;
	padding: 14px 16px;
}

.metric-label {
	font-size: 11px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.5px;
	color: var(--text);
	margin-bottom: 6px;
}

.metric-value {
	font-size: 28px;
	font-weight: 600;
	color: var(--text-h);
	font-family: var(--mono);
	line-height: 1;
	margin-bottom: 10px;
}

.metric-bar {
	height: 4px;
	background: var(--border);
	border-radius: 2px;
	overflow: hidden;
}

.metric-fill {
	height: 100%;
	background: var(--accent);
	border-radius: 2px;
	transition: width 0.5s ease;
}

.metric-fill.focus {
	background: #0ea5e9;
}

.classification-badge {
	display: inline-block;
	padding: 6px 16px;
	border-radius: 20px;
	font-size: 16px;
	font-weight: 700;
	margin-top: 4px;
}

.label-healthy {
	color: #16a34a;
	background: #dcfce7;
}

.label-anomaly {
	color: #b45309;
	background: #fef3c7;
}

.label-unknown {
	color: var(--text);
	background: var(--border);
}

/* Histogram */
.histogram-section {
	padding: 16px 20px 20px;
	flex-shrink: 0;
}

/* Spinner */
.spinner {
	width: 28px;
	height: 28px;
	border: 3px solid var(--border);
	border-top-color: var(--accent);
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}
</style>
