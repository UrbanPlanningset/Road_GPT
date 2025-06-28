<h1>🚦 RoadGPT: A Road Reconstruction Framework via Graph-enhanced Large Language Models</h1>

<p align="center">
  <img src="demo_slow.gif" width="45%" />
  <img src="demo_fast.gif" width="45%" />
</p>

<p><strong>Left:</strong> Slow-motion simulation of traffic flow using SUMO<br>
<strong>Right:</strong> Accelerated version for quick preview</p>

<p>
These animations show how RoadGPT improves traffic conditions through road reconstruction planning. Both are visualized using the SUMO microscopic traffic simulator.
</p>

<hr>

<h2>🔍 Overview</h2>

<p>
RoadGPT is an intelligent urban planning system that reduces structural traffic congestion by reconstructing road networks using advanced AI technologies. It integrates:
</p>

<ul>
  <li>🧠 <strong>Large Language Models (LLMs)</strong> for expert-level reasoning</li>
  <li>🌐 <strong>Graph Convolutional Networks (GCNs)</strong> for spatial structure modeling</li>
  <li>🔁 <strong>Reinforcement Learning (RL)</strong> for iterative optimization via simulation</li>
</ul>

<p><strong>RoadGPT =</strong> LLM (reasoning) + GCN (structure) + RL (optimization)</p>

<hr>

<h2>✨ Key Features</h2>

<ul>
  <li><strong>LLM-Centered Reasoning:</strong> Uses Chain-of-Thought (CoT) prompting to simulate expert planners and produce interpretable reconstruction strategies such as lane widening, road direction changes, and reclassification.</li>
  <li><strong>Graph-Enhanced Structural Awareness:</strong> Employs GCNs to encode topological layouts and capture higher-order spatial dependencies in the road network.</li>
  <li><strong>Reinforcement Learning Optimization:</strong> Models the reconstruction process as a Markov Decision Process (MDP) and uses feedback from the SUMO traffic simulator to continuously improve decision policies.</li>
</ul>

<hr>

<h2>🧭 System Workflow</h2>

<p>
Urban Road Data → LLM Reasoning (CoT) → GCN Embedding → Combined State → RL Agent → Action → SUMO Traffic Simulation → Feedback → Policy Update
</p>

<hr>

<h2>🚀 Getting Started</h2>

<ol>
  <li><strong>Clone the repository</strong><br>
    <code>git clone https://github.com/yourname/roadgpt.git</code><br>
    <code>cd roadgpt</code>
  </li>
  <li><strong>Install dependencies</strong><br>
    <code>pip install -r requirements.txt</code>
  </li>
  <li><strong>Prepare input data</strong><br>
    Place your road network files in the <code>data/</code> directory.
  </li>
  <li><strong>Run the demo</strong><br>
    <code>python run_demo.py --city beijing</code>
  </li>
</ol>

<hr>

<h2>📊 Experimental Results</h2>

<p>Evaluated across five real-world cities:</p>

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>RoadGPT</th>
      <th>Baseline</th>
      <th>Improvement</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Travel Time</td>
      <td>15.3 min</td>
      <td>18.0 min</td>
      <td>↓ 14.6%</td>
    </tr>
    <tr>
      <td>Reconstruction Cost</td>
      <td>$2.8M</td>
      <td>$3.45M</td>
      <td>↓ 18.7%</td>
    </tr>
    <tr>
      <td>Waiting Time</td>
      <td>2.1 min</td>
      <td>2.8 min</td>
      <td>↓ 25.1%</td>
    </tr>
  </tbody>
</table>

<p>RoadGPT shows consistent and scalable performance across different urban environments.</p>

<hr>

<h2>📽️ Demo Animation</h2>

<p>The following animation demonstrates RoadGPT in action:</p>
<ol>
  <li>Identifying traffic bottlenecks</li>
  <li>LLM generating reasoning trajectory</li>
  <li>GCN modeling the road topology</li>
  <li>RL agent proposing interventions</li>
  <li>SUMO simulation and feedback</li>
</ol>

<hr>

<h2>📦 Resources</h2>

<ul>
  <li><strong>Dataset:</strong> <a href="https://drive.google.com/file/d/1bICE26ndR2C29jkfG2qQqVkmpirK25Eu/view">Origin Data</a></li>
  <li><strong>Traffic simulation powered by SUMO:</strong> <a href="https://www.eclipse.org/sumo/">https://www.eclipse.org/sumo/</a></li>
  <li><strong>LLM models:</strong> OpenAI or HuggingFace-compatible interfaces</li>
</ul>
