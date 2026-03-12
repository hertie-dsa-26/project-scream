# Contributing Guidelines — Project SCREAM

> **Audience:** All 7 team members. This document assumes basic Git knowledge.  
> **Goal:** Keep `main` stable, avoid merge conflicts, and make collaboration predictable.

---

## Table of Contents

1. [Golden Rules](#1-golden-rules)
2. [Branch Strategy](#2-branch-strategy)
3. [Step-by-Step Workflow](#3-step-by-step-workflow)
4. [Commit Messages](#4-commit-messages)
5. [Pull Requests (PRs)](#5-pull-requests-prs)
6. [Code Review](#6-code-review)
7. [Resolving Merge Conflicts](#7-resolving-merge-conflicts)
8. [Project Structure](#8-project-structure)
9. [Python & Environment Setup](#9-python--environment-setup)
10. [Testing](#10-testing)
11. [Common Git Commands Cheat Sheet](#11-common-git-commands-cheat-sheet)

---

## 1. Golden Rules

| # | Rule |
|---|------|
| 1 | **Never push directly to `main`.** Always use a branch + pull request. |
| 2 | **Pull before you push.** Always run `git pull origin main` before starting work. |
| 3 | **One branch = one task.** Keep branches small and focused. |
| 4 | **Don't commit large data files.** The raw `.XPT` file and any derived CSVs stay local (handled by `.gitignore`). |
| 5 | **Communicate.** If you're working on something, let the team know to avoid duplicate work. |

---

## 2. Branch Strategy

We use a simple **feature-branch** workflow:

```
main  (always working, protected) (I have also added a branch rule for its protection on github)
 ├── yourname/feature-description
 ├── yourname/fix-description
 └── yourname/eda-description
```

### Branch naming convention

```
<your-first-name>/<short-description>
```

**Examples:**
- `luis/subsetting-module`
- `jesper/flask-app-setup`
- `Kevin/eda-smoking-correlation`
- `Adarsh/fix-login-route`

**Why names in branches?**  
With 7 people, it instantly tells everyone who is working on what — no need to look up the commit author.

### Branch types at a glance

| Prefix idea | Use case | Example |
|-------------|----------|---------|
| `name/feature-*` | New functionality | `luis/feature-ml-model` |
| `name/fix-*` | Bug fixes | `anna/fix-chart-axis` |
| `name/eda-*` | Exploratory analysis | `omar/eda-bmi-distribution` |
| `name/docs-*` | Documentation only | `priya/docs-readme-update` |

---

## 3. Step-by-Step Workflow

Here is the **exact sequence** every time you work on something:

### Starting a new task

```bash
# 1. Switch to main and get the latest version
git checkout main
git pull origin main

# 2. Create your branch
git checkout -b yourname/short-description

# 3. Do your work — edit files, write code, etc.

# 4. Stage your changes
git add .

# 5. Commit with a clear message (see section 4)
git commit -m "Add BMI distribution histogram"

# 6. Push your branch to GitHub
git push origin yourname/short-description

# 7. Go to GitHub → open a Pull Request → request a review
```

### Keeping your branch up to date (do this daily or before opening Pull Request (PR))

```bash
# While on your branch:
git fetch origin
git merge origin/main
# Resolve any conflicts if they appear (see section 7)
```

### After your PR is merged

```bash
git checkout main
git pull origin main
# Delete your old branch locally
git branch -d yourname/short-description
```

---

## 4. Commit Messages

Write clear, short commit messages so anyone can scan the history.

### Format

```
<What you did> (present tense, imperative mood)
```

### Good examples ✅

```
Add bar chart for exercise frequency by state
Fix NaN handling in BMI calculation
Create Flask route for visualization page
Update README with setup instructions
Implement KNN classifier from scratch
```

### Bad examples ❌

```
stuff
updates
final version
asdfgh
fixed it
```

### Tips
- Keep the first line under **72 characters**.
- If you need details, leave a blank line and add a longer description body.
- Commit **often** in small logical chunks, not one giant commit at the end.

---

## 5. Pull Requests (PRs)

Every change to `main` must go through a pull request.

### How to open a PR

1. Push your branch (step 6 above).
2. Go to the [repository on GitHub](https://github.com/hertie-dsa-26/project-scream).
3. You'll see a banner saying *"yourname/branch-name had recent pushes"* → click **Compare & pull request**.
4. Fill in the PR template:

```markdown
## What does this PR do?
<!-- Describe in 1-3 sentences -->

## Changes made
- [ ] List the key changes

## How to test
<!-- How can the reviewer verify this works? -->

## Screenshots (if UI-related)
<!-- Paste any relevant screenshots -->
```

5. On the right sidebar, **request a review** from at least 1 teammate.
6. Wait for approval before merging.

### PR etiquette

- **Keep PRs small.** Aim for under ~300 lines changed. Smaller = easier to review = faster merging.
- **One PR = one logical change.** Don't mix unrelated changes.
- **Respond to feedback** at earliest possible (maybe within 24 hours to not miss/forget details).
- **Don't merge your own PR** unless it's a trivial docs change and the team agrees.

---

## 6. Code Review

**Every PR needs at least 1 approval** from a teammate before merging. (I also added this in branch rule)

### As a reviewer

- **Be kind.** We're all learning. Frame suggestions constructively.
- **Be specific.** Instead of "this is wrong", say "this will break if X is NaN — consider adding a check on line 42."
- **Test it.** Pull the branch locally and run the code if possible:
  ```bash
  git fetch origin
  git checkout yourname/branch-name
  # Run and test
  ```
- Use GitHub's **comment**, **approve**, or **request changes** options.

### As the PR author

- If you disagree with a suggestion, explain your reasoning during stand up meetings.
- Mark conversations as "resolved" after addressing them.

---

## 7. Resolving Merge Conflicts

Conflicts happen when two people edit the same lines. Don't panic.

### Step-by-step

```bash
# 1. Update main
git checkout main
git pull origin main

# 2. Go back to your branch
git checkout yourname/your-branch

# 3. Merge main into your branch
git merge main

# 4. Git will tell you which files have conflicts.
#    Open them — you'll see markers like:
#
#    <<<<<<< HEAD
#    your version of the code
#    =======
#    the other version of the code
#    >>>>>>> main
#
# 5. Edit the file to keep the correct version (delete the markers).
# 6. Stage and commit
git add .
git commit -m "Resolve merge conflict in filename.py"
git push origin yourname/your-branch
```

### Preventing conflicts

- **Pull from main often** (at least daily when actively coding).
- **Don't edit the same files** at the same time — coordinate with the team.
- **Keep branches short-lived** (1–3 days ideally). (very important to not get confused between branch and big idea about project).

---

## 8. Project Structure

```
project-scream/
├── app/                    # Flask application
│   ├── __init__.py         # App factory
│   ├── routes/             # Route blueprints
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # CSS, JS, images
├── data/                   # Raw & processed data (git-ignored for large files)
├── eda/                    # Exploratory data analysis scripts/notebooks
├── notebooks/              # Jupyter notebooks (experiments, prototyping)
├── literature/             # Reference papers, docs
├── src/                    # Reusable Python modules
│   ├── __init__.py
│   ├── data_processing.py  # Data loading, cleaning, subsetting
│   ├── visualization.py    # Chart/plot generation functions
│   └── ml/                 # Machine learning module
│       ├── __init__.py
│       └── knn.py          # Example: KNN from scratch
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_data_processing.py
├── .gitignore
├── CONTRIBUTING.md         # ← You are here
├── pyproject.toml
└── README.md
```

### Rules for files

| Folder | What goes here | What does NOT go here |
|--------|---------------|----------------------|
| `app/` | Flask routes, templates, static assets | Data analysis code |
| `src/` | Reusable Python functions/classes | Notebooks, Flask code |
| `eda/` | EDA scripts and analysis notebooks | Production code |
| `notebooks/` | Experimental/scratch notebooks | Final analysis |
| `tests/` | Unit tests for `src/` and `app/` | Notebooks |
| `data/` | Datasets (large files git-ignored) | Code |

---

## 9. Python & Environment Setup

### First-time setup

```bash
# Clone the repo
git clone https://github.com/hertie-dsa-26/project-scream.git
cd project-scream

# Create virtual environment
python -m venv .venv

# Activate it
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### Adding a new package

1. Add it to `pyproject.toml` under `dependencies`.
2. Run `pip install -e .` again.
3. Commit the updated `pyproject.toml`.
4. **Tell the team** in your PR so everyone knows to reinstall.

> **Do NOT** commit `.venv/` — it's already in `.gitignore`.

---

## 10. Testing

We test our modules to catch bugs early. Tests live in the `tests/` folder.

### Running tests

```bash
# Run all tests
python -m pytest tests/

# Run a specific test file
python -m pytest tests/test_data_processing.py

# Run with verbose output
python -m pytest tests/ -v
```

### Writing a simple test

```python
# tests/test_data_processing.py
from src.data_processing import load_data

def test_load_data_returns_dataframe():
    df = load_data("data/sample.csv")
    assert df is not None
    assert len(df) > 0

def test_load_data_has_expected_columns():
    df = load_data("data/sample.csv")
    assert "BMI" in df.columns
```

### When to write tests

- When you create a new function in `src/`.
- When you fix a bug (write a test that catches it, then fix it).
- Before opening a PR — run `python -m pytest tests/` to make sure nothing is broken.

---

## 11. Common Git Commands Cheat Sheet

| What you want to do | Command |
|---------------------|---------|
| Check which branch you're on | `git branch` |
| See all branches (including remote) | `git branch -a` |
| Switch to an existing branch | `git checkout branch-name` |
| Create and switch to a new branch | `git checkout -b yourname/description` |
| See what files you changed | `git status` |
| See the actual changes line by line | `git diff` |
| Stage all changes | `git add .` |
| Stage specific file | `git add path/to/file.py` |
| Commit staged changes | `git commit -m "Your message"` |
| Push branch to GitHub | `git push origin yourname/branch-name` |
| Get latest from remote | `git pull origin main` |
| Undo changes to a file (before commit) | `git checkout -- filename` |
| See commit history | `git log --oneline -20` |
| Delete a local branch | `git branch -d branch-name` |

### "Help, I did something wrong!"

| Problem | Solution |
|---------|----------|
| Committed to `main` by mistake | `git reset HEAD~1` (undoes last commit, keeps changes) |
| Need to undo my last commit | `git reset --soft HEAD~1` |
| Pushed to wrong branch | Ask the team — we'll figure it out together |
| Everything is broken | Don't panic. Run `git stash`, then `git checkout main`. Your work is saved in the stash. |

---

## Quick Reference: The Daily Workflow

```
1. git checkout main
2. git pull origin main
3. git checkout -b yourname/task-description
4. ... do your work ...
5. git add .
6. git commit -m "Clear description of change"
7. git push origin yourname/task-description
8. Open PR on GitHub → request review
9. Address feedback → get approved → merge
10. git checkout main && git pull origin main
```

**That's it.** Follow these steps and we'll have a smooth project. 🚀
