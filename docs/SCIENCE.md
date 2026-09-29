# KASLU LAB — scientific basis, corrections and thesis alignment

Thesis: **AI-based early-warning and self-control for one-stage PN/A**
(Huseyn Guliyev, Environmental Engineering, Nanjing Normal University)

## 1. What was wrong and what changed (2026-09 audit)

| # | Area | Problem | Fix |
|---|------|---------|-----|
| 1 | `core/chemistry.py` | pKa(HNO₂) was 0.29 + 2200/T ≈ 7.7; the real value is ≈ 3.3. FNA was over-estimated ~2500×. | Anthonisen Ka = exp(−2300/(273+T)). Closed-form cross-check in tests. FA/FNA reported on both N basis and molecule basis (Anthonisen thresholds are in mg NH₃/L and mg HNO₂/L). |
| 2 | `core/anammox_model.py` | Specific rate × biomass in **g/L** was subtracted from concentrations in **mg/L** → anammox ~1000× too slow. | New unit-consistent AOB/NOB/AMX model `core/pna_model.py`. |
| 3 | ML (`ml_model`, `hybrid_model`, dataset) | Trained on the buggy simulator's output; NO₃/ΔNH₄ = 0.260 in all 3000 rows; "stable" class in 1/3000 rows; saved model had 7 features but received 8. | Removed. Replaced by the early-warning module that works on **real** reactor data. |
| 4 | Empty modules | `pn_model`, `pn_control`, `dilution`, `lab_state` were empty → Simulation, PN Monitor, Sample Analysis, Analytics, AI Advisor crashed. 4 empty pages. | Implemented; all 22 pages smoke-tested. |
| 5 | FA in operation log | FA computed from **influent** NH₄ with one fixed pH/T. | Reactor effluent NH₄ with per-row pH/T. |
| 6 | Lab notebook | Distilled water treated as a sample; "NO₃ removal efficiency"; NO₂/NH₄ = 1.32 applied to every point. | Distilled = reagent blank (contamination check). TIN removal, ΔNO₃/ΔNH₄, and the 1.32 check only where it applies (PN effluent / anammox feed). |
| 7 | Advice | "SRT < 5 d" and "DO 0.8" given for anammox/one-stage systems (would wash out / inhibit anammox). | Stage-aware checks: `pn` (two-stage) vs `pna` (one-stage). |
| 8 | Intrinsic NO₃ | 0.26/(1+1.32+0.26) = 10 %. | 0.26/2.32 = 11.2 % of consumed N. |
| 9 | Reference [6] | Cited as "Pollice et al. 2009". | Jubany et al. (2009) Water Res. 43(11):2761–2772. That study used OUR/DO control at SRT ≈ 30 d — it does **not** support "SRT < 5 d". |
| 10 | "Stability" | Heuristic number presented as reactor stability. | Renamed *performance index (model)* = TIN removal / theoretical max (or NAR for PN). |
| 11 | Dilution helper | Default dilution factor was computed from the undiluted absorbance and then multiplied again. | Calibration fit (≥5 standards, R² ≥ 0.999), A = k·C + b, blank subtraction, re-measure advice when A > 0.8. |
| 12 | Optimisation / Monte Carlo | Ran on the buggy model; Monte-Carlo DO could be negative. | Vectorised PN/A model; DO clipped; objective = max NRR subject to TIN, NO₂ and ΔNO₃/ΔNH₄ constraints. |

## 2. Key equations

**Anammox (Strous et al., 1998)**
NH₄⁺ + 1.32 NO₂⁻ + 0.066 HCO₃⁻ + 0.13 H⁺ → 1.02 N₂ + 0.26 NO₃⁻ + 0.066 CH₂O₀.₅N₀.₁₅ + 2.03 H₂O

**Alternative (Lotti et al., 2014)** — selectable in the app:
NH₄⁺ + 1.146 NO₂⁻ + 0.071 HCO₃⁻ + 0.057 H⁺ → 0.986 N₂ + 0.161 NO₃⁻ + 0.071 CH₁.₇₄O₀.₃₁N₀.₂₀ + 2.002 H₂O
(verify the coefficients against the paper before citing them numerically).

**One-stage PN/A indicator**
NH₄ removed = 1 + 1.32 = 2.32 per NH₄ used by anammox; NO₃ produced = 0.26
→ ΔNO₃/ΔNH₄ = 0.112 (Strous) or 0.075 (Lotti); maximum autotrophic TIN removal ≈ 89 %.

**FA / FNA (Anthonisen et al., 1976)**
FA (mg NH₃/L) = 17/14 · TAN · 10^pH / (exp(6344/(273+T)) + 10^pH)
FNA (mg HNO₂/L) = 46/14 · NO₂-N / (exp(−2300/(273+T)) · 10^pH)

## 3. Mechanistic model (`core/pna_model.py`)

* Groups: AOB, NOB, anammox (AMX). Monod kinetics, oxygen switches, Arrhenius temperature
  correction (Ea: AOB 68, NOB 44, AMX 70 kJ/mol), FA/FNA non-competitive inhibition of AOB/NOB,
  Haldane nitrite inhibition of anammox. Default parameters: Hao et al. (2002) and Strous et al. (1998).
* CSTR/SBR-average with separate retention for flocs (AOB/NOB) and granules/biofilm (AMX);
  prescribed DO, optional intermittent aeration.
