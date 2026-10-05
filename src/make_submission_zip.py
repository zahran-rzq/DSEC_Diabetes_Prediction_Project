#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pembuat berkas pengumpulan MyITS Classroom.
Contoh:  python src/make_submission_zip.py --nama "Zahran Rizqi" --nrp 0712345678
Hasil  : TugasProyek_EC_ZahranRizqi_0712345678.zip
"""
import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INCLUDE = [
    # Fase I — source code & artefak
    "src/diabetes_model_development.ipynb",
    "src/app.py",
    "src/test_backend.py",
    "artifacts/model.keras",
    "artifacts/preprocessor.pkl",
    "artifacts/training_history.json",
    # Fase laporan & dokumen
    "laporan/Laporan_Teknis_Prediksi_Diabetes.pdf",
    "README.md",
    "requirements.txt",
    "diabetes_prediction_dataset.csv",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nama", default="NamaLengkap", help='Nama lengkap, mis. "Budi Santoso"')
    ap.add_argument("--nrp", default="NRP", help="NRP mahasiswa")
    args = ap.parse_args()

    nama = "".join(args.nama.split()) or "NamaLengkap"
    out = ROOT / f"TugasProyek_EC_{nama}_{args.nrp}.zip"

    missing = [p for p in INCLUDE if not (ROOT / p).exists()]
    if missing:
        raise SystemExit("File berikut belum ada (jalankan notebook dahulu):\n  " +
                         "\n  ".join(missing))

    # figur evaluasi ikut disertakan sebagai lampiran visual
    fig_dir = ROOT / "assets" / "figures"
    extra = [p.relative_to(ROOT).as_posix() for p in sorted(fig_dir.glob("*.png"))]

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in INCLUDE + extra:
            z.write(ROOT / rel, f"{out.stem}/{rel}")

    print(f"✔ Berkas pengumpulan dibuat: {out}")
    print(f"  ukuran: {out.stat().st_size / 1e6:.2f} MB — berisi {len(INCLUDE) + len(extra)} berkas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
