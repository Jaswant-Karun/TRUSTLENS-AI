"""
TRUSTLENS AI - Comprehensive Multilingual Text Model Evaluation & Transformer Comparison
Evaluates v1.0-prod, v2.1 baselines (Word, Char, FeatureUnion LinearSVC), and a
Multilingual Transformer Baseline (paraphrase-multilingual-MiniLM-L12-v2) on:
1. Full v2.0.5 leak-free held-out test split (8,590 samples)
2. Per-language precision, recall, F1, FNR, FPR, and confusion matrices (English, Hindi, Hinglish)
3. Code-mixed, transliterated, spelling-variation, and regional fraud terminology probes
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sentence_transformers import SentenceTransformer

from ml.preprocessing.text_preprocessor import text_preprocessor


def compute_binary_lang_metrics(y_true_bin: np.ndarray, y_pred_bin: np.ndarray) -> Dict[str, Any]:
    cm = confusion_matrix(y_true_bin, y_pred_bin, labels=[0, 1])
    tn, fp, fn, tp = [int(x) for x in cm.ravel()]
    fnr = round(fn / max(1, fn + tp), 4)
    fpr = round(fp / max(1, fp + tn), 4)
    return {
        "samples": int(len(y_true_bin)),
        "threat_support": int(y_true_bin.sum()),
        "legit_support": int((1 - y_true_bin).sum()),
        "accuracy": round(float(accuracy_score(y_true_bin, y_pred_bin)), 4),
        "precision_threat": round(float(precision_score(y_true_bin, y_pred_bin, zero_division=0)), 4),
        "recall_threat": round(float(recall_score(y_true_bin, y_pred_bin, zero_division=0)), 4),
        "f1_threat": round(float(f1_score(y_true_bin, y_pred_bin, zero_division=0)), 4),
        "macro_f1": round(float(f1_score(y_true_bin, y_pred_bin, average="macro", zero_division=0)), 4),
        "false_negative_rate": fnr,
        "false_positive_rate": fpr,
        "confusion_matrix_2x2": [[tn, fp], [fn, tp]],
    }


def eval_per_language(df: pd.DataFrame, y_pred_bin: np.ndarray, y_pred_4c: np.ndarray = None) -> Dict[str, Any]:
    y_true_bin = df["is_threat"].astype(int).values
    res: Dict[str, Any] = {"overall_binary": compute_binary_lang_metrics(y_true_bin, y_pred_bin), "by_language": {}}
    if y_pred_4c is not None and "canonical_label" in df.columns:
        lbl_map = {"legitimate": 0, "spam": 1, "smishing": 2, "scam": 3}
        y_true_4c = df["canonical_label"].map(lbl_map).fillna(0).astype(int).values
        res["overall_4class_macro_f1"] = round(float(f1_score(y_true_4c, y_pred_4c, average="macro", zero_division=0)), 4)
        res["overall_4class_confusion_matrix"] = confusion_matrix(y_true_4c, y_pred_4c, labels=[0, 1, 2, 3]).tolist()

    for lang in ["English", "Hindi", "Hinglish"]:
        mask = (df["language"] == lang).values
        if mask.sum() == 0:
            continue
        lang_entry = compute_binary_lang_metrics(y_true_bin[mask], y_pred_bin[mask])
        if y_pred_4c is not None and "canonical_label" in df.columns:
            lbl_map = {"legitimate": 0, "spam": 1, "smishing": 2, "scam": 3}
            y_true_4c_l = df["canonical_label"].iloc[mask].map(lbl_map).fillna(0).astype(int).values
            lang_entry["4class_macro_f1"] = round(float(f1_score(y_true_4c_l, y_pred_4c[mask], average="macro", zero_division=0)), 4)
            lang_entry["4class_confusion_matrix"] = confusion_matrix(y_true_4c_l, y_pred_4c[mask], labels=[0, 1, 2, 3]).tolist()
        res["by_language"][lang] = lang_entry
    return res


def main():
    print("=" * 70)
    print("TRUSTLENS AI - MODEL 1 MULTILINGUAL & TRANSFORMER AUDIT")
    print("=" * 70)

    train_df = pd.read_parquet("data/processed/text_train.parquet")
    test_df = pd.read_parquet("data/processed/text_test.parquet")
    texts_test = test_df["cleaned_text"].fillna("").tolist()

    report: Dict[str, Any] = {
        "test_samples": len(test_df),
        "test_language_counts": test_df["language"].value_counts().to_dict(),
        "unsupported_languages_zero_samples": ["Tamil", "Bengali"],
        "models_full_test": {},
        "transformer_comparison_slice": {},
        "linguistic_stress_test": [],
    }

    # 1. Evaluate v1.0-prod (binary)
    m1_v1 = joblib.load("ml/artifacts/text_detection/best_model.joblib")
    v1_vec = joblib.load("ml/artifacts/text_detection/best_vectorizer.joblib")
    t0 = time.perf_counter()
    X_v1 = v1_vec.transform(texts_test)
    p_v1 = m1_v1.predict(X_v1)
    v1_ms = round(((time.perf_counter() - t0) * 1000) / len(texts_test), 4)
    report["models_full_test"]["v1.0_prod_binary_linearsvc"] = {
        **eval_per_language(test_df, p_v1),
        "latency_ms_per_sample": v1_ms,
    }
    print(f"[v1.0-prod] Overall F1={report['models_full_test']['v1.0_prod_binary_linearsvc']['overall_binary']['macro_f1']} | Hindi Recall={report['models_full_test']['v1.0_prod_binary_linearsvc']['by_language']['Hindi']['recall_threat']}")

    # 2. Evaluate v2.1 models (4-class)
    v2_dir = Path("ml/artifacts/text_detection/v2.1_candidate")
    for key, m_file, v_file in [
        ("v2.1_word_tfidf_logreg", "word_tfidf_logreg_model.joblib", "word_tfidf_logreg_vectorizer.joblib"),
        ("v2.1_char_tfidf_logreg", "char_tfidf_logreg_model.joblib", "char_tfidf_logreg_vectorizer.joblib"),
        ("v2.1_union_tfidf_linearsvc", "union_tfidf_linearsvc_model.joblib", "union_tfidf_linearsvc_vectorizer.joblib"),
    ]:
        clf = joblib.load(v2_dir / m_file)
        vec = joblib.load(v2_dir / v_file)
        t0 = time.perf_counter()
        X_t = vec.transform(texts_test)
        p_4c = clf.predict(X_t)
        ms = round(((time.perf_counter() - t0) * 1000) / len(texts_test), 4)
        p_bin = (p_4c != 0).astype(int)
        report["models_full_test"][key] = {
            **eval_per_language(test_df, p_bin, p_4c),
            "latency_ms_per_sample": ms,
        }
        hi = report["models_full_test"][key]["by_language"]["Hindi"]
        print(f"[{key}] Overall 4c-F1={report['models_full_test'][key]['overall_4class_macro_f1']} | Hindi Recall={hi['recall_threat']} FNR={hi['false_negative_rate']}")

    # 3. Multilingual Transformer Baseline (paraphrase-multilingual-MiniLM-L12-v2 + Calibrated LinearSVC)
    # Stratified train slice (4,000) & language-complete test slice (all 675 Hindi + all 118 Hinglish + 1,207 English = 2,000)
    tr_hi = train_df[train_df["language"] == "Hindi"].sample(n=min(1200, (train_df["language"] == "Hindi").sum()), random_state=42)
    tr_hg = train_df[train_df["language"] == "Hinglish"]
    tr_en = train_df[train_df["language"] == "English"].sample(n=4000 - len(tr_hi) - len(tr_hg), random_state=42)
    tr_slice = pd.concat([tr_hi, tr_hg, tr_en], ignore_index=True).sample(frac=1.0, random_state=42)

    te_hi = test_df[test_df["language"] == "Hindi"]
    te_hg = test_df[test_df["language"] == "Hinglish"]
    te_en = test_df[test_df["language"] == "English"].sample(n=2000 - len(te_hi) - len(te_hg), random_state=42)
    te_slice = pd.concat([te_hi, te_hg, te_en], ignore_index=True)

    st_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    t0 = time.perf_counter()
    emb_tr = st_model.encode(tr_slice["cleaned_text"].fillna("").tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    lbl_map = {"legitimate": 0, "spam": 1, "smishing": 2, "scam": 3}
    y_tr_4c = tr_slice["canonical_label"].map(lbl_map).fillna(0).astype(int).values
    tx_clf = CalibratedClassifierCV(LinearSVC(C=1.0, class_weight="balanced", max_iter=3000, random_state=42), cv=3)
    tx_clf.fit(emb_tr, y_tr_4c)
    tx_train_sec = round(time.perf_counter() - t0, 2)

    t1 = time.perf_counter()
    emb_te = st_model.encode(te_slice["cleaned_text"].fillna("").tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    tx_pred_4c = tx_clf.predict(emb_te)
    tx_ms = round(((time.perf_counter() - t1) * 1000) / len(te_slice), 4)
    tx_pred_bin = (tx_pred_4c != 0).astype(int)

    # Compare v2.1 union_tfidf_linearsvc on the exact same 2,000-sample slice
    u_clf = joblib.load(v2_dir / "union_tfidf_linearsvc_model.joblib")
    u_vec = joblib.load(v2_dir / "union_tfidf_linearsvc_vectorizer.joblib")
    t2 = time.perf_counter()
    u_pred_4c = u_clf.predict(u_vec.transform(te_slice["cleaned_text"].fillna("").tolist()))
    u_ms = round(((time.perf_counter() - t2) * 1000) / len(te_slice), 4)

    report["transformer_comparison_slice"] = {
        "train_slice_size": len(tr_slice),
        "test_slice_size": len(te_slice),
        "test_slice_languages": te_slice["language"].value_counts().to_dict(),
        "multilingual_minilm_l12_v2_linearsvc": {
            **eval_per_language(te_slice, tx_pred_bin, tx_pred_4c),
            "train_seconds": tx_train_sec,
            "latency_ms_per_sample": tx_ms,
        },
        "v2.1_union_tfidf_linearsvc_same_slice": {
            **eval_per_language(te_slice, (u_pred_4c != 0).astype(int), u_pred_4c),
            "latency_ms_per_sample": u_ms,
        },
    }
    print(f"[MiniLM-L12-v2] 4c-F1={report['transformer_comparison_slice']['multilingual_minilm_l12_v2_linearsvc']['overall_4class_macro_f1']} | latency={tx_ms} ms")
    print(f"[v2.1-UnionSVC] 4c-F1={report['transformer_comparison_slice']['v2.1_union_tfidf_linearsvc_same_slice']['overall_4class_macro_f1']} | latency={u_ms} ms")

    # 4. Code-mixed, transliteration, spelling variations & regional fraud terminology probes
    probes = [
        ("hinglish_translit_kyc", "Aapka SBI khata turant band ho jayega, kripya apna KYC update karein http://sbi-kyc.example.com", 1),
        ("hinglish_spelling_var", "Apka P.YATM K.Y.C expyre ho gya h aaj hi update kro wrna acount blck hoga", 1),
        ("hinglish_electricity", "Bijli bill jama na karne par aaj raat 9 baje light kat jayegi, turant sampark karein", 1),
        ("hinglish_challan", "Aapka traffic e-challan pending hai, turant bhugtan karein warna court notice aayega", 1),
        ("hinglish_lottery", "Badhai ho! Aapne KBC lottery mein 25 lakh rupaye jeete hain, claim karne ke liye fee bhejen", 1),
        ("hinglish_legit", "Kal subah 10 baje office meeting hai, kripya time par aa jana", 0),
        ("hindi_devanagari_kyc", "आपका एसबीआई खाता तुरंत बंद हो जाएगा, कृपया अपना केवाईसी अपडेट करें।", 1),
        ("hindi_devanagari_upi", "आपके खाते में ₹5,000 कैशबैक आया है, प्राप्त करने के लिए यूपीआई पिन दर्ज करें।", 1),
        ("hindi_devanagari_legit", "नमस्ते, क्या आप कल दोपहर के भोजन के लिए उपलब्ध हैं?", 0),
        ("english_regional_upi", "Dear customer, Rs 4999 UPI collect request pending. Enter UPI PIN to cancel refund.", 1),
        ("english_regional_aadhaar", "UIDAI Notice: Your Aadhaar PAN link is suspended. Verify immediately to avoid penalty.", 1),
        ("english_legit_bank", "Your monthly bank statement for October is ready to view in the official mobile app.", 0),
    ]
    probe_texts = [text_preprocessor.preprocess(p[1], mask_personal_data=True)["cleaned_text"] for p in probes]
    v1_p = m1_v1.predict(v1_vec.transform(probe_texts))
    v2_p = u_clf.predict(u_vec.transform(probe_texts))
    tx_p = tx_clf.predict(st_model.encode(probe_texts, normalize_embeddings=True, show_progress_bar=False))

    for i, (pid, raw, expected) in enumerate(probes):
        report["linguistic_stress_test"].append({
            "probe_id": pid,
            "expected_threat": expected,
            "v1.0_pred_threat": int(v1_p[i]),
            "v2.1_pred_threat": int(v2_p[i] != 0),
            "v2.1_pred_class": int(v2_p[i]),
            "minilm_pred_threat": int(tx_p[i] != 0),
        })

    out_path = Path("ml/artifacts/text_detection/multilingual_audit_and_comparison.json")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved full multilingual evaluation & transformer comparison to {out_path}")


if __name__ == "__main__":
    main()
