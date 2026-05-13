# Project Log — DSA Team Project (Hertie DSA 26)

A running record of what the team has built and when. Updated as the project progresses.

---

## Team Members

| GitHub Handle | Name |
|---|---|
| `luiscza` | Luis |
| `adarsht27` | Adarsh | 
| `YenusAyalew` | Yenus | 
| `JesperBoon` | Jesper | 
| `mateism` | Marci | 
| `KJ-7` | Kevine | 
| `davraco9-lab` | David | 

---

## February 2026 — Project Kickoff & Dataset Selection

**Feb 11:** Marci creates the team group chat ("SCREAM"). Team begins scheduling their first sprint/scrum meeting.

**Feb 12 — First Scrum Meeting** (hybrid): Kevine assigns first tasks — everyone reviews the project rubric, explores datasets, and prepares a dataset pitch for the next meeting.

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

**Mar 9:** Marci fixes a path bug in the pipeline instructions.

**Mar 10–11 — Sprint Planning Meeting:** Team formally switches to biweekly sprints and adopts Microsoft Teams for screen-sharing stand-ups. Roles are distributed:

| Role | Members |
|---|---|
| Flask development | Jesper, Marci |
| Visualization/Prototyping | Yenus, Luis |
| Scrum Master / Version Control | Adarsh |
| EDA | Kevine, David |

**Mar 12:** Adarsh establishes contributing guidelines and version control workflow for the team (PR #11 merged) — branch naming, PR review process, commit standards, `.gitignore`.

**Mar 13:** Marci completes the depression EDA notebook (PR #12). Adarsh shares the official workflow docs with the team.

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

**Apr 23 — Coworking Session:**

Task split for the session:
- **Marci & Jesper** — side map, design document based on last stand-up
- **Yenus, Kevine, David** — subsetting data to agreed-on features, training models (Random Forest, SFM, XGBoost, GBM)
- **Luis** — project documentation, basic design
- **Luis & Jesper** — centralizing task distribution and coordination

Marci also attending Prof. Dimmery's office hours.

**Apr 24:** PR #35 (Adarsh's literature summaries) merged.
 
**Apr 30:**
- Adarsh prepares the SVM pipeline notebook and serialises pickle files + feature JSON for the Flask app (PR #40).
- Jesper integrates logistic regression into the Flask app as an initial wired-up model.
- PR #38 (Jesper's skeleton work) merged by Yenus.
- PR #40 (SVM model upload) merged by Adarsh.
---
 
## May 2026 — Tests, CI, and Final Refinements
 
**May 1:** PR #27 (Luis's patch) merged. Marci resolves outstanding review comments.
 
**May 2:** Marci pushes interim app progress — prediction and explorer pages taking shape.

**May 4:** Marci adds a pytest test suite and a GitHub Actions YML file for CI. Fixes to the prediction and explorer pages; pytest integrated into the `uv` workflow. This closes the "Set up test suite" and "CI" items from the to-do list.
 
**May 6:**
- Adarsh updates the README and benchmarks the project against the rubric (PR #48, merged). Citations reformatted closer to APA style.

**May 7 – Coworking Session:**
- PR #42 (feat/ml-integration) merged by Marci.
- PR #44 (tests) merged by Marci.
- Survey respondent count corrected in `home.html`.
- Luis and Adarsh attended Prof. Dimmery's office hours to gather feedback to the app and input for the presentation
- Extensive internal feedback session to features and flask app


**May 9:** Adarsh sets up temporary Cloudflare tunnel to demo the live app to the team. Team member reviews it on mobile - no issues, slight load time on the explorer page noted (acceptable given it queries the Parquet directly; team decides not to refactor the dataloader at this stage).

**May 10 — PR #50 opened (Final Refinements), by Marci:**
 
A comprehensive polish and model-swap PR. Highlights:

- **ManualSVM replaces logistic regression** — satisfying the rubric requirement. Risk scoring via `sigmoid(decision_score)`; thresholds low < 40%, moderate 40–60%, high > 60%. `retrain_svm.py` included for regenerating artifacts.
- **Predictions form:** BMI replaced with height + weight fields and metric/imperial toggle; preferences persist via `localStorage`. Form state and results persist across navigation. Tooltip hints added to key fields. Quit-smoking suggestion always shown for current smokers.
- **Details page:** SVM weight chart replaces odds ratio chart. Population comparison table shows readable categorical benchmarks; alcohol added. CDC resources section added.
- **Explorer page:** Charts highlight the user's position from their last prediction, with a toggle to show/hide.
- **Home page:** Map prevalence computed from BRFSS parquet instead of hardcoded values. Animated zoom to southern belt on scroll. Respondent count corrected to 450,000+.
- **Tests:** All 75 tests passing.

Marci also shares `CLEANUP.md`, `DOCS.md`, and `TODO.md` with the team.

**May 11 — Final fixes to PR #50:**
- Smoking delta numbers hidden from the suggestion UI — model signal for this feature deemed unreliable; tests updated to match.
- fix: chart label cutoff, consistent sidebar on home page, imperial form repopulation

**May 11 — Team meeting:**
- Spun up Cloudflare and walked through the live app together 
- Discussed the app demo, the general presentation structure
- README
- Repo cleanup.

**May 12 - Final Presentation prep:**
- Merge PR #51 (README.md update to reflect refinements)
- Done with the presentation slides preparation

**May 13 - Final Presentation & Individual retrospectives:**
- Each member writes individual retrospectives (each team member, 1 page)
- Final presentation done

**OVER AND OUT GUYS...GOOD JOB TO EVERYONE**

---

## Models & ML Decisions

| Model | Notes |
|---|---|
| ManualSVM | **Live model — from-scratch implementation required by rubric. Risk via sigmoid(decision_score).** |
| GBM (Gradient Boosting Machine) | Trained and evaluated during model selection phase |
| SFM (Select From Model) | Feature selection step |

**Primary metric:** F1-score and PR-AUC (recall prioritized — false negatives are costly in a medical context)

**Prediction target:** Diabetes / Heart Disease (finalized Apr 21)

---

## Still To Do

- [ ] 

---

*Last updated: May 13, 2026*
