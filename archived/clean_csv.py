import csv, re, json

BULLET = chr(8226)

# Pakej STEM classification constants
STEM_A_CORE = {'Biologi', 'Fizik', 'Kimia', 'Matematik Tambahan'}
STEM_B_EXTRA = {
    'Sains Tambahan', 'Grafik Komunikasi Teknikal', 'Asas Kelestarian',
    'Pertanian', 'Sains Rumah Tangga', 'Reka Cipta',
}
STEM_C1_SUBJECTS = {
    'Sains Tambahan', 'Grafik Komunikasi Teknikal', 'Asas Kelestarian', 'Pertanian',
    'Sains Rumah Tangga', 'Reka Cipta', 'Sains Komputer', 'Sains Sukan',
    'Pengajian Kejuruteraan Awam', 'Pengajian Kejuruteraan Mekanikal',
    'Pengajian Kejuruteraan Elektrik & Elektronik', 'Lukisan Kejuruteraan',
}
STEM_C2_SUBJECTS = {
    'Produksi Reka Tanda', 'Hiasan Dalaman', 'Kerja Paip Domestik',
    'Pembinaan Domestik', 'Pembuatan Perabot', 'Reka Bentuk Grafik Digital',
    'Produksi Multimedia', 'Katering dan Penyajian', 'Pemprosesan Makanan',
    'Rekaan dan Jahitan Pakaian', 'Penggayaan Rambut',
    'Asuhan dan Pendidikan Awal Kanak-Kanak', 'Geomatik', 'Pendawaian Domestik',
    'Menservis Peralatan Elektrik Domestik', 'Menservis Automobil',
    'Kimpalan Arka dan Gas', 'Menservis Motosikal',
    'Menservis Peralatan Penyejukan dan Penyaman Udara',
    'Landskap dan Nurseri', 'Tanaman Makanan', 'Akuakultur dan Haiwan Rekreasi',
}
STEM_C_ALL = STEM_C1_SUBJECTS | STEM_C2_SUBJECTS
BIO_FIZIK_KIMIA = {'Biologi', 'Fizik', 'Kimia'}

INPUT_PATH = r"C:\Users\Intel\Desktop\SPM-UPUadvisor\program_pengajian_kategori_A_SPM_2026.csv"
OUTPUT_PATH = r"C:\Users\Intel\Desktop\SPM-UPUadvisor\program_pengajian_cleaned.csv"

WAJIB_MAP = {
    'Bahasa Melayu': 'Req_BM',
    'Bahasa Inggeris': 'Req_BI',
    'Sejarah': 'Req_Sejarah',
    'Matematik': 'Req_Math',
    'Matematik Tambahan': 'Req_AddMath',
    'Fizik': 'Req_Fizik',
    'Kimia': 'Req_Kimia',
    'Biologi': 'Req_Bio',
    'Sains': 'Req_Sains',
    'Pendidikan Islam': 'Req_PI',
    'Bahasa Arab': 'Req_BahasaArab',
    'Bahasa Arab Tinggi': 'Req_BahasaArab',
}

WORD_TO_NUM = {
    'SATU': 1, 'DUA': 2, 'TIGA': 3, 'EMPAT': 4,
    'LIMA': 5, 'ENAM': 6, 'TUJUH': 7, 'LAPAN': 8,
}

INFO_LABELS = [
    "Peringkat Pengajian", "Mod Pengajian", "Tempoh Pengajian", "Bidang NEC",
    "Bertemu duga / Ujian", "Joint / Dual / Double Degree", "Purata Markah Merit", "Catatan",
]

NOISE_PREFIXES = ('Berketurunan', 'Anak Negeri', 'Orang Asli', 'Taraf', 'Calon')


