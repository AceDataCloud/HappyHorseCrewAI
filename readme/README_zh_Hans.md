# HappyHorse by Ace Data Cloud：CrewAI 独立原生工具

由 **Ace Data Cloud** 提供，不是 HappyHorse 或 CrewAI 官方产品。独立品牌工具包，不是通用服务合集。[English](../README.md)

## 安装

已有[GitHub预览wheel/sdist](https://github.com/AceDataCloud/HappyHorseCrewAI/releases/tag/v0.1.0-preview.1)，源码仍在审阅；尚未PyPI发布、尚未进入CrewAI官方Tools/AMP目录。先检查[源码PR](https://github.com/AceDataCloud/HappyHorseCrewAI/pulls)，用审阅后的固定完整SHA安装，不把仓库或本地导入当官方收录：

```bash
uv add 'crewai-happyhorse @ git+https://github.com/AceDataCloud/HappyHorseCrewAI.git@62936c47d3aa1d73787ae884e4e8985fe35c14f9'
```

正式PyPI发布后目标为 `uv add crewai-happyhorse`，目前不要假设可用。Python3.10–3.13；Intel macOS可能缺CrewAI强制依赖lancedb wheel，正式使用选择受支持Linux，不跳依赖伪装正常安装。


```bash
uv add 'crewai-happyhorse @ https://github.com/AceDataCloud/HappyHorseCrewAI/releases/download/v0.1.0-preview.1/crewai_happyhorse-0.1.0-py3-none-any.whl#sha256=501d1e8b96a32ab2d7cb1278e04775b1777b7f55e45f3bf4262bf042472d9027'
```

历史preview.1 wheel来自原源码fb9afa391146fa482cd47eca51698e8ad7f427f8，上方推荐源码为含终态修复的新SHA62936c47d3aa1d73787ae884e4e8985fe35c14f9，二者分别记录，URL强制SHA256校验；若附件被替换必须摘要失败。release页面/tag仅提供信息，不作信任锚。

## 注册登录、General application和专用Token

1. 打开 [Ace Applications](https://platform.acedata.cloud/console/applications?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorsecrewai_readme_zh_api_key)，注册并登录。必要时初始化General application。
2. 打开General application，确认HappyHorse权限、当前[模型价格和余额](https://platform.acedata.cloud/models?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorsecrewai_readme_zh_pricing)；服务专属应用只可使用对应授权服务。
3. 点击下图1复制已有Key，或2 **Manage Keys → Create** 创建 `HappyHorse CrewAI` 专用Key。

![真实Key复制和Manage Keys入口，凭据已遮挡](../assets/tutorial/get-api-key-en.png)

4. 按需设过期、额度限制。Allowed APIs启用时同时允许 `/happyhorse/videos`、`/happyhorse/tasks`。

![创建专用Key的真实历史截图](../assets/tutorial/create-api-key-en.png)

2026-10-18从SunoDify固定SHA `8d3d03570e73324220f111f7fe343da0792a8071` 原样复用。第二图历史名字Dify tutorial只是例子，这里填 `HappyHorse CrewAI`；没有可见真实凭据。[来源](../assets/tutorial/source.json)。

将原始API消费者Token安全写入环境变量 `ACEDATACLOUD_API_KEY`，不加Bearer/空格/引号，不用platform管理Token，不写prompt、截图或提交.env。可由密钥存储传入api_key参数，序列化不包含它。

## CrewAI粘贴位置与具名工具

```python
from crewai import Agent
from happyhorse_crewai import HappyHorseGenerateVideoTool, HappyHorseRetrieveTaskTool

agent = Agent(
    role="HappyHorse制作助手",
    goal="按已批准额度生成，并查询原任务结果",
    backstory="通过Ace Data Cloud使用HappyHorse",
    llm=your_configured_llm,
    tools=[HappyHorseGenerateVideoTool(), HappyHorseRetrieveTaskTool()],
    allow_delegation=False,
    max_retry_limit=0,
)
```

Key放环境变量，工具加入Agent的tools列表，无需MCP。工具名为 **HappyHorse by Ace Data Cloud - Generate Video / Retrieve Task**。仅添加不调用；实际付费由使用者批准。每个生成实例默认一次使用，防止重复提交，但不是资金上限/授权系统。

## 服务差异、首用与异步同ID查询

明确区分 generate、image_to_video、reference_to_video、video_edit，分别需要 prompt 以及对应 image_url/image_urls/video_url；后3项本地校验参考素材必填。分辨率是大写 `720P/1080P`，duration 3..15，可选 ratio、watermark、audio_setting auto/origin、seed。模型与动作兼容性由当前API决定，不自动换模型。

[当前目录](https://platform.acedata.cloud/models?utm_source=github&utm_medium=referral&utm_campaign=evergreen&utm_content=happyhorsecrewai_readme_zh_first_use)决定可用模型/组合和价格，模型ID原样传递，不自动fallback。下面是固定合同的示例，不是永久默认；**真实执行生成收费，本教程未执行**：

```python
import json
from happyhorse_crewai import HappyHorseGenerateVideoTool, HappyHorseRetrieveTaskTool

parameters = {
    "model": "happyhorse-1.1-t2v",
    "prompt": "A calm sunrise over a mountain lake",
    "resolution": "720P",
    "ratio": "16:9",
    "duration": 3
}
# 执行会收费，须先批准模型和额度。
submitted = HappyHorseGenerateVideoTool().run(**parameters)
submitted = json.loads(submitted)  # 先处理可能的ToolFailure，不能直接当成功。
result = HappyHorseRetrieveTaskTool().run(task_id=submitted["task_id"], wait_seconds=240)
print(result)
```

生成只提交一次async=true，accepted/pending不是成功，即使外层success=true也不例外。保存原task_id，未完成/超时/结果不明时先查历史，不重新生成。等待只查询同一ID，有界等待还可能包含在途请求的超时。终态必须有finished_at、服务success及目标媒体URL；嵌套失败和终态缺媒体不当成功。

查询自己已有任务的免费例子：

```bash
uv run python examples/query_existing.py YOUR_EXISTING_TASK_ID
```

实际查询 `POST /happyhorse/tasks`、action=retrieve、id=原ID；输出status/success/task_id/media_urls/原cost（Credits，不是USD或新账单）。不返回原prompt/请求、账户应用身份或原始诊断；URL存在不代表已验证长期可播放。

## 查看工具执行

![CrewAI官方历史真实界面，仅作交互参考，非Ace本包运行](../assets/tutorial/official-crewai-tracing.png)

[官方tracing参考](https://docs.crewai.com/en/observability/tracing)，2026-10-18取回，图中10/1/2025日期标记、版本未注明。左为执行步骤，右只展开Response；**非本包运行、非Ace调用、不承诺新GUI**。可选trace账号/认证/同意须由用户依官方规则完成，本包不启用。真实截图不要泄露Key/私人媒体。

## 常见问题

| 情况 | 处理 |
|---|---|
| 401/403 | 检查完整消费者Token、过期、服务授权、Allowed APIs与余额；403不一概等于审核。 |
| 400/本地schema失败 | 用本服务的字段、大小写及模型组合；错误跨服务字段联网前拒绝。 |
| pending/无结果 | 只查询原ID，不重新生成。 |
| 429 | 降并发等待；工具HTTP不自动重试，LLM/agent本身可能另有重试。 |
| 超时/5xx | 提交可能已到服务端，先查历史再决定是否重发。 |
| ToolFailure | 失败或终态缺正确媒体，结构化默认不可重试；联系支持用task/trace ID，别交Key。 |
| 媒体打不开 | 核终态与网络；不把URL存在当播放验收。 |

代码免费，媒体与配置的LLM按当前价格计费；无支付处理器/自动收费重试/fallback。原Credits费用按当前应用套餐折扣，不硬编码旧美元换算。不把安装/测试数当注册或收入。prompt/参考素材与Token仅发往api.acedata.cloud；本包无追踪，CrewAI/LLM设置另算。[隐私](../PRIVACY.md) · [源码](https://github.com/AceDataCloud/HappyHorseCrewAI) · [反馈](https://github.com/AceDataCloud/HappyHorseCrewAI/issues) · dev@acedata.cloud

开发：uv sync --group dev；uv run pytest；uv run ruff check .；uv build。测试Mock收费HTTP，真实Agent/Task/Crew使用本地确定性模型，不冒充真实AI决策。合同固定来源见tests/contract-source.json。

最新固定源码已修正finished_at写入前的明确失败判断；旧preview.1作为历史不变附件保留，建议用当前固定源码取得修复。
