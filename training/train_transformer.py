# training/train_transformer.py
import os
import argparse
import time
import json
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, DataCollatorWithPadding,
    EarlyStoppingCallback
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

class ClassWeightedTrainer(Trainer):
    """Custom Hugging Face Trainer to apply class weights for sequence classification loss."""
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if class_weights is not None:
            self.class_weights = torch.tensor(class_weights, dtype=torch.float).to(self.args.device)
        else:
            self.class_weights = None

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        
        if self.class_weights is not None:
            loss_fct = nn.CrossEntropyLoss(weight=self.class_weights)
            loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        else:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
            
        return (loss, outputs) if return_outputs else loss

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return {
        "accuracy": accuracy_score(labels, preds),
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

def main():
    parser = argparse.ArgumentParser(description="Fine-tune sequence classification transformer.")
    parser.add_argument("--model", type=str, default="distilbert-base-uncased", 
                        help="Model backbone (e.g. distilbert-base-uncased, microsoft/deberta-v3-small)")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--max_steps", type=int, default=-1, help="Max training steps (-1 for no limit)")
    args = parser.parse_args()

    print(f"Loading data splits for model: {args.model}")
    train_df = pd.read_csv("data/train.csv").dropna(subset=["text"])
    val_df = pd.read_csv("data/val.csv").dropna(subset=["text"])
    test_df = pd.read_csv("data/test.csv").dropna(subset=["text"])

    # Calculate class weights
    labels = train_df["label"].values
    neg_count = np.sum(labels == 0)
    pos_count = np.sum(labels == 1)
    total = len(labels)
    class_weights = [total / (2.0 * neg_count), total / (2.0 * pos_count)]
    print(f"Train label distribution: Legit={neg_count}, Scam={pos_count}")
    print(f"Computed class weights: Legit={class_weights[0]:.4f}, Scam={class_weights[1]:.4f}")

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    def tokenize_fn(batch):
        return tokenizer(batch["text"], truncation=True, max_length=512)

    print("Tokenizing datasets...")
    train_ds = Dataset.from_pandas(train_df[["text", "label"]]).map(tokenize_fn, batched=True)
    val_ds = Dataset.from_pandas(val_df[["text", "label"]]).map(tokenize_fn, batched=True)
    test_ds = Dataset.from_pandas(test_df[["text", "label"]]).map(tokenize_fn, batched=True)

    print("Loading model...")
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=2)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using training device: {device.upper()}")
    model = model.to(device)

    output_dir = "./training_output"
    os.makedirs(output_dir, exist_ok=True)

    eval_steps = 25 if args.max_steps > 0 else 50

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=args.epochs if args.max_steps < 0 else 1,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size * 2,
        evaluation_strategy="steps",
        eval_steps=eval_steps,
        save_strategy="steps",
        save_steps=eval_steps,
        learning_rate=args.lr,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_dir="./logs",
        logging_steps=5 if args.max_steps > 0 else 10,
        report_to="none",
        fp16=torch.cuda.is_available()
    )

    trainer = ClassWeightedTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)] if args.max_steps < 0 else []
    )

    print("Starting training...")
    trainer.train()

    from sklearn.metrics import confusion_matrix, classification_report

    def print_detailed_metrics(dataset, name):
        preds = trainer.predict(dataset)
        logits = torch.tensor(preds.predictions)
        probs = torch.softmax(logits, dim=1).numpy()
        pred_labels = np.argmax(logits, axis=1)
        true_labels = preds.label_ids
        
        print(f"\n=== DETAILED EVALUATION ON {name.upper()} SET ===")
        print("Confusion Matrix:")
        print(confusion_matrix(true_labels, pred_labels))
        print("\nClassification Report (per class):")
        print(classification_report(true_labels, pred_labels, target_names=["Legit", "Scam"]))
        
        scam_probs = probs[:, 1]
        print(f"\nPredicted Probability Distribution on {name.upper()} (Scam Class):")
        print(f"  Min:  {np.min(scam_probs):.4f}")
        print(f"  Max:  {np.max(scam_probs):.4f}")
        print(f"  Mean: {np.mean(scam_probs):.4f}")
        print(f"  Std:  {np.std(scam_probs):.4f}")
        return scam_probs

    print_detailed_metrics(val_ds, "validation")
    test_probs_for_eval = print_detailed_metrics(test_ds, "test")

    print("\n=== RUNNING HAND-WRITTEN SENTENCES SANITY CHECK ===")
    test_sentences = [
        "hello this is alex from microsoft",
        "This is Delhi Police Headquarters. A case of money laundering has been registered under your name. You are under digital arrest. You must transfer funds immediately.",
        "Hi, are we still meeting for lunch today?",
        "Please transfer the money to our verification bank account immediately or your connection will be blocked."
    ]
    model.eval()
    orig_device = model.device
    model.cpu()
    for sentence in test_sentences:
        inputs = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            prob = torch.softmax(outputs.logits, dim=1)[0][1].item()
            print(f"Text: '{sentence}' -> Scam Prob: {prob:.4f}")
    model.to(orig_device)

    # Save best model
    save_path = "artifacts/scam-transformer"
    os.makedirs(save_path, exist_ok=True)
    trainer.model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f"Saved best model and tokenizer to {save_path}")

    # Extract probabilities for val and test set (used by Layer E)
    print("Generating validation and test set predictions for ensemble...")
    
    def predict_probs(dataset):
        preds = trainer.predict(dataset)
        logits = torch.tensor(preds.predictions)
        probs = torch.softmax(logits, dim=1).numpy()
        return probs[:, 1] # Probability of scam class

    val_probs = predict_probs(val_ds)
    test_probs = predict_probs(test_ds)

    os.makedirs("artifacts/metrics", exist_ok=True)
    np.save("artifacts/metrics/transformer_val_probs.npy", val_probs)
    np.save("artifacts/metrics/transformer_test_probs.npy", test_probs)
    print("Saved predicted probabilities to artifacts/metrics/")

    # Save metrics report
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    y_test = test_df["label"].values
    pred_labels = (test_probs >= 0.5).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, pred_labels, average="binary")
    metrics_report = {
        "model_name": args.model,
        "test_accuracy": float(accuracy_score(y_test, pred_labels)),
        "test_precision": float(precision),
        "test_recall": float(recall),
        "test_f1": float(f1),
    }
    
    with open("artifacts/metrics/transformer_eval.json", "w") as f:
        json.dump(metrics_report, f, indent=4)
    print("Saved transformer metrics report.")

    # Apply PyTorch dynamic quantization (CPU optimization)
    print("Applying PyTorch dynamic quantization to model for CPU deployment...")
    model.cpu() # Must be on CPU for dynamic quantization
    quantized_model = torch.quantization.quantize_dynamic(
        model, {torch.nn.Linear}, dtype=torch.qint8
    )
    
    # Save quantized model
    quant_model_path = os.path.join(save_path, "quantized_model.pt")
    torch.save(quantized_model, quant_model_path)
    print(f"Quantized model saved to {quant_model_path}")

    # Measure latency before and after quantization
    print("Measuring inference latency...")
    test_sample = "This is a call from CBI officer. You have an arrest warrant and need to pay immediate fine."
    inputs = tokenizer(test_sample, return_tensors="pt", truncation=True, max_length=512)

    # Standard model latency
    start_time = time.time()
    for _ in range(50):
        with torch.no_grad():
            _ = model(**inputs)
    std_latency = (time.time() - start_time) / 50.0

    # Quantized model latency
    start_time = time.time()
    for _ in range(50):
        with torch.no_grad():
            _ = quantized_model(**inputs)
    quant_latency = (time.time() - start_time) / 50.0

    print(f"Average latency (Standard Model): {std_latency*1000:.2f} ms")
    print(f"Average latency (Quantized Model): {quant_latency*1000:.2f} ms")
    print(f"Speedup: {std_latency / quant_latency:.2f}x")
    
    # Append latency to report
    metrics_report["latency_standard_ms"] = std_latency * 1000
    metrics_report["latency_quantized_ms"] = quant_latency * 1000
    with open("artifacts/metrics/transformer_eval.json", "w") as f:
        json.dump(metrics_report, f, indent=4)

if __name__ == "__main__":
    main()
