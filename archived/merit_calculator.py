"""
SPM Merit Calculator
Formula: Merit = ((Jumlah / 80) * 90) + Ko_Kurikulum

Jumlah breakdown (max 80):
  Wajib    (40%): 4 subjects x 10 pts each  -> BM, BI, Matematik, Sejarah
  Pilihan  (30%): 2 subjects x 15 pts each  -> best 2 from student's aliran pool
  Tambahan (10%): 2 subjects x  5 pts each  -> best 2 remaining subjects
"""

GRED_MARKS: dict[str, int] = {
    'A+': 18, 'A': 16, 'A-': 14,
    'B+': 12, 'B': 10,
    'C+': 8,  'C': 6,
    'D':  4,  'E': 2, 'G': 0,
}

GRADE_ORDER = ['A+', 'A', 'A-', 'B+', 'B', 'C+', 'C', 'D', 'E', 'G']

SUBJEK_WAJIB = {'Bahasa Melayu', 'Bahasa Inggeris', 'Matematik', 'Sejarah'}

# Pilihan pool per aliran - student picks BEST 2 from subjects they actually took
PILIHAN_POOL: dict[str, list[str]] = {
    'STEM_A': [
        'Biologi', 'Fizik', 'Kimia', 'Matematik Tambahan',
    ],
    'STEM_B': [
        'Biologi', 'Fizik', 'Kimia',
        'Sains Tambahan', 'Grafik Komunikasi Teknikal', 'Asas Kelestarian',
        'Pertanian', 'Sains Rumah Tangga', 'Reka Cipta',
    ],
    'STEM_C': [
        'Sains Tambahan', 'Grafik Komunikasi Teknikal', 'Asas Kelestarian',
        'Pertanian', 'Sains Rumah Tangga', 'Reka Cipta', 'Sains Komputer',
        'Sains Sukan', 'Pengajian Kejuruteraan Awam',
        'Pengajian Kejuruteraan Mekanikal',
        'Pengajian Kejuruteraan Elektrik & Elektronik', 'Lukisan Kejuruteraan',
        'Produksi Reka Tanda', 'Hiasan Dalaman', 'Kerja Paip Domestik',
        'Pembinaan Domestik', 'Pembuatan Perabot', 'Reka Bentuk Grafik Digital',
        'Produksi Multimedia', 'Katering dan Penyajian', 'Pemprosesan Makanan',
        'Rekaan dan Jahitan Pakaian', 'Penggayaan Rambut',
        'Asuhan dan Pendidikan Awal Kanak-Kanak', 'Geomatik',
        'Pendawaian Domestik', 'Menservis Peralatan Elektrik Domestik',
        'Menservis Automobil', 'Kimpalan Arka dan Gas', 'Menservis Motosikal',
        'Menservis Peralatan Penyejukan dan Penyaman Udara',
        'Landskap dan Nurseri', 'Tanaman Makanan', 'Akuakultur dan Haiwan Rekreasi',
    ],
    # KSI pilihan = everything NOT in wajib and NOT in any STEM pool
    # handled dynamically in _pilihan_pool_for_ksi()
}

# All STEM subjects (union of all STEM pools)
SEMUA_STEM = set(PILIHAN_POOL['STEM_A']) | set(PILIHAN_POOL['STEM_B']) | set(PILIHAN_POOL['STEM_C'])


def _pilihan_pool_ksi(semua_subjek: set[str]) -> list[str]:
    """KSI pilihan pool = all non-wajib, non-STEM subjects the student took."""
    return [s for s in semua_subjek if s not in SUBJEK_WAJIB and s not in SEMUA_STEM]


def gred_ke_markah(gred: str) -> int:
    return GRED_MARKS.get(gred.strip(), 0)


def memenuhi_gred(dimiliki: str, diperlukan: str) -> bool:
    """True if student's grade meets or exceeds the required grade."""
    if not diperlukan:
        return True
    if not dimiliki:
        return False
    try:
        return GRADE_ORDER.index(dimiliki) <= GRADE_ORDER.index(diperlukan)
    except ValueError:
        return False


