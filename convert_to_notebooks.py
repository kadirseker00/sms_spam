"""
convert_to_notebooks.py
Her .py dosyasını, görevine göre hücrelere ayırarak .ipynb notebook'una çevirir.
"""

import json
import os
import re

# Hücre sınırlarını belirleyen kalıplar (öncelik sırasıyla)
CELL_BREAK_PATTERNS = [
    r'^import\s',
    r'^from\s',
    r'^#\s*---',
    r'^#\s*===',
    r'^# (Verinin|Hedef|Özellik|eğitim|bag-of|tf-idf|ölçekleme|Chi-|Karşılıklı|LASSO|Rastgele|Recursive|Modellerin)',
    r'^# (lojistik|decision|knn|SVM|Nearest|Gradient|xgboost|random forest)',
    r'^# (lojistik|decision|knn|SVM|Nearest|Gradient|xgboost|random forest)',
]

def make_cell(source_lines, cell_type="code"):
    """Bir notebook hücresi oluşturur."""
    source = "".join(source_lines)
    if cell_type == "code":
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source.rstrip("\n")
        }
    else:
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": source.rstrip("\n")
        }

def make_markdown(title, description=""):
    """Markdown başlık hücresi oluşturur."""
    content = f"## {title}"
    if description:
        content += f"\n{description}"
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": content
    }

def split_into_sections(lines):
    """
    .py dosyasını anlamlı bölümlere ayırır.
    Her bölüm (başlık, kod_satırları) tuple'ı döner.
    """
    sections = []
    current_lines = []
    current_title = "İmportlar ve Kurulum"

    # Özel başlık eşleştirme
    SECTION_TITLES = {
        r'# .*[Vv]eri.*[Yy]ükl': "Veri Yükleme",
        r'# .*[Ee]tiket': "Etiket Kodlama (ham→0, spam→1)",
        r'# .*[Öö]zellik.*[Hh]edef': "Özellik / Hedef Ayrımı",
        r'# .*[Ee]ğitim.*[Tt]est': "Eğitim / Test Bölünmesi (%70/%30)",
        r'# .*bag.of|# .*[Bb]o[Ww]|# .*CountVect': "BoW Vektörleştirme",
        r'# .*tf.idf|# .*[Tt]fidf|# .*TF-IDF': "TF-IDF Vektörleştirme",
        r'# .*[Ww]ord2[Vv]ec': "Word2Vec Yükleme & Vektörleştirme",
        r'# .*[Ss]MOTE': "SMOTE Oversampling",
        r'# .*[Uu]nder[Ss]ampl|# .*[Rr]andom.*[Uu]nder': "Random Undersampling",
        r'# .*[Öö]lçekleme|def scale_': "Ölçekleme (Scaling)",
        r'# .*[Cc]hi.?[Ss]quare|# .*[Cc]hi-?2': "Özellik Seçimi: Chi-Square",
        r'# .*[Kk]arşılıklı|# .*[Mm]utual': "Özellik Seçimi: Mutual Information",
        r'# .*LASSO': "Özellik Seçimi: LASSO (L1)",
        r'# .*[Rr]astgele.*[Oo]rman|# .*[Rr]andom.*[Ff]orest.*[Yy]ön': "Özellik Seçimi: Random Forest",
        r'# .*RFE|# .*[Rr]ecursive': "Özellik Seçimi: RFE",
        r'# .*[Mm]odellerin.*[Ee]ğitim|models\s*=\s*\{': "Model Karşılaştırma Altyapısı",
        r'# .*[Ll]ojistik': "Sınıflayıcı: Lojistik Regresyon (LR)",
        r'# .*[Dd]ecision|# .*[Kk]arar': "Sınıflayıcı: Decision Tree (DT)",
        r'# .*[Kk][Nn][Nn]|# .*k en yakın': "Sınıflayıcı: KNN (k=3)",
        r'# .*SVM|# .*[Dd]estek [Vv]ektör': "Sınıflayıcı: SVM (kernel=poly)",
        r'# .*[Nn]earest [Cc]entroid|# .*[Ee]n [Yy]akın [Mm]erkez': "Sınıflayıcı: Nearest Centroid (NC)",
        r'# .*[Gg]radient [Bb]oost': "Ensemble: Gradient Boosting (GB)",
        r'# .*xgboost|# .*XGBoost': "Ensemble: XGBoost (XGB)",
        r'# .*[Rr]andom [Ff]orest.*sınıfl|# .*[Rr]andomforest': "Ensemble: Random Forest (RF)",
        r'print\(\)|print\("': None,  # print satırları birleştir
    }

    i = 0
    import_lines = []
    in_imports = True

    # Önce tüm import satırlarını topla
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from ') or stripped == '' or stripped.startswith('#') and in_imports:
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append(line)
                in_imports = True
            elif in_imports:
                import_lines.append(line)
            else:
                break
        else:
            in_imports = False
            break
        i += 1

    # İmport bölümünü ekle
    if import_lines:
        # Docstring varsa başa ekle
        sections.append(("İmportlar ve Kurulum", import_lines))

    # Geri kalan satırları işle
    current_lines = []
    current_title = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Boş satır
        if stripped == '':
            current_lines.append(line)
            i += 1
            continue

        # Başlık eşleştir
        matched_title = None
        for pattern, title in SECTION_TITLES.items():
            if re.match(pattern, stripped):
                matched_title = title
                break

        if matched_title is not None and current_lines and any(l.strip() for l in current_lines):
            # Mevcut bölümü kaydet
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_lines = [line]
            current_title = matched_title
        else:
            if current_title is None and matched_title:
                current_title = matched_title
            current_lines.append(line)

        i += 1

    # Son bölümü ekle
    if current_lines and any(l.strip() for l in current_lines):
        sections.append((current_title or "Diğer", current_lines))

    return sections


