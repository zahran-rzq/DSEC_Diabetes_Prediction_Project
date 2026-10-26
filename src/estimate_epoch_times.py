#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 ESTIMASI DURATION EPOCH — untuk sumbu waktu (MENIT) pada plot pelatihan (ETS)
================================================================================
 Ketentuan ETS : plot performa model wajib memakai sumbu waktu dalam MENIT
 (bukan indeks titik data), light theme, dan tanpa efek jitter.

 Pendekatan (TANPA melatih ulang model produksi):
   1. Bangun ulang pipeline data yang identik dengan notebook Fase I
      (dataset + drop_duplicates + split 70:15:15 stratified, seed 42).
   2. Bangun ulang arsitektur Model A, B, C yang SAMA PERSIS dengan notebook.
   3. Ukur wall-clock 1 epoch (train + 1 validasi, batch 1024, verbose=0)
      pada tiap model — model pengukuran ini DISANGKA (tidak menggantikan
      artefak produksi di artifacts/).
   4. Simpan artifacts/epoch_timing.json, lalu regenerasi
      assets/figures/fig_training_history.png dengan sumbu x = menit
      kumulatif (i * detik_per_epoch / 60) dari riwayat training yang asli.

 Jalankan :  .venv/bin/python src/estimate_epoch_times.py
