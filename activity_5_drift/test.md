# Activity 5: Detect Drift and Retrain - Test

This test evaluates your understanding of drift detection, model retraining, and closed-loop lifecycle management as implemented in Activity 5.

---

## Question 1
A liquor distributor notices that 30% more orders are coming from a newly developed suburban area. Product mix and average order sizes remain the same. The model's sales predictions for the new area are inaccurate. Is this data drift or concept drift?
- [ ] Concept drift — the relationship between features and sales has changed
- [ ] Both — any change in the real world is simultaneously data drift and concept drift
- [ ] Neither — the model is simply wrong and needs more training data
- [ ] Data drift — the input distribution has shifted (new geographic area with different characteristics), but the underlying relationship between features and sales is the same; the model just hasn't seen this type of input before

## Question 2
A model trained on 2019 Iowa liquor sales is deployed in January 2020. By April 2020, predictions are wildly inaccurate — the model overestimates bar/restaurant sales and underestimates retail store sales. What type of drift is this, and why can't the model adapt on its own?
- [ ] Data drift — the model needs more features to capture COVID-19
- [ ] The model is overfitting to 2019 data — a simpler model would handle 2020 fine
- [ ] Concept drift — COVID-19 changed the fundamental relationship between features and sales (bars closed, retail surged); the model cannot adapt because it is a static function learned from pre-pandemic data and has no mechanism to update its parameters without retraining
- [ ] This is not drift — 2020 sales are just an outlier year that should be excluded

## Question 3
The production model has R2=0.82 on the current month's data. A retrained candidate model achieves R2=0.79 on the same data. Should the candidate be promoted?
- [ ] No — the candidate (0.79) is worse than the production model (0.82); promoting it would degrade production performance; retraining on new data does not guarantee improvement
- [ ] Yes — the candidate was trained on newer data, so it must be more relevant
- [ ] Yes — 0.79 is close enough to 0.82 that it makes no difference
- [ ] Promote it only if the difference is less than 0.05

## Question 4
Same scenario reversed: production R2=0.75, candidate R2=0.85 on the same data. Should the candidate be promoted? What made the difference?
- [ ] No — the production model has been validated in production for longer, making it more trustworthy
- [ ] Yes — the candidate (0.85) clearly outperforms production (0.75); the candidate was likely retrained on data that includes recent patterns the original model never learned, improving its ability to predict current behavior
- [ ] No — a 0.10 improvement might be overfitting to the current month's data
- [ ] Maybe — run it for 3 months in shadow mode before deciding

## Question 5
The monitoring system uses an expanding window (all historical + new data) for retraining. An alternative is a sliding window (last N months only). During a sudden economic shift, which window adapts faster, and which is more robust to transient anomalies?
- [ ] Both windows behave identically — the window size does not affect model quality
- [ ] Sliding window is always better because old data is irrelevant
- [ ] Expanding window always adapts faster because it has more data
- [ ] Sliding window adapts faster (recent data dominates) but is vulnerable to transient anomalies; expanding window is more robust (more data provides stability) but adapts slower because historical patterns dilute new signals

## Question 6
The model starts at version 1. Over 24 months of monitoring with closed-loop retraining, the model_version reaches 3. How many successful promotions occurred, and what triggers each promotion?
- [ ] 3 promotions — one per version number
- [ ] 24 promotions — one per month
- [ ] 2 promotions (version 1→2, then 2→3) — each promotion means drift was detected, a candidate was retrained, and the candidate outperformed the current production model on that month's data
- [ ] 10 promotions — one per drift month

## Question 7
Of 10 drift months, only 2 led to promotions. The other 8 retrained candidates were rejected. Is the system working correctly?
- [ ] Something is wrong — every drift detection should result in a promotion
- [ ] The system is working correctly — a low promotion rate means the production model is robust; retrained candidates on limited new data often cannot beat a model trained on the full expanding window; the comparison step correctly prevents regressions
- [ ] The system should be reconfigured to always promote retrained models
- [ ] The 8 rejections indicate the retraining process has a bug

## Question 8
The Population Stability Index (PSI) detects a significant shift in the `bottles_sold` feature distribution, but the model's R2 is still 0.83 (above the 0.80 drift threshold). Should the team retrain?
- [ ] Not yet — PSI detects input distribution shift, but R2 shows the model is still performing well; the shift hasn't affected predictions yet; the team should increase monitoring frequency but not retrain a well-performing model
- [ ] Yes — PSI detected drift, so the model must be retrained immediately
- [ ] PSI is unreliable and should be ignored if R2 is acceptable
- [ ] The team should lower the R2 threshold to 0.70 to avoid unnecessary retraining

## Question 9
A monitoring dashboard plots R2 over time. The line shows: stable ~0.90 for months 1-3, drops to ~0.75-0.80 for months 4-8, recovers to ~0.85 for months 9-15, drops again for months 16-20, and recovers for months 21-24. What does this "sawtooth" pattern indicate?
- [ ] The model is broken — R2 should be constant
- [ ] The model is overfitting and underfitting in alternation
- [ ] The sawtooth is caused by random noise — it has no meaning
- [ ] The pattern shows the drift-retrain-recover cycle: performance degrades as the world changes (drift), retraining produces a model that captures new patterns (recovery), until the world changes again (next drift) — this is normal closed-loop behavior

## Question 10
Looking across all 5 activities (A1-A5), trace the evolution of the "validation gate" concept. How does it grow from a simple R2 check to a full closed-loop system?
- [ ] The validation gate is the same in every activity — just checking R2 >= 0.70
- [ ] A1: validate.py checks R2 and sets exit code (pass/fail signal). A2: Docker propagates exit codes to the host (CI integration). A3: Make uses exit codes to block promotion (quality gate in a pipeline). A4: MLflow records the metrics behind the gate decision (auditability). A5: the gate triggers retraining and compares candidates against production (self-healing). The same simple concept — "check a metric, signal pass/fail" — scales from a script to an automated lifecycle
- [ ] The validation gate is removed in A5 — drift detection replaces it
- [ ] Each activity uses a completely different validation approach with no connection
