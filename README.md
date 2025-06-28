🚦 RoadGPT: A Road Reconstruction Framework via Graph-enhanced Large Language Models

<p align="center">
  <img src="demo_slow.gif" width="45%" />
  <img src="demo_fast.gif" width="45%" />
</p>

🔍 Overview

RoadGPT is an intelligent urban planning system that reduces structural traffic congestion by reconstructing road networks using advanced AI technologies. It integrates:
	•	🧠 Large Language Models (LLMs) for expert-level reasoning
	•	🌐 Graph Convolutional Networks (GCNs) for spatial structure modeling
	•	🔁 Reinforcement Learning (RL) for iterative optimization via simulation

RoadGPT = LLM (reasoning) + GCN (structure) + RL (optimization)

⸻

✨ Key Features
	•	LLM-Centered Reasoning
Uses Chain-of-Thought (CoT) prompting to simulate expert planners and produce interpretable reconstruction strategies such as lane widening, road direction changes, and reclassification.
	•	Graph-Enhanced Structural Awareness
Employs GCNs to encode topological layouts and capture higher-order spatial dependencies in the road network.
	•	Reinforcement Learning Optimization
Models the reconstruction process as a Markov Decision Process (MDP) and uses feedback from the SUMO traffic simulator to continuously improve decision policies.

⸻

🧭 System Workflow

Urban Road Data → LLM Reasoning (CoT)
→ GCN Embedding → Combined State
→ RL Agent → Action
→ SUMO Traffic Simulation
→ Feedback → Policy Update

⸻

🚀 Getting Started

1. Clone the repository

git clone https://github.com/yourname/roadgpt.git
cd roadgpt

2. Install dependencies

pip install -r requirements.txt

3. Prepare input data

Place your road network files in the data/ directory:

data/
├── beijing.json
├── shanghai.json
└── …

4. Run the demo

python run_demo.py –city beijing

⸻

📁 Project Structure

roadgpt/
├── llm_reasoning/ — Prompt engineering and reasoning logic
├── gcn_encoder/ — Graph-based structural modeling
├── rl_planner/ — Reinforcement learning policy module
├── simulation/ — SUMO interface and traffic metrics
├── data/ — Sample urban road networks
├── assets/ — GIFs and visualizations
└── main.py — Entrypoint script

⸻

📊 Experimental Results

Evaluated across five real-world cities:

Metric	RoadGPT	Baseline	Improvement
Travel Time	15.3 min	18.0 min	↓ 14.6%
Reconstruction Cost	$2.8M	$3.45M	↓ 18.7%
Waiting Time	2.1 min	2.8 min	↓ 25.1%

RoadGPT shows consistent and scalable performance across different urban environments.

⸻

📽️ Demo Animation

The following animation demonstrates RoadGPT in action:
	1.	Identifying traffic bottlenecks
	2.	LLM generating reasoning trajectory
	3.	GCN modeling the road topology
	4.	RL agent proposing interventions
	5.	SUMO simulation and feedback


⸻

📦 Resources
	•	Dataset and code: https://anonymous.4open.science/r/RoadGPT
	•	Traffic simulation powered by SUMO: https://www.eclipse.org/sumo/
	•	LLM models used via OpenAI or HuggingFace-compatible interfaces

