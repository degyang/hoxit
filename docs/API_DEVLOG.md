# hoxit 接口健壮性跟踪日志

用于记录外部数据源接口变更、`Reference/a-stock-data` 同步情况、hoxit 侧修复状态和验证结果。每次同步外部参考项目或修复线上接口异常时，在本文件追加一条记录。

## 记录模板

```markdown
## YYYY-MM-DD

- 来源：
- 触发原因：
- 影响接口：
- hoxit 变更：
- 验证：
- 后续关注：
```

## 2026-06-28

- 来源：`Reference/a-stock-data` `main` 最新提交 `8f72540`（tag `v3.2.5`）。
- 触发原因：按用户要求对照参考项目最新 CHANGELOG 同步 hoxit 相关逻辑。
- 影响接口：
  - `market.mootdx_bars`：参考项目 #31 发现 `category` 参数 mootdx `bars()` 不存在，被 `**kwargs` 静默吞掉，分钟 K 线恒退化为日线。同时复权参数 `adjust` 也不存在于 mootdx `bars()` 签名。
  - `utils.em_get` / `utils.em_post`：参考项目 glm review P1.3 建议增加连接级自动重试（瞬态错误/429/5xx 指数退避）。
  - `valuation._extract_eps_forecast`：参考项目发现旧 `iloc[2]` 实为「最小值」而非文档声明的「均值＝机构一致预期 EPS」，虽 hoxit 已按列名取值，仍需补 NaN 防护和 `[WARN]` 日志。
- hoxit 变更：
  - `hoxit/market.py`：`mootdx_bars` 参数 `category: int = 4` → `frequency: int = 9`；移除不存在的 `adjust` 参数；添加完整频率值表 docstring（8=1分钟、0=5分钟、9=日线默认等）和「不复权」警示；`_patch_mootdx_pandas_fillna_method()` 改为无条件调用（mootdx 内部可能用到 `fillna(method=...)`）。
  - `hoxit/cli.py`：`market bars` 子命令 `--category` → `--frequency`，默认 `9`；移除 `--adjust` 选项。
  - `hoxit/utils.py`：`_get_em_session()` 挂载 `HTTPAdapter + Retry`（`total=3`，指数退避，`status_forcelist=[429,500,502,503,504]`，仅 GET）；`em_get`/`em_post` 限流抖动改用 `random.uniform(0.1, 0.5)`；新增 `import random`。
  - `hoxit/valuation.py`：`_extract_eps_forecast` 增加 `pd.notna()` 防护和 `try/except` 打印 `[WARN]`，按列名取「均值」/「预测机构数」保持不变。
  - `hoxit/uzen.py`：`provider.bars()` 调用同步更新为 `frequency=9, offset=60`，移除 `adjust="qfq"`。
  - 测试：`tests/test_market.py`、`tests/test_cli.py`、`tests/test_live_endpoints.py`、`tests/test_uzen.py` 同步更新 `category` → `frequency`，移除 `adjust` 断言。
- 验证：
  - `.venv/bin/python -m pytest -q`：287 passed, 29 skipped。
- 后续关注：
  - mootdx `bars` 不复权问题长期需评估腾讯财经前复权日 K 作为替代数据源。
  - `em_get` 重试对 403 不生效（东财风控信号），住宅 IP 环境仍需靠 `EM_MIN_INTERVAL` 降频。
  - 同花顺 `worth.html` 表结构若再次变化，列名匹配的 `_extract_eps_forecast` 会 fallback 到空（已有 `[WARN]` 提示），无需紧急跟进。

## 2026-06-23

- 来源：`Reference/a-stock-data` `main` 最新提交 `e40d065`（tag `v3.2.4`）和前一提交 `3c5d8a8`（tag `v3.2.3`）。
- 触发原因：按用户要求深入检查参考项目最新 git 提交，并同步 hoxit 相关模块。
- 影响接口：
  - `reports`：参考项目新增东财行业研报 `eastmoney_industry_reports()`，与个股研报同用 `reportapi.eastmoney.com/report/list`，但 `qType=1`，`industryCode="*"` 可拉全行业，传行业码可过滤。
  - `market` / `fundamentals`：参考项目新增 `tdx_client()`，规避 mootdx 0.11.x 干净环境 `BESTIP.HQ=""` 导致裸 `Quotes.factory(market="std")` 抛 `ValueError: not enough values to unpack`。
