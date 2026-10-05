#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 DIABETES PREDICTION SYSTEM — Clinical Decision Support System (Desktop GUI)
================================================================================
 Elektronika Cerdas · Semester Gasal 2026/2027
 Departemen Teknik Elektro — FTEIC — Institut Teknologi Sepuluh Nopember
--------------------------------------------------------------------------------
 Fase II  : GUI Desktop (CustomTkinter, dengan fallback Tkinter murni)
 Fase III : Integrasi Sistem — memuat `model.keras` + `preprocessor.pkl`,
            validasi input, transformasi pipeline identik dengan training,
            dan inferensi real-time.

 Cara menjalankan :
     python app.py
     python app.py --artifacts <folder>      # opsional: lokasi artefak lain

 Kebutuhan : Python 3.9+, tensorflow, scikit-learn, pandas, numpy, joblib
             (GUI memakai CustomTkinter; bila tidak terpasang, otomatis
              menggunakan Tkinter bawaan Python).
================================================================================
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

# ----------------------------------------------------------------------------
# Konfigurasi form klinis — urutan kolom HARUS sama dengan saat training
# ----------------------------------------------------------------------------
NUMERIC_FIELDS = ["age", "bmi", "HbA1c_level", "blood_glucose_level"]
CATEGORICAL_FIELDS = ["gender", "hypertension", "heart_disease", "smoking_history"]
INPUT_COLUMNS = ["gender", "age", "hypertension", "heart_disease",
                 "smoking_history", "bmi", "HbA1c_level", "blood_glucose_level"]

GENDER_OPTIONS = ["Female", "Male", "Other"]
BINER_OPTIONS = ["0", "1"]
SMOKING_OPTIONS = ["never", "current", "former", "ever", "not current", "No Info"]

# Batas validasi input yang wajar secara klinis (lebih longgar dari rentang dataset)
NUMERIC_RANGES = {
    "age":               (0.0, 120.0,  "Usia (tahun)"),
    "bmi":               (5.0, 100.0,  "BMI (kg/m²)"),
    "HbA1c_level":       (2.0, 16.0,   "HbA1c (%)"),
    "blood_glucose_level": (40.0, 600.0, "Glukosa Darah (mg/dL)"),
}

# Warna tema
COLOR_OK      = "#2E9E5B"   # hijau  -> NEGATIF
COLOR_DANGER  = "#D64545"   # merah  -> POSITIF
COLOR_NEUTRAL = "#8A94A6"


