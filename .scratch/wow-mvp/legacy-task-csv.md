# Legacy task CSV (pre-grilling planning artifact)

Provenance: task list the user brought in on 2026-08-12, written before the grilling rounds settled the MVP decisions. Kept for provenance; the wayfinder map in `map.md` is canonical. Conflicts resolved in favor of settled decisions (384-dim local embeddings, five components, single free-text onboarding, latency post-demo, English deliverables, four persona fixtures as acceptance). Finer slices absorbed into tickets 04/09/10/11/12. Backlog items (Ollama naht, Human-Eval-Admin-View) match the map's Out of scope.

```csv
title,labels,milestone,description
"Setup: Repo-Struktur und Env-Templates","setup","M0-Setup","Monorepo mit frontend/, backend/, data/, prompts/. .env.example mit OPENROUTER_KEY, NEO4J_URI, NEO4J_USER, NEO4J_PASS. README verlinkt Architektur-Sketch und HTML-Doku."
"Neo4j Aura: Free-Tier Vektor-Index verifizieren","setup,daten","M0-Setup","CREATE VECTOR INDEX mvp_test mit 8 dims auf der Aura-Free-Instanz ausführen und wieder droppen. Bei Fehler: Tier-Entscheidung treffen und dokumentieren. Acceptance: Entscheidung steht."
"Embedding- und Chat-Modell festlegen","setup,entscheidung","M0-Setup","EMBED_MODEL = openai/text-embedding-3-small (1536 dims) und Chat-Modell für beide Agenten wählen. Acceptance: llm.py existiert als Single Source of Truth, inkl. embed_batch, embed_one, cloud_model."
"Vektor-Index profile_embeddings anlegen","daten","M1-Daten","CREATE VECTOR INDEX profile_embeddings FOR (p:Profile) ON (p.embedding) mit 1536 dims und cosine. Acceptance: Index in der Aura-Konsole sichtbar."
"Graph-Schema definieren","daten","M1-Daten","Nodes: Student, School, Enterprise, Topic, Event, Profile. Relationships: ATTENDS, HAS_PROFILE, INTERESTED_IN, SEEKS_EXPERTISE, SPONSORS. Kommentiert in neo4j.cypher ablegen."
"Beispieldaten students.json anlegen","daten","M1-Daten","data/students.json mit 5 Studenten: id, name, school, interests, bio. Format exakt wie von ingest.py erwartet."
"ingest.py implementieren und erster Lauf","daten,backend","M1-Daten","profile_text, embed_batch, LOAD_QUERY mit MERGE und UNWIND, BATCH=50. Acceptance: Erster Lauf erzeugt Nodes plus Vektoren, zweiter Lauf erzeugt keine Duplikate (Idempotenz-Test)."
"Sanity-Check: Hybrid-Query manuell","daten,test","M1-Daten","Hybrid-Query aus retrieval.py manuell gegen die ingestierten Daten absetzen. Acceptance: Top-5-Matches sind semantisch plausibel."
"FastAPI-Skeleton plus CORS","backend","M2-Backend","main.py mit FastAPI-App, CORS für Vite-Dev-Server localhost:5173, Health-Endpoint /health."
"ui_schema.py: Allowlist-Schema","backend,sicherheit","M2-Backend","Enums ComponentType, ColorToken, ActionType, Layout. UINode rekursiv mit children und entity_ids. ExperienceSchema. strip_markup-Validator und max_length-Limits."
"retrieval.py: Backend-side Retrieval","backend","M2-Backend","embed_one plus HYBRID_QUERY (Vektor plus Graph-Traversal in einem Cypher). Liefert context-String und allowed_ids-Whitelist an den Orchestrator."
"agents.py: beide Agenten mit System-Prompts","backend,agents","M2-Backend","PersonaModel-Schema. persona_agent und ui_agent via PydanticAI mit output_type. System-Prompts als prompts/persona_modeler.md und prompts/experience_builder.md, beim Start geladen."
"main.py: /api/experience plus verify plus Fallback","backend","M2-Backend","Pipeline: Agent 1, retrieve_context, Agent 2, verify (entity_ids gegen allowed_ids). try/except liefert DEFAULT_EXPERIENCE. Acceptance: Graceful Degradation ohne Crash."
"Agent-Tracing und Logging","backend","M2-Backend","Pro Request: User-Input, Persona-Output, Retrieval-Ergebnis, UI-Output und Latenz in Log-Datei oder Tabelle schreiben. Wichtig für Prompt-Iteration."
"Vue plus Vite Setup plus API-Client","frontend","M3-Frontend","Vue-Projekt mit Vite erzeugen. Fetch-Wrapper für POST /api/experience. TypeScript-Typen aus dem Schema ableiten."
"UiRenderer.vue plus Component Registry","frontend","M3-Frontend","Rekursiver Renderer mit Registry-Mapping auf registrierte Komponenten. Acceptance: kein v-html anywhere, Vue-Escaping bleibt intakt."
"Die sechs Allowlist-Komponenten bauen","frontend,design","M3-Frontend","SignalCard, StudentProfile, EnterpriseCard, NetworkGraph, EventBanner, TextBlock. Styling über Design-Tokens, keine Hex-Codes in Komponenten hartkodiert."
"Onboarding-Flow Tell me about You","frontend","M3-Frontend","Formular mit 3 bis 5 Fragen. Optionaler Step: Zusatzfragen basierend auf Match-Made-Insights. Sendet Antworten an /api/experience."
"Presentation-View plus Theme-Mapping","frontend,design","M3-Frontend","Rendert ExperienceSchema via UiRenderer. ColorToken wird auf persönliche Akzentfarbe des Users gemappt. Layout single_column und grid unterstützen."
"Persona-Persistenz in Neo4j","backend,daten","M4-Robustheit","User-Identität minimal (Session-ID). (:User)-[:HAS_PERSONA]->(:Persona) schreiben, damit Persona beim zweiten Besuch wiederverwendbar ist."
"Rate-Limiting und Cost-Guard","sicherheit","M4-Robustheit","Limit pro IP oder Session auf /api/experience, z.B. 10 Requests pro Tag. Acceptance: Event-Demo kann kein Budget verbrennen."
"Response-Caching für Repeat-User","backend","M4-Robustheit","Cache-Key aus User-ID oder Answers-Hash. Liefert gespeicherte Experience ohne neuen LLM-Call. Spart Kosten und Latenz."
"Fallback-Drill","test","M5-Demo","LLM-Fehler simulieren: falscher Key, Timeout, kaputtes JSON. Acceptance: Default-Experience wird gerendert, Frontend crasht nie."
"E2E-Test mit Beispieldaten","test","M5-Demo","Kompletter Pfad: Onboarding, Persona, Retrieval, UI-JSON, Rendering in Vue, mit den 5 Beispiel-Studenten. Acceptance: Demo läuft in unter 10 Sekunden."
"Prompt-Iteration an echten Antworten","agents","M5-Demo","Beide System-Prompts anhand von mindestens 10 Testläufen schärfen. Fehlertypen (falsche Komponenten, erfundene IDs, Markup) dokumentieren und wegtrainieren."
"Optional: Ollama-Fallback-Naht","zukunft","Backlog","llm.py auf base_url-Switch vorbereiten. Migrations-Plan für komplettes Re-Embedding dokumentieren. Nicht Teil der MVP-Deadline."
"Optional: Human-Eval-Admin-View","zukunft","Backlog","Operator-View, der generierte Templates vor Live-Gang freischaltet. Nicht Teil der MVP-Deadline."
```
