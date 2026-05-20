# 📚 Week 5 Detailed Execution Guide

**Adaptive Importance Scoring & User Feedback System**

*Phase 2 Begins | 40 hours of focused development*

---

## 🎯 Week 5 Objective

Implement feedback collection system and adaptive importance scoring based on actual usage patterns.

**Success Criteria:**
- ✓ User feedback system working
- ✓ Importance learner implemented
- ✓ Weight optimization functional
- ✓ 20+ new tests passing
- ✓ Integration with Phase 1 complete
- ✓ Feedback data collected

---

## Day 21: Feedback System Design & Implementation

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design feedback system**
- Feedback types:
  - Explicit: User rates memory importance (1-5 stars)
  - Implicit: Track retrieval frequency and patterns
  - Indirect: Measure dwell time on results
- Feedback storage:
  - New table: `memory_feedback` (memory_id, user_id, feedback_type, rating, timestamp)
  - Track: Rating, retrieval count, retrieval recency
  - Calculate: Prediction error (predicted importance vs actual usage)

**Task 2: Implement feedback collector**
- Create: `src/feedback_system.py` (300 lines)
  - `record_feedback(memory_id, feedback_type, value)`
  - `get_feedback_for_memory(memory_id)`
  - `get_user_feedback_stats(user_id)`
  - `calculate_feedback_accuracy()`
  - Track implicit feedback (retrieval frequency)
  - Calculate prediction error (expected vs actual)

**Task 3: Add feedback to API**
- Update `src/memory_system.py`:
  - `add_feedback(memory_id, rating)` - Explicit
  - `track_retrieval(memory_id)` - Implicit
  - `get_memory_feedback(memory_id)`

**Quick Check:**
```bash
python -c "from src.feedback_system import FeedbackSystem; print('✓ Feedback API OK')"
```

### Afternoon (4 hours)

**Task 4: Write feedback tests**
- Create: `tests/test_feedback_system.py` (300 lines)
- Test cases:
  - Record explicit feedback (3 tests)
  - Track implicit feedback (3 tests)
  - Retrieval tracking (2 tests)
  - Feedback accuracy calculation (2 tests)
  - User feedback aggregation (2 tests)
  - Edge cases (2 tests)
- Total: 14 new feedback tests

**Task 5: CLI integration**
- Update `cli.py`:
  - `rate` command - Rate memory importance
  - `feedback_stats` - Show feedback statistics
  - `accuracy` - Show prediction accuracy

**Run This:**
```bash
pytest tests/test_feedback_system.py -v
# Expected: 14 tests passing
python cli.py feedback_stats
```

**Progress:**
- ✓ Feedback system: **IMPLEMENTED**
- ✓ Tests: **14 PASSING**
- ✓ API integration: **COMPLETE**

---

## Day 22: Importance Learner Implementation

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design importance learner**
- Current formula (Phase 1):
  ```
  importance = 0.20*novelty + 0.30*success + 0.25*frequency + 0.15*user + 0.10*emotion
  ```
- Goal: Learn optimal weights from feedback
- Algorithm: Gradient descent optimization
- Constraints: Weights sum to 1.0, all between 0-1

**Task 2: Implement learner**
- Create: `src/importance_learner.py` (400 lines)
  - `ImportanceLearner` class
  - Methods:
    - `collect_training_data()` - Gather feedback samples
    - `calculate_loss(weights)` - MSE between predicted and actual
    - `optimize_weights()` - Gradient descent
    - `get_current_weights()` - Return learned weights
    - `apply_weights()` - Use learned weights in scoring
  - Training:
    - Collect 50+ feedback samples minimum
    - Use scipy.optimize for gradient descent
    - Constraints: 0 <= weight <= 1, sum = 1
    - Learning rate: 0.01
    - Iterations: 100+

**Task 3: Integrate with memory system**
- Update `src/models.py`:
  - Add `weight_version` to EpisodicMemory
  - Track which weights were used
- Update `src/memory_system.py`:
  - Use learned weights in importance calculation
  - Periodic retraining (daily/weekly)
  - Version weights (A/B test)

