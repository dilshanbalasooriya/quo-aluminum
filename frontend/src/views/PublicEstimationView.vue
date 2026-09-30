<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import apiClient from '@/api/axios'
import WindowSvgPreview from '@/components/WindowSvgPreview.vue'
import type { ProfileOut, TypeOut } from '@/types'

const profiles = ref<ProfileOut[]>([])
const types = ref<TypeOut[]>([])
const selectedProfileId = ref<number | null>(null)
const selectedTypeId = ref<number | null>(null)
const widthMm = ref<number | ''>(1200)
const heightMm = ref<number | ''>(1500)
const quantity = ref<number | ''>(1)
const priceAdjustment = ref<number | ''>(0)
const itemTotal = ref(0)
const weight = ref(0)
const isLoading = ref(true)
const isPricing = ref(false)
const errorMessage = ref('')

const activeTypes = computed(() => types.value)
const activeProfiles = computed(() => profiles.value)
const currentType = computed(() => types.value.find((type) => type.id === selectedTypeId.value))
const currentProfile = computed(() => profiles.value.find((profile) => profile.id === selectedProfileId.value))
const toNumber = (value: number | '' | null | undefined) => Number(value) || 0
const isValid = computed(() =>
  selectedTypeId.value !== null &&
  selectedProfileId.value !== null &&
  toNumber(widthMm.value) >= 100 &&
  toNumber(heightMm.value) >= 100 &&
  toNumber(quantity.value) >= 1,
)
const adjustment = computed(() => toNumber(priceAdjustment.value))
const estimateTotal = computed(() => Math.max(0, itemTotal.value + adjustment.value))
const formatMoney = (value: number) => `Rs ${value.toLocaleString()}`

let priceRequestId = 0
let priceTimer: ReturnType<typeof setTimeout> | undefined

function printEstimate() {
  window.print()
}

async function loadCatalog() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [profileResponse, typeResponse] = await Promise.all([
      apiClient.get<ProfileOut[]>('/public/catalog/aluminium-profiles'),
      apiClient.get<TypeOut[]>('/public/catalog/window-door-types'),
    ])
    profiles.value = profileResponse.data
    types.value = typeResponse.data
    selectedProfileId.value = profiles.value[0]?.id ?? null
    selectedTypeId.value = types.value[0]?.id ?? null
    if (!profiles.value.length || !types.value.length) {
      errorMessage.value = 'Estimation options are not available right now.'
    }
  } catch {
    errorMessage.value = 'Could not load estimation options. Please try again.'
  } finally {
    isLoading.value = false
  }
}

async function refreshPrice() {
  const requestId = ++priceRequestId
  if (!isValid.value) {
    itemTotal.value = 0
    weight.value = 0
    isPricing.value = false
    return
  }
  isPricing.value = true
  try {
    const response = await apiClient.post('/public/quotations/price-preview', {
      aluminium_profile_id: selectedProfileId.value,
      window_door_type_id: selectedTypeId.value,
      width_mm: toNumber(widthMm.value),
      height_mm: toNumber(heightMm.value),
      quantity: toNumber(quantity.value),
    })
    if (requestId !== priceRequestId) return
    itemTotal.value = Number(response.data.item_total)
    weight.value = Number((response.data.calculated_weight_kg * toNumber(quantity.value)).toFixed(3))
    errorMessage.value = ''
  } catch {
    if (requestId === priceRequestId) {
      itemTotal.value = 0
      weight.value = 0
      errorMessage.value = 'Could not calculate this estimate. Check your dimensions and try again.'
    }
  } finally {
    if (requestId === priceRequestId) isPricing.value = false
  }
}

watch([selectedTypeId, selectedProfileId, widthMm, heightMm, quantity], () => {
  clearTimeout(priceTimer)
  priceTimer = setTimeout(refreshPrice, 250)
})

onMounted(async () => {
  await loadCatalog()
  if (isValid.value) await refreshPrice()
})

onBeforeUnmount(() => clearTimeout(priceTimer))
</script>

