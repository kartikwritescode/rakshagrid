# training/prepare_dataset.py
import pandas as pd

# Combine your sources: Kaggle fraud-call-india, BothBosu scam-dialogue (HF),
# teeconnie scam/non-scam dataset, + your own synthetic LLM-generated transcripts.
# End goal: a single CSV with columns: text, label (1=scam, 0=normal)

def build_dataset():
    df1 = pd.read_csv("data/fraud_call_india.csv")       
    df2 = pd.read_parquet("data/bothbosu_scam_dialogue.parquet")
    df3 = pd.read_csv("data/synthetic_transcripts.csv")

    combined = pd.concat([
        df1[["text", "label"]],
        df2[["text", "label"]],
        df3[["text", "label"]],
    ], ignore_index=True).drop_duplicates()

    combined.to_csv("data/train_dataset.csv", index=False)
    print(f"Total: {len(combined)} | Scam: {combined.label.sum()} | Normal: {(combined.label==0).sum()}")

if __name__ == "__main__":
    build_dataset()