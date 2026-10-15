# CadQuery AI Skill

This repository hosts an AI Skill (`SKILL.md`) for CadQuery. The goal is to provide a highly optimized, dense markdown file that LLMs can use to write perfect CadQuery scripts.

**Status:** The skill itself is tested, but the automated maintenance cron loop is currently untested.

## Goals

1. **Provide Context for LLMs**: Distill the official CadQuery documentation into essential syntax, capabilities, and concepts, specifically optimized for LLM consumption.
2. **Autonomous Maintenance Setup**: While this repository hosts the finalized `SKILL.md`, maintenance is automated via a weekly GitHub Actions workflow independent of local machines. The workflow tracks upstream CadQuery changes, detects modifications under `doc/`, uses Google's Gemini API to synthesize updates while strictly preserving our coordinate conventions, and opens a Pull Request assigned to the maintainer for human-in-the-loop review.
3. **Capture Domain Quirks**: Record critical, undocumented, or non-intuitive behaviors (e.g., coordinate system nuances in CadQuery) to help agents avoid common pitfalls.

## Installation & Usage

### 1. Global Installation (All Projects)
Clone this repository into your global Antigravity skills directory:
```bash
cd ~/.gemini/config/skills/
git clone https://github.com/atiretoo/cadquery-ai-skill.git
```

### 2. Project-Level Installation
Alternatively, install it into a specific project's workspace:
```bash
git clone https://github.com/atiretoo/cadquery-ai-skill.git <project_root>/.agents/skills/cadquery-ai-skill
```

### 3. Activating & Using the Skill
- **Automatic:** Antigravity agents automatically discover the skill and load `SKILL.md` whenever generating, modifying, or debugging CadQuery code.
- **Explicit Mention:** In any Antigravity conversation, type `@cadquery` to force the agent to load the full skill into its context.
- **Always-On Rule (Recommended):** To ensure agents never miss the coordinate conventions, add a rule to `~/.gemini/config/rules/cadquery.md` pointing to this skill.

## Development & AI Policy: The "Centaur" Approach

This project is developed using a collaborative human-AI workflow. The code, architecture, and documentation were written and refined with the assistance of advanced AI models. 

I approach AI not as a tool for blind self-automation, but as a collaborative interaction. I aspire to be a [centaur](https://mitsloan.mit.edu/ideas-made-to-matter/3-ways-to-use-ai-are-you-a-cyborg-a-centaur-or-a-self-automator), "... maintain[ing] structured and controlled interactions with AI, harnessing it as a tool for targeted efficiency". I acknowledge that when learning a new domain I might be a cyborg "... collaborat[ing] closely with the AI tool -- probing its suggestions, allowing it to lead the way, and taking its advice on some occasions while pushing back against it on others." Both are OK. In this model, the AI acts as a high-powered pair-programming partner. It helps me rapidly explore and develop my own understanding of complex topics. Meanwhile, I hold the strategic vision, conduct the physical testing/validation, and apply and build domain knowledge as I go.

For rules regarding AI-assisted contributions from the community, please see the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](LICENSE). 

*Note: This skill is a derivative work of the official [CadQuery Documentation](https://github.com/CadQuery/cadquery), which is originally licensed under the Apache License 2.0. The Apache 2.0 license permits derivative works to be distributed under different licenses provided the original attribution is maintained.*
