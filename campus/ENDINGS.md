# 结局 · 伤痕世界

> 非 CP 终选。simulation 运算逻辑；Agent 对齐含义，每局重写措辞。

---

## 五种收束

| ID | 标题 | 含义 | 引擎倾向 |
|----|------|------|----------|
| **smile_fell** | 微笑碎掉 | 烟花下看见夏阳哭；笑容卸下 | `--gentle` + 锚点ε + 信任 |
| **the_question** | 你还好吗 | 问过并等待，不只得到微笑 | `--gentle` + `asked_ok` |
| **entrusted** | 拜托你了 | 程雨托付部分真相 | `--watch-cheng` + 锚点δ |
| **the_letter** | 展信佳 | 夏阳离开后的信 | 全弧 + 锚点Ω |
| **unasked** | 从未问起 | 礼貌到底，伤口未触 | `--polite` |

---

## 不是什么

- 不是「选夏阳还是选程雨」
- 不是攻略成功 / Bad End
- 同一局可能**治愈一人、伤害另一人**

---

## CLI 测试

```bash
cd narrative_engine
python run_campus.py --gentle --agent-brief --quiet      # smile_fell / the_question
python run_campus.py --watch-cheng --agent-brief --quiet # entrusted
python run_campus.py --polite --agent-brief --quiet      # unasked
```

旧别名仍可用：`--reach-out` = `--gentle` · `--focus-chen` = `--watch-cheng` · `--shy` = `--polite`

---

## 结局之后：情感回响（必做）

叙事收束 ≠ 局结束。Agent 在**文学尾声**之后写 **`## 回响 · 对主人`**（非 `存档：` 行）。

| 结局 | 回响可靠近的情绪 |
|------|------------------|
| smile_fell | 笑与泪同时发生；刺眼的不只是烟花 |
| the_question | 问出口的代价；关心是否伤人 |
| entrusted | 接过六年重量的惶恐 |
| the_letter | 「不是假的」与仍然失去 |
| unasked | 礼貌的钝痛；从未问出口 |

→ 完整协议 [EMOTIONAL_DEBRIEF.md](EMOTIONAL_DEBRIEF.md) · 标杆 [samples/debrief_smile_fell.md](samples/debrief_smile_fell.md)

---

*路径：`campus/ENDINGS.md`*