================================================================================
"""

from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "assets" / "figures"
ART_DIR = ROOT / "artifacts"

SEED = 42
np.random.seed(SEED)


# ----------------------------------------------------------------------------
# 1. Pipeline data — identik dengan notebook Fase I
# ----------------------------------------------------------------------------
def build_data() -> tuple[pd.DataFrame, pd.Series]:
    df_raw = pd.read_csv(ROOT / "diabetes_prediction_dataset.csv")
    df = df_raw.drop_duplicates().reset_index(drop=True).copy()
    X = df.drop(columns=["diabetes"])
    y = df["diabetes"].astype(int)
    return X, y


def build_split(X: pd.DataFrame, y: pd.Series):
    from sklearn.model_selection import train_test_split

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=SEED)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=SEED)
    return X_train, X_val, y_train, y_val


def build_preprocessor(X_train: pd.DataFrame):
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    NUM_FEATURES = ["age", "hypertension", "heart_disease", "bmi",
                    "HbA1c_level", "blood_glucose_level"]
    CAT_FEATURES = ["gender", "smoking_history"]
    pp = ColumnTransformer(transformers=[
        ("num", StandardScaler(), NUM_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
    ])
    pp.fit(X_train)
    return pp


# ----------------------------------------------------------------------------
# 2. Arsitektur — sama persis dengan notebook Fase I
# ----------------------------------------------------------------------------
def build_model_a(n: int, tf):
    inp = tf.keras.Input(shape=(n,), name="clinical_input")
    x = tf.keras.layers.Dense(64, activation="relu")(inp)
    x = tf.keras.layers.Dropout(0.30)(x)
    x = tf.keras.layers.Dense(32, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.20)(x)
    out = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    m = tf.keras.Model(inp, out, name="timing_model_a")
    m.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
              loss="binary_crossentropy", metrics=["accuracy"])
    return m


def build_model_b(n: int, tf):
    inp = tf.keras.Input(shape=(n,), name="clinical_input")
    x = tf.keras.layers.Dense(128, activation="relu")(inp)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.30)(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    x = tf.keras.layers.Dense(32, activation="relu")(x)
    out = tf.keras.layers.Dense(2, activation="softmax")(x)
    m = tf.keras.Model(inp, out, name="timing_model_b")
    m.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=5e-4),
              loss="categorical_crossentropy", metrics=["accuracy"])
    return m


def smotenc_train(X_train: pd.DataFrame, y_train: pd.Series):
    from imblearn.over_sampling import SMOTENC

    cat_idx = [X_train.columns.get_loc(c) for c in ("gender", "smoking_history")]
    sm = SMOTENC(categorical_features=cat_idx, random_state=SEED, k_neighbors=5)
    Xs, ys = sm.fit_resample(X_train, y_train)
    return Xs, ys


# ----------------------------------------------------------------------------
# 3. Timing 1 epoch per model
# ----------------------------------------------------------------------------
def time_one_epoch(model, Xtr, ytr, Xva, yva, tf) -> float:
    """Wall-clock satu epoch lengkap (train + 1 validasi), batch 1024."""
    t0 = time.perf_counter()
    model.fit(Xtr, ytr, validation_data=(Xva, yva),
              epochs=1, batch_size=1024, verbose=0)
    return time.perf_counter() - t0


def main() -> None:
    warnings.filterwarnings("ignore")
    import tensorflow as tf  # noqa: E402  (di-import setelah data, agar timing jelas)

    print("Memuat data & membangun split 70:15:15 (seed 42) …")
    X, y = build_data()
    X_train, X_val, y_train, y_val = build_split(X, y)
    pp = build_preprocessor(X_train)
    Xtr = pp.transform(X_train)
    Xva = pp.transform(X_val)
    ytr_b = tf.keras.utils.to_categorical(y_train.to_numpy(), 2)
    yva_b = tf.keras.utils.to_categorical(y_val.to_numpy(), 2)
    print(f"Train = {len(Xtr):,} | Val = {len(Xva):,} | fitur = {Xtr.shape[1]}")

    hist = json.loads((ART_DIR / "training_history.json").read_text())
    n_epochs = {k: len(v["loss"]) for k, v in hist.items()
                if isinstance(v, dict) and "loss" in v}

    timing: dict[str, dict] = {}

    print("\n[1/3] Mengukur durasi 1 epoch — Model A (Sigmoid) …")
    ma = build_model_a(Xtr.shape[1], tf)
    t_a = time_one_epoch(ma, Xtr, y_train.to_numpy(), Xva, y_val.to_numpy(), tf)
    del ma
    timing["model_a"] = {"seconds_per_epoch": round(t_a, 3)}

    print(f"[2/3] Mengukur durasi 1 epoch — Model B (Softmax) … (t≈{t_a:.1f} dtk)")
    mb = build_model_b(Xtr.shape[1], tf)
    t_b = time_one_epoch(mb, Xtr, ytr_b, Xva, yva_b, tf)
    del mb
    timing["model_b"] = {"seconds_per_epoch": round(t_b, 3)}

    print("[3/3] SMOTENC (train only) + mengukur durasi 1 epoch — Model C …")
    X_train_sm, y_train_sm = smotenc_train(X_train, y_train)
    Xtr_c = pp.transform(X_train_sm)
    ytr_c = tf.keras.utils.to_categorical(y_train_sm.to_numpy(), 2)
    print(f"      Train hasil SMOTENC = {len(Xtr_c):,} sampel")
    mc = build_model_b(Xtr_c.shape[1], tf)
    t_c = time_one_epoch(mc, Xtr_c, ytr_c, Xva, yva_b, tf)
    del mc
    timing["model_c"] = {"seconds_per_epoch": round(t_c, 3)}

    # ---- simpan hasil ----
    payload = {
        "method": ("Wall-clock 1 epoch (train+validasi, batch 1024, verbose=0) pada "
                   "arsitektur & ukuran data yang identik dengan training asli; "
                   "model produksi di artifacts/ TIDAK dilatih ulang."),
        "seed": SEED,
        "n_train": int(len(Xtr)),
        "n_val": int(len(Xva)),
        "n_train_smotenc": int(len(Xtr_c)),
        "n_epochs_original": n_epochs,
        "models": timing,
    }
    out = ART_DIR / "epoch_timing.json"
    out.write_text(json.dumps(payload, indent=2))
    print(f"\n✔ Simpan {out}")
    for k, v in timing.items():
        n = n_epochs[k]
        print(f"  {k}: {v['seconds_per_epoch']} dtk/epoch "
              f"→ total {n} epoch ≈ {n * v['seconds_per_epoch'] / 60:.1f} menit")

    # ---- regenerasi plot dengan sumbu waktu (menit) ----
    regenerate_figure(hist, payload)
    print(f"✔ Figur pelatihan (sumbu menit) : {FIG_DIR / 'fig_training_history.png'}")


def regenerate_figure(hist: dict, timing_payload: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    # LIGHT THEME (aturan ETS) — whitegrid, tanpa efek jitter apa pun
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["figure.dpi"] = 110

    names = {"model_a": "Model A (Sigmoid)",
             "model_b": "Model B (Softmax)",
             "model_c": "Model C (Softmax+SMOTENC)"}
    t = {k: timing_payload["models"][k]["seconds_per_epoch"] for k in names}

    fig, axes = plt.subplots(3, 2, figsize=(11.5, 10))
    for row, (key, name) in enumerate(names.items()):
        h = hist[key]
        n = len(h["loss"])
        x = [i * t[key] / 60.0 for i in range(1, n + 1)]   # menit kumulatif
        axl, axa = axes[row]
        axl.plot(x, h["loss"], lw=2, label="Train loss", color="#4C72B0")
        axl.plot(x, h["val_loss"], lw=2, label="Val loss", color="#DD8452")
        axl.set_title(f"{name} — Loss", fontweight="bold")
        axl.set_xlabel("Waktu pelatihan (menit)"); axl.set_ylabel("Loss")
        axl.legend()
        axa.plot(x, h["accuracy"], lw=2, label="Train accuracy", color="#4C9F70")
        axa.plot(x, h["val_accuracy"], lw=2, label="Val accuracy", color="#D64545")
        axa.set_title(f"{name} — Accuracy", fontweight="bold")
        axa.set_xlabel("Waktu pelatihan (menit)"); axa.set_ylabel("Accuracy")
        axa.legend()
        axa.set_ylim(0.5, 1.0)
    sns.despine()
    fig.suptitle("Kurva Pelatihan — Sumbu Waktu dalam Menit "
                 "(estimasi dari durasi 1 epoch terukur)", fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "fig_training_history.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