* Numerics: positivity-preserving Patankar–Euler, vectorised over scenarios.
* **Limitations**: no spatial gradients (lumped into an *apparent* anammox K_O), no pH/alkalinity
  dynamics, no heterotrophs/COD, no N₂O. **Not calibrated** — calibrate μmax, K_O and SRTs with your data.

Behaviour checked against literature (`core/scientific_validation.py`, 34 checks): Anthonisen closed forms,
N balance of both stoichiometries, anammox doubling time and specific activity, SHARON principle
(NOB washout at 35 °C, failure at 20 °C), PN/A at DO 0.3 vs 1.0 (Hao et al. 2002), and early-warning
specificity/lead time on a synthetic fault.

## 4. Early warning & self-control (thesis core)

`core/early_warning.py`
1. Indicators: TIN removal, NLR/NRR, ΔNO₃/ΔNH₄, effluent NO₂, residual NH₄, FA, FNA.
2. Rules: ΔNO₃/ΔNH₄ ≥ 0.15 warning, ≥ 0.20 alarm; NO₂ ≥ 20 / 50 mg N/L; TIN removal floor.
3. Statistics: EWMA charts (λ = 0.3, L = 3, analytical-noise floors) and Hotelling T² against a
   baseline of stable days.
4. Forecast: local linear trend → days until warning/alarm (lead time).

`core/self_control.py`
* Expert-rule supervisory controller and a velocity-form PI controller (NH₄ residual + ΔNO₃/ΔNH₄),
  bounded DO steps, intermittent-aeration fallback, **operator confirmation required**.
* `closed_loop_test`: runs each strategy against the model as a digital twin (3 % measurement noise).

## 5. Validation plan for the thesis (what the app cannot do for you)

1. **Data**: daily influent/effluent NH₄, NO₂, NO₃ (and TN), DO, pH, T, HRT; ideally online DO/pH/ORP
   and NH₄/NO₃ probes at 5–15 min resolution. Keep a log of operator actions and upsets.
2. **Calibrate** the model on a stable period (μmax AOB/NOB, apparent K_O,AMX, floc SRT), validate on a
   different period.
3. **Early warning**: label real events (NOB outbreaks, NO₂ build-ups); report detection rate, false
   alarm rate and lead time; compare rules vs EWMA/T² vs any ML model (e.g., LSTM) on a time-ordered split.
4. **Control**: compare fixed DO vs rule vs PI first on the calibrated twin, then in the reactor with
   supervision.
5. **Persistence**: Streamlit Community Cloud resets the SQLite file on restart — export CSVs or move
   to a hosted database before collecting thesis data in the app.

## 6. Corrections for the article "First Stage of Anammox…"

1. "1.32 means nitrite is consumed 32 % faster" → it is a molar ratio (mol NO₂ per mol NH₄), not a rate.
2. "0.13 H⁺ consumption helps keep pH neutral" → consuming H⁺ **raises** pH (anammox produces alkalinity).
3. Standard Methods 4500-NH₃ F is the **phenate** method; Nesslerisation is not in the current edition.
   For Nessler in China cite **HJ 535-2009**; nitrite GB 7493-87 / SM 4500-NO₂⁻ B; nitrate UV
   HJ/T 346-2007 / SM 4500-NO₃⁻ B (A₂₂₀ − 2·A₂₇₅).
4. Reference [6] → Jubany et al. (2009), and it does not support "SRT < 5 d" (they used SRT ≈ 30 d
   with OUR/DO control). Cite Hellinga et al. (1998) for short-SRT (SHARON, SRT = HRT ≈ 1–1.5 d at 30–40 °C).
5. Calibration with 3 standards is too few: use ≥ 5 incl. zero, R² ≥ 0.999; report ×DF back-calculation.
6. AOB outgrow NOB only above ≈ 20–25 °C (Hellinga et al., 1998); at lower temperature NOB can grow faster.
7. The decision table should be quantitative: ΔNO₃/ΔNH₄ ≈ 0.26 (anammox stage) or ≈ 0.11 (one-stage PN/A);
   clearly higher → NOB, clearly lower → heterotrophic denitrification.
8. Table 1 (DO 0.5–1.0, SRT < 5 d, 30–40 °C) describes **two-stage, suspended, sidestream** PN.
   For one-stage PN/A use low DO (≈ 0.1–0.5 mg/L or intermittent aeration), long anammox retention
   (granules/biofilm) and floc-selective wasting (Hao et al., 2002).
9. Consider mentioning Lotti et al. (2014) stoichiometry (1.146 / 0.161) used in recent work.

## References

1. Strous M. et al. (1998) Appl. Microbiol. Biotechnol. 50:589–596.
2. Strous M., Kuenen J.G., Jetten M.S.M. (1999) Appl. Environ. Microbiol. 65(7):3248–3250.
3. Hellinga C. et al. (1998) Water Sci. Technol. 37(9):135–142.
4. Anthonisen A.C. et al. (1976) J. Water Pollut. Control Fed. 48(5):835–852.
5. APHA/AWWA/WEF Standard Methods, 23rd ed. (2017); HJ 535-2009; GB 7493-87; HJ/T 346-2007.
6. Jubany I., Lafuente J., Baeza J.A., Carrera J. (2009) Water Res. 43(11):2761–2772.
7. Lotti T., Kleerebezem R., Lubello C., van Loosdrecht M.C.M. (2014) Water Res. 60:1–14.
8. Hao X., Heijnen J.J., van Loosdrecht M.C.M. (2002) Water Res. 36(19):4839–4849.
9. Emerson K. et al. (1975) J. Fish. Res. Board Can. 32:2379–2383.
