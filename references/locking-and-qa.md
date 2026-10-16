# Progressive Locking and Visual QA

## Stages

| Stage | Goal | Locking behavior | Candidate breadth |
|---|---|---|---|
| `explore` | discover concept families | only observed identity and safety are LOCKED | 4–8 concepts; vary role, silhouette, artifact |
| `define` | select a design system | lock identity, humanoid band, role, shape grammar, focal artifact | 3–4; vary costume implementation and shot |
| `canon` | approve the character | lock approved face, markings, proportions, palette, costume landmarks, artifact | 2–3; vary only performance and scene within bounds |
| `production` | make consistent images | all canon fields LOCKED; acting/camera CONTROLLED; atmosphere FREE | 1–3 per shot |

Reference images are evidence anchors, not style-only inspiration. Record their role (`identity`, `costume`, `proportion`, `palette`, or `shot`) and never let a scene reference override an identity reference.

## Field policy

- `LOCKED/P0`: subject ID, source evidence, selected one-to-three-channel Cat Residue contract, humanoid floor, resolved user-approved or source-supported human appearance direction, no deity replication, culture/safety gates, canon reference IDs.
- `DERIVED/P1`: Personality Pattern, Core Contradiction, Emotional Meaning, distinction fingerprint, Guardian Identity, Lore, Worldbuilding, Mythic Resonance, power logic, and symbol semantics.
- `CONTROLLED/P1–P2`: silhouette family, costume modules, artifact implementation, facial intensity, pose, story beat, lens, light direction.
- `FREE/P3`: minor particles, weather texture, secondary props, non-symbolic set dressing, micro color variation.

No lower state may override a higher-priority or more locked field. A retry changes the smallest set of failed CONTROLLED/FREE fields.

## Preflight QA before generation

Reject or repair when:

- humanoid target is below 0.80 or above 0.95, feline residue is outside 5–20%, or prompt asks for quadruped/pet anatomy;
- fewer than three supplied cat identity anchors are present without an explicit missing-data warning;
- Cat Residue is applied before Identity/Lore/Silhouette, uses more than three visual channels, or defaults to the ears+tail+fur+whiskers+claws stack;
- Core Contradiction lacks two evidence-supported truths, or Personal Resonance has fewer than two owner-recognizable anchors;
- a Spirit or myth claim lacks an evidence trace;
- a named myth figure, sacred object, ritual pose, or culture-specific costume is copied;
- pose lacks weight/action/gaze or story beat lacks trigger/now/implied next;
- background has no relation to the action or is directed to dominate the subject;
- LOCKED fields are absent from the compiled prompt and constraint layer.

## Image QA after generation

Score each 0–4 and apply weights from `evals/rubric.md`:

1. identity consistency;
2. humanoid degree and functional humanlike anatomy;
3. feline subtlety and fidelity to the selected residue channels;
4. human cultural/ethnic representation fidelity and non-stereotyping;
5. originality and non-literal Mythic DNA;
6. requested rendering-style fidelity, with `2d_anime_oc` as the default;
7. Western OC character logic and Identity Originality;
8. character recognizability / silhouette;
9. facial acting and gaze specificity;
10. body acting, weight, and line of action;
11. story-beat readability;
12. costume and symbol semantic consistency;
13. Personal Resonance;
14. subject/background hierarchy;
15. canon consistency;
16. artifact and hand integrity.

Hard fail regardless of total score: wrong subject identity, quadruped/pet result, generic anime cat-person default under Western direction, more than three feline-residue channels, extra limbs, deity replica, sacred-symbol misuse, or reference-image identity drift.

## Auto-selection and retry

1. Eliminate hard failures.
2. Rank survivors by weighted score, then by P0 identity score, then story/acting score.
3. Accept only if total ≥ 82/100, every P0 dimension ≥ 3/4, and no canon dimension regresses from the current approved baseline.
4. Retry at most 2 times in `explore/define` and 3 times in `canon/production`.
5. Build a targeted repair prompt from failed dimensions. Preserve seed/reference and repeat every LOCKED/P0 clause verbatim.
6. Stop and return diagnostics if the same hard failure repeats twice or the final retry remains below threshold. Never silently relax identity, culture, or humanoid constraints.

Before image retries, run one character-design-layer retry when `personal_resonance < 7`, `identity_originality < 7`, or `genericness_risk > 4`. This retry may change Identity implementation, Lore, Motifs, Silhouette, Costume, and Props, but may not change evidence or approved identity fields.

Image QA is `pending_pixels` until the rendered image is actually inspected. Structured preflight passing does not imply visual success.
