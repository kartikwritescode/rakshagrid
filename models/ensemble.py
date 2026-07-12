# models/ensemble.py
import os
import joblib
import numpy as np
from scipy.optimize import minimize
import config
from utils.helpers import get_risk_band

class BoundedLogisticRegression:
    """
    Logistic regression with per-feature box constraints on coefficients.
    
    Uses scipy L-BFGS-B to enforce that specified feature coefficients
    (e.g. component model probabilities) are non-negative, preventing
    multicollinearity from producing pathological negative weights on
    highly-correlated inputs.
    """
    
    def __init__(self, non_negative_indices=None, C=1.0, random_state=42):
        self.non_negative_indices = non_negative_indices or []
        self.C = C  # Inverse regularization strength (higher = less regularization)
        self.random_state = random_state
        self.coef_ = None
        self.intercept_ = None
        self.classes_ = None
        self.n_features_in_ = None
    
    def _loss_and_grad(self, params, X, y, sample_weight):
        """Negative log-likelihood + L2 penalty, with gradient."""
        n_features = X.shape[1]
        intercept = params[0]
        coef = params[1:]
        
        # Linear predictor
        z = X @ coef + intercept
        
        # Numerically stable sigmoid
        pos_mask = z >= 0
        neg_mask = ~pos_mask
        
        sigmoid = np.empty_like(z)
        sigmoid[pos_mask] = 1.0 / (1.0 + np.exp(-z[pos_mask]))
        exp_z = np.exp(z[neg_mask])
        sigmoid[neg_mask] = exp_z / (1.0 + exp_z)
        
        # Clip for numerical stability
        sigmoid = np.clip(sigmoid, 1e-15, 1 - 1e-15)
        
        # Weighted negative log-likelihood
        nll = -np.sum(sample_weight * (y * np.log(sigmoid) + (1 - y) * np.log(1 - sigmoid)))
        
        # L2 regularization (not on intercept)
        reg = 0.5 * (1.0 / self.C) * np.dot(coef, coef)
        loss = nll + reg
        
        # Gradient
        residuals = sample_weight * (sigmoid - y)
        grad_intercept = np.sum(residuals)
        grad_coef = X.T @ residuals + (1.0 / self.C) * coef
        
        grad = np.concatenate([[grad_intercept], grad_coef])
        return loss, grad
    
    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        self.classes_ = np.array([0, 1])
        self.n_features_in_ = X.shape[1]
        
        if sample_weight is None:
            # Compute balanced class weights
            n_samples = len(y)
            n_classes = 2
            class_counts = np.bincount(y.astype(int), minlength=2)
            class_weight = n_samples / (n_classes * class_counts)
            sample_weight = np.array([class_weight[int(yi)] for yi in y])
        
        n_features = X.shape[1]
        
        # Build bounds: (None, None) for intercept, then per-feature
        bounds = [(None, None)]  # intercept is unconstrained
        for i in range(n_features):
            if i in self.non_negative_indices:
                bounds.append((0, None))  # coefficient must be >= 0
            else:
                bounds.append((None, None))  # unconstrained
        
        # Initialize from zeros
        rng = np.random.RandomState(self.random_state)
        x0 = rng.randn(1 + n_features) * 0.01
        
        # Force initial non-negative values for constrained features
        for i in self.non_negative_indices:
            x0[1 + i] = abs(x0[1 + i])
        
        result = minimize(
            self._loss_and_grad,
            x0,
            args=(X, y, sample_weight),
            method='L-BFGS-B',
            jac=True,
            bounds=bounds,
            options={'maxiter': 10000, 'ftol': 1e-12, 'gtol': 1e-8}
        )
        
        if not result.success:
            print(f"Warning: Optimizer did not converge: {result.message}")
        
        self.intercept_ = np.array([result.x[0]])
        self.coef_ = np.array([result.x[1:]])
        
        return self
    
    def predict_proba(self, X):
        X = np.asarray(X, dtype=np.float64)
        z = X @ self.coef_[0] + self.intercept_[0]
        
        # Numerically stable sigmoid
        sigmoid = np.where(
            z >= 0,
            1.0 / (1.0 + np.exp(-z)),
            np.exp(z) / (1.0 + np.exp(z))
        )
        
        return np.column_stack([1 - sigmoid, sigmoid])
    
    def predict(self, X):
        proba = self.predict_proba(X)
        return self.classes_[np.argmax(proba, axis=1)]

_clf = None

def _load_model():
    global _clf
    if _clf is None:
        if os.path.exists(config.ENSEMBLE_MODEL_PATH):
            try:
                _clf = joblib.load(config.ENSEMBLE_MODEL_PATH)
            except Exception as e:
                print(f"Error loading ensemble meta-model: {e}")

def score_ensemble(tfidf_prob: float, transformer_prob: float, rules_score: float, eng_feats: dict) -> dict:
    """
    Combines outputs of TF-IDF, Transformer, and Rules along with 9 engineered features
    using a trained meta-classifier (HistGradientBoostingClassifier or LogisticRegression).
    Falls back to a weighted average if model is not loaded.
    """
    _load_model()
    
    # Feature list ordered EXACTLY as during training
    feats = [
        tfidf_prob,
        transformer_prob,
        rules_score,
        eng_feats["turn_count"],
        eng_feats["char_len"],
        eng_feats["word_count"],
        eng_feats["placeholder_count"],
        eng_feats["urgency_word_count"],
        eng_feats["money_word_count"],
        eng_feats["authority_word_count"],
        eng_feats["has_phone_number"],
        eng_feats["exclaim_count"]
    ]
    
    if _clf is not None:
        try:
            # Predict probability of class 1 (scam)
            prob = float(_clf.predict_proba([feats])[0][1])
            band = get_risk_band(prob)
            return {"score": prob, "band": band, "method": "ensemble_stacking"}
        except Exception as e:
            print(f"Ensemble meta-model prediction error: {e}")
            
    # Fallback: Weighted average
    weighted_score = (rules_score * 0.20) + (tfidf_prob * 0.30) + (transformer_prob * 0.50)
    band = get_risk_band(weighted_score)
    return {"score": weighted_score, "band": band, "method": "weighted_average_fallback"}

# Load the model eagerly at import time to prevent OpenMP collision with PyTorch
_load_model()
