<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCatalogStore } from '@/stores/catalogStore'
import { useToastStore } from '@/stores/toastStore'
import apiClient from '@/api/axios'
import WindowSvgPreview from '@/components/WindowSvgPreview.vue'

const catalog = useCatalogStore()
const toast = useToastStore()

// ---------- helpers ----------
// Change this one constant to switch the whole page (e.g. to 'Rs. ').
const CURRENCY_SYMBOL = 'RS'
const MIN_SIZE_MM = 100
const DEFAULT_WORKER_FEE = 500

const formatMoney = (v: number) => `${CURRENCY_SYMBOL}${v.toLocaleString()}`
// Number inputs are '' while the user has cleared the field; treat that as 0 in maths.
const toNum = (v: number | '' | null | undefined) => Number(v) || 0

// Shared Tailwind class strings (text-base on mobile stops iOS zooming the page on focus)
const cardClass =
  'rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:p-6'
const headingClass = 'text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400'
const labelClass = 'mb-1 block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400'
const inputClass =
  'w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-base text-slate-950 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 sm:text-sm'
const selectedTileClass = 'border-slate-950 bg-slate-50 shadow-sm dark:border-slate-100 dark:bg-slate-800'
const idleTileClass = 'border-slate-200 hover:border-slate-300 dark:border-slate-800 dark:hover:border-slate-700'
const pdfActionClass =
  'rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'

// ---------- state ----------
interface CartItem {
  id: string
  window_door_type_id: number
  aluminium_profile_id: number
  typeName: string
  profileName: string
  width_mm: number
  height_mm: number
  quantity: number
  calculated_weight_kg: number
  item_total: number
}

const selectedTypeId = ref<number | null>(null)
const selectedProfileId = ref<number | null>(null)
const widthMm = ref<number | ''>(1200)
const heightMm = ref<number | ''>(1500)
const quantity = ref<number | ''>(1)

const cartItems = ref<CartItem[]>([])
const customerName = ref('')
const customerPhone = ref('')
const workerFee = ref<number | ''>(DEFAULT_WORKER_FEE)
const isSubmitting = ref(false)

// The PDF modal is shown while this is non-null
const issuedQuotationId = ref<number | null>(null)
const pdfFrame = ref<HTMLIFrameElement | null>(null)
const cartSection = ref<HTMLElement | null>(null)

onMounted(async () => {
  if (catalog.profiles.length === 0 || catalog.aluTypes.length === 0) {
    await catalog.fetchCatalog()
  }
  if (catalog.aluTypes?.length > 0) selectedTypeId.value = catalog.aluTypes[0]?.id ?? null
  if (catalog.profiles?.length > 0) selectedProfileId.value = catalog.profiles[0]?.id ?? null
})

// ---------- derived ----------
const activeTypes = computed(() => catalog.aluTypes.filter((t) => t.is_active))
const activeProfiles = computed(() => catalog.profiles.filter((p) => p.is_active))
const currentType = computed(() => catalog.aluTypes.find((t) => t.id === selectedTypeId.value))
const currentProfile = computed(() => catalog.profiles.find((p) => p.id === selectedProfileId.value))

const previewWeight = computed(() => {
  if (!currentProfile.value) return 0
  const weightPerMeter = Number(currentProfile.value.weight_per_meter) || 0
  const perimeterMeters = ((toNum(widthMm.value) + toNum(heightMm.value)) * 2) / 1000
  const totalMeters = perimeterMeters * (1 + (currentType.value?.vertical_bars_count || 0) * 0.5)
  return Number((totalMeters * weightPerMeter * toNum(quantity.value)).toFixed(2))
})

const previewTotal = computed(() => {
  if (!currentProfile.value) return 0
  const ratePerKg = Number(currentProfile.value.rate_per_kg) || 0
  return Number((previewWeight.value * ratePerKg).toFixed(2))
})

const cartSubtotal = computed(() => cartItems.value.reduce((sum, item) => sum + item.item_total, 0))
const cartGrandTotal = computed(() => Number((cartSubtotal.value + toNum(workerFee.value)).toFixed(2)))