# ============================================================================
# BACKEND — logika inferensi (framework-agnostic, dipakai semua varian GUI)
# ============================================================================
class DiabetesPredictor:
    """Memuat model + pipeline, memvalidasi input, dan menjalankan inferensi."""

    def __init__(self, artifacts_dir: str | Path | None = None):
        self.artifacts_dir = Path(artifacts_dir) if artifacts_dir else self._locate_artifacts()
        self.model = tf.keras.models.load_model(self.artifacts_dir / "model.keras")
        bundle = joblib.load(self.artifacts_dir / "preprocessor.pkl")

        self.preprocessor = bundle["preprocessor"]
        self.feature_names = list(bundle["feature_names"])
        self.threshold = float(bundle.get("optimal_threshold", 0.5))
        self.default_threshold = float(bundle.get("default_threshold", 0.5))
        self.output_mode = bundle.get("output_mode", "sigmoid")
        self.best_model_name = bundle.get("best_model_name", "Custom MLP")

    @staticmethod
    def _locate_artifacts() -> Path:
        """Cari folder `artifacts` di beberapa lokasi umum (robust)."""
        here = Path(__file__).resolve().parent
        candidates = [
            here.parent / "artifacts",   # struktur repo   : src/app.py -> ../artifacts
            here / "artifacts",          # flat            : app.py + artifacts/
            Path.cwd() / "artifacts",    # cwd pengguna
        ]
        for c in candidates:
            if (c / "model.keras").exists() and (c / "preprocessor.pkl").exists():
                return c
        raise FileNotFoundError(
            "Artefak model tidak ditemukan!\n\n"
            "Pastikan file `model.keras` dan `preprocessor.pkl` berada di folder "
            "`artifacts/` (jalankan notebook Fase I terlebih dahulu atau gunakan "
            "artefak yang disertakan dalam pengumpulan)."
        )

    # ------------------------------------------------------------------ #
    @staticmethod
    def validate_record(raw: dict) -> tuple[bool, str, dict | None]:
        """Validasi 8 input form. Return (ok, pesan_error, record_tervalidasi)."""
        record: dict = {}

        # --- field kategorik ---
        if raw.get("gender") not in GENDER_OPTIONS:
            return False, f"Pilih Gender yang valid: {', '.join(GENDER_OPTIONS)}", None
        record["gender"] = raw["gender"]

        for f in ("hypertension", "heart_disease"):
            if raw.get(f) not in BINER_OPTIONS:
                return False, f"Pilih nilai {f} yang valid: 0 (Tidak) atau 1 (Ya).", None
            record[f] = int(raw[f])

        if raw.get("smoking_history") not in SMOKING_OPTIONS:
            return False, "Pilih Smoking History yang valid.", None
        record["smoking_history"] = raw["smoking_history"]

        # --- field numerik ---
        for f, (lo, hi, label) in NUMERIC_RANGES.items():
            text = (raw.get(f) or "").strip().replace(",", ".")
            if not text:
                return False, f"{label} belum diisi.", None
            try:
                value = float(text)
            except ValueError:
                return False, f"{label} harus berupa angka (didapat: '{raw[f]}').", None
            if not (lo <= value <= hi):
                return False, (
                    f"{label} = {value:g} berada di luar rentang wajar "
                    f"({lo:g} – {hi:g}). Mohon periksa kembali."
                ), None
            record[f] = value

        return True, "", record

    # ------------------------------------------------------------------ #
    def predict(self, record: dict) -> dict:
        """Transformasi input dengan pipeline training -> inferensi model."""
        df = pd.DataFrame([record])[INPUT_COLUMNS]          # urutan kolom = training
        X = self.preprocessor.transform(df)                 # scaler+encoder identik
        raw = np.asarray(self.model.predict(X, verbose=0))
        prob = float(raw.ravel()[0]) if self.output_mode == "sigmoid" else float(raw[0][1])

        positive = bool(prob >= self.threshold)
        confidence = prob if positive else 1.0 - prob
        return {
            "prob": prob,
            "positive": positive,
            "confidence": confidence,
            "threshold": self.threshold,
            "flags": self._clinical_flags(record),
        }

    @staticmethod
    def _clinical_flags(record: dict) -> list[str]:
        """Catatan faktor risiko klinis sederhana (pelengkap CDSS)."""
        flags = []
        if record["HbA1c_level"] >= 6.5:
            flags.append(f"HbA1c {record['HbA1c_level']:g}% ≥ 6.5% (ambang diagnostik diabetes, ADA).")
        if record["blood_glucose_level"] >= 200:
            flags.append(f"Glukosa darah {record['blood_glucose_level']:g} mg/dL ≥ 200 mg/dL (hiperglikemia).")
        if record["bmi"] >= 30:
            flags.append(f"BMI {record['bmi']:g} kg/m² ≥ 30 (obesitas).")
        if record["hypertension"] == 1:
            flags.append("Riwayat hipertensi.")
        if record["heart_disease"] == 1:
            flags.append("Riwayat penyakit jantung.")
        return flags


# ============================================================================
# TAMPILAN — varian GUI (CustomTkinter modern / Tkinter fallback)
# ============================================================================
def _msg_error(parent, title: str, message: str) -> None:
    """Popup error — import messagebox secara lazy agar backend bebas tkinter."""
    from tkinter import messagebox
    messagebox.showerror(title, message, parent=parent)


class _AppLogicMixin:
    """Logika bersama: baca form -> validasi -> prediksi -> tampilkan hasil."""

    predictor: DiabetesPredictor

    def _do_predict(self) -> None:
        ok, err, record = DiabetesPredictor.validate_record(self._read_form())
        if not ok:
            _msg_error(self, "Input Tidak Valid", err)
            return
        try:
            result = self.predictor.predict(record)
        except Exception as exc:  # pragma: no cover
            _msg_error(self, "Kesalahan Inferensi", str(exc))
            return
        self._show_result(result)

    def _do_reset(self) -> None:
        self._reset_form()
        self._clear_result()


