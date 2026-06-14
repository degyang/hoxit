# iWencai comprehensive_search 契约

公告搜索和研报搜索使用此契约。

## 请求

- Method: `POST`
- URL: `https://openapi.iwencai.com/v1/comprehensive/search`
- Auth: `Authorization: Bearer $IWENCAI_API_KEY`
- Content type: `application/json`

必需 Claw headers：

| Header | 取值 |
|---|---|
| `X-Claw-Call-Type` | `normal` 或 `retry` |
| `X-Claw-Skill-Id` | `announcement-search` 或 `report-search` |
| `X-Claw-Skill-Version` | `hoxit/routes.json` 中的 route version |
| `X-Claw-Plugin-Id` | `none` |
| `X-Claw-Plugin-Version` | `none` |
| `X-Claw-Trace-Id` | 每次请求新生成的 64 位十六进制 id |

公告 Payload：

```json
{
  "channels": ["announcement"],
  "app_id": "AIME_SKILL",
  "query": "贵州茅台 公告"
}
```

研报 Payload：

```json
{
  "channels": ["report"],
  "app_id": "AIME_SKILL",
  "query": "机器人行业研究报告"
}
```

## 响应

典型成功响应：

```json
{
  "data": [
    {
      "title": "文章标题",
      "summary": "文章摘要",
      "url": "文章网址",
      "publish_date": "发布时间"
    }
  ]
}
```

对 `report-search`，尽量透明传递 gateway 响应，不做业务层重组。

## 来源

复制的原始参考资料：

- `references/original-docs/report-search-api.md`
- `references/original-docs/announcement-search-api.md`
