<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    widthMm?: number
    heightMm?: number
    verticalBars?: number
    horizontalBars?: number
    category?: 'WINDOW' | 'DOOR'
  }>(),
  {
    widthMm: 1200,
    heightMm: 1500,
    verticalBars: 1,
    horizontalBars: 1,
    category: 'WINDOW',
  }
)

// Dynamically scale SVG coordinate canvas width based on real-world millimeter proportions
const svgWidth = computed(() => {
  const w = props.widthMm || 1200
  const h = props.heightMm || 1500
  // Keep base width around 400, but scale relative to height to match real dimensions
  return Math.max(200, Math.min(800, (w / h) * 400))
})

const svgHeight = 400
const padding = 24

// Calculate inner frame dimensions
const innerWidth = computed(() => svgWidth.value - padding * 2)
const innerHeight = computed(() => svgHeight - padding * 2)

// Calculate vertical bars coordinates inside the frame
const verticalLines = computed<number[]>(() => {
  const lines: number[] = []
  const count = props.verticalBars || 0
  if (count <= 0) return lines
  const step = innerWidth.value / (count + 1)
  for (let i = 1; i <= count; i++) {
    lines.push(padding + i * step)
  }
  return lines
})

// Calculate horizontal bars coordinates inside the frame
const horizontalLines = computed<number[]>(() => {
  const lines: number[] = []
  const count = props.horizontalBars || 0
  if (count <= 0) return lines
  const step = innerHeight.value / (count + 1)
  for (let i = 1; i <= count; i++) {
    lines.push(padding + i * step)
  }
  return lines
})
</script>

<template>
  <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 flex flex-col items-center justify-center shadow-sm">
    <div class="flex items-center justify-between w-full mb-4">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
        Live Blueprint Preview
      </span>
      <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
        {{ category }}
      </span>
    </div>

    <!-- SVG Container Box -->
    <div class="relative w-full max-w-[320px] aspect-[4/3] flex items-center justify-center bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-700 p-2 overflow-hidden">
      <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`" class="w-full h-full max-h-[220px] drop-shadow-sm transition-all duration-200">
        <!-- Outer Frame Structure -->
        <rect
          x="16"
          y="16"
          :width="svgWidth - 32"
          :height="svgHeight - 32"
          rx="6"
          class="fill-white dark:fill-slate-800 stroke-slate-800 dark:stroke-sky-400"
          stroke-width="8"
        />

        <!-- Glass Pane Tint Effect -->
        <rect
          :x="padding"
          :y="padding"
          :width="innerWidth"
          :height="innerHeight"
          rx="4"
          class="fill-sky-50/50 dark:fill-sky-950/20"
        />

        <!-- Vertical Bars -->
        <line
          v-for="x in verticalLines"
          :key="'v-' + x"
          :x1="x"
          :y1="padding"
          :x2="x"
          :y2="svgHeight - padding"
          class="stroke-slate-400 dark:stroke-slate-600"
          stroke-width="4"
          stroke-linecap="round"
        />

        <!-- Horizontal Bars -->
        <line
          v-for="y in horizontalLines"
          :key="'h-' + y"
          :x1="padding"
          :y1="y"
          :x2="svgWidth - padding"
          :y2="y"
          class="stroke-slate-400 dark:stroke-slate-600"
          stroke-width="4"
          stroke-linecap="round"
        />
      </svg>
    </div>

    <!-- Dimension Badge -->
    <div class="mt-4 flex items-center space-x-2 text-xs font-medium text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-700/60 px-3 py-1.5 rounded-lg">
      <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
      </svg>
      <span>{{ widthMm }} mm (W) × {{ heightMm }} mm (H)</span>
    </div>
  </div>
</template>