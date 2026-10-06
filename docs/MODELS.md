# Raksha Grid AI Model Registry & Provenance

This document specifies the canonical machine learning artifacts, architectures, training procedures, and retrieval mechanisms for Raksha Grid.

---

## Module 1: Counterfeit Currency Identification (EfficientNet-B0)

### 1. Overview
- **Task**: 5-class banknote authenticity and counterfeit defect classification.
- **Model Architecture**: Transfer learning with `EfficientNet-B0` backbone:
  - Input layer: `(224, 224, 3)` RGB banknote image
  - Feature extractor: `EfficientNetB0(include_top=False, weights="imagenet")` with frozen weights (`base.trainable = False`)
  - Pooling: `GlobalAveragePooling2D`
  - Regularization: `Dropout(rate=0.3)`
  - Classification Head: `Dense(5, activation="softmax")`
- **Output Classes** (5 classes):
  1. `real` — Authentic genuine banknote
  2. `fake_print_defect` — Counterfeit with ink/offset print defects
  3. `fake_color_shift` — Counterfeit with incorrect optical color shifting
  4. `fake_missing_thread` — Counterfeit missing embedded metallic security thread
  5. `fake_missing_microprint` — Counterfeit lacking micro-lettering security features

### 2. Model Artifact & Configuration
- **Canonical Storage Location**: `storage/models/currency_model.h5`
- **File Format**: Keras HDF5 weights (`.h5`)
- **File Size**: ~16.5 MB (16,496,112 bytes)
- **Configuration Variable**: `CURRENCY_MODEL_PATH` (defaults to `storage/models/currency_model.h5` resolved via `rakshagrid.common.configs.base_config.artifact_config`)
- **Version Control Policy**: Model binaries (`*.h5`, `*.keras`, `*.safetensors`, `*.pt`) are strictly excluded from git tracking via `.gitignore`. Never commit model binary files.

### 3. How the Model Is Obtained and Trained
The model is trained using the pipeline notebook located at:
[`pipelines/notebooks/currency_model.ipynb`](file:///c:/files/programming/Python/projects/rakshagrid/pipelines/notebooks/currency_model.ipynb)

#### Training Workflow:
1. **Dataset Ingestion**:
   - High-resolution scans and mobile photographs of authentic Indian currency notes (₹500, ₹2000, ₹100, ₹200).
   - Synthetic defect generation applying realistic optical flaws (color shifts, blurred security threads, micro-print erosion).
2. **Preprocessing & Augmentation**:
   - Resized to `(224, 224)`.
   - Augmentation pipeline: `tf.keras.layers.RandomFlip`, `RandomRotation(0.05)`, `RandomZoom(0.1)`, `RandomContrast(0.15)`.
3. **Training Configuration**:
   - Optimizer: `Adam(learning_rate=1e-3)`
   - Loss function: `sparse_categorical_crossentropy`
   - Initial feature extraction head training followed by fine-tuning.
4. **Export**:
   - Saved via `model.save_weights("storage/models/currency_model.h5")`.

### 4. Calibration & Decision Thresholds
- **Confidence Threshold**: `0.80` (configured in `rakshagrid.common.constants.risk_bands.CALIBRATION.currency_confidence_threshold`).
- **Decision Logic**:
  - `predicted_label == "real"` and $\text{confidence} \ge 0.80 \implies \text{status} = \text{"genuine"}$, $\text{calibrated\_verdict} = \text{"authentic"}$.
  - `predicted_label == "real"` and $\text{confidence} < 0.80 \implies \text{status} = \text{"counterfeit"}$, $\text{calibrated\_verdict} = \text{"suspicious\_low\_confidence"}$ (flagged for manual forensic review).
  - `predicted_label != "real"` $\implies \text{status} = \text{"counterfeit"}$, $\text{calibrated\_verdict} = \text{f"counterfeit\_{predicted\_label}"}$.

### 5. Runtime Failure Handling
- If `currency_model.h5` is not present on disk, the engine **never** initializes random weights for production inference.
- It raises `MissingModelArtifactError` with `module_name="ai-currency"`, returning structured **HTTP 503 Service Unavailable** with machine-readable code `MODEL_UNAVAILABLE`.
