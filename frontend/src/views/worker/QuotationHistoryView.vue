<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import apiClient from '@/api/axios'
import { useToastStore } from '@/stores/toastStore'

const toast = useToastStore()

// ---------- config ----------
// Use the exact path shown in FastAPI /docs (a missing/extra trailing slash triggers a redirect).
const LIST_URL = '/quotations'
const pdfUrlFor = (id: number) => `/quotations/quot-pdf/${id}/invoice.pdf`

// Change this one constant to switch the page's currency (e.g. to 'Rs. ').
const CURRENCY_SYMBOL = 'Rs.'
const PAGE_SIZE = 20

const formatMoney = (v: number) => `${CURRENCY_SYMBOL}${v.toLocaleString()}`
const formatDate = (iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : ''

// ---------- API shape ----------
interface QuotationRow {
  id: number
  number: string
  customerName: string
  customerPhone: string
  total: number
  createdAt: string | null
  itemCount: number | null
}

// The ONLY place that knows the API's field names. Adjust here if your response differs.
function normalize(raw: Record<string, any>): QuotationRow {
  const subtotal = Number(raw.subtotal) || 0
  const workerFee = Number(raw.worker_fee) || 0
  return {
    id: raw.id,
    number: raw.quotation_number ?? `#${raw.id}`,
    customerName: raw.customer_name ?? raw.customer?.name ?? raw.customer?.customer_name ?? 'Unknown customer',
    customerPhone: raw.customer_phone ?? raw.customer?.phone ?? raw.customer?.customer_phone ?? '',
    total: Number(raw.total ?? raw.grand_total ?? raw.total_amount ?? subtotal + workerFee) || 0,
    createdAt: raw.created_at ?? raw.issued_at ?? null,
    itemCount: Array.isArray(raw.items) ? raw.items.length : null,
  }
}

// ---------- state ----------
const rows = ref<QuotationRow[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const search = ref('')
const visibleCount = ref(PAGE_SIZE)
const downloadingId = ref<number | null>(null)

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [r.customerName, r.customerPhone, r.number].some((field) => field.toLowerCase().includes(q)),
  )
})
const visibleRows = computed(() => filtered.value.slice(0, visibleCount.value))

watch(search, () => {
  visibleCount.value = PAGE_SIZE
})

// ---------- actions ----------
async function loadQuotations() {
  status.value = 'loading'
  try {
    const res = await apiClient.get(LIST_URL)
    const list: Record<string, any>[] = Array.isArray(res.data) ? res.data : (res.data?.items ?? [])
    rows.value = list.map(normalize).sort((a, b) => b.id - a.id) // newest first
    status.value = 'ready'
  } catch {
    status.value = 'error'
    toast.error('Failed to load quotations.')
  }
}

// Fetched through axios so the JWT is sent (a plain link/iframe cannot send it).
async function downloadPdf(row: QuotationRow) {
  if (downloadingId.value !== null) return
  downloadingId.value = row.id
  try {
    const res = await apiClient.get(pdfUrlFor(row.id), { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `Quotation_${row.number.replace(/[^\w-]+/g, '')}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.error('Could not download this quotation.')
  } finally {
    downloadingId.value = null
  }
}

onMounted(loadQuotations)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-950 dark:text-slate-100">Saved quotations</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">Find a past quotation and download its PDF.</p>
      </div>
      <button
        type="button"
        :disabled="status === 'loading'"
        @click="loadQuotations"
        class="rounded-xl border border-slate-300 px-4 py-2 text-sm font-bold text-slate-700 transition-colors hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        Refresh
      </button>
    </div>

    <!-- Search -->
    <label class="block">
      <span class="sr-only">Search quotations</span>
      <input
        v-model="search"
        type="search"
        placeholder="Search by customer, phone or quotation number"
        class="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-base text-slate-950 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 sm:text-sm"
      />
    </label>

    <!-- List card -->
    <section class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p v-if="status === 'loading'" class="px-6 py-10 text-center text-sm text-slate-500">Loading quotations…</p>

      <div v-else-if="status === 'error'" class="flex flex-col items-center gap-3 px-6 py-10 text-sm text-slate-600 dark:text-slate-400">
        <p>The quotations could not be loaded.</p>
        <button
          type="button"
          @click="loadQuotations"
          class="rounded-lg bg-slate-950 px-4 py-2 text-xs font-bold text-white hover:bg-slate-900 dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-white"
        >
          Try again
        </button>
      </div>

      <p v-else-if="rows.length === 0" class="px-6 py-10 text-center text-sm text-slate-500">
        No quotations yet. Quotations you issue will appear here.
      </p>

      <p v-else-if="filtered.length === 0" class="px-6 py-10 text-center text-sm text-slate-500">
        No quotations match “{{ search }}”.
      </p>

      <ul v-else class="divide-y divide-slate-100 dark:divide-slate-800">
        <li
          v-for="row in visibleRows"
          :key="row.id"
          class="flex flex-wrap items-center gap-x-4 gap-y-3 px-4 py-4 sm:px-6"
        >
          <div class="min-w-0 flex-1 basis-56">
            <p class="truncate font-bold text-slate-950 dark:text-slate-100">{{ row.customerName }}</p>
            <p class="text-xs text-slate-500">
              {{ row.number }}
              <span v-if="row.createdAt"> · {{ formatDate(row.createdAt) }}</span>
              <span v-if="row.customerPhone"> · {{ row.customerPhone }}</span>
            </p>
          </div>

          <div class="text-right">
            <p class="text-lg font-extrabold text-emerald-600 dark:text-emerald-400">{{ formatMoney(row.total) }}</p>
            <p v-if="row.itemCount !== null" class="text-xs text-slate-500">
              {{ row.itemCount }} {{ row.itemCount === 1 ? 'item' : 'items' }}
            </p>
          </div>

          <button
            type="button"
            :disabled="downloadingId !== null"
            @click="downloadPdf(row)"
            class="shrink-0 rounded-xl bg-slate-950 px-4 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-slate-900 disabled:opacity-50 dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-white"
          >
            {{ downloadingId === row.id ? 'Preparing…' : 'Download PDF' }}
          </button>
        </li>
      </ul>

      <!-- Footer: count + load more -->
      <div
        v-if="status === 'ready' && filtered.length > 0"
        class="flex items-center justify-between gap-3 border-t border-slate-100 px-4 py-3 text-xs text-slate-500 dark:border-slate-800 sm:px-6"
      >
        <span>Showing {{ visibleRows.length }} of {{ filtered.length }}</span>
        <button
          v-if="visibleRows.length < filtered.length"
          type="button"
          @click="visibleCount += PAGE_SIZE"
          class="font-bold text-slate-700 underline dark:text-slate-300"
        >
          Show more
        </button>
      </div>
    </section>
  </div>
</template>