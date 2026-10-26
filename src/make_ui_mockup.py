#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 UI MOCKUP — mockup antarmuka desktop (Pillow) untuk laporan ETS
================================================================================
 Menggambarkan tampilan `src/app.py` (light theme) dalam 3 keadaan:
   1. fig_ui_mockup_idle.png            — kondisi awal ("Menunggu prediksi…")
   2. fig_ui_mockup_risiko.png          — hasil "Risiko Diabetes" (merah)
   3. fig_ui_mockup_tidak_berisiko.png  — hasil "Tidak Berisiko Diabetes" (hijau)

 Nilai P/confidence pada mockup hasil adalah LUASAN RIIL backend
 (src/app.py --selftest), bukan angka fiktif.

 Jalankan :  .venv/bin/python src/make_ui_mockup.py
================================================================================
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

S = 2  # skala render (2x agar tajam saat dicetak/dimasukkan PDF)

# Palet — identik dengan PALETTE di src/app.py
BG        = "#F4F6FA"
PANEL     = "#FFFFFF"
HEADER    = "#2F6FED"
HEADER_SUB= "#DCE7FB"
TEXT      = "#1F2937"
MUTED     = "#6B7280"
IDLE      = "#E8ECF3"
IDLE_TEXT = "#374151"
BORDER    = "#C9D2E0"
PANEL_BD  = "#E1E6EF"
ACCENT    = "#2F6FED"
ACCENT_H  = "#1F55C4"
BTN_IDLE  = "#D8DEE9"
FLAG      = "#B45309"
RED       = "#D64545"
GREEN     = "#2E9E5B"

W, H = 1060, 680
W2, H2 = W * S, H * S


def _fonts() -> dict:
    from matplotlib import get_data_path
    base = Path(get_data_path()) / "fonts" / "ttf"
    def f(name, px):
        return ImageFont.truetype(str(base / name), px * S)
    return {
        "title":    f("DejaVuSans-Bold.ttf", 22),
        "subtitle": f("DejaVuSans.ttf", 12),
        "panel":    f("DejaVuSans-Bold.ttf", 18),
        "desc":     f("DejaVuSans.ttf", 12),
        "label":    f("DejaVuSans.ttf", 13),
        "value":    f("DejaVuSans.ttf", 13),
        "status":   f("DejaVuSans-Bold.ttf", 24),
        "conf":     f("DejaVuSans-Bold.ttf", 16),
        "prob":     f("DejaVuSans.ttf", 13),
        "flag":     f("DejaVuSans.ttf", 12),
        "btn":      f("DejaVuSans-Bold.ttf", 16),
        "note":     f("DejaVuSans.ttf", 11),
        "bar":      f("DejaVuSans.ttf", 11),
        "win":      f("DejaVuSans.ttf", 12),
    }


def s(v: float) -> int:
    return int(v * S)