**Quick Check:**
```bash
python -c "from src.importance_learner import ImportanceLearner; print('✓ Learner OK')"
```

### Afternoon (4 hours)

**Task 4: Write learner tests**
- Create: `tests/test_importance_learner.py` (350 lines)
- Test cases:
  - Weight optimization (3 tests)
  - Loss calculation (2 tests)
  - Convergence (2 tests)
  - Constraint satisfaction (2 tests)
  - Weight application (2 tests)
  - Multiple learner instances (2 tests)
  - Edge cases (2 tests)
- Total: 15 new learner tests

**Task 5: A/B testing setup**
- Support multiple weight sets
- Randomize which weights to use
- Track performance of each
- Compare in statistics

**Run This:**
```bash
pytest tests/test_importance_learner.py -v
# Expected: 15 tests passing
```

**Progress:**
- ✓ Importance learner: **IMPLEMENTED**
- ✓ Tests: **15 PASSING**
- ✓ Total Week 5: **29 tests**

---

## Day 23: Weight Learning Pipeline

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design learning pipeline**
- Phases:
  - Data collection (500+ samples minimum)
  - Feature normalization (0-1 scale)
  - Model training (gradient descent)
  - Validation (hold-out test set)
  - Deployment (use new weights)

**Task 2: Implement data collection**
- Create: `src/learning_pipeline.py` (300 lines)
  - `collect_samples()` - Gather feedback data
  - `prepare_training_data()` - Normalize features
  - `split_train_test(ratio=0.8)` - Validation split
  - `calculate_metrics()` - Accuracy, MSE, correlation

**Task 3: Implement validation**
- Cross-validation: 5-fold
- Hold-out test set: 20%
- Metrics:
  - Mean squared error
  - Mean absolute error
  - Correlation coefficient
  - Prediction accuracy (within 0.1)

**Quick Check:**
```bash
python -c "from src.learning_pipeline import LearningPipeline; print('✓ Pipeline OK')"
```

### Afternoon (4 hours)

**Task 4: Write pipeline tests**
- Create: `tests/test_learning_pipeline.py` (300 lines)
- Test cases:
  - Data collection (2 tests)
  - Feature normalization (2 tests)
  - Train/test split (2 tests)
  - Validation metrics (3 tests)
  - Cross-validation (2 tests)
  - Edge cases (2 tests)
- Total: 13 new pipeline tests

**Task 5: Performance profiling**
- Time to collect 500 samples
- Time to train weights
- Time to validate
- Document results

**Run This:**
```bash
pytest tests/test_learning_pipeline.py -v
# Expected: 13 tests passing
```

**Progress:**
- ✓ Learning pipeline: **IMPLEMENTED**
- ✓ Tests: **13 PASSING**
- ✓ Validation: **COMPLETE**

---

## Day 24: Adaptive Scoring & Monitoring

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Implement adaptive scoring**
- Update `src/memory_system.py`:
  - Use learned weights in all importance calculations
  - Track weight version with each memory
  - Support multiple weight versions for A/B test
  - Fallback to Phase 1 weights if learning incomplete

**Task 2: Add monitoring**
- Create: `src/learning_monitor.py` (250 lines)
  - Track training metrics over time
  - Monitor weight stability
  - Alert if weights diverge significantly
  - Log learning progress
  - Visualize weight changes

**Task 3: Implement scheduling**
- Schedule periodic retraining:
  - Daily if 100+ new feedback samples
  - Weekly if 500+ samples available
  - Hold-out final 50 samples for validation
  - Deploy only if improves validation accuracy

**Quick Check:**
```bash
python -c "from src.learning_monitor import LearningMonitor; print('✓ Monitor OK')"
```

### Afternoon (4 hours)

**Task 4: Write monitoring tests**
- Create: `tests/test_learning_monitor.py` (250 lines)
- Test cases:
  - Track metrics (3 tests)
  - Detect divergence (2 tests)
  - Alert conditions (2 tests)
  - Logging (2 tests)
  - Schedule accuracy (2 tests)
  - Edge cases (2 tests)
- Total: 13 new monitoring tests

