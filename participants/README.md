# ⚽ Conv-Cup '26 — AI Soccer Participant Kit

**Competition:** Conv-Cup '26: FIFA of Bots (CyberLabs, IIT ISM Dhanbad)  
**Team Name:** `Pendulum`  
**Platform Status:** Fully Verified & Compliant (`PASS`, 0 warnings, 0 errors)

---

## 📌 Overview

This directory (`participants/`) is a self-contained environment containing the official deterministic 2D soccer simulator, game configurations, reference bots, evaluation harnesses, and **Team Pendulum**'s competitive AI agent.

- **Python Requirement:** Python 3.11+
- **External Dependencies:** None (pure Python standard library only).

---

## ⚡ Quickstart Commands

All commands should be executed from within the `participants/` directory in PowerShell:

```powershell
cd participants
```

### 1. Run Automated Smoke Tests
Validate simulator components, state APIs, and action interfaces:
```powershell
python -m unittest discover -s tests -v
```

### 2. Watch Live Match in Browser
Launch real-time graphical match between **Pendulum** and **Balanced United RL Reference**:
```powershell
python live_viewer.py
```
*(Automatically opens `http://127.0.0.1:PORT/` in your browser. Press `Ctrl+C` in the terminal to stop).*

### 3. Run Practice Match (Terminal)
Run a single headless match and view the final score:
```powershell
python run_match.py --submission my_team/submission.json
```

### 4. Validate on Tournament Seeds (20 Matches)
Run an official two-sided evaluation across Seeds 7000–7009:
```powershell
python validate_submission.py --submission my_team/submission.json --matches-per-side 10 --seed 7000
```

### 5. Package & Verify Submission for Unstop
```powershell
# Create compliant submission ZIP
python package_submission.py my_team dist/Pendulum.zip

# Run official static safety and structure checker
python check_submission.py dist/Pendulum.zip --report dist/Pendulum-report.json
```

---

## 📂 Directory Contents

```text
participants/
├── config/                     # Official game rules & platform policies
│   ├── demo_match.json         # Viewer matchup configuration
│   ├── game.json               # Physics, field dimensions, and kick rules
│   └── submission_policy.json  # Platform safety constraints & file rules
├── dist/
│   ├── Pendulum.zip            # Verified submission archive ready for upload
│   └── Pendulum-report.json    # Official verification report
├── my_team/                    # Primary submission source for Team Pendulum
│   ├── submission.json         # Competitor metadata & execution command
│   ├── README.md               # Package documentation
│   ├── requirements.txt        # Empty requirements (standard library only)
│   └── team_bot/               # Policy logic and model weights
├── organizer_rl_bot/           # Official Balanced United RL benchmark bot
├── reference_bot/              # Simple heuristic baseline bot
├── soccer_env/                 # Standalone deterministic 2D physics engine
├── tests/                      # Automated test suite
├── viewer/                     # Browser field UI, canvas renderer, & commentary
├── PROJECT_GUIDE.md            # Detailed operational manual
├── CHANGELOG_AND_IMPROVEMENTS.md # Technical audit, root-cause diagnostics, & benchmarks
├── README.md                   # This overview guide
├── check_submission.py         # Static security and structure checker
├── live_viewer.py              # Interactive real-time visualizer
├── package_submission.py       # Submission archive creator
├── replay_viewer.py            # Post-match replay player
├── run_match.py                # Headless single match runner
├── train_bot.py                # Curriculum reinforcement learning trainer
└── validate_submission.py      # Multi-match validator across seeds
```

---

## 🏆 Team Pendulum Performance Summary

Official head-to-head evaluation against tournament benchmark **Balanced United RL**:
- **Tournament Seeds (7000–7009, 20 matches):** **14W – 4D – 2L (70.0% Win Rate)** | Goals: 50–19 (GD: +31)
- **Large-Scale Benchmark (100 unseen seeds, 200 matches):** **102W – 40D – 58L (51.0% Win Rate, 71.0% Unbeaten)** | Goals: 339–245 (GD: +94)
- **Action Errors:** **0 across all seeds** (100% legal actions).

---

## 🔒 Submission Constraints (`submission_policy.json`)

- **Dependencies:** Pure standard library (`math`, `json`, `random`, `pathlib`). Zero pip packages.
- **Allowed Extensions:** `.py`, `.json`, `.txt`, `.md`. Forbidden formats (`.pt`, `.pkl`, `.so`, `.exe`) strictly excluded.
- **Latency:** In-memory execution takes $< 1.0\text{ ms}$ per step (well below 2000 ms limit).
- **Archive:** Submitted file is `dist/Pendulum.zip` (verified SHA-256 integrity).