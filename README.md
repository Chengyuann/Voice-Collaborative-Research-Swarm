# NexusAI: Voice Collaborative Research Swarm
### (语音驱动的智能协作研究蜂群)

> **Transforming unstructured voice commands into analyst-grade intelligence reports through autonomous multi-agent collaboration.**

![Status](https://img.shields.io/badge/Status-Active-success) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![OpenAgents](https://img.shields.io/badge/Powered%20by-OpenAgents-orange) ![LLM](https://img.shields.io/badge/Model-Qwen%20Max-violet)

## 📖 Executive Summary

**NexusAI** is an advanced multi-agent system designed to automate the lifecycle of complex information research. Unlike traditional search engines, NexusAI operates as a **hierarchical swarm**:

1.  **Listens**: It accepts direct **voice commands** (ASR integration).
2.  **Reasons**: A charismatic "Team Leader" agent decomposes the intent.
3.  **Acts**: Specialized agents perform real-time deep web searches (Google, HackerNews).
4.  **Synthesizes**: An expert analyst compiles raw data into professional, actionable reports.

This project demonstrates the potential of **LLM-based Agentic Workflows** in handling ambiguous human instructions and delivering structured, high-value outputs.

---

## 🏗️ System Architecture

NexusAI adopts a **Hub-and-Spoke (Router)** architectural pattern, enhanced with an asynchronous event bus for robust inter-agent communication.

```ascii
      [ 👤 User Voice Command ]
                │
                ▼ (.wav/.mp3)
    ┌─────────────────────────────┐
    │       NEXUS CORE            │
    │     (Router Agent)          │◀─── Orchestrates & Encourages
    │  "The Charismatic Leader"   │
    └──────┬───────────────▲──────┘
           │               │
  Task     │               │ Final
  Delegate │               │ Report
           ▼               │
    ┌─────────────┐   ┌─────────────┐
    │  INFO SCOUT │   │  SYNTH MIND │
    │(Web Searcher)│   │  (Analyst)  │
    │ "The Hunter"│──▶│ "The Expert"│
    └─────────────┘   └─────────────┘
      ▲     ▲             ▲
      │     │             │
   Google  HackerNews    Knowledge Base

```

---

## 🤖 The Agent Squad

We have engineered distinct personalities for each agent to simulate a high-performance human research team:

| Agent ID | Role | Personality & Capabilities |
| --- | --- | --- |
| **`router`** | **Nexus Core (Team Lead)** | **Charismatic & Strategic.** Handles ASR (Speech-to-Text), interprets user intent, motivates the team with encouraging feedback, and ensures quality control before delivering the final result. |
| **`web-searcher`** | **Info Scout** | **Energetic & Resourceful.** Scours the open web and technical forums (Hacker News). It loves to "brag" about finding hidden gems before submitting raw data. |
| **`analyst`** | **Synth Mind** | **Deep & Academic.** Filters noise from search results, identifies trends, cross-references facts, and generates structured Executive Summaries and Key Findings. |

---

## ✨ Key Innovations

### 1. Seamless Voice-to-Action Pipeline

NexusAI integrates a custom **Voice Tool** module. Users can upload raw audio files (e.g., "Research the current state of Siri"), and the Router automatically:

* Detects the file type.
* Transcribes audio to text using Qwen-Audio models.
* Initiates the research workflow without manual text input.

### 2. "Human-in-the-Loop" Simulation

Unlike silent robotic agents, the NexusAI team creates a **transparent workspace**:

* Agents confirm receipt of tasks.
* They communicate progress updates ("Found 3 interesting articles!").
* They provide mutual feedback ("Great job, Scout! Analyst, take it from here.").
* This builds trust and keeps the user informed of the system's "thought process."

### 3. Robust Event-Driven State Machine

To prevent hallucinations and loops (common in LLM agents), NexusAI implements:

* **Strict Identity Filters:** Prevents agents from responding to their own echoes.
* **Structured Payloads:** Uses standardized JSON events (`task.delegate`, `task.complete`) for error-free data handoff.
* **Fallback Mechanisms:** Handles empty search results or API timeouts gracefully.

---

## 🛠️ Technology Stack

* **Framework:** OpenAgents (Modular Agent System)
* **LLM Backbone:** Qwen-Max / Qwen-Turbo (via Aliyun DashScope)
* **Communication:** gRPC & HTTP Event Bus
* **Tools:**
* `web_search.py`: Brave Search / DuckDuckGo / HackerNews API
* `voice_tools.py`: Audio file processing & ASR transcription



---

## 🚀 Quick Start Guide

### Prerequisites

* Python 3.10+
* Aliyun DashScope API Key (for LLM & Audio)

### 1. Environment Setup

```bash
# Export your API keys
export DASHSCOPE_API_KEY="sk-your-key-here"
# Optional: Better search results
export BRAVE_API_KEY="your-brave-key-here"

# Set python path
export PYTHONPATH=$PYTHONPATH:.

```

### 2. Launch the Swarm

Start all agents in parallel (recommended for full experience):

```bash
# Start the orchestration network
openagents network start network.yaml &

# Launch the agents
openagents agent start agents/router.yaml &
openagents agent start agents/web_searcher.yaml &
openagents agent start agents/analyst.yaml &

```

### 3. Interact

You can interact via the OpenAgents Studio UI or CLI.

* **Text Mode:** "Research the latest breakthroughs in solid-state batteries."
* **Voice Mode:** *Upload a `.wav` file containing your instruction.*

---

## 📂 Project Structure

```
.
├── agents/
│   ├── router.yaml       # The Coordinator with Voice capabilities
│   ├── web_searcher.yaml # The Search Specialist
│   └── analyst.yaml      # The Data Synthesizer
├── tools/
│   ├── voice_tools.py    # ASR implementation
│   └── web_search.py     # Search engines integration
├── network.yaml          # Network topology
└── README.md             # This file

```

---

## 🔮 Future Roadmap

* **Real-time Voice Output (TTS):** Allow the Router to speak the final summary back to the user.
* **Visual Data Generation:** Enable the Analyst to generate charts/graphs based on data.
* **Multi-Modal Input:** Support analyzing images (charts/screenshots) alongside voice commands.

---

**Built for the Future of Work.**
*Competition Submission 2026*

```

```
