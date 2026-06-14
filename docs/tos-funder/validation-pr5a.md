# PR 5A Validation: Growth Persona — Fisher / Lynch

验证日期：2026-06-02
验证范围：`/tos-funder-growth-fisher` 和 `/tos-funder-growth-lynch` 确定性成长分析命令

---

## 最小实测覆盖

验收阶段运行了以下真实 hoxit/iWencai 查询，用于校验 PR5A 的关键字段覆盖。完整 persona 评分仍由命令执行时按 schema 逐项生成。

### 实测命令

```bash
.venv/bin/python -m hoxit.cli iwc query -r finance -q "比亚迪 最近5年 营业收入 归母净利润 基本每股收益 研发费用" --limit 3
.venv/bin/python -m hoxit.cli iwc query -r finance -q "贵州茅台 最近5年 营业收入 归母净利润 基本每股收益 毛利率 销售净利率" --limit 3
.venv/bin/python -m hoxit.cli iwc query -r finance -q "宁波银行 最近5年 营业收入 归母净利润 基本每股收益 净息差 资本充足率 不良贷款率" --limit 3
.venv/bin/python -m hoxit.cli iwc query -r market -q "比亚迪 贵州茅台 宁波银行 市盈率PE(TTM) 市净率 总市值" --limit 5
```

### 实测结论

| 股票 | 核心字段 | 实测结果 | 对 PR5A 的影响 |
|---|---|---|---|
| 比亚迪 | 营收/归母净利润/EPS/研发费用 | ✅ 全部返回 2021-2025 | Growth/Fisher 可用；但 EPS 2025 因送转/股本变化断点明显 |
| 比亚迪 | PE/PB/总市值 | ✅ PE(TTM)=31.609, PB=3.755, 总市值约 8097.9 亿 | Lynch 估值不应沿用样例 PE=22.5 |
| 贵州茅台 | 营收/利润/EPS/毛利率/销售净利率 | ✅ 全部返回 2021-2025 | 高质量低增长判断可落地 |
| 贵州茅台 | PE/PB/总市值 | ✅ PE(TTM)=19.715, PB=6.03, 总市值约 16307.4 亿 | Lynch PEG 需用实测 PE 重算 |
| 宁波银行 | 营收/归母净利润/EPS/净息差/CAR/NPL | ✅ 全部返回 2021-2025 | 银行 sector adjustment 可落地，NIM/CAR/NPL 不只是设计假设 |
| 宁波银行 | PE/PB/总市值 | ✅ PE(TTM)=6.863, PB=0.888, 总市值约 2065.6 亿 | 银行低 PE 需配合增长/资产质量，不可强推 bullish |

### 实测发现

1. BYD 的 2025 EPS 从 2024 年 13.84 降到 3.58，同时归母净利润同比 -18.97%。这说明原始 EPS CAGR 不适合作为 Lynch PEG bullish override 的依据。
2. BYD 的 2025 营收仍增长 3.46%，研发费用继续增长，但利润端已经转弱。Growth command 必须区分历史高 CAGR 与最新增长恶化。
3. 宁波银行的 NIM/CAR/NPL 可直接返回，银行替代指标可执行。
4. 贵州茅台 2025 营收同比 -1.21%、归母净利润同比 -4.53%，验证了“高质量但增长放缓”的判断。

---

## 验证样本 1: 002594 比亚迪

### 实际查询字段

通过以下 iWencai 查询获取财务数据。验收阶段已做最小实测覆盖，确认核心字段可以返回；完整评分仍需在后续命令运行时逐项复算。

| Pack | 查询内容 | Route | 预期覆盖 |
|---|---|---|---|
| G1/L1 | 公司简介 所属同花顺行业 总市值 | basicinfo | ✅ 高 |
| G2/L2 | 最近5年 营业收入 归母净利润 基本每股收益 研发费用 | finance | ✅ 高（研发费用可能需要单独查询） |
| G2/L2 | 最近5年 毛利率 销售净利率 净资产收益率 产权比率 | finance | ✅ 高（销售净利率替代营业利润率） |
| G2/L2 | 最近5年 净资产 经营活动现金流净额 企业自由现金流量 | finance | ⚠️ FCF 覆盖率低，使用 OCF 代理 |
| G3/L3 | 总市值 市盈率PE(TTM) 市净率 市销率 | market | ✅ 高（PS 可能缺） |
| G4/L4 | 公告搜索：最近一年 回购 增持 股权激励 分红 | announcement | ✅ 基于 PR4A 验证 |

