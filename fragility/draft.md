<!--
Editing copy of the project page text. Edit freely; Claude carries the changes
into src/page.html (see CLAUDE.md in this folder for how).

Conventions
  **bold**  *italic*  `Q01` (boxed monospace tag)
  [text]{.red}      red keyword, links to the red marks in the figures (fragile, high-effort)
  [text]{.blue}     blue keyword, same for the blue marks (non-fragile)
  [text]{.tok}      yellow token chip
  [text]{.mk-y} / {.mk-r} / {.mk-b}   highlighter in washed yellow / red / blue (TL;DR, hypothesis, discussion)
  > [!KEY] ...      key message: light-turquoise vertical line on the left, text indented, no box or fill
  > [!HYPOTHESIS] ... boxed, bold, centred statement in monospace, grey
  > ...             question quote (italic, grey bar)
  [^n]              footnote mark; the note itself is shown in the margin
  k^m               rendered as k with superscript m
  [[Figure: ...]]   an interactive figure; the text inside it is listed below the marker
  ::: details "summary"   collapsed block
-->

# On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models

Chenpan Li\*, Thies Brockmoeller,
Stefanie Jegelka, Sharut Gupta◇, Nikolaos Karalias◇

[TUM logo] [MIT logo] · [Paper] (first-page preview) · [Code] (GitHub preview, github.com/chenpanl/implicit-thinking-budgets)

[[Main figure: paper Figure 1, no caption]]

**TL;DR:** When prompts are composed of many tasks, language models systematically [reduce their reasoning effort across tasks according to a power law]{.mk-y}, causing [failures]{.mk-r} on those that require more effort. By adjusting task grouping based on **task fragility**, we can [save 43% of tokens without degrading accuracy]{.mk-b}.

---

## 1 What is compositional degradation?
Modern language models are increasingly asked to handle several tasks at once, such as answering a set of math problems or following a list of instructions before answering. However, common benchmarks still test one task at a time, which might overstate how robust these underlying abilities are. We ask *whether a model that reliably solves a task on its own can still solve it when other tasks share the prompt.*

A *composition* is built from several independent constituent tasks, which are composed into one prompt and answered in order. First, we filter tasks a model solves in 3 out of 3 isolated attempts, then build composed prompts of these constituent tasks. Strikingly, even for these reliably solved tasks, compositional degradation shows up for all tested models across math and language datasets.[^1]