def py_to_notebook(py_path, nb_path=None):
    """Bir .py dosyasını .ipynb notebook'una çevirir."""
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines(keepends=True)

    filename = os.path.basename(py_path)
    name_no_ext = os.path.splitext(filename)[0]

    # Dosya başlığı ve açıklaması için ilk yorum bloğunu bul
    file_description = ""
    if lines and lines[0].strip().startswith('"""'):
        doc_end = 1
        while doc_end < len(lines) and '"""' not in lines[doc_end]:
            doc_end += 1
        doc_lines = lines[1:doc_end]
        file_description = "".join(doc_lines).strip()
        lines = lines[doc_end+1:]

    sections = split_into_sections(lines)

    cells = []

    # Başlık markdown hücresi
    title_md = f"# {name_no_ext}\n"
    if file_description:
        title_md += f"\n{file_description}"
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": title_md
    })

    for section_title, section_lines in sections:
        # Boş bölümleri atla
        code = "".join(section_lines).strip()
        if not code:
            continue

        # Markdown başlık hücresi
        if section_title:
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": f"### {section_title}"
            })

        # Kod hücresi
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": code
        })

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.12.0"
            }
        },
        "cells": cells
    }

    if nb_path is None:
        nb_path = py_path.replace('.py', '.ipynb')

    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)

    return nb_path


# Tüm .py dosyalarını dönüştür (dönüştürücünün kendisi hariç)
base_dir = os.path.dirname(os.path.abspath(__file__))
py_files = [f for f in sorted(os.listdir(base_dir))
            if f.endswith('.py') and f != 'convert_to_notebooks.py']

print(f"Toplam {len(py_files)} dosya dönüştürülecek...\n")

for py_file in py_files:
    py_path = os.path.join(base_dir, py_file)
    nb_path = py_path.replace('.py', '.ipynb')
    try:
        result = py_to_notebook(py_path, nb_path)
        print(f"  [OK] {py_file} → {os.path.basename(nb_path)}")
    except Exception as e:
        print(f"  [HATA] {py_file}: {e}")

print(f"\nTamamlandı! {len(py_files)} notebook oluşturuldu.")