def extract_info_field(info, field_label):
    idx = INFO_LABELS.index(field_label)
    next_labels = INFO_LABELS[idx + 1:]
    if next_labels:
        lookahead = "|".join(re.escape(l) for l in next_labels)
        pattern = rf"{re.escape(field_label)}\s*:\s*(.+?)(?=\s*(?:{lookahead})\s*:|\Z)"
    else:
        pattern = rf"{re.escape(field_label)}\s*:\s*(.+?)$"
    m = re.search(pattern, info, re.DOTALL)
    return m.group(1).strip() if m else ""


def clean_subjects(raw):
    """Extract clean subject names from bullet/slash text, strip noise."""
    subjects = []
    # Strip trailing ATAU
    raw = re.sub(r'\s+ATAU\s*$', '', raw).strip()
    # Truncate at Bumiputera/noise text boundary
    noise_pattern = r'(?:Berketurunan|Taraf Perkahwinan|Calon hendaklah)'
    noise_m = re.search(noise_pattern, raw)
    if noise_m:
        raw = raw[:noise_m.start()].strip()
    for part in re.split(rf'[{BULLET}]', raw):
        for s in re.split(r'\s*/\s*', part):
            s = s.strip().rstrip('.').strip()
            # Strip trailing ATAU from individual subjects
            s = re.sub(r'\s+ATAU\s*$', '', s).strip()
            if s and not any(s.startswith(p) for p in NOISE_PREFIXES):
                subjects.append(s)
    return subjects


def clean_subject_name(name):
    """Clean a single specific subject name - strip period and trailing noise."""
    name = name.strip()
    # Take only the part before the first period
    name = name.split('.')[0].strip()
    # Strip trailing noise
    for prefix in NOISE_PREFIXES:
        if prefix in name:
            name = name[:name.index(prefix)].strip()
    return name


def parse_sentence(sentence):
    """
    Parse one requirement clause.
    Returns list of (type, grade, bil, subjects) tuples.
    Most sentences return one tuple; DAN sentences return two.
    """
    sentence = sentence.strip()
    if not sentence.startswith('Mendapat'):
        return []

    grade_m = re.match(r'Mendapat sekurang-kurangnya Gred\s+(\S+)\s+dalam\s+', sentence)
    if not grade_m:
        return []

    # Remaining: "mana-mana N (n) mata pelajaran yang belum"
    rem_m = re.search(r'mana-mana\s+(\S+)\s+(?:\(\d+\)\s+)?mata pelajaran\s+yang belum', sentence)
    if rem_m:
        grade = grade_m.group(1)
        bil = WORD_TO_NUM.get(rem_m.group(1), rem_m.group(1))
        return [('remaining', grade, bil, [])]

    # DAN pattern: "Gred X dalam SATU(1) mat pelajaran DAN Gred Y dalam N(n) mata pelajaran berikut"
    dan_m = re.match(
        r'Mendapat sekurang-kurangnya Gred\s+(\S+)\s+dalam\s+'
        r'(?:SATU|DUA|TIGA|EMPAT|LIMA|ENAM|TUJUH|LAPAN)\s+\((\d+)\)\s+'
        r'mata pelajaran\s+DAN\s+Gred\s+(\S+)\s+dalam\s+'
        r'(?:SATU|DUA|TIGA|EMPAT|LIMA|ENAM|TUJUH|LAPAN)\s+\((\d+)\)\s+'
        r'mata pelajaran berikut\s*:\s*(.+)',
        sentence, re.DOTALL
    )
    if dan_m:
        grade1 = dan_m.group(1)
        bil1 = int(dan_m.group(2))
        grade2 = dan_m.group(3)
        bil2 = int(dan_m.group(4))
        subjects = clean_subjects(dan_m.group(5))
        return [
            ('choice', grade1, bil1, subjects),
            ('choice', grade2, bil2, subjects),
        ]

    # Specific mandatory subject: "dalam mata pelajaran X"
    spec_m = re.match(
        r'Mendapat sekurang-kurangnya Gred\s+(\S+)\s+dalam\s+mata pelajaran\s+(.+)',
        sentence
    )
    if spec_m:
        grade = spec_m.group(1)
        subj = clean_subject_name(spec_m.group(2))
        return [('specific', grade, 1, [subj])]

    # Choice group: "dalam SATU/DUA/... (N) mata pelajaran berikut : ..."
    choice_m = re.match(
        r'Mendapat sekurang-kurangnya Gred\s+(\S+)\s+dalam\s+'
        r'(?:SATU|DUA|TIGA|EMPAT|LIMA|ENAM|TUJUH|LAPAN)\s+\((\d+)\)\s+'
        r'mata pelajaran berikut\s*:\s*(.+)',
        sentence, re.DOTALL
    )
    if choice_m:
        grade = choice_m.group(1)
        bil = int(choice_m.group(2))
        subjects = clean_subjects(choice_m.group(3))
        return [('choice', grade, bil, subjects)]

    return []


