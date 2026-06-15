#!/usr/bin/env python3
"""Run 放学之后 · SCAR — Matsukawa High sandbox milestones."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from games.campus.simulation import run_and_narrate


def _loc_zh(loc: str) -> str:
    return {
        "classroom": "教室",
        "corridor": "走廊",
        "rooftop": "天台",
        "library": "图书馆",
        "gate_slope": "校门口坡道",
        "music_room": "音乐教室",
        "levee": "河堤",
    }.get(loc, loc)


def _build_agent_brief(state: dict, out_dir: Path) -> dict:
    tags = state.get("relation_tags", {})
    xia_tag = (tags.get("xia_yang") or ["—"])[-1]
    loc = _loc_zh(state.get("location", "classroom"))
    if state.get("game_complete"):
        end_title = {
            "smile_fell": "微笑碎掉",
            "the_question": "你还好吗",
            "entrusted": "拜托你了",
            "the_letter": "展信佳",
            "unasked": "从未问起",
        }.get(state.get("ending_id", ""), "收束")
        resume = f"六十三天已尽。这一局走向「{end_title}」。"
        next_step = (
            "用文学尾声收束叙事（禁止存档行/进度行）。"
            "然后必写「## 回响 · 对主人」（EMOTIONAL_DEBRIEF.md）。"
        )
    else:
        resume = (
            f"故事停在 {state.get('calendar', '四月')}，{loc}。"
            f"夏阳那边像是「{xia_tag}」。下一场用新场景框继续。"
        )
        next_step = "主人说「继续」→ 下一场景框接写，勿输出进度/数值行。"

    return {
        "game": state.get("game"),
        "player_role": "转学生 · 第一人称「我」（仅叙事阶段）",
        "audience_role": "主人 · 只看文学叙事与终幕回响",
        "truth_source": str(out_dir / "events.jsonl"),
        "narrative_ref": str(out_dir / "outline.md"),
        "outline_ref": str(out_dir / "outline.md"),
        "resume_line": resume,
        "next_step": next_step,
        "delogified": True,
        "startup_reads": [
            "campus/GAME_CORE.md",
            "campus/AGENT_PLAYBOOK.md",
            "campus/AGENT_SESSION.md",
            "campus/PLAYER_UX.md",
            "campus/WORLDBUILDING.md",
            "campus/ANCHORS.md",
            "campus/EMOTIONAL_DEBRIEF.md",
            "campus/samples/opening.md",
            "campus/samples/rain_umbrella.md",
            "campus/samples/night_line.md",
            "campus/samples/piano_room.md",
            "campus/samples/notebook.md",
            "campus/samples/library_question.md",
            "campus/samples/crack.md",
            "campus/samples/fireworks.md",
            "campus/samples/levee.md",
            "campus/samples/ending_slope.md",
        ],
        "debrief_required": True,
        "debrief_doc": "campus/EMOTIONAL_DEBRIEF.md",
        "debrief_heading": "## 回响 · 对主人",
        "debrief_sample": "campus/samples/debrief_smile_fell.md",
        "ending_tests": {
            "smile_fell": "python run_campus.py --gentle",
            "the_question": "python run_campus.py --gentle",
            "entrusted": "python run_campus.py --watch-cheng",
            "the_letter": "python run_campus.py --gentle (full arc)",
            "unasked": "python run_campus.py --polite",
        },
        "rules": [
            "去日志化：禁止进度/存档管道行",
            "outline.md 仅 Agent 自用，禁止贴给主人",
            "每场对标 samples 留风镇密度扩写",
            "每局重写措辞，禁止照抄 samples",
            "收束后必写「## 回响 · 对主人」",
            "禁止恋爱攻略体与 CP 终选",
            "events.jsonl 仅后台，不粘贴给主人",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="放学之后 · SCAR")
    parser.add_argument("--ticks", type=int, default=None, help="Max phases (default: full 12)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--gentle", action="store_true", help="靠近与追问 → smile_fell / the_question")
    parser.add_argument("--watch-cheng", action="store_true", help="程雨守护线 → entrusted")
    parser.add_argument("--polite", action="store_true", help="礼貌到底 → unasked")
    parser.add_argument("--reach-out", action="store_true", help="(alias) same as --gentle")
    parser.add_argument("--focus-chen", action="store_true", help="(alias) same as --watch-cheng")
    parser.add_argument("--shy", action="store_true", help="(alias) same as --polite")
    parser.add_argument("--agent-brief", action="store_true", help="Write agent_brief.json")
    parser.add_argument("--quiet", action="store_true", help="Skip narrative print")
    args = parser.parse_args()

    gentle = args.gentle or args.reach_out
    watch_cheng = args.watch_cheng or args.focus_chen
    polite = args.polite or args.shy

    base = Path(__file__).resolve().parent
    out_dir = Path(args.out) if args.out else base / "output" / "campus"
    out_dir.mkdir(parents=True, exist_ok=True)

    result, narrative = run_and_narrate(
        ticks=args.ticks,
        seed=args.seed,
        gentle=gentle if (gentle or watch_cheng or polite) else None,
        watch_cheng=watch_cheng,
        polite=polite,
    )

    with (out_dir / "events.jsonl").open("w", encoding="utf-8") as f:
        for event in result.events:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    (out_dir / "outline.md").write_text(narrative, encoding="utf-8")

    world = result.world
    player = result.player
    state = {
        "game": "放学之后",
        "subtitle": "SCAR · Matsukawa High",
        "tick": world.tick if world else 0,
        "phase": world.phase if world else 0,
        "calendar": world.calendar if world else "4月8日",
        "month": world.month if world else "四月",
        "period": world.period if world else "早晨",
        "location": world.location if world else "classroom",
        "game_complete": world.game_complete if world else False,
        "ending_id": world.ending_id if world else None,
        "relations": world.relations if world else {},
        "relation_tags": world.relation_tags if world else {},
        "anchors_found": world.anchors_found if world else [],
        "skills_used": list(dict.fromkeys(world.skills_used)) if world else [],
        "chapters_reached": sorted(world.chapters) if world else [],
        "flags": {
            "gentle": world.gentle_mode if world else True,
            "watch_cheng": world.watch_cheng_mode if world else False,
            "polite": world.polite_mode if world else False,
            "asked_ok": world.asked_ok if world else False,
        },
        "objective": world.objective if world else "",
        "player": player.name if player else "我",
        "recent_thoughts": player.thoughts[-3:] if player else [],
    }
    (out_dir / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if args.agent_brief:
        brief = _build_agent_brief(state, out_dir)
        (out_dir / "agent_brief.json").write_text(
            json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    ticks_label = args.ticks if args.ticks is not None else "full"
    print(
        f"After School · SCAR | ticks={ticks_label} | complete={state['game_complete']} | "
        f"ending={state['ending_id']}"
    )
    print(f"Relations: {state['relations']}")
    print(f"Anchors: {state['anchors_found']}")
    print(f"Tags: {state['relation_tags']}")
    print(f"Output: {out_dir}")
    if not args.quiet:
        print(narrative)


if __name__ == "__main__":
    main()