def klasifikasi_pakej(subjek_diambil: set[str]) -> str:
    """
    Classify student into stream pakej based on subjects taken.
    Returns: 'STEM_A', 'STEM_B', 'STEM_C', or 'KSI'
    """
    STEM_A_CORE = {'Biologi', 'Fizik', 'Kimia', 'Matematik Tambahan'}
    STEM_B_EXTRA = {
        'Sains Tambahan', 'Grafik Komunikasi Teknikal', 'Asas Kelestarian',
        'Pertanian', 'Sains Rumah Tangga', 'Reka Cipta',
    }
    STEM_C1 = {
        'Sains Tambahan', 'Grafik Komunikasi Teknikal', 'Asas Kelestarian',
        'Pertanian', 'Sains Rumah Tangga', 'Reka Cipta', 'Sains Komputer',
        'Sains Sukan', 'Pengajian Kejuruteraan Awam',
        'Pengajian Kejuruteraan Mekanikal',
        'Pengajian Kejuruteraan Elektrik & Elektronik', 'Lukisan Kejuruteraan',
    }
    STEM_C2 = {
        'Produksi Reka Tanda', 'Hiasan Dalaman', 'Kerja Paip Domestik',
        'Pembinaan Domestik', 'Pembuatan Perabot', 'Reka Bentuk Grafik Digital',
        'Produksi Multimedia', 'Katering dan Penyajian', 'Pemprosesan Makanan',
        'Rekaan dan Jahitan Pakaian', 'Penggayaan Rambut',
        'Asuhan dan Pendidikan Awal Kanak-Kanak', 'Geomatik',
        'Pendawaian Domestik', 'Menservis Peralatan Elektrik Domestik',
        'Menservis Automobil', 'Kimpalan Arka dan Gas', 'Menservis Motosikal',
        'Menservis Peralatan Penyejukan dan Penyaman Udara',
        'Landskap dan Nurseri', 'Tanaman Makanan', 'Akuakultur dan Haiwan Rekreasi',
    }
    BIO_FIZIK_KIMIA = {'Biologi', 'Fizik', 'Kimia'}

    if STEM_A_CORE.issubset(subjek_diambil):
        return 'STEM_A'

    bfk_count = len(subjek_diambil & BIO_FIZIK_KIMIA)
    if bfk_count >= 2 and bool(subjek_diambil & STEM_B_EXTRA):
        return 'STEM_B'

    c1_count = len(subjek_diambil & STEM_C1)
    c2_count = len(subjek_diambil & STEM_C2)
    if c1_count >= 2 or c2_count >= 1:
        return 'STEM_C'

    return 'KSI'


def hitung_merit(
    semua_gred: dict[str, str],
    ko_kurikulum: float,
    pakej: str | None = None,
) -> dict:
    """
    Calculate SPM merit score.

    Automatically selects the best 2 pilihan and best 2 tambahan subjects
    based on the student's aliran (pakej).

    Args:
        semua_gred: {subject_name: grade} for ALL subjects the student took,
                    including wajib (BM, BI, Matematik, Sejarah)
        ko_kurikulum: co-curriculum score 0.00 - 10.00
        pakej: 'STEM_A', 'STEM_B', 'STEM_C', 'KSI', or None to auto-detect

    Returns:
        dict with merit, breakdown, selected subjects
    """
    if not (0.0 <= ko_kurikulum <= 10.0):
        raise ValueError("Ko-kurikulum mesti antara 0.00 dan 10.00")

    # Auto-detect pakej if not provided
    if pakej is None:
        pakej = klasifikasi_pakej(set(semua_gred.keys()))

    # --- Wajib subjects (fixed 4) ---
    wajib_gred = {s: semua_gred.get(s, 'G') for s in SUBJEK_WAJIB}
    skor_wajib = sum((gred_ke_markah(g) / 18) * 10 for g in wajib_gred.values())

    # --- Pilihan subjects: best 2 from the aliran pool ---
    if pakej == 'KSI':
        pool = _pilihan_pool_ksi(set(semua_gred.keys()))
    else:
        pool = PILIHAN_POOL.get(pakej, [])

    # Filter to subjects the student actually took, sort by marks desc
    pool_diambil = [s for s in pool if s in semua_gred]
    pool_diambil.sort(key=lambda s: gred_ke_markah(semua_gred[s]), reverse=True)
    pilihan_terpilih = pool_diambil[:2]

    skor_pilihan = sum((gred_ke_markah(semua_gred[s]) / 18) * 15 for s in pilihan_terpilih)

    # --- Tambahan subjects: best 2 from remaining non-wajib, non-pilihan ---
    dikecualikan = SUBJEK_WAJIB | set(pilihan_terpilih)
    tambahan_calon = [
        s for s in semua_gred
        if s not in dikecualikan
    ]
    tambahan_calon.sort(key=lambda s: gred_ke_markah(semua_gred[s]), reverse=True)
    tambahan_terpilih = tambahan_calon[:2]

    skor_tambahan = sum((gred_ke_markah(semua_gred[s]) / 18) * 5 for s in tambahan_terpilih)

    # --- Final merit ---
    jumlah = skor_wajib + skor_pilihan + skor_tambahan
    merit = (jumlah / 80) * 90 + ko_kurikulum

    return {
        'merit': round(merit, 2),
        'pakej': pakej,
        'wajib': {s: wajib_gred[s] for s in SUBJEK_WAJIB},
        'pilihan_terpilih': {s: semua_gred[s] for s in pilihan_terpilih},
        'tambahan_terpilih': {s: semua_gred[s] for s in tambahan_terpilih},
        'ko_kurikulum': ko_kurikulum,
        'skor_wajib': round(skor_wajib, 4),
        'skor_pilihan': round(skor_pilihan, 4),
        'skor_tambahan': round(skor_tambahan, 4),
        'jumlah': round(jumlah, 4),
    }