- hoxit 变更：
  - `hoxit.reports.eastmoney_industry_reports(industry_code="*", max_pages=5, ...)` 新增行业研报列表，复用东财 `em_get` 限流和 PDF 下载记录结构。
  - CLI 新增 `hoxit reports industry --industry-code 1238 --max-pages 2`，默认 `--industry-code "*"`。
  - `hoxit.market.tdx_client()` 新增 TDX 服务器顺序探测、显式 `server=(ip, port)` 创建、`bestip=True` fallback、裸 factory fallback 和明确 RuntimeError。
  - `market` 的 quote/bars/transactions 与 `fundamentals.finance_snapshot()` / `fundamentals.f10()` 均统一走 `tdx_client()`；测试注入的 client 边界保持不变。
  - 新增静态回归测试，确保除 `hoxit/market.py` 统一 helper 外，生产代码不再直接调用 `Quotes.factory`。
  - `docs/INTERFACES.md` 增加行业研报命令示例。
- 验证：
  - `.venv/bin/python -m pytest tests/test_reports.py -q`：3 passed。
  - `.venv/bin/python -m pytest tests/test_market.py tests/test_fundamentals.py tests/test_mootdx_alignment.py -q`：20 passed。
  - `.venv/bin/python -m pytest tests/test_reports.py tests/test_cli.py -q`：17 passed。
  - `.venv/bin/python -m pytest -q`：287 passed, 29 skipped。
- 后续关注：
  - 行业码表端点在参考项目实测不可用，当前做法是允许 `industry_code="*"` 拉取后从结果反查行业码。
  - `_TDX_SERVERS` 是参考项目 2026-06 验证的服务器列表，如通达信服务器老化或网络环境变化，应更新列表或增加外部配置。

## 2026-06-20

- 来源：本机 `scripts/akdoctor.py` 默认抽样验证；AKShare 本地源码 `/Users/mac/Developments/akshare`；输出证据位于 `data/akdoctor-20260620-verify/`。
- 触发原因：用户要求验证 AKShare 接口测试失败是否来自参数错误或反爬/上游限制，并持续跟踪。
- 影响接口：
  - `scripts/akdoctor.py --out-dir data/akdoctor-20260620-verify --log`：13 个策略分类默认样本中 9 个成功、4 个失败。
  - 失败样本均为东财实时行情 `push2` 通道：`stock_zh_index_spot_em`、`forex_spot_em`、`stock_hk_spot_em`、`stock_zh_a_spot_em`。
  - 成功对照包含东财 `push2delay` 通道：`fund_etf_spot_em` 返回 1514 行；东财 `datacenter-web`：`stock_comment_em` 返回 5184 行；非东财接口如宏观、债券、空气质量、油价、新闻等均成功。
- hoxit 变更：
  - `scripts/akdoctor.py` 已区分 `ok`、`quality_empty`、`not_exported`、`missing_sample_args`、`client_parse_error`、`network_error`、`anti_bot_suspected`。
  - 默认抽样改为每类优先稳定样例；`--all` 仍逐接口覆盖。
  - 修复 pandas `Index` 真值判断误报：首轮“全部失败”中大量 `ValueError: The truth value of a Index is ambiguous` 是脚本自身问题，不是反爬。
- 验证：
  - `.venv/bin/python scripts/akdoctor.py --out-dir data/akdoctor-20260620-verify --log`：`planned=13`，`ok=9`，`failed=4`，`network_error=4`，`missing_sample_args=0`，`not_exported=0`。
  - `data/akdoctor-20260620-verify/targeted-eastmoney.jsonl`：对 4 个失败 `push2` 接口和 1 个 `push2delay` 对照接口各测 3 轮。
  - 结果：`82.push2.eastmoney.com`、`72.push2.eastmoney.com`、`48.push2.eastmoney.com`、`push2.eastmoney.com` 均为 `0/3` 成功，错误均为 `RemoteDisconnected`；`push2delay.eastmoney.com` 为 `3/3` 成功，HTTP 200，返回 `total=1514`。
  - `.venv/bin/python -m pytest -q`：`280 passed, 29 skipped`。