const pdfUrl = computed(() => {
  if (issuedQuotationId.value === null) return ''
  return `${apiClient.defaults.baseURL || ''}/quotations/quot-pdf/${issuedQuotationId.value}/invoice.pdf`
})

// ---------- cart actions ----------
function handleAddToCart() {
  const type = currentType.value
  const profile = currentProfile.value
  if (!type || !profile) {
    toast.error('Please select both a window/door type and an aluminium profile.')
    return
  }
  if (toNum(widthMm.value) < MIN_SIZE_MM || toNum(heightMm.value) < MIN_SIZE_MM || toNum(quantity.value) < 1) {
    toast.error(`Width and height must be at least ${MIN_SIZE_MM} mm and quantity at least 1.`)
    return
  }

  cartItems.value.push({
    id: Math.random().toString(36).substring(2, 9),
    window_door_type_id: type.id,
    aluminium_profile_id: profile.id,
    typeName: type.type_name,
    profileName: profile.profile_name,
    width_mm: toNum(widthMm.value),
    height_mm: toNum(heightMm.value),
    quantity: toNum(quantity.value),
    calculated_weight_kg: previewWeight.value,
    item_total: previewTotal.value,
  })
  toast.success('Item added to quotation batch.')
}

function handleRemoveCartItem(index: number) {
  cartItems.value.splice(index, 1)
}

function scrollToCart() {
  cartSection.value?.scrollIntoView({ block: 'start' })
}

function clearDraft() {
  cartItems.value = []
  customerName.value = ''
  customerPhone.value = ''
}

function handleDiscard() {
  if (!confirm('Are you sure you want to discard this quotation draft?')) return
  clearDraft()
  workerFee.value = DEFAULT_WORKER_FEE
  toast.success('Draft discarded.')
}

// ---------- checkout ----------
async function handleConfirmQuotation() {
  if (!customerName.value.trim()) {
    toast.error('Please enter the customer name.')
    return
  }
  if (cartItems.value.length === 0) {
    toast.error('Please add at least one item to the quotation.')
    return
  }

  isSubmitting.value = true
  try {
    const res = await apiClient.post('/quotations', {
      customer_name: customerName.value,
      customer_phone: customerPhone.value,
      worker_fee: toNum(workerFee.value),
      items: cartItems.value.map((item) => ({
        aluminium_profile_id: item.aluminium_profile_id,
        window_door_type_id: item.window_door_type_id,
        height_mm: item.height_mm,
        width_mm: item.width_mm,
        quantity: item.quantity,
      })),
    })
    issuedQuotationId.value = res.data.id
    toast.success('Quotation issued successfully!')
  } catch {
    toast.error('Failed to issue quotation.')
  } finally {
    isSubmitting.value = false
  }
}

function handleCloseAndNew() {
  issuedQuotationId.value = null
  clearDraft()
}

// ---------- PDF actions ----------
function handleDownloadPdf() {
  if (pdfUrl.value) window.open(pdfUrl.value, '_blank')
}

function handlePrintPdf() {
  if (pdfFrame.value?.contentWindow) pdfFrame.value.contentWindow.print()
  else handleDownloadPdf()
}

