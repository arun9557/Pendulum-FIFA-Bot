# Team Pendulum — Submission Package

**Competition:** Conv-Cup '26: FIFA of Bots  
**Team Name:** `Pendulum`  
**Execution Command:** `python -m team_bot.bot --model team_bot/models/example_policy.json`

---

## 1. System Overview & Architecture

Team Pendulum utilizes a **Hierarchical Hybrid Decision Engine** designed for deterministic 2D soccer simulation with procedurally placed obstacles.

### Core Modules:
1. **Anti-Rebound Obstacle Radar:**
   - Evaluates direct shooting lines against all active obstacles up to 16 units ahead.
   - Prevents self-inflicted rebound own-goals by automatically routing shots through unobstructed flank lanes (`UP_LEFT`, `UP_RIGHT`) or carrying possession via safe dribbling.
2. **Confidence-Aware Decision Gating:**
   - Interfaces with optional format-3 reinforcement learning models.
   - Requires a minimum of 8 state visits and a statistical confidence margin ($Q_{best} - Q_{2nd} \ge 0.25$) before permitting RL overrides against the tactical master.
3. **Goal-Side Defense & Interception:**
   - Guards the critical defensive corridor between opponent and own goal mouth.
   - Intercepts loose balls based on multi-step trajectory leads.

---

## 2. Directory Structure Inside Archive

```text
submission.json          # Main competitor descriptor (Team name & launch command)
README.md                # System documentation and interface usage
requirements.txt         # Runtime dependencies (pure Python standard library)
team_bot/
  __init__.py
  bot.py                 # Protocol loop (JSON stdin/stdout handler)
  policy.py              # Hybrid policy implementation
  models/
    example_policy.json  # Tactical Master configuration (active)
    trained_rl.json      # Trained format-3 Q-learning model (alternate)
```

---

## 3. State & Action Interface Usage

- **Observations (`stdin`):** Receives single-line JSON objects containing `player_id`, `opponent_id`, `attack_direction`, `ball` coordinates, player positions, field dimensions, and `obstacles`.
- **Actions (`stdout`):** Emits exactly one JSON line per tick:
  - Movement only: `{"move":"UP"}`
  - Movement + Kick: `{"move":"UP","kick":{"direction":"UP_RIGHT","power":3}}`
- **Error Handling:** Fallback to safe directional movement ensures zero action timeouts and zero action errors.

---

## 4. Dependencies & Runtime

- **Python Version:** 3.11+
- **External Dependencies:** None (Zero third-party packages required).
- **Execution Deadline:** In-memory inference takes < 1ms per step (well within the 2000ms deadline).
