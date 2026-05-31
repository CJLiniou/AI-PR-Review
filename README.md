# AI PR Review Assistant

基于 FastAPI 的 AI 驱动 GitHub PR 自动审查工具。输入 PR 链接，自动拉取代码变更，结合**规则引擎**和**大模型**生成结构化 Review 报告。支持 Web 界面、API 和命令行三种使用方式。

## 功能列表

- 解析 GitHub PR 链接，自动提取 owner / repo / pull number
- 获取 PR 元数据、变更文件（含分页）、commit 记录
- 十多条内置规则引擎：路径风险、关键词扫描、大 PR 规模检测
- 可选接入 DeepSeek / OpenAI 等大模型，生成 PR 总结、风险分析和 Review 建议
- Markdown 报告生成，Web 端渲染预览
- 勾选一键发布 Review 评论到 GitHub PR 评论区
- 风险去重合并，低置信度过滤
- 测试文件识别，高风险变更缺少测试提醒
- `.aiprignore` 忽略文件支持
- 统一 API 错误响应（400 / 403 / 404 / 502）

## 目录结构

```text
AI-PR-Review/
├── main.py                    FastAPI 应用入口
├── pyproject.toml             依赖和 CLI 入口配置
├── static/
│   └── index.html             Web 前端页面
├── src/ai_pr_review/
│   ├── ai/                    AI 客户端和 Prompt 模板
│   ├── api/                   FastAPI 路由
│   ├── github/                GitHub URL 解析、数据模型、API 客户端
│   ├── review/                规则引擎、风险检测、去重过滤
│   ├── report/                Markdown 报告生成器
│   ├── schemas/               API 请求与响应模型
│   ├── utils/                 日志工具
│   ├── cli.py                 命令行入口
│   ├── config.py              环境变量配置
│   └── exceptions.py          自定义异常类型
├── tests/                     单元测试和 API 测试
├── examples/
│   ├── demo.py                Mock 数据演示脚本
│   ├── demo_script.md         视频演示讲话稿
│   └── review_report.md       示例 Review 报告
└── docs/
    └── design.md              系统设计文档
```

## 环境要求

Python 3.10+

## 安装

```bash
# 创建虚拟环境
python -m venv .venv

# 激活（Windows PowerShell）
.\.venv\Scripts\Activate.ps1

# 激活（macOS / Linux）
source .venv/bin/activate

# 安装
pip install -e .

# 运行测试
python -m pytest
```

## 环境变量配置

在项目根目录创建 `.env` 文件（参考 `.env.example`）：

```env
# GitHub Personal Access Token（公开仓库可不填，但有 60次/小时 速率限制）
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# LLM 配置（不填 AI 相关项则走 Mock 模式，仅使用规则引擎）
LLM_API_KEY=sk-your-api-key
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1
```

> DeepSeek / OpenAI / 其他兼容 OpenAI 协议的厂商均可，只需修改 `LLM_BASE_URL`。

## 启动服务

```bash
uvicorn main:app --reload
```

浏览器打开 **http://127.0.0.1:8000** 即进入 Web 界面，或访问 **http://127.0.0.1:8000/docs** 使用 Swagger UI。

## 使用方式

### Web 界面

1. 打开 `http://127.0.0.1:8000`
2. 粘贴 GitHub PR 链接
3. 点击「开始 Review」
4. 查看报告预览、风险详情和 Markdown 原文
5. 勾选「发布评论」可将报告发到 GitHub PR 评论区

### API 调用

```bash
curl -X POST http://127.0.0.1:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"pr_url": "https://github.com/owner/repo/pull/123"}'

# 发布到 GitHub 评论区
curl -X POST http://127.0.0.1:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"pr_url": "https://github.com/owner/repo/pull/123", "publish": true}'
```

返回示例：

```json
{
  "success": true,
  "message": "PR review completed.",
  "data": {
    "pr": {"title": "...", "author": "...", "state": "open"},
    "summary": {"total_files": 6, "total_additions": 270, "total_deletions": 17},
    "ai_summary": "本 PR 在结算流程中新增优惠券校验功能...",
    "risks": [
      {
        "file": "src/checkout/service.py",
        "line": 6,
        "risk_level": "high",
        "source": "ai",
        "category": "logic",
        "message": "apply_discount 未处理边界情况",
        "suggestion": "增加防御性检查"
      }
    ],
    "markdown_report": "# AI PR Review Report\n..."
  }
}
```

### CLI

```bash
ai-pr-review review https://github.com/owner/repo/pull/123
```

### Demo 脚本（无需 Token，无需网络）

```bash
python examples/demo.py
```

## 规则引擎

内置三类规则，默认启用，无需 LLM：

| 类型 | 说明 |
|------|------|
| 路径规则 | `auth/` → 高危/安全, `payment/` → 高危/逻辑, `migration/` → 高危/逻辑, `config/` → 中危/可维护性 等 |
| 关键词规则 | `eval()`, `exec()`, `shell=True`, `chmod 777`, `DROP TABLE`, `secret` 等 |
| 规模规则 | 文件数 >20 中危、>50 高危；单文件 >300 行高危；总变更 >1000 行高危 |

## 忽略文件

创建 `.aiprignore`（参考 `.aiprignore.example`）：

```text
dist/
generated/
*.min.js
package-lock.json
```

## 错误处理

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `INVALID_PR_URL` | PR URL 格式不合法 |
| 403 | `GITHUB_AUTH_ERROR` | GitHub Token 无效 |
| 404 | `PULL_REQUEST_NOT_FOUND` | PR 不存在 |
| 502 | `GITHUB_API_ERROR` | GitHub API 异常 |
| 502 | `AI_SERVICE_ERROR` | AI 模型调用失败 |

## 视频链接
https://pan.baidu.com/s/13pu3HLMCDjLKaWPBVlpsrA?pwd=t5pz