# ----------------------------- CustomTkinter ------------------------------ #
def build_ctk_app(predictor: DiabetesPredictor):
    import customtkinter as ctk
    import tkinter as tk  # noqa: F401 — dibutuhkan CTk (StringVar, dsb.)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    class DiabetesAppCTk(ctk.CTk, _AppLogicMixin):
        FONT = "Segoe UI"

        def __init__(self, predictor: DiabetesPredictor):
            super().__init__(fg_color="#101623")
            self.predictor = predictor
            self.title("Diabetes Prediction System — Sistem Prediksi Diabetes")
            self.geometry("1060x680")
            self.minsize(980, 620)

            # ---------- Header ----------
            header = ctk.CTkFrame(self, fg_color="#1B2A4A", corner_radius=0)
            header.pack(fill="x")
            ctk.CTkLabel(
                header, text="🩺  DIABETES PREDICTION SYSTEM",
                font=ctk.CTkFont(self.FONT, 24, "bold"), text_color="white",
            ).pack(anchor="w", padx=24, pady=(14, 0))
            ctk.CTkLabel(
                header,
                text="Clinical Decision Support System · Custom Deep Neural Network · "
                     "Elektronika Cerdas FTEIC ITS",
                font=ctk.CTkFont(self.FONT, 12), text_color="#9FB3D9",
            ).pack(anchor="w", padx=24, pady=(0, 12))

            # ---------- Konten dua panel ----------
            content = ctk.CTkFrame(self, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=18, pady=14)
            content.grid_columnconfigure(0, weight=5, uniform="col")
            content.grid_columnconfigure(1, weight=4, uniform="col")

            self._build_left_panel(content)
            self._build_right_panel(content)

            # ---------- Status bar ----------
            status = (f"Model termuat: {predictor.best_model_name}   |   "
                      f"Ambang keputusan θ = {predictor.threshold:.2f}   |   "
                      f"Engine: TensorFlow {tf.__version__}   |   "
                      f"Artefak: {predictor.artifacts_dir.name}/")
            ctk.CTkLabel(self, text=status, font=ctk.CTkFont(self.FONT, 11),
                         text_color="#7C8AA5", anchor="w").pack(fill="x", padx=24, pady=(0, 8))

            self._reset_form()
            self._clear_result()

        # ---------------- Panel kiri: Patient Information ---------------- #
        def _build_left_panel(self, parent):
            panel = ctk.CTkFrame(parent, fg_color="#182338", corner_radius=14)
            panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

            ctk.CTkLabel(panel, text="👤  Patient Information",
                         font=ctk.CTkFont(self.FONT, 18, "bold"),
                         text_color="white").grid(row=0, column=0, columnspan=2,
                                                  sticky="w", padx=22, pady=(18, 6))
            ctk.CTkLabel(panel, text="Lengkapi 8 data klinis pasien, lalu tekan Predict.",
                         font=ctk.CTkFont(self.FONT, 12), text_color="#9FB3D9"
                         ).grid(row=1, column=0, columnspan=2, sticky="w", padx=22, pady=(0, 10))

            self.opts: dict[str, ctk.CTkOptionMenu] = {}
            self.entries: dict[str, ctk.CTkEntry] = {}

            def add_combo(r, label, values):
                ctk.CTkLabel(panel, text=label, font=ctk.CTkFont(self.FONT, 13),
                             anchor="w").grid(row=r, column=0, sticky="ew", padx=(22, 8), pady=6)
                w = ctk.CTkOptionMenu(panel, values=values, width=210, height=32,
                                      font=ctk.CTkFont(self.FONT, 13))
                w.grid(row=r, column=1, sticky="ew", padx=(0, 22), pady=6)
                return w

            def add_entry(r, label, placeholder):
                ctk.CTkLabel(panel, text=label, font=ctk.CTkFont(self.FONT, 13),
                             anchor="w").grid(row=r, column=0, sticky="ew", padx=(22, 8), pady=6)
                w = ctk.CTkEntry(panel, width=210, height=32,
                                 font=ctk.CTkFont(self.FONT, 13), placeholder_text=placeholder)
                w.grid(row=r, column=1, sticky="ew", padx=(0, 22), pady=6)
                return w

            r = 2
            self.opts["gender"] = add_combo(r, "Gender", GENDER_OPTIONS); r += 1
            self.opts["hypertension"] = add_combo(r, "Hypertension", BINER_OPTIONS); r += 1
            self.opts["heart_disease"] = add_combo(r, "Heart Disease", BINER_OPTIONS); r += 1
            self.opts["smoking_history"] = add_combo(r, "Smoking History", SMOKING_OPTIONS); r += 1
            self.entries["age"] = add_entry(r, "Age (tahun)", "misal: 45"); r += 1
            self.entries["bmi"] = add_entry(r, "BMI (kg/m²)", "misal: 27.3"); r += 1
            self.entries["HbA1c_level"] = add_entry(r, "HbA1c Level (%)", "misal: 5.6"); r += 1
            self.entries["blood_glucose_level"] = add_entry(r, "Blood Glucose (mg/dL)",
                                                            "misal: 140"); r += 1

            panel.grid_rowconfigure(r, weight=1)

        # ---------------- Panel kanan: Diabetes Diagnosis ---------------- #
        def _build_right_panel(self, parent):
            panel = ctk.CTkFrame(parent, fg_color="#182338", corner_radius=14)
            panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
            panel.grid_rowconfigure(6, weight=1)

            ctk.CTkLabel(panel, text="📋  Diabetes Diagnosis",
                         font=ctk.CTkFont(self.FONT, 18, "bold"),
                         text_color="white").grid(row=0, column=0, sticky="w",
                                                  padx=22, pady=(18, 10))

            self.status_label = ctk.CTkLabel(
                panel, text="—", font=ctk.CTkFont(self.FONT, 26, "bold"),
                text_color="white", fg_color="#2A3550", corner_radius=14, height=86,
            )
            self.status_label.grid(row=1, column=0, sticky="ew", padx=22, pady=6)

            self.conf_label = ctk.CTkLabel(panel, text="Confidence: —",
                                           font=ctk.CTkFont(self.FONT, 16, "bold"),
                                           text_color="#E8EEF9")
            self.conf_label.grid(row=2, column=0, pady=(6, 0))
            self.prob_label = ctk.CTkLabel(panel, text="P(diabetes) = —",
                                           font=ctk.CTkFont(self.FONT, 13), text_color="#9FB3D9")
            self.prob_label.grid(row=3, column=0)
            self.flags_label = ctk.CTkLabel(panel, text="", font=ctk.CTkFont(self.FONT, 12),
                                            text_color="#F0C75E", justify="left", wraplength=400)
            self.flags_label.grid(row=4, column=0, pady=(8, 0))

            buttons = ctk.CTkFrame(panel, fg_color="transparent")
            buttons.grid(row=5, column=0, pady=16)
            ctk.CTkButton(buttons, text="🔍  Predict", width=170, height=44,
                          font=ctk.CTkFont(self.FONT, 16, "bold"),
                          fg_color="#2F6FED", hover_color="#1F55C4",
                          command=self._do_predict).grid(row=0, column=0, padx=8)
            ctk.CTkButton(buttons, text="↺  Reset", width=120, height=44,
                          font=ctk.CTkFont(self.FONT, 15),
                          fg_color="#3A4763", hover_color="#2B3550",
                          command=self._do_reset).grid(row=0, column=1, padx=8)

            self.note_label = ctk.CTkLabel(
                panel,
                text="Aplikasi ini adalah alat bantu edukasi & pendukung keputusan.\n"
                     "Diagnosis definitif tetap harus dilakukan oleh tenaga medis.",
                font=ctk.CTkFont(self.FONT, 11), text_color="#7C8AA5", justify="center",
            )
            self.note_label.grid(row=7, column=0, pady=(0, 14))

        # ---------------- aksi form ---------------- #
        def _read_form(self) -> dict:
            return {
                "gender": self.opts["gender"].get(),
                "hypertension": self.opts["hypertension"].get(),
                "heart_disease": self.opts["heart_disease"].get(),
                "smoking_history": self.opts["smoking_history"].get(),
                "age": self.entries["age"].get(),
                "bmi": self.entries["bmi"].get(),
                "HbA1c_level": self.entries["HbA1c_level"].get(),
                "blood_glucose_level": self.entries["blood_glucose_level"].get(),
            }

        def _reset_form(self) -> None:
            self.opts["gender"].set("Female")
            self.opts["hypertension"].set("0")
            self.opts["heart_disease"].set("0")
            self.opts["smoking_history"].set("never")
            defaults = {"age": "30", "bmi": "25.0", "HbA1c_level": "5.5",
                        "blood_glucose_level": "110"}
            for k, w in self.entries.items():
                w.delete(0, "end")
                w.insert(0, defaults[k])

        def _show_result(self, result: dict) -> None:
            if result["positive"]:
                self.status_label.configure(text="✚  POSITIVE — DIABETIC",
                                            fg_color=COLOR_DANGER)
                conf_txt = f"Confidence: {result['confidence'] * 100:.1f}%  (P = {result['prob']:.3f})"
            else:
                self.status_label.configure(text="✔  NEGATIVE — NON-DIABETIC",
                                            fg_color=COLOR_OK)
                conf_txt = f"Confidence: {result['confidence'] * 100:.1f}%  (P = {result['prob']:.3f})"
            self.conf_label.configure(text=conf_txt)
            self.prob_label.configure(
                text=f"P(diabetes) = {result['prob']:.4f}   |   ambang θ = {result['threshold']:.2f}"
                     f"   →   kelas = {'Positif' if result['positive'] else 'Negatif'}")
            self.flags_label.configure(
                text=("⚠ Faktor risiko terdeteksi:\n• " + "\n• ".join(result["flags"]))
                if result["flags"] else "")

        def _clear_result(self) -> None:
            self.status_label.configure(text="Menunggu prediksi…", fg_color="#2A3550")
            self.conf_label.configure(text="Confidence: —")
            self.prob_label.configure(text="P(diabetes) = —")
            self.flags_label.configure(text="")

    return DiabetesAppCTk(predictor)


