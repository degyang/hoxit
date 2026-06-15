# dcf

运行轻量估值视图。

## 执行路径

```bash
hoxit uzen dcf <code> --output-dir uzen-skills/reports
```

## 数据提供方（Data Providers）

调用 5 个 provider：
- quote, metrics, valuation, fundamentals, finance

## 输出

- `<code>-dcf.json` — 估值聚焦快照
- `<code>-dcf.md` — 紧凑 Markdown 报告

## 模式配置（Mode Profile）

- depth: `focused`
- primary_section: `valuation`

## 限制

第一版使用 hoxit 可用的估值和预测字段。完整 UZI DCF 对标已延迟。
