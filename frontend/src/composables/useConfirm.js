import { ref } from 'vue'

const showDialog = ref(false)
const dialogConfig = ref({
  title: '',
  message: '',
  confirmText: 'Confirmer',
  cancelText: 'Annuler',
  variant: 'primary'
})

let resolvePromise = null

export function useConfirm() {
  const confirm = (config) => {
    dialogConfig.value = {
      title: config.title || 'Confirmation',
      message: config.message || 'Êtes-vous sûr?',
      confirmText: config.confirmText || 'Confirmer',
      cancelText: config.cancelText || 'Annuler',
      variant: config.variant || 'primary'
    }
    
    showDialog.value = true
    
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  const handleConfirm = () => {
    showDialog.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }

  const handleCancel = () => {
    showDialog.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }

  const handleClose = () => {
    showDialog.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }

  return {
    confirm,
    showDialog,
    dialogConfig,
    handleConfirm,
    handleCancel,
    handleClose
  }
}
