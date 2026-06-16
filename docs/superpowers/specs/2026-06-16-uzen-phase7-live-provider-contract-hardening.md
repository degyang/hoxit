# UZEN Phase 7: hoxit Live Provider Contract Hardening

## 背景

Phase 6 已完成 A 股数据覆盖扩展，但宁波银行 `002142` live 报告验收暴露出一个更基础的问题：UZEN 虽然优先调用 hoxit provider，但报告层没有充分尊重真实 hoxit 输出形态。

已暴露问题包括：

- `mootdx_quote()` 返回 `price`、`last_close`，但不一定返回 `change_pct`，UZEN 原先未补算涨跌幅。
- `finance_snapshot()` live 可返回 pandas DataFrame，UZEN 原先直接布尔判断导致失败。
- `signals.concept()` live 返回 dict `{total, boards, concept_tags}`，UZEN 原先只支持 `list[dict]`。
- `signals.dragon_tiger()` live 返回 dict `{records, seats, institution}`，UZEN 原先只支持 list。
- 宁波银行报告中 `ROE`、`净利润`、`DCF`、`Comps` 等字段仍大量 `data_needed`，说明财务/估值字段归一化不足。

这不是单个 bug，而是 provider contract 和 report contract 之间缺少稳定归一化层。

## 目标

Phase 7 的目标是让 UZEN 报告建立在真实 hoxit 输出契约之上：

1. 明确 hoxit provider 输出形态，增加 UZEN normalization 层。
2. 对基础行情 OHLCV 可衍生指标做稳定补算。
3. 将 finance DataFrame/dict 统一为报告可读字段。
4. 为银行股补足基本财务和估值报告质量，先服务宁波银行。
5. 引入数据源质量评估（source quality evaluation）和字段级 fallback，遇到 hoxit 当前数据源不合格时，参考 UZI 原项目机制选择更可靠的 hoxit 可复用数据源或新增 hoxit provider。
6. 建立 live smoke gate，防止 mock-only 通过但真实报告缺关键字段。

## 非目标

- 不做 HTML/PNG/Playwright 可视化。
- 不新增非 hoxit 的 one-off scraper。
- 不绕过 hoxit provider 直接在 UZEN 中抓网页。
- Phase 7 暂不引入 akshare 作为 fallback 候选；akshare 当前稳定性问题较多。
- 不声明完整 UZI parity。
- 不做 65/66 persona parity。
- 不做 LHB 席位身份推断。
- 不做社交/操纵证据判断。

## 设计原则

### hoxit-first

所有数据采集必须通过 hoxit 已有模块或新增 hoxit 可复用接口完成。UZEN 只能做：

- 字段归一化（normalization）
- 确定性派生计算（deterministic derived metrics）
- 报告组织与 data quality 标注

### 字段级 fallback

不要因为某个 provider 缺一个字段就整源标坏。字段应独立标注：

- available
- derived
- missing
- unsupported

例如 `quote.price` 可用、`quote.change_pct` 缺失时，应由 `price/last_close` 补算并标注 derived。

### 数据源质量评估

遇到数据源不合格时，不能只在 UZEN 报告里接受缺失。应按 UZI 原项目思路做综合评估：

- 优先使用 hoxit 已有 provider。
- 如果 hoxit 当前 provider 字段缺失、结构不稳定、长期空数据或明显不适合该资产类型，应记录为 source-level 或 field-level quality issue。
- 对同一字段可评估多个 hoxit sources，例如腾讯、东财、mootdx、iwencai、巨潮、同花顺。
- 选择质量更好的数据源时，优先新增或增强 hoxit reusable helper，而不是在 UZEN 内部写 one-off 抓取。
- fallback 必须字段级生效：一个数据源只补缺失字段，不应覆盖已有高质量字段。
- 每个 fallback 字段要保留 source/basis，避免报告混淆来源。

参考 UZI 已有机制：

- 多源 fallback：参考 UZI 的字段级补齐机制，但 Phase 7 候选优先限定为 hoxit 现有或可控增强源，例如 Eastmoney、Tencent、mootdx、iwencai、CNInfo、同花顺公开页等；暂不考虑 akshare。
- 字段级 fallback gate：主源拿到 PE/PB 但 name 缺失时，只补 name，不整源替换。
- 数据质量 banner / review gate：关键字段缺失时给出明确 warning 或阻断。
- 对资产类型降级：ETF、银行股、港股等不能套用普通股票字段时，改用适配口径。

