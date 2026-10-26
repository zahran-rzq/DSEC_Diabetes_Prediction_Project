# 🩺 Diabetes Prediction System — Custom Deep Neural Network

**Tugas Proyek + Jawaban ETS — Dasar Sistem Elektronika Cerdas (Semester Gasal 2026/2027)**
Departemen Teknik Elektro · FTEIC · Institut Teknologi Sepuluh Nopember

> ## 📝 Kepatuhan ETS (Soal 1) — terpenuhi
> | Ketentuan ETS | Status |
> |---|---|
> | Dataset Kaggle `iammustafatz/diabetes-prediction-dataset` | ✅ `diabetes_prediction_dataset.csv` |
> | Input manual 8 atribut + panel hasil | ✅ `src/app.py` (CustomTkinter, light theme) |
> | Teks prediksi **"Risiko Diabetes" / "Tidak Berisiko Diabetes"** | ✅ status label GUI + `--selftest` |
> | Light theme keseluruhan antarmuka | ✅ `set_appearance_mode("light")` + palet terang (termasuk fallback Tkinter) |
> | Plot: light theme | ✅ style `whitegrid` |
> | Plot: sumbu waktu = **menit** (bukan indeks) | ✅ `assets/figures/fig_training_history.png` + `artifacts/epoch_timing.json` (estimasi dari 1 epoch terukur, tanpa retrain) |
> | Plot: **tanpa jitter** | ✅ tidak ada stripplot/swarmplot |
> | Laporan jawaban .pdf lengkap + gambar UI | ✅ `laporan/Laporan_ETS_DSEC_Prediksi_Diabetes.pdf` (17 hal.) |
>
> Alat bantu ETS: `src/estimate_epoch_times.py` (estimasi durasi epoch),
> `src/make_ui_mockup.py` (mockup UI 3 keadaan), `laporan/build_ets_report.py`
> (generator PDF jawaban ETS — isi nama/NRP lewat `--nama`/`--nrp`).

Clinical Decision Support System untuk memprediksi risiko diabetes mellitus dari 8 fitur
rekam medis, berbasis **custom Multi-Layer Perceptron (TensorFlow/Keras)** dengan aplikasi
desktop **CustomTkinter** dan inferensi real-time.

## 📊 Ringkasan Hasil

| | Model A — Sigmoid (BCE) | **Model B — Softmax (CCE)** ✅ | Model C — Softmax + SMOTENC |
|---|---|---|---|
| Topologi | 15 → 64 → 32 → 1 (Dropout) | 15 → 128 → 64 → 32 → 2 (BN + Dropout) | = Model B, train di-oversampling |
| Accuracy (Test) | 0,9709 | **0,9724** | 0,9714 |
| Precision | 0,9410 | 0,9740 | **0,9778** |
| Recall | **0,7146** | 0,7060 | 0,6918 |
| F1-Score | 0,8123 | **0,8186** | 0,8103 |
| ROC-AUC | **0,9773** | 0,9772 | 0,9737 |
| Ambang θ (tuned di validasi) | 0,86 | **0,85** | 0,90 |

- Dataset Kaggle 100.000 rekam medis → cleaning (3.854 duplikat dibuang) → **96.146 sampel**.
- Split **70 : 15 : 15 stratified** — seluruh scaler/encoder **fit hanya pada data train**
  (tanpa data leakage).
- Class imbalance 91,5 % : 8,5 % → **class weighting balanced** + **decision threshold
  tuning** (F1-Score pada validasi); **SMOTENC diuji sebagai eksperimen pembanding**
  (hanya pada data train) dan terbukti sedikit kalah efektif → class weighting dipertahankan.
- Model terbaik (Model B, softmax) + pipeline diekspor ke `artifacts/` dan dipakai GUI.

## 🗂️ Struktur Repositori

```
├── diabetes_prediction_dataset.csv        # dataset Kaggle (100.000 baris)
├── Diabetes_Prediction_Project.pdf        # naskah tugas (sumber)
├── requirements.txt
├── src/
│   ├── diabetes_model_development.ipynb   # FASE I : EDA → split → preprocessing →
│   │                                      #         Model A vs B → evaluasi → ekspor
│   ├── app.py                             # FASE II+III : GUI desktop (LIGHT) + inferensi
│   ├── test_backend.py                    # uji mandiri backend (python src/test_backend.py)
│   ├── estimate_epoch_times.py            # ETS : estimasi durasi epoch → plot sumbu menit
│   ├── make_ui_mockup.py                  # ETS : mockup UI (3 keadaan) untuk laporan
│   └── make_submission_zip.py             # pembuat berkas .zip pengumpulan
├── artifacts/
│   ├── model.keras                        # Model B terlatih (produksi)
│   ├── preprocessor.pkl                   # StandardScaler+OneHotEncoder+ambang θ*
│   ├── training_history.json              # riwayat training & metrik
│   └── epoch_timing.json                  # ETS : durasi 1 epoch terukur (sumbu menit)
├── assets/figures/                        # figur EDA & evaluasi + mockup UI (light)
└── laporan/
    ├── Laporan_ETS_DSEC_Prediksi_Diabetes.pdf   # ★ JAWABAN ETS (17 hal.)
    ├── build_ets_report.py                # generator jawaban ETS (--nama/--nrp)
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

- **Light theme** di seluruh antarmuka (ketentuan ETS) — CustomTkinter maupun fallback Tkinter.
- Panel kiri **Patient Information**: 4 dropdown (Gender, Hypertension, Heart Disease,
  Smoking History) + 4 entry numerik (Age, BMI, HbA1c, Blood Glucose).
- Panel kanan **Diabetes Diagnosis**: status **merah** ("Risiko Diabetes") / **hijau**
  ("Tidak Berisiko Diabetes") sesuai ketentuan ETS, confidence score, probabilitas,
  faktor risiko klinis, tombol **Predict** dan **Reset**.
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
# 1) Isi identitas di laporan ETS, lalu bangun ulang PDF:
.venv/bin/python laporan/build_ets_report.py --nama "Nama Lengkap" --nrp 07xxxxxxxx

# 2) (Opsional) kemas seluruh proyek:
python src/make_submission_zip.py --nama "Nama Lengkap" --nrp 07xxxxxxxx
# menghasilkan: TugasProyek_EC_NamaLengkap_NRP.zip
```

> **ETS:** unggah `laporan/Laporan_ETS_DSEC_Prediksi_Diabetes.pdf` ke MyITS Classroom
> pada waktu pengumpulan; demo aplikasi (`python src/app.py`) akan dilaksanakan di kelas.
> Video demonstrasi (1–3 menit) direkam mandiri oleh mahasiswa sesuai ketentuan tugas.

## 📄 Laporan Teknis

`laporan/Laporan_Teknis_Prediksi_Diabetes.pdf` — metodologi preprocessing & pencegahan
leakage, arsitektur Sigmoid vs Softmax (teoretis & empiris), tabel metrik klinis, confusion
matrix, ROC/PR curve, dan *user guide* aplikasi.
