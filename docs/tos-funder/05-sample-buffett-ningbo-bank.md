# Sample: Buffett Analysis for 宁波银行

This sample shows the expected output shape for `tos-funder-value-buffett`.

## Command

```text
/tos-funder-value-buffett 宁波银行
```

## Data Quality

| Area | Status |
|---|---|
| Basic company data | covered by `basicinfo` |
| Financial metrics | covered by `finance` |
| Market valuation | covered by `market` |
| Capital allocation | covered by `finance`, partially by `management` |
| Events | covered by `event`, `announcement` |
| Owner earnings | sector-adjusted because this is a bank |

## Facts Bundle

```text
target:
  code: 002142.SZ
  name: 宁波银行
  industry: 银行 / 城商行
  date: 2026-06-01

data_quality:
  route_coverage: basicinfo, finance, market, event, announcement
  missing_fields: bank asset-quality details need deeper report/annual-report review
  fallback_used: none

scores:
  original_buffett:
    fundamentals: 2/7
    consistency: 3/3
    moat: 3/5
    management: 2/2
    pricing_power: 3/5
    book_value_growth: 4/5
    total: 17/27

valuation:
  method: bank_adjusted
  market_cap: 2074.19 亿
  pb: 0.89
  pe_ttm: 6.89
  margin_of_safety: medium

signal:
  signal: neutral
  confidence: 68
  action: watch
  reasoning: Good bank quality and low PB, but ROE is falling and bank-adjusted valuation limits confidence.
```

## Expected Report Summary

宁波银行属于质量较高、估值不贵、但需要按银行业口径降级评估安全边际的标的。它不是差公司，也不是明显高估；但巴菲特策略要求“好业务 + 明确安全边际”。当前 ROE 下行、银行资产质量不透明、Owner Earnings DCF 不适合银行股，因此最终动作是 `watch`。

## Implementation Notes

- Do not force standard industrial-company DCF on banks.
- Use `bank_adjusted` valuation.
- Use `ROE + PB + BVPS growth + dividend + asset quality risk`.
- If asset quality fields are insufficient, keep confidence below high-conviction levels.
