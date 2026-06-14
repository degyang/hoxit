# Trading Funder Scan: 可重复分析工作流策略

Created: 2026-06-03

## 1. 目标

将 tos-funder 从「单次命令工具箱」升级为「可重复分析工作流」：

```
当前状态:  每个命令独立运行 → 看 stdout → 一次性的
目标状态:  /tos-funder-scan 002142 --mode redundant
            ↓
            outputs/002142-宁波银行/
              ├── _report.md          ← 人工可读的完整报告
              ├── _scan-metadata.json ← 扫描元数据
              ├── value/graham.json
              ├── value/buffett.json
              ├── growth/...
              └── ...
            
            /tos-funder-scan 002142 --mode incremental
            ↓
            只更新过期的分析师输出，保留未过期的
```

核心能力：
- **冗余模式**（第一次）：跑所有分析师，每层输出独立文件，最终生成综合报告
- **增量模式**（跟踪）：判断哪些输出已过期，只跑增量，保留未过期的
- **报告驱动**：每次扫描产生一份可阅读的 `_report.md`

---

## 2. 输出目录结构

### 2.1 目录布局

```
outputs/
  <stock-code>-<股票名>/          # 例: 002142-宁波银行
    _scan-metadata.json           # {mode, timestamp, analysts_run[], errors[], ttl_config}
    _report.md                    # 完整可读报告（人工消费）
    
    # 各分析师输出（原始 JSON，机器消费）
    price-series/
      output.json
    
    value/
      buffett-output.json
      graham-output.json
    
    growth/
      fisher-output.json
      lynch-output.json
      aggregate-output.json
    
    quant/
      fundamentals-output.json
      technicals-output.json
      sentiment-output.json
    
    tactical/
      catalyst-output.json
      tail-risk-output.json
      synthesis-output.json
    
    macro/
      topdown-output.json
    
    risk/
      manager-output.json
    
    portfolio/
      decision-output.json
```

### 2.2 文件格式规范

每个分析师输出文件的内容 = 该命令的完整 JSON 输出（如 `output-schema-examples.md` 中定义的 schema）。

`_scan-metadata.json`：
```json
{
  "stock_code": "002142",
  "stock_name": "宁波银行",
  "mode": "redundant",
  "timestamp": "2026-06-03T14:00:00+08:00",
  "analysts_run": [
    {"name": "price-series", "status": "success", "duration_s": 2},
    {"name": "value-graham", "status": "success", "duration_s": 45},
    {"name": "growth-fisher", "status": "skipped", "reason": "no_new_data"}
  ],
  "errors": [
    {"name": "tactical-tail-risk", "error": "iWencai returned empty"}
  ],
  "ttl_config": {
    "price-series": "1d",
    "value-graham": "7d",
    "growth-fisher": "7d",
    "quant-technicals": "1d",
    "quant-sentiment": "1d",
    "tactical-catalyst": "1d",
    "macro-topdown": "1d",
    "risk-manager": "1d",
    "portfolio": "always"
  }
}
```

`_report.md` 的结构在第 4 节详述。

---

## 3. 模式设计

### 3.1 冗余模式（`--mode redundant`）

谁用：**首次分析一只股票**，或者用户说「重新全面分析一次」。

行为：
1. 如果输出目录已存在 → 询问确认（`rm -rf outputs/002142-宁波银行`）
2. 创建目录结构
3. 串行运行所有分析师（price-series 必须先跑，因为它是技术/风险的前置条件）
4. 每条命令的输出用 Write tool 写入对应 JSON 文件
5. 全部完成后，读取所有 JSON 文件 → 生成 `_report.md`
6. 更新 `_scan-metadata.json`

运行顺序（有依赖关系）：

