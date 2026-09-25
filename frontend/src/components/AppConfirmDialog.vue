<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useConfirmStore } from '@/stores/confirmStore'

const confirmStore = useConfirmStore()
const cancelButton = ref<HTMLButtonElement | null>(null)

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && confirmStore.request) {
    confirmStore.respond(false)
  }
}

watch(
  () => confirmStore.request,
  async (request) => {
    if (request) {
      await nextTick()
      cancelButton.value?.focus()
    }
  },
)

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="confirmStore.request"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
      role="presentation"
      @click.self="confirmStore.respond(false)"
    >
      <section
        class="w-full max-w-md rounded-2xl border border-slate-200 border-t-4 border-t-rose-500 bg-white p-6 shadow-2xl dark:border-slate-700 dark:border-t-rose-400 dark:bg-slate-900"
        role="alertdialog"
        aria-modal="true"
        :aria-labelledby="'confirm-title'"
        :aria-describedby="'confirm-message'"
      >
        <div class="flex items-start gap-4">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-rose-100 text-rose-600 dark:bg-rose-950/60 dark:text-rose-300" aria-hidden="true">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M10.3 3.7 2.8 17a2 2 0 0 0 1.7 3h15a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0Z" />
            </svg>
          </div>
          <div>
            <h2 id="confirm-title" class="text-lg font-bold text-slate-950 dark:text-white">
              {{ confirmStore.request.title }}
            </h2>
            <p id="confirm-message" class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
              {{ confirmStore.request.message }}
            </p>
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button
            ref="cancelButton"
            type="button"
            class="min-w-24 rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-slate-400 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-800"
            @click="confirmStore.respond(false)"
          >
            Cancel
          </button>
          <button
            type="button"
            class="min-w-36 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-400"
            @click="confirmStore.respond(true)"
          >
            {{ confirmStore.request.confirmLabel }}
          </button>
        </div>
      </section>
    </div>
  </Transition>
</template>