def parse_syarat_khas(text):
    wajib = {v: '' for v in set(WAJIB_MAP.values())}
    choices = []
    remaining_grade = ''
    remaining_bil = ''
    has_atau = 'Tidak'
    atau_json = ''

    if 'ATAU' in text:
        has_atau = 'Ya'

    # Split into clauses at each "Mendapat" boundary
    sentences = re.split(r'(?=Mendapat sekurang-kurangnya)', text)

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        if 'ATAU' in sent and re.search(r'ATAU\s+Mendapat', sent):
            # ATAU connects two or more full requirement sentences
            parts = re.split(r'\s+ATAU\s+(?=Mendapat)', sent)
            or_groups = []
            for part in parts:
                part = part.strip()
                results = parse_sentence(part)
                for typ, grade, bil, subjs in results:
                    if typ in ('specific', 'choice'):
                        or_groups.append({'gred': grade, 'bil': bil, 'subjek': subjs})
            if or_groups:
                choices.append({
                    'grade': or_groups[0]['gred'],
                    'bil': or_groups[0]['bil'],
                    'subjects': or_groups[0]['subjek'],
                    'atau': or_groups,
                })
        else:
            results = parse_sentence(sent)
            for typ, grade, bil, subjects in results:
                if typ == 'specific' and subjects:
                    subj = subjects[0]
                    col = WAJIB_MAP.get(subj)
                    if col:
                        if not wajib[col]:
                            wajib[col] = grade
                    else:
                        choices.append({'grade': grade, 'bil': 1, 'subjects': subjects, 'atau': None})

                elif typ == 'choice':
                    choices.append({'grade': grade, 'bil': bil, 'subjects': subjects, 'atau': None})

                elif typ == 'remaining':
                    remaining_grade = grade
                    remaining_bil = str(bil)

    atau_groups = [c['atau'] for c in choices if c.get('atau')]
    if atau_groups:
        atau_json = json.dumps(atau_groups, ensure_ascii=False)

    return wajib, choices, remaining_grade, remaining_bil, has_atau, atau_json


ALL_STEM_SUBJECTS = STEM_A_CORE | STEM_B_EXTRA | STEM_C_ALL | {'Sains'}

PAKEJ_RANK = {'STEM A': 0, 'STEM A atau B': 1, 'STEM A, B atau C': 2, 'Semua Pakej': 3}


def _stricter(a: str, b: str) -> str:
    """Return whichever pakej is more restrictive (lower rank)."""
    return a if PAKEJ_RANK[a] < PAKEJ_RANK[b] else b


