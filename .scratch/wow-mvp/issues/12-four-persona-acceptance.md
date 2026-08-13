# Run the four-persona acceptance

Type: task
Status: claimed
Blocked by: 09, 10, 11

## Question

End-to-end acceptance: run the four fixtures' example prompts through the live stack; capture one screenshot per persona; human-eval Agent 1's output against each fixture's expected PersonaModel JSON; check the four pages are visibly distinct (components, layout, accent, register) and every displayed entity is grounded in the retrieval whitelist. Iterate on prompts/grammar until the user accepts. The four screenshots are the deliverable the user asked to see.

## Comments

2026-08-13 overnight run: 4/4 personas composed live end-to-end, themes boardroom/festival/garden/ledger visibly distinct, all entities grounded, theater + staged reveal working, recursive children rendered (David's mentor story). Screenshots: repo `acceptance/` (acceptance-miriam/jonas/david/tobias.png). Iteration queue for the joint session: (1) Miriam — show numeric match scores on SignalCard, fixture asks "ranked by match score"; (2) David — deliver 2–3 mentorship stories, got 1; (3) Tobias — add connections-per-sector view + filterable enterprise list (transparency ask partially met); (4) Jonas — "entrepreneurship" implied not named (minor). Resolution waits on user acceptance.
