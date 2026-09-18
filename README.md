# CadQuery AI Skill Maintainer

This repository hosts a self-updating AI Skill (`SKILL.md`) for CadQuery. The goal is to provide a highly optimized, dense markdown file that LLMs can use to write perfect CadQuery scripts.

## Goals

1. **Provide Context for LLMs**: Distill the official CadQuery documentation into essential syntax, capabilities, and concepts, specifically optimized for LLM consumption.
2. **Autonomous Maintenance**: Automatically keep the `SKILL.md` file up to date with the latest upstream CadQuery changes via an autonomous AI cron loop.
3. **Capture Domain Quirks**: Record critical, undocumented, or non-intuitive behaviors (e.g., coordinate system nuances in CadQuery) to help agents avoid common pitfalls.

## Development & AI Policy: The "Centaur" Approach

This project is developed using a collaborative human-AI workflow. The CadQuery scripts, Python generators, and overall system architecture were written and refined with the assistance of **Google Gemini**. 

We approach AI not as a tool for blind automation, but as a [collaborative "Centaur"](https://mitsloan.mit.edu/ideas-made-to-matter/3-ways-to-use-ai-are-you-a-cyborg-a-centaur-or-a-self-automator). In this model, the AI acts as a high-powered pair-programming partner. It helps us rapidly explore and develop our own understanding of complex topics—whether that is navigating the quirks of 3D modeling coordinate systems, calculating trapezoidal tolerances, or optimizing Python code. Meanwhile, we maintain the strategic vision, conduct the physical testing, and apply and build domain knowledge in maker systems as we go.

For rules regarding AI-assisted contributions from the community, please see our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the [Apache License 2.0](LICENSE).
