from __future__ import annotations

import math
import sys
import time
from pathlib import Path
from typing import Any

from soccer_env import GameConfig, SoccerEnv
from organizer_rl_bot.policy import OrganizerRLOpponent

BASE_DIRECTORY = Path(__file__).resolve().parent

DIRECTION_VECTORS: dict[str, tuple[int, int]] = {
    "STAY": (0, 0),
    "UP": (0, 1),
    "UP_RIGHT": (1, 1),
    "RIGHT": (1, 0),
    "DOWN_RIGHT": (1, -1),
    "DOWN": (0, -1),
    "DOWN_LEFT": (-1, -1),
    "LEFT": (-1, 0),
    "UP_LEFT": (-1, 1),
}
MOVES = list(DIRECTION_VECTORS)

def _line_hits_box(x1: float, y1: float, x2: float, y2: float, obs: dict[str, Any], pad: float = 2.0) -> bool:
    min_x, max_x = obs["x"] - pad, obs["x"] + obs["width"] + pad
    min_y, max_y = obs["y"] - pad, obs["y"] + obs["height"] + pad
    dx, dy = x2 - x1, y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - min_x, max_x - x1, y1 - min_y, max_y - y1]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-9:
            if qi < 0: return False
        else:
            t = qi / pi
            if pi < 0:
                if t > u2: return False
                if t > u1: u1 = t
            else:
                if t < u1: return False
                if t < u2: u2 = t
    return u1 <= u2

def _move_is_safe(obs: dict[str, Any], move: str) -> bool:
    if move == "STAY": return True
    state = obs["state"]
    me = state["players"][obs["player_id"]]
    field = state["field"]
    vx, vy = DIRECTION_VECTORS[move]
    length = math.hypot(vx, vy) or 1.0
    x = me["x"] + vx / length * 4.0
    y = me["y"] + vy / length * 4.0
    if x - 3.0 < 0 or x + 3.0 > field["width"] or y - 3.0 < 0 or y + 3.0 > field["height"]:
        return False
    for o in state.get("obstacles", []):
        cx = min(max(x, o["x"]), o["x"] + o["width"])
        cy = min(max(y, o["y"]), o["y"] + o["height"])
        if math.hypot(x - cx, y - cy) < 3.25:
            return False
    return True

def _safe_move(obs: dict[str, Any], pref: str) -> str:
    pref_vec = DIRECTION_VECTORS[pref]
    choices = [m for m in MOVES if m != "STAY" and _move_is_safe(obs, m)]
    if not choices: return "STAY"
    return max(choices, key=lambda m: (DIRECTION_VECTORS[m][0]*pref_vec[0] + DIRECTION_VECTORS[m][1]*pref_vec[1], m == pref))

def direction_toward(dx: float, dy: float, dead_zone: float = 6.0) -> str:
    h = "" if abs(dx) <= dead_zone else ("RIGHT" if dx > 0 else "LEFT")
    v = "" if abs(dy) <= dead_zone else ("UP" if dy > 0 else "DOWN")
    return f"{v}_{h}" if v and h else v or h or "STAY"

