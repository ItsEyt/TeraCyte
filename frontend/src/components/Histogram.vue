<template>
	<div class="histogram-wrap">
		<canvas ref="canvasEl" />
	</div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from "vue";
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip } from "chart.js";

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

const props = defineProps<{ data: number[] }>();

const canvasEl = ref<HTMLCanvasElement | null>(null);
let chart: Chart<"bar"> | null = null;

const LABELS = Array.from({ length: 256 }, (_, i) => i);
const DURATION = 400;

function buildChart() {
	if (!canvasEl.value) return;

	chart = new Chart(canvasEl.value, {
		type: "bar",
		data: {
			labels: LABELS,
			datasets: [
				{
					data: props.data.length ? props.data : new Array(256).fill(0),
					backgroundColor: "rgba(192,132,252,0.25)",
					hoverBackgroundColor: "#c084fc",
					borderColor: "transparent",
					borderWidth: 0,
					borderRadius: 1,
					categoryPercentage: 1.0,
					barPercentage: 1.0,
				},
			],
		},
		options: {
			animation: { duration: DURATION, easing: "easeOutQuart" },
			responsive: true,
			maintainAspectRatio: false,
			interaction: {
				mode: "index",
				intersect: false, // false allows triggering without touching the bar
			},
			plugins: {
				legend: { display: false },
				tooltip: {
					callbacks: {
						title: (items) => `Bin ${items[0].label}`,
						label: (item) => ` ${Number(item.raw).toLocaleString()} px`,
					},
					displayColors: false,
					backgroundColor: "rgba(30,30,40,0.92)",
					titleColor: "#c084fc",
					bodyColor: "#f3f4f6",
					borderColor: "rgba(192,132,252,0.4)",
					borderWidth: 1,
					padding: 8,
					titleFont: { size: 14, weight: "bold" },
					bodyFont: { size: 14 },
				},
			},
			scales: {
				x: { display: true, grid: { display: false }, ticks: { maxTicksLimit: 5 } },
				y: { display: false },
			},
		},
	});
}

onMounted(buildChart);

onUnmounted(() => {
	chart?.destroy();
	chart = null;
});

watch(
	() => props.data,
	(newData) => {
		if (!chart || !newData.length) return;
		chart.data.datasets[0].data = newData;
		chart.data.datasets[0].backgroundColor = "rgba(192,132,252,0.25)";
		chart.data.datasets[0].hoverBackgroundColor = "#c084fc";
		chart.update();
	},
	{ deep: true },
);
</script>

<style scoped>
.histogram-wrap {
	width: 100%;
}

.histogram-wrap canvas {
	width: 100% !important;
	height: 120px !important;
	display: block;
	border-radius: 6px;
	overflow: hidden;
}

.histogram-axis {
	display: flex;
	justify-content: space-between;
	font-size: 12px;
	color: var(--text);
	margin-top: 4px;
	padding: 0 2px;
}
</style>
