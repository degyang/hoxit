# comps

运行行业与同业对比。

## 执行路径

```bash
hoxit uzen comps <code> [--agent-analysis <json-file>] --output-dir uzen-skills/reports
```

## 数据提供方（Data Providers）

调用 4 个 provider：
- quote, metrics, fundamentals, industry

## 输出

- `<code>-comps.json` — 行业聚焦快照
- `<code>-comps.md` — 紧凑 Markdown 报告

## 模式配置（Mode Profile）

- depth: `focused`
- primary_section: `industry`

## 同业比较模型

基于行业横向对比的可比公司分析：

### 输入数据

- 主体 PE TTM：`metrics.pe_ttm`
- 主体 PB：`metrics.pb`
- 主体行业：`fundamentals.industry`
- 同行数据：`signals.industry`（来自 `hoxit.signals.industry_comparison`）

### 计算逻辑

1. 从同行数据提取 PE/PB 值
2. 计算中位 PE 和中位 PB
3. 判断主体估值位置：
   - `below_median`：主体 PE < 中位 PE × 0.9
   - `near_median`：主体 PE 在中位 PE × 0.9 ~ 1.1 之间
   - `above_median`：主体 PE > 中位 PE × 1.1

### 输出结构

```json
{
  "status": "computed",
  "subject": { "name": "测试", "industry": "软件开发", "pe_ttm": 18.0, "pb": 2.1 },
  "rows": [
    { "name": "同行A", "code": "000001", "pe_ttm": 20.0, "pb": 2.5 },
    "..."
  ],
  "median_pe": 22.0,
  "median_pb": 2.5,
  "position": "below_median",
  "input_quality": {
    "peer_rows": 5,
    "pe_samples": 5,
    "pb_samples": 5,
    "missing": []
  },
  "warnings": []
}
```

## 说明

- 当前行为使用 `hoxit.signals.industry_comparison` 获取同行数据
- 同行数据不足时返回 `status: "data_needed"`
- iwencai 同行 fallback 已延迟——未接入 UZEN comps 运行时
