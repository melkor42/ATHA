<script setup>
import FactList from './atoms/FactList.vue'
import StageFlow from './atoms/StageFlow.vue'
import PartnerLayers from './atoms/PartnerLayers.vue'
import editionFacts from '@knowledge/edition_facts.json'
import ontology from '@knowledge/digest_ontology.json'

// The concept page states the edition's standing context as a fixed reference.
// It reads the same committed sources that seed the knowledge graph and reuses
// the composed atoms, so this page and a live composed answer present the
// edition identically — same labels, same order, same status pills — and the
// two cannot drift apart.

// Mirrors the backend's label derivation (id slug -> Capitalised words) so the
// static facts read exactly as the composed FactList does.
const labelFromId = (id) =>
  id.replace(/-/g, ' ').replace(/^\w/, (c) => c.toUpperCase())

// The brand never-list, mirroring backend/skeleton.py NEVER_LIST. These names
// are felt but never shown on a page; composed answers filter them at query
// time, so the static page filters them at render to keep the two in agreement.
const NEVER = /\b(hadora|teamwork|whack|monash|cristian)\b/i
const banned = (...parts) => parts.some((p) => p && NEVER.test(p))

const editionNode = {
  title: 'Edition 001 — where things stand',
  text: 'The current state of the first ATHA edition',
  facts: editionFacts.facts
    .filter((f) => !banned(f.id, f.fact, f.status))
    .map((f) => ({
      label: labelFromId(f.id),
      value: f.fact,
      status: f.status
    }))
}

// Same ordering the graph tail uses: stages by their arc order, partners by
// rank (initiator, co-host, then the rest).
const KIND_RANK = { initiator: 0, 'co-host': 1 }

const rhythmNode = {
  title: 'The rhythm — seven stages',
  text: 'The arc every ATHA edition follows',
  stages: [...ontology.ontology.arc_stages]
    .sort((a, b) => a.order - b.order)
    .filter((s) => !banned(s.name, s.description))
    .map((s) => ({ name: s.name, description: s.description }))
}

const layersNode = {
  title: 'Who stands behind ATHA',
  text: 'The partners and their roles',
  layers: [...ontology.ontology.organizations]
    .sort((a, b) => (KIND_RANK[a.kind] ?? 2) - (KIND_RANK[b.kind] ?? 2))
    .filter((o) => !banned(o.name, o.kind, o.description))
    .map((o) => ({ name: o.name, kind: o.kind, description: o.description }))
}
</script>

<template>
  <section class="edition">
    <p class="label kicker">Edition 001</p>
    <p class="lede">{{ editionFacts.preamble }}</p>
    <div class="atoms">
      <FactList :node="editionNode" />
      <StageFlow :node="rhythmNode" />
      <PartnerLayers :node="layersNode" />
    </div>
  </section>
</template>

<style scoped>
.edition {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-top: clamp(48px, 9vh, 104px);
}
.kicker { opacity: 0.6; }
.lede {
  font-size: 17px;
  line-height: 1.5;
  opacity: 0.8;
  max-width: 68ch;
}
.atoms {
  display: flex;
  flex-direction: column;
  gap: clamp(40px, 6vh, 64px);
  margin-top: 22px;
}
</style>
