# training/train_distilbert.py
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

MODEL_NAME = "distilbert-base-uncased"   # swap for "ai4bharat/indic-bert" if you need regional languages

df = pd.read_csv("data/train.csv")
train_df, test_df = train_test_split(df, test_size=0.15, stratify=df["label"], random_state=42)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, max_length=256)

train_ds = Dataset.from_pandas(train_df[["text", "label"]]).map(tokenize, batched=True)
test_ds = Dataset.from_pandas(test_df[["text", "label"]]).map(tokenize, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return {"accuracy": accuracy_score(labels, preds), "precision": precision, "recall": recall, "f1": f1}

training_args = TrainingArguments(
    output_dir="./training_output",
    num_train_epochs=4,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    logging_dir="./logs",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=test_ds,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics,
)

trainer.train()
print(trainer.evaluate())

model.save_pretrained("artifacts/scam-distilbert")
tokenizer.save_pretrained("artifacts/scam-distilbert")