```
Layer 0 — 前置条件
  price-series (提供 qfq OHLCV + adjustment_check)
  
Layer 1 — 基本面/估值（可并行）
  value-graham
  value-buffett
  growth-fisher
  growth-lynch
  quant-fundamentals

Layer 2 — 合成（等待 Layer 1）
  growth (聚合 Fisher + Lynch + quant-fundamentals)

Layer 3 — 技术/情绪（可并行，等待 price-series）
  quant-technicals
  quant-sentiment

Layer 4 — 战术/宏观（可并行）
  tactical-catalyst
  tactical-tail-risk
  macro-topdown

Layer 5 — 战术合成（等待 Layer 4 的 catalyst + tail-risk）
  tactical

Layer 6 — 风险（等待 price-series）
  risk-manager

Layer 7 — 组合决策（等待全部上层）
  portfolio
```

串行实现更简单（对于 Claude Code 执行来说），Layer 内的并行需要多轮对话交互才能实现——串行是更务实的起点。

### 3.2 增量模式（`--mode incremental`）

谁用：**跟踪已有分析过的股票**，用户昨天分析过，今天想看更新。

行为：
1. 检查输出目录是否存在
2. 读取 `_scan-metadata.json` 获取元数据
3. 用 **TTL 规则**判断每条分析师输出是否过期
4. 只运行：
   - 已过期的分析师
   - 不存在输出文件的分析师
   - 依赖链中上游有更新的分析师
5. 未过期的分析师直接从磁盘读取
6. 重新生成 `_report.md`

#### TTL 规则

| 分析师 | TTL | 理由 |
|---|---|---|
| `price-series` | 1 个交易日 | OHLCV 每日更新 |
| `quant-technicals` | 1 个交易日 | MA/RSI/MACD 每日变化 |
| `quant-sentiment` | 1 个交易日 | 新闻/公告随时出现 |
| `tactical-catalyst` | 1 个交易日 | 事件/催化剂每日变化 |
| `tactical-tail-risk` | 1 个交易日 | 风险指标每日变化 |
| `tactical` | 1 个交易日 | 合成结果随输入变化 |
| `macro-topdown` | 1 个交易日 | 市场状态每日变化 |
| `risk-manager` | 1 个交易日 | 波动率/回撤每日变化 |
| `portfolio` | always | 每次都重新合成 |
| `value-graham` | 7 天 | 基本面变化慢 |
| `value-buffett` | 7 天 | 基本面变化慢 |
| `growth-fisher` | 7 天 | 财务数据变化慢 |
| `growth-lynch` | 7 天 | 财务数据变化慢 |
| `quant-fundamentals` | 7 天 | 基本面变化慢 |
| `growth` | 7 天 | 聚合结果变化慢 |

#### 增量传播规则

如果某个分析师在 Layer N 被标记为过期并重新运行，所有依赖它的下游分析师也必须重新运行（无论它们自己的 TTL 是否过期）：

```
例: price-series 过期
  → 重新运行 price-series
  → 依赖它的 quant-technicals 重新运行（即使 TTL 未到）
  → 依赖它的 risk-manager 重新运行
  → portfolio 重新运行（always）
```

#### 强制全部重新分析

用户可以覆盖 TTL：

```
/tos-funder-scan 002142 --force
```

这会忽略所有 TTL，重新运行全部分析师（等价于 redundant 模式但保留历史目录）。

### 3.3 快速模式（`--mode quick`）

补充模式，非必须但实用。

行为：
1. 只运行 value 族 + quant-technicals + portfolio
2. 用于快速估值 + 技术面检查
3. 输出到 `outputs/<stock>/_quick-scan-<timestamp>.md`，不覆盖正式输出

---

## 4. 报告设计

### 4.1 `_report.md` 结构

```markdown
# 宁波银行 (002142) 分析报告

扫描时间: 2026-06-03 14:00
模式: redundant

---

## 一、宏观环境

{macro-topdown 的核心结论}

市场状态: 震荡
行业强弱排名: 银行 4/30
风险偏好: 中性

---

## 二、估值分析

### 格雷厄姆视角

信号: bullish | 强度: medium | 信心: 72
安全边际: 18%
关键指标: PE=6.2, PB=0.85, 股息率=3.2%

### 巴菲特视角

信号: neutral | 强度: weak | 信心: 55
护城河评分: 6/10
ROE 稳定性: 良好

---

## 三、成长分析

### 费雪视角

{...}

### 林奇视角

{...}

### 成长聚合

{...}

---

## 四、量化分析

### 基本面评分

{...}

### 技术面

{...}

### 情绪面

{...}

---

## 五、战术分析

### 催化剂

{...}

### 尾部风险

{...}

### 战术合成

立场: 谨慎观望

---

## 六、宏观视角

{...}

---

## 七、风险管理

{...}

---

## 八、组合决策

最终动作: hold
置信度: 69
推理: ...
```

