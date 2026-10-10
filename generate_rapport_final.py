#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=== RAPPORT PFE URBAIN SUSTAINABILITY SYSTEM - GENERATION FINALE ===
Document Word professionnel avec:
  - Pages preliminaires en chiffres romains (i, ii, iii...)
  - Pages principales en chiffres arabes (1, 2, 3...)
  - Design carreau noir + ligne pour chaque titre de chapitre
  - Sommaire automatique (champ TOC Word)
  - En-tetes differents par chapitre
  - Numerotation hierarchique correcte
  - Aucune ligne verticale parasite
"""

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement
from docx.enum.style import WD_STYLE_TYPE
import copy, os

doc = Document()

# ============================================================
# FONCTIONS OUTILS XML
# ============================================================

def make_element(tag, attrib=None, text=None):
    el = OxmlElement(tag)
    if attrib:
        for k, v in attrib.items():
            el.set(qn(k) if ':' in k else k, v)
    if text is not None:
        el.text = text
    return el

def add_field(paragraph, field_code, display_text=""):
    """Ajoute un champ Word (PAGE, NUMPAGES, TOC, etc.)"""
    run1 = paragraph.add_run()
    run1._r.append(make_element('w:fldChar', {'w:fldCharType': 'begin'}))
    
    run2 = paragraph.add_run()
    run2._r.append(make_element('w:instrText', {'xml:space': 'preserve'}, field_code))
    
    run3 = paragraph.add_run()
    run3._r.append(make_element('w:fldChar', {'w:fldCharType': 'separate'}))
    
    run4 = paragraph.add_run(display_text)
    
    run5 = paragraph.add_run()
    run5._r.append(make_element('w:fldChar', {'w:fldCharType': 'end'}))
    return [run1, run2, run3, run4, run5]

def set_cell_shading(cell, color):
    shading = make_element('w:shd', {'w:fill': color, 'w:val': 'clear'})
    cell._tc.get_or_add_tcPr().append(shading)

# ============================================================
# CONFIGURATION PAGE
# ============================================================

def setup_section(section, is_first=False):
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3)
    section.right_margin = Cm(2.5)
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)

# Section 0: préliminaire
setup_section(doc.sections[0])
# Pas d'en-tête pour les pages préliminaires
header0 = doc.sections[0].header
header0.is_linked_to_previous = False
hp0 = header0.paragraphs[0]
hp0.text = ""
hp0.paragraph_format.first_line_indent = Cm(0)

# Footer préliminaire avec chiffres romains
footer0 = doc.sections[0].footer
footer0.is_linked_to_previous = False
fp0 = footer0.paragraphs[0]
fp0.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp0.paragraph_format.first_line_indent = Cm(0)
# Format romain
rp = fp0.add_run()
rp._r.append(make_element('w:fldChar', {'w:fldCharType': 'begin'}))
rp2 = fp0.add_run()
rp2._r.append(make_element('w:instrText', {'xml:space': 'preserve'}, 'PAGE'))
rp3 = fp0.add_run()
rp3._r.append(make_element('w:fldChar', {'w:fldCharType': 'separate'}))
rp4 = fp0.add_run("i")
rp5 = fp0.add_run()
rp5._r.append(make_element('w:fldChar', {'w:fldCharType': 'end'}))
for r in [rp, rp2, rp3, rp4, rp5]:
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)

# Définir le format des numéros de page en romain pour la section préliminaire
sectPr0 = doc.sections[0]._sectPr
pgNumType0 = make_element('w:pgNumType', {'w:fmt': 'lowerRoman'})
sectPr0.append(pgNumType0)

# ============================================================
# STYLES
# ============================================================

# Normal
normal = doc.styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(12)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
normal.paragraph_format.first_line_indent = Cm(0.5)
normal.paragraph_format.line_spacing = 1.15
normal.paragraph_format.space_after = Pt(6)

# Heading 1 - Chapitre (avec design)
h1 = doc.styles['Heading 1']
h1.font.name = 'Times New Roman'
h1.font.size = Pt(22)
h1.font.bold = True
h1.font.color.rgb = RGBColor(0, 0, 0)
h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
h1.paragraph_format.space_before = Pt(36)
h1.paragraph_format.space_after = Pt(6)
h1.paragraph_format.first_line_indent = Cm(0)
h1.paragraph_format.keep_with_next = True

# Heading 2
h2 = doc.styles['Heading 2']
h2.font.name = 'Times New Roman'
h2.font.size = Pt(16)
h2.font.bold = True
h2.font.color.rgb = RGBColor(0, 0, 0)
h2.paragraph_format.space_before = Pt(24)
h2.paragraph_format.space_after = Pt(10)
h2.paragraph_format.first_line_indent = Cm(0)
h2.paragraph_format.keep_with_next = True

# Heading 3
h3 = doc.styles['Heading 3']
h3.font.name = 'Times New Roman'
h3.font.size = Pt(14)
h3.font.bold = True
h3.font.color.rgb = RGBColor(0, 0, 0)
h3.paragraph_format.space_before = Pt(18)
h3.paragraph_format.space_after = Pt(8)
h3.paragraph_format.first_line_indent = Cm(0)
h3.paragraph_format.keep_with_next = True

# Heading 4
h4 = doc.styles['Heading 4']
h4.font.name = 'Times New Roman'
h4.font.size = Pt(13)
h4.font.bold = True
h4.font.italic = True
h4.font.color.rgb = RGBColor(0, 0, 0)
h4.paragraph_format.space_before = Pt(12)
h4.paragraph_format.space_after = Pt(6)
h4.paragraph_format.first_line_indent = Cm(0)

# ============================================================
# NUMEROTATION MULTINIVEAU (Heading 1/2/3)
# ============================================================

# Remove any default numbering on heading styles first
for hname in ['Heading 1', 'Heading 2', 'Heading 3']:
    style = doc.styles[hname]
    pPr = style.element.find(qn('w:pPr'))
    if pPr is not None:
        numPr = pPr.find(qn('w:numPr'))
        if numPr is not None:
            pPr.remove(numPr)

def create_lvl_xml(ilvl, fmt, lvl_text, sz_val, heading_style):
    lvl = OxmlElement('w:lvl')
    lvl.set(qn('w:ilvl'), str(ilvl))
    start = make_element('w:start', {'w:val': '1'}); lvl.append(start)
    nf = make_element('w:numFmt', {'w:val': fmt}); lvl.append(nf)
    lt = make_element('w:lvlText', {'w:val': lvl_text}); lvl.append(lt)
    lj = make_element('w:lvlJc', {'w:val': 'left'}); lvl.append(lj)
    pPr_lvl = OxmlElement('w:pPr')
    ps = make_element('w:pStyle', {'w:val': heading_style}); pPr_lvl.append(ps)
    ind = make_element('w:ind', {'w:left': '0'}); pPr_lvl.append(ind)
    lvl.append(pPr_lvl)
    rPr_lvl = OxmlElement('w:rPr')
    rf = make_element('w:rFonts', {'w:ascii': 'Times New Roman', 'w:hAnsi': 'Times New Roman', 'w:cs': 'Times New Roman'}); rPr_lvl.append(rf)
    sz = make_element('w:sz', {'w:val': str(sz_val)}); rPr_lvl.append(sz)
    szCs = make_element('w:szCs', {'w:val': str(sz_val)}); rPr_lvl.append(szCs)
    b = make_element('w:b'); rPr_lvl.append(b)
    lvl.append(rPr_lvl)
    return lvl

# Access or create numbering part
try:
    numbering_part = doc.part.numbering_part
    numbering_el = numbering_part.element
except Exception:
    from docx.opc.part import Part
    from docx.opc.packuri import PackURI
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from lxml import etree
    numbering_el = make_element('w:numbering')
    from docx.parts.numbering import NumberingPart
    numbering_part = NumberingPart(None, PackURI('/word/numbering.xml'), numbering_el, doc.part.package)
    doc.part.relate_to(numbering_part, RT.NUMBERING)

# Clear old numbering definitions to avoid conflicts
for child in list(numbering_el):
    numbering_el.remove(child)

# Abstract numbering
abs_num = make_element('w:abstractNum', {'w:abstractNumId': '100'})
mlt = make_element('w:multiLevelType', {'w:val': 'hybridMultilevel'}); abs_num.append(mlt)
abs_num.append(create_lvl_xml(0, 'decimal', 'Chapitre %1', 44, 'Heading1'))
abs_num.append(create_lvl_xml(1, 'decimal', '%1.%2', 32, 'Heading2'))
abs_num.append(create_lvl_xml(2, 'decimal', '%1.%2.%3', 28, 'Heading3'))
numbering_el.append(abs_num)

# Num instance
num_el = make_element('w:num', {'w:numId': '100'})
aid = make_element('w:abstractNumId', {'w:val': '100'}); num_el.append(aid)
numbering_el.append(num_el)

# Link heading styles to numbering
for hname, ilvl in [('Heading 1', 0), ('Heading 2', 1), ('Heading 3', 2)]:
    style = doc.styles[hname]
    pPr = style.element.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr'); style.element.append(pPr)
    numPr = make_element('w:numPr')
    nid = make_element('w:numId', {'w:val': '100'}); numPr.append(nid)
    il = make_element('w:ilvl', {'w:val': str(ilvl)}); numPr.append(il)
    pPr.append(numPr)

# ============================================================
# FONCTIONS DE CONTENU
# ============================================================

def add_para(text, bold=False, italic=False, size=12, align=None, indent=True, space_after=6, style='Normal'):
    p = doc.add_paragraph(style=style)
    if text:
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        run.bold = bold
        run.italic = italic
    if align:
        p.paragraph_format.alignment = align
    p.paragraph_format.first_line_indent = Cm(0.5 if indent else 0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    return p

def add_chapter_title(text, number=None):
    """Ajoute un titre de chapitre en Heading 1 avec carreau noir + ligne (numbered only)"""
    p = doc.add_paragraph(style='Heading 1')
    # Black square
    run_square = p.add_run("  ")
    rPr = run_square._r.get_or_add_rPr()
    shd = make_element('w:shd', {'w:fill': '000000', 'w:val': 'clear'})
    rPr.append(shd)
    run_space = p.add_run("   ")
    # Title text with chapter label
    if number is not None:
        run_label = p.add_run(f"CHAPITRE {number}")
        run_label.font.name = 'Times New Roman'; run_label.font.size = Pt(14); run_label.bold = True
        run_br = p.add_run("\n"); run_br.font.size = Pt(4)
    run_title = p.add_run(text)
    run_title.font.name = 'Times New Roman'; run_title.font.size = Pt(22); run_title.bold = True
    # Bottom border
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = make_element('w:bottom', {'w:val': 'single', 'w:sz': '12', 'w:space': '4', 'w:color': '000000'})
    pBdr.append(bottom); pPr.append(pBdr)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(12)
    return p

def add_main_title(text):
    """Ajoute un titre principal non-chapitre (Intro, Conclusion, Biblio, Annexes) — Normal style, pas de Heading 1"""
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    numPr = pPr.find(qn('w:numPr'))
    if numPr is not None:
        pPr.remove(numPr)
    p.style = doc.styles['Normal']
    run_square = p.add_run("  ")
    rPr = run_square._r.get_or_add_rPr()
    shd = make_element('w:shd', {'w:fill': '000000', 'w:val': 'clear'})
    rPr.append(shd)
    run_space = p.add_run("   ")
    run_title = p.add_run(text)
    run_title.font.name = 'Times New Roman'; run_title.font.size = Pt(22); run_title.bold = True
    pBdr = OxmlElement('w:pBdr')
    bottom = make_element('w:bottom', {'w:val': 'single', 'w:sz': '12', 'w:space': '4', 'w:color': '000000'})
    pBdr.append(bottom); pPr.append(pBdr)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(36)
    p.paragraph_format.space_after = Pt(12)
    return p

def add_section_title(text):
    """Ajoute un titre de section en Heading 2"""
    p = doc.add_paragraph(style='Heading 2')
    run = p.add_run(text)
    run.font.name = 'Times New Roman'; run.font.size = Pt(16); run.bold = True
    p.paragraph_format.first_line_indent = Cm(0)
    return p

def add_subsection_title(text):
    """Ajoute un titre de sous-section en Heading 3"""
    p = doc.add_paragraph(style='Heading 3')
    run = p.add_run(text)
    run.font.name = 'Times New Roman'; run.font.size = Pt(14); run.bold = True
    p.paragraph_format.first_line_indent = Cm(0)
    return p

def add_table_placeholder(num, title, desc=""):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(f"[Insérer Tableau {num} : {title}]")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.bold = True
    r.italic = True
    r.font.color.rgb = RGBColor(100, 100, 100)
    if desc:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.first_line_indent = Cm(0)
        p2.paragraph_format.space_after = Pt(12)
        r2 = p2.add_run(desc)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10)
        r2.italic = True
        r2.font.color.rgb = RGBColor(130, 130, 130)

def add_table(title, headers, rows, col_widths=None):
    """Ajoute un tableau fonctionnel avec style: fond bleu entete, pas de lignes verticales"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(title)
    r.font.name = 'Times New Roman'; r.font.size = Pt(11); r.bold = True
    r.italic = True

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.style = 'Table Grid'

    for ci, header in enumerate(headers):
        cell = table.rows[0].cells[ci]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pPr = p._p.get_or_add_pPr()
        shd = make_element('w:shd', {'w:fill': '1565C0', 'w:val': 'clear'})
        pPr.append(shd)
        r = p.add_run(header)
        r.font.name = 'Times New Roman'; r.font.size = Pt(10); r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for ri, row_data in enumerate(rows):
        for ci, cell_text in enumerate(row_data):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ''
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            pPr = p._p.get_or_add_pPr()
            # Remove vertical borders from this cell
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for side in ['left', 'right']:
                border = OxmlElement(f'w:{side}')
                border.set(qn('w:val'), 'nil')
                tcBorders.append(border)
            tcPr.append(tcBorders)
            if ri % 2 == 1:
                shd = make_element('w:shd', {'w:fill': 'F5F5F5', 'w:val': 'clear'})
                pPr.append(shd)
            r = p.add_run(str(cell_text))
            r.font.name = 'Times New Roman'; r.font.size = Pt(10)

    # Remove vertical borders from header row too
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for side in ['left', 'right']:
            border = OxmlElement(f'w:{side}')
            border.set(qn('w:val'), 'nil')
            tcBorders.append(border)
        tcPr.append(tcBorders)

    for ci in range(len(headers)):
        if col_widths and ci < len(col_widths):
            for row in table.rows:
                row.cells[ci].width = Cm(col_widths[ci])

    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(6)

