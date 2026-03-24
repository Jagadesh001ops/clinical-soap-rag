<template>
  <main class="workspace">
    <!-- LEFT PANE: Clinical Note Input -->
    <section class="pane pane-note">
      <div class="pane-header">
        <span class="pane-label">Clinical Note</span>
        <span class="badge">Input</span>
      </div>

      <textarea
        v-model="store.noteText"
        class="note-input"
        placeholder="Paste or type the clinical note here…"
        spellcheck="false"
      />

      <div class="pane-footer">
        <button
          class="btn btn-primary"
          :disabled="!store.noteText.trim() || store.loading"
          @click="handleGenerate"
        >
          <span v-if="store.loading" class="spinner" />
          <span v-else>⚡ Generate SOAP</span>
        </button>
        <button class="btn btn-ghost" @click="store.resetSOAP">Reset</button>
      </div>

      <div v-if="store.error" class="error-banner">
        {{ store.error }}
      </div>
    </section>

    <!-- DIVIDER -->
    <div class="divider" />

    <!-- RIGHT PANE: SOAP Editor -->
    <section class="pane pane-soap">
      <div class="pane-header">
        <span class="pane-label">SOAP Note</span>
        <div
          class="validation-pill"
          :class="store.validationStatus"
        >{{ validationLabel }}</div>
      </div>

      <div v-if="!store.hasSOAP && !store.loading" class="empty-state">
        <div class="empty-icon">🩺</div>
        <p>Generate a SOAP note from the clinical note on the left.</p>
      </div>

      <template v-else>
        <div
          v-if="store.validationErrors.length"
          class="error-list"
        >
          <p v-for="e in store.validationErrors" :key="e">⚠ {{ e }}</p>
        </div>

        <div class="soap-form">
          <SoapSection
            v-for="s in soapSections"
            :key="s.key"
            :label="s.label"
            :icon="s.icon"
            v-model="store.soap[s.key]"
          />
        </div>

        <div class="pane-footer">
          <button class="btn btn-outline" @click="store.validateSOAP">✓ Validate</button>
          <button class="btn btn-success" @click="store.exportPDF()">↓ Export PDF</button>
        </div>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useSoapStore } from '../stores/soap'
import SoapSection from '../components/SoapSection.vue'

const store = useSoapStore()

const soapSections = [
  { key: 'subjective', label: 'Subjective', icon: '🗣' },
  { key: 'objective',  label: 'Objective',  icon: '🔬' },
  { key: 'assessment', label: 'Assessment', icon: '🩺' },
  { key: 'plan',       label: 'Plan',       icon: '📋' },
]

const validationLabel = computed(() => ({
  passed:  '✓ Validated',
  failed:  '✗ Issues Found',
  pending: '○ Not Validated',
}[store.validationStatus] ?? '○ Not Validated'))

async function handleGenerate() {
  await store.generateSOAP(store.noteText)
}
</script>

<style scoped>
.workspace {
  display: flex;
  height: calc(100vh - 60px);
  overflow: hidden;
  background: var(--color-bg);
}

.pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 1.5rem;
}

.divider {
  width: 1px;
  background: var(--color-border);
  flex-shrink: 0;
}

.pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.pane-label {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted);
}

.badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  background: var(--color-surface);
  border-radius: 999px;
  color: var(--color-muted);
}

.validation-pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.75rem;
  border-radius: 999px;
}
.validation-pill.passed  { background: #d1fae5; color: #065f46; }
.validation-pill.failed  { background: #fee2e2; color: #991b1b; }
.validation-pill.pending { background: #f3f4f6; color: #6b7280; }

.note-input {
  flex: 1;
  resize: none;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.7;
  background: var(--color-surface);
  color: var(--color-text);
  outline: none;
}
.note-input:focus { border-color: var(--color-primary); }

.pane-footer {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
}

.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--color-primary); color: white; }
.btn-outline  { background: transparent; border: 1.5px solid var(--color-primary); color: var(--color-primary); }
.btn-success  { background: #059669; color: white; }
.btn-ghost    { background: transparent; color: var(--color-muted); }

.spinner {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--color-muted);
}
.empty-icon { font-size: 3rem; }

.error-banner, .error-list p {
  color: #991b1b;
  font-size: 0.875rem;
  padding: 0.5rem;
  margin-top: 0.5rem;
}

.soap-form { flex: 1; overflow-y: auto; }
</style>