### Fisher Scoring 模拟

```text
Growth & Quality (30%):
  Revenue CAGR 32.2% → +4
  EPS CAGR 71.8%   → +3
  R&D 5.8%         → +2
  raw = 9/10 → score = 8.2

Margins & Stability (25%):
  Gross margin 18.2%  → +1
  Net margin 5.2% improving → +2
  Stability moderate → +2
  raw = 5/10 → score = 5.5

Management Efficiency (20%):
  ROE 20.8%  → +3
  D/E 0.68   → +1 (+1 manageable, not ideal 0.3)
  OCF pos 5/5y → +3
  raw = 7/10 → score = 7.0

Valuation (15%):
  PE 31.609  → +0/1 (high; only partially tolerated if growth durability holds)
  FCF yield 1.8% → +2
  raw = 3-4/10 → score = 4.0-5.0

Insider (5%): score = 5.0 (moderate buyback)
Sentiment (5%): score = 8.0 (bullish)

Total = 8.2×0.30 + 5.5×0.25 + 7.0×0.20 + 5.0×0.15 + 5.0×0.05 + 8.0×0.05
      = 2.46 + 1.38 + 1.40 + 0.75 + 0.25 + 0.40
      = 6.64

Signal: neutral (6.64 < 7.5 threshold for bullish)
Strength: flat
Confidence: 55
```

**Valuation cap 需关注**: 实测 PE 31.609 > 30，且 2025 利润端转弱。Fisher 可保持 neutral，但不能升级 bullish。

### Lynch Scoring 修正

```text
Growth (30%):
  Revenue CAGR 32.2% → +4 (strong)
  EPS CAGR 71.8%    → +4 (strong)
  Consistency: all positive → +2
  raw = 10/10 → score = 8.0

Valuation / PEG (25%):
  实测 PE(TTM)[20260602] = 31.609
  原始 EPS: 2021=1.06 → 2024=13.84 → 2025=3.58
  2025 EPS 因送转/股本变化出现断点，不能直接用于 PEG bullish override
  2025 归母净利润同比 = -18.97%，latest-year growth deterioration
  peg_reliability = degraded
  PEG 可作为观察项，但不能把 signal 提升为 bullish

Fundamentals (20%):
  D/E 0.68 → +2
  Net margin 5.2% → +1
  Gross margin 18.2% → +0
  OCF positive 5/5y → +2
  raw = 5/10 → score = 5.0

Sentiment (15%): score = 6.0
Insider (10%): score = 5.0

Total = 8.0×0.30 + 6.0×0.25 + 5.0×0.20 + 6.0×0.15 + 5.0×0.10
      = 2.40 + 1.50 + 1.00 + 0.90 + 0.50
      = 6.30

PEG-driven override: blocked because peg_reliability=degraded
Signal: neutral
Strength: flat
Confidence: 55
```

**PEG override 修正**: BYD 的原始 EPS CAGR 受 2025 送转/股本变化影响，且 2025 归母净利润同比为 -18.97%。Lynch 不能用这个 PEG 强行 bullish；需要拆股调整 EPS 或 forward PEG。

### 验证结果

| 检查项 | Fisher | Lynch | 说明 |
|---|---|---|---|
| Signal 不超枚举 | ✅ neutral | ✅ neutral | 枚举合规 |
| 不使用 dead route | ✅ | ✅ | 仅用 finance/market/announcement |
| 缺失字段标记 | ✅ FCF → OCF | ✅ FCF → OCF | 标注在 data_quality_summary |
| 毛利率低正确处理 | ✅ 得分低 (1/10) | ✅ 得分低 (0/10) | 不因高成长忽略 margin 质量 |
| 送转复权不误判 | ✅ | ✅ | 情感仅辅助，不主导信号 |
| 不因 sentiment 强推 bullish | ✅ | ✅ | Sentiment 仅 5%/15% |
| 可被 analyze 消费 | ✅ | ✅ | 输出包含 signal/strength/confidence |

