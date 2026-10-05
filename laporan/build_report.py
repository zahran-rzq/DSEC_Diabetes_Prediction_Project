#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator Laporan Teknis Proyek — Prediksi Penyakit Diabetes (PDF).
Jalankan:  python laporan/build_report.py   (butuh: pip install fpdf2)
Output   : laporan/Laporan_Teknis_Prediksi_Diabetes.pdf
"""
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "assets" / "figures"
OUT = Path(__file__).resolve().parent / "Laporan_Teknis_Prediksi_Diabetes.pdf"
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

NAVY, ACCENT, GRAY = (27, 42, 74), (47, 111, 237), (90, 100, 120)


class Report(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("DejaVu", "", f"{FONT_DIR}/DejaVuSans.ttf")
        self.add_font("DejaVu", "B", f"{FONT_DIR}/DejaVuSans-Bold.ttf")
        self.add_font("DejaVu", "I", f"{FONT_DIR}/DejaVuSans.ttf")  # fallback italic
        self.add_font("Mono", "", f"{FONT_DIR}/DejaVuSansMono.ttf")
        self.add_font("Mono", "B", f"{FONT_DIR}/DejaVuSansMono-Bold.ttf")
        self._chapter_no = 0
        self._footer_on = False

    # ---------- layout ----------
    def header(self):
        if not self._footer_on or self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 7.5)
        self.set_text_color(*GRAY)
        self.cell(0, 5, "Laporan Proyek — Elektronika Cerdas (Gasal 2026/2027) · "
                        "Sistem Prediksi Diabetes Berbasis Custom DNN", align="L")
        self.cell(0, 5, "FTEIC ITS", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y() + 1, self.w - self.r_margin, self.get_y() + 1)
        self.ln(5)

    def footer(self):
        if not self._footer_on or self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Halaman {self.page_no()}", align="C")

    # ---------- blok konten ----------
    def chapter(self, title):
        self.add_page()
        self._chapter_no += 1
        self.set_font("DejaVu", "B", 15)
        self.set_text_color(*NAVY)
        self.cell(0, 10, f"BAB {self._chapter_no}   {title.upper()}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.l_margin + 60, self.get_y())
        self.ln(5)

    def h2(self, title):
        self.ln(2)
        if self.get_y() > self.h - 45:
            self.add_page()
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 6.5, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def h3(self, title):
        self.ln(1)
        self.set_font("DejaVu", "B", 10.5)
        self.set_text_color(*NAVY)
        self.multi_cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def para(self, text, size=10, gap=2.2):
        self.set_font("DejaVu", "", size)
        self.set_text_color(30, 32, 40)
        self.multi_cell(0, 5.4, text, align="J", new_x="LMARGIN", new_y="NEXT")
        self.ln(gap)

    def bullet(self, items, size=10):
        self.set_font("DejaVu", "", size)
        self.set_text_color(30, 32, 40)
        for it in items:
            x = self.get_x()
            self.cell(5, 5.4, "•")
            self.multi_cell(self.w - self.l_margin - self.r_margin - 5, 5.4, it,
                            align="L", new_x="LMARGIN", new_y="NEXT")
            self.set_x(x)
        self.ln(1.5)

    def numbered(self, items, size=10):
        self.set_font("DejaVu", "", size)
        self.set_text_color(30, 32, 40)
        for i, it in enumerate(items, 1):
            self.cell(6, 5.4, f"{i}.")
            self.multi_cell(self.w - self.l_margin - self.r_margin - 6, 5.4, it,
                            align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def table(self, header, rows, widths=None, fontsize=8.6, header_fill=NAVY):
        if widths is None:
            n = len(header)
            widths = [(self.w - self.l_margin - self.r_margin) / n] * n
        self.set_font("DejaVu", "B", fontsize)
        self.set_fill_color(*header_fill)
        self.set_text_color(255, 255, 255)
        h = 6.2
        # estimasi tinggi baris header multi-baris
        max_lines = 1
        for w_, cell in zip(widths, header):
            lines = self.multi_cell(w_ - 1.6, h, str(cell), dry_run=True, output="LINES")
            max_lines = max(max_lines, len(lines))
        hdr_h = max_lines * h
        if self.get_y() + hdr_h + 8 > self.h - 22:
            self.add_page()
        x0, y0 = self.get_x(), self.get_y()
        for w_, cell in zip(widths, header):
            self.set_xy(x0, y0)
            self.rect(x0, y0, w_, hdr_h, "F")
            self.set_xy(x0 + 0.8, y0 + 1)
            self.multi_cell(w_ - 1.6, h, str(cell), align="C")
            x0 += w_
        self.set_y(y0 + hdr_h)
        self.set_font("DejaVu", "", fontsize)
        for r_i, row in enumerate(rows):
            max_lines = 1
            for w_, cell in zip(widths, row):
                lines = self.multi_cell(w_ - 1.6, h, str(cell), dry_run=True, output="LINES")
                max_lines = max(max_lines, len(lines))
            row_h = max_lines * h
            if self.get_y() + row_h > self.h - 22:
                self.add_page()
                self.set_font("DejaVu", "", fontsize)
            x0 = self.get_x()
            y0 = self.get_y()
            fill = r_i % 2 == 1
            if fill:
                self.set_fill_color(238, 242, 250)
                self.rect(x0, y0, sum(widths), row_h, "F")
            self.set_text_color(30, 32, 40)
            for w_, cell in zip(widths, row):
                self.set_xy(x0 + 0.8, y0 + 1)
                self.multi_cell(w_ - 1.6, h, str(cell), align="C")
                x0 += w_
            self.set_y(y0 + row_h)
        self.set_draw_color(190, 198, 214)
        self.set_line_width(0.25)
        self.ln(3)

    def figure(self, name, caption, w=150):
        path = FIG / name
        if not path.exists():
            self.para(f"[figur tidak ditemukan: {name}]")
            return
        from PIL import Image  # noqa
        img = Image.open(path)
        ratio = img.height / img.width
        h = w * ratio
        if self.get_y() + h + 12 > self.h - 22:
            self.add_page()
        self.image(str(path), x=(self.w - w) / 2, y=self.get_y(), w=w)
        self.set_y(self.get_y() + h + 1.5)
        self.set_font("DejaVu", "I", 8.3)
        self.set_text_color(*GRAY)
        self.multi_cell(0, 4.4, caption, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def code(self, text, size=8.0):
        self.set_fill_color(244, 246, 250)
        self.set_draw_color(200, 208, 222)
        self.set_font("Mono", "", size)
        self.set_text_color(25, 30, 45)
        x, y = self.get_x(), self.get_y()
        lines = text.split("\n")
        h = 4.4
        block_h = len(lines) * h + 5
        if y + block_h > self.h - 22:
            self.add_page()
            x, y = self.get_x(), self.get_y()
        self.rect(x, y, self.w - self.l_margin - self.r_margin, block_h, "DF")
        self.set_xy(x + 3, y + 2.5)
        for line in lines:
            self.cell(0, h, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(x + 3)
        self.set_y(y + block_h + 3)


def build():
    pdf = Report()
    W = pdf.w - pdf.l_margin - pdf.r_margin

    # ================================================================ COVER
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, 62, "F")
    pdf.set_y(20)
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_text_color(159, 179, 217)
    pdf.cell(0, 7, "ELEKTRONIKA CERDAS  ·  SEMESTER GASAL 2026/2027", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 11, "LAPORAN TUGAS PROYEK", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 11, "PREDIKSI PENYAKIT DIABETES", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(78)
    pdf.set_font("DejaVu", "B", 15)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 8, "Clinical Decision Support System Berbasis\n"
                         "Custom Deep Neural Network dengan Aplikasi Desktop",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6.5, "Dataset: Kaggle — Diabetes Prediction Dataset (100.000 rekam medis)",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6.5, "Engine: TensorFlow (Keras)   ·   GUI: CustomTkinter / Tkinter",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(18)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.6)
    pdf.line(pdf.w / 2 - 40, pdf.get_y(), pdf.w / 2 + 40, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_text_color(30, 32, 40)
    pdf.cell(0, 7, "Nama        :  ...............................................................",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "NRP         :  ...............................................................",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6.5, "DEPARTEMEN TEKNIK ELEKTRO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6.5, "FAKULTAS TEKNIK ELEKTRO, INFORMATIKA, DAN INTELIJEN — FTEIC",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6.5, "INSTITUT TEKNOLOGI SEPULUH NOPEMBER", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6.5, "2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf._footer_on = True

    # ================================================================ RINGKASAN
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 9, "RINGKASAN EKSEKUTIF", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*ACCENT)
    pdf.line(pdf.l_margin, pdf.get_y() + 1, pdf.l_margin + 55, pdf.get_y() + 1)
    pdf.ln(5)
    pdf.para(
        "Proyek ini membangun sistem pendukung keputusan klinis (Clinical Decision Support "
        "System) untuk memprediksi risiko diabetes mellitus dari 8 fitur rekam medis pasien. "
        "Dataset Kaggle berisi 100.000 sampel dibersihkan (3.854 baris duplikat dibuang) lalu "
        "dibagi 70:15:15 secara stratified menjadi data Train / Validation / Test. Seluruh "
        "transformer preprocessing (StandardScaler + OneHotEncoder) di-fit hanya pada data "
        "train sehingga tidak terjadi kebocoran data (data leakage). Ketidakseimbangan kelas "
        "91,5 % : 8,5 % ditangani dengan pembobotan kelas balanced dan penyesuaian ambang "
        "keputusan (decision threshold tuning) berbasis F1-Score pada data validasi.")
    pdf.para(
        "Tiga percobaan custom Multi-Layer Perceptron dibandingkan: Model A (output sigmoid, "
        "binary_crossentropy, Dropout), Model B (output softmax 2-neuron, "
        "categorical_crossentropy, BatchNormalization + Dropout, lebih dalam dan lebih lebar, "
        "learning rate lebih kecil), serta Model C (arsitektur B yang sama, tetapi dilatih "
        "pada data train hasil oversampling SMOTENC) untuk menguji teknik mitigasi imbalance. "
        "Pada Test Set dengan ambang optimal, Model B (Softmax + class weighting) unggul "
        "dengan Accuracy 97,24 %, Precision 97,40 %, Recall 70,60 %, F1-Score 0,8186, dan "
        "ROC-AUC 0,9772 — mengalahkan Model C (F1 0,8103) sehingga class weighting dinyatakan "
        "lebih efektif daripada SMOTE pada kasus ini. Model B diekspor ke model.keras beserta "
        "preprocessor.pkl, lalu diintegrasikan ke aplikasi desktop \"Diabetes Prediction "
        "System\" (CustomTkinter) yang melakukan inferensi real-time dengan transformasi "
        "pipeline yang identik dengan proses training.")

    # ================================================================ BAB 1
    pdf.chapter("Pendahuluan")
    pdf.h2("1.1  Latar Belakang")
    pdf.para(
        "Diabetes mellitus adalah penyakit kronis dengan prevalensi yang terus meningkat dan "
        "berisiko fatal bila terdeteksi lambat. Sistem pendukung keputusan klinis berbasis "
        "machine learning dapat membantu tenaga medis melakukan skrining awal: dari 8 fitur "
        "rekam medis (gender, usia, hipertensi, penyakit jantung, riwayat merokok, BMI, kadar "
        "HbA1c, dan glukosa darah) model memperkirakan probabilitas pasien menderita "
        "diabetes. Proyek ini membangun sistem tersebut secara end-to-end — dari data mentah, "
        "pelatihan custom deep neural network, hingga aplikasi desktop dengan GUI.")
    pdf.h2("1.2  Tujuan")
    pdf.numbered([
        "Membangun pipeline preprocessing data klinis yang bebas kebocoran data (no data "
        "leakage) serta menangani class imbalance secara tepat.",
        "Merancang, melatih, dan membandingkan minimal dua arsitektur custom MLP yang "
        "bervariasi (kedalaman, lebar, regularisasi, learning rate).",
        "Mengimplementasikan dan mengkomparasi formulasi output layer Sigmoid vs Softmax "
        "beserta loss function yang sesuai, dengan justifikasi teoretis dan empiris.",
        "Mengevaluasi model dengan metrik klinis lengkap: Accuracy, Precision, Recall, "
        "F1-Score, Confusion Matrix, ROC dan PR Curve.",
        "Mengintegrasikan model terlatih + pipeline preprocessing ke aplikasi desktop "
        "(CustomTkinter) untuk inferensi real-time.",
    ])
    pdf.h2("1.3  Arsitektur Sistem End-to-End")
    pdf.para(
        "Alur kerja sistem mengikuti 8 tahap: (1) Dataset Kaggle 100k records → (2) "
        "Preprocessing: cleaning, encoding, StandardScaler tanpa leakage → (3) Pemodelan: "
        "Model A vs Model B, Sigmoid vs Softmax, regularisasi & tuning → (4) Evaluasi: "
        "Accuracy, Precision, Recall, F1, Confusion Matrix → (5) Serialisasi: model.keras + "
        "preprocessor.pkl → (6) GUI Desktop CustomTkinter → (7) Integrasi logika inferensi "
        "real-time dengan objek scaler/encoder → (8) Hasil prediksi klinis & tampilan "
        "diagnosis.")
    pdf.figure("fig_target_distribution.png",
               "Gambar 1.1  Distribusi kelas target: 91,5 % negatif vs 8,5 % positif — "
               "tantangan class imbalance (Accuracy Paradox).", w=105)

    # ================================================================ BAB 2
    pdf.chapter("Dataset & Preprocessing")
    pdf.h2("2.1  Deskripsi Dataset")
    pdf.para(
        "Dataset publik Kaggle \"Diabetes Prediction Dataset\" berisi 100.000 sampel rekam "
        "medis dengan 8 fitur prediktor dan 1 target biner. Rincian fitur:")
    pdf.table(
        ["Fitur", "Tipe", "Rentang / Kategori", "Perlakuan Preprocessing"],
        [
            ["gender", "Kategorik", "Female, Male, Other", "OneHotEncoder"],
            ["age", "Numerik", "0,08 – 80,0 tahun", "StandardScaler"],
            ["hypertension", "Biner", "0 / 1", "StandardScaler (indikator)"],
            ["heart_disease", "Biner", "0 / 1", "StandardScaler (indikator)"],
            ["smoking_history", "Kategorik", "6 kategori (incl. No Info)", "OneHotEncoder"],
            ["bmi", "Numerik", "10,01 – 95,69 kg/m²", "StandardScaler"],
            ["HbA1c_level", "Numerik", "3,5 – 9,0 %", "StandardScaler"],
            ["blood_glucose_level", "Numerik", "80 – 300 mg/dL", "StandardScaler"],
            ["diabetes (target)", "Biner", "0 = negatif, 1 = positif", "—"],
        ],
        widths=[34, 22, 48, W - 104],
    )
    pdf.h2("2.2  Pembersihan Data (Cleaning)")
    pdf.bullet([
        "Missing value: tidak ditemukan satu pun nilai kosong pada seluruh 100.000 baris, "
        "sehingga imputasi tidak diperlukan (diverifikasi dengan df.isna().sum()).",
        "Duplikasi: ditemukan 3.854 baris duplikat sempurna dan dibuang "
        "(drop_duplicates) agar sampel identik tidak bocor antar partisi split — ukuran akhir "
        "96.146 sampel.",
        "Kategori 'Other' pada gender (18 sampel) tetap dipertahankan sebagai kategori "
        "tersendiri oleh OneHotEncoder.",
    ])
    pdf.figure("fig_numeric_distributions.png",
               "Gambar 2.1  Distribusi fitur numerik per kelas: HbA1c dan glukosa darah kelas "
               "positif bergeser jauh ke kanan (pemisah terkuat).", w=165)
    pdf.figure("fig_correlation_heatmap.png",
               "Gambar 2.2  Heatmap korelasi: HbA1c_level ↔ diabetes ≈ 0,56 dan "
               "blood_glucose_level ↔ diabetes ≈ 0,55 — dominan dibanding fitur lain.", w=115)
    pdf.figure("fig_categorical_distribution.png",
               "Gambar 2.3  Distribusi fitur kategorik terhadap kelas target.", w=165)

    pdf.h2("2.3  Pembagian Data — Train / Validation / Test (70 : 15 : 15, Stratified)")
    pdf.para(
        "Split dilakukan dengan dua kali train_test_split (70/30 lalu 15/15) menggunakan "
        "stratify=y agar proporsi kelas positif ±8,8 % terjaga di setiap partisi. Split "
        "dilakukan SEBELUM preprocessing apa pun.")
    pdf.table(
        ["Partisi", "Jumlah Sampel", "Proporsi", "p(diabetes=1)"],
        [
            ["Train", "67.302", "70,0 %", "0,0882"],
            ["Validation", "14.422", "15,0 %", "0,0883"],
            ["Test", "14.422", "15,0 %", "0,0882"],
        ],
        widths=[42, 42, 42, W - 126],
    )
    pdf.h2("2.4  Pipeline Preprocessing & Pencegahan Data Leakage")
    pdf.para(
        "Preprocessing memakai ColumnTransformer Scikit-Learn: StandardScaler untuk 6 kolom "
        "numerik dan OneHotEncoder(handle_unknown='ignore') untuk 2 kolom kategorik. "
        "Setelah one-hot, dimensi fitur model menjadi 15 (6 numerik + 3 gender + 6 smoking).")
    pdf.para(
        "Kaidah kritis pencegahan kebocoran data: preprocessor.fit() dipanggil HANYA pada "
        "data Train; data Validation dan Test hanya menerima transform(). Dengan demikian "
        "statistik train (mean/std scaler, daftar kategori encoder) tidak pernah melihat data "
        "evaluasi. Objek preprocessor yang sama diserialisasi ke preprocessor.pkl sehingga "
        "aplikasi desktop memakai transformasi yang identik dengan proses training.")
    pdf.code(
        "preprocessor = ColumnTransformer([\n"
        "    ('num', StandardScaler(), NUM_FEATURES),\n"
        "    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CAT_FEATURES),\n"
        "])\n"
        "preprocessor.fit(X_train)                 # FIT hanya pada TRAIN\n"
        "X_train_pp = preprocessor.transform(X_train)\n"
        "X_val_pp   = preprocessor.transform(X_val)    # transform saja\n"
        "X_test_pp  = preprocessor.transform(X_test)   # transform saja")

    pdf.h2("2.5  Penanganan Class Imbalance")
    pdf.para(
        "Rasio kelas negatif : positif = 10,34 : 1. Model naif yang selalu memprediksi 0 "
        "memperoleh akurasi 91,5 % tanpa mendeteksi satu pun pasien diabetes (Accuracy "
        "Paradox). Dua mitigasi diterapkan:")
    pdf.bullet([
        "Class weighting 'balanced' — dihitung hanya dari data train: bobot kelas 0 = 0,5484 "
        "dan kelas 1 = 5,6680. Model A menerimanya lewat class_weight; Model B (label one-hot) "
        "lewat sample_weight yang ekuivalen secara matematis.",
        "Decision threshold tuning — ambang klasifikasi θ dioptimalkan pada data VALIDATION "
        "dengan memaksimalkan F1-Score kelas positif (grid θ ∈ [0,10; 0,90]), lalu ambang "
        "terbaik diterapkan pada Test Set. Default θ = 0,5 tidak cocok karena pembobotan kelas "
        "menggeser distribusi probabilitas model.",
        "Oversampling SMOTENC (eksperimen pembanding, Model C) — kelas minoritas pada data "
        "train disintesis hingga seimbang: 67.302 → 122.730 sampel (positif 5.937 → 61.365). "
        "SMOTENC dijalankan HANYA pada train setelah split (anti-leakage) dan arsitekturnya "
        "identik dengan Model B agar perbandingan adil. Hasil lengkap dikomparasi pada Bab 4.",
    ])
    pdf.para(
        "Metrik akurasi TIDAK dijadikan acuan utama: evaluasi berfokus pada Recall "
        "(sensitivitas — menghindari False Negative yang fatal secara medis), Precision, "
        "F1-Score, Confusion Matrix, serta ROC/PR Curve.", gap=3)

    # ================================================================ BAB 3
    pdf.chapter("Arsitektur Model — Sigmoid vs Softmax")
    pdf.h2("3.1  Desain Dua Arsitektur Custom MLP")
    pdf.para(
        "Kedua arsitektur dibangun dari awal (Functional Keras) dengan variasi kedalaman, "
        "lebar, regularisasi, dan learning rate sesuai spesifikasi tugas; arsitektur Model B "
        "kemudian dipakai ulang sebagai Model C pada eksperimen SMOTENC (Bab 2.5 & 4.6). "
        "Callback: EarlyStopping(patience=7, restore_best_weights) dan "
        "ReduceLROnPlateau(factor=0,5, patience=3). Batch size 1024, maksimal 60 epoch; "
        "konvergensi stabil dengan best validation loss 0,194 (A), 0,204 (B), dan 0,191 (C, "
        "early stopping epoch 35). Seed global 42 untuk reproducibility.")
    pdf.table(
        ["Aspek", "Model A — Sigmoid", "Model B — Softmax"],
        [
            ["Topologi", "15 → 64 → 32 → 1", "15 → 128 → 64 → 32 → 2"],
            ["Kedalaman (hidden)", "2 layer", "3 layer (lebih dalam)"],
            ["Lebar maksimum", "64 neuron", "128 neuron (lebih lebar)"],
            ["Regularisasi", "Dropout 0,30 / 0,20", "BatchNorm + Dropout 0,30 / 0,25"],
            ["Aktivasi output", "Sigmoid (1 neuron)", "Softmax (2 neuron)"],
            ["Loss", "binary_crossentropy", "categorical_crossentropy"],
            ["Format label", "Skalar y ∈ {0, 1}", "One-hot y ∈ {[1,0],[0,1]}"],
            ["Optimizer / LR awal", "Adam, lr = 1×10⁻³", "Adam, lr = 5×10⁻⁴"],
            ["LR scheduling", "ReduceLROnPlateau", "ReduceLROnPlateau"],
            ["Imbalance handling", "class_weight", "sample_weight (ekuivalen)"],
        ],
        widths=[36, (W - 36) / 2, (W - 36) / 2],
    )
    pdf.h2("3.2  Formulasi Matematis Output Layer")
    pdf.h3("Opsi A — Sigmoid")
    pdf.para(
        "Satu neuron output: σ(z) = 1 / (1 + e^(−z)) ∈ [0, 1], diinterpretasikan sebagai "
        "P(diabetes). Loss binary_crossentropy per sampel: "
        "L_BCE = −[ y·ln(ŷ) + (1−y)·ln(1−ŷ) ]. Keputusan: ŷ ≥ θ → Positif.")
    pdf.h3("Opsi B — Softmax")
    pdf.para(
        "Dua neuron output: P(y=i | z) = e^(z_i) / Σⱼ e^(z_j), i ∈ {0,1}, menghasilkan "
        "distribusi probabilitas penuh (P₀, P₁). Loss categorical_crossentropy: "
        "L_CCE = −Σᵢ yᵢ·ln(ŷᵢ). Keputusan: argmax(P₀, P₁) atau P₁ ≥ θ. Untuk kasus biner, "
        "kedua formulasi ekuivalen secara teoretis; perbandingan empiris pada Bab 4 "
        "menentukan pilihan akhir.", gap=3)
    pdf.h2("3.3  Justifikasi Pemilihan Arsitektur")
    pdf.para(
        "Model A mewakili desain ringan (dangkal, sempit, dropout murni) dengan learning rate "
        "relatif besar; Model B mewakili desain dalam-lebar dengan Batch Normalization untuk "
        "stabilitas gradien dan learning rate lebih kecil. Perbedaan desain ini disengaja agar "
        "komparasi Bab 4 menjawab pertanyaan: apakah kapasitas dan regularisasi ekstra "
        "sepadan, serta formulasi output mana yang lebih baik pada data timpang ini?")

    # ================================================================ BAB 4
    pdf.chapter("Hasil Evaluasi & Seleksi Model")
    pdf.h2("4.1  Decision Threshold Tuning (Data Validation)")
    pdf.para(
        "Karena pembobotan kelas menggeser distribusi probabilitas, ambang default 0,5 bukan "
        "pilihan terbaik. Sweep θ pada data validasi menghasilkan θ* = 0,86 untuk Model A, "
        "θ* = 0,85 untuk Model B, dan θ* = 0,90 untuk Model C (F1 validasi ≈ 0,79 untuk "
        "ketiganya). Ambang model terbaik inilah yang disimpan ke preprocessor.pkl dan dipakai "
        "aplikasi desktop.")
    pdf.figure("fig_threshold_sweep.png",
               "Gambar 4.1  Sweep ambang keputusan pada data Validation: F1-Score kelas "
               "positif vs θ untuk kedua model.", w=145)
    pdf.h2("4.2  Metrik Klinis pada Test Set")
    pdf.h3("a) Titik operasi default θ = 0,50")
    pdf.table(
        ["Metrik", "Model A (Sigmoid)", "Model B (Softmax)", "Model C (Softmax+SMOTE)"],
        [
            ["Accuracy", "0,8954", "0,8981", "0,8987"],
            ["Precision", "0,4544", "0,4611", "0,4616"],
            ["Recall (Sensitivitas)", "0,9237", "0,9167", "0,8923"],
            ["F1-Score", "0,6091", "0,6135", "0,6084"],
            ["ROC-AUC", "0,9773", "0,9772", "0,9772"],
            ["PR-AUC (AP)", "0,8847", "0,8840", "0,8840"],
        ],
        widths=[44, (W - 44) / 3, (W - 44) / 3, (W - 44) / 3],
    )
    pdf.h3("b) Titik operasi ambang optimal θ* (hasil tuning)")
    pdf.table(
        ["Metrik", "Model A (θ*=0,86)", "Model B (θ*=0,85)", "Model C (θ*=0,90)"],
        [
            ["Accuracy", "0,9709", "0,9724", "0,9714"],
            ["Precision", "0,9410", "0,9740", "0,9778"],
            ["Recall (Sensitivitas)", "0,7146", "0,7060", "0,6918"],
            ["F1-Score", "0,8123", "0,8186", "0,8103"],
            ["ROC-AUC", "0,9773", "0,9772", "0,9737"],
            ["PR-AUC (AP)", "0,8847", "0,8840", "0,8728"],
        ],
        widths=[44, (W - 44) / 3, (W - 44) / 3, (W - 44) / 3],
    )
    pdf.para(
        "Tanpa tuning (θ=0,5) ketiga model sangat sensitif (Recall 0,89–0,92) tetapi precision "
        "rendah (±0,46): hampir separuh alarm positif adalah palsu. Dengan ambang optimal, "
        "precision melonjak ke 0,94–0,98 dengan recall tetap 0,69–0,71 — titik operasi yang "
        "sehat untuk alat skrining pendamping tenaga medis. Pemilihan θ dapat digeser sesuai "
        "kebijakan klinis: turunkan θ bila sensitivitas harus diprioritaskan.")
    pdf.h2("4.3  Confusion Matrix (Test Set, θ*)")
    pdf.figure("fig_confusion_matrix.png",
               "Gambar 4.2  Confusion Matrix kedua model pada Test Set (14.422 sampel).", w=160)
    pdf.table(
        ["Model", "TN", "FP", "FN", "TP"],
        [
            ["Model A (Sigmoid, θ=0,86)", "13.093", "57", "363", "909"],
            ["Model B (Softmax, θ=0,85)", "13.126", "24", "374", "898"],
            ["Model C (Softmax+SMOTE, θ=0,90)", "13.130", "20", "392", "880"],
        ],
        widths=[62, (W - 62) / 4, (W - 62) / 4, (W - 62) / 4, (W - 62) / 4],
    )
    pdf.h2("4.4  ROC & Precision–Recall Curve")
    pdf.figure("fig_roc_curve.png",
               "Gambar 4.3  ROC Curve: ketiga model hampir identik (AUC 0,974–0,977).", w=110)
    pdf.figure("fig_pr_curve.png",
               "Gambar 4.4  Precision–Recall Curve: AP 0,873–0,885 — jauh di atas baseline "
               "prevalensi 0,088.", w=110)
    pdf.h2("4.5  Riwayat Pelatihan")
    pdf.figure("fig_training_history.png",
               "Gambar 4.5  Kurva loss & akurasi train/validation: konvergensi stabil tanpa "
               "overfitting signifikan (gap train–val kecil).", w=165)
    pdf.h2("4.6  Seleksi Model Terbaik & Peran SMOTE")
    pdf.para(
        "Kriteria seleksi utama: F1-Score kelas positif pada Test Set dengan ambang optimal "
        "(metrik paling informatif untuk data timpang), ROC-AUC sebagai pembanding. Hasil: "
        "Model B (Softmax, class weighting) unggul — F1 0,8186, Precision 0,9740, Recall "
        "0,7060, Accuracy 0,9724, ROC-AUC 0,9772 — diikuti Model A (F1 0,8123) dan Model C "
        "(F1 0,8103).")
    pdf.para(
        "Temuan empiris mengenai SMOTE: dengan arsitektur yang identik (Model B vs Model C), "
        "oversampling SMOTENC TIDAK mengungguli class weighting — F1 turun 0,8186 → 0,8103, "
        "ROC-AUC turun 0,9772 → 0,9737, dan recall pun sedikit lebih rendah (0,6918 vs "
        "0,7060) meski precision tertinggi (0,9778). Sintesis sampel interpolatif pada data "
        "berdimensi 15 dengan fitur kuat (HbA1c, glukosa) tidak menambah informasi baru, "
        "malah menambah biaya komputasi (train 122.730 vs 67.302 sampel) dan risiko artefak "
        "sintetis. Karena itu class weighting + threshold tuning dipertahankan sebagai teknik "
        "mitigasi imbalance utama, dan Model B ditetapkan sebagai model produksi.")
    pdf.para(
        "Justifikasi output layer: secara teoretis sigmoid dan softmax ekuivalen untuk "
        "klasifikasi biner; secara empiris pada proyek ini arsitektur softmax dengan "
        "BatchNormalization dan kapasitas lebih besar menghasilkan kalibrasi keputusan yang "
        "sedikit lebih baik (precision tertinggi, FP terendah) sehingga Model B ditetapkan "
        "sebagai model produksi. Model B diekspor ke artifacts/model.keras bersama ambang "
        "θ* = 0,85 di preprocessor.pkl.")
    pdf.para(
        "Catatan klinis: recall 0,706 berarti ±29 % kasus positif lolos skrining pada titik "
        "operasi ini. Dalam praktik, hasil aplikasi harus selalu dikonfirmasi tes diagnostik "
        "(FPG/OGTT/HbA1c lab), dan θ dapat diturunkan bila sensitivitas lebih diprioritaskan.",
        gap=3)

    # ================================================================ BAB 5
    pdf.chapter("Integrasi Sistem & Aplikasi Desktop")
    pdf.h2("5.1  Artefak Serialisasi")
    pdf.bullet([
        "artifacts/model.keras — arsitektur + bobot Model B terlatih (dimuat dengan "
        "tf.keras.models.load_model).",
        "artifacts/preprocessor.pkl — bundle joblib berisi: objek ColumnTransformer "
        "(StandardScaler + OneHotEncoder hasil fit data train), daftar urutan 15 fitur, "
        "ambang optimal θ*, mode output ('softmax'), dan metadata model.",
        "artifacts/training_history.json — riwayat loss/akurasi, bobot kelas, dan seluruh "
        "metrik untuk reproduktibilitas laporan.",
    ])
    pdf.h2("5.2  Alur Inferensi GUI (Fase III)")
    pdf.numbered([
        "Saat aplikasi dimulai, src/app.py melokalisasi folder artifacts/, memuat model.keras "
        "dan preprocessor.pkl, lalu menampilkan nama model dan ambang pada status bar.",
        "Pengguna mengisi 8 kontrol input (4 dropdown kategorik + 4 entry numerik) pada panel "
        "kiri \"Patient Information\".",
        "Tombol Predict memicu validasi input: field kosong, nilai non-numerik, dan nilai di "
        "luar rentang klinis wajar ditolak dengan dialog pop-up informatif — aplikasi tidak "
        "pernah crash karena input salah.",
        "Input valid disusun menjadi DataFrame dengan urutan kolom identik saat training, "
        "ditransformasi preprocessor.pkl (scaler + encoder yang sama persis), lalu diumpankan "
        "ke model.",
        "Probabilitas P(diabetes) dibandingkan θ* = 0,85; panel kanan \"Diabetes Diagnosis\" "
        "menampilkan status berwarna (MERAH = Positive/Diabetic, HIJAU = "
        "Negative/Non-Diabetic), confidence score, probabilitas, dan daftar faktor risiko "
        "klinis yang terdeteksi (mis. HbA1c ≥ 6,5 %).",
        "Tombol Reset mengembalikan form ke kondisi awal dan mengosongkan panel hasil.",
    ])
    pdf.h2("5.3  Hasil Uji Integrasi")
    pdf.table(
        ["Skenario Pasien", "Input Utama", "P(diabetes)", "Keputusan GUI"],
        [
            ["Sehat", "Female, 27 th, BMI 21,5, HbA1c 5,0 %, glukosa 95", "0,0005",
             "NEGATIVE (hijau)"],
            ["Berisiko tinggi", "Male, 58 th, hipertensi, perokok aktif, BMI 32,4, "
             "HbA1c 7,8 %, glukosa 210", "1,0000", "POSITIVE (merah)"],
            ["Default form", "Female, 30 th, BMI 25,0, HbA1c 5,5 %, glukosa 110", "0,090",
             "NEGATIVE (hijau)"],
        ],
        widths=[34, 74, 24, W - 132], fontsize=8.2,
    )
    pdf.para(
        "Seluruh skenario diverifikasi otomatis oleh src/test_backend.py (uji validasi input, "
        "inferensi kedua pasien contoh, dan penanganan error) serta smoke test GUI pada kedua "
        "varian antarmuka (CustomTkinter dan fallback Tkinter).")

    # ================================================================ BAB 6
    pdf.chapter("Panduan Instalasi & Pengoperasian (User Guide)")
    pdf.h2("6.1  Kebutuhan Sistem")
    pdf.bullet([
        "Python 3.9 atau lebih baru (disarankan 3.10–3.12).",
        "Paket: tensorflow, pandas, numpy, scikit-learn, joblib, matplotlib, seaborn, "
        "customtkinter (GUI; bila tidak ada, aplikasi otomatis memakai Tkinter bawaan).",
        "Sistem operasi apa pun dengan tampilan grafis (Windows / macOS / Linux).",
    ])
    pdf.h2("6.2  Instalasi")
    pdf.code(
        "# 1. ekstrak berkas ZIP tugas ke sebuah folder\n"
        "# 2. buat virtual environment (disarankan)\n"
        "python -m venv .venv\n"
        ".venv\\Scripts\\activate        # Windows\n"
        "source .venv/bin/activate     # macOS/Linux\n"
        "\n"
        "# 3. pasang dependensi\n"
        "pip install -r requirements.txt\n"
        "\n"
        "# 4. jalankan aplikasi desktop\n"
        "python src/app.py")
    pdf.h2("6.3  Mengoperasikan Aplikasi")
    pdf.numbered([
        "Buka aplikasi — jendela \"Diabetes Prediction System\" muncul dengan panel kiri "
        "\"Patient Information\" dan panel kanan \"Diabetes Diagnosis\". Status bar "
        "menampilkan model dan ambang θ yang aktif.",
        "Pilih nilai dropdown: Gender (Female/Male/Other), Hypertension (0/1), Heart Disease "
        "(0/1), Smoking History (never/current/former/ever/not current/No Info).",
        "Ketik nilai numerik: Age (tahun), BMI (kg/m²), HbA1c Level (%), Blood Glucose "
        "(mg/dL). Koma maupun titik desimal diterima.",
        "Tekan Predict — panel kanan menampilkan diagnosis: teks besar merah (POSITIVE — "
        "DIABETIC) atau hijau (NEGATIVE — NON-DIABETIC), confidence score (%), probabilitas, "
        "dan faktor risiko klinis yang terdeteksi.",
        "Bila input kosong/tidak valid, muncul dialog peringatan yang menjelaskan kesalahannya "
        "— perbaiki lalu coba lagi.",
        "Tekan Reset untuk mengembalikan form ke nilai awal.",
    ])
    pdf.h2("6.4  Melatih Ulang Model (Opsional)")
    pdf.para(
        "Buka src/diabetes_model_development.ipynb (Jupyter) dan jalankan seluruh sel. "
        "Notebook melakukan EDA, split stratified, preprocessing, pelatihan Model A vs B, "
        "evaluasi lengkap, lalu menulis ulang artifacts/model.keras dan "
        "artifacts/preprocessor.pkl yang langsung dipakai aplikasi.")

    # ================================================================ BAB 7
    pdf.chapter("Penutup")
    pdf.h2("7.1  Kesimpulan")
    pdf.numbered([
        "Pipeline data klinis 96.146 sampel dibangun bebas kebocoran data: split stratified "
        "70:15:15 mendahului preprocessing; scaler/encoder di-fit hanya pada train; objek "
        "yang sama dipakai ulang saat inferensi GUI.",
        "Class imbalance 10,3 : 1 diatasi dengan class weighting balanced dan decision "
        "threshold tuning — akurasi tidak dijadikan metrik tunggal (Accuracy Paradox). "
        "Oversampling SMOTENC diuji sebagai pembanding dan terbukti sedikit kalah efektif "
        "(F1 0,8103 vs 0,8186), menegaskan pilihan class weighting.",
        "Komparasi dua arsitektur custom MLP menunjukkan Model B (Softmax + BatchNorm, "
        "15→128→64→32→2) sebagai yang terbaik: Accuracy 97,24 %, Precision 97,40 %, Recall "
        "70,60 %, F1 0,8186, ROC-AUC 0,977 pada Test Set.",
        "Formulasi sigmoid vs softmax terbukti ekuivalen secara kapasitas (ROC-AUC hampir "
        "identik); pilihan akhir ditentukan oleh desain arsitektur dan hasil empiris.",
        "Aplikasi desktop \"Diabetes Prediction System\" berhasil mengintegrasikan model, "
        "pipeline, validasi input, dan inferensi real-time dengan kode warna diagnosis yang "
        "intuitif.",
    ])
    pdf.h2("7.2  Saran Pengembangan")
    pdf.bullet([
        "Eksplorasi ambang berbasis kurva ROC (Youden's J) atau biaya klinis FP/FN asimetris.",
        "Teknik mitigasi imbalance lanjutan: SMOTE, focal loss, atau ensemble.",
        "Penambahan fitur rekam medis lain dan validasi eksternal pada data rumah sakit riil.",
        "Kalibrasi probabilitas (Platt/Isotonic) dan kemasan distribusi (PyInstaller) menjadi "
        "executable satu berkas.",
    ])

    # ================================================================ LAMPIRAN
    pdf.chapter("Lampiran — Struktur Repositori & Dependensi")
    pdf.code(
        "DSEC_Diabetes_Prediction_Project/\n"
        "├── diabetes_prediction_dataset.csv     # dataset Kaggle (100.000 baris)\n"
        "├── Diabetes_Prediction_Project.pdf     # naskah tugas\n"
        "├── README.md, requirements.txt\n"
        "├── src/\n"
        "│   ├── diabetes_model_development.ipynb # Fase I: EDA → training → ekspor\n"
        "│   ├── app.py                          # Fase II+III: GUI + integrasi inferensi\n"
        "│   ├── test_backend.py                 # uji mandiri backend\n"
        "│   └── make_submission_zip.py          # pembuat berkas pengumpulan .zip\n"
        "├── artifacts/\n"
        "│   ├── model.keras                     # Model B terlatih (produksi)\n"
        "│   ├── preprocessor.pkl                # scaler+encoder+ambang optimal\n"
        "│   └── training_history.json\n"
        "├── assets/figures/                     # seluruh figur laporan\n"
        "└── laporan/\n"
        "    ├── Laporan_Teknis_Prediksi_Diabetes.pdf\n"
        "    └── build_report.py                 # generator laporan")
    pdf.h3("requirements.txt")
    pdf.code(
        "tensorflow>=2.16\npandas>=2.0\nnumpy>=1.26\nscikit-learn>=1.4\njoblib>=1.3\n"
        "matplotlib>=3.8\nseaborn>=0.13\ncustomtkinter>=5.2")

    pdf.output(str(OUT))
    print("PDF laporan ditulis:", OUT)


if __name__ == "__main__":
    build()