### 4.2 报告生成方式

报告由 Claude Code 在全部分析师运行完成后生成：
1. 读取所有 `output.json`
2. 按照 `_report.md` 模板填充
3. 用 Write tool 写入

模板本身可以作为命令文件的一部分，或者作为一个独立的 `_report-template.md` 参考文件。

---

## 5. 实现路径

### 5.1 方案对比

| 方案 | 描述 | 优点 | 缺点 |
|---|---|---|---|
| **A. 纯命令文件** | `/tos-funder-scan` 是一个 markdown 命令，Claude Code 执行全部步骤 | 无新增基础设施；完全在 skill 范式内 | 命令文件很长（~500 行）；Claude Code 做文件管理容易出错 |
| **B. Python 编排器** | 写一个 `hoxit-scan` CLI 工具处理目录/过期逻辑，命令文件调用它 | 健壮；可测试；Claude Code 只需处理分析师输出 | 新增二进制依赖；不在 skill 范式内 |
| **C. 混合（推荐）** | `/tos-funder-scan` 命令 + `tos-funder/bin/save-output.sh` 等轻量辅助脚本 | 命令保持可读；辅助脚本处理机械操作 | 逻辑分散在两处 |

### 5.2 推荐方案：C（混合）

```
tos-funder/
  commands/
    tos-funder-scan.md      ← 编排逻辑（Claude Code 执行）
  bin/
    scan-init.sh            ← 创建目录结构 + 写入初始 metadata
    scan-check-ttl.py       ← 判断哪些分析师需要重新运行
    scan-generate-report.py ← 读取所有 JSON → 生成 _report.md
```

分工：
- **命令文件**定义工作流：什么时候跑谁，顺序，依赖关系，如何解读结果
- **辅助脚本**处理机械操作：文件存在性检查、TTL 计算、时间戳比较、报告模板渲染

这样命令文件保持为「Claude Code 可执行的策略文档」，而机械操作由脚本处理。

### 5.3 实施步骤

```
Phase 1 — 基础架构
  1. 创建 tos-funder/bin/ 目录
  2. 实现 scan-init.sh: 创建 outputs/<stock>/ 目录结构 + 写 _scan-metadata.json
  3. 实现 scan-check-ttl.py: 读取 metadata → 输出需要更新的 analyst 列表
  
Phase 2 — 命令文件
  4. 创建 tos-funder/commands/tos-funder-scan.md
  5. 实现冗余模式流程
  6. 实现增量模式流程
  
Phase 3 — 报告
  7. 实现 scan-generate-report.py: 读取全部 JSON → 输出 _report.md
  8. 迭代报告模板
  
Phase 4 — 抛光
  9. 测试完整工作流（宁波银行、茅台、比亚迪）
  10. 边界条件处理（分析师失败、数据质量 blocked、iWencai 超时）
  11. 更新 quick-guide.md 和 usage-strategy.md
```

### 5.4 命令文件关键段落示例