<template>
  <div class="min-h-screen bg-[#f5f6f2] text-slate-950">
    <header class="border-b border-slate-200/80 bg-white/85">
      <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-8">
        <RouterLink to="/" class="flex items-center gap-3" aria-label="QUO Aluminium home">
          <span class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-800 text-sm font-black text-white">QA</span>
          <span class="leading-tight">
            <span class="block text-sm font-black">QUO Aluminium</span>
            <span class="block text-xs text-slate-500">Frame cost estimator</span>
          </span>
        </RouterLink>
        <RouterLink
          to="/login"
          class="rounded-md border border-slate-300 px-4 py-2 text-sm font-bold text-slate-700 transition hover:border-slate-500 hover:bg-slate-50"
        >
          Staff sign in
        </RouterLink>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-4 py-8 sm:px-8 sm:py-12">
      <div class="mb-8 flex flex-col justify-between gap-5 border-b border-slate-300 pb-7 sm:flex-row sm:items-end">
        <div>
          <p class="mb-2 text-xs font-bold uppercase text-emerald-800">Build your estimate</p>
          <h1 class="text-3xl font-black leading-tight sm:text-4xl">Shape a frame. Set your price.</h1>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Choose a frame style and aluminium profile, then tune the dimensions and price adjustment. Your estimate updates as you work.
          </p>
        </div>
        <button
          type="button"
          class="w-fit rounded-md bg-slate-950 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-emerald-900 disabled:cursor-not-allowed disabled:opacity-50 print:hidden"
          :disabled="!itemTotal || isPricing"
          @click="printEstimate"
        >
          Print estimate
        </button>
      </div>

      <p v-if="errorMessage && activeTypes.length && activeProfiles.length" role="alert" class="mb-6 border-l-4 border-rose-600 bg-rose-50 px-4 py-3 text-sm text-rose-800">
        {{ errorMessage }}
      </p>
      <div v-if="isLoading" class="py-16 text-center text-sm font-semibold text-slate-500">Loading frame options...</div>
      <div v-else-if="!activeTypes.length || !activeProfiles.length" class="py-12 text-center text-sm text-slate-600">
        <p role="alert">{{ errorMessage || 'No frame options are available at the moment.' }}</p>
      </div>

      <div v-else class="grid items-start gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.8fr)]">
        <div class="space-y-8">
          <section aria-labelledby="style-heading">
            <div class="mb-4 flex items-baseline justify-between gap-3">
              <h2 id="style-heading" class="text-lg font-extrabold">01 / Frame style</h2>
              <span class="text-xs font-semibold text-slate-500">{{ activeTypes.length }} available</span>
            </div>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <button
                v-for="type in activeTypes"
                :key="type.id"
                type="button"
                :aria-pressed="selectedTypeId === type.id"
                class="flex min-h-28 flex-col justify-between border p-4 text-left transition"
                :class="selectedTypeId === type.id ? 'border-emerald-800 bg-emerald-50 ring-1 ring-emerald-800' : 'border-slate-300 bg-white hover:border-slate-500'"
                @click="selectedTypeId = type.id"
              >
                <span class="text-sm font-bold">{{ type.type_name }}</span>
                <span class="mt-4 flex items-end justify-between text-[11px] uppercase text-slate-500">
                  <span>{{ type.category }}</span>
                  <span>{{ type.vertical_bars_count }}V / {{ type.horizontal_bars_count }}H</span>
                </span>
              </button>
            </div>
          </section>

          <section aria-labelledby="profile-heading">
            <div class="mb-4 flex items-baseline justify-between gap-3">
              <h2 id="profile-heading" class="text-lg font-extrabold">02 / Aluminium profile</h2>
              <span class="text-xs font-semibold text-slate-500">Select a rate</span>
            </div>
            <div class="divide-y divide-slate-200 border-y border-slate-300 bg-white">
              <label
                v-for="profile in activeProfiles"
                :key="profile.id"
                class="flex cursor-pointer items-center gap-3 px-4 py-4 transition hover:bg-slate-50"
                :class="selectedProfileId === profile.id ? 'bg-emerald-50/70' : ''"
              >
                <input v-model="selectedProfileId" type="radio" :value="profile.id" class="h-4 w-4 accent-emerald-800" />
                <span class="min-w-0 flex-1">
                  <span class="block truncate text-sm font-bold">{{ profile.profile_name }}<span v-if="profile.brand"> · {{ profile.brand }}</span></span>
                  <span class="block text-xs text-slate-500">Gauge {{ profile.gauge }} · {{ profile.weight_per_meter }} kg/m</span>
                </span>
                <span class="shrink-0 text-sm font-extrabold text-emerald-900">Rs {{ Number(profile.rate_per_kg).toLocaleString() }}/kg</span>
              </label>
            </div>
          </section>
        </div>

        <aside class="space-y-4 lg:sticky lg:top-6">
          <div class="print:border-slate-400">
            <WindowSvgPreview
              :category="currentType?.category || 'WINDOW'"
              :vertical-bars="currentType?.vertical_bars_count || 0"
              :horizontal-bars="currentType?.horizontal_bars_count || 0"
              :width-mm="toNumber(widthMm)"
              :height-mm="toNumber(heightMm)"
            />
          </div>

          <section class="border border-slate-300 bg-white p-5 sm:p-6" aria-labelledby="dimensions-heading">
            <h2 id="dimensions-heading" class="mb-4 text-lg font-extrabold">03 / Dimensions & quantity</h2>
            <div class="grid grid-cols-3 gap-3">
              <label class="min-w-0">
                <span class="mb-1 block text-xs font-bold uppercase text-slate-500">Width · mm</span>
                <input v-model.number="widthMm" type="number" min="100" class="w-full rounded border border-slate-300 px-3 py-2.5 text-base font-bold" />
              </label>
              <label class="min-w-0">
                <span class="mb-1 block text-xs font-bold uppercase text-slate-500">Height · mm</span>
                <input v-model.number="heightMm" type="number" min="100" class="w-full rounded border border-slate-300 px-3 py-2.5 text-base font-bold" />
              </label>
              <label class="min-w-0">
                <span class="mb-1 block text-xs font-bold uppercase text-slate-500">Quantity</span>
                <input v-model.number="quantity" type="number" min="1" class="w-full rounded border border-slate-300 px-3 py-2.5 text-base font-bold" />
              </label>
            </div>
            <p v-if="!isValid" class="mt-2 text-xs font-semibold text-rose-700">Enter dimensions of at least 100 mm and a quantity of at least 1.</p>
          </section>

          <section class="border-t-4 border-emerald-800 bg-slate-950 p-5 text-white sm:p-6" aria-labelledby="estimate-heading">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h2 id="estimate-heading" class="text-xs font-bold uppercase text-slate-400">Your estimate</h2>
                <p class="mt-1 text-xs text-slate-300">{{ weight.toLocaleString() }} kg estimated weight</p>
              </div>
              <span v-if="isPricing" class="text-xs text-emerald-300">Updating...</span>
            </div>
            <div class="mt-5 space-y-3 border-t border-slate-700 pt-4 text-sm">
              <div class="flex justify-between gap-4 text-slate-300"><span>Frame cost</span><span>{{ formatMoney(itemTotal) }}</span></div>
              <label class="flex items-center justify-between gap-4 text-slate-300">
                <span>Custom price adjustment</span>
                <span class="flex items-center gap-2">
                  <span>Rs</span>
                  <input v-model.number="priceAdjustment" type="number" step="10" class="w-28 rounded border border-slate-600 bg-slate-900 px-2 py-1.5 text-right text-sm font-bold text-white" aria-label="Custom price adjustment in rupees" />
                </span>
              </label>
              <div class="flex items-end justify-between gap-4 border-t border-slate-700 pt-4">
                <span class="font-bold">Estimated total</span>
                <span class="text-2xl font-black text-emerald-300" :class="{ 'opacity-50': isPricing }">{{ formatMoney(estimateTotal) }}</span>
              </div>
            </div>
            <p class="mt-4 text-[11px] leading-5 text-slate-400">Price adjustment is applied to this estimate only. Nothing is saved or submitted.</p>
          </section>
        </aside>
      </div>
    </main>

    <footer class="border-t border-slate-200 bg-white px-4 py-5 text-center text-xs text-slate-500">
      QUO Aluminium · Estimates are indicative and may change with final measurements and material rates.
    </footer>
  </div>
</template>

<style>
@media print {
  header a:last-child,
  button,
  footer {
    display: none !important;
  }

  body {
    background: white !important;
  }
}
</style>