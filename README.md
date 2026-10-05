# 🩺 Diabetes Prediction System — Custom Deep Neural Network

**Tugas Proyek — Elektronika Cerdas (Semester Gasal 2026/2027)**
Departemen Teknik Elektro · FTEIC · Institut Teknologi Sepuluh Nopember

Clinical Decision Support System untuk memprediksi risiko diabetes mellitus dari 8 fitur
rekam medis, berbasis **custom Multi-Layer Perceptron (TensorFlow/Keras)** dengan aplikasi
desktop **CustomTkinter** dan inferensi real-time.

## 📊 Ringkasan Hasil

| | Model A — Sigmoid (BCE) | **Model B — Softmax (CCE)** ✅ |
|---|---|---|
| Topologi | 15 → 64 → 32 → 1 (Dropout) | 15 → 128 → 64 → 32 → 2 (BN + Dropout) |
| Accuracy (Test) | 0,9709 | **0,9724** |
| Precision | 0,9410 | **0,9740** |
| Recall | **0,7146** | 0,7060 |
| F1-Score | 0,8123 | **0,8186** |
| ROC-AUC | **0,9773** | 0,9772 |
| Ambang θ (tuned di validasi) | 0,86 | **0,85** |

- Dataset Kaggle 100.000 rekam medis → cleaning (3.854 duplikat dibuang) → **96.146 sampel**.
- Split **70 : 15 : 15 stratified** — seluruh scaler/encoder **fit hanya pada data train**
  (tanpa data leakage).
- Class imbalance 91,5 % : 8,5 % → **class weighting balanced** + **decision threshold
  tuning** (F1-Score pada validasi).
- Model terbaik (Model B, softmax) + pipeline diekspor ke `artifacts/` dan dipakai GUI.

## 🗂️ Struktur Repositori

```
├── diabetes_prediction_dataset.csv        # dataset Kaggle (100.000 baris)
├── Diabetes_Prediction_Project.pdf        # naskah tugas (sumber)
├── requirements.txt
├── src/
│   ├── diabetes_model_development.ipynb   # FASE I : EDA → split → preprocessing →
│   │                                      #         Model A vs B → evaluasi → ekspor
│   ├── app.py                             # FASE II+III : GUI desktop + integrasi inferensi
│   ├── test_backend.py                    # uji mandiri backend (python src/test_backend.py)
│   └── make_submission_zip.py             # pembuat berkas .zip pengumpulan
├── artifacts/
│   ├── model.keras                        # Model B terlatih (produksi)
│   ├── preprocessor.pkl                   # StandardScaler+OneHotEncoder+ambang θ*
│   └── training_history.json              # riwayat training & metrik
├── assets/figures/                        # figur EDA & evaluasi (ROC, PR, CM, dll.)
└── laporan/
    ├── Laporan_Teknis_Prediksi_Diabetes.pdf  # laporan teknis (16 hal.)
    └── build_report.py                    # generator laporan (opsional)
```

## ⚙️ Instalasi

```bash
# 1. Python 3.9+
python -m venv .venv && source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate                             # Windows

# 2. Dependensi
pip install -r requirements.txt
```

## 🖥️ Menjalankan Aplikasi Desktop (Fase III)

```bash
python src/app.py
```

- Panel kiri **Patient Information**: 4 dropdown (Gender, Hypertension, Heart Disease,
  Smoking History) + 4 entry numerik (Age, BMI, HbA1c, Blood Glucose).
- Panel kanan **Diabetes Diagnosis**: status **hijau** (NEGATIVE) / **merah** (POSITIVE),
  confidence score, probabilitas, faktor risiko klinis, tombol **Predict** dan **Reset**.
- Input kosong / tidak valid / di luar rentang klinis ditolak dengan dialog pop-up.
- Tanpa CustomTkinter, aplikasi otomatis memakai fallback Tkinter bawaan Python.
- Uji cepat tanpa GUI: `python src/app.py --selftest` dan `python src/test_backend.py`.

## 🔁 Melatih Ulang Model (Fase I)

```bash
jupyter notebook src/diabetes_model_development.ipynb   # jalankan semua sel
```

Notebook menulis ulang `artifacts/model.keras` dan `artifacts/preprocessor.pkl`, yang
langsung dibaca ulang oleh GUI.

## 📦 Pengumpulan (MyITS Classroom)

```bash
python src/make_submission_zip.py --nama "Nama Lengkap" --nrp 07xxxxxxxx
# menghasilkan: TugasProyek_EC_NamaLengkap_NRP.zip
```

> Video demonstrasi (1–3 menit) direkam mandiri oleh mahasiswa sesuai ketentuan tugas.

## 📄 Laporan Teknis

`laporan/Laporan_Teknis_Prediksi_Diabetes.pdf` — metodologi preprocessing & pencegahan
leakage, arsitektur Sigmoid vs Softmax (teoretis & empiris), tabel metrik klinis, confusion
matrix, ROC/PR curve, dan *user guide* aplikasi.
