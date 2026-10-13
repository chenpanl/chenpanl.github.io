<!--
Editing copy of the project page text. Edit freely; Claude carries the changes
into src/page.html (see CLAUDE.md in this folder for how).

Conventions
  **bold**  *italic*  `Q01` (boxed monospace tag)
  [text]{.red}      red keyword, links to the red marks in the figures (fragile, high-effort)
  [text]{.blue}     blue keyword, same for the blue marks (non-fragile)
  [text]{.tok}      yellow token chip
  [text]{.mk-y} / {.mk-r} / {.mk-b}   TL;DR highlighter in washed yellow / red / blue
  > [!KEY] ...      key-message box (light turquoise)
  > ...             question quote (italic, grey bar)
  [^n]              footnote mark; the note itself is shown in the margin
  k^m               rendered as k with superscript m
  [[Figure: ...]]   an interactive figure; the text inside it is listed below the marker
  ::: details "summary"   collapsed block
-->

# On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models

Chenpan Li\*, Thies Brockmöller,
Stefanie Jegelka, Sharut Gupta◇, Nikolaos Karalias◇

[TUM logo] [MIT logo] · Paper (first-page preview) · Code (GitHub preview, github.com/chenpanl/implicit-thinking-budgets)

[[Main figure: paper Figure 1, no caption]]

**TL;DR:** When prompts are composed of many tasks, language models systematically [reduce their reasoning effort across tasks according to a power law]{.mk-y}, causing [failures]{.mk-r} on those that require more effort. By adjusting task grouping based on **task fragility**, we can [save 43% of tokens without degrading accuracy]{.mk-b}.

---

## 1 What is compositional degradation?

A *composition* is built from several independent constituent tasks, which are pasted into one prompt and answered in order. We keep only tasks a model solves in 3 out of 3 isolated attempts, then compose them. Even for these reliably solved tasks, an accuracy drop shows up for all tested models across math and language datasets.[^1],[^2]

[^1]: It is not error accumulation. If composition had no effect, we would expect the accuracy drop to be close to 0.
[^2]: Nor is it context length. Most responses use under 25% of the context window, and in most datasets fewer than 1% hit the limit.

[[Figure 1: animated terminal]]

```
# filtering tasks solved 3 out of 3 times in isolation
$ solve "∫ 3x² dx"             ✓ ✓ ✓
$ solve "∫ 2·sin(4x+1) dx"     ✓ ✓ ✓
$ solve "∫ x·e^(2x) dx"        ✓ ✓ ✓

$ solve "∫ 3x² + 2·sin(4x+1) + x·e^(2x) dx"
thinking ···
term 1 ✓   term 2 ✓   term 3 ✗
# each term: 3/3 separately. in composition: 2/3.
# why is that?
```

*Figure 1.* Each integral is solved in 3 of 3 attempts alone, but composing them (i.e. summing them) causes failures.

> If a model can solve every constituent task alone, why does it fail a composition of them, and what mechanism drives it?

## 2 What does implicit budgeting look like?

To observe how thinking tokens are distributed, every task in the prompt gets a tag (`Q01`, `Q02`, …). The model names the tag whenever it turns to a task, which allows for an exact attribution of thinking tokens. The *token ratio* r = T(k) / T(1) is a measurement of how much of the thinking tokens in isolation remains when the task is placed together in a composition of k tasks.

Measured across many open-weight LLMs, the token ratio falls as a power law, r ≈ k^m, with median slope **m = −0.54** and median R² of **0.91**. In plain terms, with 4 tasks each keeps about half its thinking; with 10, about 29%.

[[Figure 2: power-law chart with dataset and model selectors]]
legend: isolated thinking: long · medium · short

*Figure 2.* Thinking per task relative to solving it alone. Lines bin tasks by the thinking tokens they use in isolation (red long, yellow medium, blue short). Line: fitted k^m.

> [!KEY] Under composition, LLMs reduce thinking tokens for each task, by applying roughly the same proportional reduction (with factor k^m) to all of them.[^3]

[^3]: The model does this voluntarily. The prompt sets no per-task limit and the context window is far from full, so the model rations on its own.

## 3 What tasks fail under composition?

The same reduction causes highly uneven degradation. [High-effort]{.red} tasks, the ones with long thinking traces alone, lose the most accuracy.[^4] We call these tasks [fragile]{.red}, whereas tasks that are robust to this reduction we call [non-fragile]{.blue}, since they show almost no degradation.[^5],[^6]

[^4]: An analogous effect arises when a solo task is forced to stop thinking at its composed budget.
[^5]: Q: Why is the degradation so uneven? A: Short traces carry slack, more thinking than the task needs. High-effort tasks are more vulnerable because they actually need that many thinking tokens to be solved.
[^6]: Fragility is a stable property of a task for a given model: the same tasks fail across composition sizes and orderings (correlation **0.81**), whereas different models break on different tasks (**0.24**).