def draw_window(F: dict, state: str) -> Image.Image:
    img = Image.new("RGB", (W2, H2), BG)
    d = ImageDraw.Draw(img)

    def rrect(x, y, x2, y2, fill, outline=None, radius=8, width=1):
        d.rounded_rectangle([s(x), s(y), s(x2), s(y2)], radius=s(radius),
                            fill=fill, outline=outline, width=s(width))

    def text(x, y, str, font, fill):
        d.text((s(x), s(y)), str, font=font, fill=fill)

    def text_c(cx, cy, str, font, fill):
        b = d.textbbox((0, 0), str, font=font)
        w, h = (b[2] - b[0]) / S, (b[3] - b[1]) / S
        d.text((s(cx - w / 2), s(cy - h / 2 - b[1] / S)), str, font=font, fill=fill)

    # ---------- title bar window ----------
    rrect(0, 0, W, 34, fill="#E8ECF3", radius=0)
    for i, c in enumerate(("#F26D6D", "#F5C26B", "#6BCB77")):
        d.ellipse([s(14 + i * 22), s(13), s(22 + i * 22), s(21)], fill=c)
    text_c(W / 2, 17, "Diabetes Prediction System — Sistem Prediksi Diabetes",
           F["win"], MUTED)

    # ---------- header ----------
    rrect(0, 34, W, 106, fill=HEADER, radius=0)
    # ikon stetoskop sederhana (lingkaran + tabung)
    d.ellipse([s(22), s(52), s(46), s(76)], outline="#FFFFFF", width=s(3))
    d.arc([s(30), s(66), s(54), s(90)], 0, 90, fill="#FFFFFF", width=s(3))
    d.line([s(40), s(74), s(46), s(88)], fill="#FFFFFF", width=s(3))
    text(58, 46, "DIABETES PREDICTION SYSTEM", F["title"], "#FFFFFF")
    text(58, 76, "Clinical Decision Support System · Custom Deep Neural Network · "
                 "Elektronika Cerdas FTEIC ITS", F["subtitle"], HEADER_SUB)

    # ---------- panel kiri ----------
    LX0, LY0, LX1, LY1 = 18, 122, 548, 650
    rrect(LX0, LY0, LX1, LY1, fill=PANEL, outline=PANEL_BD, radius=14, width=1)
    # ikon pasien
    d.ellipse([s(38), s(138), s(54), s(154)], outline=ACCENT, width=s(3))
    d.arc([s(33), s(158), s(59), s(184)], 180, 360, fill=ACCENT, width=s(3))
    text(66, 136, "Patient Information", F["panel"], TEXT)
    text(40, 168, "Lengkapi 8 data klinis pasien, lalu tekan Predict.", F["desc"], MUTED)

    if state == "idle":
        form = {"gender": "Female", "hypertension": "0", "heart_disease": "0",
                "smoking_history": "never", "age": "30", "bmi": "25.0",
                "HbA1c_level": "5.5", "blood_glucose_level": "110"}
    elif state == "risiko":
        form = {"gender": "Male", "hypertension": "1", "heart_disease": "0",
                "smoking_history": "current", "age": "58", "bmi": "32.4",
                "HbA1c_level": "7.8", "blood_glucose_level": "210"}
    else:  # tidak_berisiko
        form = {"gender": "Female", "hypertension": "0", "heart_disease": "0",
                "smoking_history": "never", "age": "27", "bmi": "21.5",
                "HbA1c_level": "5.0", "blood_glucose_level": "95"}

    rows = [
        ("Gender", "combo"), ("Hypertension", "combo"), ("Heart Disease", "combo"),
        ("Smoking History", "combo"),
        ("Age (tahun)", "entry"), ("BMI (kg/m²)", "entry"),
        ("HbA1c Level (%)", "entry"), ("Blood Glucose (mg/dL)", "entry"),
    ]
    y = 196
    for label, kind in rows:
        text(40, y + 6, label, F["label"], TEXT)
        wx0, wx1, wy0, wy1 = 252, 524, y, y + 30
        rrect(wx0, wy0, wx1, wy1, fill="#FFFFFF", outline=BORDER, radius=6, width=1)
        key = {"Gender": "gender", "Hypertension": "hypertension",
               "Heart Disease": "heart_disease", "Smoking History": "smoking_history",
               "Age (tahun)": "age", "BMI (kg/m²)": "bmi",
               "HbA1c Level (%)": "HbA1c_level",
               "Blood Glucose (mg/dL)": "blood_glucose_level"}[label]
        text(wx0 + 10, y + 7, form[key], F["value"], TEXT)
        if kind == "combo":
            d.polygon([(s(wx1 - 22), s(y + 12)), (s(wx1 - 14), s(y + 12)),
                       (s(wx1 - 18), s(y + 18))], fill=MUTED)
        y += 44

    # ---------- panel kanan ----------
    RX0, RY0, RX1, RY1 = 562, 122, 1042, 650
    rrect(RX0, RY0, RX1, RY1, fill=PANEL, outline=PANEL_BD, radius=14, width=1)
    # ikon clipboard (panel kanan: offset +544 dari panel kiri)
    d.rounded_rectangle([s(582), s(140), s(600), s(164)], radius=s(3),
                        outline=ACCENT, width=s(3))
    d.rounded_rectangle([s(586), s(136), s(596), s(144)], radius=s(2),
                        fill=ACCENT)
    text(610, 136, "Diabetes Diagnosis", F["panel"], TEXT)

    # kotak status hasil
    SX0, SY0, SX1, SY1 = 584, 182, 1020, 268
    if state == "idle":
        st_fill, st_txt, st_str = IDLE, IDLE_TEXT, "Menunggu prediksi…"
    elif state == "risiko":
        st_fill, st_txt, st_str = RED, "#FFFFFF", "✚  Risiko Diabetes"
    else:
        st_fill, st_txt, st_str = GREEN, "#FFFFFF", "✔  Tidak Berisiko Diabetes"
    rrect(SX0, SY0, SX1, SY1, fill=st_fill, radius=14)
    text_c((SX0 + SX1) / 2, (SY0 + SY1) / 2, st_str, F["status"], st_txt)

    if state == "idle":
        text(584, 288, "Confidence: —", F["conf"], TEXT)
        text(584, 316, "P(diabetes) = —", F["prob"], MUTED)
    elif state == "risiko":
        text(584, 288, "Confidence: 100.0%  (P = 1.000)", F["conf"], TEXT)
        text(584, 316, "P(diabetes) = 1.0000   |   ambang θ = 0.85   "
                       "→   hasil: Risiko Diabetes", F["prob"], MUTED)
        flags = ["⚠ Faktor risiko terdeteksi:",
                 "•  HbA1c 7.8% ≥ 6.5% (ambang diagnostik diabetes, ADA).",
                 "•  Glukosa darah 210 mg/dL ≥ 200 mg/dL (hiperglikemia).",
                 "•  BMI 32.4 kg/m² ≥ 30 (obesitas).",
                 "•  Riwayat hipertensi."]
        fy = 348
        for fline in flags:
            text(584, fy, fline, F["flag"], FLAG)
            fy += 20
    else:
        text(584, 288, "Confidence: 100.0%  (P = 0.000)", F["conf"], TEXT)
        text(584, 316, "P(diabetes) = 0.0005   |   ambang θ = 0.85   "
                       "→   hasil: Tidak Berisiko Diabetes", F["prob"], MUTED)

    # tombol
    BY = 468
    rrect(584, BY, 756, BY + 44, fill=ACCENT, radius=8)
    text_c((584 + 756) / 2, BY + 22, "Predict", F["btn"], "#FFFFFF")
    rrect(774, BY, 894, BY + 44, fill=BTN_IDLE, radius=8)
    text_c((774 + 894) / 2, BY + 22, "Reset", F["btn"], IDLE_TEXT)

    # catatan
    text_c((RX0 + RX1) / 2, 596, "Aplikasi ini adalah alat bantu edukasi & pendukung keputusan.",
           F["note"], MUTED)
    text_c((RX0 + RX1) / 2, 614, "Diagnosis definitif tetap harus dilakukan oleh tenaga medis.",
           F["note"], MUTED)

    # ---------- status bar ----------
    text(24, 660,
         "Model termuat: Model B (Softmax)   |   Ambang keputusan θ = 0.85   |   "
         "Engine: TensorFlow 2.21.0   |   Artefak: artifacts/",
         F["bar"], MUTED)

    return img


def main() -> None:
    F = _fonts()
    for state, fname in [
        ("idle", "fig_ui_mockup_idle.png"),
        ("risiko", "fig_ui_mockup_risiko.png"),
        ("tidak_berisiko", "fig_ui_mockup_tidak_berisiko.png"),
    ]:
        img = draw_window(F, state)
        p = OUT_DIR / fname
        img.save(p)
        print(f"✔ {p}  ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