```markdown
# /tos-funder-scan

分析一只 A 股并保存结构化输出到 outputs/<stock>/。

## 参数

$ARGUMENTS

格式: <股票代码> [--mode redundant|incremental|quick] [--force]

默认 mode 是 redundant。

## 前置检查

1. 读取 $ARGUMENTS 解析股票代码和 mode
2. 如果 mode=incremental，检查 outputs/<stock>/ 是否存在
3. 如果不存在 → fallback 到 redundant

## 冗余模式流程

### Step 1: 初始化

```bash
bash tos-funder/bin/scan-init.sh <stock>
```

创建 outputs/<stock>/ 目录结构并写入初始 metadata。

### Step 2: 价格序列（前置条件）

运行 /tos-funder-quant-price-series <stock>。
将输出保存到 outputs/<stock>/price-series/output.json。

### Step 3: 基本面层（可并行）

运行以下命令并保存输出：
- /tos-funder-value-graham <stock>
- /tos-funder-value-buffett <stock>
- /tos-funder-growth-fisher <stock>
- /tos-funder-growth-lynch <stock>
- /tos-funder-quant-fundamentals <stock>

### Step 4: 技术/情绪层（可并行）

- /tos-funder-quant-technicals <stock>
- /tos-funder-quant-sentiment <stock>

### Step 5: 战术/宏观层（可并行）

- /tos-funder-tactical-catalyst <stock>
- /tos-funder-tactical-tail-risk <stock>
- /tos-funder-macro-topdown <stock>

### Step 6: 战术合成

- /tos-funder-tactical <stock>

### Step 7: 风险

- /tos-funder-risk-manager <stock>

### Step 8: 组合决策

- /tos-funder-portfolio <stock>

### Step 9: 生成报告

```bash
python3 tos-funder/bin/scan-generate-report.py <stock>
```

读取所有 JSON 输出，生成 _report.md。

## 增量模式流程

### Step 1: 读取元数据

读取 outputs/<stock>/_scan-metadata.json。

### Step 2: 检查 TTL

```bash
python3 tos-funder/bin/scan-check-ttl.py <stock>
```

输出需要重新运行的分析师列表 + 需要传播的下游列表。

### Step 3: 只运行过期 + 传播的分析师

针对列表中的每个分析师：
  - 运行对应的 /tos-funder-<analyst> <stock>
  - 保存输出到对应路径

### Step 4: 重新生成报告

```bash
python3 tos-funder/bin/scan-generate-report.py <stock>
```
```

---

## 6. 边界条件处理

### 6.1 分析师执行失败

- 某个分析师失败 → 不影响其他分析师
- 失败记录到 `_scan-metadata.json.errors[]`
- 报告中对应段落标注 "数据不可用"

### 6.2 数据质量 blocked

- 如果 `adjustment_check.adjustment_status == "blocked"` → 整个技术/风险层跳过
- 报告中标注 "技术分析不可用：数据质量 blocked"

### 6.3 部分分析师不存在

- 某些股票可能没有完整的 iWencai 基本面覆盖
- 覆盖率不足的分析师输出 `coverage_status: "degraded"` 或 `"blocked"`
- 报告中保留章节但标注 "coverage degraded"

### 6.4 并发安全

- Claude Code 单线程串行运行分析师
- 无需考虑并发写冲突

---

## 7. 后续扩展方向

### 7.1 多股对比

```
outputs/
  _portfolio/
    scan-2026-06-03/
      002142-宁波银行/   ← 符号链接或复制
      600519-贵州茅台/
      002594-比亚迪/
    _comparison-report.md
```

### 7.2 时间序列追踪

每次扫描记录关键指标（PE、信号值、confidence）到 `_history.json`，支持趋势可视化：

```
_history.json:
{
  "002142": [
    {"date": "2026-06-01", "portfolio_action": "watch", "confidence": 55, "pe": 6.1},
    {"date": "2026-06-02", "portfolio_action": "hold", "confidence": 69, "pe": 6.2},
    {"date": "2026-06-03", "portfolio_action": "hold", "confidence": 68, "pe": 6.2}
  ]
}
```

### 7.3 通知触发

监控 `portfolio.decision.final_action` 的变化——如果从 hold 变为 sell，触发通知。

---

## 8. 总结

| 方面 | 推荐方案 |
|---|---|
| 编排方式 | 混合：命令文件 + 辅助脚本 |
| 输出格式 | JSON（机器） + Markdown（人工） |
| 过期策略 | TTL + 传播依赖，每天一更新的短 TTL + 每周一更新的长 TTL |
| 失败处理 | 单分析师失败不影响其他，记录 error |
| 报告生成 | Python 脚本从 JSON 合成 Markdown |
| 实施顺序 | 目录管理 → 冗余模式 → 增量模式 → 报告模板 → 抛光 |
