# Solo Founder Playbook — Claude Code Skills for Founders

**5 AI-powered startup skills based on data from 101 Starter Story video analyses.**

Think of it as having a data-backed startup advisor in your terminal. Every recommendation comes from real patterns extracted from 101 founder interviews on the [Starter Story](https://www.youtube.com/@starterstory) YouTube channel.

## Skills

| Skill | What it does |
|-------|-------------|
| `/analyze-idea` | Evaluate your startup idea against 101 real founder patterns |
| `/startup-playbook` | Get a step-by-step playbook for any startup goal |
| `/growth-strategy` | Data-backed growth & marketing recommendations |
| `/startup-patterns` | Browse the full pattern database (11 categories, 80+ patterns) |
| `/roast-my-plan` | Get your startup plan roasted — Garry Tan style, with data |

## Quick Start

1. Clone this repo into your project (or anywhere):
```bash
git clone https://github.com/yayashuxue/solo-founder-playbook.git
cd solo-founder-playbook
```

2. Open Claude Code:
```bash
claude
```

3. Use any skill:
```
/analyze-idea A SaaS tool that helps indie hackers find validated business ideas from Reddit
```

```
/startup-playbook How do I get my first 100 paying users?
```

```
/roast-my-plan I want to spend 6 months building a perfect product before launching
```

## What's in the Data

The knowledge base was built by running 101 Starter Story videos through an analysis pipeline:

**11 Categories analyzed:**
- Idea Generation, Validation, Building/Development, Launch
- Marketing/Distribution, Growth, Monetization
- Challenges/Failures, Team/Hiring, Cost/Expenses, Advice/Lessons

**Key findings across 101 videos:**
- 74.3% mention AI as a core tool
- Organic channels outperform paid 3.5:1
- 32 founders say "just start" and "ship fast"
- 18 founders explicitly cloned existing ideas and improved them
- Subscription model dominates (42 videos)
- Average successful solo founder runs at 90%+ profit margins

## Run the Pipeline Yourself

Want to re-run the analysis or analyze a different channel? The pipeline scripts are included.

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
```

### Pipeline Steps
```bash
bash run.sh step1  # Get video URLs from YouTube channel
bash run.sh step2  # Download transcripts
bash run.sh step3  # Analyze chapters with Claude
bash run.sh step4  # Summarize and refine
bash run.sh step5  # Extract cross-video patterns
```

### Required API Keys
- `ANTHROPIC_API_KEY` — for Claude analysis (steps 3-5)
- `YOUTUBE_DATA_API_KEY` — for fetching video URLs (step 1)
- `YOUTUBE_TRANSCRIPT_IO_API_KEY` — for downloading transcripts (step 2)

## Project Structure

```
.claude/commands/      # The 5 Claude Code skills
knowledge/
  patterns.json        # Structured pattern data (11 categories)
  insights.md          # Detailed pattern descriptions + keywords
step1-5_*.py           # Pipeline scripts
```

## License

MIT
