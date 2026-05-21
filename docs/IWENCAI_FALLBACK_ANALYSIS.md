# iWencai 备选数据源评估

对照来源：`Reference/skills-iwencai-all`

## 已建立引用

`Reference/skills-iwencai-all` 已软链接到：

```text
/Users/mac/Projects/POS/00-System/Skills/skills-iwencai-all
```

## 可用能力

`skills-iwencai-all` 提供两类接口：

- `query2data`: `market`, `astock`, `basicinfo`, `finance`, `event`, `business`, `management`, `industry`, `sector`, `macro`, `zhishu`, `etf`, `cb`, `futures`, `futures-selector`, `hkstock`, `usstock`
- `comprehensive_search`: `announcement`, `report`

所有 route 必须使用 `scripts/routes.json` 中的原始 `X-Claw-Skill-Id`，不能统一写成 `skills-iwencai-all`。

## 实测结论

| 当前 hoxit 数据点 | 当前来源 | iWencai route | 替代性 | 说明 |
|---|---|---|---|---|
| 个股基本信息 | 东财 push2 | `basicinfo` | 高 | 实测可返回行业、上市日期、总股本、流通股。可作为 push2 断连 fallback。 |
| 个股资金流 | 东财 push2/push2his | `market` | 高 | 实测可返回主力资金、DDE 大单、小单区间净额。适合作为资金流 fallback。 |
| 行业对比/估值 | 东财 push2 | `industry` | 中高 | 实测可返回行业内股票估值/行情；但与当前“行业板块排行”结构不同，需要适配查询语句和字段。 |
| 龙虎榜 | 东财 datacenter | `event` | 中高 | 实测可返回上榜原因、营业部、买卖席位、买入/卖出/净买入额。可替代席位明细。 |
| 限售解禁 | 东财 datacenter | `event` | 中 | 简单“未来90天限售解禁”问法未返回解禁字段，需要更精确 prompt 和测试后再自动 fallback。 |
| 财务指标 | mootdx / 新浪待补 | `finance` | 高 | 实测可返回收入、归母净利、ROE、毛利率、负债率。 |
| 股东户数/前十大股东 | 东财 datacenter 待补 | `management` | 高 | 实测可返回股东户数、变化率、前十大股东、股本结构。 |
| 公告搜索 | 巨潮 cninfo | `announcement` | 高 | 实测可返回公告 PDF URL、摘要、发布日期；适合作为 cninfo 搜索失败备选。 |
| 研报搜索 | 东财 reportapi / iwencai | `report` | 已用 | 当前 hoxit 已有 `iwencai_search`，但应按 route 使用 `report-search`。 |
| 个股新闻/快讯 | 东财/财联社 | 无本地 route | 低 | `news-search` 在参考文档中存在，但本地 `routes.json` 未安装，暂不作为正式替代。 |
| 实时行情/K线/盘口 | mootdx/腾讯 | `market` | 中 | 可返回价格、涨跌幅、成交、技术指标，但不能替代五档盘口和逐笔成交。 |

## 实现建议

1. 抽一个 `hoxit.iwencai` adapter，直接复用 `skills-iwencai-all` 的 route table 设计。
2. `reports.iwencai_search()` 只保留 `report`，新增通用 `iwencai_query(route, query, limit)` 和 `iwencai_search(route, query)`。
3. 只在明确可映射字段的场景自动 fallback：`basicinfo`, `market` 资金流, `finance`, `management`, `announcement`, `event` 龙虎榜。
4. 对 `event` 解禁、`industry` 行业排行先做人工/CLI 备选，不直接替换主路径。
5. live tests 应同时覆盖主源和 iWencai fallback，避免自然语言 query 字段漂移后静默误判。