### 受控 Web / Playwright fallback

如果 hoxit 已有 HTTP/API provider 仍无法覆盖关键字段，可以评估 Web/Playwright fallback，但必须受控：

- 先在 PR 中明确提出需要的字段、目标网页、稳定性风险和用户协助项。
- 需要登录、验证码、Cookie、浏览器 profile、手动确认页面结构时，必须先请求用户协助。
- Playwright/Web 逻辑应沉淀为 hoxit reusable helper，不允许写在 UZEN 报告层。
- 默认单元测试不得依赖浏览器或网络；Playwright/live 测试必须显式环境变量启用并默认跳过。
- 报告必须标注来源和 quality，不得把网页推断当成官方结构化数据。
- 如果网页不稳定、字段来源不明确或需要频繁人工介入，应标为 deferred，而不是让报告链路不可靠。

### pandas 止于边界

hoxit 核心原则是统一返回 dict/list；如果历史 provider 仍返回 DataFrame，UZEN normalization 必须在边界消化，不能让 DataFrame 进入报告渲染逻辑。

### Live smoke 是准入门槛

每个涉及 provider contract 的 PR，都必须至少用 mock/unit tests 覆盖真实形态；最后一个 PR 必须跑宁波银行 live report smoke，并检查关键字段。

## 关键数据缺口

### 基础行情与 OHLCV 衍生指标

需要从 quote/bars 补算：

- `change_pct`
- `change_amount`
- `amplitude_pct`
- `avg_price`
- `return_5d`
- `return_20d`
- `ma5`
- `ma20`
- `volatility_20d`
- `drawdown_60d`

其中无法可靠计算的字段必须标为 data_needed，并说明缺少哪个输入。

### 财务字段

需要将 `finance_snapshot()` 的真实返回统一为：

- `roe`
- `net_profit`
- `revenue`
- `gross_margin`
- `net_margin`
- `total_assets`
- `total_equity`
- `total_shares`

如果 hoxit 当前源无法提供，应先通过 hoxit 基本面/iwencai/公告/研报等已有接口评估可补路径，再决定是否新增 hoxit reusable helper。

### 估值字段

当前 PE/PB 来自 `market.tencent_metrics()`，但报告还需要稳定：

- `pe_ttm`
- `pb`
- `market_cap`
- `total_shares`
- `dividend_yield`
- `forward_pe`（如可从研报 EPS/PE 衍生，需标注来源）

### 银行股专项

宁波银行这类银行股不适合普通 FCFF DCF 作为主估值方法。Phase 7 先补报告质量，不强行做完整银行估值模型：

- ROE
- PB
- 股息率
- 净息差（NIM，如可取）
- 不良贷款率（NPL ratio，如可取）
- 拨备覆盖率（provision coverage，如可取）
- 核心一级资本充足率 / 资本充足率（如可取）

## 成功标准

宁波银行 `002142` 的 `analyze-stock` Markdown 报告至少满足：

- 核心结论显示名称、最新价、涨跌幅。
- 行情与估值显示 PE TTM、PB，且市场相关字段能说明缺失原因。
- 基本面与财务不因 DataFrame/dict 形态导致字段空转。
- 报告自审 `passed` 或明确列出非阻断 warnings。
- JSON 中 `analysis.summary.change_pct` 不为空。
- 不出现 raw dict/list repr。
- 若 ROE/净利润/银行专项指标仍缺失，必须在 `input_quality` 或 data quality 中清楚说明缺哪类 hoxit source，而不是静默缺失。

## PR 分解

Phase 7 分 5 个 PR：

1. `PR-LIVE-001`: UZEN Provider Normalization Boundary
2. `PR-LIVE-002`: UZEN Derived Market Metrics
3. `PR-LIVE-003`: hoxit/UZEN Finance Field Normalization And Source Quality
4. `PR-LIVE-004`: Bank Report Quality For Ningbo Bank
5. `PR-LIVE-005`: Live Smoke Gate And Docs Sync

## 风险

- 外部接口不稳定：live smoke 不能成为默认单元测试，必须环境变量显式启用。
- pandas DataFrame 字段名可能随 provider 变化：需要多字段 alias 和可测试 fallback。
- 银行业字段可能不适用于所有行业：银行专项必须只在银行股或字段可用时启用。
- DCF/Comps 不适合银行股：报告应降级说明，不应输出假精确估值。
