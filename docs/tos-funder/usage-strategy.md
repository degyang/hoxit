# Trading Funder 实战使用策略 & Cheatsheet

Created: 2026-06-03

本文档面向已掌握 tos-funder 架构的用户，提供日常实战的使用策略和命令速查。

---

## 一、实战使用策略

### 1. 三层工作流

日常使用分三层，深度递增：

```
Layer 1 — 宏观定调  (1-3 min)
  └─ /tos-funder-macro-topdown → 市场状态 / 风险偏好 / 行业强弱

Layer 2 — 个股扫描  (3-5 min/支)
  └─ /tos-funder-analyze <code> family=value|growth|quant → 快速信号

Layer 3 — 组合决策  (5-10 min/支)
  └─ 按序运行 value → growth → quant → tactical → risk → portfolio
  └─ /tos-funder-portfolio 输出 final_actions
```

### 2. 推荐日常流程

#### 早盘宏观扫描（3 分钟）

```
1. /tos-funder-macro-topdown
   - 看 market_regime: 牛市/震荡/熊市?
   - 看 coverage_status: 数据够不够?
   - 决定当天偏进攻(全量分析)还是防守(只看 risk)
2. 如果发现板块轮动信号 -> 关注对应板块个股
```

#### 个股首次分析（15 分钟）

标准流水线：

```
Step 1: /tos-funder-quant-price-series <code>
        → 获取 qfq OHLCV，确认 adjustment_status

Step 2: /tos-funder-value-graham <code>
        → 安全边际评估

Step 3: 选做
   /tos-funder-value-buffett <code>
   /tos-funder-growth <code>
   /tos-funder-quant-fundamentals <code>

Step 4: /tos-funder-quant-technicals <code>
        → 趋势 / 动量 / 波动率

Step 5: /tos-funder-quant-sentiment <code>
        → 事件分类 / 情绪信号

Step 6: /tos-funder-tactical <code>
        → 催化剂 + 尾部风险合成

Step 7: /tos-funder-risk-manager <code>
        → 波动率 / 回撤 / VaR / 流动性

Step 8: /tos-funder-portfolio <code>
        → 七层融合 → final_action
```

#### 持仓健康检查（5 分钟/支）

```
/tos-funder-risk-manager <code>
→ 看 overall_risk_level, drawdown, var
→ 看 action_constraints.action_ceiling 有没有收紧

/tos-funder-analye <code> family=quant
→ 技术面是否破位
→ 情绪面是否恶化
```

#### 事件驱动扫描

```
/tos-funder-tactical-catalyst <code>
→ 检查近期公告/研报中的催化剂信号

/tos-funder-tactical-tail-risk <code>
→ 检查下行风险 / 尾部风险信号
```

### 3. 命令组合速查

| 目标 | 命令流水线 | 预期耗时 |
|---|---|---|
| 快速看一只票 | `/tos-funder-analyze <code> family=value` | 2 min |
| 全量分析一只票 | price-series → value → growth → quant → tactical → risk → portfolio | 10-15 min |
| 检查持仓风险 | `/tos-funder-risk-manager <code>` | 2 min |
| 检查市场状态 | `/tos-funder-macro-topdown` | 1 min |
| 事件催化剂扫描 | `/tos-funder-tactical <code>` | 3 min |
| 多股组合风险 | `/tos-funder-risk-manager` (multi-stock mode) | 3 min |

### 4. 如何收集问题供下一轮 PR

日常使用中，用 markdown 文件记录问题：

```markdown
# tos-funder 实战问题日志

## YYYY-MM-DD

### 数据质量问题
- [ ] 某条命令返回数据质量 degraded 的频率过高
- [ ] iWencai 某字段经常为空

### 命令输出问题
- [ ] 某条命令的 confidence 与直觉偏差过大
- [ ] 某条命令的 missing_data 缺少关键字段

### 工作流程问题
- [ ] 某两步之间的衔接不顺畅
- [ ] 某条命令缺少必要的上下文指引

### 架构问题
- [ ] 某条命令的输出格式下游无法直接消费
- [ ] 某条规则在实际案例中给出了反直觉的结果
```

**分类建议**：

| 类别 | 严重程度 | 处理时机 |
|---|---|---|
| 数据质量 gap | High | 优先修——影响所有依赖该数据的命令 |
| Command 输出不合预期 | Medium | 收集到足够复现案例后修 |
| 工作流不顺畅 | Low | 下一轮 PR 顺手改 |
| Schema / 边界条件 | Medium | 随问题发现一起修 |
| 新策略需求 | Future | 攒够后开新 PR |

---

## 二、Cheatsheet（命令速查）

### 全部 16 条命令

