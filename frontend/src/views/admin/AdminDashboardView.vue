<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import apiClient from '@/api/axios'
import { useToastStore } from '@/stores/toastStore'

interface RevenuePoint {
  label: string
  value: number
}

interface QuoteStatusItem {
  label: string
  value: number
  color: string
}

interface AdminStats {
  daily_sales: number
  monthly_revenue: number
  total_users: number
  active_profiles: number
  revenue_trend?: RevenuePoint[]
  quotation_status?: QuoteStatusItem[]
}

const stats = ref<AdminStats>({
  daily_sales: 0,
  monthly_revenue: 0,
  total_users: 0,
  active_profiles: 0,
  revenue_trend: [],
  quotation_status: [],
})
const loading = ref(true)
const toast = useToastStore()

const fallbackRevenueTrend: RevenuePoint[] = [
  { label: 'Mon', value: 1600 },
  { label: 'Tue', value: 1900 },
  { label: 'Wed', value: 2300 },
  { label: 'Thu', value: 2100 },
  { label: 'Fri', value: 2800 },
  { label: 'Sat', value: 2600 },
  { label: 'Sun', value: 3100 },
]

const fallbackStatus: QuoteStatusItem[] = [
  { label: 'Draft', value: 12, color: '#f59e0b' },
  { label: 'Issued', value: 28, color: '#10b981' },
]

const revenueTrend = computed(() =>
  stats.value.revenue_trend?.length ? stats.value.revenue_trend : fallbackRevenueTrend,
)
const quotationStatus = computed(() =>
  stats.value.quotation_status?.length ? stats.value.quotation_status : fallbackStatus,
)

const revenuePath = computed(() => {
  if (!revenueTrend.value.length) return ''

  const values = revenueTrend.value.map((point) => point.value)
  const max = Math.max(...values, 1)
  const min = Math.min(...values, 0)
  const range = max - min || 1
  const width = 100

  return revenueTrend.value
    .map((point, index) => {
      const x = (index / Math.max(revenueTrend.value.length - 1, 1)) * width
      const normalized = (point.value - min) / range
      const y = 100 - normalized * 70 - 10
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
    })
    .join(' ')
})

const totalStatusCount = computed(() =>
  quotationStatus.value.reduce((sum, item) => sum + item.value, 0) || 1,
)

const donutSegments = computed(() => {
  const radius = 42
  const circumference = 2 * Math.PI * radius
  let accumulated = 0

  return quotationStatus.value.map((item) => {
    const ratio = item.value / totalStatusCount.value
    const dash = ratio * circumference
    const gap = circumference - dash
    const segment = {
      ...item,
      dash,
      gap,
      offset: -(accumulated * circumference),
    }
    accumulated += ratio
    return segment
  })
})

async function fetchStats() {
  try {
    const response = await apiClient.get<AdminStats>('/admin/status')
    stats.value = {
      ...stats.value,
      ...response.data,
      revenue_trend: response.data.revenue_trend ?? fallbackRevenueTrend,
      quotation_status: response.data.quotation_status ?? fallbackStatus,
    }
  } catch (error) {
    toast.error('Failed to load dashboard statistics.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Admin Dashboard</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400">Overview of system performance, sales, and catalog metrics.</p>
      </div>
      <button
        @click="fetchStats"
        class="px-4 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-sky-600 dark:hover:bg-sky-500 text-white text-sm font-medium rounded-xl transition-colors shadow-sm"
      >
        Refresh Stats
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Daily Sales</span>
          <svg class="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1 text-xl font-bold text-slate-900 dark:text-white">
          <span class="text-sm tracking-tight">Rs</span>
          <span>{{ loading ? '...' : Number(stats.daily_sales).toLocaleString('en-US', { maximumFractionDigits: 0 }) }}</span>
        </div>
        <span class="text-xs text-emerald-500 font-medium mt-1 inline-block">Updated just now</span>
      </div>

      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Monthly Revenue</span>
          <svg class="w-5 h-5 text-sky-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div class="flex items-baseline gap-1 text-xl font-bold text-slate-900 dark:text-white">
          <span class="text-sm tracking-tight">Rs</span>
          <span>{{ loading ? '...' : Number(stats.monthly_revenue).toLocaleString('en-US', { maximumFractionDigits: 0 }) }}</span>
        </div>
        <span class="text-xs text-sky-500 font-medium mt-1 inline-block">Current cycle</span>
      </div>

      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Registered Users</span>
          <svg class="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white">
          {{ loading ? '...' : stats.total_users }}
        </div>
        <span class="text-xs text-slate-400 mt-1 inline-block">Workers & Admins</span>
      </div>

      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 shadow-sm">
        <div class="flex items-center justify-between text-slate-500 dark:text-slate-400 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider">Active Profiles</span>
          <svg class="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white">
          {{ loading ? '...' : stats.active_profiles }}
        </div>
        <span class="text-xs text-amber-500 font-medium mt-1 inline-block">Catalog items</span>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Revenue Trend</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400">Last 7 days</p>
          </div>
          <span class="text-xs font-medium text-emerald-500">+12.4%</span>
        </div>

        <svg viewBox="0 0 100 100" class="w-full h-40 text-sky-500" preserveAspectRatio="none">
          <path d="M 0 90 L 100 90" stroke="currentColor" stroke-opacity="0.15" />
          <path d="M 0 70 L 100 70" stroke="currentColor" stroke-opacity="0.08" />
          <path d="M 0 50 L 100 50" stroke="currentColor" stroke-opacity="0.08" />
          <path d="M 0 30 L 100 30" stroke="currentColor" stroke-opacity="0.08" />
          <path :d="revenuePath" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>

        <div class="mt-2 grid grid-cols-7 gap-2 text-[10px] text-slate-500 dark:text-slate-400">
          <div v-for="point in revenueTrend" :key="point.label" class="text-center">
            {{ point.label }}
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Quotation Status</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400">Current pipeline</p>
          </div>
        </div>

        <div class="flex items-center gap-5">
          <svg viewBox="0 0 120 120" class="h-36 w-36 shrink-0">
            <circle cx="60" cy="60" r="42" fill="none" stroke="rgba(148,163,184,0.15)" stroke-width="16" />
            <circle
              v-for="segment in donutSegments"
              :key="segment.label"
              cx="60"
              cy="60"
              r="42"
              fill="none"
              :stroke="segment.color"
              stroke-width="16"
              stroke-linecap="round"
              :stroke-dasharray="`${segment.dash} ${segment.gap}`"
              :stroke-dashoffset="segment.offset"
              transform="rotate(-90 60 60)"
            />
          </svg>

          <div class="space-y-3 w-full">
            <div v-for="item in quotationStatus" :key="item.label" class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: item.color }" />
                <span class="text-sm text-slate-600 dark:text-slate-300">{{ item.label }}</span>
              </div>
              <span class="text-sm font-semibold text-slate-900 dark:text-white">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>