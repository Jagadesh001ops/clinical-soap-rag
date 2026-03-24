<template>
  <nav class="app-nav">
    <div class="nav-brand">
      <span class="brand-icon">🏥</span>
      <span class="brand-name">ClinicalSOAP</span>
      <span class="brand-tag">beta</span>
    </div>
    <div class="nav-links">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/workspace">Workspace</RouterLink>
    </div>
  </nav>
</template>

<style scoped>
.app-nav {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1rem;
}
.brand-icon  { font-size: 1.25rem; }
.brand-name  { color: var(--color-text); }
.brand-tag {
  font-size: 0.65rem;
  padding: 0.1rem 0.45rem;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 999px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.nav-links { display: flex; gap: 1.5rem; }
.nav-links a {
  text-decoration: none;
  font-size: 0.875rem;
  color: var(--color-muted);
  font-weight: 500;
}
.nav-links a.router-link-active { color: var(--color-primary); }
</style>
