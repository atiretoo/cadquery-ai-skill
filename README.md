# CadQuery AI Skill (Untested)

This repository hosts an AI Skill (`SKILL.md`) for CadQuery. The goal is to provide a highly optimized, dense markdown file that LLMs can use to write perfect CadQuery scripts.

**Status:** Untested.

## Goals

1. **Provide Context for LLMs**: Distill the official CadQuery documentation into essential syntax, capabilities, and concepts, specifically optimized for LLM consumption.
2. **Autonomous Maintenance Setup**: While this repository hosts the finalized `SKILL.md`, the actual maintenance happens via a local automated setup. A local cron job runs within an Antigravity AI agent, which fetches upstream changes from the main CadQuery repository, scans for documentation updates, and autonomously updates and pushes the revised `SKILL.md` here.
3. **Capture Domain Quirks**: Record critical, undocumented, or non-intuitive behaviors (e.g., coordinate system nuances in CadQuery) to help agents avoid common pitfalls.

## Development & AI Policy: The "Centaur" Approach

This project is developed using a collaborative human-AI workflow. The CadQuery scripts, Python generators, and overall system architecture were written and refined with the assistance of **Google Gemini**. 

We approach AI not as a tool for blind automation, but as a [collaborative "Centaur"](https://mitsloan.mit.edu/ideas-made-to-matter/3-ways-to-use-ai-are-you-a-cyborg-a-centaur-or-a-self-automator). In this model, the AI acts as a high-powered pair-programming partner. It helps us rapidly explore and develop our own understanding of complex topics—whether that is navigating the quirks of 3D modeling coordinate systems, calculating trapezoidal tolerances, or optimizing Python code. Meanwhile, we maintain the strategic vision, conduct the physical testing, and apply and build domain knowledge in maker systems as we go.

For rules regarding AI-assisted contributions from the community, please see our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](LICENSE). 

*Note: This skill is a derivative work of the official [CadQuery Documentation](https://github.com/CadQuery/cadquery), which is originally licensed under the Apache License 2.0. The Apache 2.0 license permits derivative works to be distributed under different licenses provided the original attribution is maintained.*
