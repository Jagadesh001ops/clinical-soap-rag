<template>
  <div class="soap-editor">
    <div class="soap-header">
      <h2>SOAP Note</h2>
      <div class="validation-badge" :class="validationStatus">
        {{ validationLabel }}
      </div>
    </div>

    <div v-if="errors.length" class="validation-errors">
      <p v-for="err in errors" :key="err" class="error-item">⚠ {{ err }}</p>
    </div>

    <div class="soap-sections">
      <SoapSection
        v-for="section in sections"
        :key="section.key"
        :label="section.label"
        :icon="section.icon"
        v-model="localSoap[section.key]"
        :warning="sectionWarning(section.key)"
      />
    </div>

    <div class="soap-actions">
      <button class="btn btn-validate" @click="$emit('validate', localSoap)">
        ✓ Validate
      </button>
      <button class="btn btn-export" @click="$emit('export', localSoap)">
        ↓ Export PDF
      </button>
      <button class="btn btn-save" @click="$emit('save', localSoap)">
        Save Draft
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import SoapSection from './SoapSection.vue'

const props = defineProps({
  soap: { type: Object, default: () => ({}) },
  validationStatus: { type: String, default: 'pending' },
  errors: { type: Array, default: () => [] },
  warnings: { type: Array, default: () => [] },
})
defineEmits(['validate', 'export', 'save', 'update:soap'])

const localSoap = ref({ ...props.soap })

watch(() => props.soap, (val) => { localSoap.value = { ...val } }, { deep: true })

const sections = [
  { key: 'subjective', label: 'Subjective', icon: '🗣' },
  { key: 'objective',  label: 'Objective',  icon: '🔬' },
  { key: 'assessment', label: 'Assessment', icon: '🩺' },
  { key: 'plan',       label: 'Plan',       icon: '📋' },
]

const validationLabel = computed(() => ({
  passed:  '✓ Validated',
  failed:  '✗ Validation Failed',
  pending: '○ Not Validated',
}[props.validationStatus] ?? '○ Not Validated'))

const sectionWarning = (key) =>
  props.warnings.find(w => w.toLowerCase().includes(key)) ?? null
</script>

<style scoped>
.soap-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1.5rem;
  background: var(--color-surface);
}
.soap-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.validation-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}
.validation-badge.passed  { background: #d1fae5; color: #065f46; }
.validation-badge.failed  { background: #fee2e2; color: #991b1b; }
.validation-badge.pending { background: #f3f4f6; color: #6b7280; }
.validation-errors { margin-bottom: 1rem; }
.error-item { color: #b91c1c; font-size: 0.875rem; margin: 0.25rem 0; }
.soap-sections { flex: 1; overflow-y: auto; }
.soap-actions { display: flex; gap: 0.75rem; padding-top: 1rem; }
.btn { padding: 0.5rem 1.25rem; border-radius: 6px; font-weight: 600; cursor: pointer; border: none; }
.btn-validate { background: #2563eb; color: white; }
.btn-export   { background: #059669; color: white; }
.btn-save     { background: #f3f4f6; color: #374151; }
</style>