def semak_layak(student_gred: dict[str, str], program: dict) -> dict:
    """
    Check if a student is eligible for a program.

    Args:
        student_gred: {subject_name: grade} for ALL subjects student took
        program: a row from program_pengajian_cleaned.csv as dict

    Returns:
        dict with keys: layak (bool), sebab_gagal (list), merit_min (float)
    """
    sebab_gagal = []

    req_cols = {
        'Req_BM': 'Bahasa Melayu',
        'Req_BI': 'Bahasa Inggeris',
        'Req_Sejarah': 'Sejarah',
        'Req_Math': 'Matematik',
        'Req_AddMath': 'Matematik Tambahan',
        'Req_Fizik': 'Fizik',
        'Req_Kimia': 'Kimia',
        'Req_Bio': 'Biologi',
        'Req_Sains': 'Sains',
        'Req_PI': 'Pendidikan Islam',
        'Req_BahasaArab': 'Bahasa Arab',
    }

    # Check mandatory subjects
    for col, subj in req_cols.items():
        req_gred = program.get(col, '')
        if req_gred:
            gred_student = student_gred.get(subj, '')
            if not memenuhi_gred(gred_student, req_gred):
                sebab_gagal.append(
                    f"{subj}: perlukan Gred {req_gred}, "
                    f"dimiliki '{gred_student or 'tiada'}'"
                )

    # Check choice groups
    dikira = set()
    for col, subj in req_cols.items():
        if program.get(col):
            dikira.add(subj)

    for n in range(1, 9):
        gred_req = program.get(f'Pilihan_{n}_Gred', '')
        bil = program.get(f'Pilihan_{n}_Bil', '')
        subjek_str = program.get(f'Pilihan_{n}_Subjek', '')
        if not (gred_req and bil and subjek_str):
            continue

        bil = int(bil)
        subjek_list = subjek_str.split('|')
        lulus = [
            s for s in subjek_list
            if memenuhi_gred(student_gred.get(s, ''), gred_req)
        ]
        dikira.update(subjek_list)

        if len(lulus) < bil:
            ringkas = ', '.join(subjek_list[:3])
            if len(subjek_list) > 3:
                ringkas += f' (+{len(subjek_list)-3} lagi)'
            sebab_gagal.append(
                f"Pilihan {n}: perlukan Gred {gred_req} dalam {bil} daripada "
                f"[{ringkas}], hanya memenuhi {len(lulus)}/{bil}"
            )

    # Check remaining subjects requirement
    lain_gred = program.get('Lain_Gred', '')
    lain_bil = program.get('Lain_Bil', '')
    if lain_gred and lain_bil:
        lain_bil = int(lain_bil)
        lulus_lain = [
            s for s, g in student_gred.items()
            if s not in dikira and memenuhi_gred(g, lain_gred)
        ]
        if len(lulus_lain) < lain_bil:
            sebab_gagal.append(
                f"Subjek lain: perlukan Gred {lain_gred} dalam {lain_bil} subjek "
                f"tambahan, hanya memenuhi {len(lulus_lain)}/{lain_bil}"
            )

    return {
        'layak': len(sebab_gagal) == 0,
        'sebab_gagal': sebab_gagal,
        'merit_min': float(program.get('Merit', 0) or 0),
    }