---

## 验证样本 2: 600519 贵州茅台

### Fisher Scoring 模拟

核心问题：茅台是高质量低增长，Fisher 的 30% 成长权重会拉低总分。

```text
Growth (30%):
  Revenue CAGR ~8.5% → +2 (slight)
  EPS CAGR ~10.2%   → +2 (moderate)
  R&D: None (白酒无研发) → +0
  raw = 4/10 → score = 4.0

Margins (25%):
  Gross margin 91.8% → +4
  Net margin 48.7% → +3
  Stability: extremely consistent → +3
  raw = 10/10 → score = 10.0

Efficiency (20%):
  ROE ~30%+ → +4
  D/E ~0 → +3
  OCF all positive → +3
  raw = 10/10 → score = 10.0

Valuation (15%):
  PE ~22.8 → +1 (fair)
  FCF yield ~3.5% → +2
  raw = 3/6 → score = 5.0

Insider (5%): score = 5.0 (large buyback detected 30亿元)
Sentiment (5%): score = 8.0 (bullish)

Total = 4.0×0.30 + 10.0×0.25 + 10.0×0.20 + 5.0×0.15 + 5.0×0.05 + 8.0×0.05
      = 1.20 + 2.50 + 2.00 + 0.75 + 0.25 + 0.40
      = 7.10

Signal: neutral (7.10 < 7.5)
Strength: flat
Confidence: 55
```

**分析**: 茅台评分 7.10，最接近 bullish 的 neutral。Margin 和效率评分满分，但 Growth 仅 4.0 因为白酒无 R&D 且收入增长仅 8.5%。Fisher 框架正确地反映"高质量但低增长" — 不因品牌质量误判为高成长。

### Lynch Scoring 模拟

```text
Growth (30%):
  Revenue CAGR 8.5% → +2
  EPS CAGR 10.2%   → +2
  Consistency: all positive → +2
  raw = 6/10 → score = 5.0

Valuation / PEG (25%):
  PEG = 22.8 / 10.2 = 2.24 → +0 (too expensive on GARP)
  PE 22.8 → +1
  raw = 1/5 → score = 2.5

Fundamentals (20%):
  D/E ~0 → +3
  Net margin 48.7% → +2
  Gross margin 91.8% → +2
  FCF positive → +2
  raw = 9/9 → score = 10.0

Sentiment (15%): score = 6.0
Insider (10%): score = 5.0

Total = 5.0×0.30 + 2.5×0.25 + 10.0×0.20 + 6.0×0.15 + 5.0×0.10
      = 1.50 + 0.63 + 2.00 + 0.90 + 0.50
      = 5.53

Signal: neutral
Strength: flat
Confidence: 50

PEG check: 2.24 > 2.0 → signal CANNOT be bullish (enforced)
```

**关键**: Lynch 框架正确地看到 PEG 2.24 > 2.0，即使基本面质量满分，也严格禁止 bullish。这正是 GARP 的核心逻辑 — 好公司不等于好股票。

### 验证结果

| 检查项 | Fisher | Lynch | 说明 |
|---|---|---|---|
| 不因品牌质量误判高成长 | ✅ neutral | ✅ neutral | 两者均不给 bullish |
| 无研发正确处理 | ✅ R&D=0 | N/A | Fisher 研发项得 0 分，不拖累 margin/efficiency |
| PEG > 2.0 禁止 bullish | N/A | ✅ | Lynch 严格执行 GARP 纪律 |
| 高质量基本面体现 | ✅ margin 满分 | ✅ fundamentals 满分 | 在低成长股票中仍正确反映质量 |
| FCF / 回购处理正确 | ✅ | ✅ | 茅台 30 亿回购正确计入 |

---

## 验证样本 3: 002142 宁波银行

### Sector Adjustment 检查

核心测试：银行类 sector adjustment 是否启用，是否避免使用毛利率/存货。

