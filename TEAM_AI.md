# ZeroGate — AI Team Roadmap

## Team Responsibilities
- ML anomaly detection model development
- Trust score model design and implementation
- Model explainability and transparency
- Model card documentation
- Model evaluation and validation
- Integration with Backend Risk Scoring Engine

---

## 📋 Issues Assigned to AI Team

### Phase 1: Model Documentation (Week 5-6)
**Can start once Backend Risk Scoring is underway**

#### Issue #28: Model Card & Explainability Contract
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1 week  

**Tasks:**
- [ ] **Model Card Documentation:**
  - Model overview and purpose
  - Intended use cases
  - Model architecture (Isolation Forest / LightGBM / etc.)
  - Training data description
  - Evaluation metrics (precision, recall, F1)
  - Limitations and known biases
  - Ethical considerations
  
- [ ] **Explainability Contract:**
  - Every point must be attributable to a named signal
  - Explain how anomaly score maps to point deduction
  - Document the -15 cap and why it exists
  - Explain how model fits into overall scoring (one input among many)
  - Describe what "transparent additive model" means
  
- [ ] **Signal Catalog Documentation:**
  - All identity signals (ID-01 to ID-05) with point values
  - All device signals (DV-01 to DV-07) with point values
  - All network signals (NW-01 to NW-06) with point values
  - All behavioral signals (BH-01 to BH-02) with point values
  - Conditions for each signal
  - Examples for each signal
  
- [ ] **Category Caps Documentation:**
  - Explain why caps exist (prevent one bad observation from dominating)
  - Document cap for each category
  - Show calculation examples
  
- [ ] **Hard Gates Documentation:**
  - List all hard gates (unknown credential, counter regression, etc.)
  - Explain why they cannot be overridden
  - Show decision flow diagram
  
- [ ] **Defense Preparation:**
  - Talking points for academic review
  - Example scenarios with explainable outputs
  - Comparison to black-box models
  - Justification for design choices

**Deliverables:**
- Complete model card document
- Explainability contract ready for defense
- Signal catalog with examples
- Decision flow diagrams
- Ready to defend in academic review

**Dependencies:**
- Backend #5 (Risk Scoring design)
- `docs/risk-scoring-report.md` (reference)

---

### Phase 2: ML Model Development (Week 5-7)

#### Issue #27: Trust Score ML Model ⭐
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2.5 weeks  

**Tasks:**
- [ ] **Feature Engineering:**
  - Time-of-day (normalized 0-1)
  - Day-of-week (one-hot encoded)
  - Historical login velocity (logins per hour)
  - Geographic distance from user's centroid (past 30 days)
  - Device switching frequency
  - Resource sensitivity score
  - Failed auth attempts (past 24 hours)
  - Session duration patterns
  - IP reputation score
  
- [ ] **Data Collection:**
  - Gather historical login data (if available)
  - Generate synthetic data for training (if no history)
  - Label anomalies (manual or rule-based)
  - Train/validation/test split (70/15/15)
  
- [ ] **Model Selection:**
  - **Option 1: Isolation Forest** (unsupervised)
    - Good for detecting outliers without labeled data
    - Fast inference
    - Easy to explain (depth in tree)
  - **Option 2: LightGBM** (supervised)
    - Better accuracy if labeled data available
    - Feature importance scores
    - Histogram-based, very fast
  - **Option 3: Autoencoder** (unsupervised)
    - Deep learning approach
    - Reconstruction error as anomaly score
    - Higher computational cost
  
- [ ] **Training Pipeline:**
  - Data preprocessing and normalization
  - Model training with hyperparameter tuning
  - Cross-validation
  - Model serialization (pickle / ONNX)
  
- [ ] **Bounded Adjustment Logic:**
  - Raw anomaly score → bounded adjustment
  - Map score to [-15, 0] range
  - Ensure cap is never exceeded
  - Test edge cases (extreme anomalies)
  
- [ ] **Model Versioning:**
  - Version 1.0.0 (initial production model)
  - Metadata: version, features, training date, accuracy
  - Artifact storage (model file + metadata)
  
- [ ] **Inference Endpoint:**
  - Integrate with Backend #6
  - `POST /v1/risk/evaluate` implementation
  - Feature extraction from request context
  - Model prediction
  - Return bounded adjustment + confidence
  
- [ ] **Shadow Mode:**
  - Run model and log predictions
  - Do NOT affect actual authorization decisions
  - Monitor: prediction distribution, inference latency
  - Compare shadow vs rule-based scores
  