> [!KEY] Modern LLMs mostly solve difficult tasks in isolation without trouble. Given a composition, however, they fail to assign each task the thinking budget it needs, so the most difficult constituent tasks fail first.

[[Figure 3: shrinking bars, term 1–3]]
legend: needed · slack · deficit
comment: # [high-effort]{.red} tasks fail earlier under composition

*Figure 3.* Same reduction, different slack. Every trace shrinks by the same factor k^m, and only term 3 drops below the thinking it needs.

::: details "the evidence: accuracy drop vs token reduction (paper fig. 5)"

[[Figure 3b: accuracy change against token reduction, with dataset and model selectors]]

*Figure 3b.* Accuracy change of tasks solved 3 of 3 times alone, against the share of thinking that composition removed. Each point is one composition size k; bins as in Figure 2.

:::

## 4 Exploiting implicit budgeting for efficient inference

> [!KEY] **Fragility-aware batching.** The composition size k controls how much thinking each task gets. So put [non-fragile]{.blue} tasks into large batches to save tokens, and keep [fragile]{.red} tasks in small ones to avoid degradation.

The result is [**43% fewer tokens**]{.tok} on average across datasets, with accuracy unchanged (+0.6 pp). Random batching saves more tokens in the end, but in most cases it comes with a substantial accuracy loss. The method is black-box, needing no weights or internal states, so it also works on Claude Opus 5: [**24% fewer tokens**]{.tok} on GPQA-Diamond while losing only 0.4 pp. For unseen tasks, a linear probe on task embeddings predicts fragility and still saves [**31%**]{.tok} of tokens while losing at most 0.5 pp.

[[Figure 4: batching animation, tasks T1–T6, T2 and T6 fragile]]
toggle: random batching · fragility-aware
counter: tokens −45% / −42% · correct 4/6 / 6/6
comment: # batching by fragility avoids tasks failing due to implicit budgeting while still allowing substantial savings

*Figure 4.* Toy example with six tasks; savings follow approximately a power law. Fragility-aware batching: 43% fewer tokens at unchanged accuracy across datasets.

::: details "full results: all models × datasets (paper Table 2)"

[[Table 2 with dataset selector]]
hint (phones only): scroll sideways for all four policies →

notes: Accuracy and output tokens per task (thinking plus answer); changes against k = 1 in parentheses, in pp for accuracy and in % for tokens. Accuracy losses of 1 pp or more are red.

:::

## 5 Discussion & Implications

**Previous context can cause degradation too.** We deliberately compose independent tasks of the same type, isolating the budget effect in its simplest form. Prior work finds that reasoning traces also shorten when the same task is embedded in irrelevant context, conversation history, or a larger task ([Rodionov et al., 2026](https://arxiv.org/abs/2604.01161)), suggesting that implicit thinking budgeting may extend beyond same-type composition.

**Long-running agents in production.** This is particularly relevant to agentic workflows, where tool outputs, interaction histories, and intermediate results continually accumulate. Agents are widely observed to degrade as their context grows, a phenomenon known as context rot ([Hong et al., 2025](https://trychroma.com/research/context-rot)). Our results point to a degradation that sets in long before the context fills up: a high-effort step can be unknowingly misbudgeted, possibly leading to error propagation in subsequent tasks. As a direct practical intervention, agents can keep their context lean and hand reasoning-intensive steps to subagents that start from a fresh context.

**Post-training as a potential mitigation.** Our results suggest that reasoning allocation contributes to the difficulty of composed tasks, even when the constituent tasks are solvable in isolation. Integrating budget management into RL pipelines through explicit training on composed tasks could help models allocate reasoning more effectively across a shared prompt.

## 6 How to cite this work?

```bibtex
@inproceedings{li2026implicitthinkingbudgets,
  title = {On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models},
  author = {Li, Chenpan and Brockm{\"o}ller, Thies and Jegelka, Stefanie and Gupta, Sharut and Karalias, Nikolaos},
  year = {2026},
}
```

Correspondence: chenpan.li@tum.de

This project was funded by NSF award CCF-2112665 (TILOS) and an Alexander von Humboldt professorship. Sharut Gupta was supported by a MathWorks Engineering Fellowship. Thies Brockmöller and Chenpan Li are supported by the scholarship of the Studienstiftung des deutschen Volkes, and Chenpan Li is also supported by the scholarship of the Thomas-Weiland Wissenschaftsstiftung.

<small>Page design inspired by [Base Models Can Reason By Taking a Cue From Training Data](https://www.sophielwang.com/cues), [Unpaired Multimodal Learning](https://unpaired-multimodal.github.io/) and [The Platonic Representation Hypothesis](https://phillipi.github.io/prh/).</small>
