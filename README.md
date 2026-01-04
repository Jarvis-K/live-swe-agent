<div align="center">
<a href="https://mini-swe-agent.com/latest/"><img src="https://raw.githubusercontent.com/live-swe-agent/live-swe-agent.github.io/refs/heads/main/img/livesweagent.png" alt="mini-swe-agent banner" style="height: 8em"/></a>
</div>

<h1 align="center">Live-SWE-agent | The First Live AI Software Agent</h1>

<p align="center">
    <a href="https://live-swe-agent.github.io/"><img src="https://img.shields.io/badge/%F0%9F%8F%86-leaderboard-8A2BE2?style=for-the-badge"></a>
    <a href="https://arxiv.org/abs/2511.13646"><img src="https://img.shields.io/badge/📃-Arxiv-a8324c.svg?style=for-the-badge"></a>
    <a href="https://huggingface.co/livesweagent"><img src="https://img.shields.io/badge/🤗-HuggingFace-eba134.svg?style=for-the-badge"></a>
</p>

Live-SWE-agent is the **first *live*, runtime self-evolving software engineering agent** that expands and revises its own capabilities *on the fly* while working on real-world issues.
Our key insight is that **software agents are themselves software systems**, and modern LLM-based agents already possess the intrinsic capability to extend or modify their own behavior at runtime.

## 📣 News

- **[Nov 24th, 2025]**: Claude Opus 4.5 + Live-SWE-agent scores 79.2% on SWE-bench Verified, leading all current open-source scaffolds!
- **[Nov 20th, 2025]**: Gemini 3 Pro + Live-SWE-agent scores 77.4% on SWE-bench Verified, outperforming all available models!
- **[Nov 17th, 2025]**: Live-SWE-agent achieves the new state-of-the-art solve rate of 45.8% on SWE-Bench Pro!
- **[Nov 17th, 2025]**: We've released Live-SWE-agent 1.0.0!

## 🚀 Quick Start

```bash
# Install dependencies
pip install mini-swe-agent swebench

# Run on a small test set
./run.sh

# Customize your run
SLICE=0:10 MODEL=claude-opus-4 ./run.sh
```

For detailed setup and usage instructions, see [docs/GUIDE.md](docs/GUIDE.md).

## 📁 Repository Structure

```
live-swe-agent/
├── config/              # Agent configuration files
├── docs/                # Complete documentation
│   └── GUIDE.md        # Setup, usage, and troubleshooting
├── scripts/             # Utility scripts
│   ├── analyze_results.py
│   ├── convert_to_predictions.py
│   ├── generate_memory_tools.py
│   ├── run_evaluation.py
│   ├── setup_github_mirror.sh
│   └── setup_git_proxy.sh
├── memory/              # Agent memory storage
├── memory_tools/        # Auto-generated memory tools
├── tools/               # Agent tools
├── run.sh              # Main execution script
└── README.md           # This file
```

## 🏆 Leaderboard

Live-SWE-agent offers a unified and powerful platform that enables genuinely fair, apples-to-apples comparisons for model releases.

On our leaderboard of recent models (all evaluated with Live-SWE-agent), **Claude Opus 4.5** retains the #1 spot with a score of 79.2% on SWE-bench Verified.

<p align="center">
<img src="./assets/leaderboard.png" style="width:50%; margin-left: auto; margin-right: auto;">
</p>

For more details, visit our [leaderboard](https://live-swe-agent.github.io/).

## 📊 Comparison

Comparison between Live-SWE-agent and state-of-the-art solutions on SWE-bench Verified and SWE-Bench Pro:

<p align="center">
<img src="./assets/comparison.png" style="width:80%; margin-left: auto; margin-right: auto;">
</p>

## ⚙️ Artifacts

Download complete trajectories, patches, and results from our [v1.0.0 release](https://github.com/OpenAutoCoder/live-swe-agent/releases/tag/v1.0.0):
- `swebench_verified`: Complete runs on SWE-bench Verified
- `swebench_pro`: Complete runs on SWE-Bench Pro

Also available on 🤗 HuggingFace [datasets](https://huggingface.co/livesweagent/datasets).

## 📖 Documentation

- **[Complete Guide](docs/GUIDE.md)** - Setup, usage, evaluation workflow, memory system, and troubleshooting

## 📜 Citation

```bibtex
@article{livesweagent,
  author    = {Xia, Chunqiu Steven and Wang, Zhe and Yang, Yan and Wei, Yuxiang and Zhang, Lingming},
  title     = {Live-SWE-agent: Can Software Engineering Agents Self-Evolve on the Fly?},
  year      = {2025},
  journal   = {arXiv preprint},
}
```

## 🙏 Acknowledgements

- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)
- [SWE-bench](https://www.swebench.com/)
- [SWE-Bench Pro](https://scale.com/blog/swe-bench-pro/)
