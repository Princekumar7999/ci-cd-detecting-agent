# Video Submission Transcript: Autonomous DevOps Agent

**Target Duration**: 3-5 Minutes
**Team Name**: [INSERT_TEAM_NAME]
**Project**: Autonomous DevOps Agent (RIFT 2026 Hackathon)

---

## 1. Introduction & The Hook (0:00 - 0:45)

**[Visual: Title Slide with Project Name + Team Name]**

**Speaker**:
"Hello everyone! We are Team [Team Name], and we are excited to present our project for the RIFT 2026 Hackathon: the **Autonomous DevOps Agent**."

**[Visual: Split screen showing a terminal with a crash error vs. a developer holding their head in frustration]**

**Speaker**:
"We all know the pain: You push code on a Friday evening, and the CI/CD pipeline explodes. Syntax errors, missing imports, broken tests—debugging these manually is slow, repetitive, and kills productivity. What if your pipeline could fix itself?"

---

## 2. The Solution (0:45 - 1:30)

**[Visual: High-level Architecture Diagram (from README)]**

**Speaker**:
"Meet our Autonomous DevOps Agent. It's not just a linter; it's an intelligent, self-healing system designed to detect, diagnose, and autonomously fix code issues in real-time."

**[Visual: Bullet points of features appearing one by one]**

**Speaker**:
"Our agent handles:"
1.  **Detection**: Identifying syntax bugs, linting errors, and logic failures.
2.  **Analysis**: Using LLMs to understand *why* the code broke.
3.  **Autonomous Repair**: Generating and applying fixes automatically.
4.  **Verification**: Running sandboxed tests in Docker to ensure the fix actually works.

---

## 3. Tech Stack (1:30 - 2:00)

**[Visual: Logos of Tech Stack: React, Python, FastAPI, LangGraph, Google Gemini, Docker]**

**Speaker**:
"We built this using a powerful modern stack:
*   **Frontend**: A sleek, responsive dashboard built with **React** and **Vite**, styled with **TailwindCSS**.
*   **Backend**: A robust **FastAPI** server powered by **LangGraph** for agentic workflows.
*   **Intelligence**: **Google Gemini** provides the reasoning capabilities to understand complex codebases.
*   **Safety**: All executions happen inside **Docker** containers, ensuring complete isolation."

---

## 4. Live Demo (2:00 - 4:00)

**[Visual: Screen recording of the Web Application]**

**Speaker**:
"Let's see it in action. Here is our dashboard."

**[Action: User types in a GitHub Repo URL, Team Name, and Leader Name]**

**Speaker**:
"I'm entering the URL of a repository that has known issues—some syntax errors and a broken test. I enter my team details and hit **Run Agent**."

**[Action: Dashboard changes to 'Running' state. Progress bars/steps appear]**

**Speaker**:
"The agent immediately clones the repository and begins the **Analysis Phase**. You can see the real-time logs here."

**[Visual: Zoom in on the 'Analysis' step completing and 'Fixing' step starting]**

**Speaker**:
"It found a syntax error in `validator.py`. The agent is now generating a fix using Gemini... and applying it."

**[Visual: Show the 'Fixed' status appearing next to the error]**

**Speaker**:
"Now, it's verifying the fix. It spins up a Docker container, runs the tests again... and **Success!** The pipeline is green. The agent creates a new branch with the fixes and pushes it back to GitHub automatically."

---

## 5. Conclusion (4:00 - End)

**[Visual: Final Slide with 'Thank You' and Links]**

**Speaker**:
"The Autonomous DevOps Agent drastically reduces the 'Mean Time to Recovery' for broken builds. It frees developers to focus on features, not fighting fires. Thank you for watching!"
