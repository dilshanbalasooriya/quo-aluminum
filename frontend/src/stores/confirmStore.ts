import { ref } from 'vue'
import { defineStore } from 'pinia'

export interface ConfirmRequest {
  title: string
  message: string
  confirmLabel: string
}

export const useConfirmStore = defineStore('confirm', () => {
  const request = ref<ConfirmRequest | null>(null)
  let resolver: ((confirmed: boolean) => void) | null = null

  function ask(
    message: string,
    title = 'Confirm action',
    confirmLabel = 'Delete permanently',
  ): Promise<boolean> {
    if (resolver) resolver(false)

    request.value = { title, message, confirmLabel }
    return new Promise((resolve) => {
      resolver = resolve
    })
  }

  function respond(confirmed: boolean) {
    const resolve = resolver
    resolver = null
    request.value = null
    resolve?.(confirmed)
  }

  return {
    request,
    ask,
    respond,
  }
})