def add_figure_image(num, title, desc=""):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(f"[Insérer Figure {num} : {title}]")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.bold = True
    r.italic = True
    r.font.color.rgb = RGBColor(100, 100, 100)
    if desc:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.first_line_indent = Cm(0)
        p2.paragraph_format.space_after = Pt(12)
        r2 = p2.add_run(desc)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10)
        r2.italic = True
        r2.font.color.rgb = RGBColor(130, 130, 130)

# ---- FICHIERS IMAGES PAR NUMERO DE FIGURE ----
FIGURE_IMAGE_MAP = {
    1:  "fig01_architecture_globale.png",
    2:  "fig_diagramme_cas_utilisation.png",
    3:  "fig_diagramme_classes.png",
    4:  "fig_diagramme_sequence_envoi_notification.png",
    5:  "fig_diagramme_etat_signal.png",
    6:  "Fonctionnalit\u00e9s par Profil d'Utilisateur.png",
    7:  "fig_chaine_ia_pipeline.png",
    8:  "Tableau de Bord Administrateur.png",
    9:  "fig_diagramme_flux_donnees.png",
    10: "fig_systeme_notification.png",
    11: "fig_gantt_planning.png",
    12: "fig_signal_workflow.png",
    13: None,  # collection de captures
    14: "fig_architecture_physique_simple.png",
    15: "fig_ecran_connexion.png",
    16: "fig_ecran_analyze_ai_signalement.png",
    17: "fig_ecran_creation_signalement.png",
    18: "fig_ecran_detail_signalement.png",
    19: "fig_ecran_carte_interactive.png",
    20: "fig_ecran_pipeline_ia.png",
}

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "rapport_figures")

def add_figure_image(num, title, desc=""):
    """Insère l'image réelle si disponible, sinon placeholder texte."""
    fname = FIGURE_IMAGE_MAP.get(num)
    if fname:
        path = os.path.join(FIGURES_DIR, fname)
    else:
        path = None

    if path and os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run()
        run.add_picture(path, width=Inches(5.8))
    else:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"[Insérer Figure {num} : {title}]")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.bold = True
        r.italic = True
        r.font.color.rgb = RGBColor(100, 100, 100)

    # Légende centrée sous l'image
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.space_before = Pt(4)
    cap.paragraph_format.space_after = Pt(6)
    r2 = cap.add_run(f"Figure {num} : {title}")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10)
    r2.bold = True

    if desc:
        p3 = doc.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.first_line_indent = Cm(0)
        p3.paragraph_format.space_after = Pt(4)
        r3 = p3.add_run(desc)
        r3.font.name = 'Times New Roman'
        r3.font.size = Pt(10)
        r3.italic = True


def page_break():
    doc.add_page_break()

def new_main_section(chapter_name):
    """Nouvelle section pour chapitre principal avec numérotation arabe"""
    s = doc.add_section()
    setup_section(s)
    s._sectPr.append(make_element('w:pgNumType', {'w:fmt': 'decimal'}))
    
    # En-tête
    h = s.header
    h.is_linked_to_previous = False
    hp = h.paragraphs[0]
    hp.paragraph_format.first_line_indent = Cm(0)
    hp.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
    run_g = hp.add_run("URBAIN Sustainability System")
    run_g.font.name = 'Times New Roman'
    run_g.font.size = Pt(9)
    run_g.italic = True
    run_g.font.color.rgb = RGBColor(120, 120, 120)
    run_t = hp.add_run(f"\t\t{chapter_name}")
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(9)
    run_t.italic = True
    run_t.font.color.rgb = RGBColor(120, 120, 120)
    
    # Pied de page avec numérotation arabe (Page X / Y)
    f = s.footer
    f.is_linked_to_previous = False
    fp = f.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fp.paragraph_format.first_line_indent = Cm(0)
    fp.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT)
    
    # Ligne décorative au-dessus
    p_dec = f.paragraphs[0]
    p_dec.paragraph_format.first_line_indent = Cm(0)
    p_dec.paragraph_format.space_after = Pt(2)
    # Ajouter PAGE / NUMPAGES directement
    r0 = fp.add_run("Page ")
    r0.font.name = 'Times New Roman'
    r0.font.size = Pt(9)
    
    add_field(fp, ' PAGE ', '1')
    for r in fp.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9)
    
    r_sep = fp.add_run(" / ")
    r_sep.font.name = 'Times New Roman'
    r_sep.font.size = Pt(9)
    
    add_field(fp, ' NUMPAGES ', '1')
    for r in fp.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9)
    
    return s

def add_toc():
    """Insère un champ TOC Word"""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_after = Pt(12)
    add_field(p, ' TOC \\o "1-3" \\h \\z \\u ', 
              "[Mettre a jour : clic droit > Mettre a jour les champs]")
    # Appliquer la police à tous les runs générés par add_field
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        if "Mettre" in (run.text or ""):
            run.italic = True
            run.font.color.rgb = RGBColor(150, 150, 150)

def create_table(headers, rows):
    """Tableau professionnel sans lignes verticales"""
    ncols = len(headers)
    nrows = 1 + len(rows)
    table = doc.add_table(rows=nrows, cols=ncols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Style: seulement bordures horizontales
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    borders = parse_xml(
        '<w:tblBorders %s>'
        '<w:top w:val="single" w:sz="8" w:space="0" w:color="333333"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="333333"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(borders)
    
    # En-tête
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(h)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(cell, '2C3E50')
    
    # Données
    for ri, row_data in enumerate(rows):
        for ci, val in enumerate(row_data):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(str(val))
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            if ri % 2 == 1:
                set_cell_shading(cell, 'F5F5F5')
    
    return table

# ============================================================
# CONTENU DU RAPPORT
# ============================================================

# ---- PAGE DE GARDE ----
LOGO_UNIV = r"C:\Users\seifa\Downloads\logo_univ.jpg"

# Top header table (left: INT + logo, right: Republic + coat of arms)
t = doc.add_table(rows=1, cols=2)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.autofit = True
for row in t.rows:
    for cell in row.cells:
        cell.width = Cm(8.5)
        set_cell_shading(cell, "FFFFFF")
        # remove borders
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        for border_name in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'none')
            border.set(qn('w:sz'), '0')
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), 'auto')
            tcBorders.append(border)
        tcPr.append(tcBorders)

# Left cell: university logo + name
left_cell = t.cell(0, 0)
left_para = left_cell.paragraphs[0]
left_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
left_para.paragraph_format.first_line_indent = Cm(0)
left_para.paragraph_format.space_after = Pt(0)
if os.path.exists(LOGO_UNIV):
    run_logo = left_para.add_run()
    run_logo.add_picture(LOGO_UNIV, width=Cm(1.8))
    run_logo.add_text("  ")
run_int = left_para.add_run("INT Institut des Nouvelles Technologies")
run_int.font.name = 'Times New Roman'
run_int.font.size = Pt(11)
run_int.bold = True

# Right cell: coat of arms + ministry text
right_cell = t.cell(0, 1)
right_para = right_cell.paragraphs[0]
right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
right_para.paragraph_format.first_line_indent = Cm(0)
right_para.paragraph_format.space_after = Pt(0)
run_r = right_para.add_run("REPUBLIQUE TUNISIENNE\nMINISTERE DE L'ENSEIGNEMENT SUPERIEUR\nET DE LA RECHERCHE SCIENTIFIQUE")
run_r.font.name = 'Times New Roman'
run_r.font.size = Pt(8)
run_r.bold = True

# Spacer
add_para("", indent=False, size=12, space_after=6)

# Ligne décorative
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Cm(0)
r = p.add_run("━" * 50)
r.font.color.rgb = RGBColor(44, 62, 80)
r.font.size = Pt(6)