def _pakej_for_choice(subjects_set: set, bil: int) -> str:
    """
    Given a choice group (subjects + minimum count needed), return the
    minimum pakej a student must be in to satisfy this group.

    Key rule: non-STEM subjects count as 'free' options for KSI students.
    If there are enough non-STEM subjects to satisfy bil, any pakej works.
    """
    non_stem_count = len(subjects_set - ALL_STEM_SUBJECTS)
    if non_stem_count >= bil:
        return 'Semua Pakej'

    # Student must pick at least (bil - non_stem_count) STEM subjects
    stem_needed = bil - non_stem_count
    stem_a_in_group = subjects_set & STEM_A_CORE
    bfk_in_group = subjects_set & BIO_FIZIK_KIMIA

    if stem_needed >= 3 and len(stem_a_in_group) >= 3:
        return 'STEM A'
    if stem_needed >= 2 and len(bfk_in_group) >= 2:
        return 'STEM A atau B'
    if bfk_in_group or stem_a_in_group:
        return 'STEM A, B atau C'
    # Only STEM C subjects required
    return 'STEM A, B atau C'


def derive_pakej_min(wajib: dict, choices: list) -> str:
    """
    Derive minimum student pakej required for a program.

    Mandatory subjects are checked first (most reliable signal).
    Choice groups are checked accounting for non-STEM escape options.
    """
    wajib_bfk = sum(1 for col in ['Req_Bio', 'Req_Fizik', 'Req_Kimia'] if wajib.get(col))
    has_addmath = bool(wajib.get('Req_AddMath'))
    wajib_stem_a = wajib_bfk + (1 if has_addmath else 0)

    # 3+ STEM A subjects mandatory (includes AddMath) -> STEM A
    if wajib_stem_a >= 3:
        return 'STEM A'
    # All 3 of Bio/Fizik/Kimia mandatory -> STEM A
    if wajib_bfk == 3:
        return 'STEM A'
    # 2 of Bio/Fizik/Kimia mandatory -> STEM A atau B
    if wajib_bfk == 2:
        return 'STEM A atau B'
    # AddMath + 1 of Bio/Fizik/Kimia mandatory -> STEM A atau B
    if has_addmath and wajib_bfk >= 1:
        return 'STEM A atau B'
    # Any 1 of Bio/Fizik/Kimia mandatory (KSI students don't take these) -> STEM A, B atau C
    if wajib_bfk >= 1:
        return 'STEM A, B atau C'
    # AddMath alone mandatory (uncommon for KSI) -> STEM A, B atau C
    if has_addmath:
        return 'STEM A, B atau C'

    # Check choice groups - accumulate most restrictive result
    best = 'Semua Pakej'
    for c in choices:
        candidate = _pakej_for_choice(set(c['subjects']), c['bil'])
        best = _stricter(best, candidate)

    return best