- 结论：
  - 当前剩余失败不是参数错误：接口函数为无参默认样例，直接第一页请求也被远端断连。
  - 当前也不是 Eastmoney 全域不可用：`push2delay.eastmoney.com` 和 `datacenter-web.eastmoney.com` 可用。
  - 更可能是当前网络/IP/请求指纹对东财 `push2` 实时行情通道触发远端快速断连，或该通道短期策略限制。
- 后续关注：
  - `akdoctor` 可继续增加 provider/domain 字段，便于按域名聚合失败。
  - 对 Eastmoney `push2` 可评估合规的 session 预热、Referer/Accept-Language 固化、指数退避和备用 `push2delay`/历史行情接口；不做验证码绕过、封禁规避或代理池撞限。
  - 若后续 `push2` 恢复，记录恢复时间和是否与访问频率/网络环境变化有关。

### Playwright 兜底验证

- 来源：`.venv/bin/python` 中已安装的 Playwright 1.60.0；验证输出 `data/akdoctor-20260620-verify/playwright-eastmoney.jsonl`。
- 方法：用 Chromium headless 打开 `https://quote.eastmoney.com/center/gridlist.html#hs_a_board`，页面返回 HTTP 200 后，在同一页面上下文中 `fetch()` 5 个 Eastmoney API。
- 结果：
  - `stock_zh_index_spot_em` 对应 `48.push2.eastmoney.com`：成功，HTTP 200，`total=268`。
  - `forex_spot_em` 对应 `push2.eastmoney.com`：成功，HTTP 200，`total=190`。
  - `fund_etf_spot_em` 对照 `push2delay.eastmoney.com`：成功，HTTP 200，`total=1514`。
  - `stock_zh_a_spot_em` 对应 `82.push2.eastmoney.com`：失败，浏览器 `fetch` 返回 `TypeError: Failed to fetch`。
  - `stock_hk_spot_em` 对应 `72.push2.eastmoney.com`：失败，浏览器 `fetch` 返回 `TypeError: Failed to fetch`。
- 结论：
  - Playwright 可以作为部分兜底：对 `requests` 断连但浏览器上下文可访问的 `push2` 接口有效，例如指数和外汇。
  - Playwright 不能作为完整兜底：A 股和港股数字 `push2` 子域在浏览器上下文中仍失败。
  - 后续实现应采用“按接口失败后可选浏览器兜底”，而不是全局默认 Playwright；并保留 `diagnosis`，标记 `browser_fallback_ok` / `browser_fallback_failed`。

### Playwright request context 复核

- 来源：`data/akdoctor-20260620-verify/playwright-request-eastmoney.jsonl`。
- 方法：继续用 Chromium 打开东财行情页，但不在页面 JS 中 `fetch()`；改用 Playwright `context.request.get()` 复用浏览器上下文发起请求，避免页面 CORS 限制。
- 结果：
  - `82.push2.eastmoney.com` / `stock_zh_a_spot_em`：HTTP 200，`total=5865`。
  - `72.push2.eastmoney.com` / `stock_hk_spot_em`：HTTP 200，`total=4670`。
  - `48.push2.eastmoney.com` / `stock_zh_index_spot_em`：HTTP 200，`total=268`。
  - `push2.eastmoney.com` / `forex_spot_em`：HTTP 200，`total=190`。
- 结论：
  - 当前没有证据表明需要人为验证码参与；没有出现验证码页、登录页或 403。
  - 先前页面 `fetch()` 中 A 股/港股失败更可能是页面上下文跨域/CORS 或 fetch 安全策略导致，不是源站业务认证失败。
  - 可行兜底方案应优先使用 Playwright `context.request`，而不是让用户手动处理验证码。

### 指数页人工验证码复测

- 来源：用户在 Playwright 打开的 `https://quote.eastmoney.com/center/gridlist.html#index_sz` 页面中手动完成图形/拖拽验证；复测输出 `data/akdoctor-20260620-verify/after-index-manual-verify.jsonl`。
- 方法：验证码完成后，连续 3 轮对比：
  - AKShare 当前指数接口使用的 `https://48.push2.eastmoney.com/api/qt/clist/get`。
  - 页面实际加载过的 `https://push2.eastmoney.com/webguest/api/qt/clist/get`。
