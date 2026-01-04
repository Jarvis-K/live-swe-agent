# Agent-Environment Interaction Visualizer

A minimal web app to visualize the interactions between the agent and environment in live-swe-agent.

## Features

- Select and view different issues from the results directory
- Display agent's thought process, actions, and environment outputs
- Show return codes and execution status
- Timeline view of the entire interaction sequence

## Usage

1. Start the server:
```bash
python3 serve.py
```

2. Open your browser to:
```
http://localhost:8000/visualizer.html
```

3. Select an issue from the dropdown and click "Load" to visualize the interaction

## Data Sources

The visualizer reads directly from:
- `/root/live-swe-agent/results/*/*.traj.json` - Trajectory files containing agent-environment interactions
- `/root/live-swe-agent/config/livesweagent_swebench.yaml` - Configuration file defining the agent behavior

## Visualization Components

Each step in the timeline shows:
- **Thought**: Agent's reasoning and analysis
- **Action**: Bash command executed
- **Output**: Environment response with return code
- **Memory**: (if applicable) Retrieved experiences and memory updates

## Files

- `visualizer.html` - Single-page web application
- `serve.py` - Python HTTP server to serve files and trajectory data