- [ ] **Canary Deployment:**
  - Apply model to 10% of traffic
  - Monitor for false positives
  - Compare metrics: precision, recall, latency
  - Gradually increase to 100% if metrics acceptable
  
- [ ] **Performance Optimization:**
  - Inference latency ≤ 100ms (p95)
  - Model size ≤ 50MB
  - Memory usage ≤ 200MB
  - Batch inference for efficiency (if applicable)
  
- [ ] **Evaluation Metrics:**
  - Precision (of anomaly detection)
  - Recall (of anomaly detection)
  - F1 score
  - False positive rate (target: < 5%)
  - False negative rate (target: < 10%)
  - AUC-ROC curve

**Deliverables:**
- Trained ML model (serialized file)
- Model produces anomaly scores 0-100
- Adjustment always bounded in [-15, 0]
- Inference latency ≤ 100ms (p95)
- Shadow mode logs predictions
- Evaluation metrics documented
- Model cannot override hard gates

**Dependencies:**
- Backend #5 (Risk Scoring integration point)
- Backend #6 (ML integration)
- Issue #28 (Model Card)

---

## 🔄 After Core Issues Complete (Week 8+)

### Model Monitoring & Maintenance
- [ ] **Monitoring:**
  - Prediction distribution drift
  - Feature distribution drift
  - Inference latency trends
  - Error rate trends
  - False positive / negative rate
  
- [ ] **A/B Testing:**
  - Compare shadow vs active model
  - Compare different model versions
  - Statistical significance testing
  
- [ ] **Model Retraining:**
  - Retraining trigger: performance degradation
  - Automated retraining pipeline
  - Model validation before promotion
  - Rollback capability
  
- [ ] **Feedback Loop:**
  - Collect ground truth labels (security incidents)
  - Retrain model with new data
  - Continuous improvement

### Advanced Features (if time permits)
- [ ] **Ensemble Model:**
  - Combine Isolation Forest + LightGBM
  - Weighted voting
  - Improved accuracy
  
- [ ] **Time-Series Anomaly Detection:**
  - Detect behavioral changes over time
  - LSTM or Transformer for sequential patterns
  
- [ ] **User Profiling:**
  - Build per-user behavioral profiles
  - Detect deviation from user's baseline
  
- [ ] **Explainable AI (SHAP/LIME):**
  - Feature importance per prediction
  - Visual explanations for admins

### Documentation
- [ ] Model training guide
- [ ] Inference API documentation
- [ ] Feature engineering rationale
- [ ] Model evaluation report
- [ ] Troubleshooting guide
- [ ] Retraining procedures

---

## 📊 Success Metrics

- ✅ Model produces scores 0-100 with bounded adjustment
- ✅ Inference latency ≤ 100ms (p95)
- ✅ False positive rate < 5%
- ✅ False negative rate < 10%
- ✅ Adjustment always in [-15, 0]
- ✅ Shadow mode works without affecting decisions
- ✅ Model card complete and ready for defense
- ✅ All 2 issues closed
- ✅ Model explainability verified

---

## 🔗 Critical Dependencies

**Blocked by:**
- Backend #5 (Risk Scoring Engine) — provides integration point
- Backend #6 (ML Anomaly service) — provides inference endpoint

**Blocks:**
- None (AI model is enhancement, not blocker)

---

## 📅 Recommended Timeline

```
Week 5:    #28 (Model Card) — start while Backend works on #5
Week 5-7:  #27 (ML Model) — feature engineering, training, integration
Week 8:    Shadow mode deployment and monitoring
Week 9:    Canary deployment (10% → 50% → 100%)
Week 10+:  Monitoring, evaluation, potential retraining
```

---

## 💡 Tips for AI Team

