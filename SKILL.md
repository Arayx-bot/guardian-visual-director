---
name: guardian-visual-director
description: Convert cat behavior evidence, photo identity, Spirit/Mythic Resonance, and lore into a soul-first, strongly humanoid Western fantasy/RPG Guardian OC brief, layered image prompt, and automated QA contract. Use for MOMO Guardian design, regeneration, canon locking, or image-API preparation; do not use for deity replicas, generic anime cat-person templates, or four-legged cats with accessories.
---

## 全局入口与操作确认

以本文件真实目录为包根；从软链接调用时先 resolve，不依赖外层 MOMO 仓库。Python 3.10+，编译器只用标准库；缺环境先说明安装来源与影响，按用户选择安装并复检。输入由使用者指定，输出默认 stdout；显式 --output 使用用户工作目录，不写安装目录。

备份、上传、修改线上页面（包括隐藏草稿）、付费生成、删除：执行前先说明具体动作、输入与目标、影响范围及预计费用，等待用户对该次范围确认后执行；费用未知如实说明，非交互会话只给方案。对同一明确范围已有确认的不重复询问。Skill 调用不隐含这些动作的授权。只读调用验收仅检查流程与输入要求，不生成素材、创建稿件、写状态或调用真实外部服务。


# Guardian Visual Director

Create a contemporary original Guardian OC whose soul, role, lore, silhouette, and visual storytelling are complete before subtle cat identity residue is applied.

## Highest-level principle

**Design the soul first. Design the character second. Add the cat last.**

先设计灵魂，再设计角色，最后才加入猫。The intended result is “a cat's soul became a humanoid Guardian,” never “a beautiful person wearing cat elements.”

## Non-negotiable direction

- The subject is a humanoid fantasy being, normally `humanoid_level` 0.80–0.95 with only 5–20% feline residue. Humanlike torso, arms, hands, legs, stance, costume, and facial acting are required.
- The default audience is the United States / Western OC, fantasy, RPG, D&D, and TTRPG community. Default rendering is polished 2D Western fantasy OC / RPG character art: identity-first, lore-driven, personality-driven, and readable in silhouette. East Asian game-art finish is allowed, but a generic anime cat-person template is not. Use `2d_anime_oc` only when explicitly requested.
- Default portrait composition leaves visible breathing room without making the OC feel remote: keep the full/medium-full subject near 79–82% of canvas height, preserve roughly 6–9% headroom, and reserve negative space toward gaze and implied next action. Do not let the character fill the frame unless the user explicitly asks for a close shot.
- Compose for asymmetrical equilibrium, not mechanical symmetry. The Guardian is the only primary focal point; background people or human-shaped silhouettes are off by default. No isolated near-black peripheral mass, competing face, or high-contrast background figure may pull the visual center of gravity away from the Guardian.
- Default background presentation is `game_character_select_stage`: a shallow circular raised platform, two or three broad character-linked value fields, large incomplete offset structural arcs, one subdued atmospheric depth layer, and a single Artifact response line/node. It should feel like premium 2D game key art, never a furnished room, literal temple, complete halo, sacred gateway, or dense HUD.
- Default to a `minimal` background complexity budget: one architectural motif, at most three material families, no decorative props, and no background people. Use broad low-contrast value planes and warm/cool separation for depth; reserve fine edges, texture, saturation, and peak contrast for the Guardian. Increase background complexity only when the user explicitly asks or a Story Beat cannot read without one essential object.
- Build a deliberate three-value character architecture. Light coat/hair characters still need controlled mid/dark anchors in underlayers, waist structure, legs, footwear, harness, or Artifact; dark characters need protected light windows around face and hands. Background colors may echo the OC but must not merge with the identity silhouette.
- Do not begin from cat ears, tail, fur color, or hairstyle. Apply one to three selective cat-residue channels only after Identity, Lore, Personality, Core Contradiction, Archetype, Silhouette, and Visual Storytelling work without them. Behavioral feline residue outranks decorative residue. Do not default to ears + tail + fur + whiskers + claws, a quadruped cat, mascot, pet in costume, or generic furry body.
- Direct the humanoid character's human cultural/ethnic appearance explicitly when evidence or the user supports it. Keep source tradition, geography, modern nationality, ethnicity, and visible appearance as separate fields; never infer one from another without provenance.
- Treat observed behavior as evidence, not mind-reading. Keep a traceable chain: evidence → pattern → relationship/personality signal → spirit meaning → Mythic DNA → original concept → visual translation.
- Myth is downstream resonance/lineage, never a casting decision or costume sheet. Apply “Ancient meaning, original character, contemporary design.” Original Guardian identity must exist before mythic resonance is considered. Do not recreate named deities, sacred bodies, ritual poses, regalia, weapons, mounts, or protected motifs.
- Design from the subject-specific manner of expression, not only the top Spirit label. Two cautious cats must diverge when one waits at thresholds and another retreats then returns.
- Produce both a Structured Visual Brief and a compiled, layered Image Prompt. Never return only prompt prose.
- Prefer autonomous operation. Ask only when missing identity evidence would make canon claims unsafe; otherwise mark uncertainty and continue with reversible, unlocked fields.

