#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uji mandiri backend inferensi (tanpa GUI).
Jalankan:  python src/test_backend.py
Membutuhkan artefak `model.keras` + `preprocessor.pkl` hasil Fase I.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app import DiabetesPredictor, NUMERIC_RANGES  # noqa: E402


def main() -> int:
    predictor = DiabetesPredictor()
    print(f"Model termuat : {predictor.best_model_name}")
    print(f"Output mode   : {predictor.output_mode} | ambang θ = {predictor.threshold:.2f}")
    print(f"Jumlah fitur  : {len(predictor.feature_names)}")
    assert len(predictor.feature_names) == 15, "Dimensi fitur one-hot tidak sesuai (harus 15)"

    # ---------- 1. Pasien sehat -> harus NEGATIF ----------
    ok, err, rec = DiabetesPredictor.validate_record({
        "gender": "Female", "hypertension": "0", "heart_disease": "0",
        "smoking_history": "never", "age": "27", "bmi": "21.5",
        "HbA1c_level": "5.0", "blood_glucose_level": "95",
    })
    assert ok, f"Validasi pasien sehat gagal: {err}"
    res = predictor.predict(rec)
    print(f"Pasien sehat   -> P={res['prob']:.4f} | positif={res['positive']}")
    assert not res["positive"], "Pasien sehat seharusnya diprediksi NEGATIF"
    assert res["confidence"] == 1.0 - res["prob"]

    # ---------- 2. Pasien berisiko tinggi -> harus POSITIF ----------
    ok, err, rec = DiabetesPredictor.validate_record({
        "gender": "Male", "hypertension": "1", "heart_disease": "0",
        "smoking_history": "current", "age": "58", "bmi": "32.4",
        "HbA1c_level": "7.8", "blood_glucose_level": "210",
    })
    assert ok, f"Validasi pasien berisiko gagal: {err}"
    res = predictor.predict(rec)
    print(f"Pasien risiko  -> P={res['prob']:.4f} | positif={res['positive']}")
    assert res["positive"], "Pasien berisiko tinggi seharusnya diprediksi POSITIF"
    assert res["confidence"] == res["prob"]
    assert any("HbA1c" in f for f in res["flags"]), "Flag klinis HbA1c tidak muncul"

    # ---------- 3. Validasi input ----------
    cases = [
        ({"gender": "Female", "hypertension": "0", "heart_disease": "0",
          "smoking_history": "never", "age": "", "bmi": "25",
          "HbA1c_level": "5.5", "blood_glucose_level": "110"}, "kosong"),
        ({"gender": "Female", "hypertension": "0", "heart_disease": "0",
          "smoking_history": "never", "age": "abc", "bmi": "25",
          "HbA1c_level": "5.5", "blood_glucose_level": "110"}, "bukan angka"),
        ({"gender": "Female", "hypertension": "0", "heart_disease": "0",
          "smoking_history": "never", "age": "250", "bmi": "25",
          "HbA1c_level": "5.5", "blood_glucose_level": "110"}, "di luar rentang"),
        ({"gender": "X", "hypertension": "0", "heart_disease": "0",
          "smoking_history": "never", "age": "30", "bmi": "25",
          "HbA1c_level": "5.5", "blood_glucose_level": "110"}, "kategori tak dikenal"),
    ]
    for raw, desc in cases:
        ok, err, _ = DiabetesPredictor.validate_record(raw)
        assert not ok, f"Kasus '{desc}' seharusnya ditolak"
        assert err, f"Pesan error kasus '{desc}' kosong"
        print(f"Validasi benar menolak kasus: {desc:<18} -> {err[:60]}...")

    # tanda koma desimal (locale) harus diterima
    ok, _, _ = DiabetesPredictor.validate_record({
        "gender": "Other", "hypertension": "1", "heart_disease": "1",
        "smoking_history": "No Info", "age": "45,5", "bmi": "28,1",
        "HbA1c_level": "6,2", "blood_glucose_level": "150",
    })
    assert ok, "Format koma desimal seharusnya diterima"
    print("Format koma desimal diterima ✔")

    print("\nSEMUA UJI BACKEND LULUS ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
