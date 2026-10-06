from __future__ import annotations

import sys
import time
from pathlib import Path

from soccer_env import GameConfig, SoccerEnv
from organizer_rl_bot.policy import OrganizerRLOpponent
from my_team.team_bot.policy import tactical_action

BASE_DIRECTORY = Path(__file__).resolve().parent

def run_large_benchmark(num_seeds: int = 100, start_seed: int = 8000):
    config = GameConfig.from_json(BASE_DIRECTORY / "config" / "game.json")
    organizer = OrganizerRLOpponent()

    wins, draws, losses = 0, 0, 0
    p1_wins, p2_wins = 0, 0
    goals_for, goals_against = 0, 0
    
    t0 = time.time()
    for offset in range(num_seeds):
        seed = start_seed + offset
        for player_side in ("player_1", "player_2"):
            env = SoccerEnv(config)
            observations = env.reset(seed=seed)
            organizer.start_episode()
            
            while not env.done:
                if player_side == "player_1":
                    a1 = tactical_action(observations["player_1"])
                    a2 = organizer.choose_action(observations["player_2"])
                else:
                    a1 = organizer.choose_action(observations["player_1"])
                    a2 = tactical_action(observations["player_2"])
                observations, info = env.step(a1, a2)

            sc = env.result()["score"]
            pf = sc[player_side]
            pa = sc["player_2" if player_side == "player_1" else "player_1"]

            goals_for += pf
            goals_against += pa
            if pf > pa:
                wins += 1
                if player_side == "player_1":
                    p1_wins += 1
                else:
                    p2_wins += 1
            elif pf == pa:
                draws += 1
            else:
                losses += 1

    total_matches = num_seeds * 2
    elapsed = time.time() - t0
    win_rate = (wins / total_matches) * 100
    draw_rate = (draws / total_matches) * 100
    loss_rate = (losses / total_matches) * 100
    gd = goals_for - goals_against

    print("=" * 65)
    print(f"LARGE-SCALE BENCHMARK ({total_matches} MATCHES across {num_seeds} UNSEEN SEEDS {start_seed}..{start_seed+num_seeds-1})")
    print(f"Time: {elapsed:.2f}s ({total_matches/elapsed:.1f} matches/sec)")
    print(f"Record: {wins}W - {draws}D - {losses}L (Win Rate: {win_rate:.1f}%, Unbeaten: {win_rate+draw_rate:.1f}%)")
    print(f"Goals: {goals_for} For, {goals_against} Against | Goal Diff: {gd:+d} (Avg: {gd/total_matches:+.2f}/game)")
    print(f"Player 1 Wins: {p1_wins}/{num_seeds} ({p1_wins/num_seeds*100:.1f}%) | Player 2 Wins: {p2_wins}/{num_seeds} ({p2_wins/num_seeds*100:.1f}%)")
    print("=" * 65)
    return {
        "wins": wins, "draws": draws, "losses": losses,
        "gf": goals_for, "ga": goals_against, "gd": gd, "win_rate": win_rate
    }

if __name__ == "__main__":
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    run_large_benchmark(seeds, 8000)