## Workflow

1. Normalize either `director-input-v1` or the project’s `guardian-packet-v0`. For existing packets, preserve evidence IDs and all generation/culture gates.
2. Build an evidence ledger. Separate direct observation, supplied interpretation, sourced myth, and creative extension. Never promote a creative inference to observed fact.
3. Derive, in order: Personality Pattern → Core Contradiction → Emotional Meaning → Guardian Identity → Archetype/Role → minimal Lore → one to three Symbolic Motifs → Silhouette/Body Language → Costume/Props → Cat Residue. Read [references/western-oc-character-system.md](references/western-oc-character-system.md) whenever creating or revising a Guardian concept.
4. Compute a distinction fingerprint across approach, recovery, spatial choice, bond mode, temporal ritual, exploration strategy, contradiction, silhouette, motif family, and owner-specific signals. Use open-ended signals when evidence does not fit the seed rules.
5. Resolve the human identity direction. Read [references/human-identity-and-culture.md](references/human-identity-and-culture.md) whenever a mythic source, country/region, nationality, ethnicity, skin tone, facial-feature direction, or hair texture should influence the OC.
6. Translate the completed character system into shape language, silhouette, costume, material language, prop/artifact, facial acting, body acting, story beat, camera, light, and environment. Read [references/director-rules.md](references/director-rules.md) for the decision rules.
7. Assign every important field a mutability state and priority. Read [references/locking-and-qa.md](references/locking-and-qa.md) when creating variants, using canon references, or preparing automated retries.
8. Build the explicit Prompt Builder fields, then compile them into the existing layered prompt contract. Repeat soul/identity anchors near the beginning and hard constraints; place selected cat residue late.
9. Run structural, personal-resonance, genericness, and image preflight QA. Regenerate the character-design layer once if Personal Resonance or Identity Originality is below 7/10, or Genericness Risk is above 4/10. If pixels are available, rank candidates and retry only failed dimensions while preserving LOCKED fields.

## Mutability contract

- `LOCKED`: exact evidence, approved identity/canon anchors, and selected cat-residue contract; never vary during retries.
- `DERIVED`: recompute only when source evidence changes.
- `CONTROLLED`: may vary within explicit bounds or an approved option set.
- `FREE`: may vary for freshness but cannot contradict higher-priority fields.
- Priorities are `P0` hard identity/safety, `P1` meaning/readability, `P2` direction, and `P3` polish.

Use progressive locking: `explore` varies widely, `define` locks identity and concept, `canon` locks the approved design and reference image, and `production` varies only shot-level details.

## Resources

- Run `scripts/guardian_visual_director.py` for deterministic baseline compilation and schema-aware output.
- Validate with `scripts/public_evals.py` (synthetic, independent of project outputs); read [evals/rubric.md](evals/rubric.md) when judging model-authored briefs or rendered images.
- Input contract: [schemas/director-input.schema.json](schemas/director-input.schema.json).
- Output contract: [schemas/visual-brief.schema.json](schemas/visual-brief.schema.json).
- Seed translation rules: [rules/director-rules.json](rules/director-rules.json). Extend these rules rather than forcing novel evidence into an existing label.
- Western/US-market character logic: [references/western-oc-character-system.md](references/western-oc-character-system.md).
- Synthetic example: [examples/synthetic-cat.input.json](examples/synthetic-cat.input.json); all observations are invented and no images are included. The original project examples are excluded from the public package.

## Completion contract

Return or save a schema-valid brief containing the soul-first principle, traced personality pattern, core contradiction, emotional meaning, Guardian identity, archetype/role, lore, worldbuilding, motifs, silhouette-first design, meaningful costume/props/materials, one-to-three-channel cat residue, personal resonance, distinctiveness, humanoid level, human identity direction, acting/story/camera direction, Prompt Builder fields, compiled prompt, hard constraints, field controls, scored QA, candidate selection, and retry policy. State unresolved evidence explicitly. Do not claim image-level QA passed until pixels were inspected.
