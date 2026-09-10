# CONTRIBUTING · 仓库纪律

> 本文件是「Symbiote vs Spore」整合包开发仓库的强制纪律，依据《整合包开发方案 v4》4.1–4.2 与《AI 协同开发工作流》第 5 节制定。任何提交（人工或 AI 生成）都必须遵守。

## 1. 分批添加纪律（方案 4.2）

模组**绝不一次性堆入**，按以下批次顺序推进，每批各占独立 commit：

1. 核心战斗层：Epic Fight + Weapons of Miracles（锁定 EF 系列版本）
2. 次核心层：**各占一批、单独验证**——Symbiote → Sword Soaring / EpicFight-Nightfall → Fungal Infection: Spore
3. 扩展层：同样各占一批——Saint's Dragons（含 GeckoLib + Mount Fix）→ Tinkers' Construct（含 Mantle + Tinkers Integration）→ RoadWeaver
4. 大型内容模组（Cataclysm → 暮色森林 → Alex's Caves → Iron's Spells → Epic Knights，世界生成 Terralith 须最先定型）
5. 性能优化栈
6. QoL 小模组

**每批添加后完整启动一次并进存档实测，验证过线才允许 commit**；AI 产物未实测不 commit。

## 2. Commit message 规范

格式：`type(scope): 描述 [模型批次]`

- `type` ∈ `feat`（新增内容/模组）/ `fix` / `chore`（仓库与工具）/ `docs` / `refactor` / `test` / `balance`（数值与魔改调整）
- `scope`：受影响面，如 `ef`、`spore`、`quests`、`kubejs`、`repo`、`perf`
- `[模型批次]`：AI 生成内容标注模型与复核状态，如 `[K3]`、`[glm5.3flash]`、`[qwen3.8flash+P11过审]`；纯人工写 `[manual]`。翻车按批次精确回滚，同时积累各模型一次通过率数据
- 示例：`feat(mods): 第二批 Symbiote 入包并完成键位实测 [K3]`

## 3. EF 版本锁定红线

Epic Fight 本体及全部附属（Impactful / Battle Arts / Resurrection / Indestructible / Epic Foes / Sword Soaring / Nightfall / WoM / CompatLink / EFMCompat 等）**全包统一锁定 20.14.x 系列，禁止单独升级任何一个**。

任何 EF 升级必须由人工决策，并触发全量武器动作回归测试后随单独 commit 落地。AI 模型提出"升级 EF 或某附属"一律拒绝。

## 4. jar 红线与模组管理

- 任何 `*.jar` 不得入库（`.gitignore` 已全局拦截）；模组只经 `packwiz curseforge install` / `packwiz modrinth install` 添加，删除用 `packwiz remove`
- `pack.toml` / `index.toml` / `mods/*.pw.toml` 记录精确文件版本；冻结顺序：EF 附属先行 → 内容模组随后 → 性能模组最后
- `config/`、`kubejs/`、`scripts/` 覆盖层与元数据同步版本化

## 5. 入库前校验

- B 级批量产物（EF capability JSON、战利品表、配方 JSON 等）入库前必跑：
  ```
  python tools/check_json.py
  ```
  默认校验 `config/openloader/data/` 与 `kubejs/data/` 下全部 JSON，全绿才允许 commit
- 物品 ID、配置键名一律以 `/kubejs hand`、`/ct hand`、F3+H 现场核实为准；未核实的 ID 视为占位符，不进版本库

## 6. 原版内容政策【待定】

决策落地（阶段⑤平衡实测）前：任何提交不得改动原版配方、数值与门控；阶段门控只锁模组内容。AI 提出的原版修改建议一律归入待办，不当场执行。
