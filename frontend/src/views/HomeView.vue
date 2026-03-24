<template>
  <div class="home">
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">Haystack · Gemini 1.5 Pro · pgvector</div>
        <h1 class="hero-title">
          Clinical Documentation,<br />
          <span class="highlight">Intelligently Structured</span>
        </h1>
        <p class="hero-subtitle">
          A RAG pipeline that processes lengthy clinical notes and generates
          validated SOAP summaries — powered by Gemini 1.5 Pro's 1M-token
          context window and a pgvector retrieval layer on PostgreSQL.
        </p>
        <div class="hero-actions">
          <RouterLink to="/workspace" class="btn btn-primary">
            Open Workspace →
          </RouterLink>
          <a
            href="https://github.com/YOUR_USERNAME/clinical-soap-rag"
            target="_blank"
            class="btn btn-outline"
          >View on GitHub</a>
        </div>
      </div>
      <div class="hero-visual">
        <div class="pipeline-card">
          <div v-for="step in pipeline" :key="step.label" class="pipeline-step">
            <span class="step-icon">{{ step.icon }}</span>
            <div class="step-body">
              <div class="step-label">{{ step.label }}</div>
              <div class="step-desc">{{ step.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="features">
      <div v-for="f in features" :key="f.title" class="feature-card">
        <div class="feature-icon">{{ f.icon }}</div>
        <h3>{{ f.title }}</h3>
        <p>{{ f.desc }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
const pipeline = [
  { icon: '📄', label: 'Clinical Note', desc: 'Raw, unstructured patient note' },
  { icon: '🔒', label: 'De-identification', desc: 'PHI scrubbing before processing' },
  { icon: '🔍', label: 'pgvector Retrieval', desc: 'Cosine search over MIMIC-IV embeddings' },
  { icon: '🤖', label: 'Gemini 1.5 Pro', desc: '1M-token context · SOAP generation' },
  { icon: '✅', label: 'Multi-step Validation', desc: 'Completeness · ICD codes · Coherence' },
  { icon: '📋', label: 'SOAP + PDF Export', desc: 'Editable note with one-click PDF' },
]

const features = [
  {
    icon: '🧠',
    title: 'Haystack RAG Pipeline',
    desc: 'Haystack 2.x orchestrates retrieval, prompt building, generation, and validation as composable, testable components.',
  },
  {
    icon: '🗄️',
    title: 'pgvector on PostgreSQL',
    desc: 'Vector search co-located with structured patient data — no separate vector database service required.',
  },
  {
    icon: '⚡',
    title: 'Gemini 1.5 Pro',
    desc: "Google's 1M-token context window handles even the longest discharge summaries without chunking.",
  },
  {
    icon: '🛡️',
    title: 'Multi-step Validation',
    desc: 'Four validation gates check completeness, ICD-10 code presence, clinical coherence, and output length.',
  },
  {
    icon: '🖥️',
    title: 'Split-screen Editor',
    desc: 'Vue.js workspace with the original note on the left and an editable SOAP form on the right.',
  },
  {
    icon: '🐳',
    title: 'Docker Compose',
    desc: 'Single `docker compose up` spins up the API, frontend, and pgvector-enabled PostgreSQL together.',
  },
]
</script>

<style scoped>
.home { padding: 3rem 2rem; max-width: 1200px; margin: 0 auto; }

.hero {
  display: flex;
  gap: 4rem;
  align-items: flex-start;
  margin-bottom: 5rem;
}

.hero-content { flex: 1; }

.hero-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  padding: 0.3rem 0.9rem;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 999px;
  margin-bottom: 1.25rem;
  text-transform: uppercase;
}

.hero-title {
  font-size: 2.75rem;
  font-weight: 800;
  line-height: 1.15;
  color: var(--color-text);
  margin-bottom: 1.25rem;
}
.highlight { color: var(--color-primary); }

.hero-subtitle {
  font-size: 1.05rem;
  color: var(--color-muted);
  line-height: 1.7;
  max-width: 520px;
  margin-bottom: 2rem;
}

.hero-actions { display: flex; gap: 1rem; }

.btn {
  padding: 0.65rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s;
}
.btn-primary { background: var(--color-primary); color: white; }
.btn-outline  { background: transparent; border: 1.5px solid var(--color-border); color: var(--color-text); }

.hero-visual { flex: 0 0 340px; }

.pipeline-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.pipeline-step {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-border);
}
.pipeline-step:last-child { border-bottom: none; }

.step-icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 2px; }
.step-label { font-size: 0.85rem; font-weight: 600; color: var(--color-text); }
.step-desc  { font-size: 0.78rem; color: var(--color-muted); margin-top: 2px; }

/* Features grid */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.feature-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1.5rem;
}
.feature-icon { font-size: 1.75rem; margin-bottom: 0.75rem; }
.feature-card h3 { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.4rem; color: var(--color-text); }
.feature-card p  { font-size: 0.85rem; color: var(--color-muted); line-height: 1.6; }

@media (max-width: 900px) {
  .hero { flex-direction: column; }
  .hero-visual { width: 100%; }
  .hero-visual .pipeline-card { flex-direction: column; }
  .features { grid-template-columns: 1fr 1fr; }
}
</style>