# ------------------------------- Tkinter ---------------------------------- #
def build_tk_app(predictor: DiabetesPredictor):
    """Fallback tanpa dependensi tambahan: Tkinter + ttk bergaya flat."""
    import tkinter as tk
    from tkinter import ttk

    BG, PANEL, FG, ACCENT = "#101623", "#182338", "#E8EEF9", "#2F6FED"

    class DiabetesAppTk(tk.Tk, _AppLogicMixin):
        def __init__(self, predictor: DiabetesPredictor):
            super().__init__(bg=BG)
            self.predictor = predictor
            self.title("Diabetes Prediction System — Sistem Prediksi Diabetes")
            self.geometry("1040x660")
            self.minsize(960, 600)

            st = ttk.Style(self)
            try:
                st.theme_use("clam")
            except tk.TclError:
                pass
            st.configure("Flat.TCombobox", fieldbackground=PANEL, background=PANEL,
                         foreground=FG, arrowcolor=FG, bordercolor=PANEL,
                         lightcolor=PANEL, darkcolor=PANEL, font=("Segoe UI", 10))
            st.map("Flat.TCombobox",
                   fieldbackground=[("readonly", PANEL)],
                   foreground=[("readonly", FG)])

            # Header
            header = tk.Frame(self, bg="#1B2A4A")
            header.pack(fill="x")
            tk.Label(header, text="🩺  DIABETES PREDICTION SYSTEM", bg="#1B2A4A", fg="white",
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=24, pady=(12, 0))
            tk.Label(header, text="Clinical Decision Support System · Custom Deep Neural "
                                  "Network · Elektronika Cerdas FTEIC ITS",
                     bg="#1B2A4A", fg="#9FB3D9",
                     font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(0, 10))

            content = tk.Frame(self, bg=BG)
            content.pack(fill="both", expand=True, padx=18, pady=14)
            content.grid_columnconfigure(0, weight=5, uniform="col")
            content.grid_columnconfigure(1, weight=4, uniform="col")
            content.grid_rowconfigure(0, weight=1)

            self._build_left(content)
            self._build_right(content)

            status = (f"Model termuat: {predictor.best_model_name}   |   "
                      f"Ambang θ = {predictor.threshold:.2f}   |   "
                      f"TensorFlow {tf.__version__}")
            tk.Label(self, text=status, bg=BG, fg="#7C8AA5", anchor="w",
                     font=("Segoe UI", 9)).pack(fill="x", padx=24, pady=(0, 6))

            self._reset_form()
            self._clear_result()

        def _build_left(self, parent):
            panel = tk.Frame(parent, bg=PANEL, highlightbackground="#2A3550",
                             highlightthickness=1)
            panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
            tk.Label(panel, text="👤  Patient Information", bg=PANEL, fg="white",
                     font=("Segoe UI", 15, "bold")).grid(row=0, column=0, columnspan=2,
                                                         sticky="w", padx=22, pady=(16, 4))
            tk.Label(panel, text="Lengkapi 8 data klinis pasien, lalu tekan Predict.",
                     bg=PANEL, fg="#9FB3D9", font=("Segoe UI", 10)).grid(
                row=1, column=0, columnspan=2, sticky="w", padx=22, pady=(0, 8))

            self.opts: dict[str, ttk.Combobox] = {}
            self.entries: dict[str, tk.Entry] = {}

            def add_combo(r, label, values):
                tk.Label(panel, text=label, bg=PANEL, fg=FG, anchor="w",
                         font=("Segoe UI", 11)).grid(row=r, column=0, sticky="ew",
                                                     padx=(22, 8), pady=5)
                w = ttk.Combobox(panel, values=values, state="readonly", width=24,
                                 style="Flat.TCombobox")
                w.grid(row=r, column=1, sticky="ew", padx=(0, 22), pady=5)
                return w

            def add_entry(r, label):
                tk.Label(panel, text=label, bg=PANEL, fg=FG, anchor="w",
                         font=("Segoe UI", 11)).grid(row=r, column=0, sticky="ew",
                                                     padx=(22, 8), pady=5)
                w = tk.Entry(panel, width=26, bg="#0F1728", fg=FG,
                             insertbackground=FG, relief="flat", font=("Segoe UI", 11),
                             highlightbackground="#2A3550", highlightthickness=1)
                w.grid(row=r, column=1, sticky="ew", padx=(0, 22), pady=5, ipady=4)
                return w

            r = 2
            self.opts["gender"] = add_combo(r, "Gender", GENDER_OPTIONS); r += 1
            self.opts["hypertension"] = add_combo(r, "Hypertension", BINER_OPTIONS); r += 1
            self.opts["heart_disease"] = add_combo(r, "Heart Disease", BINER_OPTIONS); r += 1
            self.opts["smoking_history"] = add_combo(r, "Smoking History", SMOKING_OPTIONS); r += 1
            self.entries["age"] = add_entry(r, "Age (tahun)"); r += 1
            self.entries["bmi"] = add_entry(r, "BMI (kg/m²)"); r += 1
            self.entries["HbA1c_level"] = add_entry(r, "HbA1c Level (%)"); r += 1
            self.entries["blood_glucose_level"] = add_entry(r, "Blood Glucose (mg/dL)"); r += 1
            panel.grid_rowconfigure(r, weight=1)

        def _build_right(self, parent):
            panel = tk.Frame(parent, bg=PANEL, highlightbackground="#2A3550",
                             highlightthickness=1)
            panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
            panel.grid_rowconfigure(6, weight=1)

            tk.Label(panel, text="📋  Diabetes Diagnosis", bg=PANEL, fg="white",
                     font=("Segoe UI", 15, "bold")).grid(row=0, column=0, sticky="w",
                                                          padx=22, pady=(16, 8))

            self.status_label = tk.Label(panel, text="—", bg="#2A3550", fg="white",
                                         font=("Segoe UI", 20, "bold"), pady=26)
            self.status_label.grid(row=1, column=0, sticky="ew", padx=22, pady=6)

            self.conf_label = tk.Label(panel, text="Confidence: —", bg=PANEL, fg=FG,
                                       font=("Segoe UI", 13, "bold"))
            self.conf_label.grid(row=2, column=0, pady=(6, 0))
            self.prob_label = tk.Label(panel, text="P(diabetes) = —", bg=PANEL,
                                       fg="#9FB3D9", font=("Segoe UI", 10))
            self.prob_label.grid(row=3, column=0)
            self.flags_label = tk.Label(panel, text="", bg=PANEL, fg="#F0C75E",
                                        justify="left", font=("Segoe UI", 10))
            self.flags_label.grid(row=4, column=0, pady=(8, 0))

            buttons = tk.Frame(panel, bg=PANEL)
            buttons.grid(row=5, column=0, pady=14)
            tk.Button(buttons, text="🔍 Predict", width=16, font=("Segoe UI", 13, "bold"),
                      bg=ACCENT, fg="white", activebackground="#1F55C4", activeforeground="white",
                      relief="flat", cursor="hand2", pady=8,
                      command=self._do_predict).grid(row=0, column=0, padx=8)
            tk.Button(buttons, text="↺ Reset", width=10, font=("Segoe UI", 12),
                      bg="#3A4763", fg="white", activebackground="#2B3550",
                      activeforeground="white", relief="flat", cursor="hand2", pady=8,
                      command=self._do_reset).grid(row=0, column=1, padx=8)

            tk.Label(panel, text="Aplikasi ini adalah alat bantu edukasi & pendukung keputusan.\n"
                                 "Diagnosis definitif tetap harus dilakukan oleh tenaga medis.",
                     bg=PANEL, fg="#7C8AA5", justify="center",
                     font=("Segoe UI", 9)).grid(row=7, column=0, pady=(0, 12))

        def _read_form(self) -> dict:
            return {
                "gender": self.opts["gender"].get(),
                "hypertension": self.opts["hypertension"].get(),
                "heart_disease": self.opts["heart_disease"].get(),
                "smoking_history": self.opts["smoking_history"].get(),
                "age": self.entries["age"].get(),
                "bmi": self.entries["bmi"].get(),
                "HbA1c_level": self.entries["HbA1c_level"].get(),
                "blood_glucose_level": self.entries["blood_glucose_level"].get(),
            }

        def _reset_form(self) -> None:
            defaults_combo = {"gender": "Female", "hypertension": "0",
                              "heart_disease": "0", "smoking_history": "never"}
            for k, w in self.opts.items():
                w.set(defaults_combo[k])
            defaults = {"age": "30", "bmi": "25.0", "HbA1c_level": "5.5",
                        "blood_glucose_level": "110"}
            for k, w in self.entries.items():
                w.delete(0, "end")
                w.insert(0, defaults[k])

        def _show_result(self, result: dict) -> None:
            if result["positive"]:
                self.status_label.configure(text="✚  POSITIVE — DIABETIC", bg=COLOR_DANGER)
            else:
                self.status_label.configure(text="✔  NEGATIVE — NON-DIABETIC", bg=COLOR_OK)
            self.conf_label.configure(
                text=f"Confidence: {result['confidence'] * 100:.1f}%  (P = {result['prob']:.3f})")
            self.prob_label.configure(
                text=f"P(diabetes) = {result['prob']:.4f}   |   ambang θ = {result['threshold']:.2f}"
                     f"   →   kelas = {'Positif' if result['positive'] else 'Negatif'}")
            self.flags_label.configure(
                text=("⚠ Faktor risiko terdeteksi:\n• " + "\n• ".join(result["flags"]))
                if result["flags"] else "")

        def _clear_result(self) -> None:
            self.status_label.configure(text="Menunggu prediksi…", bg="#2A3550")
            self.conf_label.configure(text="Confidence: —")
            self.prob_label.configure(text="P(diabetes) = —")
            self.flags_label.configure(text="")

    return DiabetesAppTk(predictor)


