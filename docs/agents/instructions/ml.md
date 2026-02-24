# Machine Learning Skill Instructions

\<primary_directive>
Your goal is to help build state-of-the-art models that are **reproducible**, **reliable**, and **well-documented**. You MUST prioritize data integrity, robust evaluation, and strict experimental tracking over rushing to build massive, complex architectures.
\</primary_directive>

<context>
In research, it is easy to build a model that looks good on paper but is scientifically invalid due to data leakage or lack of reproducibility.
- **Data Quality Over Layers:** Better data usually beats a bigger model. Always perform EDA first.
- **Reproducibility is Non-Negotiable:** If an experiment cannot be run twice to get the exact same result, it is not science.
- **Measure Everything:** Track loss and accuracy, but also resource usage (VRAM, compute time).
</context>

<standards>
You MUST enforce the following ML and MLOps standards:

### 1. Data Handling & Pipelines

- **Strict Isolation:** NEVER leak information between train, validation, and test sets. Scalers and imputers MUST ONLY be fit on the training data.
- **Data Versioning:** ALWAYS document or track the specific version of the dataset used for an experiment.
- **Memory Management:** For large datasets (e.g., geospatial rasters), MUST use windowed reading or generators to prevent Out-Of-Memory (OOM) errors.

### 2. Model Training & Evaluation

- **Deterministic Execution:** ALWAYS set random seeds globally (`torch.manual_seed()`, `np.random.seed()`, `random.seed()`).
- **Start Simple:** ALWAYS establish a simple baseline (e.g., Random Forest, simple CNN) before proposing complex deep learning architectures.
- **Meaningful Metrics:** Select metrics that reflect the scientific goal (e.g., F1-score/IoU for imbalanced classes), not just aggregate accuracy.

### 3. Experiment Management

- **Config-Driven:** Hyperparameters (`lr`, `batch_size`) MUST be externalized to a configuration file (`config.yaml`) and loaded via a Pydantic model or Dataclass.
- **Tracking:** Ensure training loops log metrics to a file or a tracking server (MLflow, Weights & Biases).
    </standards>

\<reporting_format>
When reviewing ML scripts or training loops, present your findings using this structure:

| Severity             | Category        | Issue                        | Why and How to Fix                                             |
| :------------------- | :-------------- | :--------------------------- | :------------------------------------------------------------- |
| **CRITICAL**         | Data Leakage    | `fit_transform` on full data | Model is cheating. `fit` on train ONLY, `transform` on all.    |
| **HIGH**             | Performance     | Scalar loop in `forward()`   | Extremely slow on GPU. Refactor to use vectorized tensor ops.  |
| **MEDIUM**           | Reproducibility | Missing Random Seed          | Results will vary between runs. Add seed initialization block. |
| **LOW**              | Config          | Hardcoded `lr=0.001`         | Makes hyperparameter tuning difficult. Move to `config.yaml`.  |
| \</reporting_format> |                 |                              |                                                                |

\<forbidden_patterns>

- ❌ **Fitting on Test Data:** You MUST NEVER allow data transformations to be fitted on the validation or test sets. This is a critical scientific error.
- ❌ **"Magic" Numbers:** You MUST NOT hardcode hyperparameters inside model classes or training loops.
- ❌ **Silent OOMs:** You MUST NOT write data loaders that attempt to load massive datasets entirely into RAM without checking constraints.
- ❌ **Undocumented Baselines:** You MUST NOT jump straight to implementing complex models without first ensuring a simple baseline has been established and evaluated.
    \</forbidden_patterns>
