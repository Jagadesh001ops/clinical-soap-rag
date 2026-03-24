<template>
  <div class="soap-section">
    <div class="section-header">
      <span class="section-icon">{{ icon }}</span>
      <span class="section-label">{{ label }}</span>
    </div>
    <textarea
      class="section-textarea"
      :placeholder="`Enter ${label.toLowerCase()} findings…`"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </div>
</template>

<script setup>
defineProps({
  label:      { type: String, required: true },
  icon:       { type: String, default: '•' },
  modelValue: { type: String, default: '' },
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.soap-section {
  margin-bottom: 1rem;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.35rem;
}
.section-icon  { font-size: 0.9rem; }
.section-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-primary);
}
.section-textarea {
  width: 100%;
  min-height: 90px;
  resize: vertical;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.65rem 0.85rem;
  font-size: 0.875rem;
  line-height: 1.6;
  background: var(--color-surface);
  color: var(--color-text);
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}
.section-textarea:focus {
  border-color: var(--color-primary);
}
</style>
