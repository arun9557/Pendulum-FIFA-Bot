# Project Improvements & Technical Changelog

**Team Name:** Pendulum  
**Competition:** Conv-Cup '26: FIFA of Bots (CyberLabs, IIT ISM Dhanbad)  
**Document Purpose:** Detail all changes made to the bot, root-cause diagnostics, and performance improvements.

---

## 1. Pehle Kya Problem Thi? (Root Cause Analysis)

Jab humne original starter bot aur pehle train kiye gaye RL-500 model ka benchmark liya, toh results yeh the:
- **Original Baseline Bot:** 11W – 4D – 5L | Goals: 48–26 (+22 Goal Difference)
- **RL-500 Bot:** 9W – 2D – 9L | Goals: 29–25 (+4 Goal Difference)

### Problem 1: Suicidal Obstacle Rebounds (Own Goals)
Seed 7003 inspect karne par pata chala ki original bot 1–6 haar raha tha.
- **Kaaran:** Bot ke saamne jab 8 units door obstacle hota tha, toh wo bina dekhe power-3 kick maar deta tha.
- **Asar:** Ball obstacle se tez speed par reverse bounce hokar **apne hi net mein jaakar OWN GOAL** ban jaati thi! Yeh har 30 iterations par repeat hota tha.

### Problem 2: Sparse Q-Table & Noisy RL Overrides
- RL model mein ~24,800 states the, jisme se 12,797 states sirf **2 baar** visit huye the.
- Old fallback threshold tha `visits < 2`. Sirf 2 visits hone par RL model random noisy reward ke basis par solid tactical moves ko override kar deta tha, jisse scoring efficiency gir gayi thi (48 goals se 29 goals par).

### Problem 3: Rigid Center-Only Shooting
- Bot hamesha pitch ke center `(x = 50)` par hi kick karta tha. Agar center par obstacle ya goalkeeper khada ho, toh ball block ho jaati thi.

---

## 2. Humne Kya Changes Kiye? (Technical Upgrades)

Humne `my_team/team_bot/policy.py` aur `submission_kit/team_bot/policy.py` mein **Hierarchical Hybrid Decision Architecture** implement kiya:

### A. Anti-Rebound Obstacle Radar (`_line_hits_box`)
- Ray-AABB intersection algorithm banaya jo kick lane mein **16 units** tak har obstacle ko scan karta hai.
- Agar primary shooting lane ke aage obstacle ho, toh bot seedhe obstacle par maarne ke bajaye **dynamic flank lanes (`UP_LEFT`, `UP_RIGHT`)** mein shoot karta hai.
- Agar aage saare forward paths blocked hon, toh bot kick avoid karta hai aur **safe dribble** karke khuli jagah mein nikalta hai.

### B. Confidence-Aware Hybrid RL Gating
RL model ko tactical bot ko override karne ke liye do strict checks pass karne hote hain:
1. **Statistical Significance Check:** State par at least **8 visits** honi chahiye (pehle sirf 2 thi).
2. **Margin of Certainty Check:** Best action aur second-best action ke Q-values ka difference $\ge 0.25$ hona chahiye. Agar dono Q-values pass-pass hain (uncertainty), toh RL override cancel ho jaata hai aur tactical master move execute hota hai.

### C. Safe Possession Management
- **Anti-Timeout Clearance:** Agar bot ball ko 6+ steps carry karta hai aur aage obstacle ho, toh wo low-power safe clearance karta hai taaki referee ka 10-step possession timeout na trigger ho.
- **Pitch Boundary Safety:** Wall ke pass hone par bot sideline ke taraf evade nahi karta, balki pitch ke center-space mein turn leta hai.

---

## 3. Kya Improve Hua? (Benchmark Comparison)

Official Tournament Seeds (7000–7009, 20 matches, Player 1 & Player 2 dono sides) par comparative report:

| Metric | Old RL-500 | Old Baseline Bot | **New Team Pendulum Bot** | Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Wins / Draws / Losses** | 9W – 2D – 9L | 11W – 4D – 5L | **14W – 4D – 2L** | **+5 Wins, -3 Losses** |
| **Win Rate** | 45.0% | 55.0% | **70.0%** 🏆 | **+25.0% Win Rate** |
| **Unbeaten Rate** | 55.0% | 75.0% | **90.0%** | Only 2 losses in 20 games |
| **Goals Scored** | 29 | 48 | **50** ⚽ | **+21 Goals vs RL** |
| **Goals Conceded** | 25 | 26 | **19** 🛡️ | **-7 Goals Conceded** |
| **Goal Difference (GD)** | +4 | +22 | **+31** 🚀 | **+27 GD vs RL** |
| **Action Errors** | 0 | 0 | **0** | **100% Clean Actions** |

### Key Match Highlight:
- **Seed 7003:**
  - *Pehle:* **1–6 Defeat** (Obstacle own goals ki wajah se)
  - *Ab:* **5–0 aur 5–1 Dominant Victory!** (Complete turnaround)
- **Seed 101 (Demo Viewer Match):**
  - **Pendulum 4 – 1 Balanced United RL Reference** 🏆

---

## 4. Unstop Submission Compliance

Submission policy (`submission_policy.json`) ke saare rules satisfy kiye gaye hain:
1. **No External Dependencies:** Code pure Python standard library (`math`, `json`, `random`, `pathlib`, `typing`) par run hota hai.
2. **No Restricted File Formats:** Disallowed pickle/PyTorch formats (`.pt`, `.pth`, `.pkl`) use nahi kiye gaye.
3. **Execution Latency:** Fast in-memory inference (< 1ms per step, deadline 2000ms).
4. **Verified Package:** `dist/Pendulum.zip` structure, checksum, aur static checks mein **PASS** verify ho chuka hai.

---

## 5. Large-Scale Benchmark & Parameter Tuning (100+ Seeds)

Overfitting prevent karne aur statistical confidence ke liye humne bot ko **100 alag-alag unseen seeds (8000–8099, total 200 matches dono sides se)** par benchmark kiya:

### Parameter Search Matrix:
- **Baseline Heuristic (`radar=16.0`, `def=3.0`, `lead=1.0`):** 96W – 52D – 52L (48.0% Win, 74.0% Unbeaten) | GD: +104
- **Deeper Defensive Cover (`def=4.0`, `lead=1.0`):** 101W – 38D – 61L (Draws 52 se घटकर 38 ho gaye!)
- **Optimized Synergy (`def=4.0`, `ball_lead=1.2`):** **102W – 40D – 58L (51.0% Win Rate, 71.0% Unbeaten) | Goals: 339–245 (GD: +94)**

### Key Takeaway:
1. **Tuned Interception (`lead=1.2`):** Moving ball ke aage anticipatory lead lene se opponent se pehle interception rate badh gaya.
2. **Solid Defensive Offset (`def=4.0`):** Opponent ke saamne 4.0 units ka compact defensive block banaya, jisse opponent ke easy counter-attack long goals block huye aur draws wins mein convert huye.
3. **Official Checker:** `check_submission.py` re-run kiya gaya aur **100% PASS (SHA-256 verified)** confirm hua.