- 结果：
  - `48.push2.eastmoney.com/api/qt/clist/get`：3/3 失败，均为 `RemoteDisconnected`。
  - `push2.eastmoney.com/webguest/api/qt/clist/get`：3/3 成功，HTTP 200，`total=902`。
- 结论：
  - 人工验证码对页面实际 host/path 有效，但没有自动放行 AKShare 当前使用的 `48.push2.eastmoney.com/api`。
  - 后续兜底不应只做“人工验证后重试原 AKShare URL”；还需要记录页面实际可用 URL，并考虑为指数接口增加 `webguest` 路径 fallback。

## 2026-06-16

- 来源：本机 `hoxit uzen analyze-stock 002142` 宁波银行 live 报告验收；涉及 mootdx、腾讯、东财、巨潮、iwencai、同花顺/东财信号等现有 hoxit providers。
- 触发原因：按用户要求验证 Phase 6 合并后的 UZEN 报告方向能力，目标为宁波银行 `002142`，输出 JSON/Markdown 到 `tos/90-Inbox`，不测试可视化。
- 影响接口：
  - `hoxit uzen analyze-stock 002142 --output-dir tos/90-Inbox`：真实 provider 返回形态与单元测试 mock 不完全一致，报告生成初始失败。
  - `provider.finance()`：live 返回 pandas DataFrame，原 `_map_or_skip()` 使用 `not result` 触发 `The truth value of a DataFrame is ambiguous`。
  - `provider.concept()`：live 返回 `{"total": ..., "boards": [...], "concept_tags": [...]}` dict，原 `_compact_concepts()` 只支持 `list[dict]`。
  - `provider.dragon_tiger()`：live 返回 `{"records": [...], "seats": ..., "institution": ...}` dict，原龙虎榜详情渲染只支持 list。
  - `provider.quote()`：mootdx 返回 `price` 和 `last_close`，但不一定直接返回 `change_pct`，原 UZEN summary 未补算涨跌幅。
- hoxit 变更：
  - UZEN source quality 判断新增 `_is_empty_result()`，显式处理 `None`、DataFrame-like `.empty` 和普通容器，避免对 pandas DataFrame 做布尔判断。
  - `_compact_concepts()` 兼容 dict 形态，优先读取 `concept_tags`，否则读取 `boards[*].name`，保留原 `list[dict]` 行为。
  - 龙虎榜详情 Markdown 兼容 dict `records`，仅输出记录数和最新上榜原因，不做席位身份推断。
  - UZEN summary 新增涨跌幅补算：优先使用 `change_pct`，缺失时用 `(price - last_close) / last_close * 100`。
  - 新增 4 个 UZEN 回归测试覆盖 DataFrame-like finance、dict concept、dict dragon_tiger、mootdx quote 涨跌幅补算。
- 验证：
  - `set -a; source .env.local; set +a; .venv/bin/hoxit uzen analyze-stock 002142 --output-dir tos/90-Inbox`：生成 `002142-analyze-stock.json` 和 `002142-analyze-stock.md`，退出码 0。
  - 产物复核：报告自审 `passed`；核心结论显示 `涨跌幅：-1.83%`，由 `price=32.1` 和 `last_close=32.7` 补算；关键章节包含研报/新闻/公告、治理与股权结构、经营与产业链、事件与催化剂、综合研判。
  - `.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v`：174 passed。
  - `.venv/bin/hoxit uzen --help`：CLI 正常输出。
  - `.venv/bin/python -m pytest`：273 passed, 29 skipped。
- 后续关注：
  - 宁波银行本次 live 报告仍显示 `f10` partial、`fund_flow` missing、DCF/Comps data_needed；后续可继续补银行股专用 ROE/COE/PB、股息率、同业样本和资金流解析。
  - `business_summary()` 对银行股的主营/产业链字段较弱，需评估是否增加银行业专用经营指标。
  - `event_summary()` 当前事件标题对宁波银行返回较薄，后续应结合公告/新闻/研报做更稳的事件归因。

## 2026-06-13