1. **Start with documentation (#28)** — Clarify what you're building before building it
2. **Synthetic data is OK** — If no historical data, generate realistic synthetic data
3. **Start simple** — Isolation Forest is easier than deep learning
4. **Shadow mode is critical** — Never deploy directly to production
5. **Explainability > Accuracy** — This is a zero-trust system, transparency matters
6. **Bounded adjustment is non-negotiable** — Test edge cases thoroughly
7. **Performance matters** — 100ms inference target is strict
8. **Document everything** — You'll defend this in front of reviewers

---

## 🛠️ Recommended Tech Stack

**ML Frameworks:**
- **scikit-learn** (Isolation Forest, preprocessing)
- **LightGBM** (gradient boosting, fast)
- **TensorFlow/PyTorch** (if using deep learning)

**Feature Engineering:**
- **Pandas** (data manipulation)
- **NumPy** (numerical operations)
- **geopy** (distance calculations for location anomalies)

**Model Serving:**
- **FastAPI** (Python API for inference)
- **ONNX Runtime** (cross-platform model inference)
- **TensorFlow Serving** (if using TensorFlow)

**Monitoring:**
- **MLflow** (experiment tracking, model registry)
- **Prometheus** (metrics)
- **Grafana** (dashboards)
- **Evidently AI** (model drift detection)

**Development:**
- **Jupyter Notebooks** (exploration and prototyping)
- **Poetry** or **pip** (dependency management)
- **pytest** (testing)

---

## 🧪 Testing Checklist

### Model Card (#28)
- [ ] Document is complete and readable
- [ ] All signals documented with examples
- [ ] Hard gates explained clearly
- [ ] Decision flow diagram included
- [ ] Ready for academic review

### ML Model (#27)
- [ ] Model trains successfully
- [ ] Inference works on sample data
- [ ] Bounded adjustment always in [-15, 0]
- [ ] Edge case: extreme anomaly → exactly -15
- [ ] Edge case: normal behavior → 0
- [ ] Inference latency ≤ 100ms (p95)
- [ ] Memory usage ≤ 200MB
- [ ] Model serialization and loading work
- [ ] Versioning metadata correct

### Integration
- [ ] Backend #6 calls model successfully
- [ ] Feature extraction from request context works
- [ ] Response format correct (score + confidence)
- [ ] Error handling (model unavailable, timeout)
- [ ] Fallback behavior (if model fails, use rule-based only)

### Shadow Mode
- [ ] Predictions logged without affecting decisions
- [ ] Log format includes: timestamp, features, prediction, confidence
- [ ] No performance degradation (latency impact ≤ 10ms)
- [ ] Metrics collected: prediction distribution, latency

### Canary Deployment
- [ ] 10% traffic routed to model
- [ ] Metrics compared: shadow vs canary
- [ ] No increase in false positives
- [ ] Rollback plan tested
- [ ] Gradual rollout: 10% → 25% → 50% → 100%

---

## 📐 ML Model Architecture

### Isolation Forest (Recommended for MVP)

```
Input Features (9 dimensions)
    ↓
Isolation Forest (100 trees, depth 8)
    ↓
Anomaly Score (0-1, higher = more anomalous)
    ↓
Mapping Function: score → [-15, 0]
    ↓
Bounded Adjustment (-15 to 0)
```

**Advantages:**
- Unsupervised (no labeled data needed)
- Fast training and inference
- Easy to explain (tree depth = anomaly)
- Battle-tested for anomaly detection

**Training:**
- 100 trees (n_estimators)
- Max depth 8 (auto)
- Contamination 0.05 (5% anomalies expected)

**Mapping:**
```python
def map_to_adjustment(anomaly_score):
    # anomaly_score in [0, 1]
    # 0 = normal, 1 = highly anomalous
    # Map to [-15, 0]
    adjustment = -15 * anomaly_score
    return max(-15, min(0, adjustment))
```

---

### Feature Importance (Expected)

Based on risk scoring design:

1. **Geographic distance** (high) — Impossible travel is strong signal
2. **Login velocity** (high) — Brute force detection
3. **Time-of-day deviation** (medium) — Unusual login times
4. **Device switching** (medium) — Credential sharing detection
5. **IP reputation** (medium) — Known bad actors
6. **Resource sensitivity** (low) — Context for access patterns

---

## 🎓 Defense Preparation

### Questions You'll Get Asked

**Q: Why not a black-box deep learning model?**  
A: Zero-trust requires explainability. Every point must be attributable. A neural network's decision is opaque; our additive model with bounded ML adjustment is transparent.

**Q: How do you prevent the ML model from overriding security decisions?**  
A: Hard gates are evaluated BEFORE the ML model runs. The ML adjustment is capped at -15 points and can only make the score worse, never better.

**Q: What happens if the model is wrong?**  
A: The worst case is -15 points. A user at 95 score drops to 80 (still ALLOW). The ML model cannot cause a DENY on its own; it must combine with other signals.

**Q: How do you handle adversarial attacks on the model?**  
A: The model sees only server-side signals (location, time, history). An attacker cannot directly manipulate model inputs. Even if they could, the -15 cap limits damage.

**Q: How often do you retrain?**  
A: Initially, quarterly or when performance degrades. In production, we'd implement continuous retraining with new ground truth labels from security incidents.

**Q: How do you validate the model?**  
A: Cross-validation during training, shadow mode deployment, A/B testing, and monitoring false positive/negative rates in production.

---

**Generated:** 2026-11-04  
**Repository:** https://github.com/mohamed-hashem182005/ZeroGate  
**Team:** AI (with Backend Team)
