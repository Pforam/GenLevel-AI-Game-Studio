# 🕹️ GenLevel Studio

> **Describe a vibe. Get the full drop.**
> Procedural content generation engine powered by Google Gemini and algorithmic validation.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

---

## ⚡ Overview

**GenLevel Studio** bridges the gap between creative Generative AI and strict game engine requirements. Instead of relying on unconstrained text or unstable visual models, it combines **Google Gemini LLMs** with **deterministic algorithmic validators** (like `A*` pathfinding and node reachability checks) to output reliable, engine-ready JSON manifests.

---

## 🎯 Supported Blueprints

### 1. 🗺️ 2D Grid Level Layouts
- Generates grid matrices for platformers, rogue-likes, and dungeon crawlers.
- **Algorithmic Guardrail:** Runs an `A*` pathfinding validation loop to guarantee a clear, unobstructed path from the player spawn (`4`) to the goal exit (`5`).

### 2. 📜 RPG Quests & Dialogue Trees
- Generates narrative setups, NPC profiles, rewards, and branching conversation graphs.
- **Algorithmic Guardrail:** Validates that every dialogue node is reachable, choices point to valid IDs, and conversations feature proper endpoints.

### 3. 🌍 3D World Asset Manifests
- Spawns environments with skyboxes, lighting, and categorized assets mapped to spatial coordinates (X, Y, Z).

### 4. ⚔️ Combo Mode (Quest + World)
- Synthesizes an interconnected world where NPC spawn locations and quest objectives link directly to real 3D coordinates.

---

## 🚀 Quick Start Guide

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/GenLevel-Studio.git
cd GenLevel-Studio
```

### 2. Install Dependencies

Make sure you have Python installed, then install the required packages:

```bash
pip install streamlit openai pydantic
```

### 3. Run the Streamlit App

```bash
streamlit run app.py
```

---

## 🔑 Configuration & Usage

1. Open the app in your browser (usually `http://localhost:8501`).
2. Enter your Google Gemini API Key in the sidebar (grab a free one from [Google AI Studio](https://aistudio.google.com/)).
3. Select your desired generation blueprint and adjust hyperparameters like **Chaos Level** (Temperature) or **Grid Dimensions**.
4. Choose a quick-starter preset or write your own custom concept prompt and click **Make it happen!**
5. Download the engine-ready JSON payload for your game project.

---

## 📘 Engine Integration Handbook

GenLevel outputs structured JSON payloads designed to plug directly into standard game development workflows:

| Target | Use Case | How to Integrate |
|--------|----------|------------------|
| **Unity / Godot** | 2D Grids | Parse the 2D integer array row-by-row to instantiate tile prefabs dynamically. |
| **Web / UI** | Dialogue Trees | Feed the node graph into a state machine script to handle choices and outcomes. |
| **Unreal / Blender** | 3D Worlds | Loop through the asset manifest to spawn actors at exact vector coordinates. |

---

## 🛠️ Tech Stack

- **Frontend & UI:** Streamlit (with custom CSS/HTML styling)
- **Intelligence Layer:** Google Gemini API (`gemini-2.5-flash`) via OpenAI-compatible endpoints
- **Validation Layer:** Python algorithms (heapq-based `A*` pathfinding, graph traversal checks)
- **Data Interchange:** Pydantic & strict JSON Mode constraints

---

## 📄 License

This project is open-source and developed for academic and prototyping use. Feel free to fork, modify, and build epic game worlds!