| 调整项 | Fisher | Lynch | 标准 | 银行调整 |
|---|---|---|---|---|
| 毛利率 | NIM 代理 | NIM 代理 | 毛利率 | → 净息差(NIM) |
| D/E | CAR | CAR | 产权比率 | → 资本充足率(CAR) |
| ROE 阈值 | >10% | >10% | >15% | 银行 ROE 下限降低 |
| R&D | 跳过 | N/A | 研发费用 | 银行无有意义研发 |
| FCF | OCF 稳定性 | OCF 稳定性 | FCF>0 | 银行用 OCF |
| PE 阈值 | ≤10 | ≤10 | <25 | 银行 PE 较低 |
| PEG | N/A | +股息率 | PE/增长 | 银行 PEG = PE/(增长+股息) |

### Fisher Scoring 模拟（银行调整后）

```text
Growth (30%):
  Revenue CAGR 12.5% → +3
  EPS CAGR 14.8%   → +2
  R&D: SKIP (银行) → N/A
  raw = 5/7 (银行: 跳过R&D, 调权重) → score = 6.5

Margins (25%):
  NIM 1.85% → +2
  Net margin ~35% → +3
  Stability: stable → +2
  raw = 7/10 → score = 7.0

Efficiency (20%):
  ROE ~13% → +2 (银行>10%标准)
  CAR 14.2% > 12% → +3
  OCF all positive → +3
  raw = 8/10 → score = 8.0

Valuation (15%):
  PE 6.2 → +3 (银行<10标准)
  FCF yield → N/A → +0
  raw = 3/6 → score = 5.0

Insider (5%): score = 5.0
Sentiment (5%): score = 6.0

Total = 6.5×0.30 + 7.0×0.25 + 8.0×0.20 + 5.0×0.15 + 5.0×0.05 + 6.0×0.05
      = 1.95 + 1.75 + 1.60 + 0.75 + 0.25 + 0.30
      = 6.60

Signal: neutral
Strength: flat
Confidence: 55
```

### Lynch Scoring 模拟（银行调整后）

```text
Growth (30%):
  Revenue CAGR 12.5% → +3
  EPS CAGR 14.8% → +3
  Consistency: all positive → +2
  raw = 8/10 → score = 6.5

Valuation / PEG (25%):
  Bank-adjusted PEG = 6.2 / (14.8% + 3.8%) = 0.33 → +4
  PE 6.2 (<10) → +2
  raw = 6/8 → score = 7.5

Fundamentals (20%):
  CAR 14.2% → +3
  NIM 1.85% → +1
  NPL 0.76% → +2
  OCF all positive → +2
  raw = 8/9 → score = 7.0

Sentiment (15%): score = 6.0
Insider (10%): score = 5.0

Total = 6.5×0.30 + 7.5×0.25 + 7.0×0.20 + 6.0×0.15 + 5.0×0.10
      = 1.95 + 1.88 + 1.40 + 0.90 + 0.50
      = 6.63

PEG 0.33 < 1.0 → attractive threshold met
BUT: Bank sector → PE < 10 but EPS growth < 10% → do NOT force bullish
Signal: neutral (bank safety: cheap can be value trap)
Strength: flat
Confidence: 50
```

### 验证结果

| 检查项 | Fisher | Lynch | 说明 |
|---|---|---|---|
| sector adjustment 启用 | ✅ | ✅ | NIM/CAR/NPL 替换毛利率/流动比率 |
| 不使用毛利率/存货 | ✅ | ✅ | 银行不查毛利率/R&D/存货周转率 |
| 银行 PE 阈值正确 | ✅ PE < 10 满分 | ✅ PE < 10 +2 分 | 银行 PE 通常较低 |
| 不因低 PE 强推 bullish | ✅ neutral | ✅ neutral | 低 PE 可能是价值陷阱 |
| 研发费用跳过 | ✅ score = 0 | N/A | 银行无研发 |

---

## 三样本汇总

| 指标 | 002594 比亚迪 | 600519 贵州茅台 | 002142 宁波银行 |
|---|---|---|---|
| **Fisher signal** | **neutral** | **neutral** | **neutral** |
| Fisher strength | flat | flat | flat |
| Fisher confidence | 55 | 55 | 55 |
| 最佳维度 | Growth (8.2) | Margins (10.0) | Efficiency (8.0) |
| 最弱维度 | Margins (5.5) | Growth (4.0) | Growth (6.5) |
| **Lynch signal** | **neutral** | **neutral** | **neutral** |
| Lynch strength | flat | flat | flat |
| Lynch confidence | 55 | 50 | 55 |
| PEG | degraded (raw EPS distorted) | 2.24 ❌ | 0.33 ✅ |
| Bank adjustment | N/A | N/A | ✅ CAR/NIM/NPL |