# Self-test
if __name__ == '__main__':
    print("=== Merit Calculator Self-Test ===\n")

    # STEM A student - all A+
    r = hitung_merit({
        'Bahasa Melayu':'A+','Bahasa Inggeris':'A+','Matematik':'A+','Sejarah':'A+',
        'Biologi':'A+','Fizik':'A+','Kimia':'A+','Matematik Tambahan':'A+',
    }, ko_kurikulum=10.0)
    print(f"STEM A, all A+, ko=10 -> Merit: {r['merit']} (expected 100.0)")
    print(f"  Pakej: {r['pakej']}")
    print(f"  Pilihan: {r['pilihan_terpilih']}")
    print(f"  Tambahan: {r['tambahan_terpilih']}\n")

    # STEM A student - realistic grades
    r = hitung_merit({
        'Bahasa Melayu':'B','Bahasa Inggeris':'B+','Matematik':'A','Sejarah':'C',
        'Biologi':'A-','Fizik':'B','Kimia':'B+','Matematik Tambahan':'A-',
    }, ko_kurikulum=8.5)
    print(f"STEM A, realistic -> Merit: {r['merit']}")
    print(f"  Pilihan terpilih (best 2): {r['pilihan_terpilih']}")
    print(f"  Tambahan terpilih: {r['tambahan_terpilih']}\n")

    # STEM B student
    r = hitung_merit({
        'Bahasa Melayu':'A','Bahasa Inggeris':'B+','Matematik':'A-','Sejarah':'B',
        'Biologi':'A','Fizik':'B+','Sains Tambahan':'A-','Pertanian':'C',
    }, ko_kurikulum=7.0)
    print(f"STEM B -> Merit: {r['merit']}, Pakej: {r['pakej']}")
    print(f"  Pilihan: {r['pilihan_terpilih']}")
    print(f"  Tambahan: {r['tambahan_terpilih']}\n")

    # STEM C student
    r = hitung_merit({
        'Bahasa Melayu':'B','Bahasa Inggeris':'C+','Matematik':'B','Sejarah':'B',
        'Sains Komputer':'A','Reka Cipta':'B+','Grafik Komunikasi Teknikal':'C',
    }, ko_kurikulum=6.0)
    print(f"STEM C -> Merit: {r['merit']}, Pakej: {r['pakej']}")
    print(f"  Pilihan: {r['pilihan_terpilih']}")
    print(f"  Tambahan: {r['tambahan_terpilih']}\n")

    # KSI student
    r = hitung_merit({
        'Bahasa Melayu':'A','Bahasa Inggeris':'A-','Matematik':'B+','Sejarah':'A',
        'Ekonomi':'A-','Prinsip Perakaunan':'B+','Perniagaan':'B','Geografi':'C',
    }, ko_kurikulum=9.0)
    print(f"KSI -> Merit: {r['merit']}, Pakej: {r['pakej']}")
    print(f"  Pilihan: {r['pilihan_terpilih']}")
    print(f"  Tambahan: {r['tambahan_terpilih']}\n")

    # Pakej classification tests
    print("=== Pakej Classification ===")
    print("STEM A:", klasifikasi_pakej({'Biologi','Fizik','Kimia','Matematik Tambahan','Bahasa Melayu','Bahasa Inggeris','Matematik','Sejarah'}))
    print("STEM B:", klasifikasi_pakej({'Biologi','Fizik','Sains Tambahan','Bahasa Melayu','Bahasa Inggeris','Matematik','Sejarah'}))
    print("STEM C:", klasifikasi_pakej({'Sains Komputer','Reka Cipta','Bahasa Melayu','Bahasa Inggeris','Matematik','Sejarah'}))
    print("KSI:   ", klasifikasi_pakej({'Ekonomi','Prinsip Perakaunan','Bahasa Melayu','Bahasa Inggeris','Matematik','Sejarah'}))
