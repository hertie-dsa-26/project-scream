# Project Log — DSA Team Project (Hertie DSA 26)

A running record of what the team has built and when. Updated as the project progresses.

---

## Team Members

| GitHub Handle | Name | Role |
|---|---|---|
| `luiscza` | Luis | Visualization/Prototyping, Documentation |
| `adarsht27` | Adarsh | Scrum Master, Version Control & Workflow |
| `YenusAyalew` | Yenus | Visualization/Prototyping, EDA |
| `JesperBoon` | Jesper | Flask Development, Task Coordination |
| `mateism` | Marci | Flask Development |
| `KJ-7` | Kevine | EDA |
| `davraco9-lab` | David | EDA |

---

## February 2026 — Project Kickoff & Dataset Selection

**Feb 11:** Marci creates the team group chat ("SCREAM"). Team begins scheduling their first sprint/scrum meeting.

**Feb 12 — First Scrum Meeting** (Room 3.33, hybrid): Kevine assigns first tasks — everyone reviews the project rubric, explores datasets, and prepares a dataset pitch for the next meeting.

**Feb 18 — Dataset Pitching Meeting:** Each member presents a candidate dataset:
- Jesper → Anthropic Economic Index
- Luis → ACLED conflict data
- Yenus → CDC BRFSS (Behavioral Risk Factor Surveillance System)
- Kevine → ProPublica COMPAS dataset (recidivism)
- Marci → Urban datasets (road network, urban sounds, floods)

**Feb 19:** Yenus outlines the CDC BRFSS dataset scope (345 variables, 450k+ respondents, 49 states) for predicting health outcomes. Kevine shares notes from a consultation with Prof. Dimmery: project must focus heavily on software engineering and efficient data structures. Team tasked with doing EDA on CDC and ACLED datasets.

**Feb 25–26:** Yenus attempts to push the raw BRFSS data to GitHub but hits the 100MB file size restriction.

**Outcome:** Team aligned on the BRFSS dataset as their choice.

---

## March 2026 — Subsetting, Workflow & Sprint Planning

**Mar 2:** Luis finishes subsetting the data, converts to Parquet format to bypass GitHub's file size limits, and opens PR #9.

**Mar 4:** PR #9 merged (subsetting pipeline). Jesper begins insurance EDA.

**Mar 9:** Mateis fixes a path bug in the pipeline instructions.

**Mar 10–11 — Sprint Planning Meeting:** Team formally switches to biweekly sprints and adopts Microsoft Teams for screen-sharing stand-ups. Roles are distributed:

| Role | Members |
|---|---|
| Flask development | Jesper, Marci |
| Visualization/Prototyping | Yenus, Luis |
| Scrum Master / Version Control | Adarsh |
| EDA | Kevine, David |

**Mar 12:** Adarsh establishes contributing guidelines and version control workflow for the team (PR #11 merged) — branch naming, PR review process, commit standards, `.gitignore`.

**Mar 13:** Mateis completes the depression EDA notebook (PR #12). Adarsh shares the official workflow docs with the team.

**Mar 15:** PR #12 (depression EDA) merged.

**Outcome:** Clean pipeline in place, team roles defined, shared development standards established.

---

## April 2026 — App Development & Machine Learning

**Apr 8–10:** Team regroups after a short break. Marci pins a format for daily progress reports (accomplishments, plans, roadblocks).

**Apr 11:**
- **App prototypes:** Marci shares a crude Flask skeleton explaining the repository structure. Jesper shares an alternative "New York Times scrolling data page" style skeleton.
- **EDA delivery:** David finishes the EDA and uploads `Diabetes_and_HeartDisease_EDA.ipynb` to GitHub (PR #20).
- **Flask skeleton merged:** Jesper & Marci's app skeleton — application factory pattern, blueprint registration, scrollytelling homepage, `/predict` stub, `/eda` and `/models` blueprint stubs, centralized data loader with caching, error templates (404, 500).

**Apr 12:** Keving adds a general EDA notebook.

**Apr 14–17 — ML Formulation:**
- Kevine, Yenus, and Adarsh define the ML problem and review academic literature.
- Research finds XGBoost and Random Forest are top performers for this type of data.
- Adarsh flags that in a medical context, false negatives are heavily costly → team decides to prioritize **recall** over overall accuracy, using **F1-score** and **PR-AUC** as primary metrics.
- Adarsh, Yenus, and Keving upload literature review summaries (PRs #22, #24, #26).

**Apr 18:** Kevine updates the README with a formal problem definition and diabetes prediction references.

**Apr 18–20:** Team sets goal of a working prototype by end of April. Major coworking session scheduled.

**Apr 21 — Extended Stand-up (45 min):** Meeting to discuss progress of Adarsh, Yenus, Kevine, and David on ML work. Discussed integration with the Flask skeleton. **Final models confirmed.**

**Apr 23 (Today) — Coworking Session (2:00–4:00 PM, Room 2.30):**

Task split for the session:
- **Marci & Jesper** — side map, design document based on last stand-up
- **Yenus, Kevine, David** — subsetting data to agreed-on features, training models (Random Forest, SFM, XGBoost, GBM)
- **Luis** — project documentation, basic design
- **Luis & Jesper** — centralizing task distribution and coordination

Marci also attending Prof. Dimmery's office hours.

---

## Models & ML Decisions

| Model | Notes |
|---|---|
| Random Forest | Strong baseline, interpretable feature importance |
| XGBoost | Top performer in literature |
| GBM (Gradient Boosting Machine) | Good benchmark alongside XGBoost |
| SFM (Select From Model) | Feature selection step, not a standalone model |

**Primary metric:** F1-score and PR-AUC (recall prioritized — false negatives are costly in a medical context)

**Prediction target:** Diabetes / Heart Disease (finalized Apr 21)

---

## Still To Do

- [ ] Implement final ML algorithm from scratch (no external ML libraries for core implementation — rubric requirement)
- [ ] Wire real data and model outputs into Flask routes
- [ ] Build interactive visualizations (Plotly / Chart.js / D3)
- [ ] Complete side map and design document (Marci & Jesper)
- [ ] Set up test suite (pytest)
- [ ] Set up CI (GitHub Actions)
- [ ] Write individual retrospectives (each team member, 1 page)

---

*Last updated: April 23, 2026*