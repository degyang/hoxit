# PR-LIVE-006: hoxit Playwright Fallback Provider Foundation

## Goal

为 hoxit 建立可复用的浏览器兜底基础设施接口，为未来 F10/银行专项/snapshot 等网页兜底能力打下基础。

## Scope

### In Scope

- `hoxit/web_fallback.py` — 新模块，包含：
  - 错误分类体系：`WebFallbackError` 层级（timeout / navigation / extraction / auth_required / captcha）
  - 结果数据结构：`WebFetchResult`（fields, errors, source_url, quality, timestamp）
  - Provider 协议：`WebFallbackProvider` 抽象接口（fetch, is_available, close）
  - Fake driver：`FakeWebDriver` 用于测试，可注入预设页面内容
  - 默认关闭机制：`HOXIT_WEB_FALLBACK=1` 环境变量启用
  - 用户协助请求：当遇到 auth/captcha 时生成结构化 `UserAssistanceRequest`
- `tests/test_web_fallback.py` — 全部用 fake driver，不依赖网络/浏览器
- 文档更新：`docs/INTERFACES.md`、`uzen-skills/README.md`

### Out of Scope

- 不接入 UZEN 生产路径（uzen.py 不 import web_fallback）
- 不抓取具体数据源（不做同花顺/东财/巨潮页面抓取）
- 不引入 akshare
- 不做可视化
- 不做 Playwright 安装/配置
- 需要登录/Cookie/浏览器 profile 的场景只做用户协助请求，不自动处理

## Tests

1. `WebFetchResult` 构造与字段访问
2. 错误分类：timeout / navigation / extraction / auth_required / captcha
3. `FakeWebDriver` 注入预设内容 → fetch 返回预期字段
4. `FakeWebDriver` 注入错误 → fetch 返回预期错误分类
5. `UserAssistanceRequest` 结构化输出
6. 默认关闭：无环境变量时 `create_provider()` 返回 None
7. 字段级 quality 标注（available / missing / error）

## Acceptance

- [ ] `python -m pytest tests/test_web_fallback.py -v` 全部通过
- [ ] `python -m pytest` 全套通过（无回归）
- [ ] `docs/INTERFACES.md` 更新
- [ ] 不引入新第三方依赖（仅 stdlib + pytest）
- [ ] 环境变量默认关闭
