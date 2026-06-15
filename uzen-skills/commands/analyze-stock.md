# analyze-stock

运行完整 A 股 UZEN 报告。

## 执行路径

```bash
hoxit uzen analyze-stock <code> --output-dir uzen-skills/reports
```

## 数据提供方（Data Providers）

调用全部 20 个 provider（完整覆盖）：
- quote, bars, metrics, valuation, fundamentals, finance, f10
- reports, news, filings
- hot, concept, fund_flow, dragon_tiger, lockup, industry
- margin_trading, block_trade, holder_num, dividend

## 输出

- `<code>-analyze-stock.json` — 完整快照（含 sources、analysis、data_quality）
- `<code>-analyze-stock.md` — 紧凑 Markdown 报告

## JSON 结构

```json
{
  "code": "600519",
  "market": "A",
  "mode": "analyze-stock",
  "data_quality": {
    "complete": true,
    "warnings": [],
    "sources": { "...": { "quality": "full", "..." : "..." } }
  },
  "sources": { "..." : "..." },
  "analysis": {
    "summary": { "name": "...", "price": 10.0, "change_pct": 2.5 },
    "valuation": { "..." : "..." },
    "industry": { "rows": ["..."] },
    "panel": { "score": 65, "verdict": "bullish", "signals": ["..."], "vote_distribution": {"...": "..."} },
    "market_risk": { "level": "low", "basis": "market_data", "flags": [] },
    "trap_risk": { "status": "unsupported", "basis": "social_evidence", "evidence": [], "warnings": ["..."] },
    "dcf": { "status": "computed", "intrinsic_value_per_share": 25.50, "..." : "..." },
    "comps": { "status": "computed", "median_pe": 22.0, "position": "below_median", "..." : "..." },
    "mode_profile": { "depth": "standard", "primary_section": "full_report" },
    "followups": []
  }
}
```

## 分析模型

完整报告包含所有分析模型：

- **DCF 估值**：轻量 DCF 模型，5 年显式预测 + 终值
- **同业比较（Comps）**：行业中位 PE/PB 对比
- **投资者面板**：5 个确定性投资者信号
- **市场数据风险**：基于可观测市场数据的风险标记
- **社交/操纵风险**：当前状态：unsupported
