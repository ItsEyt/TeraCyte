<template>
	<Teleport to="body">
		<Transition name="panel">
			<div v-if="open" class="overlay" @click.self="$emit('close')">
				<aside class="panel">
					<div class="panel-header">
						<div>
							<h2>History</h2>
							<p v-if="stats" class="stats-summary">
								{{ stats.total_snapshots }} snapshots &nbsp;·&nbsp; avg intensity {{ stats.avg_intensity }} &nbsp;·&nbsp; avg focus
								{{ stats.avg_focus }}
							</p>
						</div>
						<button class="close-btn" @click="$emit('close')" aria-label="Close">✕</button>
					</div>

					<div v-if="stats?.label_counts" class="label-counts">
						<span v-for="(count, label) in stats.label_counts" :key="label" class="label-chip" :class="labelClass(String(label))">
							{{ label }}: {{ count }}
						</span>
					</div>

					<ul v-if="history.length" class="history-list">
						<li
							v-for="item in history"
							:key="item.image_id"
							class="history-item"
							:class="{ active: item.image_id === activeImageId }"
							@click="$emit('select', item)">
							<div class="item-thumb" v-if="item.image_data_base64">
								<img :src="'data:image/png;base64,' + item.image_data_base64" alt="" />
							</div>
							<div class="item-info">
								<div class="item-id">{{ item.image_id }}</div>
								<div class="item-ts">{{ formatTs(item.timestamp) }}</div>
								<div class="item-meta">
									<span :class="labelClass(item.classification_label ?? '')">{{ item.classification_label ?? "-" }}</span>
									<span>focus {{ item.focus_score?.toFixed(2) ?? "-" }}</span>
								</div>
							</div>
						</li>
					</ul>

					<div v-else class="empty">No history yet</div>
				</aside>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup lang="ts">
import type { HistoryItem, Stats } from "../composables/useDashboard";

defineProps<{
	open: boolean;
	history: HistoryItem[];
	stats: Stats | null;
	activeImageId: string;
}>();

defineEmits<{
	close: [];
	select: [item: HistoryItem];
}>();

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
.overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.35);
	z-index: 100;
	display: flex;
	justify-content: flex-end;
}

.panel {
	width: 380px;
	max-width: 90vw;
	background: var(--bg);
	height: 100%;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	border-left: 1px solid var(--border);
	box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
}

.panel-header {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	padding: 20px 20px 12px;
	border-bottom: 1px solid var(--border);
	position: sticky;
	top: 0;
	background: var(--bg);
	z-index: 1;
}

.panel-header h2 {
	margin: 0 0 4px;
	font-size: 18px;
	color: var(--text-h);
}

.stats-summary {
	font-size: 12px;
	color: var(--text);
}

.close-btn {
	background: none;
	border: none;
	font-size: 18px;
	cursor: pointer;
	color: var(--text);
	padding: 4px 8px;
	border-radius: 4px;
	line-height: 1;
}

.close-btn:hover {
	background: var(--accent-bg);
	color: var(--accent);
}

.label-counts {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
	padding: 12px 20px;
	border-bottom: 1px solid var(--border);
}

.label-chip {
	font-size: 12px;
	padding: 3px 8px;
	border-radius: 20px;
	font-weight: 600;
}

.history-list {
	list-style: none;
	padding: 0;
	margin: 0;
	flex: 1;
}

.history-item {
	display: flex;
	gap: 12px;
	padding: 12px 20px;
	border-bottom: 1px solid var(--border);
	cursor: pointer;
	transition: background-color 0.15s;
}

.history-item:hover {
	background: var(--accent-bg);
}
.history-item.active {
	background: var(--accent-bg);
	border-left: 3px solid var(--accent);
}

.item-thumb {
	width: 56px;
	height: 56px;
	flex-shrink: 0;
	border-radius: 6px;
	overflow: hidden;
	background: var(--code-bg);
}

.item-thumb img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.item-info {
	flex: 1;
	min-width: 0;
}

.item-id {
	font-size: 12px;
	font-family: var(--mono);
	color: var(--text-h);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.item-ts {
	font-size: 11px;
	color: var(--text);
	margin: 2px 0 6px;
}

.item-meta {
	display: flex;
	gap: 8px;
	font-size: 12px;
	color: var(--text);
	align-items: center;
}

.empty {
	padding: 40px 20px;
	text-align: center;
	color: var(--text);
	font-size: 14px;
}

/* label colours */
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
	background: var(--code-bg);
}

/* panel slide transition */
.panel-enter-active,
.panel-leave-active {
	transition:
		transform 0.25s ease,
		opacity 0.25s ease;
}
.panel-enter-from,
.panel-leave-to {
	transform: translateX(100%);
	opacity: 0;
}
</style>