**Task 5: Integration tests**
- End-to-end: Feedback → Learning → New weights
- Verify improved predictions
- Measure convergence
- Test fallback behavior

**Run This:**
```bash
pytest tests/test_learning_monitor.py -v
# Expected: 13 tests passing
```

**Progress:**
- ✓ Adaptive scoring: **WORKING**
- ✓ Monitoring: **IMPLEMENTED**
- ✓ Scheduling: **CONFIGURED**

---

## Day 25: Week 5 Completion & Integration

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Full test suite**
```bash
pytest tests/ -v --cov=src
# Expected: Coverage increasing, all tests passing
```

**Task 2: Code review**
- New modules review:
  - feedback_system.py
  - importance_learner.py
  - learning_pipeline.py
  - learning_monitor.py
- Check: Type safety, documentation, error handling

**Task 3: Documentation**
- Create: `LEARNING_SYSTEM.md` (500 lines)
  - Feedback system overview
  - Importance learner design
  - Training process explanation
  - Weight interpretation
  - Limitations and future work

### Afternoon (4 hours)

**Task 4: CLI enhancements**
- Add commands:
  - `feedback add [memory_id] [rating]` - Record feedback
  - `feedback stats` - Show feedback statistics
  - `learning status` - Show training status
  - `learning metrics` - Show accuracy metrics
  - `learning train` - Manual training trigger

**Task 5: Week 5 Summary**
- Count new tests (68+ total)
- Measure improvement in importance prediction
- Verify feedback collection working
- Prepare for Week 6

**Run This:**
```bash
python cli.py learning status
# Expected: Training status displayed
pytest tests/ --cov=src
# Expected: 175+ tests, 85%+ coverage
```

**Progress:**
- ✓ Feedback system: **WORKING**
- ✓ Importance learner: **TRAINED**
- ✓ Monitoring: **OPERATIONAL**
- ✓ Tests: **68+ NEW**
- ✓ Week 5: **COMPLETE**

---

## 📊 Week 5 Metrics

**Code**
- New modules: 4 (feedback, learner, pipeline, monitor)
- New lines: 1200+
- New tests: 68+
- Starting coverage: 85%
- Ending coverage: 85%+ (stable)

**Learning**
- Feedback samples collected: 50-100+
- Weight convergence: Monitored
- Prediction accuracy: Baseline established
- Training time: < 1 minute

**Features**
- Explicit feedback collection: Working
- Implicit feedback tracking: Working
- Weight optimization: Working
- Adaptive scoring: Working
- Monitoring: Working

---

## ✅ Week 5 Completion Checklist

- [ ] Feedback system implemented (14 tests)
- [ ] Importance learner implemented (15 tests)
- [ ] Learning pipeline complete (13 tests)
- [ ] Monitoring system working (13 tests)
- [ ] All tests passing (68+ new)
- [ ] Adaptive scoring functional
- [ ] CLI updated with learning commands
- [ ] Documentation written
- [ ] Integration complete
- [ ] Ready for Week 6

**If all YES:** Week 5 Complete! ✅

---

## 🎓 What You've Built

**Adaptive System Components**
- Feedback collection (explicit + implicit)
- Importance learner (gradient descent optimization)
- Training pipeline (data prep + validation)
- Monitoring system (metrics + alerts)
- Scheduling system (periodic retraining)

**Learning Capabilities**
- Learns optimal signal weights from feedback
- Validates learning with hold-out test set
- Detects and alerts on weight divergence
- Supports A/B testing of different weights
- Automated periodic retraining

**Integration**
- Works with Phase 1 core system
- Backward compatible (fallback to Phase 1 weights)
- Non-intrusive monitoring
- Graceful degradation

---

## 🚀 Ready for Week 6?

**Completion Requirements:**
- ✓ All 68+ tests passing
- ✓ Feedback system stable
- ✓ Learner converging
- ✓ Coverage maintained
- ✓ Documentation complete

→ Proceed to `WEEK6_GUIDE.md`

---

**Week 5 Status:** ✅ COMPLETE  
**Tests Added:** 68+  
**Coverage:** Stable at 85%+  
**Next:** Semantic Memory Layer (Week 6)  

Let's build more! 🚀
