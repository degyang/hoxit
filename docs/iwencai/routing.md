# iWencai Route Map

Route 定义在 `hoxit/routes.json`。route key 是本地 alias；`skill_id` 是 gateway 使用的原始 skill id。

## query2data Routes

| Route | Gateway skill id | 使用场景 |
|---|---|---|
| `astock` | `hithink-astock-selector` | A股条件筛选 |
| `basicinfo` | `hithink-basicinfo-query` | 股票、公司、基金、债券、合约等基础资料 |
| `business` | `hithink-business-query` | 主营业务、客户、供应商、子公司、合同 |
| `cb` | `hithink-cb-selector` | 可转债条件筛选 |
| `etf` | `hithink-etf-selector` | ETF 条件筛选 |
| `event` | `hithink-event-query` | 业绩预告、再融资、质押、解禁、调研、监管函 |
| `finance` | `hithink-finance-query` | 营收、利润、ROE、现金流、毛利率、负债 |
| `futures` | `hithink-futures-query` | 期货/期权数据查询 |
| `futures-selector` | `hithink-futures-selector` | 期货/期权条件筛选 |
| `hkstock` | `hithink-hkstock-selector` | 港股条件筛选 |
| `industry` | `hithink-industry-query` | 行业估值、财务、排名、行情 |
| `macro` | `hithink-macro-query` | GDP、CPI、PPI、利率、汇率、社融、M2、PMI |
| `management` | `hithink-management-query` | 股东股本、股权结构、实控人 |
| `market` | `hithink-market-query` | 价格、涨跌幅、成交量、资金流向、技术指标 |
| `sector` | `hithink-sector-selector` | 板块条件筛选 |
| `usstock` | `hithink-usstock-selector` | 美股条件筛选 |
| `zhishu` | `hithink-zhishu-query` | 指数点位、涨跌幅、成交量 |

## comprehensive_search Routes

| Route | Gateway skill id | Channel | 使用场景 |
|---|---|---|---|
| `announcement` | `announcement-search` | `announcement` | 上市公司、ETF、基金、港股公告 |
| `report` | `report-search` | `report` | 研报、评级、目标价、机构研究 |

## 本地未安装项

`TOS/90-Inbox/问财SkillHub.md` 提到了 `news-search` 和 `hithink-insresearch-query`，但 2026-05-19 创建本统一 skill 时，本地没有对应 skill 目录。只有拿到本地接口契约后，才应加入 `routes.json`。
