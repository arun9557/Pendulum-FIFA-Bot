# ⚽ Team Pendulum — AI Soccer Bot (Conv-Cup '26)

> **Tournament:** Conv-Cup '26: FIFA of Bots  
> **Conducted by:** Machine Learning Division, CyberLabs (IIT ISM Dhanbad)  
> **Team Name:** `Pendulum`  
> **Evaluation Outcome:** **14W – 4D – 2L (70% Win Rate, +31 Goal Difference)** vs Organizer RL Bot

---

## 🏆 Performance Highlights

Official head-to-head evaluation across 20 matches (Seeds 7000–7009, playing both Player 1 and Player 2 roles) against the tournament's official **Balanced United RL Reference**:

| Metric | Baseline Tactical Bot | Old Q-Learning RL | **Team Pendulum (Our Solution)** |
| :--- | :---: | :---: | :---: |
| **Record (W / D / L)** | 11W – 4D – 5L | 9W – 2D – 9L | **14W – 4D – 2L** 🥇 |
| **Win Rate** | 55.0% | 45.0% | **70.0%** |
| **Unbeaten Rate** | 75.0% | 55.0% | **90.0%** (Only 2 losses in 20 matches) |
| **Goals Scored** | 48 | 29 | **50** ⚽ |
| **Goals Conceded** | 26 | 25 | **19** 🛡️ |
| **Goal Difference (GD)** | +22 | +4 | **+31** 🚀 |
| **Action Errors** | 0 | 0 | **0** (100% Clean Actions) |

---

## 🧠 Architecture: Hierarchical Hybrid Decision Engine

Instead of relying solely on sparse Q-learning (which caused erratic play and own goals), Team Pendulum implements a **Hierarchical Hybrid Decision System**:

```text
               ┌────────────────────────┐
               │    GAME OBSERVATION    │
               │ Players, Ball, Obstacle│
               └───────────┬────────────┘
                           │
                           ▼
               ┌────────────────────────┐
               │  SITUATION CLASSIFIER  │
               │ Attack / Defend / Press│
               └───────────┬────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌──────────────────┐               ┌──────────────────┐
│  TACTICAL MASTER │               │   RL Q-LEARNING  │
│  Decision Engine │               │   Confidence Gate│
└────────┬─────────┘               └─────────┬────────┘
         │                                   │
         │ (Fallback if uncertain / visits<8)│
         └─────────────────┬─────────────────┘
                           │
                           ▼
               ┌────────────────────────┐
               │  ANTI-REBOUND RADAR    │
               │ Ray-Box Obstacle Mask  │
               └───────────┬────────────┘
                           │
                           ▼
               ┌────────────────────────┐
               │    FINAL SAFE ACTION   │
               │ Move + Directional Kick│
               └────────────────────────┘
```

1. **Anti-Rebound Obstacle Radar:** Scans candidate kick trajectories up to 16 units ahead. If an obstacle is in the direct line of sight, the bot dynamically routes shots through open diagonal corridors (`UP_LEFT`, `UP_RIGHT`) or carries with safe dribbling, completely eliminating self-inflicted rebound own-goals.
2. **Confidence-Aware RL Gating:** RL overrides the tactical master only when the state has at least **8 visits** and a distinct Q-value superiority margin ($Q_{best} - Q_{2nd} \ge 0.25$).
3. **Multi-Step Physics Interception:** Predicts ball bounce angles and deceleration to intercept loose balls steps ahead of the opponent.
4. **Goal-Side Arc Defense:** Maintains a defensive corridor between the opponent and our own net, executing aggressive tackles within a 6-unit contact perimeter.

---

## 🚀 Quickstart & Usage

Open PowerShell in `participants/`:

```powershell
cd participants
```

### 1. Verify Test Suite
```powershell
python -m unittest discover -s tests -v
```

### 2. Watch Live Match in Browser Viewer
Watch **Team Pendulum** play in real-time with visual commentary:
```powershell
python live_viewer.py
```
*(Automatically opens `http://127.0.0.1:PORT/` in your browser)*

### 3. Run Practice Match (Terminal)
```powershell
python run_match.py --submission my_team/submission.json
```

### 4. Run Tournament Benchmark (20 Matches)
```powershell
python validate_submission.py --submission my_team/submission.json --matches-per-side 10 --seed 7000
```

### 5. Package & Verify Submission for Unstop
```powershell
# Create ZIP
python package_submission.py my_team dist/Pendulum.zip

# Run static policy checker
python check_submission.py dist/Pendulum.zip --report dist/Pendulum-report.json
```

---

## 📁 Repository Structure

```text
Mlfootball_env/
├── README.md                           # Main GitHub presentation & overview
├── .gitignore                          # Clean repository rules
└── participants/
    ├── my_team/                        # Primary submission source for Team Pendulum
    │   ├── submission.json             # Team metadata and launch command
    │   ├── README.md                   # Packaged submission documentation
    │   ├── requirements.txt            # Approved runtime dependencies
    │   └── team_bot/
    │       ├── bot.py                  # Standard I/O protocol interface
    │       ├── policy.py               # Champion Hybrid Policy
    │       └── models/
    │           ├── example_policy.json # Active Tactical Master model
    │           └── trained_rl.json     # Trained format-3 RL model
    ├── dist/
    │   ├── Pendulum.zip                # Official upload archive for Unstop
    │   └── Pendulum-report.json        # Static checker validation report
    ├── config/                         # Simulation parameters & match setups
    ├── soccer_env/                     # 2D deterministic soccer engine
    ├── organizer_rl_bot/               # Balanced United RL benchmark bot
    ├── PROJECT_GUIDE.md                # Comprehensive user and testing manual
    ├── CHANGELOG_AND_IMPROVEMENTS.md   # Diagnostic report and metrics changelog
    ├── live_viewer.py                  # Live browser visualizer
    ├── run_match.py                    # Match runner
    ├── train_bot.py                    # Reinforcement learning trainer
    └── validate_submission.py          # Match validation runner
```

---

## 📜 Documentation Links

- 📖 [PROJECT_GUIDE.md](participants/PROJECT_GUIDE.md) — Detailed instructions on all scripts and tools.
- 🔬 [CHANGELOG_AND_IMPROVEMENTS.md](participants/CHANGELOG_AND_IMPROVEMENTS.md) — Complete diagnosis, root-cause analysis, and before/after match statistics.

---

## 🔒 Competition Rules & Compliance

- **No External Dependencies:** 100% pure Python standard library.
- **Deterministic:** Completely reproducible from match seeds and starting state.
- **Verified Policy:** Passes `submission_checker.py` with 0 warnings, 0 errors, and 0 action errors......