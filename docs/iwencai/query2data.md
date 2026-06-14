# iWencai query2data 契约

所有 `hithink-*` route 使用此契约。

## 请求

- Method: `POST`
- URL: `https://openapi.iwencai.com/v1/query2data`
- Auth: `Authorization: Bearer $IWENCAI_API_KEY`
- Content type: `application/json`

必需 Claw headers：

| Header | 取值 |
|---|---|
| `X-Claw-Call-Type` | `normal` 或 `retry` |
| `X-Claw-Skill-Id` | `hoxit/routes.json` 中的原始子 skill id |
| `X-Claw-Skill-Version` | 原始子 skill version |
| `X-Claw-Plugin-Id` | `none` |
| `X-Claw-Plugin-Version` | `none` |
| `X-Claw-Trace-Id` | 每次请求新生成的 64 位十六进制 id |

Payload：

```json
{
  "query": "用户查询或改写后的金融查询语句",
  "page": "1",
  "limit": "10",
  "is_cache": "1",
  "expand_index": "true"
}
```

## 响应

典型成功响应：

```json
{
  "datas": [],
  "code_count": 0,
  "chunks_info": {}
}
```

`datas` 内部字段会随查询问题变化，不要假设固定列名。

## 空结果

如果 `datas` 为空，调用方可以最多重试两次：简化查询条件，并使用 `--call-type retry` 标记重试。

## 来源

原始本地参考资料复制在 `references/original-docs/` 下。
