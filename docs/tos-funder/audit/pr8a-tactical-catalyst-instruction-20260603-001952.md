# PR8A Instruction — Tactical Catalyst Proxy

Created: 2026-06-03 00:19:52 Asia/Shanghai
Author: Codex
Type: CC instruction

## Command For CC

```text
PR 8A: Tactical Catalyst Proxy — A 股事件催化剂代理层

目标：
在 tos-funder 中实现 tactical/catalyst 代理层，用于识别 A 股中短期事件催化剂。该层服务于后续 Druckenmiller / Ackman / Taleb 等 tactical/macro persona，但本 PR 只做确定性 catalyst proxy，不做最终投资建议，不输出 final_action。

必须先阅读：
1. docs/tos-funder/07-cc-working-constitution.md
2. tos-funder/references/command-template.md
3. tos-funder/references/output-schema-examples.md
4. tos-funder/references/skill-workflow.md
5. tos-funder/references/sentiment-event-proxy.md
6. tos-funder/commands/tos-funder-quant-sentiment.md
7. tos-funder/references/price-series.md
8. tos-funder/commands/tos-funder-quant-price-series.md
9. tos-funder/commands/tos-funder-quant-technicals.md
10. tos-funder/commands/tos-funder-risk-manager.md
11. docs/tos-funder/validation-pr4a.md
12. docs/tos-funder/validation-pr6a.md
13. docs/tos-funder/validation-pr6b.md

交付文件：
1. 新建：
   - tos-funder/references/tactical-catalyst.md
   - tos-funder/commands/tos-funder-tactical-catalyst.md
   - docs/tos-funder/validation-pr8a.md

2. 更新：
   - tos-funder/SKILL.md
   - tos-funder/commands/tos-funder-analyze.md
   - tos-funder/references/agent-taxonomy.md
   - tos-funder/references/output-schema-examples.md
   - tos-funder/references/skill-workflow.md

设计要求：
1. `/tos-funder-tactical-catalyst` 是确定性 proxy command。
2. 它可以消费：
   - `/tos-funder-quant-sentiment`
   - `/tos-funder-quant-technicals`
   - `/tos-funder-risk-manager`
   - `/tos-funder-quant-price-series`
   - iWencai 公告/研报搜索结果
3. 它不应该重新发散为宏观平台，不接外部新闻 API，不移植 ai-hedge-fund runtime。
4. 它必须区分：
   - factual catalyst：公告披露的事实事件
   - opinion catalyst：研报/分析师观点
   - price catalyst：技术突破、放量、趋势改变
   - risk catalyst：监管、诉讼、减持、质押、财务恶化、复权异常
5. 它不能把 sentiment bullish 直接变成 catalyst bullish。
6. 它不能把 degraded risk metrics 当成真实负面催化剂。
7. 如果 price-series adjustment_status=suspect，必须标记 data_quality warning，并禁止使用 max_dd 或全序列极端指标作为 catalyst。
8. 如果 iWencai report search 只有正面研报，必须应用 PR4A 的 report polarization cap，不得把“一堆正面研报”当成强催化剂。
9. 输出必须是 analyst signal，不输出 final_action。

建议 schema 名称：
- `tactical_catalyst_signal`

必须输出字段：
- target
- signal_type: "tactical_catalyst"
- data_quality_summary
- catalyst_facts
- price_context
- risk_context
- sentiment_context
- catalyst_scoring
- hard_gates
- signal
- strength
- confidence
- confidence_calculation
- risks
- opportunities
- next_steps

signal 只能用：
- bullish
- neutral
- bearish
- blocked

strength 只能用：
- strong
- weak
- flat

评分建议：
- factual catalyst: 35%
- price confirmation: 25%
- risk asymmetry: 20%
- sentiment/opinion support: 10%
- recency/materiality: 10%

Hard gates：
1. data-quality gate：
   - adjustment_status=suspect/unknown → price catalyst confidence capped at 50
   - degraded max_dd/downside_vol 不得作为 negative catalyst
2. report polarization gate：
   - all reports positive + no factual catalyst → signal cannot exceed neutral
3. risk event gate：
   - 监管/诉讼/重大减持/质押危机/业绩大幅下修 → signal cannot be bullish
4. price confirmation gate：
   - no volume/price confirmation → bullish catalyst cannot be strong
5. stale event gate：
   - all events older than 180 days → confidence capped at 40

验证样本：
1. 002594 比亚迪
   - 检查送转/分红/研发/研报正向是否被识别为事实/观点催化剂
   - 必须避免把 2025-07-29 复权跳变当成真实 price collapse
   - 预期：neutral 或 weak bullish，但不能 strong bullish，除非价格确认有效且 adjustment verified
2. 600519 贵州茅台
   - 高质量公司但增长放缓，研报正向偏置明显
   - 预期：neutral，不能因为一堆正面研报直接 bullish
3. 002142 宁波银行
   - 银行资产质量/分红/研报正向
   - 预期：neutral 或 weak bullish；必须区分银行低估值和真实催化剂
4. 可选负面样本：
   - 找一个有监管函/诉讼/减持公告的股票，验证 risk event gate

验收标准：
1. command frontmatter 声明 consumed_schema / produced_schema / consumable_by。
2. output-schema-examples.md 新增 `#tactical_catalyst_signal`。
3. skill-workflow.md 增加 `/tos-funder-tactical-catalyst` 路由。
4. analyze.md family=tactical 默认先使用 `/tos-funder-tactical-catalyst`。
5. validation-pr8a.md 必须记录每个样本：
   - consumed inputs
   - source_status
   - catalyst classification
   - hard gates
   - confidence calculation
   - final signal
