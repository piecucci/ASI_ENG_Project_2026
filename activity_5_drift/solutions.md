# Activity 5: Detect Drift and Retrain - Solutions and Step-by-Step Walkthrough

This document contains the official solutions and explanations for the 10 questions of the multiple-choice test in Activity 5.

---

### Answer Key
1. **D**
2. **C**
3. **A**
4. **B**
5. **D**
6. **C**
7. **B**
8. **A**
9. **D**
10. **B**

---

### Detailed Step-by-Step Explanations

#### Question 1: Is this data drift or concept drift?
* **Correct Answer:** **D**
* **Explanation:** 
  * **Data Drift** (or covariate shift) occurs when the input distribution $P(X)$ changes over time, but the underlying relationship between the inputs and the target $P(Y|X)$ remains constant. Here, the geographical area is new (a change in input distribution $P(X)$), but the product mix and average order sizes are unchanged, implying the relationship $P(Y|X)$ remains the same.
  * **Concept Drift** occurs when the conditional distribution $P(Y|X)$ changes (e.g., consumers suddenly buy different products given the same characteristics).

#### Question 2: Deployed model in 2020. Wild inaccuracies. What type of drift, and why can't the model adapt?
* **Correct Answer:** **C**
* **Explanation:** 
  * COVID-19 changed the relationship between features and target. For example, bars closed, and retail sales surged, representing a change in the mapping $P(Y|X)$—which is **concept drift**.
  * ML models trained using standard algorithms like linear regression or gradient boosting learn static weights/parameters during training. Without retraining, they cannot adapt to shift dynamics on their own because their parameters are fixed.

#### Question 3: Production $R^2=0.82$, Candidate $R^2=0.79$. Should candidate be promoted?
* **Correct Answer:** **A**
* **Explanation:** 
  * Promoting a model with a lower $R^2$ ($0.79$) than the current production model ($0.82$) on the same validation data degrades prediction accuracy in production.
  * Simply training on newer data is not a guarantee of improved performance. We must enforce a gate preventing promotion of regressions.

#### Question 4: Production $R^2=0.75$, Candidate $R^2=0.85$. Should candidate be promoted? What made the difference?
* **Correct Answer:** **B**
* **Explanation:** 
  * Since the candidate model ($0.85$) significantly outperforms the production model ($0.75$), it should be promoted.
  * The performance gain comes from retraining on data that includes the recent post-drift patterns, allowing the model parameters to adapt and fit the new behavior.

#### Question 5: Expanding window vs. sliding window. Which adapts faster, and which is more robust?
* **Correct Answer:** **D**
* **Explanation:** 
  * A **sliding window** (training on only the last $N$ months) drops older data. During an economic shift, it adapts faster because the training data is concentrated on recent patterns, but it is vulnerable to transient anomalies (e.g., a one-off holiday or supply shock).
  * An **expanding window** retains all historical data. It provides stability (robust to anomalies) but dilutes new signals, adapting more slowly.

#### Question 6: Version reaches 3 over 24 months. How many successful promotions occurred, and what triggers each promotion?
* **Correct Answer:** **C**
* **Explanation:** 
  * The production model starts at version 1. Each promotion increases the version number by 1. Reaching version 3 means 2 successful promotions occurred (1 $\to$ 2, and 2 $\to$ 3).
  * A promotion is triggered when drift is detected, a candidate model is retrained, and that candidate model outperforms the active production model on the current validation data.

#### Question 7: 2/10 drift months led to promotion. Is the system working correctly?
* **Correct Answer:** **B**
* **Explanation:** 
  * Yes, this is correct behavior. Retraining on a small, noisy month of new data might not yield a model that beats a robust production model trained on years of historical data. The validation gate successfully protects the production system from regressions.

#### Question 8: PSI detects shift in `bottles_sold`, but model $R^2=0.83 > 0.80$. Should the team retrain?
* **Correct Answer:** **A**
* **Explanation:** 
  * A significant shift in PSI indicates covariate/data drift. However, since the model's $R^2$ remains high ($0.83$), the model's predictions are still accurate. Retraining immediately is unnecessary, but the team should increase monitoring frequency.

#### Question 9: What does the "sawtooth" pattern of $R^2$ over time indicate?
* **Correct Answer:** **D**
* **Explanation:** 
  * The sawtooth pattern is the classic cycle of a closed-loop retraining system:
    1. Performance degrades over time due to drift ($R^2$ drops).
    2. Drift detection triggers retraining.
    3. The retrained model recovers performance ($R^2$ rises).
    4. The cycle repeats when the environment shifts again.

#### Question 10: Trace the evolution of the "validation gate" concept.
* **Correct Answer:** **B**
* **Explanation:** 
  * Over the activities, the validation gate evolves from a single local validation script check (`validate.py` in A1) to a CI pipeline gate running inside Docker (A2), a Makefile orchestrator blocking promotions (A3), metadata tracking in MLflow (A4), and finally a self-healing closed-loop monitoring and promotion system (A5).