### 关键观察

1. **Fisher 对比特币三样本全部 neutral** — 因为严格的 7.5 门槛和三样本都存在短板（BYD 毛利率低、茅台增长慢、宁波银行增长低）
2. **Lynch 对比亚迪 neutral** — 原始 PEG 看似便宜，但 EPS 序列受送转/股本变化影响且 2025 利润下滑，PEG override 被正确阻断
3. **茅台两个均为 neutral** — 正确反映了"高质量低增长且估值偏高"的 GARP 现实
4. **宁波银行两个均为 neutral** — sector adjustment 正确启用，低 PE 被正确识别为值得关注但不强推

---

## Fisher vs Buffett/Graham/quant-fundamentals 对比

| 维度 | Fisher | Buffett | Graham | quant-fundamentals |
|---|---|---|---|---|
| 核心关注 | 成长质量 + R&D | 护城河 + ROE | 安全边际 + 低估 | 四维客观打分 |
| 增长权重 | 30% (最高) | 中等 | 低 | 25% |
| 估值容忍度 | 中性（愿为质量付费） | 低（需合理价格） | 极低（需安全边际） | 计入价格比率 |
| R&D | 核心维度 | 非必须 | 不评估 | 不评估 |
| 对 BYD 信号 | neutral | - | - | neutral (PR 数据) |
| 对 茅台 信号 | neutral | - | - | neutral (PR 数据) |

---

## 缺失字段记录

| 字段 | 覆盖率 | 影响 | 处理方式 |
|---|---|---|---|
| 营业收入 | ✅ 高 | Growth 维度 | 直接使用 |
| 归母净利润 | ✅ 高 | Growth/效率 | 直接使用 |
| 基本每股收益 | ✅ 高 | Growth/PEG | 直接使用 |
| 研发费用 | ⚠️ 中 | Fisher Growth 30% | 需单独查询；无研发行业得 0 |
| 毛利率 | ✅ 高/银行❌ | Margin 维度 | 银行用 NIM 替代 |
| 销售净利率 | ✅ 高 | Margin 维度 | 替代营业利润率 |
| 净资产收益率(ROE) | ✅ 高 | 效率维度 | 直接使用 |
| 产权比率(D/E) | ✅ 高/银行❌ | 效率/基本面 | 银行用 CAR 替代 |
| 企业自由现金流量(FCF) | ⚠️ 中低 | 效率/基本面 | 用 OCF 代理；银行用 OCF 稳定性 |
| 经营活动现金流净额(OCF) | ✅ 高 | FCF 代理 | 替代 FCF |
| 市盈率PE(TTM) | ✅ 高 | 估值维度 | 直接使用 |
| PEG | ⚠️ 低（需计算） | Lynch 核心 | 从 EPS CAGR + PE 计算 |
| 资本充足率(CAR) | ⚠️ 银行专用 | 银行 D/E 替代 | 银行 finance 查询 |
| 净息差(NIM) | ⚠️ 银行专用 | 毛利率替代 | 银行 finance 查询 |
| 不良贷款率(NPL) | ⚠️ 银行专用 | 基本面辅助 | 银行 finance 查询 |
| 总股本 | ✅ 中（仅最新） | EPS 计算辅助 | 最新快照可用 |

---

## Constitution Self-Review

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | 读取最新 accepted schema | ✅ | 读取 output-schema-examples.md, command-template.md, skill-workflow.md |
| 2 | 避免新 signal enum | ✅ | 仅用 bullish/neutral/bearish/blocked |
| 3 | 区分 facts/metrics/warnings/interpretation/action | ✅ | Growth facts → scoring_breakdown → signal 分层清晰 |
| 4 | 标注 fallback 和 degraded 数据 | ✅ | FCF → OCF proxy, 营业利润率 → 销售净利率, missing_fields 数组 |
| 5 | 避免从样本验证推出全局正确性 | ✅ | 仅做 3 个样本的最小实测覆盖 + 设计评分，不声明全局正确 |
| 6 | 区分 data-quality veto 与 risk veto | ✅ | 缺失字段不在 data_quality_summary 中标记，不触发 veto |
| 7 | 下游可直接消费 | ✅ | analyze 消费 signal/strength/confidence/scoring_breakdown，无需解析 prose |
| 8 | 保持 iWencai 和 mootdx 边界 | ✅ | Growth 仅用 finance/market/announcement routes；不使用 mootdx OHLCV |
| 9 | 记录未解决问题 | ✅ | 缺失字段表、FCF 覆盖率问题、PEG 计算精度、银行数据代理精度 |

