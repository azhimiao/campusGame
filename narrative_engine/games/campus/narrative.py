"""Campus SCAR narrative — delogified prose for the master."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from core.types import Event, EventKind

if TYPE_CHECKING:
    from .simulation import CampusWorld, PlayerState

_LOC_ZH = {
    "classroom": "教室",
    "corridor": "走廊",
    "rooftop": "天台",
    "library": "图书馆",
    "gate_slope": "校门口坡道",
    "music_room": "音乐教室",
    "levee": "河堤",
}

# Agent 扩写密度标杆（提纲内提示，勿贴给主人）
_SAMPLE_REF: dict[str, str] = {
    "4月8日·转学": "campus/samples/opening.md",
    "4月8日·教室": "campus/samples/opening.md",
    "4月15日·午休": "campus/samples/lunch_alone.md",
    "4月22日·雨": "campus/samples/rain_umbrella.md",
    "5月3日·夜": "campus/samples/night_line.md",
    "5月12日·音乐教室": "campus/samples/piano_room.md",
    "5月20日·图书馆": "campus/samples/notebook.md · 或 library_question.md",
    "6月1日·学园祭前夜": "campus/samples/fireworks.md",
    "6月3日·学园祭": "campus/samples/fireworks.md",
    "6月8日·裂痕": "campus/samples/crack.md",
    "6月12日·图书馆": "campus/samples/crack.md",
    "6月18日·梅雨": "campus/samples/levee.md",
    "6月25日·坡道": "campus/samples/ending_slope.md",
}


def extract_campus_narrative(
    events: list[Event],
    world: CampusWorld | None = None,
    player: PlayerState | None = None,
) -> str:
    by_tick: dict[int, list[Event]] = defaultdict(list)
    for e in events:
        by_tick[e.tick].append(e)

    lines: list[str] = [
        "# 放学之后 · 伤痕世界",
        "",
        "> **事件提纲**（仅供 Agent 对照 `events.jsonl` 扩写，**勿直接给主人看**）",
        "",
    ]

    for tick in sorted(by_tick):
        chunk = by_tick[tick]
        for event in chunk:
            if event.kind == EventKind.CHAPTER:
                title = event.payload.get("title", "")
                if title:
                    lines.append(f"## {title}")
                    ref = _SAMPLE_REF.get(title)
                    if ref:
                        lines.append(f"> 扩写参照：`{ref}`")
                    loc = event.payload.get("location")
                    if loc:
                        loc_zh = _LOC_ZH.get(loc, loc)
                        period = event.payload.get("period", "")
                        weather = event.payload.get("weather", "")
                        bits = [b for b in [event.payload.get("calendar"), period, loc_zh, weather] if b]
                        if bits:
                            lines.append(f"> 场景框：{' · '.join(bits)}")
                    lines.append("")
                continue
            block = _render(event)
            if block:
                lines.append(block)
                lines.append("")

    if world and world.game_complete:
        lines.append("---")
        lines.append("")
        lines.append(
            "*（叙事已尽。请以 Agent 身份撰写 "
            "「## 回响 · 对主人」——见 campus/EMOTIONAL_DEBRIEF.md。）*"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render(event: Event) -> str:
    p = event.payload
    k = event.kind

    if k == EventKind.EXPLORE:
        action = p.get("action")
        if action == "wake":
            return (
                f"{p.get('calendar')}，{p.get('period', '早晨')}。{p.get('scene')}\n\n"
                f"{p.get('objective')}"
            )
        if action == "observe":
            inner = f"\n\n*{p.get('inner')}*" if p.get("inner") else ""
            return f"{p.get('detail')}。{inner}".strip()
        if action == "enter":
            loc = p.get("location_name") or _LOC_ZH.get(p.get("location", ""), "")
            scene = p.get("scene", "").strip()
            if loc and scene:
                return f"【{loc}】{scene}"
            return scene or loc
        if action == "dialogue":
            ch = f"（{p.get('channel')}）" if p.get("channel") else ""
            line = f"{ch}我说：「{p.get('line')}」\n\n对方：「{p.get('response')}」"
            if p.get("inner"):
                return f"{line}\n\n*{p.get('inner')}*"
            return line
        if action == "compress":
            return p.get("summary", "")
        if action == "debrief_prompt":
            return (
                "\n---\n\n"
                "*叙事在此收束。下一必写：「## 回响 · 对主人」"
                "（campus/EMOTIONAL_DEBRIEF.md）。*"
            )
        return ""

    if k == EventKind.AGENT_THOUGHT:
        return f"*{p.get('text')}*"

    # Delogified: anchors/trust/tags stay in events.jsonl only
    if k in (EventKind.CLUE_FOUND, EventKind.TRUST_SHIFT, EventKind.WORLD_ADAPT):
        return ""

    if k == EventKind.PHASE_END:
        if p.get("phase") == "game":
            return ""
        return ""

    if k == EventKind.ENDING:
        return ""

    return ""