- 来源：hoxit iwencai routes.json 中的 `management`、`business`、`event` route。
- 触发原因：PR-DATA-001 扩展 hoxit 治理/经营/事件接口，补充 UZEN 工作流所需的 A 股特有数据维度。
- 影响接口：
  - `hoxit/fundamentals.py`：新增 `governance_summary()` 使用 iwencai `management` route。
  - `hoxit/fundamentals.py`：新增 `business_summary()` 使用 iwencai `business` route。
  - `hoxit/signals.py`：新增 `event_summary()` 使用 iwencai `event` route。
- hoxit 变更：
  - `fundamentals.governance_summary(code, http_post=None)`：返回实控人、股权质押比例、股东增减持、高管持股等字段。数据不足时返回 `status: "data_needed"`。
  - `fundamentals.business_summary(code, http_post=None)`：返回主营构成、客户/供应商集中度、前五大客户等字段。
  - `signals.event_summary(code, http_post=None)`：返回近期事件列表、催化剂、正面/负面事件计数。含情绪分类（positive/negative/neutral）。
  - 辅助函数：`_safe_float()`、`_extract_shareholder_changes()`、`_extract_revenue_segments()`、`_extract_top_items()`、`_extract_events()`、`_extract_catalysts()`、`_classify_event_sentiment()`。
  - 新增 19 个单元测试覆盖三个新函数的正常/异常/边界情况。
- 验证：
  - `.venv/bin/python -m pytest tests/test_fundamentals.py tests/test_signals.py tests/test_iwencai.py -v`：64 passed。
  - `.venv/bin/hoxit --help`：CLI 正常输出。
  - `git diff --check -- hoxit tests docs`：无 whitespace 问题。
- 后续关注：
  - iwencai `event` route 返回的事件字段可能因股票/时间段不同而变化，需持续观察字段名映射。
  - 情绪分类基于关键词匹配，后续可考虑接入 NLP 模型或 iwencai 内置情感字段。
  - 治理/经营数据可能需要按季度/年度区分，当前实现取最新一期。

## 2026-06-20

- 来源：AKShare `.venv` 版本 `1.18.60`，本地源码 `/Users/mac/Developments/akshare`，以及乐咕乐股/亿牛网真实 HTTP 请求。
- 触发原因：验证 AKShare 教程中 “A 股市盈率和市净率” 一组接口是否可用。
- 影响接口：
  - `stock_market_pe_lg`：AKShare 包装层可用，返回 343 行非空数据。
  - `stock_index_pe_lg(symbol="上证50")`：AKShare 包装层可用，返回 5209 行非空数据。
  - `stock_market_pb_lg`：AKShare 包装层可用，返回 5210 行非空数据。
  - `stock_index_pb_lg(symbol="上证50")`：AKShare 包装层可用，返回 5209 行非空数据。
  - `stock_hk_indicator_eniu(symbol="hk00700", indicator="市盈率")`：AKShare 包装层可用，返回 4009 行非空数据。
  - `stock_a_high_low_statistics(symbol="all")`：源站 `www.legulegu.com/stockdata/member-ship/get-high-low-statistics/all` 可用，返回 500 条真实 JSON；但 `.venv` 中 AKShare `1.18.60` 仍按旧的数组日期结构解析，当前源站返回 `YYYY-MM-DD` 字符串，包装层报 `TypeError: 'str' object cannot be interpreted as an integer`。本地 `/Users/mac/Developments/akshare` 源码已改为 `pd.to_datetime(..., errors="coerce")`，该接口属于包装层版本滞后，不是反爬或参数错误。
  - `stock_a_below_net_asset_statistics(symbol="全部A股")`：源站 `legulegu.com/stockdata/below-net-asset-statistics-data` 可用，返回 5198 条真实 JSON；但当前返回字段为 `belowNetAsset`、`totalCompany`、`date`、`close`，不再包含旧实现删除的 `marketId`，且 `date` 已是字符串而非毫秒时间戳，包装层报 `KeyError: 'marketId'`。该接口属于 AKShare 包装层字段适配问题，不是反爬或参数错误。
- 验证：
  - `.venv/bin/python` 直接调用上述 7 个 AKShare 函数；前 5 个返回非空 DataFrame，后 2 个在包装层异常。
  - 直接请求乐咕乐股源站，`stock_a_high_low_statistics` 的 `all`、`sz50`、`hs300`、`zz500` 均 HTTP 200 且返回 500 条 JSON。
  - 直接请求破净股源站，`全部A股`、`沪深300`、`上证50`、`中证500` 均 HTTP 200 且返回 4720-5209 条 JSON。
  - 证据文件：`data/akdoctor-20260620-verify/valuation-market-breadth-check.jsonl`、`data/akdoctor-20260620-verify/legulegu-raw-check.jsonl`。
