# Image API Integration Contract

The compiler output is provider-neutral. An adapter should map:

- `compiled_prompt.positive_prompt` → primary prompt/input text;
- `compiled_prompt.negative_prompt` → negative prompt where supported, otherwise append as explicit avoid clauses;
- `identity_translator.reference_images` → image/reference inputs with roles and weights;
- `automation.candidate_generation.count` → number of candidates;
- `automation.seed_policy` → seed behavior;
- `automation.image_qa_checks` → vision evaluator request;
- `automation.retry_policy` → bounded orchestration.

Store per candidate: provider, model/version, request ID, seed, prompt hash, reference IDs and weights, raw response metadata, image URI, QA scores, hard failures, and selection status.

Recommended loop:

```text
validate input
→ compile brief
→ generate candidate batch
→ run image QA against brief + canon references
→ reject hard failures
→ auto-select passing candidate
→ otherwise create dimension-specific repair prompt
→ bounded retry
→ save winner as optional Canon candidate
```

Do not automatically promote a winner to Canon. Promotion is a separate state change; once approved, capture face, markings, proportions, palette, costume landmarks, artifact geometry, and reference image ID as LOCKED/P0 fields for later runs.