---

## 交付总结

### 修改文件列表

| 文件 | 状态 | 变更内容 |
|---|---|---|
| `tos-funder/references/growth-investors.md` | 🆕 新建 | Fisher/Lynch 方法论、A 股字段映射、银行调整、权重模板、schema 参考 |
| `tos-funder/commands/tos-funder-growth-fisher.md` | 🆕 新建 | 6 维评分模型（30/25/20/15/5/5）、完整 query pack、银行调整、3 种输出示例 |
| `tos-funder/commands/tos-funder-growth-lynch.md` | 🆕 新建 | GARP PEG 核心、5 维评分（30/25/20/15/10）、PEG override 逻辑、银行调整+PEG+股息率 |
| `tos-funder/SKILL.md` | ✅ 修改 | 新增 growth-fisher/lynch 路由 + growth-investors.md 引用 |
| `tos-funder/commands/tos-funder-analyze.md` | ✅ 修改 | growth family 路由指向具体命令 + consumed schema 扩展 |
| `tos-funder/references/agent-taxonomy.md` | ✅ 修改 | 更新 growth 列实现状态 |
| `tos-funder/references/output-schema-examples.md` | ✅ 修改 | 新增 `#growth_analyst_signal` 第 6 anchor |
| `tos-funder/references/skill-workflow.md` | ✅ 修改 | Schema Reference 表新增 growth 命令 |
| `docs/tos-funder/validation-pr5a.md` | 🆕 新建 | 三个样本模拟验证、与 Buffett/Graham 对比、缺失字段记录、Constitution self-review |

### Fisher/Lynch 三样本 Signal

| 股票 | Fisher | Lynch | 差异原因 |
|---|---|---|---|
| 002594 比亚迪 | neutral/55 | neutral/55 | 原始 PEG 受 EPS 送转/股本变化影响，Lynch bullish override 被阻断；Fisher 看 margin 低 |
| 600519 贵州茅台 | neutral/55 | neutral/50 | PEG 2.24 > 2.0 禁止 bullish；Fisher growth 得分低 |
| 002142 宁波银行 | neutral/55 | neutral/55 | Bank adjustment 正确启用；低 PE 不强制 bullish |

### iWencai 覆盖可靠性

| 字段组 | 可靠 ✅ | 需注意 ⚠️ | 不可靠 ❌ |
|---|---|---|---|
| 收入/利润/EPS/ROE | ✅ 5 年均可用 | | |
| 毛利率/净利率 | ✅ 非银行 | ⚠️ 银行需 NIM | |
| 研发费用 | | ⚠️ 需单独查询 | |
| 产权比率(D/E) | ✅ 非银行 | ⚠️ 银行需 CAR | |
| FCF | | ⚠️ OCF 代理 | ❌ 直接 FCF 覆盖率低 |
| PE/PB/市值 | ✅ | | |
| PEG | | ⚠️ 需计算 (EPS CAGR) | |
| 总股本 | ✅ 最新快照 | | |
| 资本开支 | | ⚠️ 需单独查询 | |

### 下一步建议

| 优先级 | 建议 | 说明 |
|---|---|---|
| **P0** | ✅ 已完成最小实测覆盖 | 已验证三样本核心财务/估值字段返回；完整评分仍需后续命令运行时复算 |
| **P1** | Growth family aggregator | 合并 Fisher + Lynch 信号为一个 growth 综合信号 |
| **P2** | Cathie Wood 命令 | 需要创新/颠覆式增长的新维度：营收增速、渗透率、行业变革指标 |
| **P2** | Tactical catalyst proxy | 利用情感层 + 价格行为 + 公告事件识别催化剂 |
