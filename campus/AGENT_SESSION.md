# 会话与进度 · SCAR（去日志化）

> 主人**不读日志**。推进 = 新场景框的日期；收束 = 文学尾声 + 回响。

---

## 完整一局

| 阶段 | 主人看到什么 |
|------|----------------|
| 推进 | 第一人称叙事 + `📍 日期·时段` 场景框 |
| 收束 | 文学性尾声（季节、分别、余韵） |
| 终幕 | `## 回响 · 对主人` |

**无** `进度：` / `存档：` 行。

---

## 续玩

主人说「继续」→ Agent 用**下一场景框**自然衔接，勿贴 JSON、勿报数值。

模式 B：`state.json` / `events.jsonl` 仅 Agent **自用**对齐，禁止粘贴给主人。

---

## 启动语

```
上传 campus/。读 SKILL.md、AGENT_PLAYBOOK、samples/（留风镇密度）。
4月8日场景框开场。每场写满再切下一场；禁止进度行。
引擎 outline.md 仅自用对照，禁止贴给主人。
收束后写「## 回响 · 对主人」。
```

## 密度与引擎

| 每轮 | ≥1 完整场景，对标 [samples/rain_umbrella.md](samples/rain_umbrella.md)（约 400–900 字） |
| 模式 B | `events.jsonl` + `outline.md` = **提纲**；主人只看 Agent 扩写 |

```bash
python run_campus.py --gentle --agent-brief --quiet
```

---

*路径：`campus/AGENT_SESSION.md`*
