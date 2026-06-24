---
name: obsidian-research-memory
description: Use when answering experiment-design, progress, run-comparison, ablation, checkpoint, project-memory, or Obsidian sync/update questions for the F-drive research workspace.
---

# Obsidian Research Memory

Use this skill for F-drive research memory work, especially EZSpecificity,
substrate predictability, Phase 1/Phase 2 experiments, MORSE, SPECTRA, and
paper-facing benchmark evidence.

## Memory-First Rule

Before answering non-trivial questions about experiments, progress, ablations,
checkpoints, or project state:

1. Read the relevant Obsidian memory first.
2. Treat raw artifacts as verification, not as a replacement for the memory
   layer.
3. If notes and artifacts disagree, use Obsidian for intent/history and current
   artifacts for execution state.
4. If writing current counts, artifact paths, or run status, verify them from
   disk before writing.

Default vault:

`F:\Obsidian_Work_Memory`

## EZSpecificity / Substrate Predictability Routing

When the task mentions EZSpecificity, substrate predictability, substrate
specificity, enzyme-substrate prediction, Rhea, BRENDA, SABIO-RK, EnzyMap,
SpecBench, ESP, MORSE, or SPECTRA, read this MOC before choosing any writeback
target:

`F:\Obsidian_Work_Memory\02_Experiments\Substrate_Predictability_MOC_20260602.md`

Use the MOC as the router. Do not create a duplicate summary note when one of
the canonical notes below applies.

| Topic | Primary writeback target |
| --- | --- |
| Substrate predictability routing, coverage list, cross-branch boundaries | `F:\Obsidian_Work_Memory\02_Experiments\Substrate_Predictability_MOC_20260602.md` |
| canonical dataset counts, quality gates, dataset contracts, do-not-mix rules | `F:\Obsidian_Work_Memory\02_Experiments\Dataset_Building_Memory_Consolidated_20260602.md` |
| Rhea official-only / Gold-Rxn / Gold-ModelReady | `F:\Obsidian_Work_Memory\02_Experiments\Rhea_HQ_ESIBank_Traceable_Dataset.md` |
| BRENDA/SABIO-RK/EnzyMap/Rhea triplet, failure, or enzyme-substrate tables | `F:\Obsidian_Work_Memory\02_Experiments\SpecBench_Triplet_Three_Tables_20260602.md` |
| BRENDA dot-SMILES, metal-complex, or product-conflict curation | `F:\Obsidian_Work_Memory\02_Experiments\BRENDA_Substrate_Specificity_Curation_20260601.md` |
| Phase 1 pair-level model status, 317k alignment, clean/leakage claims | `F:\Obsidian_Work_Memory\01_Projects\EZSpecificity_MoE_Current.md` plus the relevant Phase1-C note under `02_Experiments` |
| Phase 2 site-selectivity / regioselectivity | `F:\Obsidian_Work_Memory\02_Experiments\Phase2_Site_Selectivity_Experiments.md` |
| Phase-B / MORSE / SPECTRA | `F:\Obsidian_Work_Memory\02_Experiments\Phase_B_MORSE_EC_Predictor.md` or `F:\Obsidian_Work_Memory\02_Experiments\MORSE_Science_No_Pair_Features_20260525.md` |
| Official SOTA data-swap baseline state | `F:\Obsidian_Work_Memory\02_Experiments\EZS_317k_Official_Data_Swap_SOTA_Status.md` |
| ESP/EZSpecificity paper protocol and MORSE manuscript experiment matrix | `F:\Obsidian_Work_Memory\03_Papers\MORSE_Subjournal\MORSE_ESP_EZSpecificity_Dry_Experiment_Analysis_20260525.md` |

Hard rules:

- Keep Phase 1 pair classification, Phase 2 site selectivity, and Phase-B /
  MORSE / SPECTRA claims separate.
- Do not manually edit `02_Experiments\Auto_Run_Cards\*` or `05_Timeline\*`;
  those are generated evidence caches.
- Prefer updating existing canonical/source notes over creating new notes.
- After editing Obsidian markdown, verify wikilinks in the edited note resolve.

## ESP / EZSpecificity Protocol Guard

- EZSpecificity did not retrain ESP on ESIBank; it used released ESP direct
  inference.
- The same-data architecture/data control is EZSpecificity-w/oGCS/CPI, not ESP.
- Never label ESM2-8M + Morgan + newly trained XGBoost as ESP.
- Keep released ESP direct inference, same-data controls, and official/adapted
  data-swap comparators as separate evidence tiers.
- The local paper-aligned reconstruction has 317,577 rows versus 323,783 in the
  EZSpecificity paper; do not call local inference an exact reproduction of the
  original ESIBank aggregate.

## Generic Read Order

For non-substrate F-drive experiment questions, start with:

1. `F:\Obsidian_Work_Memory\00_Index\index.md`
2. `F:\Obsidian_Work_Memory\02_Experiments\EZSpecificity_Experiment_Index.md`
3. `F:\Obsidian_Work_Memory\02_Experiments\F_Drive_Experiment_Registry.md`

Then branch to the relevant project page, experiment family note, and generated
run card only when the task needs it.

## Sync Command

When automatic run-card memory may be stale, use the Codex-side updater:

```powershell
D:\anaconda\python.exe C:\Users\Administrator\.codex\skills\obsidian-research-memory\scripts\obsidian_research_memory.py --config F:\Obsidian_Work_Memory\.automation\research_memory_config.json --scan-once
```

This updates generated run cards, auto-status pages, and timeline artifacts. It
does not replace the manual canonical notes named above.
