#!/usr/bin/env python3
"""Compile Guardian evidence into a stable humanoid OC visual brief.

This is a deterministic baseline and orchestration contract, not a replacement for
creative model reasoning. It preserves traceability, locking, and prompt structure
so model-authored expansions remain testable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = SKILL_ROOT / "rules" / "director-rules.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def default_human_identity(source_traditions: list[str] | None = None, culture_review_required: bool = False) -> dict[str, Any]:
    contexts = [compact(x) for x in (source_traditions or []) if compact(x)]
    return {
        "mode": "source_aligned" if contexts else "unspecified",
        "cultural_context": contexts,
        "geographic_context": [],
        "modern_nationality": {"value": None, "status": "unresolved"},
        "ethnicity_reference": {"value": None, "status": "review_required" if contexts else "unresolved"},
        "appearance_direction": {"skin_tone": None, "facial_features": None, "hair_texture": None},
        "provenance_note": "Source tradition is context only; it does not by itself prove a modern nationality or a single ethnicity." if contexts else "No human cultural or ethnic direction was supplied.",
        "culture_review_required": bool(culture_review_required or contexts),
    }


def resolve_human_identity(data: dict[str, Any]) -> dict[str, Any]:
    source = data.get("human_identity_direction") or default_human_identity(
        data.get("mythic_dna", {}).get("source_traditions", []),
        data.get("mythic_dna", {}).get("culture_review_required", False),
    )
    nationality = source.get("modern_nationality", {"value": None, "status": "unresolved"})
    ethnicity = source.get("ethnicity_reference", {"value": None, "status": "unresolved"})
    appearance = source.get("appearance_direction", {})
    appearance = {
        "skin_tone": appearance.get("skin_tone"),
        "facial_features": appearance.get("facial_features"),
        "hair_texture": appearance.get("hair_texture"),
    }
    contexts = [compact(x) for x in source.get("cultural_context", []) if compact(x)]
    geography = [compact(x) for x in source.get("geographic_context", []) if compact(x)]
    ethnicity_value = compact(ethnicity.get("value"))
    nationality_value = compact(nationality.get("value"))
    appearance_phrases = [compact(v) for v in appearance.values() if compact(v)]
    resolved_statuses = {"explicit_user", "source_supported"}
    resolved = bool(ethnicity_value and ethnicity.get("status") in resolved_statuses)
    uncertainties: list[str] = []
    if not ethnicity_value:
        uncertainties.append("人类族裔/heritage 尚未确定；不得静默采用任何默认人种，也不得晋升人类外貌 Canon。")
    if ethnicity_value and not appearance_phrases:
        uncertainties.append("已有族裔参考但缺少具体外貌方向；生成时避免夸张特征，后续需补充肤色、面部和发质范围。")
    if nationality_value and nationality.get("status") not in resolved_statuses:
        uncertainties.append("现代国别尚未获得明确用户指示或来源支持，只能作为待核验信息。")

    if resolved:
        casting = f"Original humanoid OC with respectful, non-stereotyped {ethnicity_value} human representation"
        if nationality_value:
            casting += f"; modern nationality direction: {nationality_value}"
        if contexts:
            casting += f"; culturally scoped to {', '.join(contexts)}"
    elif contexts:
        casting = f"Human casting should remain source-context-aware for {', '.join(contexts)}, but ethnicity is unresolved; do not claim one correct race or default to an unrelated appearance"
    else:
        casting = "Human cultural and ethnic appearance is unresolved; use only for exploration and do not promote the face to Canon"
    if appearance_phrases:
        casting += "; visible appearance: " + "; ".join(appearance_phrases)

    return {
        "mode": source.get("mode", "unspecified"),
        "cultural_context": contexts,
        "geographic_context": geography,
        "modern_nationality": nationality,
        "ethnicity_reference": ethnicity,
        "appearance_direction": appearance,
        "casting_statement": casting,
        "provenance_note": compact(source.get("provenance_note")),
        "uncertainties": uncertainties,
        "anti_stereotype_constraints": [
            "do not exaggerate facial features to signal ethnicity",
            "do not infer personality, morality, class, temperament, or mystical power from ethnicity or nationality",
            "do not use culture-specific clothing, body marks, jewelry, or sacred symbols without separate evidence",
            "do not mix unrelated cultural signifiers into a generic exotic fantasy design",
        ],
        "culture_review_required": bool(source.get("culture_review_required", False)),
        "resolved_for_canon": resolved,
    }


def normalize_guardian_packet(packet: dict[str, Any]) -> dict[str, Any]:
    subject = packet["subject"]
    evidence = []
    for item in packet["behavior_analysis"]["evidence"]:
        evidence.append({
            "id": item["id"],
            "context": item.get("question_id", ""),
            "observation": item["observation"],
            "action": item.get("answer", ""),
            "outcome": "",
            "signals": [],
            "confidence": item.get("confidence", "medium"),
        })

    visual = packet.get("visual_research", {})
    resonance = packet.get("resonance", {})
    generation = packet.get("generation_contract", {})
    physical = compact(subject.get("physical_identity"))
    traits: list[dict[str, Any]] = []
    if physical and "没有照片" not in physical and "待" not in physical:
        traits.append({
            "id": "legacy-physical-identity",
            "kind": "other",
            "description": physical,
            "confidence": 0.55,
            "source_image_ids": [],
        })

    source_traditions = [resonance.get("entity", {}).get("tradition", "")] if resonance.get("entity") else []
    culture_review_required = packet.get("validation", {}).get("culture_review_required", False)
    return {
        "schema_version": "director-input-v1",
        "input_meta": {"id": packet["packet_meta"]["id"], "stage": "define", "language": "zh-CN"},
        "subject": {
            "display_name": subject["display_name"],
            "species": "cat",
            "sex": subject.get("sex", "unknown"),
            "photo_identity": {"traits": traits, "reference_images": []},
        },
        "evidence": evidence,
        "personality_relationship_signals": [
            trait["label"] for trait in packet.get("personality_analysis", {}).get("traits", [])
        ] + packet.get("behavior_analysis", {}).get("patterns", []),
        "spirit": {
            "dominant": packet["spirit"]["dominant"],
            "secondary": [],
            "statement": packet["spirit"]["statement"],
            "relationship_signal": packet["behavior_analysis"].get("relationship_signature", ""),
            "contradiction": "",
            "power": packet["spirit"].get("power", ""),
        },
        "mythic_dna": {
            "meaning": resonance.get("rationale", packet["spirit"]["statement"]),
            "motifs": resonance.get("matched_tags", []),
            "source_traditions": source_traditions,
            "prohibited_literal_elements": visual.get("prohibited_direct_copy", []) + generation.get("must_not_include", []),
            "culture_review_required": culture_review_required,
        },
        "human_identity_direction": default_human_identity(source_traditions, culture_review_required),
        "guardian_lore": {
            "title": packet["spirit"]["guardian_title"],
            "domain": packet["spirit"]["dominant"],
            "blessing": packet["spirit"].get("power", ""),
            "bond_blessing": packet["behavior_analysis"].get("relationship_signature", ""),
        },
        "direction_request": {"humanoid_level": 0.88, "target_audience": "western_oc", "render_style": "western_fantasy_oc_2d"},
        "canon": {"locked_fields": {}, "reference_image_ids": []},
        "_source_schema": "guardian-packet-v0",
        "_source_gate": packet.get("validation", {}),
    }


def normalize_input(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("schema_version") == "director-input-v1":
        data = dict(raw)
        data.setdefault("personality_relationship_signals", [])
        data.setdefault("guardian_lore", {})
        data.setdefault("direction_request", {})
        data.setdefault("canon", {"locked_fields": {}, "reference_image_ids": []})
        data.setdefault("human_identity_direction", default_human_identity(
            data.get("mythic_dna", {}).get("source_traditions", []),
            data.get("mythic_dna", {}).get("culture_review_required", False),
        ))
        data["_source_schema"] = "director-input-v1"
        data["_source_gate"] = {}
        return data
    if raw.get("packet_meta", {}).get("schema_version") == "guardian-packet-v0":
        return normalize_guardian_packet(raw)
    raise ValueError("Expected director-input-v1 or guardian-packet-v0 input")


def score_signals(data: dict[str, Any], rules: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    confidence_weight = {"high": 3.0, "medium": 2.0, "low": 1.0}
    scored: list[dict[str, Any]] = []
    all_explicit = {
        compact(signal).casefold()
        for ev in data["evidence"]
        for signal in ev.get("signals", [])
        if compact(signal)
    }
    known_ids = {rule["id"] for rule in rules["signal_rules"]}
    open_signals = sorted(signal for signal in all_explicit if signal not in known_ids)
    support_text = " ".join(data.get("personality_relationship_signals", []) + [
        data["spirit"].get("dominant", ""), data["spirit"].get("statement", ""),
        data["spirit"].get("relationship_signal", ""), data["spirit"].get("contradiction", "")
    ]).casefold()

    for order, rule in enumerate(rules["signal_rules"]):
        score = 0.0
        ids: list[str] = []
        matched_terms: set[str] = set()
        contexts: set[str] = set()
        for ev in data["evidence"]:
            weight = confidence_weight.get(ev.get("confidence", "medium"), 2.0)
            text = " ".join([
                compact(ev.get("context")), compact(ev.get("observation")),
                compact(ev.get("action")), compact(ev.get("outcome"))
            ]).casefold()
            explicit = {compact(x).casefold() for x in ev.get("signals", [])}
            local_terms = {kw for kw in rule["keywords"] if kw.casefold() in text}
            if rule["id"] in explicit:
                score += weight * 2.0
                local_terms.add(rule["id"])
            if local_terms:
                score += weight + min(1.5, 0.25 * len(local_terms))
                ids.append(ev["id"])
                contexts.add(compact(ev.get("context")) or ev["id"])
                matched_terms.update(local_terms)
        support_matches = {kw for kw in rule["keywords"] if kw.casefold() in support_text}
        score += min(2.0, 0.4 * len(support_matches))
        matched_terms.update(support_matches)
        if score > 0:
            score += min(1.0, 0.25 * max(0, len(contexts) - 1))
            scored.append({
                "id": rule["id"], "score": round(score, 2), "evidence_ids": sorted(set(ids)),
                "matched_terms": sorted(matched_terms), "context_diversity": len(contexts),
                "rule_order": order, "rule": rule,
            })
    scored.sort(key=lambda x: (-x["score"], -x["context_diversity"], x["rule_order"]))
    if not scored:
        fallback = {
            "id": open_signals[0] if open_signals else "open_signal",
            "score": 1.0,
            "evidence_ids": [ev["id"] for ev in data["evidence"]],
            "matched_terms": open_signals,
            "context_diversity": len(data["evidence"]),
            "rule_order": 999,
            "rule": {
                "id": "open_signal", "meaning": data["spirit"]["statement"], "role": "证据特异的原创守护者",
                "power_logic": data["spirit"].get("power") or "把反复出现的行为方式转译为可见的行动规则",
                "shape_language": ["由证据动作导出的主线", "单一反向副线"], "silhouette_verb": "执行其独特行为",
                "costume": "依据行为功能建立的原创分层服装", "artifact": "记录该行为节奏的原创工具",
                "gaze": "视线明确指向当下触发物", "mouth_jaw": "口部张力与当前决定一致",
                "body": "重心、手部动作与证据中的行动方式一致", "camera": "50mm 眼平中景",
                "lighting": "确保脸、手和身份特征优先可读", "environment": "由证据情境推导的可行动空间"
            },
        }
        scored.append(fallback)
    return scored, open_signals


def trait_translation(trait: dict[str, Any]) -> str:
    description = compact(trait["description"])
    translations = {
        "ears": f"若被选入 Cat Residue，则以克制、可动且来源一致的耳部轮廓表达：{description}",
        "eyes": f"若被选入 Cat Residue，则在人形面部上保留眼色、眼形或左右差异：{description}",
        "coat_color": f"主要转译为角色配色与材质节奏，而非全身兽化：{description}",
        "marking": f"若被选入 Cat Residue，则转译为面部识别纹、发片分区或有限表面色块：{description}",
        "tail": f"若被选入 Cat Residue，则只保留一条参与表演且来源一致的尾部轮廓：{description}",
        "facial_signature": f"若被选入 Cat Residue，则在人形脸部结构中克制保留这一识别点：{description}",
        "fur_accent": f"若被选入 Cat Residue，则只在一个小区域保留毛发质感：{description}",
        "other": f"作为可核验的身份锚点保留，不扩写未观察细节：{description}",
    }
    return translations.get(trait["kind"], translations["other"])


def character_system_profile(rules: dict[str, Any], signal_id: str) -> dict[str, Any]:
    profiles = rules.get("character_system_by_signal", {})
    return profiles.get(signal_id, profiles.get("open_signal", {
        "archetype": "Guardian",
        "identity": "Evidence-Born Guardian",
        "motifs": ["owner-specific private sign"],
        "world_rule": "Repeated behavior creates a rule the world can recognize.",
        "materials": ["evidence-derived textile", "evidence-derived tool material"],
    }))


def select_cat_residue(traits: list[dict[str, Any]], primary_rule: dict[str, Any], evidence_ids: list[str]) -> dict[str, Any]:
    channel_by_kind = {
        "eyes": "face", "facial_signature": "face", "ears": "face",
        "tail": "movement", "coat_color": "surface", "marking": "surface",
        "fur_accent": "surface", "other": "surface",
    }
    kind_priority = {
        "eyes": 0, "facial_signature": 1, "marking": 2, "coat_color": 3,
        "tail": 4, "ears": 5, "fur_accent": 6, "other": 7,
    }
    selected: list[dict[str, Any]] = []
    used_channels: set[str] = set()
    for trait in sorted(traits, key=lambda item: (kind_priority.get(item["kind"], 99), -item["confidence"], item["id"])):
        channel = channel_by_kind.get(trait["kind"], "surface")
        if channel in used_channels:
            continue
        selected.append({
            "channel": channel,
            "trait_id": trait["id"],
            "kind": trait["kind"],
            "application": trait["visual_translation"],
        })
        used_channels.add(channel)
        if len(selected) == 3:
            break
    if not selected:
        selected.append({
            "channel": "movement",
            "trait_id": "behavior-only",
            "kind": "behavioral",
            "application": f"仅通过“{primary_rule['silhouette_verb']}”的观看、退让、靠近与重心节奏保留猫科行为感；不发明外貌 Canon。",
        })
    return {
        "application_order": "Identity/Lore/Personality/Contradiction/Archetype/Silhouette/Costume first; Cat Residue last",
        "behavioral_residue": {
            "description": f"以“{primary_rule['gaze']}”和“{primary_rule['body']}”保留行为层猫科性；优先于耳、尾或毛发装饰。",
            "evidence_ids": evidence_ids,
            "priority": "highest",
        },
        "selected_visual_channels": selected,
        "decorative_stack_forbidden": ["cat ears + tail + fur + whiskers + claws", "full animal head", "generic furry body"],
        "first_read": "complete humanoid fantasy/RPG Guardian OC",
        "second_read": "subtle but unmistakable feline identity",
    }


def find_contradiction(scored: list[dict[str, Any]], data: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    present = {item["id"] for item in scored if item["score"] >= 3}
    for pair in rules["contradiction_pairs"]:
        if set(pair["signals"]).issubset(present):
            evidence_ids = sorted({eid for item in scored if item["id"] in pair["signals"] for eid in item["evidence_ids"]})
            return {"name": pair["name"], "two_truths": " and ".join(pair["signals"]), "visual_rule": pair["visual_rule"], "source": "derived_pair", "evidence_ids": evidence_ids}
    supplied = compact(data["spirit"].get("contradiction"))
    if supplied:
        return {"name": supplied, "two_truths": supplied, "visual_rule": "用主动作与一个反向副动作共同表达，不做左右善恶拼贴", "source": "supplied", "evidence_ids": sorted({eid for item in scored[:3] for eid in item["evidence_ids"]})}
    if len(scored) >= 2:
        evidence_ids = sorted(set(scored[0]["evidence_ids"] + scored[1]["evidence_ids"]))
        return {"name": f"{scored[0]['id']} / {scored[1]['id']}", "two_truths": f"{scored[0]['id']} and {scored[1]['id']}", "visual_rule": "让主要行动方向与次要保留方向同时可读，而不是把人格压成单一标签", "source": "derived_tension", "evidence_ids": evidence_ids}
    return {"name": "未确认矛盾轴", "two_truths": "one observed truth with a restrained unresolved counter-direction", "visual_rule": "不发明矛盾；只保留轻微姿态反向以避免僵硬", "source": "uncertain", "evidence_ids": scored[0]["evidence_ids"] if scored else []}


def field_controls(stage: str, traits: list[dict[str, Any]], data: dict[str, Any]) -> list[dict[str, Any]]:
    concept_state = "CONTROLLED" if stage == "explore" else "LOCKED"
    design_state = "CONTROLLED" if stage in {"explore", "define"} else "LOCKED"
    scene_state = "FREE" if stage in {"explore", "define"} else "CONTROLLED"
    human_identity = resolve_human_identity(data)
    human_state = "LOCKED" if human_identity["resolved_for_canon"] else "DERIVED"
    human_priority = "P0" if human_identity["resolved_for_canon"] else "P1"
    controls = [
        {"path": "design_principle", "mutability": "LOCKED", "priority": "P0", "reason": "Soul-first V2 产品定义"},
        {"path": "humanoid_level", "mutability": "LOCKED", "priority": "P0", "reason": "强类人产品定义", "bounds": [0.8, 0.95]},
        {"path": "character_design.render_style", "mutability": "LOCKED", "priority": "P0", "reason": "用户确认的视觉媒介；项目默认 Western fantasy/RPG OC 2D"},
        {"path": "preserved_cat_traits", "mutability": "DERIVED", "priority": "P0", "reason": "完整照片身份记录；不等于全部同时可视化"},
        {"path": "cat_residue", "mutability": "LOCKED", "priority": "P0", "reason": "角色完成后才应用的一至三个选择性猫科通道"},
        {"path": "human_identity_direction", "mutability": human_state, "priority": human_priority, "reason": "已明确的人类族裔/外貌方向锁定；未明确时仅保留来源上下文并等待解析"},
        {"path": "hard_constraints.myth_replication", "mutability": "LOCKED", "priority": "P0", "reason": "文化与原创性边界"},
        {"path": "evidence_chain", "mutability": "DERIVED", "priority": "P1", "reason": "仅随源证据重算"},
        {"path": "distinction_fingerprint", "mutability": "DERIVED", "priority": "P1", "reason": "防止同 Spirit 角色趋同"},
        {"path": "personality_pattern", "mutability": "DERIVED", "priority": "P1", "reason": "从行为证据形成稳定人格模式"},
        {"path": "core_contradiction", "mutability": "DERIVED", "priority": "P1", "reason": "高权重的 two truths 张力"},
        {"path": "guardian_identity", "mutability": concept_state, "priority": "P1", "reason": "Identity-first 原创角色身份"},
        {"path": "lore", "mutability": concept_state, "priority": "P1", "reason": "视觉元素的因果来源"},
        {"path": "symbolic_motifs", "mutability": concept_state, "priority": "P1", "reason": "一至三个行为意义来源的 Motif"},
        {"path": "original_guardian_concept", "mutability": concept_state, "priority": "P1", "reason": f"{stage} 阶段的概念锁定策略"},
        {"path": "character_design", "mutability": design_state, "priority": "P1", "reason": f"{stage} 阶段的角色设计锁定策略"},
        {"path": "character_design.value_architecture", "mutability": "CONTROLLED", "priority": "P1", "reason": "用主值/中间值/暗锚组织服装与身份轮廓，避免浅色叠浅色或暗色糊成一团"},
        {"path": "facial_acting", "mutability": "CONTROLLED", "priority": "P1", "reason": "随 Story Beat 变化但必须符合人格"},
        {"path": "body_language", "mutability": "CONTROLLED", "priority": "P1", "reason": "随镜头变化但保持动作逻辑"},
        {"path": "story_beat", "mutability": "CONTROLLED", "priority": "P2", "reason": "允许在角色方法内更换事件"},
        {"path": "cinematography", "mutability": "CONTROLLED", "priority": "P2", "reason": "镜头服务叙事，不改变身份"},
        {"path": "cinematography.subject_occupancy_ratio", "mutability": "CONTROLLED", "priority": "P2", "reason": "默认 0.79–0.82，在角色存在感与叙事留白之间保持中间尺度", "bounds": [0.5, 0.9]},
        {"path": "cinematography.headroom_ratio", "mutability": "CONTROLLED", "priority": "P2", "reason": "默认 0.06–0.09，保护耳朵轮廓与画面呼吸感", "bounds": [0.04, 0.2]},
        {"path": "cinematography.visual_balance", "mutability": "CONTROLLED", "priority": "P2", "reason": "控制暗部面积、视觉重心、竞争焦点与轮廓干扰"},
        {"path": "environment.complexity_budget", "mutability": "CONTROLLED", "priority": "P1", "reason": "项目默认 minimal；只在明确叙事需要或用户要求时提高复杂度"},
        {"path": "environment.presentation_mode", "mutability": "CONTROLLED", "priority": "P1", "reason": "项目默认 game_character_select_stage；用户明确要求时可切换"},
        {"path": "environment.free_variation", "mutability": scene_state, "priority": "P3", "reason": "低风险新鲜度"}
    ]
    for trait in traits:
        controls.append({
            "path": f"preserved_cat_traits.{trait['id']}", "mutability": "LOCKED", "priority": "P0",
            "reason": "照片确认的身份特征"
        })
    for path in sorted(data.get("canon", {}).get("locked_fields", {})):
        controls.append({"path": path, "mutability": "LOCKED", "priority": "P0", "reason": "已批准 Canon"})
    return controls


def compile_brief(raw: dict[str, Any], rules: dict[str, Any] | None = None) -> dict[str, Any]:
    rules = rules or load_json(RULES_PATH)
    data = normalize_input(raw)
    stage = data["input_meta"]["stage"]
    scored, open_signals = score_signals(data, rules)
    primary = scored[0]
    primary_rule = primary["rule"]
    secondary = [item for item in scored[1:4] if item["score"] >= 2]
    contradiction = find_contradiction(scored, data, rules)

    raw_traits = data["subject"]["photo_identity"].get("traits", [])
    traits = [{
        "id": t["id"], "kind": t["kind"], "source_description": compact(t["description"]),
        "visual_translation": trait_translation(t), "confidence": float(t["confidence"]),
        "mutability": "LOCKED", "priority": "P0"
    } for t in raw_traits]
    references = data["subject"]["photo_identity"].get("reference_images", [])
    humanoid_target = float(data.get("direction_request", {}).get("humanoid_level", rules["humanoid"]["default"]))
    humanoid_target = max(rules["humanoid"]["minimum"], min(rules["humanoid"]["maximum"], humanoid_target))
    human_identity = resolve_human_identity(data)
    target_audience = data.get("direction_request", {}).get("target_audience", "western_oc")
    render_style = data.get("direction_request", {}).get("render_style", "western_fantasy_oc_2d")
    system_profile = character_system_profile(rules, primary["id"])
    cat_residue = select_cat_residue(traits, primary_rule, primary["evidence_ids"])
    cat_residue["human_visual_structure_percent"] = round(humanoid_target * 100, 1)
    cat_residue["feline_residue_percent"] = round((1.0 - humanoid_target) * 100, 1)
    subject_occupancy_ratio = float(data.get("direction_request", {}).get("subject_occupancy_ratio", 0.81))
    subject_occupancy_ratio = max(0.5, min(0.9, subject_occupancy_ratio))
    headroom_ratio = float(data.get("direction_request", {}).get("headroom_ratio", 0.075))
    headroom_ratio = max(0.04, min(0.2, headroom_ratio))
    background_complexity = data.get("direction_request", {}).get("background_complexity", "minimal")
    background_profiles = {
        "minimal": {"primary_architectural_motifs_max": 1, "material_families_max": 3, "decorative_props_max": 0, "background_people_max": 0, "detail": "背景细节密度约为角色的三分之一或更低", "contrast": "背景局部对比显著低于脸、眼、手、Artifact 与身份轮廓"},
        "restrained": {"primary_architectural_motifs_max": 2, "material_families_max": 4, "decorative_props_max": 1, "background_people_max": 0, "detail": "背景细节密度不超过角色的一半", "contrast": "背景局部对比低于角色主要识别区"},
        "narrative": {"primary_architectural_motifs_max": 3, "material_families_max": 5, "decorative_props_max": 3, "background_people_max": 1, "detail": "仅为 Story Beat 增加必要信息", "contrast": "叙事触发物可有次级对比，但不得形成第二主角"},
        "detailed": {"primary_architectural_motifs_max": 5, "material_families_max": 7, "decorative_props_max": 6, "background_people_max": 2, "detail": "允许丰富场景但保持清晰层级", "contrast": "背景峰值对比仍不得超过主角脸与 Artifact"},
    }
    background_profile = background_profiles.get(background_complexity, background_profiles["minimal"])
    background_presentation = data.get("direction_request", {}).get("background_presentation", "game_character_select_stage")
    presentation_profiles = {
        "game_character_select_stage": {
            "setting": "非写实地点的 2D 游戏角色选择舞台",
            "grounding": "浅圆形抬高地台、干净边缘与接触阴影；不做复杂地砖或镜面地面",
            "backdrop_fields": "两到三个取自角色配色的宽幅纵向/错位明度色场",
            "identity_motif": "两段大型、不闭合、错位的结构弧围合剪影；不得闭合成头后光环、圣门或魔法阵",
            "atmospheric_layer": "一层低对比、低频率的云雾或远景岩体/城市剪影，只提供纵深",
            "artifact_response": "Artifact 发出一条细响应线，连接结构弧上的单个小节点；最多少量无文字刻度",
        },
        "graphic_field": {
            "setting": "无地点感的角色档案图形色场",
            "grounding": "仅保留接触阴影或极浅地面切面",
            "backdrop_fields": "两到三个宽幅平面色块或渐变",
            "identity_motif": "一个由 Spirit 方法生成的原创平面图形，不包围头部",
            "atmospheric_layer": "无具象远景，仅低频明度变化",
            "artifact_response": "一条极简能力轨迹，不含界面面板",
        },
        "minimal_diorama": {
            "setting": "一个被压缩的浅景深空间切片",
            "grounding": "小型地台或单一地面平面",
            "backdrop_fields": "低对比建筑大面",
            "identity_motif": "一个可行动的空间边界或目的地",
            "atmospheric_layer": "单层低细节环境暗示",
            "artifact_response": "Artifact 与必要触发物发生一次可见互动",
        },
        "narrative_splash": {
            "setting": "服务明确 Story Beat 的叙事场景",
            "grounding": "由动作与环境接触决定",
            "backdrop_fields": "用大明度组块组织环境",
            "identity_motif": "环境线条与 VFX 指向角色行动",
            "atmospheric_layer": "允许一到两层叙事远景但保持主体优先",
            "artifact_response": "Artifact 直接作用于触发物或 implied_next",
        },
    }
    presentation_profile = presentation_profiles.get(background_presentation, presentation_profiles["game_character_select_stage"])
    style_profiles = {
        "western_fantasy_oc_2d": {
            "direction": "polished 2D Western fantasy/RPG original-character illustration for US OC, D&D and TTRPG audiences; identity-first and lore-driven design; readable silhouette; confident shape masses; restrained materials; expressive human facial structure; East Asian game-art precision may inform finish without creating an anime cat-person template",
            "negative": ["generic anime cat girl", "neko boy", "kawaii cat ears", "oversized anime eyes", "generic JRPG character", "cosplay aesthetic", "photorealism", "3D CGI", "PBR materials", "game-engine screenshot", "glossy doll face"],
        },
        "western_painterly": {
            "direction": "painterly 2D Western fantasy OC concept art with readable shape design, grounded materials, lore-driven costume logic, expressive human facial acting, and no franchise imitation",
            "negative": ["generic anime cat girl", "neko boy", "generic JRPG character", "photorealism", "3D CGI", "PBR materials", "game-engine screenshot"],
        },
        "2d_anime_oc": {
            "direction": "polished hand-drawn 2D anime OC illustration; clean varied line art; flat local color; two- or three-step cel shading; graphic hair locks and fur tufts; simplified 2D painted background",
            "negative": ["photorealism", "3D CGI", "PBR materials", "game-engine screenshot", "Unreal render", "Octane render", "realistic skin pores", "subsurface scattering", "glossy doll face", "volumetric cinematic haze", "photographic bokeh"],
        },
        "2d_painterly": {
            "direction": "clearly illustrated 2D painterly character art with visible drawn shapes, controlled brushwork, simplified materials, and no 3D-render look",
            "negative": ["photorealism", "3D CGI", "PBR materials", "game-engine screenshot", "glossy doll face"],
        },
        "stylized_3d": {
            "direction": "stylized 3D character rendering with simplified materials and non-photoreal proportions",
            "negative": ["photoreal skin", "live-action human", "uncanny realistic doll face"],
        },
        "custom": {
            "direction": compact(data.get("direction_request", {}).get("variation_note")) or "user-defined rendering style",
            "negative": [],
        },
    }
    style_profile = style_profiles.get(render_style, style_profiles["western_fantasy_oc_2d"])

    lore = data.get("guardian_lore", {})
    title = compact(lore.get("title")) or system_profile["identity"]
    best_ev = next((ev for ev in data["evidence"] if ev["id"] in primary["evidence_ids"]), data["evidence"][0])
    trigger = compact(best_ev.get("context")) or compact(best_ev["observation"])
    action = compact(best_ev.get("action")) or compact(best_ev["observation"])
    outcome = compact(best_ev.get("outcome")) or "下一步尚未发生，选择仍然可见"
    trait_phrases = [t["visual_translation"] for t in traits]
    residue_phrases = [item["application"] for item in cat_residue["selected_visual_channels"]]
    identity_uncertainties = []
    if len(traits) < 3:
        identity_uncertainties.append(f"只有 {len(traits)} 个结构化照片身份锚点；生成可探索，但不得晋升 Canon。")
    if not references:
        identity_uncertainties.append("未提供身份参考图；后续一致性只能依赖文字锚点。")

    evidence_chain = []
    for item in [primary] + secondary[:2]:
        rule = item["rule"]
        evidence_chain.append({
            "evidence_ids": item["evidence_ids"],
            "behavioral_pattern": f"在 {item['context_diversity']} 类情境中反复出现：{', '.join(item['matched_terms']) or item['id']}",
            "personality_relationship_signal": item["id"],
            "spirit_meaning": rule["meaning"],
            "mythic_dna": data["mythic_dna"]["meaning"],
            "original_concept": rule["role"],
            "visual_translation": f"{rule['silhouette_verb']}；{rule['artifact']}；{rule['body']}",
            "confidence_score": item["score"]
        })

    personality_pattern = {
        "statement": f"A stable {primary['id']} pattern expressed by “{action}”: {primary_rule['meaning']}; relationship mode: {data['spirit'].get('relationship_signal') or 'not yet supplied'}.",
        "evidence_ids": primary["evidence_ids"],
        "relationship_expression": data["spirit"].get("relationship_signal") or primary_rule["meaning"],
        "not_simple_labels": True,
    }
    core_contradiction = {
        "two_truths": contradiction["two_truths"],
        "name": contradiction["name"],
        "visual_rule": contradiction["visual_rule"],
        "source": contradiction["source"],
        "evidence_ids": contradiction["evidence_ids"],
        "weight": "high",
    }
    emotional_meaning = {
        "owner_meaning": data["spirit"].get("relationship_signal") or data["spirit"]["statement"],
        "protected_truth": data["spirit"].get("power") or primary_rule["meaning"],
        "evidence_ids": sorted({eid for item in evidence_chain for eid in item["evidence_ids"]}),
    }
    guardian_identity = {
        "title": title,
        "identity_statement": f"{title} — an original {system_profile['archetype']} whose {primary_rule['role']} method protects {emotional_meaning['protected_truth']}.",
        "protected_subject": emotional_meaning["protected_truth"],
        "world_function": primary_rule["power_logic"],
        "not_a_job_label": True,
    }
    archetype_role = {
        "archetype": system_profile["archetype"],
        "narrative_function": primary_rule["power_logic"],
        "not_a_personality_label": True,
        "open_library": True,
    }
    symbolic_motifs = [{
        "motif": motif,
        "meaning": f"Expresses {primary_rule['meaning']} through {primary_rule['power_logic']}; never decorative or a copied sacred emblem.",
        "evidence_ids": primary["evidence_ids"],
    } for motif in system_profile["motifs"][:3]]
    worldbuilding = {
        "world_rule": system_profile["world_rule"],
        "guardian_function": primary_rule["power_logic"],
        "social_read": f"Other beings understand {title} as a {system_profile['archetype']} who makes “{primary_rule['meaning']}” actionable rather than ceremonial.",
    }
    lore_v2 = {
        "why_exists": f"It came into being because the repeated pattern “{action}” revealed a reliable way to protect {emotional_meaning['protected_truth']}.",
        "protects": emotional_meaning["protected_truth"],
        "belongs_to": system_profile["world_rule"],
        "symbol_causality": [f"{item['motif']}: {item['meaning']}" for item in symbolic_motifs] + [f"{primary_rule['artifact']}: externalizes the method {primary_rule['power_logic']}"],
        "defining_pattern": f"{action} → {outcome}",
        "minimum_viable": True,
    }

    palette = [t["source_description"] for t in traits if t["kind"] in {"eyes", "coat_color", "marking"}]
    palette += ["深中性色用于压低背景", "单一叙事强调色用于触发物或 Artifact"]
    recognition = residue_phrases + [
        f"黑色剪影能读为“{primary_rule['silhouette_verb']}”", primary_rule["artifact"], title
    ]
    myth_prohibited = [compact(x) for x in data["mythic_dna"].get("prohibited_literal_elements", []) if compact(x)]
    hard_constraints = list(rules["hard_constraints"])
    hard_constraints.extend(f"do not copy: {item}" for item in myth_prohibited)
    hard_constraints.extend(human_identity["anti_stereotype_constraints"])
    if render_style == "2d_anime_oc":
        hard_constraints.append("render as genuine 2D anime OC illustration; no photorealistic or 3D/PBR drift")
    if render_style in {"western_fantasy_oc_2d", "western_painterly"}:
        hard_constraints.append("render as a lore-driven Western fantasy/RPG original character for US OC/TTRPG audiences; no generic anime cat-person template")
    if background_complexity == "minimal":
        hard_constraints.append("minimal restrained background: one architectural motif, no decorative props or background people, no high-frequency texture")
    if background_presentation == "game_character_select_stage":
        hard_constraints.append("present on a premium 2D game character-select stage: shallow circular platform, broad palette fields, incomplete offset arcs, subdued atmospheric layer, and one Artifact response line; no literal room, complete halo, sacred gateway, dense HUD, or readable UI")
    hard_constraints = list(dict.fromkeys(hard_constraints))

    distinction = {
        "primary_signal": {"id": primary["id"], "score": primary["score"], "evidence_ids": primary["evidence_ids"]},
        "secondary_signals": [{"id": x["id"], "score": x["score"], "evidence_ids": x["evidence_ids"]} for x in secondary],
        "open_extension_signals": open_signals,
        "contradiction": contradiction,
        "axes": {
            "approach_recovery": action,
            "spatial_choice": compact(best_ev.get("context")) or "由主证据场景决定",
            "relationship_mode": data["spirit"].get("relationship_signal", "未提供"),
            "temporal_ritual": next((compact(ev.get("context")) for ev in data["evidence"] if any(k in compact(ev).casefold() for k in ["night", "morning", "夜", "清晨"])), "未确认"),
            "strategy": primary_rule["power_logic"],
            "silhouette": primary_rule["silhouette_verb"],
            "motif_family": [item["motif"] for item in symbolic_motifs],
            "owner_specific": [f"{ev['id']}: {compact(ev['observation'])}" for ev in data["evidence"][:3]],
        },
        "unlike_same_spirit": f"即使同样被称为“{data['spirit']['dominant']}”，该角色以“{primary_rule['silhouette_verb']}”和“{primary_rule['artifact']}”表达，而不是套用通用谨慎姿态。"
    }

    owner_anchors = [{
        "evidence_id": ev["id"],
        "recognizable_truth": compact(ev["action"]) or compact(ev["observation"]),
        "visual_or_narrative_echo": f"{primary_rule['silhouette_verb']} / {primary_rule['artifact']} / {compact(ev.get('outcome')) or 'held choice'}",
    } for ev in data["evidence"][:3]]
    personal_resonance = {
        "owner_recognition_anchors": owner_anchors,
        "swap_test": "fails_by_design: replacing the cat would invalidate the cited evidence sequence, contradiction, private symbol, and behavior-led acting",
        "private_symbol": f"{system_profile['motifs'][0]} keyed to evidence {primary['evidence_ids'][0] if primary['evidence_ids'] else 'unresolved'}",
        "ears_tail_removal_test": True,
        "owner_truth_test": True,
    }
    distinctiveness = {
        "identity": guardian_identity["identity_statement"],
        "lore": lore_v2["defining_pattern"],
        "contradiction": core_contradiction["two_truths"],
        "silhouette": primary_rule["silhouette_verb"],
        "motif": [item["motif"] for item in symbolic_motifs],
        "owner_specific": owner_anchors,
        "anti_template_actions": ["vary body type and age impression", "vary posture and costume construction", "vary material, prop and motif family", "reject repeated white-hair/cloak/glowing-eyes/magical-weapon/cat-ear/moon defaults"],
    }
    contradiction_score = 8 if contradiction["source"] != "uncertain" else 5
    internal_scores = {
        "behavior_fidelity": min(10, 7 + min(3, len(primary["evidence_ids"]))),
        "personality_specificity": 8 if primary["evidence_ids"] else 6,
        "contradiction_strength": contradiction_score,
        "identity_originality": 8,
        "lore_coherence": 8,
        "symbolic_coherence": 8,
        "silhouette_distinctiveness": 8,
        "visual_storytelling": 8,
        "feline_subtlety": 9 if 1 <= len(cat_residue["selected_visual_channels"]) <= 3 else 4,
        "personal_resonance": 8 if len(owner_anchors) >= 2 else 6,
        "genericness_risk": 2,
    }
    internal_scores["retry_required"] = bool(
        internal_scores["personal_resonance"] < 7
        or internal_scores["identity_originality"] < 7
        or internal_scores["genericness_risk"] > 4
    )
    internal_scores["retry_scope"] = "character design layer once; preserve evidence and LOCKED identity fields" if internal_scores["retry_required"] else "none"

    brief: dict[str, Any] = {
        "schema_version": "guardian-visual-brief-v1",
        "brief_meta": {
            "id": data["input_meta"]["id"], "subject_name": data["subject"]["display_name"],
            "stage": stage, "rules_version": rules["version"], "source_schema": data["_source_schema"],
            "deterministic_seed": int(hashlib.sha256(data["input_meta"]["id"].encode()).hexdigest()[:8], 16)
        },
        "design_principle": "Design the soul first. Design the character second. Add the cat last.",
        "evidence_chain": evidence_chain,
        "personality_pattern": personality_pattern,
        "core_contradiction": core_contradiction,
        "emotional_meaning": emotional_meaning,
        "guardian_identity": guardian_identity,
        "archetype_role": archetype_role,
        "lore": lore_v2,
        "worldbuilding": worldbuilding,
        "symbolic_motifs": symbolic_motifs,
        "identity_translator": {
            "body_model": "upright strongly humanoid fantasy/RPG OC; humanlike torso, arms, hands, legs and stance; feline residue added only after character design",
            "face_model": "expressive human facial structure with readable brows, cheeks, mouth and jaw; selected subtle feline residue only; no generic anime face or heavy animal muzzle",
            "trait_translations": trait_phrases,
            "reference_images": references,
            "uncertainties": identity_uncertainties
        },
        "humanoid_level": {
            "target": humanoid_target,
            "allowed_range": [rules["humanoid"]["minimum"], rules["humanoid"]["maximum"]],
            "anatomy_contract": rules["humanoid"]["required_anatomy"]
        },
        "human_identity_direction": human_identity,
        "preserved_cat_traits": traits,
        "cat_residue": cat_residue,
        "distinction_fingerprint": distinction,
        "mythic_dna": {
            "deep_meaning": data["mythic_dna"]["meaning"],
            "motifs": data["mythic_dna"].get("motifs", []),
            "source_traditions": [x for x in data["mythic_dna"].get("source_traditions", []) if x],
            "abstraction_rule": "Ancient meaning, original character, contemporary design; retain relationship and transformation logic only.",
            "literal_elements_prohibited": myth_prohibited,
            "culture_review_required": data["mythic_dna"].get("culture_review_required", False)
        },
        "mythic_resonance": {
            "placement": "after original Guardian identity and lore",
            "lineage": data["mythic_dna"].get("source_traditions", []),
            "allowed_uses": ["motif inspiration", "archetypal resonance", "symbolic lineage", "narrative pattern", "cultural reference"],
            "forbidden_equation": "Guardian = specific deity",
        },
        "original_guardian_concept": {
            "title": title, "role": system_profile["archetype"], "core_verb": primary_rule["silhouette_verb"],
            "power_logic": primary_rule["power_logic"],
            "blessing": lore.get("blessing", ""),
            "originality_statement": "角色从行为表达方式生成；不以任何传统神话人物的身体、服饰或圣物作为模板。"
        },
        "character_design": {
            "render_style": {"id": render_style, "direction": style_profile["direction"], "negative": style_profile["negative"]},
            "target_audience": target_audience,
            "shape_language": primary_rule["shape_language"],
            "silhouette": f"Silhouette-first strong humanoid fantasy form; core verb “{primary_rule['silhouette_verb']}”; {contradiction['visual_rule']}; readable in flat black before face, color, or cat residue.",
            "silhouette_system": {
                "body_proportion": "human fantasy/RPG proportion chosen for the role, not mascot or generic anime proportion",
                "stance": primary_rule["body"],
                "shoulder_and_mass": primary_rule["shape_language"],
                "weight_distribution": primary_rule["body"],
                "head_shape": "human head silhouette with only selected Cat Residue",
                "prop_silhouette": primary_rule["artifact"],
                "negative_space": f"open gaps support the verb {primary_rule['silhouette_verb']} and the contradiction {contradiction['name']}",
            },
            "costume": {
                "system": primary_rule["costume"],
                "base_layer": "贴合动作的人形基础层，不模拟完整动物躯干",
                "movement_layer": primary_rule["costume"],
                "identity_accents": residue_phrases,
                "focal_detail": primary_rule["artifact"],
                "logic": f"Every layer exists to support {primary_rule['power_logic']}; no accessory is accepted only because it looks fantasy."
            },
            "artifact_symbol": {
                "name": primary_rule["artifact"],
                "meaning": primary_rule["power_logic"],
                "use_in_scene": "由双手实际操作，并对 Story Beat 的触发作出可见反应",
                "not_a_mythic_relic": True
            },
            "palette": palette,
            "material_language": system_profile["materials"],
            "value_architecture": "建立主值、中间支撑值与受控最暗锚点；浅色毛发/服装用内层、腰带、腿部、鞋靴、Harness 或 Artifact 增加中深色骨架，暗色角色则为脸与双手保留清晰亮窗",
            "palette_relationship": "背景借用角色一到两种颜色并降低饱和度；沿头、耳、肩、手、衣摆、腿和尾巴持续保持明暗或冷暖分离，不改变真实猫身份色来迁就背景",
            "recognition_anchors": recognition
        },
        "facial_acting": {
            "intention": f"在行动前让“{primary_rule['meaning']}”变得可读",
            "eyes_gaze": primary_rule["gaze"],
            "mouth_jaw": primary_rule["mouth_jaw"],
            "brows_cheeks": "眉部与颊部承担主要微表情，避免用夸张兽口替代表演",
            "intensity": "subtle-to-medium; readable at medium shot"
        },
        "body_language": {
            "intention": primary_rule["power_logic"],
            "pose": primary_rule["body"],
            "weight_distribution": primary_rule["body"],
            "line_of_action": f"主线表达“{primary_rule['silhouette_verb']}”，副线反向承载“{contradiction['name']}”",
            "hands": f"一只手正在操作{primary_rule['artifact']}，另一只手回应触发物或保持空间关系",
            "tail": "尾巴作为次级表演线，呼应重心与情绪，不做无意义装饰曲线",
            "silhouette_read": primary_rule["silhouette_verb"]
        },
        "story_beat": {
            "before": "触发发生前，角色在日常空间中维持未介入的稳定节奏。",
            "trigger": f"{trigger}：{compact(best_ev['observation'])}",
            "now": f"画面截取其正在“{action}”的决策瞬间，Artifact 刚开始响应。",
            "emotional_shift": f"从未定状态转向“{primary_rule['meaning']}”。",
            "implied_next": outcome
        },
        "cinematography": {
            "shot": data.get("direction_request", {}).get("shot_type", "medium-full character shot"),
            "lens": primary_rule["camera"],
            "camera_angle": "非崇拜式斜侧视角，保持脸、手、重心与猫身份锚点同时可读",
            "composition": f"镜头后拉，人物约占画面高度 {subject_occupancy_ratio:.0%}，头顶留白约 {headroom_ratio:.0%}；耳朵、衣摆、手、Artifact 与尾巴周围保留呼吸空间；触发物与下一步方向形成清晰三角关系",
            "subject_occupancy_ratio": subject_occupancy_ratio,
            "headroom_ratio": headroom_ratio,
            "depth_plan": "前景提供触发线索，中景为角色行动，后景显示下一步空间",
            "negative_space": "留在视线和 implied_next 的方向",
            "focal_hierarchy": "唯一一级焦点是 Guardian 的脸与眼神；动作手/Artifact 为二级；环境为三级；背景人物与人形剪影默认关闭",
            "visual_balance": "采用非对称平衡：暗部不得以孤立大色块压在单侧，视觉重心保持在 Guardian 附近；通过门框、服装节奏、地面反射和小型环境形状分散支撑重量，不制造第二焦点"
        },
        "lighting": {
            "key": primary_rule["lighting"],
            "fill": "柔和中性填充，避免眼色、花纹和手部沉入阴影",
            "identity_readability": "耳轮廓、双眼、面部识别点、尾巴和主要花纹均需可辨",
            "meaning": primary_rule["meaning"]
        },
        "environment": {
            "setting": f"{presentation_profile['setting']}；以“{primary_rule['environment']}”提供情绪和行动含义而非复制完整地点",
            "presentation_mode": background_presentation,
            "presentation_design": {
                "grounding": presentation_profile["grounding"],
                "backdrop_fields": presentation_profile["backdrop_fields"],
                "identity_motif": presentation_profile["identity_motif"],
                "atmospheric_layer": presentation_profile["atmospheric_layer"],
                "artifact_response": presentation_profile["artifact_response"],
            },
            "story_affordances": ["至多一个必要触发物或空间边界", "明确的 implied_next 方向", "其余叙事信息由光色与留白承担"],
            "subject_hierarchy": "背景细节、边缘密度、饱和度与局部对比均低于脸、眼、手、Artifact 和身份轮廓",
            "complexity_budget": {"mode": background_complexity, **{k: v for k, v in background_profile.items() if k.endswith("_max")}},
            "detail_density": background_profile["detail"],
            "contrast_ceiling": background_profile["contrast"],
            "prohibited_clutter": ["装饰性植物", "挂画", "家具陈列", "多余门窗框", "密集地砖", "大理石花纹", "镜面反射", "细碎材质纹理", "非必要小道具"],
            "free_variation": ["大色面之间的轻微色温变化", "柔和阴影方向", "低频明度渐变"]
        },
        "narrative_moment": f"{title}在“{trigger}”发生后，以“{primary_rule['silhouette_verb']}”的姿态执行“{action}”，观众能预感下一步是“{outcome}”。",
        "visual_storytelling": {
            "principle": "Do not decorate. Explain.",
            "element_rationales": {
                "silhouette": f"communicates {primary_rule['silhouette_verb']} and the contradiction {contradiction['name']}",
                "costume": f"supports the method {primary_rule['power_logic']}",
                "artifact": f"makes {primary_rule['power_logic']} physically actionable",
                "motifs": [f"{item['motif']} derives from evidence {', '.join(item['evidence_ids'])}" for item in symbolic_motifs],
                "materials": f"{', '.join(system_profile['materials'])} express use, history, and world function rather than luxury decoration",
            },
            "decoration_rejected": ["ornament without behavior/lore cause", "random magical weapon", "meaningless glow", "accessory stacking"],
        },
        "personal_resonance": personal_resonance,
        "distinctiveness": distinctiveness,
        "internal_scores": internal_scores,
        "hard_constraints": hard_constraints,
        "field_controls": field_controls(stage, traits, data),
        "prompt_fields": {},
        "prompt_layers": {},
        "compiled_prompt": {},
        "automation": {},
        "preflight_qa": {}
    }

    identity_layer = [
        f"{humanoid_target:.2f} humanoid original Guardian OC, upright biped, humanlike torso, arms, functional hands and legs",
        guardian_identity["identity_statement"],
        personality_pattern["statement"],
        f"core contradiction: {core_contradiction['two_truths']}",
        "complete humanlike fantasy character before feline residue",
        human_identity["casting_statement"],
    ]
    if not residue_phrases:
        identity_layer.append("cat identity details are unresolved; do not invent canon markings")
    prompt_fields = {
        "guardian_identity": guardian_identity["identity_statement"],
        "core_personality": personality_pattern["statement"],
        "core_contradiction": core_contradiction["two_truths"],
        "archetype": f"{archetype_role['archetype']}: {archetype_role['narrative_function']}",
        "lore_context": f"{lore_v2['why_exists']} World rule: {worldbuilding['world_rule']}",
        "silhouette": brief["character_design"]["silhouette"],
        "body_language": f"{brief['body_language']['pose']}; weight: {brief['body_language']['weight_distribution']}; line: {brief['body_language']['line_of_action']}",
        "costume_logic": brief["character_design"]["costume"]["logic"] + " " + brief["character_design"]["costume"]["system"],
        "symbolic_motifs": [f"{item['motif']}: {item['meaning']}" for item in symbolic_motifs],
        "props": f"{primary_rule['artifact']}: {primary_rule['power_logic']}",
        "feline_residue": [cat_residue["behavioral_residue"]["description"], *residue_phrases],
        "facial_direction": f"{primary_rule['gaze']}; {primary_rule['mouth_jaw']}; expressive human facial structure, no generic anime face",
        "material_language": system_profile["materials"],
        "visual_tone": "numinous, mysterious, protective, restrained, personal, narratively coherent; never cosplay or decorative cat-person styling",
    }
    brief["prompt_fields"] = prompt_fields
    layers = {
        "identity": identity_layer,
        "meaning_mythic_dna": [emotional_meaning["owner_meaning"], primary_rule["power_logic"], "original Guardian identity precedes Mythic Resonance", data["mythic_dna"]["meaning"], "ancient meaning without literal myth replication"],
        "visual_design": [style_profile["direction"], prompt_fields["archetype"], prompt_fields["lore_context"], prompt_fields["silhouette"], prompt_fields["costume_logic"], prompt_fields["props"], "; ".join(prompt_fields["symbolic_motifs"]), "; ".join(prompt_fields["material_language"]), "; ".join(palette), brief["character_design"]["value_architecture"], brief["character_design"]["palette_relationship"], "CAT RESIDUE APPLIED LAST: " + "; ".join(prompt_fields["feline_residue"])],
        "acting": [primary_rule["gaze"], primary_rule["mouth_jaw"], primary_rule["body"], brief["body_language"]["hands"]],
        "story_beat": list(brief["story_beat"].values()),
        "cinematography": [primary_rule["camera"], brief["cinematography"]["composition"], brief["cinematography"]["negative_space"], brief["cinematography"]["focal_hierarchy"], brief["cinematography"]["visual_balance"]],
        "scene": [brief["environment"]["setting"], *brief["environment"]["presentation_design"].values(), primary_rule["lighting"], brief["environment"]["subject_hierarchy"], brief["environment"]["detail_density"], brief["environment"]["contrast_ceiling"]],
        "constraints": hard_constraints + ["use only these selected Cat Residue channels: " + "; ".join(residue_phrases)] + ([human_identity["casting_statement"]] if human_identity["resolved_for_canon"] else [])
    }
    positive = "\n\n".join(f"[{name.upper()}]\n" + "; ".join(values) for name, values in layers.items())
    negative_items = [
        "quadruped cat", "pet wearing clothes", "mascot", "feral anatomy", "paws instead of hands",
        "heavy animal muzzle", "extra limbs", "deity cosplay", "named deity replica", "sacred symbol copy",
        "ritual pose", "worship scene", "frontal icon composition", "generic smile", "empty fashion pose",
        "background overpowering subject", "subject filling the entire frame", "cramped crop around ears, hands, coat or tail",
        "secondary person", "background human silhouette", "competing face", "isolated near-black peripheral blob", "one-sided visual weight", "silhouette tangency",
        "busy background", "decorative plants", "wall art", "furniture display", "ornaments", "repeated frames", "patterned marble", "dense floor tiles", "mirror-like reflections", "high-frequency texture noise",
        "literal furnished room", "foreground bystander", "complete halo behind head", "sacred gateway", "dense HUD", "readable interface text"
        , "generic anime cat girl", "neko boy", "kawaii cat ears", "cosplay aesthetic", "decorative tail without meaning",
        "oversized anime eyes", "generic white-haired fantasy character", "random magical weapon", "meaningless glowing symbols",
        "excessive accessories", "overdesigned costume", "furry mascot", "chibi", "overly cute", "generic JRPG character",
        "direct copy of existing mythology characters", "direct copy of copyrighted characters"
    ] + myth_prohibited + style_profile["negative"]
    negative = ", ".join(dict.fromkeys(negative_items))
    prompt_hash = hashlib.sha256((positive + "\n" + negative).encode("utf-8")).hexdigest()[:16]
    brief["prompt_layers"] = layers
    brief["compiled_prompt"] = {"positive_prompt": positive, "negative_prompt": negative, "prompt_hash": prompt_hash}

    candidate_count = {"explore": 6, "define": 4, "canon": 3, "production": 2}[stage]
    variation_axes = {
        "explore": ["role implementation", "silhouette family", "artifact mechanism", "costume architecture", "story context"],
        "define": ["costume implementation", "artifact detail", "facial intensity", "shot"],
        "canon": ["acting intensity", "shot", "light direction"],
        "production": ["story beat", "shot", "atmosphere"]
    }[stage]
    brief["automation"] = {
        "candidate_generation": {"count": candidate_count, "variation_axes": variation_axes, "preserve_locked_fields": True},
        "character_design_retry": {"max_retries": 1, "trigger": "personal_resonance < 7 or identity_originality < 7 or genericness_risk > 4", "repair_scope": "Identity/Lore/Contradiction/Silhouette/Motif/Costume only; preserve evidence and P0 identity"},
        "seed_policy": "Keep seed stable within a targeted retry; change seed only after prompt repair fails once.",
        "image_qa_checks": [
            {"id": "identity_consistency", "priority": "P0", "weight": 8},
            {"id": "humanoid_degree", "priority": "P0", "weight": 8},
            {"id": "feline_subtlety_and_selected_residue", "priority": "P0", "weight": 7, "target": "one to three selected channels; behavioral residue first"},
            {"id": "human_representation_fidelity", "priority": "P0", "weight": 5, "applicable": human_identity["resolved_for_canon"]},
            {"id": "nonliteral_mythic_dna", "priority": "P0", "weight": 6},
            {"id": "render_style_fidelity", "priority": "P0", "weight": 7, "target": render_style},
            {"id": "western_oc_character_logic", "priority": "P1", "weight": 8, "target": "identity-first, lore-driven, personality-driven, silhouette-readable"},
            {"id": "identity_originality", "priority": "P1", "weight": 7},
            {"id": "character_recognizability", "priority": "P1", "weight": 6},
            {"id": "value_hierarchy_and_palette_separation", "priority": "P1", "weight": 3, "target": "three-value costume architecture; face/hands/Artifact and complete identity silhouette separate from the stage"},
            {"id": "facial_acting_and_gaze", "priority": "P1", "weight": 5},
            {"id": "body_weight_line_of_action", "priority": "P1", "weight": 5},
            {"id": "story_beat_readability", "priority": "P1", "weight": 5},
            {"id": "costume_symbol_consistency", "priority": "P1", "weight": 5},
            {"id": "personal_resonance", "priority": "P1", "weight": 8, "target": owner_anchors},
            {"id": "composition_balance_and_hierarchy", "priority": "P2", "weight": 3, "target": {"subject_occupancy_ratio": subject_occupancy_ratio, "headroom_ratio": headroom_ratio, "primary_focal_points": 1, "background_people_default": 0, "background_complexity": background_complexity, "background_presentation": background_presentation, "background_detail_ratio_max": 0.33 if background_complexity == "minimal" else None}},
            {"id": "canon_consistency", "priority": "P0", "weight": 2, "applicable": bool(data.get("canon", {}).get("locked_fields") or data.get("canon", {}).get("reference_image_ids"))},
            {"id": "artifact_and_hand_integrity", "priority": "P0", "weight": 2}
        ],
        "auto_selection": {
            "minimum_score": 82, "p0_minimum_each": 3, "score_scale": [0, 4],
            "hard_failures": ["wrong identity", "wrong rendering medium or 3D/photoreal drift when 2D is locked", "quadruped/pet body", "generic anime cat-person default", "more than three feline-residue channels", "extra limbs", "resolved human representation mismatch", "stereotyped ethnic exaggeration", "deity replica", "sacred-symbol misuse", "canon reference drift"],
            "tie_breakers": ["P0 identity subtotal", "story and acting subtotal", "lower retry count"]
        },
        "retry_policy": {
            "max_retries": 2 if stage in {"explore", "define"} else 3,
            "method": "Repair only failed CONTROLLED/FREE dimensions; repeat LOCKED/P0 clauses verbatim.",
            "stop_conditions": ["same hard failure twice", "retry budget exhausted", "culture or generation gate blocks output"]
        },
        "canon_policy": "A selected image remains a candidate until explicitly approved; approved identity, proportions, markings, palette, costume landmarks, artifact geometry and reference ID become LOCKED/P0."
    }

    checks = [
        {"id": "soul_first_order", "passed": brief["design_principle"].startswith("Design the soul first") and bool(brief["guardian_identity"] and brief["lore"] and brief["core_contradiction"]), "detail": "Identity/Lore/Contradiction exist before selected Cat Residue in the compiled design"},
        {"id": "humanoid_band", "passed": 0.8 <= humanoid_target <= 0.95, "detail": f"target={humanoid_target:.2f}; feline residue={cat_residue['feline_residue_percent']:.1f}%"},
        {"id": "humanlike_anatomy_contract", "passed": len(rules["humanoid"]["required_anatomy"]) >= 4, "detail": "upright torso/arms/hands/legs/face required"},
        {"id": "identity_anchor_handling", "passed": len(traits) >= 3 or bool(identity_uncertainties), "detail": f"{len(traits)} anchors; uncertainty is explicit"},
        {"id": "cat_residue_contract", "passed": 1 <= len(cat_residue["selected_visual_channels"]) <= 3 and 5 <= cat_residue["feline_residue_percent"] <= 20, "detail": f"{len(cat_residue['selected_visual_channels'])} selected visual channels; behavioral residue has highest priority"},
        {"id": "human_identity_handling", "passed": human_identity["resolved_for_canon"] or bool(human_identity["uncertainties"]), "detail": "resolved appearance is prompt-locked, or uncertainty is explicit"},
        {"id": "render_style_contract", "passed": render_style in style_profiles, "detail": f"render_style={render_style}; style prompt and negatives compiled"},
        {"id": "composition_bounds", "passed": 0.5 <= subject_occupancy_ratio <= 0.9 and 0.04 <= headroom_ratio <= 0.2, "detail": f"occupancy={subject_occupancy_ratio:.3f}; headroom={headroom_ratio:.3f}; project defaults are 0.79–0.82 / 0.06–0.09"},
        {"id": "background_complexity_contract", "passed": background_complexity in background_profiles, "detail": f"background_complexity={background_complexity}; explicit object/material/prop/person budgets compiled"},
        {"id": "background_presentation_contract", "passed": background_presentation in presentation_profiles, "detail": f"background_presentation={background_presentation}; grounding/fields/motif/atmosphere/Artifact response compiled"},
        {"id": "value_architecture_contract", "passed": bool(brief["character_design"]["value_architecture"] and brief["character_design"]["palette_relationship"]), "detail": "three-value costume hierarchy and character/background palette separation compiled"},
        {"id": "western_oc_logic", "passed": target_audience != "western_oc" or render_style in {"western_fantasy_oc_2d", "western_painterly", "custom"} or (render_style == "2d_anime_oc" and "render_style" in data.get("direction_request", {})), "detail": f"target_audience={target_audience}; identity/lore/personality/silhouette precede decoration; anime mode is allowed only when explicitly requested"},
        {"id": "personal_resonance", "passed": internal_scores["personal_resonance"] >= 7 and len(owner_anchors) >= 2, "detail": f"score={internal_scores['personal_resonance']}; owner anchors={len(owner_anchors)}"},
        {"id": "identity_originality", "passed": internal_scores["identity_originality"] >= 7, "detail": f"score={internal_scores['identity_originality']}"},
        {"id": "genericness_risk", "passed": internal_scores["genericness_risk"] <= 4, "detail": f"risk={internal_scores['genericness_risk']} (lower is better)"},
        {"id": "evidence_trace", "passed": all(x["evidence_ids"] for x in evidence_chain), "detail": f"{len(evidence_chain)} traced transformations"},
        {"id": "myth_abstraction", "passed": "named deity replica" in negative, "detail": "literal myth replication prohibited"},
        {"id": "acting_specificity", "passed": all(compact(brief["facial_acting"][k]) for k in ["eyes_gaze", "mouth_jaw"]), "detail": "eyes/gaze and mouth/jaw specified"},
        {"id": "story_temporality", "passed": all(compact(brief["story_beat"][k]) for k in ["before", "trigger", "now", "emotional_shift", "implied_next"]), "detail": "five beat fields present"},
        {"id": "prompt_builder_fields", "passed": len(prompt_fields) == 14 and all(prompt_fields.values()), "detail": "all 14 V2 Prompt Builder fields compiled"},
        {"id": "layered_prompt", "passed": len(layers) == 8, "detail": "all eight stable API prompt layers compiled from V2 fields"},
    ]
    source_gate = data.get("_source_gate", {})
    gate_blocked = bool(source_gate) and source_gate.get("generation_allowed") is False
    all_structural = all(check["passed"] for check in checks)
    if gate_blocked:
        status = "blocked_by_source_gate"
    elif len(traits) < 3:
        status = "needs_identity_evidence"
    else:
        status = "pass" if all_structural else "fail"
    brief["preflight_qa"] = {
        "status": status,
        "checks": checks,
        "image_qa_status": "pending_pixels",
        "source_generation_gate": source_gate,
        "unresolved": identity_uncertainties + human_identity["uncertainties"]
    }
    return brief


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="director-input-v1 or guardian-packet-v0 JSON")
    parser.add_argument("--output", "-o", type=Path, help="output JSON; stdout when omitted")
    args = parser.parse_args()
    brief = compile_brief(load_json(args.input))
    rendered = json.dumps(brief, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
