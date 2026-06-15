# 放学之后 · SCAR · After School

> 松川高中六十三天 · Agent 文学代玩 · 终幕**回响·对主人** · 去日志化

## 仓库结构

```
campusGame/
├── campus/                  ← Agent 游戏包（上传此目录或整个仓库）
├── narrative_engine/          ← 可选引擎（run_campus.py）
└── skills/campus_after_school/
```

## 快速开始

**仅 Agent 代玩（推荐）：**

```
上传 campus/ 文件夹，读 campus/SKILL.md 与 EMOTIONAL_DEBRIEF.md。
```

**含引擎自测：**

```bash
cd narrative_engine
python run_campus.py --gentle --agent-brief --quiet
```

输出：`narrative_engine/output/campus/outline.md`（提纲，勿直接给主人看）

## 文档入口

- [campus/SKILL.md](campus/SKILL.md)
- [campus/README.md](campus/README.md)
- [campus/EMOTIONAL_DEBRIEF.md](campus/EMOTIONAL_DEBRIEF.md)
- [campus/samples/](campus/samples/) — 留风镇密度标杆

## 五结局 CLI

```bash
python run_campus.py --gentle --agent-brief --quiet       # smile_fell / the_question
python run_campus.py --watch-cheng --agent-brief --quiet  # entrusted
python run_campus.py --polite --agent-brief --quiet       # unasked
```

## 许可

源自 GameBest 产品线 · 放学之后独立发布
