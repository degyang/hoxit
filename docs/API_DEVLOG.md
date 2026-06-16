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

## 2026-06-16

- 来源：本机 `hoxit uzen analyze-stock 002142` 宁波银行 live 报告验收；涉及 mootdx、腾讯、东财、巨潮、iwencai、同花顺/东财信号等现有 hoxit providers。
- 触发原因：按用户要求验证 Phase 6 合并后的 UZEN 报告方向能力，目标为宁波银行 `002142`，输出 JSON/Markdown 到 `tos/90-Inbox`，不测试可视化。
- 影响接口：
  - `hoxit uzen analyze-stock 002142 --output-dir tos/90-Inbox`：真实 provider 返回形态与单元测试 mock 不完全一致，报告生成初始失败。
  - `provider.finance()`：live 返回 pandas DataFrame，原 `_map_or_skip()` 使用 `not result` 触发 `The truth value of a DataFrame is ambiguous`。
  - `provider.concept()`：live 返回 `{"total": ..., "boards": [...], "concept_tags": [...]}` dict，原 `_compact_concepts()` 只支持 `list[dict]`。
  - `provider.dragon_tiger()`：live 返回 `{"records": [...], "seats": ..., "institution": ...}` dict，原龙虎榜详情渲染只支持 list。
- hoxit 变更：
  - UZEN source quality 判断新增 `_is_empty_result()`，显式处理 `None`、DataFrame-like `.empty` 和普通容器，避免对 pandas DataFrame 做布尔判断。
  - `_compact_concepts()` 兼容 dict 形态，优先读取 `concept_tags`，否则读取 `boards[*].name`，保留原 `list[dict]` 行为。
  - 龙虎榜详情 Markdown 兼容 dict `records`，仅输出记录数和最新上榜原因，不做席位身份推断。
  - 新增 3 个 UZEN 回归测试覆盖 DataFrame-like finance、dict concept、dict dragon_tiger。
- 验证：
  - `set -a; source .env.local; set +a; .venv/bin/hoxit uzen analyze-stock 002142 --output-dir tos/90-Inbox`：生成 `002142-analyze-stock.json` 和 `002142-analyze-stock.md`，退出码 0。
  - 产物复核：报告自审 `passed`；关键章节包含研报/新闻/公告、治理与股权结构、经营与产业链、事件与催化剂、综合研判。
  - `.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v`：173 passed。
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
