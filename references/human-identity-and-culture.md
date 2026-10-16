# Human Identity and Cultural Direction

The Guardian is a strongly humanoid OC, so its human appearance must be directed as deliberately as its cat identity. Do not collapse these distinct concepts:

- `source_tradition`: the myth/story tradition supplying deep meaning;
- `cultural_context`: cultural contexts relevant to the source or requested OC;
- `geographic_context`: place or region, historical or contemporary;
- `modern_nationality`: a modern civic identity, only when explicitly appropriate;
- `ethnicity_reference`: a human population/heritage reference used for casting or appearance;
- `appearance_direction`: visible design decisions such as skin-tone range, facial-feature direction, and hair texture.

## Provenance modes

- `user_defined`: the user explicitly chooses the OC's human identity. Treat resolved appearance as `LOCKED/P0`.
- `source_aligned`: reviewed source context supports a human representation direction. Record the source and scope; do not claim it is the deity's one true “race.”
- `fictional_original`: the setting is original and the human identity is intentionally designed, not presented as historical fact.
- `unspecified`: evidence is insufficient. Keep the field unresolved instead of silently defaulting to European, East Asian, or any other appearance.

## Source-aligned decision rule

A mythic tradition may guide representation, but it does not automatically determine a modern nationality or a single ethnicity. For example, a tradition spanning multiple regions or communities should retain that breadth until a specific episode, source community, user direction, or cultural review narrows it.

When the source alignment is sufficiently grounded, write a casting statement such as:

> Contemporary humanoid OC with source-aligned West African human features, scoped to the reviewed Akan context; avoid pan-African genericization and do not copy ceremonial dress or sacred symbols.

The casting statement controls human appearance only. Costume and symbols remain governed by separate visual-source and cultural-review rules.

## Appearance translation

Prefer concrete, respectful direction over labels alone:

- skin-tone range and undertone;
- facial geometry described without caricature;
- hair texture and styling, distinguishing natural texture from culture-specific hairstyles;
- age presentation and gender expression when supplied;
- variation allowed within the approved casting reference.

Do not exaggerate features to make ethnicity “obvious.” Do not infer personality, morality, class, temperament, or mystical power from ethnicity or nationality. Do not mix unrelated cultural signifiers to make a generic “exotic” fantasy design.

## Uncertainty and QA

If cultural context is known but ethnicity is not, output `source_context_only` and add a visible unresolved note. Generation may continue during exploration, but the result cannot become human-appearance Canon. Image QA checks whether the render matches the resolved casting direction, avoids stereotyped exaggeration, and keeps cultural dress/symbol claims within their own evidence boundaries.