- 后续关注：
  - 若 hoxit 需要直接使用这两个市场宽度接口，应在 hoxit 侧按当前 JSON 字段实现适配，不应简单依赖 AKShare `1.18.60` 包装层。
  - `stock_a_high_low_statistics` 可通过升级/同步本地 AKShare 源码中的日期解析修复。
  - `stock_a_below_net_asset_statistics` 仍需补丁：兼容字符串日期，并按 `belowNetAsset`、`totalCompany`、`date` 生成输出列。

## 2026-06-10

- 来源：本机 hoxit 完整命令链实测；参考 `Reference/a-stock-data/CHANGELOG.md` v3.2.2 中关于东财风控、巨潮 orgId、概念板块、资金流接口的说明。
- 触发原因：运行 `tos-funder` 宁波银行 `002142` full workflow 时，发现仅依赖 iWencai 会造成 forward EPS/PE、外部新闻、正式公告、行业相对强弱等证据不足；同时发现 `fundamentals f10` 在当前 mootdx `StdQuotes` 上直接失败。
- 影响接口：
  - `hoxit fundamentals f10 002142`：当前 mootdx client 无 `f10()` 方法，原实现直接抛出 `'StdQuotes' object has no attribute 'f10'`，会中断完整命令链。
  - `hoxit signals fund-flow 002142 --days 20`：本次返回空数组；未确认是源端空数据、东财风控、还是解析问题。
  - `hoxit reports eastmoney 002142 --max-pages 2`：返回 200 条研报，部分包含 `predictThisYearEps`、`predictNextYearEps`、`predictThisYearPe`、`predictNextYearPe`，可补强 forward valuation。
  - `hoxit news stock 002142`：返回 20 条东财个股新闻，可补强 iWencai report-only sentiment。
  - `hoxit filings cninfo 002142 --start-date 20250101 --end-date 20260610`：返回 30 条公告，可作为正式事件事实源。
  - `hoxit signals concept 002142`、`hoxit signals industry --top-n 30`：可补强银行/城商行/破净股等板块与行业相对强弱。
- hoxit 变更：
  - `fundamentals.f10()` 增加能力检测：client 有 `f10` 时照旧调用；无 `f10` 时返回 `{"status": "unsupported", "sections": {}, "warnings": [...]}`，不再中断 CLI。
  - 新增 `hoxit.tos_funder` helper：完整 full-run 层清单、manifest 校验、稳定 sample stdev、入口文件写入、非 iWencai 替代源评估。
  - 新增/更新测试覆盖 F10 降级、full-run 22 层校验、非 iWencai 替代评估。
- 验证：
  - `.venv/bin/hoxit fundamentals f10 002142`：返回结构化 unsupported JSON，退出码 0。
  - `.venv/bin/hoxit reports eastmoney 002142 --max-pages 2`：返回 200 条，含 forward EPS/PE 字段。
  - `.venv/bin/hoxit news stock 002142`：返回 20 条。
  - `.venv/bin/hoxit filings cninfo 002142 --start-date 20250101 --end-date 20260610`：返回 30 条。
  - `.venv/bin/hoxit signals concept 002142`：返回 19 个板块标签。
  - `.venv/bin/hoxit signals industry --top-n 30`：返回行业榜，银行/城商行进入样本。
  - `python3 -m pytest tests/test_tos_funder.py tests/test_fundamentals.py -q`：`9 passed`。
- 后续关注：
  - 继续排查 `signals fund-flow` 对 `002142` 返回空的原因，区分源端空数据、风控、解析或字段变更。
  - 为银行股估值增加 ROE/COE/PB、股息率、前瞻 EPS 的专用估值 helper，减少 Damodaran/DCF 对普通 FCFF 的误用。
  - 如需完整新闻情绪，优先增强 `news stock` 与公告/研报联合分类，而不是把 iWencai report search 当作唯一情绪源。

## 2026-06-09

