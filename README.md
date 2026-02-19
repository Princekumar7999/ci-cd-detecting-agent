# Autonomous DevOps Agent (RIFT 2026 Hackathon)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![React](https://img.shields.io/badge/frontend-React-blue)
![Python](https://img.shields.io/badge/backend-FastAPI-green)

An autonomous AI agent that detects, fixes, and verifies code issues in CI/CD pipelines. Built for the **RIFT 2026 Hackathon** (AI/ML Track).

---

## 🚀 Live Demo & Links

- **Live Application**: [INSERT_YOUR_DEPLOYED_URL_HERE] (e.g., Vercel/Netlify link)
- **Demo Video**: [INSERT_LINKEDIN_VIDEO_URL_HERE] (Must tag @RIFT2026)
- **Repository**: [INSERT_GITHUB_REPO_URL_HERE]

---

## 🏗 Architecture

The system follows a multi-agent architecture with a React frontend and Python/FastAPI backend using LangGraph.

```mermaid
graph TD
    User[User via React Dashboard] -->|Repo URL + Team Info| API[FastAPI Backend]
    API -->|Trigger| Agent[DevOps Agent Graph]
    
    subgraph "Agent Workflow (Sandboxed)"
        Clone[Clone Repo] --> Analysis[Analyze Code (Lint/Test)]
        Analysis -->|Failures Detected| Fixer[AI Fixer Agent]
        Fixer -->|Generate Fix| Applier[Apply Fix & Commit]
        Applier -->|Push Branch| Remote[GitHub Repo]
        Applier -->|Re-run| Analysis
    end
    
    Agent -->|Stream Status| Dashboard[React Dashboard]
```

## ✨ Features

- **Autonomous Healing**: Detects Syntax, Linting, Import, and Logic errors.
- **Sandboxed Execution**: Runs tests in a safe Docker environment.
- **Real-time Dashboard**: Visualizes the fix process, score, and timeline.
- **Smart Branching**: Creates branches in the required format `TEAM_NAME_LEADER_NAME_AI_Fix`.
- **Deterministic & AI Fixes**: Uses both rule-based and LLM-based fixing strategies.

## 🛠 Tech Stack

- **Frontend**: React (Vite), TailwindCSS, Lucide Icons
- **Backend**: Python (FastAPI), LangGraph, LangChain, Google Gemini (LLM)
- **Tools**: Docker, GitPython, Pylint, Pytest

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker (Running)
- Google Cloud API Key (for LLM)

### Backend Setup
1.  Navigate to `backend`:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set Environment Variables:
    ```bash
    export GOOGLE_API_KEY="your_api_key_here"
    ```
4.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```

### Frontend Setup
1.  Navigate to `frontend`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

## 🐛 Supported Bug Types

The agent can currently detect and fix:
1.  **SYNTAX**: Missing colons, indentation errors.
2.  **LINTING**: Unused imports, missing docstrings.
3.  **IMPORT**: `ModuleNotFoundError` or `ImportError`.
4.  **LOGIC**: Test failures (via pytest output analysis).
5.  **TYPE_ERROR**: Basic type mismatches (if caught by linter).

## ⚠️ Known Limitations

-   **Docker Dependency**: The host machine must have Docker running for sandboxed test execution.
-   **LLM Rate Limits**: Heavy usage may hit Gemini API rate limits (retry logic is implemented).
-   **Complex Logic**: Deep architectural bugs may require human intervention.

## 👥 Team

**Team Name**: [INSERT_TEAM_NAME]
**Team Leader**: [INSERT_LEADER_NAME]

-   Member 1: [Name]
-   Member 2: [Name]