add_para("", indent=False, space_after=12)
add_para("PROJET DE FIN D'ETUDES", bold=True, size=20, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=6)
add_para("Pour l'obtention du Brevet de Technicien Superieur", size=14, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=2)
add_para("en informatique de gestion", size=14, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Cm(0)
r = p.add_run("━" * 50)
r.font.color.rgb = RGBColor(44, 62, 80)
r.font.size = Pt(6)

add_para("", indent=False, space_after=18)
add_para("URBAIN SUSTAINABILITY SYSTEM", bold=True, size=26, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=8)
add_para("Plateforme Intelligente de Signalement et de Gestion", italic=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=2)
add_para("des Problemes Urbains", italic=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=30)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Cm(0)
r = p.add_run("━" * 50)
r.font.color.rgb = RGBColor(44, 62, 80)
r.font.size = Pt(6)

add_para("", indent=False, space_after=18)
add_para("Prepare par : Ranim Nefzy", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=4)
add_para("Encadree par : Nesrine Walha", size=14, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Cm(0)
r = p.add_run("━" * 50)
r.font.color.rgb = RGBColor(44, 62, 80)
r.font.size = Pt(6)

add_para("", indent=False, space_after=12)
add_para("Annee Universitaire 2025/2026", bold=True, size=16, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

page_break()

# ---- DEDICACE ----
add_para("DEDICACE", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)
add_para("")
add_para("Je dedie ce travail a mes parents, qui m'ont toujours soutenu et encourage tout au long de mon parcours academique. Leur amour, leur patience et leurs sacrifices ont ete le moteur de ma reussite.")
add_para("A mes professeurs, pour leur devouement et la qualite de leur encadrement.")
add_para("A tous mes amis et collegues, pour leur soutien et leurs encouragements.")
page_break()

# ---- REMERCIEMENTS ----
add_para("REMERCIEMENTS", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)
add_para("")
add_para("Je tiens tout d'abord a exprimer ma profonde gratitude envers mon encadrante academique, Mme Nesrine Walha, pour sa disponibilite, ses precieux conseils et son accompagnement tout au long de ce projet. Sa patience et son expertise ont ete d'une grande aide pour mener a bien ce travail.")
add_para("Je remercie egalement tous mes professeurs a l'Institut des Nouvelles Technologies pour la qualite de la formation qu'ils m'ont offerte et pour leur soutien tout au long de mon parcours.")
add_para("Un grand merci a mon pere, Adel Nefzi, et a ma mere, Latifa Troudi, pour leur amour inconditionnel, leur soutien constant et leurs sacrifices tout au long de mes etudes. C'est grace a eux que j'ai pu arriver jusqu'ici.")
add_para("Je remercie egalement mon cher frere, Mohamed, pour ses encouragements et sa presence a mes cotes dans les moments difficiles.")
add_para("Enfin, je remercie toutes les personnes qui ont contribue, de pres ou de loin, a la realisation de ce projet, notamment les testeurs qui ont accepte d'evaluer l'application.")
page_break()

# ---- RESUME ----
add_para("RESUME", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)
add_para("Ce rapport presente la conception et le developpement d'Urbain Sustainability System, une plateforme web intelligente de signalement et de gestion des problemes urbains destinee aux citoyens et aux administrations municipales. Face a l'urbanisation croissante et a la complexification de la gestion des villes, notre solution propose une approche integree combinant intelligence artificielle, notifications automatiques et analytics en temps reel. Le systeme permet aux citoyens de signaler des problemes (nids-de-poule, eclairage defectueux, depots sauvages, etc.) via une interface cartographique interactive, tandis que l'IA classifie automatiquement les signalements avec une precision de 85 %, evalue leur priorite et les assigne aux secteurs municipaux competents. L'architecture du systeme repose sur une stack technologique moderne : backend Python/FastAPI, frontend React 19/TypeScript avec cartographie interactive, et un pipeline IA pour la classification automatique. Le systeme integre un module de notifications multi-canaux (Email, SMS, WhatsApp) pour informer les citoyens en temps reel. Developpe selon la methodologie Agile/Scrum sur 4 mois (6 sprints), le systeme a ete valide par des scenarios de test couvrant l'ensemble des fonctionnalites.")
add_para("")
add_para("Mots-cles : Smart City, Signalement Urbain, Intelligence Artificielle, FastAPI, React, Notifications Multi-canaux, Classification NLP, Geolocalisation.", bold=True)
page_break()

# ---- LISTE DES ABREVIATIONS ----
add_para("LISTE DES ABREVIATIONS", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)
abbrevs = [
    ("API", "Application Programming Interface"), ("ASGI", "Asynchronous Server Gateway Interface"),
    ("CI/CD", "Continuous Integration / Continuous Deployment"), ("CRUD", "Create, Read, Update, Delete"),
    ("DBSCAN", "Density-Based Spatial Clustering of Applications with Noise"), ("FCM", "Firebase Cloud Messaging"),
    ("GPS", "Global Positioning System"), ("HTTP", "Hypertext Transfer Protocol"),
    ("IA", "Intelligence Artificielle"), ("IoT", "Internet of Things"),
    ("JSON", "JavaScript Object Notation"), ("JWT", "JSON Web Token"),
    ("KPI", "Key Performance Indicator"), ("LRU", "Least Recently Used"),
    ("ML", "Machine Learning"), ("NLP", "Natural Language Processing"),
    ("ONU", "Organisation des Nations Unies"), ("ORM", "Object-Relational Mapping"),
    ("PFE", "Projet de Fin d'Etudes"), ("RBAC", "Role-Based Access Control"),
    ("REST", "Representational State Transfer"), ("SLA", "Service Level Agreement"),
    ("SMTP", "Simple Mail Transfer Protocol"), ("SQL", "Structured Query Language"),
    ("TF-IDF", "Term Frequency - Inverse Document Frequency"), ("TIC", "Technologies de l'Information et de la Communication"),
    ("UML", "Unified Modeling Language"), ("UI/UX", "User Interface / User Experience"),
]
create_table(["Abreviation", "Signification"], abbrevs)
page_break()

# ---- LISTE DES FIGURES ----
add_para("LISTE DES FIGURES", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)
figs = [
    "Figure 1 : Architecture Globale du Systeme Urbain",
    "Figure 2 : Diagramme de Cas d'Utilisation General",
    "Figure 3 : Diagramme de Classes UML",
    "Figure 4 : Diagramme de Sequence - Envoi d'une Notification",
    "Figure 5 : Diagramme d'Etats - Cycle de Vie d'un Signalement",
    "Figure 6 : Fonctionnalites par Profil d'Utilisateur",
    "Figure 7 : Pipeline IA - Classification, Priorisation et Prediction",
    "Figure 8 : Tableau de Bord Administrateur",
    "Figure 9 : Diagramme de Flux de Donnees",
    "Figure 10 : Architecture du Systeme de Notification Multicanal",
    "Figure 11 : Diagramme de Gantt - Planning du Projet",
    "Figure 12 : Workflow de Traitement d'un Signalement",
    "Figure 13 : Captures d'Ecran des Principales Interfaces",
    "Figure 14 : Architecture Physique du Systeme",
    "Figure 15 : Page de Connexion",
    "Figure 16 : Analyse IA detaillee d'un Signalement",
    "Figure 17 : Creation d'un Signalement",
    "Figure 18 : Detail d'un Signalement avec Analyse IA",
    "Figure 19 : Carte Interactive des Signalements",
    "Figure 20 : Pipeline d'Intelligence Artificielle",
]
for f in figs:
    add_para(f"     {f}", indent=False, space_after=4)
page_break()

# ---- LISTE DES TABLEAUX ----
add_para("LISTE DES TABLEAUX", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)
tbls_list = [
    "Tableau 1 : Stack Technologique du Projet",
    "Tableau 2 : Comparaison des Solutions Existantes",
    "Tableau 3 : Acteurs du Systeme et leurs Permissions",
    "Tableau 4 : Dictionnaire des Donnees",
    "Tableau 5 : Environnement de Developpement",
    "Tableau 6 : Correspondance entre Besoins Fonctionnels et Fonctionnalites Implementees",
]
for t in tbls_list:
    add_para(f"     {t}", indent=False, space_after=4)
page_break()

# ---- SOMMAIRE AUTOMATIQUE ----
add_para("SOMMAIRE", bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=24)
add_toc()

# Indication pour l'utilisateur
add_para("")
add_para("NB : Pour generer le sommaire, faites un clic droit sur le texte ci-dessus", italic=True, size=10, indent=False, space_after=2)
add_para("et selectionnez « Mettre a jour les champs » > « Mettre a jour toute la table ».", italic=True, size=10, indent=False, space_after=2)

page_break()

# ============================================================
# INTRODUCTION GENERALE (première section avec chiffres arabes)
# ============================================================
new_main_section("Introduction Generale")

# Titre avec design
add_main_title("INTRODUCTION GENERALE")

add_para("")
add_para("L'urbanisation rapide constitue l'un des defis majeurs du XXIe siecle. Selon le rapport *World Urbanization Prospects 2018* du Departement des Affaires Economiques et Sociales des Nations Unies, 55 % de la population mondiale residait en zone urbaine en 2018, et cette proportion devrait atteindre 68 % d'ici 2050, ce qui represente 2,5 milliards de nouveaux urbains supplementaires. Cette croissance exponentielle exerce une pression considerable sur les infrastructures municipales et les services publics : selon la Banque Mondiale, les villes consomment deja 78 % de l'energie mondiale et produisent 60 % des emissions de gaz a effet de serre. Les municipalites doivent faire face a une multiplication des problemes urbains — degradation des voiries, dysfonctionnement de l'eclairage public, accumulation de dechets, problemes d'assainissement — dans un contexte de ressources budgetaires et humaines contraintes.")

add_para("Dans ce contexte, la notion de « Smart City » ou « Ville Intelligente » emerge comme un paradigme prometteur pour repenser la gestion urbaine. L'Union Internationale des Telecommunications (ITU) definit la Smart City comme « une ville innovante qui utilise les TIC pour ameliorer la qualite de vie, l'efficacite des operations et des services urbains, et la competitivite, tout en repondant aux besoins des generations presentes et futures ». Ce concept repose sur l'integration des technologies de l'information et de la communication pour ameliorer la qualite des services urbains, optimiser l'utilisation des ressources et renforcer la participation citoyenne.")
add_para("C'est dans ce contexte que s'inscrit notre projet de fin d'etudes, intitule « Urbain Sustainability System », qui vise a concevoir et developper une plateforme web intelligente repondant aux lacunes identifiees dans la gestion des signalements urbains.")

add_para("La problematique centrale de ce projet peut etre formulee ainsi : comment concevoir et developper une plateforme intelligente, centralisee et multi-canal permettant aux citoyens de signaler efficacement les problemes urbains, et aux administrations municipales de les traiter de maniere automatisee, priorisee et tracable, en tirant parti des technologies d'intelligence artificielle, de geolocalisation et de notifications en temps reel ?")

add_para("Les objectifs de ce projet sont multiples et couvrent l'ensemble du cycle de vie d'un systeme d'information. Premierement, concevoir une architecture logicielle robuste garantissant la maintenabilite et l'evolutivite du systeme. Deuxiemement, developper une API RESTful complete couvrant l'authentification, la gestion des signalements, des utilisateurs, des categories, des notifications multi-canaux, des analytics et de l'intelligence artificielle. Troisiemement, implementer un pipeline d'intelligence artificielle pour la classification automatique des signalements, l'evaluation de la priorite et la detection d'anomalies. Quatriemement, developper un systeme de notifications multi-canaux robuste supportant l'envoi individuel et groupe via Email, SMS et WhatsApp. Cinquiemement, fournir une interface d'administration complete avec tableaux de bord, indicateurs de performance et generation de rapports.")

add_para("Le present rapport est structure en cinq chapitres complementaires. Le premier chapitre presente le contexte general du projet et l'etat de l'art des solutions existantes et des technologies utilisees sur le marche des Smart Cities. Le deuxieme chapitre detaille l'analyse et la specification des besoins fonctionnels et non fonctionnels, avec la modelisation des acteurs, des cas d'utilisation et leur specification detaillee. Le troisieme chapitre expose la conception architecturale du systeme, incluant l'architecture en couches, le modele de donnees conceptuel et relationnel, les diagrammes UML (classes, sequence, etats-transitions) et la conception des services metier. Le quatrieme chapitre decrit l'implementation du backend FastAPI, du frontend React et du systeme de notification multi-canaux. Enfin, le cinquieme chapitre presente l'evaluation du systeme et les perspectives d'amelioration. Une conclusion generale synthetise les travaux realises, met en valeur les contributions et ouvre des perspectives d'amelioration et d'extension du systeme.")

page_break()

# ============================================================
# CHAPITRE 1 : CONTEXTE ET ETAT DE L'ART
# ============================================================
new_main_section("Chapitre 1 : Contexte et Etat de l'Art")
add_chapter_title("CONTEXTE ET ETAT DE L'ART", number=1)

add_para("")
add_para("Introduction", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre pose les fondements theoriques et contextuels de notre projet. Nous y presentons le cadre general des Smart Cities et leurs enjeux, analysons les solutions existantes sur le marche des plateformes de signalement citoyen, etudions les technologies cles du domaine et leurs justifications, et definissons clairement le positionnement innovant de notre solution par rapport a l'existant. Enfin, nous detaillons la methodologie de developpement Scrum adoptee tout au long du projet ainsi que la planification des sprints.")

# 1.1
add_section_title("Cadre du projet : Smart Cities et gestion des signalements urbains")
add_para("La Smart City, ou Ville Intelligente, est un concept qui designe une ville utilisant les technologies de l'information et de la communication (TIC) pour ameliorer la qualite des services urbains, reduire les couts et la consommation de ressources, et engager plus efficacement les citoyens dans la gestion de leur cadre de vie. Selon l'Union Internationale des Telecommunications (UIT), une Smart City se definit comme « une ville innovante qui utilise les TIC pour ameliorer la qualite de vie, l'efficacite des operations et des services urbains, et la competitivite, tout en repondant aux besoins des generations presentes et futures ». Ce concept repose sur six piliers fondamentaux interconnectes : l'economie intelligente (smart economy), la mobilite intelligente (smart mobility), l'environnement intelligent (smart environment), les citoyens intelligents (smart people), le mode de vie intelligent (smart living) et l'administration intelligente (smart governance).")
add_para("Dans le cadre de notre projet, nous nous interessons particulierement a l'administration intelligente et a l'environnement intelligent. La gestion des signalements urbains constitue un aspect critique de l'administration municipale, car elle impacte directement la qualite de vie des citoyens et l'efficacite des services publics. Une gestion inefficace peut entrainer des delais de traitement excessifs, un gaspillage de ressources budgetaires et humaines, une insatisfaction citoyenne croissante et une degradation acceleree des infrastructures municipales. Selon une etude de la Banque Mondiale, les villes qui investissent dans des solutions numeriques de gestion urbaine constatent une reduction moyenne de 30 % des delais de traitement et une augmentation de 45 % de la satisfaction citoyenne.")
add_para("Le processus traditionnel de gestion des signalements urbains dans de nombreuses municipalites souffre de lacunes structurelles importantes : absence de canaux numeriques de signalement (recours au telephone ou au guichet physique), processus papier non tracables et vulnerables aux pertes, absence d'automatisation dans l'acheminement et la priorisation des requetes, difficulte de suivi et de reporting pour les citoyens comme pour les agents, et absence d'outils d'aide a la decision bases sur les donnees historiques. Ces limitations entrainent une inefficacite operationnelle significative et une insatisfaction citoyenne chronique.")
add_para("En Tunisie, le contexte municipal est marque par une transformation numerique progressive mais inegale entre les regions. La Loi organique n° 2018-29 du 9 mai 2018 relative au Code des collectivites locales a renforce considerablement les competences des municipalites en matiere de gestion des services publics locaux, creant un besoin accru d'outils de gestion modernes, performants et transparents. Cependant, la plupart des 350 municipalites tunisiennes disposent de moyens techniques limites et de processus de gestion encore largement manuels, ce qui rend notre proposition de plateforme intelligente particulierement pertinente dans ce contexte.")
add_para("Le paysage numerique tunisien a connu des avancees significatives ces dernieres annees avec le lancement de plusieurs initiatives gouvernementales : la strategie Tunisie Digitale 2025 visant a accelerer la transformation numerique de l'administration, la plateforme E-US (E-Administration et Services) pour la dematerialisation des procedures administratives, et le programme Ville Intelligente pilote dans les municipalites de Tunis, Sousse et Sfax. Cependant, ces initiatives restent largement descendantes et ne proposent pas d'outils operationnels pour la gestion quotidienne des problemes urbains par les citoyens et les agents municipaux. Notre systeme vient combler ce vide en offrant une solution concrete, deployable et adaptee au contexte local. Le choix d'une architecture open source et modulaire permet en outre une adoption progressive par les municipalites de toutes tailles, des grandes agglomerations disposant de services informatiques aux petites municipalites rurales aux ressources limitees, qui pourraient beneficier d'un deploiement mutualise a l'echelle regionale.")

# 1.2
add_section_title("Analyse des solutions existantes")
add_para("Nous avons analyse et compare les principales solutions existantes sur le marche des plateformes de signalement citoyen, en nous basant sur huit criteres d'evaluation : le type de licence, les fonctionnalites IA, les canaux de notification supportes, les capacites analytics, la cartographie interactive, la gestion des utilisateurs et des roles, l'architecture technique, et la facilite de deploiement et de personnalisation.")
add_para("FixMyStreet est une plateforme open source britannique developpee par mySociety, qui permet aux citoyens de signaler des problemes via une carte interactive. Elle propose un workflow de base avec des notifications par email et un systeme de suivi simple. Ses limites principales resident dans l'absence totale de fonctionnalites d'intelligence artificielle, des canaux de notification limites au seul email, l'absence de dashboard analytics, et des options de configuration restreintes. Cependant, son caractere open source et sa communaute active constituent des atouts non negligeables.")
add_para("SeeClickFix est une solution commerciale americaine deployee dans plus de 200 villes. Elle offre une application mobile et web complete avec cartographie, notifications email et push, et un systeme d'alerte. Ses inconvenients majeurs incluent l'absence d'IA integree pour la classification automatique, son modele proprietaire avec abonnement payant, l'impossibilite de personnaliser le pipeline de traitement, et la dependance vis-a-vis d'un fournisseur unique.")
add_para("CitySourced est une plateforme mobile-first orientee signalement citoyen, deployee principalement en Amerique du Nord. Elle propose une interface mobile simple et intuitive, mais ne dispose pas de dashboard analytics complet, n'integre pas de capacites d'IA, offre des options de deploiement tres limitees et ne permet pas la configuration de workflows personnalises.")

add_table("Tableau 2 : Comparaison des solutions existantes",
    ["Critere", "FixMyStreet", "SeeClickFix", "CitySourced", "Urbain Sustainability"],
    [
        ["Licence", "Open Source (BSD)", "Proprietaire", "Proprietaire", "Open Source (MIT)"],
        ["IA / Classification", "Aucune", "Aucune", "Aucune", "Classification et priorisation automatiques"],
        ["Notifications", "Email uniquement", "Email + Push", "Push mobile", "Email, SMS, WhatsApp, Push, In-App"],
        ["Analytics / Reporting", "Aucun", "Dashboard basique", "Aucun", "Dashboard complet + hotspots + predictions"],
        ["Cartographie", "Oui (OpenStreetMap)", "Oui", "Oui", "Oui (Leaflet + clusters + heatmap)"],
        ["Gestion des roles", "Citoyen + Admin", "Citoyen + Agent", "Citoyen + Admin", "Citoyen, Agent sectoriel, Admin, SuperAdmin"],
        ["Architecture", "Monolithique", "SaaS (cloud)", "Mobile-first", "Modulaire, API REST, Clean Architecture"],
        ["Personnalisation", "Limitee", "Configuration fixe", "Limitee", "Workflows, priorites, categories, templates"]
    ])

add_figure_image(2, "Diagramme de Cas d'Utilisation General")
add_para("Face aux limitations de ces solutions, notre positionnement se distingue par une combinaison unique de fonctionnalites : un pipeline IA complet integre pour la classification et la priorisation automatiques des signalements ; un systeme de notifications multi-canaux (Email, SMS, WhatsApp, Push) avec mecanisme de retry intelligent ; des analytics avances avec detection de hotspots geographiques, prediction de tendances, et indicateurs de performance sectoriels ; une architecture modulaire et scalable avec API RESTful complete ; et une solution open source et personnalisable.")

# 1.3
add_section_title("Technologies et outils du marche")
add_para("Le choix des technologies a ete guide par les besoins du projet et les standards du marche. Pour le backend, nous avons choisi Python avec FastAPI, un framework moderne et performant pour creer des API web. La base de donnees PostgreSQL a ete selectionnee pour sa fiabilite et son support des donnees geographiques necessaires a la cartographie des signalements.")
add_para("Pour le frontend, React est le framework le plus utilise pour les applications web modernes. TypeScript apporte de la securite au code en detectant les erreurs avant l'execution. Leaflet permet d'afficher des cartes interactives directement dans le navigateur sans avoir recours a des services payants.")

add_table("Tableau 1 : Stack Technologique du Projet",
    ["#", "Categorie", "Technologie", "Version", "Usage"],
    [
        ["1", "Frontend (Framework)", "React", "19.0", "Application web interactive"],
        ["2", "Frontend (Langage)", "TypeScript", "5.6", "Code plus sur et maintenable"],
        ["3", "Frontend (CSS)", "Tailwind CSS", "3.4", "Design moderne et adaptatif"],
        ["4", "Frontend (Carte)", "Leaflet / React-Leaflet", "4.2", "Cartes interactives legeres"],
        ["5", "Frontend (Graphiques)", "Recharts", "2.12", "Graphiques et diagrammes"],
        ["6", "Backend (Framework)", "FastAPI", "0.115", "API rapide et performante"],
        ["7", "Backend (Auth)", "JWT", "—", "Authentification securisee"],
        ["8", "Backend (ORM)", "SQLAlchemy", "2.0", "Acces a la base de donnees"],
        ["9", "Backend (Validation)", "Pydantic", "2.10", "Validation des donnees"],
        ["10", "Database", "PostgreSQL", "15", "Base de donnees relationnelle"],
        ["11", "Cache", "Redis", "7.2", "Cache et files d'attente"],
        ["12", "IA / ML", "Python", "—", "Classification et analyse"],
        ["13", "Taches background", "Celery", "5.4", "Traitements en arriere-plan"],
        ["14", "Conteneurisation", "Docker Compose", "27.0 + 2.28", "Deploiement simplifie"],
        ["15", "Tests", "pytest", "8.3", "Tests unitaires et d'integration"],
        ["16", "Migration DB", "Alembic", "1.13", "Gestion des versions DB"],
        ["17", "CI/CD", "GitHub Actions", "—", "Tests automatises"],
        ["18", "Template Email", "Jinja2", "3.1", "Emails personnalisables"]
    ])

# 1.4
add_section_title("Methodologie de developpement")
add_para("Nous avons adopte la methodologie Agile Scrum pour le developpement de ce projet. Le choix de Scrum se justifie par la nature complexe et iterative du projet, la necessite de livrer des increments fonctionnels reguliers, la flexibilite face aux changements de specifications, et la focalisation sur la valeur metier.")
add_para("Le projet a ete organise en 6 sprints de 2 a 3 semaines chacun sur une periode de 4 mois. Le Sprint 0 a ete consacre a la mise en place de l'environnement de developpement et de la base de donnees. Les Sprints 1 et 2 ont couvert le developpement des fonctionnalites de base : signalements, categories, utilisateurs et notifications. Les Sprints 3 et 4 ont ete dedies au pipeline IA de classification et au tableau de bord analytics. Enfin, le Sprint 5 a ete consacre a l'interface d'administration et a la finalisation du systeme.")

add_figure_image(11, "Diagramme de Gantt - Planning du Projet")

add_para("Conclusion", bold=True, size=14, indent=False, space_after=10)
add_para("Ce premier chapitre nous a permis de poser le cadre theorique et contextuel de notre projet. Nous avons explore les concepts fondamentaux des Smart Cities, analyse les solutions existantes du marche et identifie leurs limites, etudie les technologies cles, et positionne notre solution comme une reponse innovante aux besoins non couverts. Le chapitre suivant detaille l'analyse et la specification des besoins de notre systeme.")

page_break()

# ============================================================
# CHAPITRE 2 : ANALYSE ET SPECIFICATION DES BESOINS
# ============================================================
new_main_section("Chapitre 2 : Analyse et Specification des Besoins")
add_chapter_title("ANALYSE ET SPECIFICATION DES BESOINS", number=2)

add_para("")
add_para("Introduction", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre presente une analyse approfondie et systematique des besoins fonctionnels et non fonctionnels de notre systeme Urbain Sustainability. Nous identifions formellement les acteurs du systeme, modelisons leurs interactions via un diagramme de cas d'utilisation UML, specifions en detail les cas d'utilisation principaux, et definissons les contraintes techniques et organisationnelles qui guideront la conception architecturale du chapitre suivant.")

add_section_title("Analyse des besoins fonctionnels")

add_para("L'analyse des besoins fonctionnels a ete menee selon une approche systematique, en identifiant huit modules fonctionnels principaux qui couvrent l'ensemble des exigences du systeme. Chaque module a fait l'objet d'une specification detaillee de ses fonctionnalites, entrees, sorties et regles de gestion associees.")

add_subsection_title("Module 1 : Gestion des utilisateurs et authentification")
add_para("Le systeme doit permettre l'inscription et la connexion securisee des utilisateurs avec trois profils distincts (citoyens, agents sectoriels, administrateurs). L'authentification repose sur un mecanisme JWT dual-token avec un token d'acces d'une duree de vie de 30 minutes et un token de rafraichissement valable 7 jours. Les fonctionnalites incluent l'inscription avec verification d'email par envoi de token, la connexion securisee avec hachage bcrypt des mots de passe, la reinitialisation du mot de passe via email avec token temporaire, la mise a jour du profil utilisateur, la modification des preferences de notification par canal (email/SMS/push active/desactive), et la possibilite de desactivation de compte par l'administrateur.")

add_subsection_title("Module 2 : Signalement des problemes urbains")
add_para("Le systeme doit permettre aux citoyens de creer des signalements complets avec titre (3-200 caracteres), description detaillee (10-2000 caracteres), localisation GPS precise (latitude/longitude avec validation de plage), adresse physique, categorie parmi 5 types predefinis, niveau de priorite initial, et pieces jointes multimedias (images JPEG/PNG max 10 Mo, documents PDF). Chaque signalement recoit un numero de reference unique au format SIG-AAAA-MM-NNNNNN (ex: SIG-2026-07-004523). Le workflow de statut couvre 9 etats distincts avec validation des transitions autorisees a chaque etape.")

add_subsection_title("Module 3 : Workflow de traitement et assignation")
add_para("Le systeme permet aux administrateurs d'assigner les signalements aux secteurs municipaux competents et aux agents sectoriels. Le workflow suit un cycle de vie complet avec des transitions validees par des regles metier strictes. Les agents sectoriels peuvent visualiser leurs signalements assignes, mettre a jour le statut avec validation des transitions autorisees, ajouter des notes internes et des resolutions detaillees, telecharger des medias de suivi (photos avant/apres), et marquer les signalements comme resolus. Les citoyens peuvent suivre l'evolution en temps reel via un tableau de bord personnel et fournir un feedback de satisfaction sur une echelle de 1 a 5 apres resolution.")

add_subsection_title("Module 4 : Notifications multi-canaux")
add_para("Le systeme integre un module de notifications robuste supportant 4 canaux de communication distincts. Le canal Email utilise le protocole SMTP via Gmail avec des templates Jinja2 personalises pour 6 types de messages (bienvenue, verification, reinitialisation, notification de signalement, mise a jour de statut, rapport). Le canal SMS utilise une chaine de fournisseurs configurable avec fallback automatique : TextBelt (API gratuite) → passerelle email-to-SMS → mock/console. Le canal WhatsApp utilise une bibliotheque d'automatisation pour le Web WhatsApp. Le canal Push s'appuie sur Firebase Cloud Messaging (FCM). Le systeme supporte l'envoi individuel, l'envoi groupe (tous citoyens, tous administrateurs, tous agents d'un secteur), et l'envoi personnalise avec adresse de contact explicite. Un mecanisme de retry intelligent avec backoff exponentiel est implemente : premier essai a 5 minutes, deuxieme a 15 minutes, troisieme a 45 minutes, avec un maximum de 3 tentatives.")

add_subsection_title("Module 5 : Intelligence artificielle et classification")
add_para("Le pipeline IA, declenche automatiquement a la creation de chaque signalement, effectue quatre traitements distincts. La classification categorielle analyse le texte du signalement pour le classer parmi 5 categories (Infrastructure, Environnement, Securite, Services, Administration) avec une precision de 85 %. L'evaluation de la priorite calcule un score d'urgence base sur la severite du probleme, son impact sur la population et le contexte. La detection d'anomalies identifie les signalements sortant des normes statistiques pour une revue manuelle. La prediction de tendances estime les volumes futurs de signalements sur des horizons de 7, 30 et 90 jours.")

add_subsection_title("Module 6 : Analytics et reporting")
add_para("Le systeme offre un tableau de bord administrateur complet avec des indicateurs de performance en temps reel. Les KPIs affiches incluent le total des signalements, le nombre de nouveaux signalements du jour, le taux de resolution, le temps moyen de reponse par priorite, et la satisfaction citoyenne moyenne. Des analyses avancees permettent la visualisation des tendances temporelles par periode (journaliere, hebdomadaire, mensuelle), la detection de hotspots geographiques via clustering DBSCAN, l'evaluation des performances sectorielles avec 4 metriques (taux de resolution, temps de reponse moyen, satisfaction, score d'efficacite), et la generation de rapports synthetiques exportables.")

add_subsection_title("Module 7 : Cartographie interactive et geolocalisation")
add_para("Le systeme integre une carte interactive basee sur Leaflet avec fonctionnalites de geocodage (conversion adresse → coordonnees via API Google Maps), geocodage inverse (coordonnees → adresse), generation de heatmap d'intensite pour visualiser les zones a forte concentration de signalements, clustering dynamique des signaux selon le niveau de zoom, recherche de signalements a proximite d'un point donne (rayon configurable), et requetes spatiales par limites geographiques (bounding box).")

add_subsection_title("Module 8 : Administration et configuration")
add_para("Le systeme permet la gestion complete des utilisateurs (CRUD, activation/desactivation, recherche), des categories (hierarchiques avec parent, sous-categories, ordre de tri), des priorites (avec niveaux SLA, delais de resolution, couleur et icone), des secteurs municipaux (9 types : eau, routes, dechets, eclairage, espaces verts, batiments, securite, environnement, administration), et des signalements (consultation, reassignation, restauration de signaux soft-deleted). Le module offre egalement la visualisation des logs d'audit avec filtrage par action, entite, utilisateur et date, la surveillance de l'etat de sante du systeme, et la gestion des workflows d'escalade des signalements depassant les SLA.")

add_section_title("Analyse des besoins non fonctionnels")
add_para("Les besoins non fonctionnels definissent les contraintes de qualite que le systeme doit respecter. Nous avons identifie six categories principales que nous detaillons ci-apres avec leurs criteres de mesure et de validation respectifs.")

add_subsection_title("Performance")
add_para("Le systeme doit repondre en moins de 200 ms pour les requetes API standards mesurees au 95e percentile, un objectif atteignable grace a l'architecture asynchrone FastAPI et SQLAlchemy async. Toutes les listes de donnees doivent supporter la pagination avec des parametres de limite par defaut (20 elements) et maximum (100 elements). Un cache LRU in-memory avec TTL configurable de 300 secondes est implemente pour reduire les acces redondants a la base de donnees, avec un taux de hit cible superieur a 70 %. Un mecanisme de rate limiting protege l'API avec une fenetre glissante de 60 secondes et une limite de 60 requetes par minute par adresse IP.")

add_subsection_title("Securite")
add_para("L'authentification JWT utilise une signature HMAC-SHA256 avec une cle secrete de 256 bits, chaque token contenant les claims standard (iss, sub, exp, iat) et personnalises (role, nom). Les mots de passe sont haches avec bcrypt avec un facteur de cout de 12 rounds de salage. Le controle d'acces RBAC definit une matrice de 36 permissions pour l'administrateur, 10 pour l'agent sectoriel et 4 pour le citoyen, chaque permission etant verifiee a chaque appel API via les dependances FastAPI (get_current_admin, get_current_sector_user). Toutes les entrees utilisateur sont validees et assainies via les schemas Pydantic, offrant une protection integree contre les injections XSS et SQL.")

add_subsection_title("Scalabilite et disponibilite")
add_para("La scalabilite du systeme est assuree par une architecture backend sans etat (stateless), permettant d'ajouter des serveurs supplementaires si le nombre d'utilisateurs augmente. La disponibilite est garantie par des mecanismes de verification automatique de l'etat de chaque service et un redemarrage automatique en cas de panne. La base de donnees PostgreSQL assure la durabilite des donnees grace a son systeme de journalisation integre, permettant de recuperer les informations meme apres un incident technique.")

add_subsection_title("Maintenabilite et compatibilite")
add_para("La maintenabilite est facilitee par l'architecture en couches strictes (4 couches avec des responsabilites clairement separees), le typage fort (TypeScript 6.0 cote frontend, Pydantic v2 et annotations Python cote backend), la documentation automatique via Swagger/OpenAPI accessible a l'adresse /docs, et une suite de tests automatises avec pytest et pytest-cov pour le suivi de la couverture de code. Enfin, la compatibilite est assuree avec les navigateurs modernes (Chrome 90+, Firefox 88+, Edge 90+, Safari 14+) et les terminaux mobiles via un design responsive concu avec Tailwind CSS, garantissant une experience utilisateur optimale sur ecrans de toutes tailles (320 px a 2560 px de largeur).")

add_section_title("Modelisation des acteurs")
add_para("Nous avons identifie et modelise quatre acteurs principaux interagissant avec le systeme, chacun possedant un perimetre de responsabilite et des droits d'acces specifiques. Le Citoyen constitue l'acteur principal du systeme : il peut creer un compte, se connecter, signaler des problemes urbains avec localisation et photos, suivre l'evolution de ses signalements en temps reel, fournir un feedback de satisfaction apres resolution, et modifier son profil et ses preferences de notification. L'Agent sectoriel est responsable du traitement des signalements : il peut visualiser la liste des signalements assignes a son secteur, examiner les details et pieces jointes, mettre a jour le statut selon le workflow autorise, ajouter des notes de traitement et des medias de resolution, et marquer les signalements comme resolus. L'Administrateur possede les droits les plus etendus : il gere les utilisateurs, categories, priorites et secteurs, configure les parametres systeme, envoie des notifications individualisees ou groupees, consulte les analytics et les rapports, visualise les logs d'audit, et peut escalader les signalements critiques. Enfin, le Systeme agit comme un acteur autonome : il execute automatiquement le pipeline de classification IA a la creation de chaque signalement, declenche les notifications selon les regles metier definies, verifie les SLA et initie les escalades necessaires, et effectue le nettoyage periodique des notifications expirees.")

# Re-number since we added a table above in Ch1
add_table("Tableau 3 : Acteurs du Systeme et leurs Permissions",
    ["Acteur", "Role", "Permissions principales", "Cas d'utilisation associes"],
    [
        ["Citoyen", "Habitant de la municipalite", "Creer un signalement, consulter la carte, suivre ses signalements, fournir un feedback", "UC-01, UC-02, UC-05"],
        ["Agent sectoriel", "Employe municipal d'un secteur", "Consulter les signalements assignes, traiter les signalements, mettre a jour le statut, ajouter des notes", "UC-02, UC-03, UC-05"],
        ["Administrateur", "Gestionnaire du systeme", "Gerer les utilisateurs, categories, priorites, secteurs, envoyer des notifications, consulter les analytics", "UC-04, UC-05, UC-06, UC-07, UC-08"]
    ])

add_section_title("Specification detaillee des cas d'utilisation")
add_para("UC-01 : Signaler un probleme urbain. Le citoyen connecte navigue vers la page de creation de signalement, saisit le titre (3-200 caracteres) et la description (10-2000 caracteres), localise le probleme sur la carte interactive Leaflet par click ou par saisie d'adresse avec geocodage automatique, selectionne une categorie parmi les 5 types disponibles, ajoute des photos (format JPEG/PNG, max 10 Mo par fichier), puis soumet le formulaire. Le systeme valide les entrees, cree le signalement avec un numero de reference unique au format SIG-AAAA-MM-NNNNNN, execute automatiquement le pipeline IA de classification et de priorisation, notifie le citoyen par email de la confirmation de creation, et achemine le signalement vers le secteur municipal competent selon la categorie detectee. Le citoyen recoit un accusé de reception avec le numero de reference et peut suivre l'evolution en temps reel depuis son tableau de bord personnel.")
add_para("UC-02 : Consulter les signalements sur la carte interactive. Le citoyen ou l'agent accede a la vue carte, qui affiche l'ensemble des signalements sous forme de marqueurs clusters (groupes dynamiques selon le niveau de zoom). Chaque marqueur est code par couleur selon le statut (vert pour RESOLVED, orange pour IN_PROGRESS, rouge pour SUBMITTED). En cliquant sur un marqueur, une infobulle affiche le titre, la date, le statut et la categorie du signalement. L'utilisateur peut filtrer les signalements par categorie, statut, priorite, secteur et date, et visualiser la heatmap d'intensite pour identifier les zones a forte concentration de problemes urbains.")
add_para("UC-03 : Traiter un signalement. L'agent sectoriel connecte consulte la liste de ses signalements assignes, triee par priorite et par date de creation. Il selectionne un signalement, examine les details complets (description, photos, historique des transitions, notes internes), met a jour le statut selon les transitions autorisees par la machine a etats (ex: ASSIGNED vers IN_PROGRESS, puis IN_PROGRESS vers RESOLVED), ajoute des notes de traitement internes et des photos de resolution (avant/apres). A la resolution, le systeme notifie automatiquement le citoyen par email et SMS de la mise a jour, et l'invite a fournir un feedback de satisfaction sur une echelle de 1 a 5.")
add_para("UC-04 : Envoyer une notification individuelle ou groupee. L'administrateur accede a l'interface NotificationManagement, selectionne le type de destinataire (single_user, all_citizens, all_admins, sector_users, custom_email ou custom_phone), choisit le canal de diffusion (EMAIL, SMS, WHATSAPP, PUSH, IN_APP, WEBHOOK), saisit le titre et le message, et selectionne la priorite (LOW, NORMAL, HIGH, CRITICAL). Le systeme cree les enregistrements de notification avec le statut PENDING, tente la livraison via le fournisseur configure, met a jour le statut (SENT, DELIVERED ou FAILED) en temps reel, et applique le mecanisme de retry exponentiel (5 min, 15 min, 45 min) en cas d'echec. L'administrateur peut suivre les statistiques de livraison (taux de succes, taux d'echec, nombre en attente) depuis le tableau de bord.")
add_para("UC-05 : Analyser les tendances et les performances. L'administrateur consulte le tableau de bord analytics qui affiche 4 cartes KPI en temps reel (total signalements, nouveaux du jour, taux de resolution, temps moyen de reponse), un graphique d'evolution temporelle avec possibilite de selectionner la periode (7, 14, 30, 90 jours), un diagramme circulaire de repartition par categorie, et un tableau de performance sectorielle avec 4 indicateurs composites (taux de resolution, temps de reponse moyen, satisfaction citoyenne, score d'efficacite calcule). L'administrateur peut egalement visualiser la carte de chaleur des hotspots geographiques identifies par clustering DBSCAN, et generer des rapports de synthese exportables au format PDF.")

add_para("Conclusion", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre a presente une analyse exhaustive des besoins de notre systeme, en couvrant les aspects fonctionnels et non fonctionnels, les acteurs et leurs interactions, ainsi que les cas d'utilisation principaux. Cette analyse constitue le fondement de la conception architecturale presentee dans le chapitre suivant.")

page_break()

# ============================================================
# CHAPITRE 3 : CONCEPTION ARCHITECTURALE
# ============================================================
new_main_section("Chapitre 3 : Conception Architecturale")
add_chapter_title("CONCEPTION ARCHITECTURALE", number=3)

add_para("")
add_para("Introduction", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre presente la conception detaillee du systeme Urbain Sustainability en couvrant cinq aspects : l'architecture globale en couches et les fonctionnalites par profil d'utilisateur, la conception des donnees avec le dictionnaire des entites, la conception des services metier, les interactions entre composants via les diagrammes de sequence, et la machine a etats du cycle de vie d'un signalement.")

add_section_title("Architecture globale du systeme")
add_para("Notre systeme est organise en plusieurs couches bien separees, chacune ayant un role precis et clairement defini. La couche de presentation correspond au frontend (React avec Tailwind CSS et Leaflet pour les cartes) qui communique avec le serveur via des requetes HTTP standards. La couche API (FastAPI avec ses modules de routes) recoit les requetes, les valide et les transmet. La couche Service contient toute la logique metier — c'est ici que sont implantees les regles de gestion, l'orchestration des traitements et les decisions importantes. La couche Repository s'occuce uniquement de stocker et recuperer les donnees dans la base de donnees via SQLAlchemy et PostgreSQL. Cette organisation permet de tester chaque partie independamment, de modifier un composant sans casser les autres, et de faire evoluer le systeme facilement.")
add_para("Le flux de donnees suit un parcours simple mais efficace : le navigateur de l'utilisateur envoie une requete a l'API, qui verifie l'identite de l'utilisateur et transmet la demande au service concerne. Le service applique la logique metier et utilise le repository pour lire ou sauvegarder les donnees. La reponse suit le chemin inverse jusqu'a l'affichage dans le navigateur. Cette organisation en couches permet de maintenir un code clair et bien structure.")
add_para("Le systeme s'articule autour de trois profils d'utilisateurs ayant chacun des fonctionnalites adaptees a leurs besoins. Le Citoyen peut creer des signalements, consulter la carte interactive et suivre l'evolution de ses demandes. L'Agent sectoriel traite les signalements assignes a son secteur, met a jour leur statut et documente les resolutions. L'Administrateur configure le systeme (categories, priorites, secteurs), envoie des notifications groupees et consulte les indicateurs de performance. Chaque profil dispose d'une interface specifique qui lui presente uniquement les actions et informations pertinentes pour son role.")

add_figure_image(1, "Architecture Globale du Systeme Urbain")
add_figure_image(6, "Fonctionnalites par Profil d'Utilisateur")
add_para("Sur le plan physique, le systeme est concu pour fonctionner sur un seul serveur mutualisant les trois services (API, base de donnees et cache), accessible depuis Internet via un navigateur web. Les citoyens, agents et administrateurs se connectent depuis leurs appareils (ordinateur, smartphone) sans installation de logiciel supplementaire. Cette architecture simplifiee reduit les couts de deploiement et de maintenance, tout en garantissant un acces universel via une simple connexion Internet.", indent=False)
add_figure_image(14, "Architecture Physique du Systeme")

add_section_title("Conception des donnees")
add_para("La conception des donnees est un element essentiel de notre architecture. La base de donnees PostgreSQL comprend 9 tables principales qui stockent l'ensemble des informations du systeme. Chaque table est conçue pour garantir la coherence et la fiabilite des donnees. Par exemple, les colonnes de statut utilisent des types specifiques qui empechent les valeurs invalides, ce qui evite les erreurs de saisie et assure l'integrite des informations.")
add_para("La table Users contient les informations des utilisateurs : identite (nom, prenom, email), informations de connexion, role (citoyen, agent ou administrateur), et preferences de notification. La table Signals est la plus importante du systeme avec pres de 50 attributs. Elle stocke pour chaque signalement : la localisation geographique (latitude et longitude), la classification (categorie et priorite), le statut d'avancement, les resultats de l'analyse IA (scores de confiance, priorite, severite), l'impact (cout estime, nombre de personnes affectees), et les dates importantes (creation, assignation, resolution, fermeture).")

add_figure_image(3, "Diagramme de Classes UML")
add_figure_image(9, "Diagramme de Flux de Donnees")

add_table("Tableau 4 : Dictionnaire des Donnees",
    ["Entite", "Description", "Attributs principaux", "Relations"],
    [
        ["User", "Utilisateurs du systeme (citoyens, agents, admins)", "id, email, username, role (ENUM), status (ENUM), sector_id (FK)", "1:N Signal (created_by), 1:N Notification"],
        ["Signal", "Signalements de problemes urbains", "id, reference, title, lat/lng, status (ENUM), source (ENUM), ai_scores (JSON)", "N:1 User, N:1 Category, N:1 Priority"],
        ["Category", "Categories de signalements", "id, name, code, type (ENUM), parent_id (FK auto-ref), icon", "1:N Signal, N:1 Category (parent)"],
        ["Priority", "Priorites de traitement", "id, name, level (ENUM), max_response_time, color, ai_weight", "1:N Signal"],
        ["Sector", "Secteurs municipaux", "id, name, code, type (ENUM), manager, working_hours (JSON)", "1:N User"],
        ["Notification", "Notifications envoyees", "id, code, channel (ENUM), status (ENUM), retry_count, template (JSON)", "N:1 User, N:1 Signal"],
        ["Report", "Rapports generes", "id, code, type (ENUM), frequency (ENUM), stats (JSON)", "N:1 User (generated_by)"],
        ["AuditLog", "Traces d'audit", "id, action, entity_type, old/new_values (JSON), ip_address", "N:1 User"],
        ["PasswordResetToken", "Jetons de reinitialisation", "id, token_hash, expires_at, used", "N:1 User"]
    ])

add_section_title("Conception des services")
add_para("La couche service constitue le c ur de la logique metier du systeme, avec 16 classes de services specialisees reparties en quatre categories principales que nous detaillons ci-dessous.")

add_subsection_title("Service d'authentification et de gestion des utilisateurs")
add_para("Le service d'authentification gere l'inscription et la connexion des utilisateurs. Lorsqu'un citoyen cree un compte, un email de verification lui est envoye pour confirmer son adresse. La connexion est securisee par mot de passe, et le systeme genere un jeton de session temporaire (30 minutes) avec un jeton de rafraichissement (7 jours) pour eviter de saisir le mot de passe trop souvent. En cas d'oubli de mot de passe, un lien temporaire permet de le reinitialiser en toute securite.")

add_subsection_title("Service de notification multi-canaux")
add_para("Le service de notification est un composant important du systeme. Il permet d'envoyer des messages aux citoyens et aux agents via differents canaux : email, SMS, WhatsApp, notifications dans l'application, et appels webhooks. Le systeme supporte plusieurs types de notifications : alerte de nouveau signalement, mise a jour de statut, affectation a un agent, confirmation citoyenne, et rapports periodiques. En cas d'echec d'envoi, le systeme reessaie automatiquement (apres 5 minutes, puis 15 minutes, puis 45 minutes) pour maximiser les chances de livraison. Un suivi complet de chaque notification est assure avec son statut (en attente, envoye, delivre, lu, echoue, annule).")

add_subsection_title("Pipeline d'intelligence artificielle")
add_para("Le service IA execute un traitement en plusieurs etapes automatiques. Premierement, le texte du signalement est prepare et nettoye. Ensuite, le systeme classifie le signalement dans la categorie appropriee (voirie, eclairage, dechets, etc.) avec une bonne precision. Puis, il evalue le niveau de priorite en fonction de la gravite du probleme, de son urgence et de son impact sur les citoyens. Enfin, il detecte les cas inhabituels qui necessitent une attention particuliere et peut predire les tendances futures pour aider les municipalites a anticiper les besoins.")

add_subsection_title("Service d'analytics et de reporting")
add_para("Le service d'analytics offre plusieurs indicateurs utiles pour le pilotage du systeme : le nombre total de signalements, les nouveaux signalements du jour, le taux de resolution et le temps de reponse moyen. Il permet egalement de visualiser les tendances sur differentes periodes (7, 14, 30 et 90 jours), d'evaluer la performance de chaque secteur municipal, et de consulter la repartition des signalements par categorie. Le module cartographique identifie les zones geographiques les plus touchees par les problemes urbains, tandis que le rapport de synthese regroupe l'ensemble de ces informations pour une vue d'ensemble complete.")

add_figure_image(7, "Pipeline IA - Classification, Priorisation et Prediction")

add_section_title("Architecture de securite")
add_para("La securite du systeme est assuree a plusieurs niveaux. Pour l'authentification, nous utilisons des jetons securises (JWT) qui permettent aux utilisateurs de se connecter de maniere fiable. Les mots de passe sont stockes de facon securisee (haches) pour proteger les donnees personnelles. Chaque utilisateur dispose de droits d'acces specifiques selon son role : les citoyens peuvent creer des signalements, les agents peuvent les traiter, et les administrateurs ont acces a toutes les fonctionnalites de gestion. Toutes les donnees saisies par les utilisateurs sont validees avant d'etre traitees, ce qui empeche les erreurs et les tentatives d'intrusion. Les fichiers telecharges (photos, documents) sont egalement verifies pour garantir leur securite.")
add_para("La hierarchie des exceptions constitue un element cle de l'architecture de securite. Le systeme definit 13 types d'exceptions personnalisees heritant d'UrbainException : AuthenticationError (401), AuthorizationError (403), NotFoundError (404), ConflictError (409), ValidationError (422), BusinessLogicError (422), InvalidStateError (422), RateLimitError (429), FileUploadError (400), ExternalServiceError (503), ServiceUnavailableError (503), DatabaseError (500). Chaque exception est interceptee par un gestionnaire global et convertie en reponse JSON structuree contenant le code d'erreur, le message et les details optionnels.")

add_section_title("Diagrammes de sequence")
add_para("Nous avons modelise les interactions entre les differents composants du systeme a travers des diagrammes de sequence. Par exemple, le diagramme d'envoi de notification montre le deroulement complet : l'administrateur remplit le formulaire d'envoi depuis l'interface, la requete est transmise au serveur, le systeme cree un enregistrement de notification en base de donnees, puis tente la livraison via le canal choisi (email, SMS ou WhatsApp). Si la livraison reussit, le statut est mis a jour en consequence. En cas d'echec, le systeme reessaie automatiquement a plusieurs reprises avec des intervalles de temps croissants pour maximiser les chances de succes.")

add_figure_image(4, "Diagramme de Sequence - Envoi d'une Notification")

add_section_title("Machine a etats du signalement")
add_para("Le cycle de vie d'un signalement suit un parcours bien defini avec plusieurs etapes. Lorsqu'un citoyen cree un signalement, il commence en etat de brouillon (DRAFT) puis passe en soumis (SUBMITTED). Un agent sectoriel l'examine (UNDER_REVIEW), l'assigne a une equipe (ASSIGNED), commence le traitement (IN_PROGRESS), et enfin le resout (RESOLVED). Une fois resolu, il est ferme (CLOSED). Le signalement peut aussi etre annule ou rejete si necessaire. Chaque etape ne peut etre franchie que si les conditions sont remplies : par exemple, seul un agent assigne peut traiter un signalement, et la resolution necessite une description du travail effectue.")
add_para("Le systeme verifie automatiquement les delais de traitement. Si un signalement urgent n'est pas traite dans le temps imparti, une alarme est declenchee pour informer les superviseurs. Ce mecanisme garantit que les problemes les plus importants sont traites en priorite.")

add_figure_image(5, "Diagramme d'Etats - Cycle de Vie d'un Signalement")
add_figure_image(12, "Workflow de Traitement d'un Signalement")

add_para("Conclusion", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre a presente la conception architecturale de notre systeme Urbain Sustainability, couvrant l'architecture en couches, le modele de donnees avec ses tables et types, les services metier avec un focus sur l'authentification, les notifications, l'IA et les analytics, ainsi que les interactions entre composants et le cycle de vie des signalements. Cette conception constitue le plan directeur pour l'implementation presentee dans le chapitre suivant.")

page_break()

# ============================================================
# CHAPITRE 4 : IMPLEMENTATION ET REALISATION
# ============================================================
new_main_section("Chapitre 4 : Implementation et Realisation")
add_chapter_title("IMPLEMENTATION ET REALISATION", number=4)

add_para("")
add_para("Introduction", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre presente l'implementation concrete et detaillee du systeme Urbain Sustainability. Nous y decrivons l'environnement de developpement, l'organisation de la structure du projet, la realisation du backend API RESTful avec ses 16 modules, l'implementation du frontend React avec ses 30 pages, et le developpement du systeme de notification multi-canaux avec ses mecanismes de robustesse.")

add_section_title("Environnement de developpement")
add_para("Le developpement a ete realise sur des postes equipes de processeurs Intel Core i7-12700H (14 cœurs, 20 threads), 32 Go de RAM DDR5, et SSD NVMe 1 To. Le systeme d'exploitation utilise est Windows 11 Pro. L'environnement logiciel comprend Python 3.11.6 avec gestion des dependances via pip et virtualenv, Node.js 20.11 LTS avec npm 10, Docker Desktop 24.0 avec WSL2, PostgreSQL 15.2, et Redis 7.0. VS Code a ete utilise comme editeur principal avec les extensions Python Pylance, TypeScript ESLint, Prettier et Docker. Git 2.42 a servi pour le versionnement avec GitHub comme depot distant et GitHub Projects pour le suivi des taches Scrum.")

add_table("Tableau 5 : Environnement de Developpement",
    ["Composant", "Nom", "Version / Modele", "Role"],
    [
        ["Processeur", "Intel Core i7-12700H", "14 coeurs / 20 threads", "Developpement et execution backend"],
        ["Memoire RAM", "DDR5", "32 Go", "Execution de conteneurs et IDE"],
        ["Stockage", "SSD NVMe", "1 To", "Base de donnees et fichiers projet"],
        ["Systeme", "Windows 11 Pro", "23H2", "Environnement de developpement"],
        ["Editeur", "VS Code", "2024", "Code source avec extensions Python/TS"],
        ["Backend", "Python", "3.11.6", "Langage du backend FastAPI"],
        ["Frontend", "Node.js", "20.11 LTS", "Runtime JavaScript"],
        ["Conteneurs", "Docker Desktop", "24.0 + WSL2", "Environnement isole (3 conteneurs)"],
        ["Base de donnees", "PostgreSQL", "15.2", "Base principale du systeme"],
        ["Cache", "Redis", "7.0", "Cache et file d'attente"],
        ["Versionnement", "Git + GitHub", "2.42", "Gestion de code source et CI/CD"]
    ])

add_section_title("Architecture et organisation du Backend")
add_para("Le backend FastAPI est organise en plusieurs modules fonctionnels. Chaque module est responsable d'un domaine specifique : la gestion des utilisateurs, des signalements, des notifications, des categories, des priorites, des secteurs, des rapports, et de l'intelligence artificielle. Cette organisation permet de retrouver facilement le code correspondant a chaque fonctionnalite et facilite la maintenance.")
add_para("Le package core/ centralise la configuration du systeme : il lit les parametres depuis un fichier de configuration et fournit des valeurs par defaut pour l'ensemble des options. La connexion a la base de donnees est configuree de maniere optimale pour assurer des performances elevees. Le module de securite gere le hachage des mots de passe, la creation des jetons de connexion, et les controles d'acces aux differents endpoints de l'API. Un systeme de gestion des erreurs permet de retourner des reponses claires et structurees en cas de probleme.")
add_para("L'implementation du pipeline IA permet de traiter automatiquement chaque nouveau signalement. Le systeme nettoie d'abord le texte, puis le classifie dans la categorie appropriee avec une precision de 85 %. Un score de priorite est ensuite calcule en fonction de la severite, de l'urgence et de l'impact du probleme. Ce pipeline entierement automatique s'execute en quelques secondes a la creation de chaque signalement, sans intervention humaine.")

add_section_title("Structure et implementation du Frontend")
add_para("Le frontend React est organise en plusieurs couches interconnectees. La couche API gere la communication avec le serveur : elle ajoute automatiquement le jeton de connexion aux requetes, et en cas de session expiree, elle tente de renouveler le jeton de maniere transparente pour l'utilisateur. Ce mecanisme permet a l'utilisateur de rester connecte sans avoir a saisir son mot de passe trop souvent.")
add_para("Le systeme dispose de plusieurs services partages : un service d'authentification qui gere l'etat de connexion de l'utilisateur et propose les fonctions de connexion, inscription et deconnexion ; un service de notifications temporaires pour afficher des messages de confirmation ou d'erreur ; et un service de synchronisation qui conserve l'etat des onglets et des filtres entre les navigations.")
add_para("L'interface utilisateur comprend une trentaine de pages reparties en plusieurs sections : les pages d'authentification (connexion, inscription, mot de passe oublie), les pages de signalements (liste, detail, creation, edition, carte interactive), les pages d'administration (tableau de bord, gestion des utilisateurs, categories, priorites, secteurs, notifications, rapports, audit, IA, etat du systeme), et la page de profil utilisateur.")

add_para("Les figures suivantes presentent les principales interfaces utilisateur de l'application, telles qu'elles apparaissent apres la phase de developpement et d'amelioration du design.")

add_figure_image(15, "Page de Connexion")
add_para("La figure 15 presente la page de connexion de l'application. Le design split-screen offre une experience moderne : a gauche, un fond degrade bleu avec le logo Urbain et une breve description du systeme ; a droite, le formulaire de connexion avec les champs email et mot de passe. Cette page constitue le point d'entree unique pour tous les utilisateurs du systeme.")

add_figure_image(16, "Analyse IA detaillee d'un Signalement")
add_para("La figure 16 presente l'analyse IA detaillee accessible depuis la page de detail d'un signalement. En cliquant sur le bouton Analyser, l'utilisateur declenche le pipeline complet : classification automatique, evaluation de la priorite, detection d'anomalies, analyse de severite et generation de rapport. Les resultats s'affichent en temps reel dans des cartes thematiques avec scores de confiance et indicateurs visuels.")

add_figure_image(17, "Creation d'un Signalement")
add_para("La figure 17 illustre le formulaire de creation de signalement en 5 etapes (Informations, Localisation, Impact, Medias, Confirmation). L'indicateur de progression horizontal guide l'utilisateur pas a pas. Cette approche向导 simplifie la saisie et reduit les erreurs.")

add_figure_image(18, "Detail d'un Signalement avec Analyse IA")
add_para("La figure 18 presente la page de detail d'un signalement. On y voit les informations completes du signalement, les photos associees, et surtout le module d'analyse IA qui affiche les scores de confiance, priorite, severite et urgence. Les boutons d'action IA permettent de lancer des analyses supplementaires (classification, detection d'anomalies, generation de rapport).")

add_figure_image(19, "Carte Interactive des Signalements")
add_para("La figure 19 montre la carte interactive Leaflet avec le clustering des signalements par zone de densite. Les filtres lateraux permettent de selectionner par statut, categorie ou priorite. La barre laterale gauche affiche la liste des signalements a proximite avec survol interactif sur la carte.")

add_figure_image(8, "Tableau de Bord Administrateur")
add_para("La figure 8 presente le tableau de bord administrateur avec les indicateurs de performance (total signalements, taux de resolution, en attente, temps moyen), la repartition par statut et priorite, les temps de reponse, les predictions IA, et la performance des secteurs municipaux.")

add_figure_image(20, "Pipeline d'Intelligence Artificielle")
add_para("La figure 20 illustre le pipeline IA en 5 etapes qui traite automatiquement chaque signalement des sa creation : classification, evaluation de la priorite, detection d'anomalies, analyse de severite et generation de rapport. Ce pipeline s'execute en quelques secondes sans intervention humaine.")

add_section_title("Implementation detaillee du systeme de notification")
add_para("Le systeme de notification constitue un element cle du projet, avec plusieurs canaux de communication et un suivi complet des envois. Le service Email utilise le serveur SMTP de Gmail pour envoyer des messages personnalises. Six modeles d'emails sont disponibles : email de bienvenue, confirmation d'adresse, reinitialisation de mot de passe, notification de signalement, mise a jour de statut, et rapport periodique. Chaque email est personnalise avec le prenom du destinataire et les informations pertinentes.")
add_para("En cas d'echec d'envoi (identifiants invalides, serveur indisponible), le systeme ne bloque pas le fonctionnement general mais enregistre l'erreur et continue son execution. Le systeme limite les tentatives de connexion a 3 avec un delai entre chaque essai pour eviter de bloquer le compte Gmail. L'envoi en lot est gere par groupes de 50 destinataires pour respecter les limites des serveurs de messagerie.")
add_para("Pour les SMS, le systeme propose plusieurs options. Il peut utiliser une API en ligne gratuite, ou bien une methode alternative qui utilise le service Gmail pour envoyer des SMS via les passerelles des operateurs telephoniques (le telephone devient une adresse email speciale). Cette approche permet d'envoyer des SMS sans frais supplementaires et sans inscription a un service payant. Le systeme supporte les operateurs de plus de 30 pays et formate automatiquement les numeros avec le code de la Tunisie (+216) par defaut.")

add_figure_image(10, "Architecture du Systeme de Notification Multicanal")
add_figure_image(4, "Diagramme de Sequence - Envoi d'une Notification")

add_para("Conclusion", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre a presente l'implementation de l'ensemble du systeme Urbain Sustainability, en couvrant l'environnement de developpement, l'architecture du backend avec ses modules fonctionnels, la structure du frontend React, et le systeme de notifications multi-canaux. Le chapitre suivant presente l'evaluation globale du systeme et discute ses perspectives.")

page_break()

# ============================================================
# CHAPITRE 5 : EVALUATION DU SYSTEME ET DISCUSSION
# ============================================================
new_main_section("Chapitre 5 : Evaluation du Systeme et Discussion")
add_chapter_title("EVALUATION DU SYSTEME ET DISCUSSION", number=5)

add_para("")
add_para("Introduction", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre propose une evaluation globale du systeme Urbain Sustainability dans une perspective de gestion et d'integration organisationnelle. Apres un bref rappel des tests de validation, nous dressons un bilan fonctionnel complet de la couverture des besoins, analysons l'experience utilisateur de l'interface, discutons les choix technologiques effectues sous l'angle de leur adequation au contexte de gestion municipale, identifions les limites et contraintes du systeme, et presentons les perspectives d'amelioration et la feuille de route pour le deploiement au sein des municipalites tunisiennes.")

add_section_title("Bilan fonctionnel et validation")
add_para("Avant d'evaluer la couverture fonctionnelle du systeme, il convient de mentionner que l'ensemble des fonctionnalites developpees a ete soumis a une campagne de validation systematique. Des tests unitaires, d'integration et de validation ont ete executes sur l'ensemble des 16 modules du backend et des 30 pages du frontend, conformement aux pratiques de developpement logiciel standard. Les resultats de ces tests ont confirme le bon fonctionnement de chaque composant du systeme et la conformite des reponses API aux specifications definies dans la phase de conception.")
add_para("Le tableau ci-dessous presente une synthese de la correspondance entre les besoins fonctionnels identifies dans le chapitre 2 et les fonctionnalites effectivement implementees dans le systeme. Cette mise en correspondance demontre la couverture exhaustive de l'ensemble des exigences formulees en debut de projet.")

add_table("Tableau 6 : Correspondance entre Besoins Fonctionnels et Fonctionnalites Implementees",
    ["Module", "Besoins identifies (Ch.2)", "Fonctionnalites implementees", "Statut"],
    [
        ["1. Gestion des utilisateurs", "Inscription, connexion, profils, roles", "Auth JWT/OAuth2, 4 roles (CITIZEN/ADMIN/SECTOR/SUPER_ADMIN), profil avec avatar", "Complete"],
        ["2. Signalement urbain", "Creation, geolocalisation, photos", "Formulaire 3 etapes, carte Leaflet, geocodage, upload images (max 10 Mo)", "Complete"],
        ["3. Workflow de traitement", "Assignation, suivi, cycle de vie", "Machine a etats (9 etats, 12 transitions), SLA, escalade automatique", "Complete"],
        ["4. Notifications", "Multi-canaux, templates, retry", "4 canaux (Email/SMS/WhatsApp/Push), 6 templates Jinja2, retry exponentiel", "Complete"],
        ["5. Intelligence artificielle", "Classification, priorisation, prediction", "TF-IDF + Logistic Regression (85%), scoring multicritere, Isolation Forest", "Complete"],
        ["6. Analytics", "Indicateurs, tendances, hotspots", "4 KPIs temps reel, courbes periodes, clustering DBSCAN, rapports PDF", "Complete"],
        ["7. Cartographie", "Visualisation, filtres, heatmap", "Marqueurs clusters, filtres par statut/categorie, heatmap d'intensite", "Complete"],
        ["8. Administration", "Configuration, audit, logs", "CRUD categories/priorites/secteurs, audit trail complet, logs actions", "Complete"]
    ])

add_section_title("Evaluation de l'experience utilisateur")
add_para("L'interface utilisateur du systeme Urbain Sustainability a ete concue selon les principes de l'utilisabilite et de l'experience utilisateur (UX) adaptes a trois profils distincts : le citoyen, l'agent sectoriel et l'administrateur municipal. Pour le citoyen, le parcours de signalement a ete simplifie au maximum : apres authentification, la creation d'un signalement s'effectue en trois etapes (description et localisation, classification et pieces jointes, confirmation) avec un temps de saisie moyen estime a moins de deux minutes. La carte interactive Leaflet offre une visualisation intuitive des signalements a proximite, avec des marqueurs colores par statut et un clustering automatique adapte au niveau de zoom.")
add_para("Pour l'agent sectoriel, l'interface de gestion des signalements assignes a ete concue pour optimiser le traitement quotidien : liste triee par priorite et par date, acces rapide aux details du signalement avec historique complet des transitions, mise a jour de statut en un clic via un menu deroulant, et ajout de notes et photos de resolution. L'administrateur municipal dispose quant a lui d'un tableau de bord complet avec des indicateurs de performance en temps reel, des graphiques d'evolution, des cartes de chaleur geographiques et des outils de gestion des utilisateurs, categories, priorites et secteurs. L'ensemble de l'interface a ete developpee avec Tailwind CSS pour garantir un design responsive, adapte aussi bien aux ecrans de bureau qu'aux tablettes et smartphones utilises par les agents sur le terrain.")

add_section_title("Analyse critique des choix technologiques")
add_para("Le choix des technologies pour ce projet a ete guide par des criteres de pertinence pour le contexte de gestion municipale, de cout de maintenance et de facilite de prise en charge par des equipes techniques locales. Python a ete selectionne pour le backend en raison de sa grande popularite dans les ecoles d'informatique tunisiennes, de sa syntaxe lisible facilitant la maintenance, et de son ecosysteme riche pour le developpement web et l'intelligence artificielle. React et TypeScript ont ete choisis pour le frontend car ce sont les technologies les plus demandees sur le marche de l'emploi tunisien, ce qui facilite le recrutement de developpeurs pour la maintenance future du systeme.")
add_para("Le choix de PostgreSQL comme systeme de gestion de base de donnees se justifie par son caractere open source et sa fiabilite eprouvee dans les administrations publiques. L'architecture en couches a ete privilegiee car elle facilite la maintenance et l'evolution du systeme par des equipes de taille modeste, ce qui correspond au profil-type des services informatiques municipaux tunisiens.")

add_section_title("Limites et contraintes du systeme")
add_para("Le systeme Urbain Sustainability, bien que fonctionnel et couvrant l'ensemble des besoins identifies, presente certaines limites qui constituent des pistes d'amelioration. La principale limite reside dans le modele de classification IA, dont la precision de 85 % est satisfaisante pour un premier prototype mais pourrait etre amelioree par l'utilisation de modeles plus avances et par l'entrainement sur un jeu de donnees plus volumineux.")
add_para("Une deuxieme limite concerne la dependance vis-a-vis des services externes pour l'envoi de notifications : le service SMTP Gmail impose une limite de 500 emails par jour pour un compte gratuit, ce qui peut etre contraignant pour une municipalite de taille moyenne. Le service de messagerie WhatsApp repose sur le web WhatsApp et n'est donc pas adapte a un usage professionnel a grande echelle. Ces limitations pourraient etre levee par l'adoption de solutions professionnelles (SendGrid, Mailjet, Twilio) lors du deploiement en production.")
add_para("Enfin, le systeme n'inclut pas encore de module d'authentification a deux facteurs (2FA), de signature electronique des rapports, ni d'interface d'import/export de donnees au format ouvert (CSV, JSON, XML) pour l'interoperabilite avec les systemes d'information municipaux existants. L'absence de version mobile native constitue egalement une limite pour les citoyens qui ne disposent pas d'un acces permanent a un ordinateur.")

add_section_title("Perspectives d'amelioration et feuille de route")
add_para("A court terme (3 a 6 mois), nous recommandons le deploiement pilote du systeme dans une municipalite partenaire, avec un accompagnement et une formation des agents municipaux. Ce deploiement permettra de collecter les retours d'experience des utilisateurs reels et d'ajuster les fonctionnalites en fonction des besoins concrets du terrain. Parallelement, le developpement d'une application mobile native (React Native ou Flutter) avec capacite de signalement hors-ligne et synchronisation differee permettrait de toucher une base de citoyens plus large.")
add_para("A moyen terme (6 a 12 mois), l'enrichissement du pipeline IA avec des modeles de deep learning et l'analyse automatique des images (detection du type de probleme a partir des photos des citoyens) constituerait une amelioration significative. L'integration avec les systemes d'information geographique (SIG) municipaux existants, le developpement d'une API publique pour les developpeurs tiers, et la mise en place d'un module de reporting avance avec generation automatique de rapports periodiques pour les elus municipaux sont egalement des axes de developpement importants. Enfin, a plus long terme, l'extension du systeme a d'autres domaines de la smart city (gestion des transports, qualite de l'air, eclairage public intelligent) pourrait faire evoluer la plateforme vers un veritable hub urbain integre au service du developpement durable des territoires.")

add_para("Conclusion", bold=True, size=14, indent=False, space_after=10)
add_para("Ce chapitre a presente une evaluation complete du systeme Urbain Sustainability, en couvrant le bilan fonctionnel qui confirme la couverture de l'ensemble des besoins initiaux, l'evaluation de l'experience utilisateur adaptee aux trois profils d'utilisateurs, l'analyse critique des choix technologiques avec leur justification dans le contexte de gestion municipale tunisien, les limites et contraintes identifiees qui constituent des pistes d'amelioration prioritaires, et les perspectives de developpement a court, moyen et long terme. Cette evaluation demontre que le systeme repond aux objectifs fixes en debut de projet tout en ouvrant des perspectives prometteuses pour son evolution future.")

page_break()

# ============================================================
# CONCLUSION GENERALE
# ============================================================
new_main_section("Conclusion Generale")
add_main_title("CONCLUSION GENERALE")

add_para("")
add_para("Ce projet de fin d'etudes nous a permis de concevoir, developper et valider Urbain Sustainability System, une plateforme web intelligente de signalement et de gestion des problemes urbains destinee aux municipalites tunisiennes. Face a la problematique centrale de la gestion municipale dans un contexte d'urbanisation croissante et de ressources limitees, notre solution apporte une reponse concrete et operationnelle en combinant de maniere synergique quatre dimensions technologiques complementaires : l'intelligence artificielle pour la classification automatique et la priorisation des signalements, un systeme de notifications multi-canaux robuste pour la communication citoyenne, la geolocalisation interactive pour la visualisation spatiale des problemes urbains, et des analytics en temps reel pour l'aide a la decision des gestionnaires municipaux.")

add_para("Les principaux resultats de ce projet temoignent de l'atteinte de l'ensemble des objectifs fixes en debut de parcours. Une API RESTful complete a ete developpee et validee par des tests d'integration garantissant la conformite de chaque endpoint. Un pipeline d'intelligence artificielle atteignant 85 % de precision de classification a ete implemente, integre au flux de creation des signalements, et capable de realiser quatre traitements : classification categorielle, evaluation de priorite, detection d'anomalies et prediction de tendances. Un systeme de notifications multi-canaux robuste supportant 4 canaux (Email, SMS, WhatsApp, Push) a ete developpe et valide. Une interface frontend moderne et reactive avec cartographie interactive, tableaux de bord analytics et gestion des utilisateurs a ete concue et developpee.")

add_para("Sur le plan de la demarche et de la methodologie, ce projet nous a permis d'experimenter l'ensemble du cycle de vie d'un projet logiciel : de la specification des besoins et la modelisation UML a l'implementation, en passant par la conception architecturale, les tests de validation, et la gestion de projet Agile Scrum sur 6 sprints. Cette experience nous a conforte dans l'importance d'une approche structuree et methodique pour la reussite de projets.")

add_para("Sur le plan technique, ce projet nous a permis d'approfondir notre maitrise de technologies modernes et pertinentes pour le marche de l'emploi : le developpement web full-stack, l'intelligence artificielle, et la methodologie Agile/Scrum pour la gestion de projet. Ces competences constituent un atout significatif pour notre insertion professionnelle.")

add_para("Les perspectives de developpement et d'amelioration de notre systeme sont nombreuses et prometteuses. A court terme (3 a 6 mois), nous envisageons le deploiement d'une version mobile pour toucher un public plus large et permettre le signalement depuis un smartphone. A moyen terme (6 a 12 mois), l'enrichissement du pipeline IA avec des modeles plus avances et l'analyse automatique des images constitueraient des ameliorations significatives. Enfin, a plus long terme, l'extension du systeme a d'autres domaines de la smart city comme la gestion des transports, la qualite de l'air ou la collecte des dechets pourrait faire evoluer notre plateforme vers un veritable hub urbain integre.")

page_break()

# ============================================================
# BIBLIOGRAPHIE
# ============================================================
new_main_section("Bibliographie")
add_main_title("BIBLIOGRAPHIE")

add_para("")
refs = [
    "[1] NATIONS UNIES. « World Urbanization Prospects: The 2018 Revision ». Department of Economic and Social Affairs, 2019, 126p.",
    "[2] HARRISON, C. et DONNELLY, I. A. « A Theory of Smart Cities ». Proceedings of the 55th Annual Meeting of the ISSS, 2011.",
    "[3] FASTAPI Documentation. « FastAPI: Modern Web Framework for Building APIs with Python ». https://fastapi.tiangolo.com, consulte le 15 mai 2025.",
    "[4] PEDREGOSA, F. et al. « Scikit-learn: Machine Learning in Python ». Journal of Machine Learning Research, vol. 12, 2011, pp. 2825-2830.",
    "[5] SQLALCHEMY. « SQLAlchemy 2.0: The Python SQL Toolkit and Object Relational Mapper ». https://www.sqlalchemy.org, consulte le 15 mai 2025.",
    "[6] ALEX, J. S. « React 19 Design Patterns and Best Practices ». Packt Publishing, 2024, 420p.",
    "[7] SCHWABER, K. et SUTHERLAND, J. « The Scrum Guide: The Definitive Guide to Scrum ». Scrum.org, 2020, 19p.",
    "[8] BASS, L., CLEMENTS, P. et KAZMAN, R. « Software Architecture in Practice ». 4e edition, Addison-Wesley, 2021, 464p.",
    "[9] GAMMA, E., HELM, R., JOHNSON, R. et VLISSIDES, J. « Design Patterns: Elements of Reusable Object-Oriented Software ». Addison-Wesley, 1994, 416p.",
    "[10] MARTIN, R. C. « Clean Architecture: A Craftsman's Guide to Software Structure and Design ». Prentice Hall, 2017, 432p.",
    "[11] ISO/IEC 25010:2011. « Systems and Software Quality Requirements and Evaluation (SQuaRE) ». ISO, 2011.",
    "[12] OWASP Foundation. « OWASP Top 10 - 2021: The Ten Most Critical Web Application Security Risks ». https://owasp.org, consulte le 1 juin 2025.",
    "[13] Loi organique n° 2018-29 relative au Code des collectivites locales. Journal Officiel de la Republique Tunisienne, 2018.",
    "[14] ANTONIOU, J. et al. « Smart City Technologies: A Systematic Literature Review ». IEEE Access, vol. 11, 2023, pp. 45872-45904.",
    "[15] VASWANI, A. et al. « Attention Is All You Need ». Advances in Neural Information Processing Systems, vol. 30, 2017.",
]
for ref in refs:
    add_para(ref, indent=False, space_after=4, size=11)

page_break()

# ============================================================
# ANNEXES
# ============================================================
new_main_section("Annexes")
add_main_title("ANNEXES")

add_para("")
add_section_title("ANNEXE A : Structure du Code Source")
add_para("La structure complete du code source est disponible dans le repertoire GitHub du projet. Le dossier backend/ contient 6 packages : api/v1/ (16 modules de routes), core/ (configuration, securite, exceptions), models/ (8 ORM models avec 18 ENUMs), schemas/ (10 schemas Pydantic), services/ (16 classes de services), repositories/ (8 repositories CRUD). Le dossier frontend/ contient : api/ (client Axios et 100+ endpoints), components/ (layout, ui, hub, workflow), pages/ (30 pages), contexts/ (3 providers), hooks/ (4 custom hooks).")

add_section_title("ANNEXE B : Guide d'Installation")
add_para("Prerequis : Python 3.11+, Node.js 20+, Docker Desktop, Git. Installation : cloner le depot, configurer le fichier backend/.env avec les identifiants de base de donnees et SMTP, executer docker-compose up --build, puis acceder a http://localhost:8000/docs (documentation API) et http://localhost:5173 (interface frontend).")

add_section_title("ANNEXE C : Utilisateurs par defaut")
add_para("Administrateur : admin@urbain.com / Admin123! | Citoyen : citizen@urbain.com / Citizen123! | Les utilisateurs sont crees par le script de seed (python seed_db.py).")

add_section_title("ANNEXE D : Tests de validation")
add_para("Les 35 scenarios de test du systeme de notification couvrent : envoi single user (valide, invalide, sans ID), envoi groupe (citoyens, admins, secteur avec/sans filtre), email personnalise (valide, invalide), validations (titre vide, message court, recipient_type invalide), priorites (LOW, HIGH, CRITICAL), consultation et filtres, marquage lecture, retry (200/422 selon etat), annulation (200/422), nettoyage expirees.")

# ============================================================
# SAUVEGARDE
# ============================================================
import datetime
base = "C:\\Users\\seifa\\Downloads\\Urbain-sustainability-project-ranim\\RAPPORT_PFE_URBAIN"
output = base + ".docx"
saved = False
for attempt in range(5):
    try:
        doc.save(output); saved = True; break
    except PermissionError:
        stamp = datetime.datetime.now().strftime("%H%M%S")
        output = f"{base}_{stamp}.docx"
if not saved:
    doc.save(output)
print(f"Rapport PFE genere avec succes: {output}")
import os
size = os.path.getsize(output)
print(f"Taille: {size} bytes ({size/1024:.1f} KB)")
print("Caracteristiques:")
print("  - Pages preliminaires: chiffres romains (i, ii, iii...)")
print("  - Pages principales: chiffres arabes (1, 2, 3...)")
print("  - Design: carreau noir + ligne pour chaque chapitre")
print("  - Sommaire: champ TOC Word automatique")
print("  - En-tetes: nom du chapitre par section")
print("  - Pieds de page: Page X / Y")
print("  - Numerotation hierarchique: Titre 1/2/3")
print("  - Tableaux: sans lignes verticales, fond bleu entete")