- 来源：`Reference/a-stock-data` `main`，最新提交 `9379ab9`，标签 `v3.2.2`。
- 触发原因：按用户要求，深入参考上游项目和财联社新版网页实际逻辑，检查 news 源接口中的财联社是否可用。
- 影响接口：
  - 财联社快讯：参考项目 `v3.2` 标记下线的是旧 `https://www.cls.cn/nodeapi/telegraphList`，本机 2026-06-09 实测返回 HTTP 404。
  - 财联社新版 `/telegraph` 页面先用 `https://www.cls.cn/api/cache?name=telegraph` 取首页缓存，但完整滚动列表依赖 `https://www.cls.cn/v1/roll/get_roll_list`，该接口直连无签名会返回 `{"errno":"10012","msg":"签名错误"}`。
  - 前端 `request` 封装会补 `os=web`、`sv=8.7.9`、`app=CailianpressWeb`，按 key 排序拼接参数字符串，再生成 `sign=md5(sha1(param_string))`。该签名为前端静态算法，无需用户申请 key。
- hoxit 变更：
  - `news.cls_flash()` 改为调用签名后的 `https://www.cls.cn/v1/roll/get_roll_list`，不再把 `api/cache` 首页缓存当作正式快讯列表接口。
  - 增加 `_cls_sign()` / `_cls_param_string()` 复现财联社前端签名。
  - 更新 CLI help 与 `docs/INTERFACES.md` 中 `news cls` 说明。
- 验证：
  - `.venv/bin/python - <<'PY' ... news.cls_flash(page_size=5) ... PY`
  - `.venv/bin/python - <<'PY' ... requests.get('https://www.cls.cn/nodeapi/telegraphList') / requests.get('https://www.cls.cn/v1/roll/get_roll_list') ... PY`
  - 结果：`nodeapi/telegraphList` 返回 404；`v1/roll/get_roll_list` 不带 `sign` 返回 `10012`，带 `sign` 返回 HTTP 200 且含 `data.roll_data`。
- 后续关注：
  - 财联社签名算法来自网页前端包，不是官方稳定 API；若后续返回签名错误、空数据或结构变化，应更新签名逻辑或将 `news cls` 再次标记为不可用并默认推荐 `news.global_news()`。

## 2026-06-09

- 来源：`Reference/a-stock-data` `main`，最新提交 `9379ab9`，标签 `v3.2.2`。
- 触发原因：检查近期参考项目变更，并同步相关接口变更到 hoxit。
- 影响接口：
  - 概念板块：百度 PAE `getrelatedblock` 失效后，参考项目改为东财 `slist`，hoxit 已使用 `signals.eastmoney_concept_blocks()`，并保留 `baidu_concept_blocks` 兼容别名。
  - 巨潮公告：`orgId` 不再按 `gssx0{code}` 机械拼接，hoxit 已通过 `utils.get_cninfo_org_id()` 动态拉取 `szse_stock.json` 映射。
  - 东财接口：hoxit 已统一使用 `utils.em_get()` 做串行限流、会话复用和请求头合并。
  - 东财个股新闻：hoxit 已兼容 `result.cmsArticleWebOld` 直接返回 list，以及旧的 `{list: [...]}` 结构。
  - 财联社快讯：旧公开接口已不可依赖，hoxit `news.cls_flash()` 标记弃用并建议使用 `news.global_news()`。
- hoxit 变更：
  - 在 `utils.py` 增加 `_CNINFO_KNOWN_ORGIDS` 离线兜底映射，覆盖参考项目明确提到的异常样例和测试用例：`601318`、`601398`、`688017`、`832000`。
  - 在线 `szse_stock.json` 映射仍然优先，只有拉取失败或缺失时才使用已知兜底，最后再回退老规则。
- 验证：
  - `pytest -q`
  - 结果：`71 passed, 26 skipped`
- 后续关注：
  - 定期对照 `Reference/a-stock-data/CHANGELOG.md` 的最新标签，优先检查东财、巨潮、同花顺、iwencai 相关解析和参数变更。
  - 如果巨潮动态映射端点不稳定，应考虑将最近成功拉取的 orgId 映射持久化到本地缓存文件。
  - `docs/INTERFACES.md` 中“百度概念板块”命名仍保留旧称，后续可改为“东财概念板块”并说明兼容别名。
