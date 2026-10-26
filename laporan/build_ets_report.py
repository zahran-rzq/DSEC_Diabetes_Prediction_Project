#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator Laporan Jawaban ETS — Prediksi Risiko Diabetes (PDF)
================================================================
 Mata kuliah : Dasar Sistem Elektronika Cerdas (ETS, Sifat Terbuka)
 Soal        : Soal 1 — Aplikasi Desktop Prediksi Risiko Diabetes
 Output      : laporan/Laporan_ETS_DSEC_Prediksi_Diabetes.pdf

 Jalankan :
   .venv/bin/python laporan/build_ets_report.py --nama "Nama Lengkap" --nrp 07xxxx
 (butuh: pip install fpdf2 pillow)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from fpdf import FPDF
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "assets" / "figures"
OUT = Path(__file__).resolve().parent / "Laporan_ETS_DSEC_Prediksi_Diabetes.pdf"


def _font_dir() -> str:
    cand = ["/usr/share/fonts/truetype/dejavu"]
    try:
        from matplotlib import get_data_path
        cand.append(str(Path(get_data_path()) / "fonts" / "ttf"))
    except Exception:
        pass
    need = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf",
            "DejaVuSans-BoldOblique.ttf", "DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf")
    for c in cand:
        if all((Path(c) / f).exists() for f in need):
            return c
    raise FileNotFoundError("Font DejaVu tidak ditemukan")


NAVY, ACCENT, GRAY = (27, 42, 74), (47, 111, 237), (90, 100, 120)