# ============================================================================
# Entry point
# ============================================================================
def main() -> int:
    parser = argparse.ArgumentParser(description="Diabetes Prediction System (Desktop GUI)")
    parser.add_argument("--artifacts", default=None,
                        help="Folder berisi model.keras & preprocessor.pkl (opsional)")
    parser.add_argument("--selftest", action="store_true",
                        help="Uji backend tanpa membuka GUI (untuk verifikasi cepat)")
    args = parser.parse_args()

    print("Memuat model & preprocessor …")
    predictor = DiabetesPredictor(args.artifacts)
    print(f"✔ Model        : {predictor.best_model_name}")
    print(f"✔ Output layer : {predictor.output_mode} | ambang θ = {predictor.threshold:.2f}")
    print(f"✔ Artefak      : {predictor.artifacts_dir}")

    if args.selftest:
        demo = {
            "Pasien sehat": dict(gender="Female", age=27.0, hypertension=0, heart_disease=0,
                                 smoking_history="never", bmi=21.5, HbA1c_level=5.0,
                                 blood_glucose_level=95.0),
            "Pasien berisiko": dict(gender="Male", age=58.0, hypertension=1, heart_disease=0,
                                    smoking_history="current", bmi=32.4, HbA1c_level=7.8,
                                    blood_glucose_level=210.0),
        }
        for name, rec in demo.items():
            res = predictor.predict(rec)
            status = "POSITIF Diabetes" if res["positive"] else "NEGATIF (Non-Diabetic)"
            print(f"  [{name}] P={res['prob']:.4f} → {status}")
        print("SELFTEST OK")
        return 0

    # GUI: coba CustomTkinter (modern), fallback ke Tkinter bawaan
    try:
        import customtkinter  # noqa: F401
        app = build_ctk_app(predictor)
        print("GUI: CustomTkinter")
    except ImportError:
        app = build_tk_app(predictor)
        print("GUI: Tkinter (fallback — pip install customtkinter untuk tampilan modern)")

    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