function handleSharePdf() {
  if (!pdfUrl.value) return
  if (navigator.share) {
    navigator
      .share({ title: 'Aluminium Quotation', text: `Quotation for ${customerName.value}`, url: pdfUrl.value })
      .catch(() => {})
  } else {
    navigator.clipboard.writeText(pdfUrl.value)
    toast.success('PDF link copied to clipboard!')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-950 dark:text-slate-100">Create quotation</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">Pick a style, set the size and watch the drawing update.</p>
      </div>
      <button
        v-if="cartItems.length > 0"
        type="button"
        @click="handleDiscard"
        class="rounded-xl border border-rose-300 px-4 py-2 text-sm font-bold text-rose-600 transition-colors hover:bg-rose-50 dark:border-rose-800 dark:text-rose-400 dark:hover:bg-rose-950/30"
      >
        Discard draft
      </button>
    </div>

    <!--
      ZONE 1 — configure.
      Below lg: one column. The workspace (preview + size inputs) comes FIRST and is sticky, so the drawing
      stays on screen while you scroll the style/profile lists and while you edit width/height.
      From lg: two columns. Style + profile on the left, workspace pinned on the right spanning both rows.

      The sticky panel must be a direct child of this container, and the container must be `flex` (not
      `grid`) on small screens, otherwise `position: sticky` has no room to stick.
      If your app header is sticky, change `top-2` to the header height (e.g. `top-16`).
    -->
    <div class="flex flex-col gap-4 lg:grid lg:grid-cols-12 lg:gap-6">
      <!-- Workspace: live preview + size inputs + live price, all in one pinned panel -->
      <section
        class="sticky top-2 z-20 space-y-3 rounded-2xl border border-slate-200 bg-white p-3 shadow-md dark:border-slate-800 dark:bg-slate-900 sm:p-4 lg:col-span-5 lg:col-start-8 lg:row-span-2 lg:row-start-1 lg:top-6 lg:space-y-4 lg:self-start [@media(max-height:30rem)]:static"
      >
        <!-- Drawing height is capped (22dvh phone / 28dvh tablet / 40dvh desktop) so the panel always fits -->
        <div class="[&_svg]:mx-auto [&_svg]:max-h-[22dvh] sm:[&_svg]:max-h-[28dvh] lg:[&_svg]:max-h-[40dvh]">
          <WindowSvgPreview
            :category="currentType?.category || 'WINDOW'"
            :vertical-bars="currentType?.vertical_bars_count || 0"
            :horizontal-bars="currentType?.horizontal_bars_count || 0"
            :width-mm="toNum(widthMm)"
            :height-mm="toNum(heightMm)"
          />
        </div>

        <div>
          <h2 :class="[headingClass, 'mb-2 hidden lg:block']">
            3. Set size & quantity — the drawing updates as you type
          </h2>
          <div class="grid grid-cols-3 gap-2 sm:gap-3">
            <label class="block">
              <span :class="labelClass">Width (mm)</span>
              <input v-model.number="widthMm" type="number" min="100" :class="[inputClass, 'font-bold']" />
            </label>
            <label class="block">
              <span :class="labelClass">Height (mm)</span>
              <input v-model.number="heightMm" type="number" min="100" :class="[inputClass, 'font-bold']" />
            </label>
            <label class="block">
              <span :class="labelClass">Quantity</span>
              <input v-model.number="quantity" type="number" min="1" :class="[inputClass, 'font-bold']" />
            </label>
          </div>
        </div>

        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs text-slate-500">{{ previewWeight }} kg estimated</p>
            <p class="text-xl font-extrabold leading-tight text-emerald-600 dark:text-emerald-400">
              {{ formatMoney(previewTotal) }}
            </p>
            <button
              v-if="cartItems.length > 0"
              type="button"
              @click="scrollToCart"
              class="text-xs font-bold text-slate-600 underline dark:text-slate-400"
            >
              Review quotation ({{ cartItems.length }})
            </button>
          </div>
          <button
            type="button"
            @click="handleAddToCart"
            class="shrink-0 rounded-xl bg-slate-950 px-4 py-3 text-sm font-bold text-white shadow-sm transition-colors hover:bg-slate-900 dark:bg-slate-100 dark:text-slate-950 dark:hover:bg-white"
          >
            + Add to quotation
          </button>
        </div>
      </section>

      <!-- 1. Style -->
      <section :class="[cardClass, 'space-y-4 lg:col-span-7 lg:col-start-1 lg:row-start-1']">
        <h2 :class="headingClass">1. Select window / door style</h2>
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <button
            v-for="t in activeTypes"
            :key="t.id"
            type="button"
            :aria-pressed="selectedTypeId === t.id"
            @click="selectedTypeId = t.id"
            class="flex flex-col items-center justify-center gap-2 rounded-xl border-2 p-3 transition-all"
            :class="selectedTypeId === t.id ? selectedTileClass : idleTileClass"
          >
            <span class="flex h-16 w-16 items-center justify-center rounded-lg bg-slate-100 p-1 dark:bg-slate-950">
              <svg viewBox="0 0 100 100" class="h-full w-full drop-shadow-sm" aria-hidden="true">
                <rect x="10" y="10" width="80" height="80" rx="4" class="fill-white stroke-slate-800 dark:fill-slate-800 dark:stroke-sky-400" stroke-width="6" />
                <rect x="16" y="16" width="68" height="68" rx="2" class="fill-sky-50/50 dark:fill-sky-950/20" />
                <template v-if="t.vertical_bars_count > 0">
                  <line
                    v-for="n in t.vertical_bars_count"
                    :key="'v' + n"
                    :x1="(100 / (t.vertical_bars_count + 1)) * n"
                    y1="16"
                    :x2="(100 / (t.vertical_bars_count + 1)) * n"
                    y2="84"
                    class="stroke-slate-400"
                    stroke-width="4"
                  />
                </template>
                <template v-if="t.horizontal_bars_count > 0">
                  <line
                    v-for="n in t.horizontal_bars_count"
                    :key="'h' + n"
                    x1="16"
                    :y1="(100 / (t.horizontal_bars_count + 1)) * n"
                    x2="84"
                    :y2="(100 / (t.horizontal_bars_count + 1)) * n"
                    class="stroke-slate-400"
                    stroke-width="4"
                  />
                </template>
              </svg>
            </span>
            <span class="text-center">
              <span class="block max-w-[110px] truncate text-xs font-bold text-slate-950 dark:text-slate-100">{{ t.type_name }}</span>
              <span class="text-[10px] uppercase text-slate-500">{{ t.category }}</span>
            </span>
          </button>
        </div>
      </section>

      <!-- 2. Profile -->
      <section :class="[cardClass, 'space-y-4 lg:col-span-7 lg:col-start-1 lg:row-start-2']">
        <h2 :class="headingClass">2. Select aluminium profile & gauge</h2>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <button
            v-for="p in activeProfiles"
            :key="p.id"
            type="button"
            :aria-pressed="selectedProfileId === p.id"
            @click="selectedProfileId = p.id"
            class="flex items-center justify-between rounded-xl border-2 p-4 text-left transition-all"
            :class="selectedProfileId === p.id ? selectedTileClass : idleTileClass"
          >
            <span>
              <span class="block text-sm font-bold text-slate-950 dark:text-slate-100">{{ p.profile_name }}</span>
              <span class="block text-xs text-slate-500">Gauge: {{ p.gauge }} | {{ p.weight_per_meter }} kg/m</span>
            </span>
            <span class="text-sm font-extrabold text-emerald-600 dark:text-emerald-400">
              {{ formatMoney(Number(p.rate_per_kg)) }}/kg
            </span>
          </button>
        </div>
      </section>
    </div>

    <!-- ZONE 2 — review & issue. Outside the sticky zone so the pinned preview doesn't crowd the form on phones. -->
    <section ref="cartSection" :class="[cardClass, 'scroll-mt-4 space-y-4']">
      <h2 :class="headingClass">Quotation cart ({{ cartItems.length }} items)</h2>

      <div class="grid gap-6 lg:grid-cols-2">
        <!-- Items -->
        <div>
          <p v-if="cartItems.length === 0" class="py-4 text-center text-sm italic text-slate-500">
            No items yet. Set a size above and choose “Add to quotation”.
          </p>
          <div v-else class="max-h-72 space-y-3 overflow-y-auto pr-1">
            <div
              v-for="(item, index) in cartItems"
              :key="item.id"
              class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-800 dark:bg-slate-950"
            >
              <div>
                <p class="font-bold text-slate-950 dark:text-slate-100">{{ item.typeName }} (x{{ item.quantity }})</p>
                <p class="text-xs text-slate-500">{{ item.profileName }} — {{ item.width_mm }}×{{ item.height_mm }}mm</p>
              </div>
              <div class="flex items-center gap-3">
                <span class="font-extrabold text-emerald-600 dark:text-emerald-400">{{ formatMoney(item.item_total) }}</span>
                <button
                  type="button"
                  aria-label="Remove item"
                  @click="handleRemoveCartItem(index)"
                  class="text-xs font-bold text-rose-500 hover:text-rose-700"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Customer + totals -->
        <div class="space-y-4">
          <div class="space-y-3">
            <label class="block">
              <span :class="labelClass">Customer name *</span>
              <input v-model="customerName" type="text" placeholder="e.g. John Doe" :class="inputClass" />
            </label>
            <label class="block">
              <span :class="labelClass">Customer phone</span>
              <input v-model="customerPhone" type="text" placeholder="e.g. +94 77 123 4567" :class="inputClass" />
            </label>
            <label class="block">
              <span :class="labelClass">Worker / labor fee ({{ CURRENCY_SYMBOL }})</span>
              <input v-model.number="workerFee" type="number" min="0" step="5" :class="inputClass" />
            </label>
          </div>

          <div class="space-y-2 border-t border-slate-100 pt-3 text-sm dark:border-slate-800">
            <div class="flex justify-between text-slate-600 dark:text-slate-400">
              <span>Subtotal:</span>
              <span class="font-bold text-slate-950 dark:text-slate-100">{{ formatMoney(cartSubtotal) }}</span>
            </div>
            <div class="flex justify-between text-slate-600 dark:text-slate-400">
              <span>Worker fee:</span>
              <span class="font-bold text-slate-950 dark:text-slate-100">{{ formatMoney(toNum(workerFee)) }}</span>
            </div>
            <div class="flex items-center justify-between border-t border-slate-100 pt-2 dark:border-slate-800">
              <span class="text-base font-bold text-slate-950 dark:text-slate-100">Grand total:</span>
              <span class="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400">{{ formatMoney(cartGrandTotal) }}</span>
            </div>
          </div>

          <button
            type="button"
            :disabled="isSubmitting || cartItems.length === 0"
            @click="handleConfirmQuotation"
            class="w-full rounded-xl bg-emerald-600 py-3 font-bold text-white shadow-sm transition-colors hover:bg-emerald-500 disabled:opacity-50"
          >
            {{ isSubmitting ? 'Confirming...' : 'Confirm & generate PDF' }}
          </button>
        </div>
      </div>
    </section>

    <!-- PDF viewer modal -->
    <div
      v-if="issuedQuotationId !== null"
      role="dialog"
      aria-modal="true"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-sm"
    >
      <div class="flex h-[90dvh] w-full max-w-4xl flex-col space-y-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-2xl dark:border-slate-800 dark:bg-slate-900 sm:p-6">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-3 dark:border-slate-800">
          <div>
            <h3 class="text-lg font-bold text-slate-950 dark:text-slate-100">Quotation issued successfully!</h3>
            <p class="text-xs text-slate-500">Preview the final PDF invoice below or use the actions.</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button type="button" :class="pdfActionClass" @click="handlePrintPdf">🖨 Print</button>
            <button type="button" :class="pdfActionClass" @click="handleDownloadPdf">📥 Download</button>
            <button type="button" :class="pdfActionClass" @click="handleSharePdf">🔗 Share</button>
            <button
              type="button"
              class="rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-rose-500"
              @click="handleCloseAndNew"
            >
              Close & new
            </button>
          </div>
        </div>

        <div class="w-full flex-1 overflow-hidden rounded-xl border border-slate-200 bg-slate-100 dark:border-slate-800 dark:bg-slate-950">
          <iframe ref="pdfFrame" :src="pdfUrl" class="h-full w-full" title="Quotation PDF preview"></iframe>
        </div>
      </div>
    </div>
  </div>
</template>