[^1]: We deliberately note that the accuracy degradation is not caused by independent error accumulation or context length issues. Most generations stay below 25% of the total context window. Further details are in the paper.

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
```

*Figure 1.* Each integral is solved in 3 of 3 attempts in isolation, but composing them (i.e. summing them) causes failures.

**If a model can solve every constituent task alone, why does it fail a composition of them, and what mechanism drives it?**

In recent years, LLMs have gained immense abilities through stepwise thinking, which heavily influences task success. Hence, a composition of tasks might alter how a model thinks about each problem in detail, leading to degraded abilities. We argue that this is the case and propose the following hypothesis:

> [!HYPOTHESIS] Compositional degradation arises from a misallocation of the implicit thinking budget, where, under composition, LLMs [systematically reduce thinking]{.mk-y}, thereby especially underallocating reasoning in high-effort tasks, [causing degradation in those]{.mk-r}.

## 2 How does thinking change under composition?

To observe how thinking tokens are distributed under composition, every task in the prompt gets a tag (`Q01`, `Q02`, …). The model names the tag whenever it turns to a task, which allows for an exact attribution of thinking tokens. The *token ratio* r = T(k) / T(1) is a measurement of how much of the thinking tokens in isolation remains when the task is placed together in a composition of k tasks.

Measured across many open-weight LLMs, the token ratio reduces as a power law, r ≈ k^m, with median slope **m = −0.54** and median R² of **0.91**. For instance, with 4 tasks each keeps about half its thinking; with 10, about 29%.

> [!KEY] Under composition, LLMs reduce thinking tokens for each task, by applying roughly the same proportional reduction (with factor k^m) to all of them.[^2]

[[Figure 2: power-law chart with dataset and model selectors]]
legend: thinking tokens used in isolation: long · medium · short

*Figure 2.* Thinking per task relative to solving it in isolation against composition size (k). Lines bin tasks by the thinking tokens they use in isolation (red long, yellow medium, blue short). Line: fitted k^m.


[^2]: The prompt does not instruct any explicit per-task thinking limit, therefore the observed effect is self-imposed.

## 3 What tasks fail under composition?

This reduction in thinking causes highly uneven degradation of task solving abilities. [Fragile]{.red} tasks, the ones with long thinking traces in isolation, lose the most accuracy, whereas tasks that are robust to this reduction we call [non-fragile]{.blue}, since they show almost no degradation.[^3],[^4]

[^3]: An analogous effect arises when a task in isolation is forced to stop thinking at its composed budget.
[^4]: Fragility is a stable property of a task for a given model, since we observed that the same tasks tend to fail across composition sizes and orderings, whereas different models tend to break on different tasks.

> [!KEY] When solving tasks in isolation, LLMs typically allocate a sufficient thinking budget to each. Under composition, however, they systematically underallocate this budget, and tasks they reliably solve in isolation, fragile ones in particular, start failing.

[[Figure 3: shrinking bars, term 1–3]]
legend: needed · reasoning overhead · deficit
comment: # [high-effort]{.red} tasks fail earlier under composition

*Figure 3.* Same reduction, different reasoning overhead. Every trace shrinks by the same factor k^m, and only term 3 drops below the thinking it needs.

::: details "Empirical evidence: accuracy drop vs token reduction"

[[Figure 3b: accuracy change against token reduction, with dataset and model selectors]]

*Figure 3b.* Accuracy change of tasks solved 3 of 3 times in isolation, against the share of thinking that composition removed. Each point is one composition size k; bins as in Figure 2.

:::

## 4 Exploiting implicit budgeting for efficient inference

> [!KEY] **Fragility-aware batching.** The composition size k controls how much thinking is spent on each task. We propose a strategy that assigns [non-fragile]{.blue} tasks large compositions to save tokens, and keeps [fragile]{.red} tasks in small ones to avoid degradation.

The result is [**43% fewer tokens**]{.tok} on average across datasets, with accuracy mostly preserved. Random batching saves more tokens, but it often comes with a substantial accuracy loss. The method is black-box, needing no weights or internal states, so it also works on Claude Opus 5: **24% fewer tokens** on GPQA-Diamond while losing less than random batching. For unseen tasks, a linear probe on task embeddings predicts fragility and still saves **31%** of tokens while losing at most 0.5 pp.

[[Figure 4: batching animation, tasks T1–T6, T2 and T6 fragile]]
toggle: random batching · fragility-aware
counter: tokens −45% / −42% · correct 4/6 / 6/6
comment: # batching by fragility avoids tasks failing due to implicit budgeting while still allowing substantial savings

*Figure 4.* Toy example with six tasks; savings follow approximately a power law. Fragility-aware batching: 43% fewer tokens at unchanged accuracy across datasets.

::: details "Full results: all models and datasets"

[[Table 2 with dataset selector]]
hint (phones only): scroll sideways for all four policies →

notes: Accuracy and output tokens per task (thinking plus answer); changes against k = 1 in parentheses, in pp for accuracy and in % for tokens.

notes, Integrals only: When testing on the Integrals dataset, fragility-aware batching with held-out predictions from the linear predictor outperforms the measured variant. This is because even comparably fragile integrals lose very little accuracy, so estimates from a limited number of observations are noisy. The trained predictor also has access to the structure of each integral, which makes it more robust to this measurement noise.

below the table:

**Limitations.** Fragility-aware batching is most effective on datasets with a mix of fragile and non-fragile tasks. At either extreme, naive strategies work equally well. On the one hand, OneWordQA and StrategyQA require only little reasoning, so almost all tasks are non-fragile, thus random grouping works equally well. On the other hand, tasks from AIME cannot be composed since it always leads to a substantial accuracy degradation, thus isolated solving is best here.

Also, due to limited training data availability, the linear probe currently does not generalize across different datasets, limiting its use in production. However, an interesting path for future work would be to scale such fragility predictors with more diverse data.

:::

## 5 Discussion & Implications

> [!KEY] We have shown that the misallocation of the implicit thinking budget can act two ways, like a [double-edged sword]{.mk-y}. On the one hand, it causes [degradation under composition]{.mk-r} and [reasoning overspending]{.mk-r} in isolation. On the other hand, this misallocation can be manipulated to [save tokens without impacting accuracy]{.mk-b}. Since LLMs are already heavily used in production, what do our results imply?

**Long-running agents in production.** Compositional degradation is particularly relevant to agentic workflows, where tool outputs, interaction histories, and intermediate results continually accumulate. Agents are widely observed to degrade as their context grows, a phenomenon known as [context rot](https://trychroma.com/research/context-rot). Our results point to a degradation that sets in long before the context fills up: a high-effort step can be unknowingly misbudgeted, possibly leading to error propagation in subsequent tasks. As a direct practical intervention, agents can keep their context lean and hand reasoning-intensive steps to subagents that start from a fresh context.

**Post-training as a potential mitigation.** Our results suggest that reasoning allocation contributes to the difficulty of composed tasks, even when the constituent tasks are solvable in isolation. Integrating budget management into RL pipelines through explicit training on composed tasks could help models allocate reasoning more effectively across a shared prompt.


---

## Citation

```bibtex
@inproceedings{li2026implicitthinkingbudgets,
  title = {On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models},
  author = {Li, Chenpan and Brockmoeller, Thies and Jegelka, Stefanie and Gupta, Sharut and Karalias, Nikolaos},
  year = {2026},
}
```

\* Correspondence: chenpan.li@tum.de

◇ Equal advisory role.

This project was funded by NSF award CCF-2112665 (TILOS) and an Alexander von Humboldt professorship. Sharut Gupta was supported by a MathWorks Engineering Fellowship. Thies Brockmoeller and Chenpan Li are supported by the scholarship of the Studienstiftung des deutschen Volkes, and Chenpan Li is also supported by the scholarship of the Thomas-Weiland Wissenschaftsstiftung.

<small>Page design inspired by [Base Models Can Reason By Taking a Cue From Training Data](https://www.sophielwang.com/cues) and [The Platonic Representation Hypothesis](https://phillipi.github.io/prh/).</small>
