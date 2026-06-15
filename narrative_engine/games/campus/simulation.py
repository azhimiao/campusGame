"""放学之后 · SCAR — milestone sandbox simulation.

Agent = transfer student living April–June at Matsukawa High.
Engine compresses 63 days into 12 phases; Agent mode may run full sandbox.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

from core.types import Event, EventKind
from .narrative import extract_campus_narrative


@dataclass
class CampusWorld:
    tick: int = 0
    seed_id: str = "campus_after_school"
    phase: int = 0
    calendar: str = "4月8日"
    month: str = "四月"
    period: str = "早晨"
    location: str = "classroom"
    relations: dict[str, float] = field(default_factory=dict)
    relation_tags: dict[str, list[str]] = field(default_factory=dict)
    anchors_found: list[str] = field(default_factory=list)
    chapters: set[int] = field(default_factory=set)
    fired: set[str] = field(default_factory=set)
    skills_used: list[str] = field(default_factory=list)
    gentle_mode: bool = True
    watch_cheng_mode: bool = False
    polite_mode: bool = False
    asked_ok: bool = False
    game_complete: bool = False
    ending_id: str | None = None
    objective: str = "在六十三天里，辨认那些微笑底下的东西。"
    seed_npcs: dict = field(default_factory=dict)


@dataclass
class PlayerState:
    id: str = "transfer_student"
    name: str = "我"
    thoughts: list[str] = field(default_factory=list)


@dataclass
class CampusResult:
    events: list[Event] = field(default_factory=list)
    world: CampusWorld | None = None
    player: PlayerState | None = None
    seed: dict = field(default_factory=dict)


def _seed_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "seeds" / "campus_after_school.json"


def load_campus_seed() -> dict:
    return json.loads(_seed_path().read_text(encoding="utf-8"))


def _emit(tick: int, kind: EventKind, payload: dict) -> Event:
    return Event(tick=tick, kind=kind, payload=payload)


def _init_relations(seed: dict) -> dict[str, float]:
    return {
        npc_id: float(meta.get("initial_trust", 0.5))
        for npc_id, meta in seed.get("npcs", {}).items()
    }


def _init_tags(seed: dict) -> dict[str, list[str]]:
    return {
        npc_id: list(meta.get("initial_tags", []))
        for npc_id, meta in seed.get("npcs", {}).items()
    }


def _chapter(tick: int, world: CampusWorld, ch: int, title: str, **extra) -> Event:
    world.chapters.add(ch)
    world.phase = ch
    payload = {
        "chapter": ch,
        "title": title,
        "calendar": world.calendar,
        "month": world.month,
        "location": world.location,
        "period": world.period,
    }
    payload.update(extra)
    return _emit(tick, EventKind.CHAPTER, payload)


def _think(tick: int, player: PlayerState, line: str) -> Event:
    player.thoughts.append(line)
    return _emit(tick, EventKind.AGENT_THOUGHT, {"text": line})


def _trust_shift(tick: int, world: CampusWorld, npc: str, delta: float, reason: str) -> Event:
    world.relations[npc] = round(min(1.0, max(0.0, world.relations.get(npc, 0.5) + delta)), 2)
    name = world.seed_npcs.get(npc, {}).get("name", npc)
    return _emit(
        tick,
        EventKind.TRUST_SHIFT,
        {
            "npc": npc,
            "name": name,
            "delta": delta,
            "trust": world.relations[npc],
            "tags": world.relation_tags.get(npc, []),
            "reason": reason,
        },
    )


def _tag_update(tick: int, world: CampusWorld, npc: str, add: str | None, remove: str | None = None) -> Event:
    tags = world.relation_tags.setdefault(npc, [])
    if remove and remove in tags:
        tags.remove(remove)
    if add and add not in tags:
        tags.append(add)
    name = world.seed_npcs.get(npc, {}).get("name", npc)
    return _emit(
        tick,
        EventKind.WORLD_ADAPT,
        {"action": "关系标签", "npc": npc, "name": name, "tags": list(tags), "added": add, "removed": remove},
    )


def _anchor(tick: int, world: CampusWorld, seed: dict, anchor_id: str) -> Event:
    if anchor_id not in world.anchors_found:
        world.anchors_found.append(anchor_id)
    text = seed.get("anchors", {}).get(anchor_id, anchor_id)
    return _emit(tick, EventKind.CLUE_FOUND, {"id": anchor_id, "kind": "anchor", "text": text})


def _resolve_ending(world: CampusWorld) -> str:
    if world.polite_mode:
        return "unasked"
    xia = world.relations.get("xia_yang", 0.48)
    cheng = world.relations.get("cheng_yu", 0.42)
    anchors = set(world.anchors_found)

    if "anchor_letter" in anchors:
        return "the_letter"
    if world.watch_cheng_mode and "anchor_notebook" in anchors and cheng >= 0.58:
        return "entrusted"
    if world.gentle_mode and "anchor_fireworks" in anchors and xia >= 0.62:
        return "smile_fell"
    if world.gentle_mode and world.asked_ok and xia >= 0.58:
        return "the_question"
    if len(anchors) <= 1 and xia < 0.52 and cheng < 0.48:
        return "unasked"
    if world.gentle_mode and xia >= 0.55:
        return "the_question"
    if world.watch_cheng_mode and cheng >= 0.52:
        return "entrusted"
    return "unasked"


def run_campus_simulation(
    ticks: int | None = None,
    seed: int | None = None,
    *,
    shy: bool = False,
    reach_out: bool = False,
    focus_chen: bool = False,
    gentle: bool | None = None,
    watch_cheng: bool | None = None,
    polite: bool | None = None,
) -> CampusResult:
    rng = random.Random(seed)
    game_seed = load_campus_seed()
    world = CampusWorld()
    world.relations = _init_relations(game_seed)
    world.relation_tags = _init_tags(game_seed)
    world.seed_npcs = game_seed.get("npcs", {})

    # Legacy CLI aliases
    world.polite_mode = polite if polite is not None else shy
    world.watch_cheng_mode = watch_cheng if watch_cheng is not None else (focus_chen and not world.polite_mode)
    world.gentle_mode = gentle if gentle is not None else (
        (reach_out or (not world.polite_mode and not world.watch_cheng_mode))
        and not world.polite_mode
    )

    player = PlayerState()
    events: list[Event] = []

    events.append(_chapter(0, world, 0, "4月8日·转学"))
    events.append(
        _emit(
            0,
            EventKind.EXPLORE,
            {
                "action": "wake",
                "location": "classroom",
                "location_name": "教室",
                "calendar": "4月8日",
                "month": "四月",
                "period": "早晨",
                "scene": "四月的阳光像融化的黄油涂在课桌上。转学证明还攥在手里。",
                "objective": world.objective,
            },
        )
    )
    events.append(
        _think(
            0,
            player,
            "有些人的微笑是求救信号。只是我们太习惯把它当作问候。",
        )
    )

    beats = _phase_beats()
    limit = ticks if ticks is not None else len(beats)
    for t, step in enumerate(beats, start=1):
        if t > limit:
            break
        world.tick = t
        events.extend(step(world, player, game_seed, rng, t))
        if world.game_complete:
            break

    return CampusResult(events=events, world=world, player=player, seed=game_seed)


# --- phases (63-day arc compressed) ---


def _step_p1_transfer(w, p, seed, rng, t) -> list[Event]:
    if "p1" in w.fired:
        return []
    w.fired.add("p1")
    w.calendar, w.month, w.period, w.location = "4月8日", "四月", "早晨", "classroom"
    w.skills_used.append("observe")
    return [
        _chapter(t, w, 1, "4月8日·教室"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "observe",
                "skill": "observe",
                "detail": "夏阳已替你拿开旁边座位的书包；程雨从书页上方看了你不到一秒",
            },
        ),
        _tag_update(t, w, "xia_yang", "好奇的礼貌", None),
        _tag_update(t, w, "cheng_yu", "暗中观察", None),
        _trust_shift(t, w, "xia_yang", 0.03, "转学第一天·预留座位"),
        _think(t, p, "夏阳在笑。程雨在确认我有没有威胁。"),
    ]


def _step_p2_april_lunch(w, p, seed, rng, t) -> list[Event]:
    if "p2" in w.fired:
        return []
    w.fired.add("p2")
    w.calendar, w.month, w.period, w.location = "4月15日", "四月", "午休", "classroom"
    return [
        _chapter(t, w, 2, "4月15日·午休"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "observe",
                "skill": "observe",
                "npc": "xia_yang",
                "detail": "夏阳的便当只有饭团和玉子烧；她五点起床，不是为了勤劳",
            },
        ),
        _think(t, p, "一个人住。冰箱里常只有鸡蛋和米饭。"),
    ] if w.polite_mode else [
        _chapter(t, w, 2, "4月15日·午休"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "dialogue",
                "skill": "listen",
                "npc": "xia_yang",
                "line": "一个人吃？",
                "response": "习惯了。你别担心我。",
                "inner": "微笑到达眼睛，但只停留了一秒",
            },
        ),
        _trust_shift(t, w, "xia_yang", 0.05, "午饭听见独居"),
        _tag_update(t, w, "xia_yang", "微妙的试探", "好奇的礼貌"),
        _think(t, p, "她不说周末去了哪里。因为「一个人去了超市」太孤独。"),
    ]


def _step_p3_rain_umbrella(w, p, seed, rng, t) -> list[Event]:
    if "p3" in w.fired:
        return []
    w.fired.add("p3")
    w.calendar, w.month, w.location = "4月22日", "四月", "corridor"
    w.period = "放学后"
    ev = [_chapter(t, w, 3, "4月22日·雨", weather="雨，闷")]
    if w.polite_mode:
        ev.append(_think(t, p, "雨很大。我撑着自己的伞走了。"))
        return ev
    ev.append(
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "corridor",
                "location_name": "走廊",
                "scene": "梅雨前的一场雨。走廊尽头有水汽。",
            },
        )
    )
    if w.gentle_mode or w.watch_cheng_mode:
        ev.append(_anchor(t, w, seed, "anchor_umbrella"))
        ev.append(
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "dialogue",
                    "skill": "ask_ok",
                    "npc": "xia_yang",
                    "line": "你怎么总带两把伞？",
                    "response": "……习惯了。给你吧，别淋着。",
                },
            )
        )
        if w.gentle_mode:
            w.asked_ok = True
            ev.append(_trust_shift(t, w, "xia_yang", 0.06, "雨天追问折叠伞"))
        else:
            ev.append(_trust_shift(t, w, "xia_yang", 0.03, "接过伞但未深问"))
    ev.append(_think(t, p, "侧袋里的伞不是给自己，是给别人准备的。"))
    return ev


def _step_p4_may_line(w, p, seed, rng, t) -> list[Event]:
    if "p4" in w.fired:
        return []
    w.fired.add("p4")
    w.calendar, w.month, w.period = "5月3日", "五月", "夜晚"
    w.location = "classroom"
    ev = [_chapter(t, w, 4, "5月3日·夜")]
    if w.polite_mode:
        ev.append(_think(t, p, "手机亮了一下。我当作群发，没回。"))
        return ev
    if w.gentle_mode:
        ev.extend([
            _anchor(t, w, seed, "anchor_line"),
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "dialogue",
                    "skill": "listen",
                    "npc": "xia_yang",
                    "channel": "LINE",
                    "line": "睡了吗？",
                    "response": "……还没。你怎么也没睡？",
                    "inner": "深夜的夏阳和白天的不是同一个人",
                },
            ),
            _trust_shift(t, w, "xia_yang", 0.07, "深夜 LINE 没有敷衍"),
            _tag_update(t, w, "xia_yang", "信任的恐惧", None),
        ])
    else:
        ev.append(_think(t, p, "五月温热起来了。真正的对话在深夜才开始。"))
    return ev


def _step_p5_music_room(w, p, seed, rng, t) -> list[Event]:
    if "p5" in w.fired:
        return []
    w.fired.add("p5")
    w.calendar, w.month, w.location = "5月12日", "五月", "music_room"
    w.period = "放学后"
    ev = [
        _chapter(t, w, 5, "5月12日·音乐教室"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "music_room",
                "location_name": "废弃音乐教室",
                "scene": "走音的钢琴。灰尘与松香。像时间停住。",
            },
        ),
    ]
    if w.watch_cheng_mode:
        ev.extend([
            _anchor(t, w, seed, "anchor_piano"),
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "dialogue",
                    "skill": "listen",
                    "npc": "cheng_yu",
                    "line": "你为什么在这里？",
                    "response": "从她在这里弹琴的时候起。",
                },
            ),
            _trust_shift(t, w, "cheng_yu", 0.08, "音乐教室承认守护起点"),
            _tag_update(t, w, "cheng_yu", "谨慎的接纳", "无兴趣的礼貌"),
        ])
    elif w.gentle_mode and not w.polite_mode:
        ev.extend([
            _anchor(t, w, seed, "anchor_piano"),
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "observe",
                    "npc": "xia_yang",
                    "detail": "夏阳弹《卡农》到一半停住：走音了，不好听",
                    "inner": "那是她妈妈唯一教过的曲子",
                },
            ),
            _trust_shift(t, w, "xia_yang", 0.06, "音乐教室听见停住的曲子"),
        ])
    else:
        ev.append(_think(t, p, "我在门口站了一会儿，没有进去。"))
    return ev


def _step_p6_notebook(w, p, seed, rng, t) -> list[Event]:
    if "p6" in w.fired:
        return []
    w.fired.add("p6")
    w.calendar, w.month, w.location = "5月20日", "五月", "library"
    w.period = "放学后"
    ev = [_chapter(t, w, 6, "5月20日·图书馆")]
    if w.watch_cheng_mode:
        ev.extend([
            _anchor(t, w, seed, "anchor_notebook"),
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "observe",
                    "npc": "cheng_yu",
                    "detail": "笔记本角落涂黑的名字透过墨水仍可辨认",
                },
            ),
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "dialogue",
                    "npc": "cheng_yu",
                    "line": "你看到了。",
                    "response": "别告诉她。",
                },
            ),
            _trust_shift(t, w, "cheng_yu", 0.09, "笔记本秘密被看见"),
            _tag_update(t, w, "cheng_yu", "委托", "暗中观察"),
        ])
    elif w.gentle_mode:
        ev.extend([
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "dialogue",
                    "skill": "ask_ok",
                    "npc": "xia_yang",
                    "line": "你还好吗？",
                    "response": "……为什么突然问这个？",
                },
            ),
        ])
        w.asked_ok = True
        ev.append(_trust_shift(t, w, "xia_yang", 0.05, "图书馆问出那句"))
    else:
        ev.append(_think(t, p, "程雨合上笔记本走了。我假装在看目录。"))
    return ev


def _step_p7_festival_eve(w, p, seed, rng, t) -> list[Event]:
    if "p7" in w.fired:
        return []
    w.fired.add("p7")
    w.calendar, w.month, w.location = "6月1日", "六月", "classroom"
    w.period = "放学后"
    return [
        _chapter(t, w, 7, "6月1日·学园祭前夜"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "observe",
                "detail": "走廊贴满海报。夏阳扛最重的东西；程雨像与热闹无关",
            },
        ),
        _think(t, p, "六月潮湿。分别的倒计时在雨声里滴答。"),
    ]


def _step_p8_fireworks(w, p, seed, rng, t) -> list[Event]:
    if "p8" in w.fired:
        return []
    w.fired.add("p8")
    w.calendar, w.month, w.location = "6月3日", "六月", "gate_slope"
    w.period = "夜晚"
    ev = [
        _chapter(t, w, 8, "6月3日·学园祭", weather="闷热，远处海风"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "gate_slope",
                "location_name": "校门口坡道",
                "scene": "烟花升空。彩灯渐熄。",
            },
        ),
    ]
    if w.gentle_mode and not w.polite_mode and len(w.anchors_found) >= 2:
        ev.extend([
            _anchor(t, w, seed, "anchor_fireworks"),
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "observe",
                    "npc": "xia_yang",
                    "detail": "夏阳在哭。她说：对不起，烟花太刺眼了",
                    "inner": "笑容像碎玻璃掉下来",
                },
            ),
            _tag_update(t, w, "xia_yang", "卸下微笑", "信任的恐惧"),
            _trust_shift(t, w, "xia_yang", 0.1, "烟花下第一次哭"),
        ])
        if w.gentle_mode:
            w.asked_ok = True
    elif w.watch_cheng_mode:
        ev.append(
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "observe",
                    "npc": "cheng_yu",
                    "detail": "程雨站在人群外。他看见夏阳哭了，手指收紧",
                },
            )
        )
        ev.append(_trust_shift(t, w, "cheng_yu", 0.04, "看见他守了六年都没做到的事"))
    else:
        ev.append(_think(t, p, "烟花很美。我站得远，没看见谁的表情。"))
    return ev


def _step_p9_crack(w, p, seed, rng, t) -> list[Event]:
    if "p9" in w.fired:
        return []
    w.fired.add("p9")
    w.calendar, w.month, w.location = "6月8日", "六月", "corridor"
    w.period = "放学后"
    ev = [_chapter(t, w, 9, "6月8日·裂痕", weather="阴，闷")]
    if w.polite_mode:
        ev.append(_think(t, p, "空气里有什么在酝酿。我选择当作没察觉。"))
        return ev
    ev.extend([
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "dialogue",
                "npc": "cheng_yu",
                "line": "你和她在一起时，和跟我说话时不一样。",
                "response": "我也不知道哪个才是真的我。",
            },
        ),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "dialogue",
                "npc": "xia_yang",
                "line": "你每次和他聊完就更远。",
                "response": "……好像我对你来说只是消遣。",
            },
        ),
        _think(t, p, "关心有时是暴力。沉默有时也是。"),
    ])
    return ev


def _step_p10_library_truth(w, p, seed, rng, t) -> list[Event]:
    if "p10" in w.fired:
        return []
    w.fired.add("p10")
    w.calendar, w.month, w.location = "6月12日", "六月", "library"
    w.period = "放学后"
    ev = [_chapter(t, w, 10, "6月12日·图书馆")]
    if w.gentle_mode and "anchor_fireworks" in w.anchors_found:
        ev.extend([
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "dialogue",
                    "npc": "xia_yang",
                    "line": "你为什么对我这么好？",
                    "response": "因为你值得被好好对待。",
                },
            ),
            _trust_shift(t, w, "xia_yang", 0.06, "图书馆独白"),
        ])
    if w.watch_cheng_mode and w.relations.get("cheng_yu", 0) >= 0.52:
        ev.extend([
            _emit(
                t,
                EventKind.EXPLORE,
                {
                    "action": "dialogue",
                    "npc": "cheng_yu",
                    "line": "拜托你了。",
                    "response": "她一个人住。别让她以为你在可怜她。",
                },
            ),
            _trust_shift(t, w, "cheng_yu", 0.05, "托付"),
        ])
    if len(ev) == 1:
        ev.append(_think(t, p, "图书馆的夕阳把书架染成金色。今天没有人把话说完。"))
    return ev


def _step_p11_june_rain(w, p, seed, rng, t) -> list[Event]:
    if "p11" in w.fired:
        return []
    w.fired.add("p11")
    w.calendar, w.month, w.location = "6月18日", "六月", "levee"
    w.period = "放学后"
    ev = [
        _chapter(t, w, 11, "6月18日·梅雨", weather="梅雨，水声"),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "enter",
                "location": "levee",
                "location_name": "河堤",
                "scene": "梅雨泡软了世界。水流声里很难听见自己。",
            },
        ),
    ]
    if w.gentle_mode and w.relations.get("xia_yang", 0) >= 0.6:
        ev.append(
            _think(t, p, "夏阳说要试试看——没有那个微笑的她，能不能活下去。")
        )
    elif w.watch_cheng_mode:
        ev.append(
            _think(t, p, "程雨说：我欠她一千步。现在她走了，我不知道我是谁了。")
        )
    else:
        ev.append(_think(t, p, "河堤上一个人坐着的时候，全世界都离你很远。"))
    return ev


def _step_p12_ending(w, p, seed, rng, t) -> list[Event]:
    if "p12" in w.fired:
        return []
    w.fired.add("p12")
    w.calendar, w.month, w.location = "6月25日", "六月", "gate_slope"
    w.period = "放学后"
    ending = _resolve_ending(w)
    w.ending_id = ending
    w.game_complete = True
    meta = seed.get("endings", {}).get(ending, {})
    title_e = meta.get("title", ending)
    ev = [
        _chapter(t, w, 12, "6月25日·坡道", weather="梅雨将歇，风有咸味"),
    ]
    if ending == "smile_fell":
        ev.append(_think(t, p, "烟花下她的笑容碎掉了。那不是假笑——是她选出来最好的自己。"))
    elif ending == "the_question":
        ev.append(_think(t, p, "我问过你还好吗。你终于没有只用微笑回答。"))
    elif ending == "entrusted":
        ev.append(_think(t, p, "程雨把六年的重量递过来一半。接不住的部分，也在风里。"))
    elif ending == "the_letter":
        ev.append(_anchor(t, w, seed, "anchor_letter"))
        ev.append(_think(t, p, "展信佳。会笑的夏阳不是假的。她是我选出来最好的那个自己。"))
    else:
        ev.append(_think(t, p, "我从第一天起就在看她笑。却从未问过：你还好吗？"))
    ev.extend([
        _emit(t, EventKind.ENDING, {"ending_id": ending, "title": title_e, "calendar": w.calendar}),
        _emit(t, EventKind.PHASE_END, {"phase": "game", "title": title_e, "ending": ending}),
        _emit(
            t,
            EventKind.EXPLORE,
            {
                "action": "debrief_prompt",
                "required": True,
                "instruction": "叙事已尽。撰写「## 回响 · 对主人」（EMOTIONAL_DEBRIEF.md）。",
            },
        ),
    ])
    return ev


def _phase_beats() -> list:
    return [
        _step_p1_transfer,
        _step_p2_april_lunch,
        _step_p3_rain_umbrella,
        _step_p4_may_line,
        _step_p5_music_room,
        _step_p6_notebook,
        _step_p7_festival_eve,
        _step_p8_fireworks,
        _step_p9_crack,
        _step_p10_library_truth,
        _step_p11_june_rain,
        _step_p12_ending,
    ]


def run_and_narrate(
    ticks: int | None = None,
    seed: int | None = None,
    *,
    shy: bool = False,
    reach_out: bool = False,
    focus_chen: bool = False,
    gentle: bool | None = None,
    watch_cheng: bool | None = None,
    polite: bool | None = None,
) -> tuple[CampusResult, str]:
    result = run_campus_simulation(
        ticks=ticks,
        seed=seed,
        shy=shy,
        reach_out=reach_out,
        focus_chen=focus_chen,
        gentle=gentle,
        watch_cheng=watch_cheng,
        polite=polite,
    )
    prose = extract_campus_narrative(result.events, result.world, result.player)
    return result, prose
