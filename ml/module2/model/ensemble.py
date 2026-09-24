# ml/module2/model/ensemble.py
"""Bounded Stacking Ensemble Meta-Classifier."""

import os
import joblib
import numpy as np
from scipy.optimize import minimize
from ml.module2.config import scam_config
from ml.module2.utils.helpers import get_risk_band

class BoundedLogisticRegression:
    """
    Logistic regression with per-feature box constraints on coefficients.
    Enforces non-negative coefficients on component model probabilities.
    """
    def __init__(self, non_negative_indices=None, C=1.0, random_state=42):
        self.non_negative_indices = non_negative_indices or []
        self.C = C
        self.random_state = random_state
        self.coef_ = None
        self.intercept_ = None
        self.classes_ = None
        self.n_features_in_ = None

    def _loss_and_grad(self, params, X, y, sample_weight):
        n_features = X.shape[1]
        intercept = params[0]
        coef = params[1:]
        
        z = X @ coef + intercept
        pos_mask = z >= 0
        neg_mask = ~pos_mask
        
        sigmoid = np.empty_like(z)
        sigmoid[pos_mask] = 1.0 / (1.0 + np.exp(-z[pos_mask]))
        exp_z = np.exp(z[neg_mask])
        sigmoid[neg_mask] = exp_z / (1.0 + exp_z)
        
        sigmoid = np.clip(sigmoid, 1e-15, 1 - 1e-15)
        nll = -np.sum(sample_weight * (y * np.log(sigmoid) + (1 - y) * np.log(1 - sigmoid)))
        reg = 0.5 * (1.0 / self.C) * np.dot(coef, coef)
        loss = nll + reg
        
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
            n_samples = len(y)
            n_classes = 2
            class_counts = np.bincount(y.astype(int), minlength=2)
            class_weight = n_samples / (n_classes * class_counts)
            sample_weight = np.array([class_weight[int(yi)] for yi in y])
        
        n_features = X.shape[1]
        bounds = [(None, None)]
        for i in range(n_features):
            if i in self.non_negative_indices:
                bounds.append((0, None))
            else:
                bounds.append((None, None))
        
        rng = np.random.RandomState(self.random_state)
        x0 = rng.randn(1 + n_features) * 0.01
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
        self.intercept_ = np.array([result.x[0]])
        self.coef_ = np.array([result.x[1:]])
        return self

    def predict_proba(self, X):
        X = np.asarray(X, dtype=np.float64)
        z = X @ self.coef_[0] + self.intercept_[0]
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
        if os.path.exists(scam_config.ENSEMBLE_MODEL_PATH):
            try:
                import sys
                import types
                if "models" not in sys.modules:
                    sys.modules["models"] = types.ModuleType("models")
                sys.modules["models.ensemble"] = sys.modules[__name__]
                _clf = joblib.load(scam_config.ENSEMBLE_MODEL_PATH)
            except Exception as e:
                print(f"Error loading ensemble meta-model: {e}")

def score_ensemble(tfidf_prob: float, transformer_prob: float, rules_score: float, eng_feats: dict) -> dict:
    _load_model()
    
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
            prob = _clf.predict_proba([feats])[0][1]
            band = get_risk_band(prob)
            return {
                "score": float(prob),
                "band": band,
                "method": "ensemble_stacking"
            }
        except Exception as e:
            print(f"Ensemble prediction error: {e}")

    # Fallback to weighted combination if model artifact is missing or fails
    weighted_score = (tfidf_prob * 0.35) + (transformer_prob * 0.45) + (rules_score * 0.20)
    band = get_risk_band(weighted_score)
    return {
        "score": float(weighted_score),
        "band": band,
        "method": "weighted_fallback"
    }

_load_model()
