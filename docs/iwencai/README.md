# hoxit iWencai 接口资料

本目录归档从 POS `trading-iwencai` skill 迁入 hoxit 的 iWencai 接口资料。运行时代码已移植到 `hoxit.iwencai`、`hoxit/routes.json` 和 CLI 子命令中，原 skill 不再保留脚本或 reference 文档副本。

## 文档入口

| 文件 | 说明 |
|---|---|
| `routing.md` | hoxit route alias、上游 gateway skill id 和使用场景 |
| `query2data.md` | `POST /v1/query2data` 请求头、payload 和响应契约 |
| `comprehensive-search.md` | 公告/研报 `POST /v1/comprehensive/search` 契约 |
| `design.md` | 从分散 iWencai skills 合并为统一入口的设计记录 |
| `问财SkillHub.md` | iWencai SkillHub 能力索引整理 |
| `original-docs/` | 迁移时保留的原始 API 文档 |

## hoxit 对应实现

- 路由配置：`hoxit/routes.json`
- Python 适配器：`hoxit/iwencai.py`
- CLI 入口：`hoxit/cli.py`
- 统一 CLI：`hoxit iwc routes`、`hoxit iwc query`、`hoxit iwc search`
- 研报快捷入口：`hoxit reports iwencai`
- Skill 兼容入口：`/Users/mac/Projects/POS/00-System/Skills/skills-trading-iwencai/trading-iwencai/commands/`

调用 iWencai OpenAPI 前需要设置 `IWENCAI_API_KEY`。每次请求必须保留 `hoxit/routes.json` 中原始子能力的 `skill_id`，不能统一替换成 `trading-iwencai`。
