# Kalkulator Merit SPM & Padanan Kursus UPU

A single-page web app that calculates a student's SPM merit score and lists eligible UPU Category A (SPM 2026) programs based on their grades and subject stream.

## Features

- **Merit calculation** — automatically selects the 2 best Pilihan subjects and up to 2 best Tambahan subjects for maximum merit
- **Stream classification** — auto-detects STEM A / STEM B / STEM C / KSI based on subjects taken
- **Course matching** — filters eligible UPU Category A programs by merit threshold, stream (Pakej), and per-subject grade requirements
- **Filters** — toggle display of Bumiputera-only and interview-required programs
- **Expandable details** — shows Syarat Khas, duration, and field of study for each program
- **No build step** — runs entirely in the browser; no server needed

## Usage

Open `index.html` directly in a browser. No installation required.

```
index.html        # main app (React + Tailwind, loaded via CDN)
programs_data.js  # UPU program data (loaded as a global JS variable)
```

Both files must be in the same directory.

## Merit Formula

| Component | Weight | Max Score |
|-----------|--------|-----------|
| Wajib (BM, BI, Math, Sejarah) | 10 pts each | 40 |
| Pilihan (best 2 from stream pool) | 15 pts each | 30 |
| Tambahan (best 2 remaining) | 5 pts each | 10 |
| Ko-Kurikulum | 0–10 | 10 |
| **Total Merit** | | **100** |

Academic score is normalized: `(academic / 80) * 90 + koko`

Grade weights: A+ = 18, A = 16, A- = 14, B+ = 12, B = 10, C+ = 8, C = 6, D = 4, E = 2, G = 0

## Stream Classification

| Stream | Criteria |
|--------|----------|
| STEM A | All 4 core: Biologi, Fizik, Kimia, Matematik Tambahan |
| STEM B | At least 2 of (Bio/Fizik/Kimia) + any STEM B elective |
| STEM C | At least 2 STEM C1 subjects OR at least 1 STEM C2 (vocational) subject |
| KSI | All other combinations (Kemanusiaan / Sastera / Ikhtisas) |

## Tech Stack

- React 18 (UMD via unpkg)
- Tailwind CSS (CDN)
- Babel Standalone (JSX in-browser compilation)
- Vanilla JavaScript — no bundler, no Node.js

## Data Source

Program data is based on the UPU Category A (SPM) 2026 list published by Unit Pusat Universiti.

## License

MIT