def make_tuned_policy(radar_dist: float = 16.0, carry_steps: int = 3, def_offset: float = 3.0, ball_lead: float = 1.0):
    def policy(observation: dict[str, Any], kick_power: int = 3) -> dict[str, Any]:
        player_id = observation["player_id"]
        opponent_id = observation["opponent_id"]
        state = observation["state"]
        me = state["players"][player_id]
        opponent = state["players"][opponent_id]
        ball = state["ball"]
        attack = observation["attack_direction"]
        sign = 1 if attack == "UP" else -1
        width = float(state["field"]["width"])
        height = float(state["field"]["height"])
        obstacles = state.get("obstacles", [])

        if ball["possession"] == player_id:
            distance_to_goal = height - me["y"] if sign > 0 else me["y"]
            possession_steps = int(ball.get("possession_steps", 0))
            opp_ahead = (
                sign * (opponent["y"] - me["y"]) > 0
                and abs(opponent["x"] - me["x"]) < 12
                and math.hypot(opponent["x"] - me["x"], opponent["y"] - me["y"]) < 55
            )
            side = "LEFT" if opponent["x"] >= me["x"] else "RIGHT"
            dribble = f"{attack}_{side}" if opp_ahead else attack
            move = _safe_move(observation, dribble)

            if distance_to_goal > 50 and possession_steps < carry_steps:
                return {"move": move}

            primary_dir = dribble if opp_ahead else direction_toward(
                width / 2.0 - me["x"], sign * distance_to_goal, dead_zone=6.0
            )

            vx, vy = DIRECTION_VECTORS[primary_dir]
            vlen = math.hypot(vx, vy) or 1.0
            hits_obs = any(
                _line_hits_box(me["x"], me["y"], me["x"] + vx / vlen * radar_dist, me["y"] + vy / vlen * radar_dist, o, pad=2.0)
                for o in obstacles
            )

            powers = observation["action_space"]["kick"]["power"]
            power = min(max(powers), max(min(powers), kick_power))

            if not hits_obs:
                return {"move": move, "kick": {"direction": primary_dir, "power": power}}

            alt_candidates = [f"{attack}_LEFT", f"{attack}_RIGHT", attack]
            for cand in alt_candidates:
                if cand == primary_dir:
                    continue
                cvx, cvy = DIRECTION_VECTORS[cand]
                cvlen = math.hypot(cvx, cvy) or 1.0
                if not any(
                    _line_hits_box(me["x"], me["y"], me["x"] + cvx / cvlen * radar_dist, me["y"] + cvy / cvlen * radar_dist, o, pad=2.0)
                    for o in obstacles
                ):
                    return {"move": move, "kick": {"direction": cand, "power": power}}

            if possession_steps >= 6:
                return {"move": move, "kick": {"direction": primary_dir, "power": min(powers)}}
            return {"move": move}

        target_x, target_y = ball["x"], ball["y"]
        if ball["status"] == "moving":
            velocity = ball.get("velocity", {})
            target_x += ball_lead * float(velocity.get("x", 0.0))
            target_y += ball_lead * float(velocity.get("y", 0.0))
        elif ball["possession"] == opponent_id:
            defend_sign = -1 if attack == "UP" else 1
            target_y += defend_sign * def_offset
            target_x += -def_offset if opponent["x"] > width / 2.0 else def_offset
        preferred = direction_toward(target_x - me["x"], target_y - me["y"], dead_zone=0.6)
        return {"move": _safe_move(observation, preferred)}
    return policy

def run_parameter_search():
    config = GameConfig.from_json("config/game.json")
    organizer = OrganizerRLOpponent()
    seeds = list(range(8000, 8100))

    configs = [
        {"name": "Baseline (radar=16, carry=3, def=3, lead=1.0)", "radar": 16.0, "carry": 3, "def": 3.0, "lead": 1.0},
        {"name": "Variant A (carry=2, faster shots)", "radar": 16.0, "carry": 2, "def": 3.0, "lead": 1.0},
        {"name": "Variant B (lead=1.5, faster intercepts)", "radar": 16.0, "carry": 3, "def": 3.0, "lead": 1.5},
        {"name": "Variant C (def=4.0, deeper cover)", "radar": 16.0, "carry": 3, "def": 4.0, "lead": 1.0},
        {"name": "Variant D (radar=14, closer clearances)", "radar": 14.0, "carry": 3, "def": 3.0, "lead": 1.0},
        {"name": "Variant E (carry=2, lead=1.5, def=3.5)", "radar": 16.0, "carry": 2, "def": 3.5, "lead": 1.5},
    ]

    for cfg in configs:
        pol = make_tuned_policy(cfg["radar"], cfg["carry"], cfg["def"], cfg["lead"])
        wins, draws, losses = 0, 0, 0
        gf, ga = 0, 0
        for s in seeds:
            for pside in ("player_1", "player_2"):
                env = SoccerEnv(config)
                obs = env.reset(seed=s)
                organizer.start_episode()
                while not env.done:
                    if pside == "player_1":
                        a1 = pol(obs["player_1"])
                        a2 = organizer.choose_action(obs["player_2"])
                    else:
                        a1 = organizer.choose_action(obs["player_1"])
                        a2 = pol(obs["player_2"])
                    obs, info = env.step(a1, a2)
                sc = env.result()["score"]
                pf = sc[pside]
                pa = sc["player_2" if pside == "player_1" else "player_1"]
                gf += pf; ga += pa
                if pf > pa: wins += 1
                elif pf == pa: draws += 1
                else: losses += 1
        tot = len(seeds) * 2
        print(f"{cfg['name']}: {wins}W - {draws}D - {losses}L (Win: {wins/tot*100:.1f}%, Unbeaten: {(wins+draws)/tot*100:.1f}%) | Goals: {gf}-{ga} (GD: {gf-ga:+d})")

if __name__ == "__main__":
    run_parameter_search()
