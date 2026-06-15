# comps

运行行业与同业对比。

## 执行路径

```bash
hoxit uzen comps <code> --output-dir uzen-skills/reports
```

## Data Providers

调用 4 个 provider：
- quote, metrics, fundamentals, industry

## 输出

- `<code>-comps.json` — 行业聚焦快照
- `<code>-comps.md` — 紧凑 Markdown 报告

## Mode Profile

- depth: `focused`
- primary_section: `industry`

## 说明

当前行为使用 `hoxit.signals.industry_comparison` 获取同行数据。

iwencai 同行 fallback 已延迟——未接入 UZEN comps 运行时。
