# Solo Founder Playbook

**5 Claude Code skills for solo founders — powered by data from 101 [Starter Story](https://www.youtube.com/@starterstory) video analyses.**

A data-backed startup advisor in your terminal. Every recommendation comes from real patterns extracted from 101 founder interviews.

## Install

```bash
claude plugin install yayashuxue/solo-founder-playbook
```

Or add the marketplace manually:

```bash
claude plugin marketplace add yayashuxue/solo-founder-playbook
```

## Skills

| Skill | What it does | Example |
|-------|-------------|---------|
| `/analyze-idea` | Evaluate your idea against 101 founder patterns | `/analyze-idea a tool that helps devs find API docs faster` |
| `/startup-playbook` | Step-by-step playbook for any goal | `/startup-playbook how do I get my first 100 users?` |
| `/growth-strategy` | Growth & marketing recommendations | `/growth-strategy I run a $2k MRR SaaS for freelancers` |
| `/startup-patterns` | Browse 80+ patterns across 11 categories | `/startup-patterns Marketing/Distribution` |
| `/roast-my-plan` | Get your plan roasted — with data | `/roast-my-plan spend 6 months building before launch` |

## What's in the Data

101 Starter Story videos analyzed through a 5-step AI pipeline:

- **11 categories**: Idea Generation, Validation, Building, Launch, Marketing, Growth, Monetization, Challenges, Team, Costs, Advice
- **80+ patterns** with frequency data
- **300+ keywords/tools** mentioned by founders

**Key findings:**
- 74.3% of founders use AI as a core tool
- Organic channels outperform paid 3.5:1
- 32 founders say "just start" and "ship fast"
- 18 founders explicitly cloned existing ideas
- Solo founders average 90%+ profit margins

## Project Structure

```
.claude-plugin/plugin.json   # Plugin manifest
skills/
  analyze-idea/SKILL.md      # Idea evaluator
  startup-playbook/SKILL.md  # Goal-oriented playbook generator
  growth-strategy/SKILL.md   # Growth advisor
  startup-patterns/SKILL.md  # Pattern browser
  roast-my-plan/SKILL.md     # Plan critic
knowledge/
  patterns.json              # Structured data (11 categories)
  insights.md                # Full pattern descriptions + keywords
```

## License

MIT
