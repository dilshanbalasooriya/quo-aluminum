/*
    toastStore haddle all the notification feedback.
    this provide a abstaction to every endpoit.
    every notification within the application haddle by this.
*/

import { ref } from 'vue'
import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
  id: string
  message: string
  type: ToastType
  timeout?: number
}

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<Toast[]>([])

  /**
   * Show a toast message
   */
  function show(message: string, type: ToastType = 'info', timeout = 4000) {
    const id = Math.random().toString(36).substring(2, 9)
    const toast: Toast = { id, message, type, timeout }

    toasts.value.push(toast)

    if (timeout > 0) {
      setTimeout(() => {
        remove(id)
      }, timeout)
    }
  }

  /**
   * Remove a specific toast by ID
   */
  function remove(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  // Convenient helper methods
  const success = (msg: string, timeout?: number) => show(msg, 'success', timeout)
  const error = (msg: string, timeout?: number) => show(msg, 'error', timeout)
  const info = (msg: string, timeout?: number) => show(msg, 'info', timeout)
  const warning = (msg: string, timeout?: number) => show(msg, 'warning', timeout)

  return {
    toasts,
    show,
    remove,
    success,
    error,
    info,
    warning
  }
})
