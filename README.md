# BRD-to-Application Copilot - Backend & Multi-Agent Orchestration Service

> **Component Notice**: This repository contains the **Backend Service and Multi-Agent Orchestration Engine** for the BRD-to-Application Generation Copilot. It powers the autonomous document parsing, LLM agent choreography, project scaffolding, and runtime process execution.

---

## Overview

The **Backend** is a high-performance Python FastAPI service responsible for converting Business Requirement Documents (BRDs) into complete full-stack Next.js + SQLite applications.

It coordinates a pipeline of specialized autonomous LLM agents that decompose complex requirements, draft technical specifications, implement frontend and backend codebases, manage ephemeral dev server processes on dynamic ports, and perform live code updates.

---

## Multi-Agent Architecture

The core of the system is a structured multi-agent architecture where distinct agents execute specialized roles with token-safe task boundaries:

```
                  ┌──────────────────────────────┐
                  │   Raw BRD (PDF/DOCX/Text)    │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                     [ 1. Architect Agent ]
               Generates complete System Spec (MD)
                                 │
                                 ▼
            ┌───────── [ 2. Refiner Agent ] ──────────┐
            │  Human-in-the-loop chat modifications   │
            └────────────────────┬────────────────────┘
                                 │ User Approval
                                 ▼
                      [ 3. Planner Agent ]
               Builds JSON task graph & file scaffolds
                                 │
             ┌───────────────────┴───────────────────┐
             ▼                                       ▼
    [ 4. Backend Agent ]                    [ 5. Frontend Agent ]
  - Node 22 SQLite (DatabaseSync)         - Dark-theme React UI
  - Seed data & schemas                   - Next.js App Router pages
  - Next.js REST API routes               - Interactive forms & widgets
             └───────────────────┬───────────────────┘
                                 │
                                 ▼
                 [ 6. Integration & QA Agent ]
               - Validates file paths & syntax
               - Links shared dependencies (junction)
               - Allocates dynamic port via ProcessManager
               - Launches Next.js dev server
                                 │
                                 ▼
                [ 7. Application Modifier Agent ]
               - Listens to live chat in Screen 3
               - Performs targeted code diffs on disk
               - Triggers instant Fast Refresh in iframe
```

### Specialized Agent Responsibilities

1. **Architect Agent**
   - **Trigger**: Document parsing and initial submission.
   - **Responsibility**: Ingests unstructured requirements and authors a comprehensive Functional & Technical Architecture Specification in Markdown. Specifies data models, SQLite table schemas, API contracts, page routes, state requirements, and UI guidelines.

2. **Refiner Agent**
   - **Trigger**: Conversational prompts in the Architecture Specification Editor.
   - **Responsibility**: Applies targeted user instructions to update, expand, or correct the Markdown specification prior to code generation.

3. **Planner Agent**
   - **Trigger**: "Approve & Generate" action.
   - **Responsibility**: Analyzes the finalized architecture specification, breaks implementation into granular, token-safe tasks, and scaffolds base files (`package.json`, `tsconfig.json`, `next.config.ts`, `globals.css`).

4. **Backend Agent**
   - **Responsibility**: Implements the SQLite database connection (`src/lib/db.ts`) utilizing Node.js built-in `node:sqlite` (`DatabaseSync`), executes table creation queries, seeds initial data, and implements Next.js App Router API route handlers (`src/app/api/.../route.ts`).

5. **Frontend Agent**
   - **Responsibility**: Generates responsive, accessible, dark-themed user interfaces adhering to standard design constraints (zinc-950 background, zinc-800 borders, Lucide SVG icons). Implements layouts, pages, interactive data grids, modals, and input forms.

6. **Integration & QA Agent**
   - **Responsibility**: Verifies directory integrity and file completeness, links local node modules, queries `ProcessManager` for an available TCP port, and boots the Next.js development server (`npm run dev -- -p <port>`).

7. **Application Modifier Agent**
   - **Trigger**: Live chat panel during runtime preview.
   - **Responsibility**: Analyzes user change requests against existing project files, makes surgical edits directly to the generated code files on disk, and leverages Next.js hot-reloading for immediate preview updates.

---

## Key Backend Services

### 1. Document Parser (`app/services/parser.py`)
Extracts clean, normalized text content from various file formats:
- Adobe PDF (`pypdf`)
- Microsoft Word (`python-docx`)
- Plain text (`.txt`, UTF-8 / ASCII)

### 2. Multi-Agent Pipeline Runner (`app/services/generator.py`)
- Manages agent state transitions, prompt templates, and execution queues.
- Streams live progress and execution logs through Server-Sent Events (SSE).
- Writes generated applications to `Downloads/generated_apps/<project_id>/`.
- Symlinks / junctions `node_modules` from the local environment for instant startup without redundant `npm install` cycles.

### 3. Subprocess & Port Manager (`app/services/process_runner.py`)
- Discovers free ephemeral ports dynamically.
- Spawns background Next.js dev server processes.
- Maintains a registry of active child PIDs and gracefully terminates processes on shutdown, regeneration, or modification to prevent port leaks.

---

## Tech Stack

- **Runtime**: Python 3.12+
- **API Framework**: FastAPI, Uvicorn
- **LLM Orchestration**: LangChain (`langchain-openai`)
- **Data Validation**: Pydantic v2
- **Document Ingestion**: PyPDF, python-docx
- **Networking & Clients**: HTTPX, python-multipart

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+ or 22+ (for running generated applications)
- LLM API credentials (OpenAI-compatible endpoint)

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`:
   ```env
   LLM_API_KEY=your_llm_api_key_here
   LLM_BASE_URL=https://api.openai.com/v1
   LLM_MODEL=gpt-4o
   PORT=8000
   ```

5. Start the backend service:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

