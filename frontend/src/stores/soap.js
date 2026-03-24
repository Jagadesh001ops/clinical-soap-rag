/**
 * Pinia store for SOAP note state management.
 * Handles API calls to the Flask backend and tracks
 * generation, validation, and export lifecycle.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API = import.meta.env.VITE_API_BASE_URL || ''

export const useSoapStore = defineStore('soap', () => {
  // State
  const noteText = ref('')
  const soap = ref({ subjective: '', objective: '', assessment: '', plan: '' })
  const validationStatus = ref('pending')   // 'pending' | 'passed' | 'failed'
  const validationErrors = ref([])
  const validationWarnings = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const hasSOAP = computed(() =>
    Object.values(soap.value).some(v => v.trim().length > 0)
  )

  // Actions
  async function generateSOAP(rawNote) {
    loading.value = true
    error.value = null
    validationStatus.value = 'pending'
    try {
      const { data } = await axios.post(`${API}/api/generate`, { note_text: rawNote })
      soap.value = {
        subjective: data.subjective || '',
        objective:  data.objective  || '',
        assessment: data.assessment || '',
        plan:       data.plan       || '',
      }
      validationStatus.value   = data.validation_status   || 'pending'
      validationErrors.value   = data.validation_errors   || []
      validationWarnings.value = data.validation_warnings || []
    } catch (err) {
      error.value = err.response?.data?.error || 'Generation failed'
    } finally {
      loading.value = false
    }
  }

  async function validateSOAP() {
    loading.value = true
    error.value = null
    try {
      const { data } = await axios.post(`${API}/api/validate`, soap.value)
      validationStatus.value   = data.validation_status
      validationErrors.value   = data.validation_errors   || []
      validationWarnings.value = data.validation_warnings || []
    } catch (err) {
      error.value = err.response?.data?.error || 'Validation failed'
    } finally {
      loading.value = false
    }
  }

  async function exportPDF(patientId = 'unknown') {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post(
        `${API}/api/export`,
        { ...soap.value, patient_id: patientId },
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `soap_${patientId}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = 'PDF export failed'
    } finally {
      loading.value = false
    }
  }

  function resetSOAP() {
    soap.value = { subjective: '', objective: '', assessment: '', plan: '' }
    validationStatus.value = 'pending'
    validationErrors.value = []
    validationWarnings.value = []
    error.value = null
  }

  return {
    noteText, soap, validationStatus, validationErrors,
    validationWarnings, loading, error, hasSOAP,
    generateSOAP, validateSOAP, exportPDF, resetSOAP,
  }
})
