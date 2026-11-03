# Solo Founder Playbook setup for coding agents

Source: https://github.com/yayashuxue/solo-founder-playbook

Install the six skills in the user's current coding agent environment. Use the matching path below and tell the user how to invoke a skill. If the environment is unclear, ask which agent they use. Do not claim installation succeeded until the commands complete and the skill files are present.

## Claude Code

Use Claude Code's plugin commands:

```
/plugin marketplace add yayashuxue/solo-founder-playbook
/plugin install solo-founder-playbook
```

The skills should be available without a restart. If these slash commands cannot be run by the agent, give them to the user to paste into Claude Code.

## OpenAI Codex

Run the installation command from the project's README:

```bash
git clone --single-branch --depth 1 https://github.com/yayashuxue/solo-founder-playbook.git ~/.codex/skills/solo-founder-playbook && bash ~/.codex/skills/solo-founder-playbook/install-codex.sh
```

Restart Codex to load the skills. If the repository already exists at that path, inspect it and use the update steps in its README instead of overwriting it.

## Try before installing

The browser version at https://sfp.fyi/try lets the user choose a skill, enter a situation, and copy a prompt into Claude, ChatGPT, or Gemini. The Chinese version is https://sfp.fyi/cn/try.

The six skills are `/solo-analyze`, `/solo-failures`, `/solo-growth`, `/solo-patterns`, `/solo-playbook`, and `/solo-roast`. The source repository is the authoritative place for install, update, and uninstall instructions.