6. 不得出现新 signal/action enum。
7. 不得输出 final_action。
8. 不得直接调用 dead routes：business/event query2data/management insider fields。
9. 不得把 report polarization 或 degraded PEG/risk metrics 作为 bullish/bearish 主因。
10. validation 必须包含 constitution self-review。

完成后汇报：
- 修改文件列表
- 三个主样本 signal/confidence
- hard gate 触发情况
- 哪些 catalyst 类型覆盖可靠，哪些不可靠
- 是否建议下一步实现 Druckenmiller，还是先做 risk/tail-risk proxy
```

## CC Response Area

CC should append its completion summary below this line.

---

### CC Response — 2026-06-03

**PR 8A 完成。交付物清单：**

#### 新建文件 (3)

| 文件 | 内容 |
|---|---|
| `tos-funder/references/tactical-catalyst.md` | 催化剂分类框架：4 种类型（事实/观点/价格/风险）、评分模型（5 维度）、5 道 Hard Gate、数据源策略、Schema 定义 |
| `tos-funder/commands/tos-funder-tactical-catalyst.md` | 确定性催化剂代理命令：数据收集（6 步）→ 事件分类 → Hard Gate → 评分 → 信号推导 |
| `docs/tos-funder/validation-pr8a.md` | 3 个主样本（BYD→neutral, 茅台→neutral, 宁波银行→neutral/weak_bullish）+ 1 个可选负面样本 |

#### 更新文件 (5)

| 文件 | 修改内容 |
|---|---|
| `tos-funder/SKILL.md` | 增加 `/tos-funder-tactical-catalyst` 命令条目 |
| `tos-funder/commands/tos-funder-analyze.md` | `family=tactical` 路由改为默认使用 catalyst；consumed schema 增加 tactical 条目 |
| `tos-funder/references/agent-taxonomy.md` | Activist/macro 行增加 Tactical Catalyst Proxy + ✅ |
| `tos-funder/references/output-schema-examples.md` | 新增 section 8: `#tactical_catalyst_signal` |
| `tos-funder/references/skill-workflow.md` | Schema Reference 表增加 `/tos-funder-tactical-catalyst` 路由 |

#### 三个主样本信号

| 样本 | Signal | Strength | Confidence | Hard Gates Triggered |
|---|---|---|---|---|
| 002594 比亚迪 | neutral | flat | 55 | Gate 1 (data quality), Gate 4 (price confirmation) |
| 600519 贵州茅台 | neutral | flat | 45 | Gate 2 (report polarization) |
| 002142 宁波银行 | neutral to weak bullish | flat to weak | 55 | None (all clear) |

#### Hard Gate 覆盖情况

| Gate | BYD | 茅台 | 宁波 | 说明 |
|---|---|---|---|---|
| 1. Data Quality | ✅ triggered | — | — | adjustment_status=suspect → price catalyst capped |
| 2. Report Polarization | — | ✅ triggered | — | 全线正面研报 + 无负面事实 → 不得 bullish |
| 3. Risk Event | — | — | — | 三样本均无监管/诉讼 |
| 4. Price Confirmation | ✅ triggered | — | borderline | vol_ratio<1.2 + 无 crossover → bullish cap weak |
| 5. Stale Event | — | — | — | 所有样本都有 180 天内事件 |

#### Catalyst 类型可靠性评估

| 类型 | 可靠性 | 说明 |
|---|---|---|
| factual | ⚠️ 高（公告搜索） | PR4A 已验证关键词搜索覆盖率，IR 过滤后事件识别率高 |
| opinion | ⚠️ 低（研报搜索） | 研报偏置已验证：0 负面，仅可用作 opinion 计数，不可用作方向判断 |
| price | ✅ 高（技术指标） | mootdx OHLCV 本地计算，MA/成交量/RSI 全部可用 |
| risk | ⚠️ 中（公告搜索 + risk-manager） | 监管/诉讼类公告覆盖率可接受；复权异常可检测但不能作为真实负面催化剂 |

#### 下一步建议

建议优先实现 **risk/tail-risk proxy**（`/tos-funder-tactical-tail-risk`），原因：

1. Druckenmiller 需要宏观数据（利率、汇率、通胀等），当前数据基础设施不支持外部宏观 API。
2. Tail-risk proxy 可以直接复用 tactical-catalyst 的 risk catalyst 分类 + risk-manager 的极端风险指标，增量成本低。
3. 风险代理层与现有 tactical-catalyst 互补 — catalyst 看事件驱动机会，tail-risk 看尾部风险保护。
4. 一个负面样本（监管/诉讼）尚未实测验证 — 可纳入 tail-risk PR 的验证计划。
