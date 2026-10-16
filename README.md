# Guardian Visual Director Skill

可独立使用的 Guardian OC 视觉导演层，不要求 MOMO 外层仓库。V2 以 **“Design the soul first. Design the character second. Add the cat last.”** 为最高原则，承接现有 `guardian-packet-v0` 或完整照片/访谈输入，将证据转成面向美国 / 西方 OC、Fantasy、RPG、D&D 与 TTRPG 社区的强类人原创角色、分层生图提示词和自动质检合同。文化来源、地域、现代国别、族裔参考和实际外貌方向继续分别记录，避免用单一“人种”标签替代设计与来源判断。

## 在项目链路中的位置

```text
Interview / Photo / Behavior Evidence
  → Personality Pattern → Core Contradiction → Emotional Meaning
  → Guardian Identity → Archetype/Role → Lore/Worldbuilding → Motifs
  → Silhouette/Body Language → Costume/Props → selective Cat Residue
  → Mythic Resonance
  → Guardian Visual Director Skill
  → Structured Visual Brief + Layered Image Prompt
  → Image API candidates
  → Visual QA / auto-selection / bounded retry
  → Canon Reference
```

本 Skill 不改写上游 Spirit，也不把传统神话人物视觉复刻为猫。它先创造完整的原创 Guardian，再把 Mythic DNA 降到后置的“意义、关系、力量逻辑和叙事母题”共鸣层。默认视觉是欧美 Fantasy/RPG OC 的 2D 角色设计；日系完成度可以用于精度控制，但不再作为猫耳角色模板。

Cat Residue 默认只选择 1–3 个视觉通道，行为残留优先于装饰残留。第一眼必须是完整的人形 Fantasy Guardian，第二眼才读出不可错认的猫科身份。

## 快速使用

```bash
python3 scripts/guardian_visual_director.py examples/synthetic-cat.input.json > /path/to/your-workspace/brief.json

python3 -B scripts/public_evals.py
```

需要 Python 3.10+；编译器只使用标准库，不需要 GPU、网络或 API Key。缺解释器时由 AI 说明官方安装来源、网络与空间影响，按使用者选择安装并复检，不静默安装。独立评测以全新虚构输入检查确定性、来源引用和身份/文化待审状态；若已安装 jsonschema 则额外检查输入和输出Schema，未安装如实报告未做该项，不自动下载。

## 目录

- `SKILL.md`：Codex 入口与不可违背的导演原则。
- `schemas/`：输入与 Structured Visual Brief 输出契约。
- `rules/`：可扩展的证据—意义—视觉规则种子，不是封闭词表。
- `references/`：导演规则、锁定策略、QA 与 API 接入说明。
- `scripts/`：可执行编译器和 eval harness。
- `examples/synthetic-cat.input.json`：全新虚构的端到端输入，无真实照片、问卷或本人故事。
- `scripts/public_evals.py`：不依赖项目输出或私人案例的合成检查；项目原有 tests 和 run_evals 不包含在独立公开包。
- `evals/`：结构化评分标准。

## 输出稳定性的来源

稳定性由字段级 mutability / priority、角色 Canon、参考图锚定、Personal Resonance / Genericness 内部评分和失败维度定向重试共同提供。若 Personal Resonance 或 Identity Originality 低于 7/10，或 Genericness Risk 高于 4/10，系统只重做一次角色设计层，不放松证据与身份锁定。Skill 本身不承诺随机生图绝对一致，也不会把未观察到的花纹写成 Canon。

## 安装与调用

将包放在自己选择的位置，使用能加载 SKILL.md 和操作本机文件的 AI，例如 Codex；其他 AI 宿主只保证能阅读说明，未实机验证自动发现。对 AI 说：“使用 Guardian Visual Director，把这份明确提供的猫行为证据整理为原创人形守护者 brief 和分层提示词，先检查环境。”真实资料放用户工作目录；首轮可用全新虚构的 synthetic-cat 样例。重定向目标目录须先存在；也可显式 --output 指定新文件，注意不要覆盖已有结果。

macOS Python 已验证，其他平台尚未实机验证。脚本离线产出JSON和提示词，不生成图片；图片生成费用、视觉质量与身份一致性均未由合成编译测试证明。输入中的未知外貌或文化方向保留待审，不能把演示素材当真实观察。

候选许可为 MIT，见 LICENSE；正式公开以本人确认本次文件与产物清单为准。独立公开白名单排除原项目 examples、tests、output、照片和业务知识库，源码仍在原登记主位置维护。