class ETSReport(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_auto_page_break(auto=True, margin=18)
        fdir = _font_dir()
        self.add_font("DejaVu", "", f"{fdir}/DejaVuSans.ttf")
        self.add_font("DejaVu", "B", f"{fdir}/DejaVuSans-Bold.ttf")
        self.add_font("DejaVu", "I", f"{fdir}/DejaVuSans-Oblique.ttf")
        self.add_font("DejaVu", "BI", f"{fdir}/DejaVuSans-BoldOblique.ttf")
        self.add_font("Mono", "", f"{fdir}/DejaVuSansMono.ttf")
        self.add_font("Mono", "B", f"{fdir}/DejaVuSansMono-Bold.ttf")
        self._footer_on = False

    # ---------- layout ----------
    def header(self):
        if not self._footer_on or self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 7.5)
        self.set_text_color(*GRAY)
        self.cell(0, 5, "ETS Dasar Sistem Elektronika Cerdas · Soal 1 — "
                        "Aplikasi Desktop Prediksi Risiko Diabetes", align="L")
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
        self.set_font("DejaVu", "B", 15)
        self.set_text_color(*NAVY)
        self.multi_cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
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
        if self.get_y() > self.h - 35:
            self.add_page()
        self.set_font("DejaVu", "B", 10.5)
        self.set_text_color(*NAVY)
        self.multi_cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def para(self, text, size=10, gap=2.2, align="J"):
        self.set_font("DejaVu", "", size)
        self.set_text_color(30, 32, 40)
        self.multi_cell(0, 5.4, text, align=align, new_x="LMARGIN", new_y="NEXT")
        self.ln(gap)

    def bullet(self, items, size=10):
        self.set_font("DejaVu", "", size)
        self.set_text_color(30, 32, 40)
        for it in items:
            self.cell(5, 5.4, "•")
            self.multi_cell(self.w - self.l_margin - self.r_margin - 5, 5.4, it,
                            align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def numbered(self, items, size=10):
        self.set_font("DejaVu", "", size)
        self.set_text_color(30, 32, 40)
        for i, it in enumerate(items, 1):
            self.cell(6, 5.4, f"{i}.")
            self.multi_cell(self.w - self.l_margin - self.r_margin - 6, 5.4, it,
                            align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def code(self, text):
        w = self.w - self.l_margin - self.r_margin
        self.set_font("Mono", "", 8.5)
        lines = text.split("\n")
        h = 4.6 * len(lines) + 8
        if self.get_y() + h > self.h - 18:
            self.add_page()
        self.set_fill_color(244, 246, 250)
        self.set_draw_color(200, 208, 224)
        self.rect(self.l_margin, self.get_y(), w, h, style="F")
        y0 = self.get_y() + 4
        for ln in lines:
            self.set_x(self.l_margin + 4)
            self.set_font("Mono", "", 8.5)
            self.set_text_color(40, 44, 56)
            self.cell(w - 8, 4.6, ln, new_x="LMARGIN", new_y="NEXT")
        self.set_y(y0 + 4.6 * len(lines) + 4)
        self.ln(2)

    def table(self, header, rows, widths=None, fontsize=8.6, header_fill=NAVY, aligns=None):
        if widths is None:
            n = len(header)
            widths = [(self.w - self.l_margin - self.r_margin) / n] * n
        if aligns is None:
            aligns = ["L"] + ["C"] * (len(header) - 1)
        self.set_font("DejaVu", "B", fontsize)
        self.set_fill_color(*header_fill)
        self.set_text_color(255, 255, 255)
        h = 5.8
        self.cell(0, h, "", new_x="LMARGIN", new_y="NEXT")
        # header
        for w_, cell, al in zip(widths, header, aligns):
            self.set_font("DejaVu", "B", fontsize)
            self.set_fill_color(*header_fill)
            self.set_text_color(255, 255, 255)
            x0 = self.get_x()
            self.multi_cell(w_, h, str(cell), align=al, fill=True,
                            new_x="RIGHT", new_y="TOP", border=0)
            self.set_xy(x0, self.get_y())
        y_after = self.get_y()
        self.set_x(self.l_margin)
        self.ln(max(0, y_after - self.get_y()))
        # rows
        for r, row in enumerate(rows):
            # cek tinggi baris (multi-baris)
            self.set_font("DejaVu", "", fontsize)
            max_lines = 1
            for w_, cell in zip(widths, row):
                lines = self.multi_cell(w_ - 1.2, h, str(cell), dry_run=True, output="LINES")
                max_lines = max(max_lines, len(lines))
            rh = h * max_lines
            if self.get_y() + rh > self.h - 18:
                self.add_page()
            fill = (244, 246, 250) if r % 2 == 0 else (255, 255, 255)
            y0 = self.get_y()
            self.set_x(self.l_margin)
            for w_, cell, al in zip(widths, row, aligns):
                self.set_font("DejaVu", "", fontsize)
                self.set_fill_color(*fill)
                self.set_text_color(30, 32, 40)
                x0 = self.get_x()
                self.multi_cell(w_, h, str(cell), align=al, fill=True,
                                new_x="RIGHT", new_y="TOP", border=0)
                self.set_xy(x0, self.get_y())
            self.set_x(self.l_margin)
            self.set_y(y0 + rh)
            self.set_draw_color(215, 222, 232)
            self.set_line_width(0.2)
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def figure(self, fname, caption, width=None, max_height=None):
        path = FIG / fname
        if not path.exists():
            self.para(f"[figur tidak ditemukan: {fname}]")
            return
        w_px, h_px = Image.open(path).size
        max_w = self.w - self.l_margin - self.r_margin
        w = max_w if width is None else width
        h = w * h_px / w_px
        if max_height and h > max_height:
            h = max_height
            w = h * w_px / h_px
        cap_h = self._caption_height(caption)
        if self.get_y() + h + cap_h + 6 > self.h - 18:
            self.add_page()
        x = self.l_margin + (max_w - w) / 2
        self.image(str(path), x=x, w=w)
        self.ln(1.5)
        self.set_font("DejaVu", "I", 8.5)
        self.set_text_color(*GRAY)
        self.multi_cell(0, 4.4, caption, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def _caption_height(self, caption):
        self.set_font("DejaVu", "I", 8.5)
        lines = self.multi_cell(self.w - self.l_margin - self.r_margin, 4.4, caption,
                                dry_run=True, output="LINES")
        return 4.4 * len(lines) + 2


# ============================================================================
# ISI LAPORAN
# ============================================================================
def build(nama: str, nrp: str) -> None:
    doc = ETSReport()
    doc.set_margins(20, 18, 20)

    # ---------------------------- HALAMAN JUDUL ----------------------------
    doc.add_page()
    doc.ln(28)
    doc.set_font("DejaVu", "", 11)
    doc.set_text_color(*GRAY)
    doc.cell(0, 7, "EVALUASI TENGAH SEMESTER (ETS) — SIFAT: TERBUKA",
             align="C", new_x="LMARGIN", new_y="NEXT")
    doc.ln(6)
    doc.set_font("DejaVu", "B", 24)
    doc.set_text_color(*NAVY)
    doc.multi_cell(0, 12, "Laporan Jawaban ETS", align="C", new_x="LMARGIN", new_y="NEXT")
    doc.ln(2)
    doc.set_font("DejaVu", "B", 15)
    doc.set_text_color(*ACCENT)
    doc.multi_cell(0, 8, "Mata Kuliah: Dasar Sistem Elektronika Cerdas",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    doc.ln(8)
    doc.set_font("DejaVu", "", 12)
    doc.set_text_color(30, 32, 40)
    doc.multi_cell(0, 7, "Soal 1 (Bobot 50%) — Rancang Bangun Aplikasi Desktop "
                         "Prediksi Risiko Diabetes Berbasis Deep Learning",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    doc.ln(18)

    def center_line(left, right, bold_right=False):
        doc.set_x(doc.l_margin + 30)
        doc.set_font("DejaVu", "", 12)
        doc.set_text_color(30, 32, 40)
        doc.cell(60, 8, left)
        doc.set_font("DejaVu", "B" if bold_right else "", 12)
        doc.cell(0, 8, right, new_x="LMARGIN", new_y="NEXT")

    center_line("Nama Mahasiswa :", nama)
    center_line("NRP            :", nrp)
    center_line("Program Studi  :", "Teknik Elektro")
    center_line("Fakultas       :", "Teknologi Industri dan Kemaritiman")
    center_line("Semester       :", "Gasal 2026/2027")
    doc.ln(14)
    doc.set_draw_color(*ACCENT)
    doc.set_line_width(0.6)
    doc.line(doc.l_margin + 40, doc.get_y(), doc.w - doc.r_margin - 40, doc.get_y())
    doc.ln(10)
    doc.set_font("DejaVu", "", 11)
    doc.set_text_color(*GRAY)
    doc.multi_cell(0, 6, "Departemen Teknik Elektro — FTEIC — Institut Teknologi "
                         "Sepuluh Nopember\n"
                         "Surabaya, 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    # ---------------------------- DAFTAR ISI ----------------------------
    doc._footer_on = True
    doc.chapter("DAFTAR ISI")
    toc = [
        "Soal 1 — Aplikasi Desktop Prediksi Risiko Diabetes",
        "    1.1  Analisis dan Preprocessing Data",
        "    1.2  Pemilihan Model dan Aturan Visualisasi",
        "    1.3  Evaluasi Model (Matriks Konfusi & Metrik Klinis)",
        "    1.4  Perancangan Antarmuka Pengguna (UI)",
        "Kesimpulan",
        "Daftar Pustaka",
    ]
    doc.set_font("DejaVu", "", 11)
    doc.set_text_color(30, 32, 40)
    for t in toc:
        doc.multi_cell(0, 7, t, new_x="LMARGIN", new_y="NEXT")

    # ==================================================================
    # SOAL 1
    # ==================================================================
    doc.chapter("SOAL 1 — APLIKASI DESKTOP PREDIKSI RISIKO DIABETES")
    doc.para(
        "Sistem yang dirancang adalah aplikasi desktop berbasis Python yang berfungsi sebagai "
        "Clinical Decision Support System (CDSS): pengguna memasukkan 8 data klinis pasien secara "
        "manual, lalu aplikasi memprediksi \"Risiko Diabetes\" atau \"Tidak Berisiko Diabetes\" "
        "berdasarkan model deep learning (Multi-Layer Perceptron, TensorFlow/Keras) yang dilatih "
        "pada dataset Kaggle Diabetes Prediction Dataset. Alur pembangunan sistem secara "
        "keseluruhan: (1) analisis dan preprocessing dataset, (2) pembangunan & pelatihan model "
        "deep learning, (3) evaluasi klinis, (4) perancangan dan integrasi antarmuka pengguna."
    )

    # ---------------- 1.1 ----------------
    doc.h2("1.1  Analisis dan Preprocessing Data")
    doc.h3("a. Deskripsi Dataset dan Atribut")
    doc.para(
        "Dataset acuan adalah Kaggle \"Diabetes Prediction Dataset\" (iamustafatz): 100.000 "
        "rekam medis dengan 8 fitur prediktor dan 1 target biner (diabetes: 1 = diabetic, "
        "0 = non-diabetic). Ringkasan atribut:"
    )
    doc.table(
        ["Atribut", "Jenis", "Domain / Kategori", "Peran Klinis"],
        [
            ["age", "Numerik (tahun)", "0,08 – 80", "Risiko meningkat seiring usia"],
            ["gender", "Kategorik", "Female / Male / Other", "Faktor demografis"],
            ["hypertension", "Biner", "0 / 1", "Komorbid kardiovaskular"],
            ["heart_disease", "Biner", "0 / 1", "Komorbid kardiovaskular"],
            ["smoking_history", "Kategorik", "never, current, former, ever, not current, No Info",
             "Faktor gaya hidup"],
            ["bmi", "Numerik (kg/m²)", "10,01 – 95,69", "Indeks obesitas"],
            ["HbA1c_level", "Numerik (%)", "3,5 – 9,0", "Rata-rata glikemik 2–3 bulan"],
            ["blood_glucose_level", "Numerik (mg/dL)", "80 – 300", "Gula darah saat pengujian"],
            ["diabetes (target)", "Biner", "0 / 1", "Label kelas (8,82% positif)"],
        ],
        widths=[34, 30, 52, 54],
        fontsize=8.2,
    )

    doc.h3("b. Analisis Data (EDA)")
    doc.para(
        "Analisis awal memperlihatkan: (i) distribusi target sangat imbang — 8.482 positif "
        "(8,82%) vs 87.664 negatif (91,18%), rasio ≈ 10,3 : 1, sehingga metrik accuracy "
        "bersifat \"menipu\" (accuracy paradox); (ii) statistik deskriptif fitur numerik: "
        "age (mean 41,8; std 22,5), bmi (mean 27,3; std 6,8), HbA1c (mean 5,53; std 1,07), "
        "glukosa (mean 138,2; std 40,9); (iii) korelasi positif terbesar terhadap target "
        "datang dari HbA1c, glukosa darah, dan usia; (iv) proporsi hipertensi 7,8% dan "
        "penyakit jantung 4,1%."
    )
    doc.figure("fig_target_distribution.png",
               "Gambar 1. Distribusi kelas target (imbang: 91,18% : 8,82%).")
    doc.figure("fig_numeric_distributions.png",
               "Gambar 2. Distribusi fitur numerik menurut kelas target.")
    doc.figure("fig_correlation_heatmap.png",
               "Gambar 3. Korelasi antar fitur numerik dan target.")
    doc.figure("fig_categorical_distribution.png",
               "Gambar 4. Distribusi fitur kategorik terhadap kelas target.")

    doc.h3("c. Langkah-langkah Persiapan Data")
    doc.para("Sebelum data siap dilatih, dilakukan pipeline berikut (urutan penting):")
    doc.numbered([
        "Pembersihan (cleaning): deteksi duplikat sempurna — 3.854 baris duplikat dibuang "
        "sehingga tersisa 96.146 sampel (menghindari model menghafal sampel yang sama di "
        "train/test). Missing value diverifikasi secara eksplisit (pandas.isna): dataset ini "
        "berisi 0 missing value. Prosedur bila ada: imputasi median (numerik) / mode "
        "(kategorik) yang di-fit hanya pada data train.",
        "Pembagian data SEBELUM preprocessing: split 70 : 15 : 15 (train 67.302, "
        "validation 14.422, test 14.422) dengan stratify=y dan seed 42 agar proporsi "
        "positif terjaga di tiap partisi.",
        "Encoding kategori: OneHotEncoder (handle_unknown='ignore') untuk gender (3 "
        "kategori) dan smoking_history (6 kategori) → 9 one-hot; hypertension & "
        "heart_disease (biner 0/1) tetap numerik. Total 15 fitur model "
        "(6 numerik + 3 gender + 6 smoking).",
        "Normalisasi: StandardScaler (z-score, (x−μ)/σ) pada 6 fitur numerik. Dipilih "
        "z-score karena MLP + Batch Normalization tidak memerlukan rentang [0,1] dan "
        "z-score mempertahankan bentuk distribusi asli; skala fitur yang berbeda (usia "
        "hingga 80 vs HbA1c 3,5–9) disamakan agar gradien stabil.",
        "Pencegahan data leakage: seluruh transformer (scaler + encoder) di-FIT HANYA pada "
        "data train, lalu di-TRANSFORM ke validation & test — statistik train tidak pernah "
        "\"bocor\" ke data evaluasi.",
        "Penanganan class imbalance: pembobotan kelas balanced (weight kelas positif ≈ 5,67×) "
        "sehingga false negative — yang fatal secara klinis — dihukum lebih berat oleh loss. "
        "Oversampling SMOTENC (train only) juga diuji sebagai pembanding (Model C).",
    ])

    # ---------------- 1.2 ----------------
    doc.h2("1.2  Pemilihan Model dan Aturan Visualisasi")
    doc.h3("a. Pemilihan Arsitektur Deep Learning")
    doc.para(
        "Data bersifat tabular (15 fitur, n = 96.146) tanpa struktur spasial (→ tidak "
        "perlu CNN) maupun urutan temporal (→ tidak perlu RNN). Arsitektur yang sesuai "
        "adalah Multi-Layer Perceptron (feed-forward) — universal approximator untuk "
        "fungsi keputusan tabular. Dua arsitektur diusulkan dan dikompetisikan:"
    )
    doc.table(
        ["Aspek", "Model A (Opsi 1)", "Model B (Opsi 2) — terpilih", "Model C (Eksperimen)"],
        [
            ["Topologi",
             "15 → 64 → 32 → 1",
             "15 → 128 → 64 → 32 → 2",
             "= Model B"],
            ["Output", "1 neuron, sigmoid", "2 neuron, softmax", "2 neuron, softmax"],
            ["Loss", "binary_crossentropy", "categorical_crossentropy", "categorical_crossentropy"],
            ["Optimizer", "Adam, lr = 1e-3", "Adam, lr = 5e-4", "Adam, lr = 5e-4"],
            ["Regularisasi", "Dropout 0,30 / 0,20", "BatchNorm + Dropout 0,30 / 0,25",
             "BatchNorm + Dropout 0,30 / 0,25"],
            ["Imbalance", "class_weight balanced", "sample_weight balanced", "SMOTENC (train only)"],
        ],
        widths=[26, 38, 42, 38],
        fontsize=8.0,
    )
    doc.para(
        "Model terpilih: Model B — softmax 2 kelas. Alasan: (i) softmax memberi probabilitas "
        "ter-normalisasi kedua kelas sehingga ambang keputusan (threshold) dapat disesuaikan "
        "sesuai kebijakan klinis; (ii) Batch Normalization mempercepat konvergensi pada "
        "arsitektur yang lebih dalam; (iii) hasil empiris lebih baik (F1 0,8186 vs 0,8123 "
        "Model A, 0,8103 Model C — lihat Subbab 1.3). Arsitektur final:"
    )
    doc.figure("fig_architecture.png",
               "Gambar 5. Arsitektur Model B (MLP 15-128-64-32-2) yang terpilih.")

    doc.h3("b. Proses Pelatihan")
    doc.para(
        "Pelatihan Model B: batch size 1024, maksimum 60 epoch, EarlyStopping "
        "(monitor val_loss, patience 7, restore_best_weights) + ReduceLROnPlateau "
        "(factor 0,5, patience 3) untuk mencegah overfitting dan menyesuaikan laju belajar. "
        "Imbalance ditangani lewat sample_weight (positif ×5,67). Setelah konvergensi, "
        "ambang keputusan θ dituning pada data VALIDATION dengan memaksimalkan F1-Score "
        "pada grid θ ∈ [0,5–0,95] → θ* = 0,85. Nilai θ > 0,5 dipilih karena pada θ = 0,5 "
        "model terlalu \"liberal\" (recall 0,917 tetapi precision hanya 0,461 — separuh "
        "prediksi positif salah); menaikkan θ meningkatkan kepercayaan (precision) hasil "
        "positif dengan pengorbanan recall yang masih dapat diterima (0,706)."
    )
    doc.para(
        "Durasi pelatihan (diukur pada hardware pengembangan, 1 epoch ≈ 1,74 dtk untuk "
        "Model B): Model A berhenti dini pada epoch 59 (≈ 1,7 menit), Model B pada epoch 59 "
        "(≈ 1,7 menit), Model C pada epoch 35 (≈ 1,5 menit) — proses cepat karena arsitektur "
        "ringan dan batch besar; konvergensi terlihat dari penurunan val_loss dan plateau "
        "akurasi validasi pada Gambar 6."
    )

    doc.h3("c. Kepatuhan Aturan Visualisasi (ETS)")
    doc.para("Seluruh plot dalam laporan ini dibuat dengan ketentuan berikut:")
    doc.bullet([
        "Tema terang (light theme): matplotlib style \"whitegrid\" (latar putih, grid abu "
        "muda) — konsisten di semua figur.",
        "Sumbu waktu menggunakan NILAI MENIT, bukan indeks titik data/epoch: durasi satu "
        "epoch diukur (wall-clock, arsitektur & ukuran data identik, tanpa melatih ulang "
        "model produksi) — Model A 1,599 dtk/epoch, Model B 1,742 dtk/epoch, Model C "
        "2,504 dtk/epoch; posisi tiap epoch pada sumbu x = epoch × (detik/epoch) / 60.",
        "Tidak ada efek jitter pada plot apa pun (tidak digunakan stripplot/swarmplot "
        "bergoyang; plot kategorik memakai countplot, plot kurva memakai line plot murni).",
    ])
    doc.figure("fig_training_history.png",
               "Gambar 6. Kurva pelatihan (loss & akurasi) tiga model — sumbu waktu dalam "
               "menit, light theme, tanpa jitter.")
    doc.figure("fig_roc_curve.png",
               "Gambar 7. ROC curve tiga model pada test set (AUC ≈ 0,97).")
    doc.figure("fig_pr_curve.png",
               "Gambar 8. Precision–Recall curve (lebih informatif pada kelas imbang).")

    # ---------------- 1.3 ----------------
    doc.h2("1.3  Evaluasi Model — Matriks Konfusi dan Metrik Klinis")
    doc.h3("a. Matriks Konfusi sebagai Dasar Analisis")
    doc.para(
        "Matriks konfusi merangkum hasil prediksi pada test set (14.422 sampel, tidak pernah "
        "tersentuh saat training/tuning) dalam empat sel: True Positive (TP) — pasien "
        "diabetes yang terdeteksi; False Positive (FP) — pasien sehat yang dinyatakan "
        "berisiko (kecemasan + biaya rujuk tidak perlu); False Negative (FN) — pasien "
        "diabetes yang dilewatkan (terlambat ditangani, berisiko komplikasi); True Negative "
        "(TN) — pasien sehat yang benar dinyatakan sehat. Dari keempat sel itulah seluruh "
        "metrik diturunkan."
    )
    doc.figure("fig_confusion_matrix.png",
               "Gambar 9. Matriks konfusi Model B (θ* = 0,85) pada test set: "
               "TP = 898, FP = 24, FN = 374, TN = 13.126.")

    doc.h3("b. Metrik yang Diturunkan")
    doc.table(
        ["Metrik", "Rumus", "Nilai (Model B, θ* = 0,85)", "Interpretasi"],
        [
            ["Accuracy", "(TP+TN) / N", "0,9724", "97,24% keputusan keseluruhan benar"],
            ["Precision", "TP / (TP+FP)", "0,9740", "97,4% dari pasien yang dinyatakan \"Risiko\" "
             "memang benar berisiko"],
            ["Recall (Sensitivitas)", "TP / (TP+FN)", "0,7060", "70,6% pasien diabetes terdeteksi"],
            ["Specificity", "TN / (TN+FP)", "0,9982", "99,8% pasien sehat tidak disalah-satakan"],
            ["F1-Score", "2·P·R / (P+R)", "0,8186", "Kompromi precision–recall; dasar tuning θ*"],
            ["NPV", "TN / (TN+FN)", "0,9723", "Hasil negatif dapat diyakini"],
            ["ROC-AUC", "Luas di bawah ROC", "0,9737", "Kualitas ranking probabilitas (ambang-bebas)"],
            ["PR-AUC (AP)", "Luas di bawah PR", "0,8728", "Mutu deteksi kelas minoritas"],
        ],
        widths=[30, 30, 36, 54],
        fontsize=8.0,
    )
    doc.para(
        "Perbandingan tiga model pada ambang optimal (test set): Model A — accuracy 0,9709, "
        "precision 0,9410, recall 0,7146, F1 0,8123; Model B (terpilih) — accuracy 0,9724, "
        "precision 0,9740, recall 0,7060, F1 0,8186; Model C — accuracy 0,9714, precision "
        "0,9778, recall 0,6918, F1 0,8103."
    )

    doc.h3("c. Alasan Pemilihan Metrik dalam Konteks Diagnosis Medis")
    doc.bullet([
        "Accuracy TIDAK cukup sebagai metrik tunggal: dengan basis positif hanya 8,82%, "
        "model \"bodoh\" yang selalu memprediksi negatif sudah mencapai accuracy 0,9118 "
        "(accuracy paradox). Bukti nyata: pada θ = 0,5, Model B menghasilkan accuracy 0,8981 "
        "— justru LEBIH RENDAH dari garis dasar — karena FP membengkak. Oleh karena itu "
        "accuracy hanya dipakai sebagai pelengkap.",
        "Recall/Sensitivitas adalah metrik paling kritis untuk skrining medis: satu kasus "
        "diabetes yang dilewatkan (FN) berarti pasien kehilangan jendela penanganan dini; "
        "komplikasi (neuropati, nefropati, retinopati) berkembang tanpa gejala. Class "
        "weighting ×5,67 dirancang khusus untuk menekan FN. Nilai 0,706 di θ* = 0,85 adalah "
        "kompromi: menurunkan θ ke 0,5 menaikkan recall ke 0,917 tetapi meruntuhkan "
        "precision ke 0,461 — secara klinis tidak layak karena separuh hasil positif palsu.",
        "Precision mengukur kepercayaan hasil positif: dalam alur layanan, hasil \"Risiko "
        "Diabetes\" memicu rujukan tes lanjutan (OGTT/HbA1c lab) yang menelan biaya dan "
        "waktu. Precision 0,9740 berarti hampir semua alarm yang dibunyikan sistem sah — "
        "membebani tenaga medis dan pasien seminimal mungkin.",
        "Specificity 0,9982 menjamin pasien sehat nyaris tidak disalah-satakan positif, "
        "sehingga kepercayaan publik terhadap CDSS terjaga.",
        "F1-Score dipakai sebagai kriteria memilih θ* karena menyeimbangkan dua risiko "
        "tersebut secara kuantitatif; ROC-AUC menilai kualitas ranking probabilitas "
        "(0,9737 — sangat baik) dan PR-AUC (0,8728) lebih bermakna daripada ROC pada "
        "kelas imbang karena fokus pada kelas positif.",
        "Kebijakan klinis menentukan titik operasi akhir: untuk skrining populasi yang "
        "murah, θ dapat diturunkan (recall ↑); untuk diagnosis konfirmasi, θ dinaikkan "
        "(precision ↑). Aplikasi menampilkan θ* yang dipilih secara transparan sehingga "
        "praktisi dapat menyesuaikannya.",
    ])

    # ---------------- 1.4 ----------------
    doc.h2("1.4  Perancangan Antarmuka Pengguna (UI)")
    doc.para(
        "Aplikasi desktop dirancang sebagai CDSS dua panel dengan LIGHT THEME (palet "
        "terang: latar #F4F6FA, panel putih, teks gelap; merah/hijau hanya sebagai status "
        "semantik hasil). Panel kiri (Patient Information) menyediakan input MANUAL untuk "
        "keseluruhan 8 atribut dataset: 4 dropdown (Gender; Hypertension 0/1; Heart Disease "
        "0/1; Smoking History) dan 4 isian numerik (Age, BMI, HbA1c, Blood Glucose). Setiap "
        "input divalidasi secara klinis (rentang wajar, format angka — koma desimal "
        "diterima); input kosong/invalid ditolak dengan dialog pop-up. Panel kanan "
        "(Diabetes Diagnosis) adalah panel hasil: kotak status besar menampilkan teks "
        "prediksi \"Risiko Diabetes\" (merah) atau \"Tidak Berisiko Diabetes\" (hijau) "
        "sesuai ketentuan soal, disertai confidence score, probabilitas P(diabetes), "
        "ambang θ, daftar faktor risiko klinis yang terdeteksi, serta tombol Predict dan "
        "Reset. Disclaimers menegaskan aplikasi bersifat alat bantu, bukan diagnosis "
        "definitif."
    )
    doc.figure("fig_ui_mockup_idle.png",
               "Gambar 10. Mockup UI — kondisi awal (input default, status \"Menunggu "
               "prediksi…\").")
    doc.figure("fig_ui_mockup_risiko.png",
               "Gambar 11. Mockup UI — hasil prediksi \"Risiko Diabetes\" (pasien: Male, "
               "58 th, hipertensi, perokok aktif, BMI 32,4, HbA1c 7,8%, glukosa 210 mg/dL; "
               "output riil backend: P = 1,0000 ≥ θ = 0,85).")
    doc.figure("fig_ui_mockup_tidak_berisiko.png",
               "Gambar 12. Mockup UI — hasil prediksi \"Tidak Berisiko Diabetes\" (pasien: "
               "Female, 27 th, non-perokok, BMI 21,5, HbA1c 5,0%, glukosa 95 mg/dL; output "
               "riil backend: P = 0,0005 < θ = 0,85).")

    doc.h3("a. Implementasi Teknis UI")
    doc.bullet([
        "Framework: CustomTkinter (tampilan modern) dengan fallback otomatis ke Tkinter "
        "bawaan bila dependensi tidak tersedia — keduanya light theme dan berbagi satu "
        "logika backend.",
        "Inferensi real-time: model produksi (model.keras) + pipeline (preprocessor.pkl) "
        "dimuat saat aplikasi start; satu prediksi selesai dalam hitungan detik pada "
        "laptop biasa (CPU).",
        "Uji cepat tanpa GUI: python src/app.py --selftest (dua pasien contoh) dan "
        "python src/test_backend.py (12 skema uji validasi & inferensi).",
    ])
    doc.code(
        "# Menjalankan aplikasi desktop\n"
        "pip install -r requirements.txt\n"
        "python src/app.py\n\n"
        "# Verifikasi cepat backend (tanpa GUI)\n"
        "python src/app.py --selftest"
    )
    doc.para(
        "Jalur data dalam aplikasi: form (8 input) → validasi rentang klinis → "
        "ColumnTransformer (identik dengan saat training) → model.keras → probabilitas → "
        "banding θ* = 0,85 → teks hasil + confidence + faktor risiko. Dengan arsitektur "
        "ini UI dapat diperluas (riwayat pasien, ekspor PDF hasil, grafik tren HbA1c) "
        "tanpa mengubah inti model."
    )

    # ---------------- KESIMPULAN ----------------
    doc.chapter("KESIMPULAN")
    doc.bullet([
        "Dataset 100.000 rekam medis (8 fitur + target) dikaji lalu dipersiapkan: 3.854 "
        "duplikat dibuang, 0 missing value, one-hot encoding, StandardScaler (fit hanya "
        "pada train, tanpa leakage), split stratified 70:15:15, dan class weighting untuk "
        "imbalance 10,3:1.",
        "Model deep learning yang diusulkan dan terpilih adalah MLP 15-128-64-32-2 "
        "(BatchNorm + Dropout, softmax, CCE, Adam) dengan EarlyStopping + ReduceLROnPlateau; "
        "ambang keputusan θ* = 0,85 dituning dari F1 pada data validasi.",
        "Evaluasi berbasis matriks konfusi menurunkan 8 metrik (accuracy, precision, recall, "
        "specificity, F1, NPV, ROC-AUC, PR-AUC); pemilihan metrik dipertanggungjawabkan "
        "secara klinis — recall dijaga tinggi untuk meminimalkan kasus terlewat, precision "
        "tinggi untuk meminimalkan alarm palsu, dan accuracy tidak dijadikan metrik tunggal "
        "karena accuracy paradox.",
        "UI desktop light theme dengan input manual 8 atribut dan panel hasil berteks "
        "\"Risiko Diabetes\" / \"Tidak Berisiko Diabetes\" telah direalisasikan (src/app.py) "
        "dan siap didemokan; semua plot mematuhi aturan visualisasi ETS (light theme, sumbu "
        "waktu dalam menit, tanpa jitter).",
    ])

    # ---------------- REFERENSI ----------------
    doc.chapter("DAFTAR PUSTAKA")
    refs = [
        "Kaggle — I. Mustafaz. (2023). Diabetes Prediction Dataset. "
        "https://www.kaggle.com/datasets/iammustafatz/diabetes-prediction-dataset",
        "Abadi, M., et al. (2016). TensorFlow: Large-Scale Machine Learning on "
        "Heterogeneous Systems. arXiv:1603.04467.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. "
        "JMLR 12, 2825–2830.",
        "American Diabetes Association. (2024). 2. Classification and Diagnosis of "
        "Diabetes: Standards of Care in Diabetes. Diabetes Care 47(Supplement 1).",
        "Chollet, F. (2017). Deep Learning with Python. Manning Publications.",
        "Departemen Teknik Elektro FTEIC ITS. (2026). Soal Evaluasi Tengah Semester — "
        "Dasar Sistem Elektronika Cerdas, Semester Gasal 2026/2027.",
    ]
    for i, r in enumerate(refs, 1):
        doc.set_font("DejaVu", "", 9.5)
        doc.set_text_color(30, 32, 40)
        doc.cell(7, 5.6, f"[{i}]")
        doc.multi_cell(doc.w - doc.l_margin - doc.r_margin - 7, 5.6, r,
                       align="L", new_x="LMARGIN", new_y="NEXT")
        doc.ln(1)

    doc.output(str(OUT))
    print(f"✔ Laporan ETS tersimpan: {OUT} "
          f"({OUT.stat().st_size // 1024} KB, {doc.page_no()} halaman)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nama", default="................................")
    ap.add_argument("--nrp", default="07................................")
    args = ap.parse_args()
    build(args.nama, args.nrp)


if __name__ == "__main__":
    main()
