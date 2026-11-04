# Data notes

Updated 2026-11-04.

## Scope

This release contains summaries of 183 selected long-form videos from the Starter Story YouTube channel. The first release covered 101 videos. The refresh adds 82 analyses: 78 videos published after the original crawl (latest original video: 2025-11-16) and four older videos that had transcripts but were not in the original refined analysis. The collection excludes videos shorter than five minutes. One original analyzed video is no longer in the current channel crawl; its source URL and summary remain in the dataset.

The video index is `source-videos.json`; the per-video category summaries are `video-summaries.csv`. `patterns.json` and `insights.md` aggregate recurring themes across those summaries. Raw transcripts are not distributed here.

## Method

The original 101-video catalog and approximate pattern counts came from the Starter Story Pipeline. For this refresh, new video transcripts were summarized by a language model into the same 11 categories. The new category summaries were classified against the existing pattern descriptions. A new theme was added only when at least five distinct new video summaries supported it and the existing catalog did not already cover it. Pattern counts were updated by adding explicit new-video matches to the original estimates. Keyword counts add literal mentions in new category summaries to the original counts.

Each pattern includes source video IDs where available. Those IDs resolve to titles and URLs in `source-videos.json`. The original catalog contained three example IDs that did not map to an analyzed video; they were removed during the refresh. Summaries and category assignments were checked for schema, duplicate IDs, and source linkage. One model-generated video ID typo was corrected against the source index, one weak fourth pattern match was removed, and the four new theme descriptions were checked against their cited summaries. The resulting classifications are model assisted and may still contain interpretation errors.

## How to interpret the data

The count next to a pattern is an **approximate number of video mentions**, not the share of founders using a tactic. Videos can have multiple categories and patterns. The original 101-video counts were model estimates, so totals are not exact survey statistics. A keyword count represents mentions in summaries, not necessarily the founder's actual use of a product.

Starter Story selects and edits stories for its audience. This is not a random sample of startups, and a founder's account is not independent verification of revenue, costs, or results. Do not read the counts as success probabilities, causal effects, or advice that will work for every business. Check the linked source video before relying on a specific claim.

The failure-mode notes under `skills/solo-failures/knowledge/failure-modes.md` come from the historical 101-video subset. Their counts were not recomputed across all 183 videos.
