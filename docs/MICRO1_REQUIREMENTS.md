# Micro1 submission checklist

Source: `micro1 - First Hackathon97ce7c5.pdf`, checked as text and as ten rendered pages on 30 August 2026.

## What the brief requires

| Requirement | PDF page | Current status |
|---|---:|---|
| Define the user, bottleneck, and practical value | 1 and 7 | Covered in the README |
| Use agents purposefully | 2 and 5 | Covered by the Harbor authoring and evaluation workflow; the brief does not require a skill or MCP server |
| Compare a reasonable baseline and final solution on the same cases | 2 and 4 | Pending as an agent-workflow comparison; Oracle/no-op smoke tests are verifier evidence, not this comparison |
| Choose one primary metric and report complete results | 4 | Primary verifier metric is defined; current-prompt runtime rebinding and Micro1 baseline/final results are pending |
| Keep an Improvement Changelog with meaningful and removed experiments | 3 and 7 | Partial: `CHANGELOG.md` records the verifier iterations and removed experiments, but the simple-baseline and final-workflow rows still need the same-case comparison results |
| Submit complete solution code and agent instructions | 7 | Present in this checkout; no commit or shareable remote yet |
| Provide a clean-environment reproduction guide with versions, runtime, cost, and expected output | 7 | Paths are documented; current-prompt runtime evidence, clean clone URL, and baseline/final runtime and cost are pending |
| Submit a solution video of no more than five minutes | 7 | Missing |
| Submit representative trajectories for every agent used | 7 | Missing |

The evaluation page says: “Ten or more cases is a good target when the task allows it.” This is guidance, not a minimum task count or a requirement to create a benchmark.

## Judging weights

| Criterion | Points |
|---|---:|
| Agent Solution and Engineering | 30 |
| End-to-End Quality | 20 |
| Problem and User Value | 15 |
| Measured Improvement | 15 |
| Reproducibility | 15 |
| Hot Take or Insights | 5 |

The brief says purposeful choices matter more than the number of components. It gives skills, memory, verification, tools, and multi-agent orchestration as possible approaches, not required components.

## Ground rules reflected here

- State what existed before the competition and what was added.
- Use components according to their licenses and service terms.
- Keep consequential execution sandboxed or simulated.
- Keep credentials and private information out of the submission.
- Tie result claims to submitted evidence.
- Give judges enough access to reproduce the main result.

## What the brief does not require

It specifies no PR count, public GitHub repository, research novelty, research-paper date, deployment, skill, MCP server, multi-agent count, benchmark-task count, or RL API. A public repository and a five-task RL environment are project choices.

## Remaining submission work

1. Define the Micro1 baseline and final workflow. The completed stock calibration does not serve as that comparison.
2. Compare both on the same task cases with the same resource budget.
3. Report complete primary-metric results, runtime, token use, and cost.
4. Publish representative redacted trajectories for every agent used.
5. Record the five-minute-or-shorter video.
6. Create a clean commit and give judges a reproducible source URL or private share.