| 命令 | 一句话用途 | 产生什么 | Consumes | 用时参考 |
|---|---|---|---|---|
| `/tos-funder-analyze` | 分析路由入口 — 选一个或多个策略族 | `final_action` + 汇总 | 各下游命令输出 | 2-15 min |
| `/tos-funder-value-buffett` | 巴菲特式护城河 + 财务质量评分 | `signal, confidence, facts` | price-series, iWencai 基本面 | 3-5 min |
| `/tos-funder-value-graham` | 格雷厄姆安全边际评估 | `signal, confidence, margin_of_safety` | price-series, iWencai 基本面 | 3-5 min |
| `/tos-funder-growth-fisher` | 费雪成长质量 6 维评分 | `signal, confidence, growth_quality` | price-series, iWencai 财务 | 3-5 min |
| `/tos-funder-growth-lynch` | 林奇 PEG + GARP 评估 | `signal, confidence, peg_analysis` | price-series, iWencai 财务 | 3-5 min |
| `/tos-funder-growth` | 成长聚合器 — 融合 Fisher, Lynch, quant | `growth_aggregate_signal` | Fisher, Lynch, quant-fundamentals, quant-sentiment | ~1 min |
| `/tos-funder-quant-fundamentals` | 确定性 4 维基本面评分 | `signal, confidence, scoring_breakdown` | iWencai 基本面 | 2-3 min |
| `/tos-funder-quant-price-series` | qfq OHLCV 获取 + 复权验证 | `price_series + adjustment_check` | mootdx/TDX | ~30 s |
| `/tos-funder-quant-technicals` | 本地计算 MA/RSI/MACD/ATR 等技术指标 | `signal, confidence, dimensions[]` | price-series (qfq OHLCV) | ~30 s |
| `/tos-funder-quant-sentiment` | 事件分类 + 情绪评分（公告/研报） | `signal, confidence, event_classification` | iWencai 公告 + 研报 | 2-3 min |
| `/tos-funder-tactical-catalyst` | 催化剂信号（事实/观点/价格/风险） | `tactical_catalyst_signal` | price-series, sentiment, risk-manager, iWencai | 2-3 min |
| `/tos-funder-tactical-tail-risk` | 尾部风险信号（事件/价格/流动性/数据质量） | `tail_risk_signal` | price-series, technicals, risk-manager, iWencai | 2-3 min |
| `/tos-funder-tactical` | 战术合成 — 催化剂 vs 尾部风险冲突决议 | `tactical_synthesis_signal` | catalyst + tail-risk | ~1 min |
| `/tos-funder-macro-topdown` | 市场状态/行业强弱/风险偏好代理 | `macro_topdown_signal` | iWencai 指数 + 板块 + 风格 | 1-2 min |
| `/tos-funder-risk-manager` | 个股 + 多股风险度量 | `risk_metrics + action_constraints` | price-series (qfq OHLCV) | 30 s-2 min |
| `/tos-funder-portfolio` | 组合决策合成器 — 唯一产生 final_actions 的命令 | `final_actions[] + confidence_calculation` | 全部 7 族信号 | ~1 min |

### 常见任务速查

```
# 快速看一支票的估值
/tos-funder-analyze 600519 family=value

# 全量分析 + 组合决策
/tos-funder-portfolio 002142

# 检查持仓风险
/tos-funder-risk-manager 002594

# 市场状态
/tos-funder-macro-topdown

# 事件驱动扫描
/tos-funder-tactical 601318

# 技术面快速判断
/tos-funder-quant-technicals 000858
```

### 需要注意的边界

| 情况 | 处理方式 |
|---|---|
| `adjustment_status` 为 suspect | max_dd 不可用于硬否决；action_ceiling 不超过 watch |
| `risk_metric_status` 为 degraded | sell/reject 需基本面独立确认 |
| `coverage_status` 为 blocked | 该命令不可用，跳过或降级 |
| `event` query2data | 死亡路由——用公告 + 研报搜索代替 |
| `management` 高管字段 | 死亡——仅允许分红/股本/股东人数等已验证字段 |
| 多股场景 | 用 `hoxit market bars --adjust qfq` 逐一获取，注意 trading_days 对齐 |
| C 浪 / 北交所 | 先/tos-funder-quant-price-series 确认数据可用性 |

### 数据源指引

| 要什么数据 | 用什么命令 | 来源 | 注意 |
|---|---|---|---|
| 日线 OHLCV | `hoxit market bars --adjust qfq` | mootdx/TDX | 主力数据源 |
| PE / PB / 市值 | 各命令内部调用 iWencai | iWencai | 不要从 IH 接口取 |
| 财务数据 | 各命令内部调用 iWencai | iWencai | 使用 `query -r management` 已验证字段 |
| 公告 / 研报 | `hoxit iwc search` | iWencai | 不要用 query2data |
| 技术指标 | 本地计算（RSI/MACD/ATR/MA） | 本地（基于 qfq OHLCV） | 不要依赖 iWencai 返回 |
| 概念板块 | `hoxit iwc query -q "..."` | iWencai | 用于 tactical/macro |

---

## 三、下一轮 Improvement PR 的预期方向

基于当前架构已知的薄弱点：

1. **数据覆盖完整性** — iWencai 某些字段（特别是中小盘股）可能返回空，需要 fallback 策略
2. **多股组合分析** — `portfolio` 命令目前设计为消费单股或多个独立信号，全组合优化需增强
3. **宏观数据源** — 当前 macro 命令受限于 iWencai 可查询的代理指标，缺少独立宏观 API
4. **回测框架** — 当前所有命令是点分析，无时间序列回测支持
5. **自然语言交互** — 当前依赖 `/tos-funder-analyze` 的参数化调用，可考虑更自由的自然语言输入

建议先用 2-4 周实际交易/跟踪场景来发现问题，再攒出一份有足够案例支撑的 improvement PR。