def parse_row(row):
    no_key = next(k for k in row.keys() if 'No' in k)
    no = row[no_key].strip('"')

    merit_str = row['Purata Merit'].replace('%', '').strip()
    try:
        merit = float(merit_str)
    except (ValueError, TypeError):
        merit = ''

    tags = row['Tags']
    is_feeder = 'Ya' if 'Perintis' in tags or 'Feeder' in tags else 'Tidak'
    is_stem = 'Ya' if 'STEM' in tags else 'Tidak'
    bumi = 'Ya' if 'Bumiputera' in tags else 'Tidak'

    info = row['Info']
    peringkat = extract_info_field(info, 'Peringkat Pengajian')
    mod = extract_info_field(info, 'Mod Pengajian')
    tempoh = extract_info_field(info, 'Tempoh Pengajian')
    bidang_nec = extract_info_field(info, 'Bidang NEC')
    bertemu_duga = extract_info_field(info, 'Bertemu duga / Ujian')
    joint_degree = extract_info_field(info, 'Joint / Dual / Double Degree')
    catatan = extract_info_field(info, 'Catatan')

    wajib, choices, rem_grade, rem_bil, has_atau, atau_json = parse_syarat_khas(row['Syarat Khas'])
    pakej_min = derive_pakej_min(wajib, choices)

    out = {
        'No': no,
        'Nama_Program': row['Nama Program'],
        'IPTA': row['IPTA'],
        'Kod_Program': row['Kod Program'],
        'Tahun': row['Tahun'],
        'Merit': merit,
        'Is_Feeder': is_feeder,
        'Is_STEM': is_stem,
        'Bumiputera_Sahaja': bumi,
        'Pakej_Min': pakej_min,
        'Peringkat_Pengajian': peringkat,
        'Mod_Pengajian': mod,
        'Tempoh_Pengajian': tempoh,
        'Bidang_NEC': bidang_nec,
        'Bertemu_Duga': bertemu_duga,
        'Joint_Degree': joint_degree,
        'Catatan': catatan,
        'Req_BM': wajib['Req_BM'],
        'Req_BI': wajib['Req_BI'],
        'Req_Sejarah': wajib['Req_Sejarah'],
        'Req_Math': wajib['Req_Math'],
        'Req_AddMath': wajib['Req_AddMath'],
        'Req_Fizik': wajib['Req_Fizik'],
        'Req_Kimia': wajib['Req_Kimia'],
        'Req_Bio': wajib['Req_Bio'],
        'Req_Sains': wajib['Req_Sains'],
        'Req_PI': wajib['Req_PI'],
        'Req_BahasaArab': wajib['Req_BahasaArab'],
        'Lain_Gred': rem_grade,
        'Lain_Bil': rem_bil,
        'Has_ATAU': has_atau,
        'ATAU_JSON': atau_json,
        'Syarat_Am': row['Syarat Am'],
        'Syarat_Khas': row['Syarat Khas'],
    }

    for n in range(1, 9):
        if n - 1 < len(choices):
            c = choices[n - 1]
            out[f'Pilihan_{n}_Gred'] = c['grade']
            out[f'Pilihan_{n}_Bil'] = c['bil']
            out[f'Pilihan_{n}_Subjek'] = '|'.join(c['subjects'])
        else:
            out[f'Pilihan_{n}_Gred'] = ''
            out[f'Pilihan_{n}_Bil'] = ''
            out[f'Pilihan_{n}_Subjek'] = ''

    return out


OUTPUT_FIELDS = [
    'No', 'Nama_Program', 'IPTA', 'Kod_Program', 'Tahun', 'Merit',
    'Is_Feeder', 'Is_STEM', 'Bumiputera_Sahaja', 'Pakej_Min',
    'Peringkat_Pengajian', 'Mod_Pengajian', 'Tempoh_Pengajian', 'Bidang_NEC',
    'Bertemu_Duga', 'Joint_Degree', 'Catatan',
    'Req_BM', 'Req_BI', 'Req_Sejarah', 'Req_Math', 'Req_AddMath',
    'Req_Fizik', 'Req_Kimia', 'Req_Bio', 'Req_Sains', 'Req_PI', 'Req_BahasaArab',
    'Pilihan_1_Gred', 'Pilihan_1_Bil', 'Pilihan_1_Subjek',
    'Pilihan_2_Gred', 'Pilihan_2_Bil', 'Pilihan_2_Subjek',
    'Pilihan_3_Gred', 'Pilihan_3_Bil', 'Pilihan_3_Subjek',
    'Pilihan_4_Gred', 'Pilihan_4_Bil', 'Pilihan_4_Subjek',
    'Pilihan_5_Gred', 'Pilihan_5_Bil', 'Pilihan_5_Subjek',
    'Pilihan_6_Gred', 'Pilihan_6_Bil', 'Pilihan_6_Subjek',
    'Pilihan_7_Gred', 'Pilihan_7_Bil', 'Pilihan_7_Subjek',
    'Pilihan_8_Gred', 'Pilihan_8_Bil', 'Pilihan_8_Subjek',
    'Lain_Gred', 'Lain_Bil',
    'Has_ATAU', 'ATAU_JSON',
    'Syarat_Am', 'Syarat_Khas',
]

rows_written = 0
with open(INPUT_PATH, newline='', encoding='utf-8-sig') as infile, \
     open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    for row in reader:
        writer.writerow(parse_row(row))
        rows_written += 1

print(f"Done. {rows_written} rows written to {OUTPUT_PATH}")
