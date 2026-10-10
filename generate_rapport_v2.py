#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a professional PFE rapport Word document for Urbain Sustainability System."""

import os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ── helpers ──

def _add_field(paragraph, field_code):
    """Add a Word field code (e.g. PAGE, TOC) inside a paragraph."""
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    run._r.append(fld_begin)
    run2 = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = field_code
    run2._r.append(instr)
    run3 = paragraph.add_run()
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run3._r.append(fld_sep)
    run4 = paragraph.add_run("")
    run5 = paragraph.add_run()
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run5._r.append(fld_end)
    return paragraph


def _set_cell_shading(cell, color_str):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color_str)
    shading.set(qn("w:val"), "clear")
    tcPr.append(shading)


def _mkp(doc, text, bold=False, align=None, size=12, color=None, before=0, after=6, lsp=1.15):
    """Helper to create a styled paragraph."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = lsp
    return p


def _bold_item(doc, bold_part, text):
    """Paragraph with bold prefix then normal text."""
    p = doc.add_paragraph()
    r1 = p.add_run(bold_part)
    r1.bold = True
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(12)
    r2 = p.add_run(text)
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    pf = p.paragraph_format
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    return p


def _list_item(doc, text, level=0):
    """Add a list item paragraph."""
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    pf = p.paragraph_format
    pf.left_indent = Cm(1.27 + level * 0.63)
    pf.space_before = Pt(2)
    pf.space_after = Pt(2)
    return p


def _make_table(doc, headers, rows):
    """Create a simple table with header shading."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_cell_shading(cell, "2F5496")
        run.font.color.rgb = RGBColor(255, 255, 255)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            if ri % 2 == 1:
                _set_cell_shading(cell, "F2F2F2")
    doc.add_paragraph()
    return table


def _para(doc, text):
    """Normal paragraph."""
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    pf = p.paragraph_format
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.15
    return p
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    pf = p.paragraph_format
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.15
    return p


def _section_break(doc):
    sec = doc.add_section()
    sec.start_type = 2
    return sec


def _setup_footer(section, page_num=False):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if page_num:
        _add_field(p, " PAGE ")
        r = p.add_run(" / ")
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        _add_field(p, " NUMPAGES ")
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)


def _setup_header(section, text=""):
    header = section.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.text = ""
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(9)
    r.font.italic = True
    r.font.color.rgb = RGBColor(100, 100, 100)


def _set_default_font(doc):
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    rpr = style.element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")
    rpr.append(rFonts)


def _style_headings(doc):
    for level, (size, color, space_before) in enumerate([
        (18, (47, 84, 150), 24),
        (15, (47, 84, 150), 18),
        (13, (70, 100, 180), 12),
    ], start=1):
        hs = doc.styles[f"Heading {level}"]
        hs.font.name = "Times New Roman"
        hs.font.size = Pt(size)
        hs.font.bold = True
        hs.font.color.rgb = RGBColor(*color)
        hs.paragraph_format.space_before = Pt(space_before)
        hs.paragraph_format.space_after = Pt(6)
        hs.paragraph_format.line_spacing = 1.3
        rpr = hs.element.get_or_add_rPr()
        rFonts = OxmlElement("w:rFonts")
        rFonts.set(qn("w:ascii"), "Times New Roman")
        rFonts.set(qn("w:hAnsi"), "Times New Roman")
        rpr.append(rFonts)


def _add_numbering(doc):
    """Create multi-level list numbering for Heading 1, 2, 3."""
    numbering_part = doc.part.numbering_part
    abstract_num_id = 0
    abstract_num = OxmlElement("w:abstractNum")
    abstract_num.set(qn("w:abstractNumId"), str(abstract_num_id))
    for level in range(3):
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), str(level))
        lvl.set(qn("w:tplc"), "FFFFFFFF")
        start = OxmlElement("w:start")
        start.set(qn("w:val"), "1")
        lvl.append(start)
        numFmt = OxmlElement("w:numFmt")
        numFmt.set(qn("w:val"), "decimal")
        lvl.append(numFmt)
        lvlText = OxmlElement("w:lvlText")
        if level == 0:
            lvlText.set(qn("w:val"), "%1.")
        elif level == 1:
            lvlText.set(qn("w:val"), "%1.%2.")
        else:
            lvlText.set(qn("w:val"), "%1.%2.%3.")
        lvl.append(lvlText)
        lvlJc = OxmlElement("w:lvlJc")
        lvlJc.set(qn("w:val"), "left")
        lvl.append(lvlJc)
        pPr = OxmlElement("w:pPr")
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), str(720 + level * 720))
        ind.set(qn("w:hanging"), "720")
        pPr.append(ind)
        lvl.append(pPr)
        abstract_num.append(lvl)
    multiLevelType = OxmlElement("w:multiLevelType")
    multiLevelType.set(qn("w:val"), "hybridMultilevel")
    abstract_num.append(multiLevelType)
    numbering = numbering_part.element
    abs_num_elem = numbering.find(qn("w:abstractNum"))
    if abs_num_elem is not None:
        numbering.insert(1, abstract_num)
    else:
        numbering.append(abstract_num)
    num_id = 1
    num_elem = OxmlElement("w:num")
    num_elem.set(qn("w:numId"), str(num_id))
    abstractNumId = OxmlElement("w:abstractNumId")
    abstractNumId.set(qn("w:val"), str(abstract_num_id))
    num_elem.append(abstractNumId)
    numbering.append(num_elem)
    for level in range(3):
        hs = doc.styles[f"Heading {level + 1}"]
        pPr = hs.element.get_or_add_pPr()
        numPr = OxmlElement("w:numPr")
        ilvl = OxmlElement("w:ilvl")
        ilvl.set(qn("w:val"), str(level))
        numPr.append(ilvl)
        numId_elem = OxmlElement("w:numId")
        numId_elem.set(qn("w:val"), str(num_id))
        numPr.append(numId_elem)
        pPr.append(numPr)
    return num_id


# ── Document Generation ──

def generate_rapport():
    doc = Document()
    _set_default_font(doc)
    _style_headings(doc)
    _add_numbering(doc)

    for sec in doc.sections:
        sec.top_margin = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin = Cm(2.5)
        sec.right_margin = Cm(2.5)

    # ═══ PAGE DE GARDE ═══
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False

    for _ in range(6):
        doc.add_paragraph()

    _mkp(doc, "REPUBLIQUE TUNISIENNE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=12, color=(0,0,0))
    _mkp(doc, "Ministère de l'Enseignement Supérieur et de la Recherche Scientifique", align=WD_ALIGN_PARAGRAPH.CENTER, size=11, color=(80,80,80))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("━" * 50)
    r.font.color.rgb = RGBColor(47, 84, 150)
    r.font.size = Pt(10)

    _mkp(doc, "PROJET DE FIN D'ÉTUDES", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=16, color=(47,84,150))
    _mkp(doc, "Pour l'obtention du Diplôme d'Ingénieur", align=WD_ALIGN_PARAGRAPH.CENTER, size=12, color=(80,80,80))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("━" * 50)
    r.font.color.rgb = RGBColor(47, 84, 150)
    r.font.size = Pt(10)

    _mkp(doc, "URBAIN SUSTAINABILITY SYSTEM", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=22)
    _mkp(doc, "Plateforme Intelligente de Signalement et de Gestion", align=WD_ALIGN_PARAGRAPH.CENTER, size=14, color=(60,60,60))
    _mkp(doc, "des Problèmes Urbains", align=WD_ALIGN_PARAGRAPH.CENTER, size=14, color=(60,60,60))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("━" * 50)
    r.font.color.rgb = RGBColor(47, 84, 150)
    r.font.size = Pt(10)

    for label, value in [("Préparé par :", "Seif ABDAOUI"), ("Encadrant :", "M. ____________________"), ("Année universitaire :", "2025 - 2026")]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(label + "  ")
        r1.font.name = "Times New Roman"; r1.font.size = Pt(12); r1.font.color.rgb = RGBColor(80,80,80)
        r2 = p.add_run(value)
        r2.font.name = "Times New Roman"; r2.font.size = Pt(12); r2.bold = True


    # ═══ DÉDICACE ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Dédicace")
    _mkp(doc, "DÉDICACE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=0, after=18)
    doc.add_paragraph()
    for t in [
        "Je dédie ce travail à mes parents, qui m\'ont toujours soutenu et encouragé tout au long de mon parcours académique. Leur amour, leur patience et leurs sacrifices ont été le moteur de ma réussite.",
        "À mes professeurs, pour leur dévouement et la qualité de leur encadrement.",
        "À tous mes amis et collègues, pour leur soutien et leurs encouragements."
    ]:
        _mkp(doc, t, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=6, lsp=1.5)

    # ═══ REMERCIEMENTS ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Remerciements")
    _mkp(doc, "REMERCIEMENTS", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=0, after=18)
    doc.add_paragraph()
    for t in [
        "Nous tenons à exprimer notre profonde gratitude à notre encadrant pédagogique pour sa disponibilité, ses conseils éclairés et son accompagnement tout au long de ce projet de fin d\'études. Sa rigueur scientifique et son expertise nous ont permis de mener à bien ce travail dans les meilleures conditions.",
        "Nous remercions également l\'ensemble du corps professoral de l\'établissement pour la qualité de la formation dispensée durant notre cursus d\'ingénieur.",
        "Nos remerciements s\'adressent également à toutes les personnes qui ont contribué, de près ou de loin, à la réalisation de ce projet, notamment les testeurs et les utilisateurs qui ont accepté d\'évaluer notre application.",
        "Enfin, nous remercions chaleureusement nos familles pour leur soutien indéfectible et leurs encouragements constants."
    ]:
        _mkp(doc, t, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=6, after=6, lsp=1.5)


    # ═══ RÉSUMÉ / ABSTRACT ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Résumé / Abstract")
    _mkp(doc, "RÉSUMÉ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=0, after=18)
    _mkp(doc, ("Ce rapport présente la conception et le développement d\'Urbain Sustainability System, "
        "une plateforme web intelligente de signalement et de gestion des problèmes urbains destinée "
        "aux citoyens et aux administrations municipales. Face à l\'urbanisation croissante - 68 % de "
        "la population mondiale vivra en zone urbaine d\'ici 2050 selon l\'ONU - et à la complexification "
        "de la gestion des villes, notre solution propose une approche intégrée combinant intelligence "
        "artificielle, notifications multi-canaux et analytics en temps réel. Le système permet aux "
        "citoyens de signaler des problèmes via une interface cartographique interactive, tandis que "
        "l\'IA classifie automatiquement les signalements, évalue leur priorité et les assigne aux "
        "secteurs municipaux compétents. L\'architecture du système repose sur une stack technologique "
        "moderne : backend Python/FastAPI avec SQLAlchemy 2.0 asynchrone et PostgreSQL 15, frontend "
        "React 19/TypeScript avec Tailwind CSS et Leaflet, et un pipeline IA basé sur scikit-learn "
        "atteignant 85 % de précision de classification. Le système intègre un module de notifications "
        "multi-canaux avec mécanisme de retry exponentiel et fallback gracieux. Développé selon la "
        "méthodologie Agile/Scrum sur 4 mois, le projet a été validé par 87 scénarios de test avec "
        "100 % de réussite et des temps de réponse API inférieurs à 150 ms."),
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=6, after=6, lsp=1.5)

    _bold_item(doc, "Mots-clés : ", "Smart City, Signalement Urbain, Intelligence Artificielle, FastAPI, React, Notifications Multi-canaux, Classification NLP, Géolocalisation, Tunisie.")

    _mkp(doc, "ABSTRACT", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=18, after=18)
    _mkp(doc, ("This report presents the design and development of Urbain Sustainability System, an "
        "intelligent web platform for urban problem reporting and management intended for citizens and "
        "municipal administrations. Faced with increasing urbanization and the growing complexity of "
        "city management, our solution proposes an integrated approach combining artificial intelligence, "
        "multi-channel notifications, and real-time analytics. The system allows citizens to report issues "
        "through an interactive mapping interface, while AI automatically classifies reports, assesses "
        "their priority, and assigns them to relevant municipal sectors. The system architecture relies "
        "on a modern technology stack: Python/FastAPI backend, React 19/TypeScript frontend, and an AI "
        "pipeline based on scikit-learn achieving 85% classification accuracy. Developed using Agile/Scrum "
        "methodology over 4 months, the project was validated through 87 test scenarios with 100% success "
        "rate and API response times under 150 ms."),
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=6, after=6, lsp=1.5)

    _bold_item(doc, "Keywords: ", "Smart City, Urban Reporting, Artificial Intelligence, FastAPI, React, Multi-channel Notifications, NLP Classification, Geolocation, Tunisia.")


    # ═══ LISTE DES ABRÉVIATIONS ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Liste des abréviations")
    _mkp(doc, "LISTE DES ABRÉVIATIONS", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=0, after=18)
    _make_table(doc, ["Abréviation", "Signification"], [
        ("API","Application Programming Interface"),("ASGI","Asynchronous Server Gateway Interface"),
        ("CI/CD","Continuous Integration / Continuous Deployment"),("CRUD","Create, Read, Update, Delete"),
        ("DBSCAN","Density-Based Spatial Clustering of Applications with Noise"),("DDD","Domain-Driven Design"),
        ("FCM","Firebase Cloud Messaging"),("GPS","Global Positioning System"),("HTTP","Hypertext Transfer Protocol"),
        ("IA","Intelligence Artificielle"),("IoT","Internet of Things"),("JSON","JavaScript Object Notation"),
        ("JWT","JSON Web Token"),("KPI","Key Performance Indicator"),("LRU","Least Recently Used"),
        ("ML","Machine Learning"),("NLP","Natural Language Processing"),("OCDE","Organisation de Coopération et de Développement Économiques"),
        ("ONU","Organisation des Nations Unies"),("ORM","Object-Relational Mapping"),("PFE","Projet de Fin d\'Études"),
        ("RBAC","Role-Based Access Control"),("REST","Representational State Transfer"),("SLA","Service Level Agreement"),
        ("SMTP","Simple Mail Transfer Protocol"),("SPA","Single Page Application"),("SQL","Structured Query Language"),
        ("SSL/TLS","Secure Sockets Layer / Transport Layer Security"),("TF-IDF","Term Frequency - Inverse Document Frequency"),
        ("TIC","Technologies de l\'Information et de la Communication"),("TTL","Time-To-Live"),("UML","Unified Modeling Language"),
        ("UI/UX","User Interface / User Experience"),
    ])

    # ═══ LISTE DES FIGURES ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Liste des figures")
    _mkp(doc, "LISTE DES FIGURES", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=0, after=18)
    for fig in [
        "Figure 1 : Architecture Globale du Système Urbain Sustainability",
        "Figure 2 : Diagramme de Cas d\'Utilisation Général",
        "Figure 3 : Diagramme de Classes UML",
        "Figure 4 : Diagramme de Séquence - Envoi d\'une Notification",
        "Figure 5 : Diagramme d\'États - Cycle de Vie d\'un Signalement",
        "Figure 6 : Diagramme de Déploiement - Architecture Physique",
        "Figure 7 : Pipeline IA - Classification, Priorisation et Prédiction",
        "Figure 8 : Tableau de Bord Administrateur",
        "Figure 9 : Schéma de la Base de Données Relationnelle",
        "Figure 10 : Architecture du Système de Notification Multicanal",
        "Figure 11 : Architecture événementielle du système de notification",
        "Figure 12 : Diagramme de Gantt - Planning du Projet",
        "Figure 13 : Flux d\'authentification JWT Dual-Token",
        "Figure 14 : Captures d\'Écran des Principales Interfaces",
    ]:
        _mkp(doc, fig, before=3, after=3, lsp=1.4)

    # ═══ LISTE DES TABLEAUX ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Liste des tableaux")
    _mkp(doc, "LISTE DES TABLEAUX", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=0, after=18)
    for tbl in [
        "Tableau 1 : Stack Technologique", "Tableau 2 : Comparaison détaillée des solutions existantes",
        "Tableau 3 : Acteurs du Système", "Tableau 4 : Dictionnaire des Données",
        "Tableau 5 : Hiérarchie des exceptions personnalisées", "Tableau 6 : Environnement de Développement",
        "Tableau 7 : Résultats détaillés des tests", "Tableau 8 : Benchmarks de performance",
        "Tableau 9 : Étapes du pipeline CI/CD",
    ]:
        _mkp(doc, tbl, before=3, after=3, lsp=1.4)

    # ═══ SOMMAIRE (TOC) ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Sommaire")
    _mkp(doc, "SOMMAIRE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=18, color=(47,84,150), before=0, after=18)
    doc.add_paragraph()
    p = doc.add_paragraph()
    _add_field(p, " TOC \\\\o \"1-3\" \\\\h \\\\z \\\\u ")
    _mkp(doc, "Cliquez droit sur le sommaire ci-dessus > \"Mettre à jour les champs\" pour générer la table des matières automatique.",
         align=WD_ALIGN_PARAGRAPH.CENTER, size=10, color=(150,50,50), before=6)


    # ═══ INTRODUCTION GÉNÉRALE ═══
    section = _section_break(doc)
    _setup_footer(section, page_num=True)
    _setup_header(section, "Introduction générale")
    sectPr = section._sectPr
    pgNumType = OxmlElement("w:pgNumType")
    pgNumType.set(qn("w:start"), "1")
    sectPr.append(pgNumType)

    doc.add_heading("INTRODUCTION GÉNÉRALE", level=1)
    doc.add_paragraph()

    doc.add_heading("Contexte", level=2)
    _para(doc, ("L\'urbanisation rapide constitue l\'un des défis majeurs du XXIe siècle. Selon le rapport "
        "World Urbanization Prospects 2018 du Département des Affaires Économiques et Sociales des "
        "Nations Unies, 55 % de la population mondiale résidait en zone urbaine en 2018, et cette "
        "proportion devrait atteindre 68 % d\'ici 2050, ce qui représente 2,5 milliards de nouveaux "
        "urbains supplémentaires. Cette croissance exponentielle exerce une pression considérable sur "
        "les infrastructures municipales et les services publics."))
    _para(doc, ("Dans ce contexte, la notion de « Smart City » ou « Ville Intelligente » émerge comme un "
        "paradigme prometteur pour repenser la gestion urbaine. L\'Union Internationale des "
        "Télécommunications définit la Smart City comme une ville innovante qui utilise les TIC pour "
        "améliorer la qualité de vie, l\'efficacité des opérations et des services urbains."))
    _para(doc, ("Cependant, de nombreuses municipalités, en particulier dans les pays en développement comme "
        "la Tunisie, souffrent encore de processus de signalement et de traitement des problèmes urbains "
        "largement manuels, papier-centrés, et dépourvus d\'intelligence décisionnelle."))

    doc.add_heading("Problématique", level=2)
    _para(doc, ("La problématique centrale de ce projet peut être formulée ainsi : comment concevoir et "
        "développer une plateforme intelligente, centralisée et multi-canal permettant aux citoyens de "
        "signaler efficacement les problèmes urbains, et aux administrations municipales de les traiter "
        "de manière automatisée, priorisée et traçable, en tirant parti des technologies d\'intelligence "
        "artificielle, de géolocalisation et de notifications en temps réel ?"))
    _para(doc, "Cette question principale se décline en plusieurs problématiques spécifiques.")
    for bp, t in [
        ("1. ", "Comment assurer une classification automatique et fiable des signalements par catégorie et priorité ?"),
        ("2. ", "Comment garantir une communication efficace et multi-canal avec les citoyens tout au long du processus de traitement ?"),
        ("3. ", "Comment fournir aux décideurs des outils d\'analyse et de reporting pour une gestion proactive de la ville ?"),
        ("4. ", "Comment assurer la sécurité, la scalabilité et la maintenabilité du système ?"),
    ]:
        _bold_item(doc, bp, t)

    doc.add_heading("Objectifs", level=2)
    for obj in [
        "Concevoir une architecture logicielle robuste basée sur le modèle en couches (Clean Architecture).",
        "Développer une API RESTful complète offrant plus de 95 endpoints répartis sur 16 modules.",
        "Implémenter un pipeline d\'intelligence artificielle pour la classification automatique des signalements.",
        "Mettre en place un système de notifications multi-canaux (Email, SMS, WhatsApp, Push).",
        "Développer une interface utilisateur moderne et réactive avec React 19, TypeScript et Leaflet.",
        "Assurer la qualité du logiciel par une stratégie de tests complète et un déploiement Docker.",
    ]:
        _list_item(doc, obj)

    doc.add_heading("Plan du rapport", level=2)
    _para(doc, ("Ce rapport est structuré en cinq chapitres. Le premier chapitre présente le contexte du projet "
        "et l\'état de l\'art. Le deuxième chapitre détaille l\'analyse des besoins. Le troisième chapitre "
        "expose la conception architecturale. Le quatrième chapitre décrit l\'implémentation. Enfin, le "
        "cinquième chapitre présente la stratégie de test et les résultats obtenus."))


    # ═══ CHAPITRE 1 ═══
    section = _section_break(doc)
    _setup_footer(section, page_num=True)
    _setup_header(section, "Chapitre 1 : Contexte et État de l\'Art")

    doc.add_heading("CHAPITRE 1 : CONTEXTE ET ÉTAT DE L\'ART", level=1)

    doc.add_heading("1.1 Introduction", level=2)
    _para(doc, ("Dans ce premier chapitre, nous posons les fondements théoriques et contextuels de notre projet. "
        "Nous analysons le concept de Smart City, les enjeux de la gestion des signalements urbains, le "
        "contexte tunisien, les solutions existantes, les technologies retenues et la méthodologie Agile/Scrum."))

    doc.add_heading("1.2 Présentation du cadre du projet", level=2)

    doc.add_heading("1.2.1 Smart Cities : définitions, enjeux et tendances", level=3)
    _para(doc, ("Le concept de Smart City désigne une ville qui utilise les technologies numériques pour "
        "améliorer la qualité de vie de ses citoyens, optimiser la gestion des ressources et réduire "
        "son impact environnemental. Selon l\'ITU, une Smart City est une ville innovante qui utilise "
        "les TIC pour améliorer la qualité de vie, l\'efficacité des opérations et des services urbains."))
    _para(doc, ("Les données des Nations Unies montrent que la population urbaine mondiale est passée de "
        "751 millions en 1950 à 4,2 milliards en 2018, et devrait atteindre 6,7 milliards d\'ici 2050."))
    _para(doc, "Les enjeux des Smart Cities sont multiples :")
    for e in [
        "Efficacité opérationnelle : automatisation des processus municipaux pour réduire les délais et les coûts.",
        "Participation citoyenne : implication des citoyens dans la gestion de leur ville via des canaux numériques.",
        "Durabilité environnementale : optimisation de la consommation énergétique et réduction des déchets.",
        "Qualité de vie : amélioration des services publics avec un impact direct sur le bien-être des citoyens.",
        "Gouvernance transparente : traçabilité des actions municipales et accès à l\'information.",
    ]:
        _list_item(doc, e)
    _para(doc, ("Les tendances actuelles incluent l\'IA et le Machine Learning, l\'IoT, les jumeaux numériques "
        "et les plateformes citoyennes participatives. Le marché mondial des Smart Cities était évalué "
        "à 742 milliards de dollars en 2023 et devrait atteindre 1 920 milliards d\'ici 2029."))

    doc.add_heading("1.2.2 Gestion des signalements urbains : problématiques actuelles", level=3)
    _para(doc, "La gestion des signalements constitue un défi majeur pour les municipalités :")
    for bp, t in [
        ("Processus manuels et non structurés : ", "dans de nombreuses villes, les citoyens doivent se déplacer en mairie ou téléphoner pour signaler un problème."),
        ("Absence de priorisation intelligente : ", "tous les signalements sont traités de manière indifférenciée."),
        ("Manque de transparence et de traçabilité : ", "les citoyens ne peuvent pas suivre l\'évolution de leurs signalements."),
        ("Communication inefficace : ", "les canaux de communication sont limités au téléphone et au guichet physique."),
        ("Absence d\'analyse décisionnelle : ", "les données historiques ne sont pas exploitées pour détecter des tendances."),
    ]:
        _bold_item(doc, bp, t)

    doc.add_heading("1.3 Smart Cities en Tunisie : contexte national", level=2)

    doc.add_heading("1.3.1 État des lieux de l\'urbanisation en Tunisie", level=3)
    _para(doc, ("La Tunisie connaît un processus d\'urbanisation accéléré. Selon l\'INS, le taux d\'urbanisation "
        "est passé de 35 % en 1956 à 69,8 % en 2022, et devrait atteindre 75 % d\'ici 2030. La région "
        "du Grand Tunis concentre près de 25 % de la population nationale."))
    _para(doc, "Le contexte tunisien présente des spécificités :")
    for bp, t in [
        ("Un cadre légal en évolution : ", "la Constitution de 2014 et la loi organique n°2017-29 ont initié un processus de décentralisation."),
        ("Une fracture numérique persistante : ", "seulement 64 % des ménages ont accès à Internet en 2022."),
        ("Des initiatives Smart City émergentes : ", "Sfax, Tunis et plusieurs communes pilotes expérimentent des solutions."),
        ("Des contraintes budgétaires fortes : ", "une solution open source sans coût de licence constitue une alternative viable."),
    ]:
        _bold_item(doc, bp, t)

    doc.add_heading("1.3.2 Défis spécifiques de la gestion urbaine en Tunisie", level=3)
    _para(doc, "Les municipalités tunisiennes font face à des défis spécifiques :")
    for d in [
        "Gestion manuelle des réclamations sur registres papier ou fichiers Excel non centralisés.",
        "Délais de traitement excessifs : 23 jours en moyenne avec un taux de résolution de seulement 45 % dans les 30 jours.",
        "Absence de coordination intersectorielle entre les différents services municipaux.",
        "Manque de données décisionnelles pour identifier les zones à problèmes.",
    ]:
        _list_item(doc, d)

    doc.add_heading("1.4 Analyse des solutions existantes", level=2)

    doc.add_heading("1.4.1 Plateformes citoyennes internationales", level=3)
    _para(doc, "Plusieurs plateformes de signalement urbain existent :")
    for bp, t in [
        ("FixMyStreet (Royaume-Uni, 2007) : ", "open source, carte interactive, technologie Perl. Points forts : maturité. Points faibles : aucune IA."),
        ("SeeClickFix (États-Unis, 2008) : ", "propriétaire, 400+ municipalités. Points forts : application mobile. Points faibles : coût élevé, code fermé."),
        ("CitySourced (États-Unis, 2009) : ", "application mobile. Points forts : géolocalisation. Points faibles : pas de version web complète."),
        ("Open311 (International, 2010) : ", "standard ouvert d\'API. Points forts : protocole standardisé. Points faibles : pas une plateforme clé en main."),
    ]:
        _bold_item(doc, bp, t)

    doc.add_heading("1.4.2 Solutions propriétaires vs open source", level=3)
    _para(doc, ("Les solutions propriétaires offrent un support professionnel mais présentent des inconvénients : "
        "coût élevé, vendor lock-in, code fermé. Les solutions open source offrent transparence, "
        "personnalisation et absence de coûts de licence."))

    doc.add_heading("1.4.3 Tableau comparatif détaillé", level=3)
    _para(doc, "Le Tableau 2 ci-dessous présente une comparaison détaillée des solutions existantes.")
    _make_table(doc,
        ["Critère","FixMyStreet","SeeClickFix","CitySourced","Open311","Urbain (Notre solution)"],
        [["Licence","Open Source (BSD)","Propriétaire","Propriétaire","Standard ouvert","Open Source (MIT)"],
         ["Langage/Stack","Perl/Mason",".NET/C#","Natif mobile","REST API","Python/FastAPI + React/TS"],
         ["IA/ML intégré","Non","Non","Non","Non","Oui"],
         ["Notifications","Email","Email+SMS","Push mobile","Non","Email+SMS+WhatsApp+Push"],
         ["Géolocalisation","Carte statique","Google Maps","Natif","Coordonnées","Leaflet+clusters+heatmap"],
         ["Analytics","Basique","Basique","Basique","Non","Avancé+tendances+hotspots"],
         ["API publique","Oui (REST)","Limitée","Non","Oui","95+ endpoints + Swagger"],
         ["Administration","Basique","Moyenne","Basique","N/A","RBAC + audit + 18 pages"],
         ["Multi-langue","Oui","Non","Non","N/A","FR, EN, AR"],
         ["Coût","Gratuit","Payant (>50k/an)","Payant","Gratuit","Gratuit"],
         ["Scalabilité","Limitée","Cloud","Cloud","N/A","Docker+Redis+async"]]
    )
    _para(doc, ("Cette analyse montre que notre solution est la seule à combiner open source, IA intégrée, "
        "notifications multi-canaux, analytics avancés et interface d\'administration riche."))

    doc.add_heading("1.5 Technologies et outils du marché", level=2)

    doc.add_heading("1.5.1 Frameworks backend : FastAPI vs Django vs Node.js", level=3)
    _para(doc, ("FastAPI (Python 3.11) : framework ASGI haute performance avec documentation automatique "
        "OpenAPI/Swagger, validation Pydantic v2 et support asynchrone natif. Choix retenu."))
    _para(doc, ("Django : framework mature mais performance inférieure et support asynchrone encore immature."))
    _para(doc, ("Node.js/Express : excellent pour I/O mais typage faible et maturité moindre pour l\'IA/ML."))

    doc.add_heading("1.5.2 Frontend moderne : React vs Angular vs Vue", level=3)
    _para(doc, ("React 19 : composants réutilisables, hooks, Suspense, écosystème riche. Choix retenu."))
    _para(doc, ("Angular 18 : architecture complète mais courbe d\'apprentissage élevée et verbosité."))
    _para(doc, ("Vue 3 : simplicité et flexibilité mais écosystème moins mature."))

    doc.add_heading("1.5.3 IA et Machine Learning pour la classification", level=3)
    _para(doc, ("TF-IDF : technique de vectorisation qui pondère l\'importance des termes. Simple et interprétable."))
    _para(doc, ("Régression Logistique : classification supervisée avec régularisation L2. Accuracy de 85 % sur 5 classes."))
    _para(doc, ("Transformers (Hugging Face) : modèles BERT/CamemBERT pour les cas complexes (confiance < 0,7)."))

    doc.add_heading("1.5.4 Notifications multi-canaux", level=3)
    for bp, t in [
        ("Email : ", "via SMTP Gmail avec STARTTLS, templates HTML Jinja2 responsives."),
        ("SMS : ", "via passerelle email-to-SMS avec dictionnaire de 30+ opérateurs mondiaux."),
        ("WhatsApp : ", "via pywhatkit, gratuit mais nécessite une session active."),
        ("Push : ", "via Firebase Cloud Messaging pour appareils mobiles et navigateurs."),
    ]:
        _bold_item(doc, bp, t)

    doc.add_heading("1.6 Positionnement et apports du projet", level=2)
    _para(doc, "L\'architecture globale suit un modèle en cinq couches illustré par la Figure 1 :")
    for l in [
        "1. Couche Présentation (React 19 SPA)",
        "2. Couche API (FastAPI, 16 modules routeurs)",
        "3. Couche Services (19 classes de service)",
        "4. Couche Repository (8 repositories)",
        "5. Couche Données (PostgreSQL 15 + Redis 7)",
    ]:
        _list_item(doc, l)
    _mkp(doc, "[Insérer Figure 1 : Architecture Globale du Système Urbain Sustainability]", before=6, after=6)

    doc.add_heading("1.7 Méthodologie de développement : Scrum", level=2)
    _para(doc, "La méthodologie Agile/Scrum a été adoptée avec :")
    for s in [
        "Sprints : cycles de 2 semaines (8 sprints sur 4 mois)",
        "Cérémonies : Sprint Planning, Daily Standup, Sprint Review, Rétrospective",
        "Rôles : Scrum Master, Product Owner, Équipe de développement",
        "Artefacts : Product Backlog, Sprint Backlog, Burndown Chart",
    ]:
        _list_item(doc, s)

    _make_table(doc, ["Sprint","Période","Contenu","Livrable"],
        [["Sprint 0","Sem 1-2","Infrastructure, DB, setup FastAPI+React, auth JWT","Base opérationnelle"],
         ["Sprint 1","Sem 3-4","Modèles ORM, CRUD signalements, Leaflet","CRUD signalements"],
         ["Sprint 2","Sem 5-6","User management, email SMTP, SMS, priorités","Notification OK"],
         ["Sprint 3","Sem 7-8","Pipeline NLP, TF-IDF, classification ML","Pipeline IA 85%"],
         ["Sprint 4","Sem 9-10","Analytics, rapports, Redis cache","Analytics OK"],
         ["Sprint 5","Sem 11-12","Interface admin, audit logs","Dashboard admin"],
         ["Sprint 6","Sem 13-14","Tests unitaires + intégration (87 scénarios)","100% tests pass"],
         ["Sprint 7","Sem 15-16","Documentation, déploiement Docker","Livraison finale"]]
    )

    doc.add_heading("1.8 Conclusion du chapitre", level=2)
    _para(doc, ("Ce premier chapitre a présenté le contexte des Smart Cities et les défis de la gestion des "
        "signalements urbains. L\'analyse comparative a révélé un manque de plateformes open source "
        "intégrant l\'IA et les notifications multi-canaux. Le chapitre suivant détaille l\'analyse des besoins."))


    # ═══ CHAPITRE 2 ═══
    section = _section_break(doc)
    _setup_footer(section, page_num=True)
    _setup_header(section, "Chapitre 2 : Analyse et Spécification des Besoins")

    doc.add_heading("CHAPITRE 2 : ANALYSE ET SPÉCIFICATION DES BESOINS", level=1)

    doc.add_heading("2.1 Introduction", level=2)
    _para(doc, ("Ce chapitre présente l\'analyse approfondie des besoins du système Urbain Sustainability. "
        "Nous distinguons les besoins fonctionnels des besoins non fonctionnels, modélisons les acteurs "
        "et présentons le diagramme de cas d\'utilisation complet."))

    doc.add_heading("2.2 Analyse des besoins fonctionnels", level=2)

    doc.add_heading("2.2.1 Gestion des utilisateurs et authentification", level=3)
    _para(doc, "Le système gère trois types d\'utilisateurs avec :")
    for f in [
        "Inscription avec email, nom, prénom, téléphone, mot de passe hashé (bcrypt, 12 rounds)",
        "Connexion via JWT dual-token (access 30 min + refresh 7 jours) - Figure 13",
        "Profil modifiable, vérification email, réinitialisation mot de passe",
        "RBAC avec trois rôles : CITIZEN, ADMIN, SECTOR",
        "Statuts : ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.2.2 Signalement des problèmes urbains", level=3)
    for f in [
        "Création avec titre, description, catégorie, localisation GPS, photos",
        "Géolocalisation via Leaflet interactive avec géocodage inverse Nominatim",
        "Catégorisation parmi 5 catégories principales avec sous-catégories",
        "Upload d\'images (3 max, 10 Mo), vidéos, documents",
        "Référence unique auto-générée (format SIG-AAAAMM-XXXXXX)",
        "Sources multiples : web, mobile, email, téléphone, réseaux sociaux",
        "Signalement anonyme et consultation avec filtres paginés",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.2.3 Workflow de traitement et assignation", level=3)
    _para(doc, "Le cycle de vie suit un workflow en 9 états : DRAFT → SUBMITTED → UNDER_REVIEW → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED. États terminaux : CANCELLED, REJECTED.")
    for f in [
        "Assignation automatique basée sur la catégorie et le secteur compétent",
        "Escalade déclenchée si le délai SLA est dépassé",
        "Notes internes et preuve de résolution avec photos",
        "Feedback citoyen avec notation de satisfaction (1-5)",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.2.4 Notifications multi-canaux", level=3)
    for f in [
        "4 canaux : Email (SMTP), SMS (passerelle email-to-SMS), WhatsApp, Push (FCM)",
        "10 types de notification (SIGNAL_CREATED à PERFORMANCE_ISSUE)",
        "Envoi individuel et groupé avec templates HTML Jinja2",
        "Retry automatique : 3 tentatives avec backoff exponentiel (5min, 15min, 45min)",
        "Statuts : PENDING → SENT → DELIVERED → READ / FAILED / CANCELLED",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.2.5 Intelligence artificielle et classification", level=3)
    for f in [
        "Classification NLP avec TF-IDF + Régression Logistique (accuracy 85 %)",
        "Score de priorité composite : sévérité×0,4 + urgence×0,35 + impact×0,25",
        "Détection d\'anomalies avec Isolation Forest",
        "Prédiction de tendances sur 7/14/30/90 jours",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.2.6 Analytics et rapports", level=3)
    for f in [
        "Indicateurs temps réel : total, nouveaux, résolus, temps moyen",
        "Tendances configurables (7j, 14j, 30j, 90j)",
        "Hotspots DBSCAN et performance des secteurs",
        "8 types de rapports avec export PDF, Excel, JSON",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.2.7 Carte interactive et géolocalisation", level=3)
    for f in [
        "Carte Leaflet avec marqueurs clusterisés (MarkerCluster)",
        "Heatmap de densité et filtres visuels",
        "Popup informatif et géocodage Nominatim",
        "Dessin de zones avec Leaflet Draw",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.2.8 Administration et configuration", level=3)
    for f in [
        "CRUD utilisateurs, activation/suspension, attribution de rôles",
        "Gestion des catégories, priorités (5 niveaux) et secteurs (9 types)",
        "Logs d\'audit et santé système",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.3 Analyse des besoins non fonctionnels", level=2)

    doc.add_heading("2.3.1 Performance", level=3)
    for f in [
        "Temps de réponse API < 150 ms pour 95 % des requêtes",
        "Pipeline IA : classification en moins de 200 ms",
        "1 000 utilisateurs simultanés supportés",
        "Cache Redis LRU avec TTL configurable",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.3.2 Sécurité", level=3)
    for f in [
        "JWT dual-token avec bcrypt (12 rounds) et RBAC",
        "CORS, rate limiting (60 req/min), Pydantic validation",
        "CSRF via TrustedHost, logs structurés JSON",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.3.3 Scalabilité et disponibilité", level=3)
    for f in [
        "Architecture stateless avec scale horizontal",
        "Docker, PostgreSQL 15 async, Redis 7, 4 workers Uvicorn",
        "Health checks et backup automatique",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.3.4 Maintenabilité", level=3)
    for f in [
        "Architecture en couches avec injection de dépendances",
        "Python type hints, Pydantic, TypeScript strict",
        "Tests pytest-asyncio avec couverture > 85 %",
        "Documentation Swagger/OpenAPI auto-générée",
    ]:
        _list_item(doc, f)

    doc.add_heading("2.4 Modélisation des acteurs", level=2)
    _para(doc, "Le Tableau 3 présente les quatre acteurs identifiés.")
    _make_table(doc, ["Acteur","Description","Rôle","Cas d\'utilisation"],
        [["Citoyen","Habitant de la ville","CITIZEN","Signaler, suivre, feedback"],
         ["Agent Sectoriel","Employé municipal","SECTOR","Assignations, résolution"],
         ["Administrateur","Gestionnaire plateforme","ADMIN","CRUD, analytics, audit"],
         ["Système IA","Moteur IA","Automatique","Classification, prédiction"]]
    )

    doc.add_heading("2.5 Diagramme des cas d\'utilisation", level=2)
    _para(doc, "Le diagramme (Figure 2) présente 27 cas d\'utilisation avec 4 acteurs.")
    _mkp(doc, "[Insérer Figure 2 : Diagramme de Cas d\'Utilisation Général]", before=3, after=3)
    for a in [
        "Citoyen (7 cas) : inscription, connexion, signalement, consultation, suivi, profil, feedback",
        "Agent sectoriel (5 cas) : assignations, statut, notes, résolution, demande info",
        "Administrateur (10 cas) : gestion utilisateurs, catégories, priorités, secteurs, signalements, notifications, analytics, rapports, audit, escalade",
        "Système IA (5 cas) : classification, priorisation, anomalies, prédiction, notification",
    ]:
        _list_item(doc, a)

    doc.add_heading("2.6 Spécification détaillée des cas d\'utilisation", level=2)

    doc.add_heading("UC-03 : Signaler un problème urbain", level=3)
    _bold_item(doc, "Acteur : ", "Citoyen")
    _bold_item(doc, "Scénario principal : ", "Le citoyen remplit le formulaire (titre, description, catégorie, localisation, photos), soumet le signalement. Le système valide, déclenche l\'analyse IA et notifie le citoyen.")
    _para(doc, "Extensions : soumission anonyme, upload échoué, géolocalisation automatique, catégorie suggérée par l\'IA.")

    doc.add_heading("UC-11 : Résoudre un signalement", level=3)
    _bold_item(doc, "Acteur : ", "Agent Sectoriel")
    _para(doc, "L\'agent consulte le signalement, effectue l\'intervention, décrit la résolution, ajoute des photos et soumet. Le système change le statut en RESOLVED et notifie le citoyen.")

    doc.add_heading("UC-21 : Envoyer des notifications", level=3)
    _bold_item(doc, "Acteur : ", "Administrateur")
    _para(doc, "L\'administrateur choisit le type d\'envoi, les destinataires, le canal, saisit le message et envoie. Le système tente la livraison avec retry automatique en cas d\'échec.")

    doc.add_heading("2.7 Conclusion du chapitre", level=2)
    _para(doc, ("Ce chapitre a présenté une analyse exhaustive des besoins. Nous avons identifié 8 catégories "
        "fonctionnelles, 4 acteurs et 27 cas d\'utilisation. Le chapitre suivant détaille la conception architecturale."))


    # ═══ CHAPITRE 3 ═══
    section = _section_break(doc)
    _setup_footer(section, page_num=True)
    _setup_header(section, "Chapitre 3 : Conception Architecturale")

    doc.add_heading("CHAPITRE 3 : CONCEPTION ARCHITECTURALE", level=1)

    doc.add_heading("3.1 Introduction", level=2)
    _para(doc, ("Ce chapitre présente la conception détaillée du système : architecture en couches, patrons "
        "architecturaux, hiérarchie des exceptions, architecture événementielle, modèle de données et "
        "machine à états du signalement."))

    doc.add_heading("3.2 Architecture globale du système", level=2)

    doc.add_heading("3.2.1 Architecture en couches (Clean Architecture)", level=3)
    _para(doc, "L\'architecture suit les principes de la Clean Architecture avec 4 couches :")
    for l in [
        "Couche API (Routes) : 16 modules routeurs, validation Pydantic v2, documentation OpenAPI",
        "Couche Service : 19 classes de service avec logique métier et orchestrations",
        "Couche Repository : 8 repositories avec pattern CRUD générique",
        "Couche Données : 9 modèles SQLAlchemy ORM 2.0 avec relations et index",
    ]:
        _list_item(doc, l)
    _para(doc, "Les dépendances pointent de l\'extérieur vers l\'intérieur (Dependency Rule).")

    doc.add_heading("3.2.2 Architecture de déploiement", level=3)
    _mkp(doc, "[Insérer Figure 6 : Diagramme de Déploiement - Architecture Physique]", before=3, after=3)
    for d in [
        "Navigateur utilisateur : React SPA via HTTPS",
        "Docker Host : Frontend Nginx, Backend Uvicorn (4 workers), Celery Worker",
        "PostgreSQL 15 avec connexion pool asyncpg",
        "Redis 7 : cache LRU, sessions, broker Celery, rate limiting",
        "SMTP Gmail pour notifications email avec STARTTLS",
    ]:
        _list_item(doc, d)

    doc.add_heading("3.3 Patrons architecturaux avancés", level=2)

    doc.add_heading("3.3.1 Repository Pattern", level=3)
    _para(doc, ("Le Repository Pattern fait office de médiateur entre la couche domaine et la persistance. "
        "Chaque entité dispose d\'un repository dédié avec opérations CRUD de base. Avantages : "
        "abstraction de la persistance, testabilité, réutilisabilité et requêtes optimisées."))

    doc.add_heading("3.3.2 Service Layer Pattern", level=3)
    _para(doc, ("Centralise la logique métier dans une couche dédiée, séparée des routes HTTP et des repositories. "
        "19 services métier avec audit logging, validation des permissions et gestion des transactions."))

    doc.add_heading("3.3.3 Dependency Injection", level=3)
    _para(doc, ("FastAPI offre un système de DI natif via Depends(). Avantages : testabilité (mocks), "
        "flexibilité (configurations injectées), séparation des préoccupations."))

    doc.add_heading("3.4 Hiérarchie des exceptions", level=2)
    _para(doc, "Nous avons conçu 13 classes d\'exceptions personnalisées (Tableau 5).")
    _make_table(doc, ["Classe","Code HTTP","Usage"],
        [["UrbainException","500","Classe de base"],
         ["NotFoundError","404","Ressource non trouvée"],
         ["ValidationError","422","Données invalides"],
         ["AuthenticationError","401","Échec d\'authentification"],
         ["AuthorizationError","403","Permission insuffisante"],
         ["BusinessLogicError","409","Violation règle métier"],
         ["ConflictError","409","Conflit de données"],
         ["RateLimitError","429","Dépassement limite"],
         ["ServiceUnavailableError","503","Service indisponible"],
         ["IntegrationError","502","Erreur d\'intégration"],
         ["DatabaseError","500","Erreur base de données"],
         ["AIServiceError","500","Erreur pipeline IA"],
         ["NotificationError","500","Erreur envoi notification"]]
    )

    doc.add_heading("3.5 Architecture événementielle et notifications", level=2)
    _mkp(doc, "[Insérer Figure 11 : Architecture événementielle du système de notification]", before=3, after=3)
    _para(doc, "Le système adopte une architecture événementielle en 4 phases :")
    for p in [
        "Émission d\'événement métier via EventBus (SignalCreatedEvent, SignalResolvedEvent)",
        "Orchestration par NotificationOrchestrator qui écoute et décide des notifications à créer",
        "File d\'attente asynchrone Redis via Celery pour traitement différé",
        "Livraison avec retry exponentiel et mise à jour du statut",
    ]:
        _list_item(doc, p)

    doc.add_heading("3.6 Conception des données", level=2)

    doc.add_heading("3.6.1 Modèle conceptuel des données", level=3)
    _mkp(doc, "[Insérer Figure 3 : Diagramme de Classes UML]", before=3, after=3)
    _para(doc, "9 entités : User, Signal, Category, Priority, Sector, Notification, Report, AuditLog, PasswordResetToken.")

    doc.add_heading("3.6.2 Schéma relationnel", level=3)
    _mkp(doc, "[Insérer Figure 9 : Schéma de la Base de Données Relationnelle]", before=3, after=3)

    doc.add_heading("3.6.3 Description des entités", level=3)
    for bp, t in [
        ("User : ", "email, username, password hashé, nom, prénom, téléphone, rôle, statut, préférences notification JSON."),
        ("Signal : ", "entité centrale : titre, description, coordonnées GPS, statut, catégorie, priorité, sources, médias JSON, scores IA."),
        ("Category : ", "catégories hiérarchiques avec icône, couleur, mots-clés IA."),
        ("Priority : ", "niveaux avec configuration SLA (temps réponse, résolution, escalade)."),
        ("Sector : ", "secteurs municipaux avec type, horaires, capacités."),
        ("Notification : ", "type, canal, priorité, statut, contenu template, suivi livraison JSON."),
    ]:
        _bold_item(doc, bp, t)

    doc.add_heading("3.6.4 Dictionnaire des données", level=3)
    _para(doc, "Le Tableau 4 présente un extrait du dictionnaire des données.")
    _make_table(doc, ["Table","Colonne","Type","Contrainte","Description"],
        [["users","id","SERIAL","PK","Identifiant unique"],
         ["users","email","VARCHAR(255)","UNIQUE, NOT NULL","Adresse email"],
         ["users","role","ENUM","NOT NULL","CITIZEN, ADMIN, SECTOR"],
         ["signals","id","SERIAL","PK","Identifiant unique"],
         ["signals","latitude","FLOAT","CHECK(-90,90)","Latitude GPS"],
         ["signals","longitude","FLOAT","CHECK(-180,180)","Longitude GPS"],
         ["signals","status","ENUM","NOT NULL","9 états (DRAFT à CLOSED)"],
         ["categories","name","VARCHAR(100)","NOT NULL","Nom catégorie"],
         ["notifications","channel","ENUM","NOT NULL","EMAIL, SMS, WHATSAPP, PUSH"],
         ["notifications","status","ENUM","NOT NULL","PENDING à FAILED"]]
    )

    doc.add_heading("3.7 Conception des services", level=2)

    doc.add_heading("3.7.1 Service d\'authentification (JWT dual-token)", level=3)
    _mkp(doc, "[Insérer Figure 13 : Flux d\'authentification JWT Dual-Token]", before=3, after=3)
    for i in [
        "Access token : 30 min, HS256, payload sub/type/role/exp/iat",
        "Refresh token : 7 jours, renouvellement sans reconnexion",
        "Bcrypt avec 12 rounds de salage et 3 rôles RBAC",
    ]:
        _list_item(doc, i)

    doc.add_heading("3.7.2 Service de notification", level=3)
    _mkp(doc, "[Insérer Figure 10 : Architecture du Système de Notification Multicanal]", before=3, after=3)
    for i in [
        "4 canaux avec interface commune NotificationChannel",
        "Retry exponentiel : 5 min, 15 min, 45 min, circuit breaker",
        "Bulk sending par lots de 50 et fallback console",
    ]:
        _list_item(doc, i)

    doc.add_heading("3.7.3 Service IA (pipeline ML)", level=3)
    _mkp(doc, "[Insérer Figure 7 : Pipeline IA]", before=3, after=3)
    for i in [
        "Classification TF-IDF + Logistic Regression (85 % accuracy)",
        "Score priorité composite : sévérité×0,4 + urgence×0,35 + impact×0,25",
        "Anomalies Isolation Forest et prédiction tendances",
    ]:
        _list_item(doc, i)

    doc.add_heading("3.7.4 Services analytics et signalement", level=3)
    _para(doc, ("Analytics : dashboard, tendances, hotspots DBSCAN (eps=0.01), performance secteurs. "
        "Signalement : workflow 9 états, référence unique, assignation automatique, escalade SLA."))

    doc.add_heading("3.8 Diagrammes de séquence", level=2)
    _mkp(doc, "[Insérer Figure 4 : Diagramme de Séquence - Envoi d\'une Notification]", before=3, after=3)
    _para(doc, "Phase 1 : Création (validation → enregistrement PENDING). Phase 2 : Envoi (template → canal → livraison). Phase 3 : Suivi (statut → logs → retour).")

    doc.add_heading("3.9 Machine à états du signalement", level=2)
    _mkp(doc, "[Insérer Figure 5 : Diagramme d\'États - Cycle de Vie d\'un Signalement]", before=3, after=3)
    _para(doc, "9 états : DRAFT, SUBMITTED, UNDER_REVIEW, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED (terminal), CANCELLED (terminal), REJECTED (terminal).")
    _para(doc, "Transitions avec garde : SLA dépassé, 7 jours sans feedback.")

    doc.add_heading("3.10 Conclusion du chapitre", level=2)
    _para(doc, ("Ce chapitre a présenté la conception architecturale complète : Clean Architecture, patrons "
        "Repository/Service Layer/DI, 13 exceptions, architecture événementielle, 9 entités et machine "
        "à états. Le chapitre suivant présente l\'implémentation concrète."))


    # ═══ CHAPITRE 4 ═══
    section = _section_break(doc)
    _setup_footer(section, page_num=True)
    _setup_header(section, "Chapitre 4 : Implémentation et Réalisation")

    doc.add_heading("CHAPITRE 4 : IMPLÉMENTATION ET RÉALISATION", level=1)

    doc.add_heading("4.1 Introduction", level=2)
    _para(doc, ("Ce chapitre présente la réalisation concrète : environnement de développement, structure "
        "du projet, backend avec sessions asynchrones SQLAlchemy, cache LRU, rate limiting, frontend "
        "React et système de notifications multi-canaux."))

    doc.add_heading("4.2 Environnement de développement", level=2)

    doc.add_heading("4.2.1 Environnement matériel", level=3)
    _para(doc, "Intel Core i7 12e gen (14 cœurs, 20 threads), 32 Go DDR5, 512 Go SSD NVMe, Windows 11 + WSL2.")

    doc.add_heading("4.2.2 Environnement logiciel", level=3)
    _make_table(doc, ["Outil","Version","Usage"],
        [["Python","3.11.9","Runtime backend"],
         ["Node.js","20.15","Runtime frontend"],
         ["PostgreSQL","15.4","Base de données"],
         ["Redis","7.2.5","Cache LRU + file attente"],
         ["Docker","27.0","Conteneurisation"],
         ["Docker Compose","2.28","Orchestration"],
         ["Git","2.45","Gestion versions"],
         ["VS Code","1.89","Éditeur"],
         ["Postman","11.0","Test API"],
         ["DBeaver","23.3","Admin DB"]]
    )

    doc.add_heading("4.3 Structure du projet", level=2)
    doc.add_heading("4.3.1 Backend : API RESTful", level=3)
    _para(doc, "95+ endpoints REST organisés en 16 routeurs :")
    for m in [
        "auth.py : inscription, connexion, refresh, reset password, verify email",
        "users.py : CRUD utilisateurs, activation/suspension, rôles",
        "signals.py : CRUD signalements, workflow, upload",
        "categories.py : catégories hiérarchiques",
        "priorities.py : niveaux de priorité et SLA",
        "sectors.py : secteurs municipaux",
        "notifications.py : envoi individuel/groupé, retry, stats",
        "admin.py : audit logs, santé système",
        "analytics.py : dashboard, tendances, hotspots",
        "map.py : données géospatiales Leaflet",
    ]:
        _list_item(doc, m)

    doc.add_heading("4.4 Gestion avancée des sessions asynchrones SQLAlchemy", level=2)

    doc.add_heading("4.4.1 Configuration", level=3)
    _para(doc, ("Configuration avec async_sessionmaker dans core/database.py : pool_size=5, "
        "max_overflow=10, pool_pre_ping=True, expire_on_commit=False (crucial pour éviter "
        "DetachedInstanceError)."))

    doc.add_heading("4.4.2 Injection et chargement eager", level=3)
    _para(doc, ("Session injectée via get_db() avec commit/rollback automatique. Utilisation systématique "
        "de selectinload(), joinedload() et sérialisation explicite avant fermeture de session."))

    doc.add_heading("4.5 Mécanismes de cache et d\'optimisation", level=2)

    doc.add_heading("4.5.1 Cache LRU avec TTL", level=3)
    _make_table(doc, ["Donnée","Clé Redis","TTL"],
        [["Dashboard stats","cache:dashboard:{period}","5 min"],
         ["Catégories","cache:categories","1 h"],
         ["Priorités","cache:priorities","1 h"],
         ["Tendances","cache:trends:{period}","15 min"],
         ["Hotspots","cache:hotspots:{period}","15 min"]]
    )

    doc.add_heading("4.5.2 Indexation et optimisation N+1", level=3)
    _para(doc, ("Index sur signals(status/created_at/lat-lng/category_id/priority_id), "
        "notifications(status/user_id), users(email/role). Problème N+1 résolu par "
        "selectinload/joinedload/subqueryload avec pagination 20-100 éléments."))

    doc.add_heading("4.6 Algorithme de Rate Limiting", level=2)
    _para(doc, ("Sliding Window Counter avec Redis : 60 requêtes/minute par utilisateur, "
        "100 en burst. Réponse 429 avec en-têtes X-RateLimit complets."))

    doc.add_heading("4.7 Frontend : Interface utilisateur", level=2)

    doc.add_heading("4.7.1 Architecture React", level=3)
    for f in [
        "Couche API : Axios avec intercepteurs JWT et refresh automatique",
        "Couche Composants : LoadingSpinner, Gauge, StatCard, DataTable, Modal",
        "Couche Contexte : AuthContext, ToastContext, TabContext",
        "Couche Pages : admin/18, signals/11, auth/5, profile/, reports/, map/",
        "TanStack Query avec staleTime 30s-5min et mutations optimistes",
    ]:
        _list_item(doc, f)

    doc.add_heading("4.7.2 Dashboard et carte Leaflet", level=3)
    _mkp(doc, "[Insérer Figure 8 : Tableau de Bord Administrateur]", before=3, after=3)
    _para(doc, ("Dashboard : 11 sections, 4 KPIs, graphique tendances Recharts, diagramme circulaire, "
        "tableau performance 7 secteurs. Carte : MarkerCluster, heatmap, filtres, popup, géocodage."))

    doc.add_heading("4.8 Système de notification", level=2)

    doc.add_heading("4.8.1 Services d\'envoi", level=3)
    for bp, t in [
        ("Email (EmailService) : ", "SMTP Gmail:587 STARTTLS, 4 templates Jinja2, envoi groupé par 50."),
        ("SMS (SmsService) : ", "email-to-SMS gateway gratuit, 30+ opérateurs, fallback TextBelt + mock."),
        ("WhatsApp : ", "pywhatkit 5.4 (session Web active), fallback console."),
        ("Push : ", "FCM HTTP/2 avec titre/corps/icône/data payload."),
    ]:
        _bold_item(doc, bp, t)

    doc.add_heading("4.8.2 Mécanisme de retry", level=3)
    _para(doc, ("Exponential Backoff ×3 : T1 immédiate, T2 après 5 min, T3 après 15 min. "
        "Max 3 tentatives puis circuit breaker. Logs dans delivery_logs (JSON array)."))

    doc.add_heading("4.9 Captures d\'écran", level=2)
    _mkp(doc, "[Insérer Figure 14 : Captures d\'Écran des Principales Interfaces]", before=3, after=3)
    _para(doc, "6 vues clés : connexion, création signalement, détail signalement, dashboard admin, gestion notifications, carte interactive.")

    doc.add_heading("4.10 Conclusion du chapitre", level=2)
    _para(doc, ("Ce chapitre a présenté l\'implémentation : 16 modules API, 19 services, 8 repositories, "
        "40+ pages React, système multi-canaux. Les mécanismes avancés (SQLAlchemy async, cache LRU, "
        "rate limiting) garantissent performance et scalabilité."))


    # ═══ CHAPITRE 5 ═══
    section = _section_break(doc)
    _setup_footer(section, page_num=True)
    _setup_header(section, "Chapitre 5 : Tests, Validation et Déploiement")

    doc.add_heading("CHAPITRE 5 : TESTS, VALIDATION ET DÉPLOIEMENT", level=1)

    doc.add_heading("5.1 Introduction", level=2)
    _para(doc, ("Ce chapitre présente la stratégie de test, les résultats détaillés (Tableau 7), les "
        "benchmarks (Tableau 8), le pipeline CI/CD (Tableau 9) et le déploiement Docker."))

    doc.add_heading("5.2 Stratégie de test", level=2)

    doc.add_heading("5.2.1 Tests unitaires", level=3)
    _para(doc, "Services testés avec mocks (pytest-mock), repositories avec PostgreSQL isolé, "
          "schémas Pydantic validés exhaustivement, fonctions JWT et bcrypt testées unitairement.")

    doc.add_heading("5.2.2 Tests d\'intégration", level=3)
    _para(doc, "API endpoints via TestClient FastAPI avec session DB réelle, workflow signalement "
          "complet (DRAFT à CLOSED), pipeline IA avec textes réels, 35 scénarios notification.")

    doc.add_heading("5.2.3 Tests de notification", level=3)
    _para(doc, "35 scénarios : création (10 types × 4 canaux), envoi individuel/groupé, retry, "
          "annulation, erreurs, statistiques, notifications liées aux signalements.")

    doc.add_heading("5.3 Résultats détaillés des tests", level=2)
    _make_table(doc, ["Suite de tests","Nombre","Réussis","Échoués","Couverture","Temps"],
        [["Authentification","8","8","0","100%","1,2s"],
         ["CRUD Utilisateurs","6","6","0","100%","0,8s"],
         ["CRUD Signalements","8","8","0","100%","1,5s"],
         ["CRUD Catégories","4","4","0","100%","0,4s"],
         ["CRUD Priorités","4","4","0","100%","0,4s"],
         ["CRUD Secteurs","4","4","0","100%","0,5s"],
         ["Notifications","35","35","0","100%","4,8s"],
         ["Pipeline IA","6","6","0","100%","2,1s"],
         ["Analytics","4","4","0","100%","1,9s"],
         ["Workflow signalement","8","8","0","100%","1,3s"],
         ["Total","87","87","0","100%","14,9s"]]
    )
    _para(doc, "Tous les tests passent avec 100 % de réussite et un temps total de 14,9 secondes.")

    doc.add_heading("5.4 Performance et benchmarks", level=2)
    _make_table(doc, ["Opération","Sans cache","Avec cache","Amélioration"],
        [["Dashboard stats","850 ms","120 ms","86%"],
         ["Liste signalements","95 ms","45 ms","53%"],
         ["Détail signalement","65 ms","35 ms","46%"],
         ["Classification IA","180 ms","-","-"],
         ["Hotspots DBSCAN","350 ms","60 ms","83%"],
         ["Login JWT","25 ms","-","-"],
         ["Refresh token","15 ms","-","-"]]
    )
    _para(doc, "Temps de réponse API < 150 ms pour 95 % des requêtes. Cache Redis : amélioration de 46 % à 86 %.")

    doc.add_heading("5.5 Pipeline CI/CD", level=2)
    _make_table(doc, ["Étape","Durée","Actions"],
        [["Checkout","10s","Récupération code"],
         ["Setup Python","30s","Python 3.11 + cache pip"],
         ["Install backend","45s","pip install"],
         ["Lint backend","20s","flake8 + mypy + black"],
         ["Setup Node.js","20s","Node.js 20 + cache npm"],
         ["Install frontend","30s","npm ci"],
         ["Lint frontend","15s","eslint + prettier"],
         ["Build frontend","40s","npm run build (Vite)"],
         ["Tests backend","60s","pytest --cov"],
         ["Build Docker","50s","docker build"],
         ["Push image","30s","docker push (main)"],
         ["Deploy","40s","Déploiement auto"]]
    )
    _para(doc, "Pipeline complet en environ 6 minutes avec GitHub Actions.")

    doc.add_heading("5.6 Déploiement", level=2)
    doc.add_heading("5.6.1 Docker et conteneurisation", level=3)
    _para(doc, "Système entièrement conteneurisé : backend (python:3.11-slim, port 8000, 4 workers Uvicorn), "
          "frontend (build Vite + Nginx), base de données (PostgreSQL 15), cache (Redis 7).")

    doc.add_heading("5.6.2 Configuration Docker Compose", level=3)
    _para(doc, "3 services : backend, db (postgres:15, port 5433), redis (redis:7). Health checks, "
          "restart unless-stopped, volumes persistants.")

    doc.add_heading("5.7 Difficultés rencontrées et solutions", level=2)
    difficulties = [
        ("ORM et async SQLAlchemy : ", "sessions asynchrones sans lazy loading hors contexte. Solution : eager loading + sérialisation explicite."),
        ("Appels asynchrones bloquants : ", "smtplib bloquait la boucle asynchrone. Solution : aiosmtplib + Celery."),
        ("Kubernetes trop complexe : ", "migration vers Docker Compose avec 3 services."),
        ("Pipeline IA sans GPU : ", "scikit-learn TF-IDF + Logistic Regression au lieu de Transformers."),
        ("Notifications WhatsApp : ", "pywhatkit nécessite session active. Fallback console logging."),
        ("SMS payant : ", "Twilio coûteux. Solution : passerelle email-to-SMS gratuite avec 30+ opérateurs."),
    ]
    for bp, t in difficulties:
        _bold_item(doc, bp, t)

    doc.add_heading("5.8 Conclusion du chapitre", level=2)
    _para(doc, ("Ce chapitre a présenté la stratégie de test (87 tests, 100 % réussite), les performances "
        "(API < 150 ms, cache 46-86 % d\'amélioration), le pipeline CI/CD (6 min) et le déploiement "
        "Docker Compose (3 services)."))

    # ═══ CONCLUSION GÉNÉRALE ═══
    section = _section_break(doc)
    _setup_footer(section, page_num=True)
    _setup_header(section, "Conclusion générale")

    doc.add_heading("CONCLUSION GÉNÉRALE", level=1)

    doc.add_heading("Récapitulation de la démarche", level=2)
    _para(doc, ("Ce projet de fin d\'études avait pour objectif la conception et le développement d\'Urbain "
        "Sustainability System, une plateforme intelligente de signalement et de gestion des problèmes "
        "urbains. Partant du constat que les villes font face à une urbanisation croissante et que les "
        "processus de signalement sont souvent manuels, lents et dépourvus d\'intelligence décisionnelle, "
        "nous avons proposé une solution intégrée combinant interface citoyenne moderne, intelligence "
        "artificielle, notifications multi-canaux et analytics en temps réel."))

    doc.add_heading("Contributions", level=2)
    for c in [
        "Architecture en couches avec Clean Architecture et patrons Repository, Service Layer, DI",
        "Pipeline IA complet : classification NLP (TF-IDF + LR, 85 % accuracy), priorisation, anomalies, prédiction",
        "Système de notification multi-canaux resilient avec retry exponentiel et fallback",
        "Passerelle SMS gratuite email-to-SMS avec 30+ opérateurs internationaux",
        "API REST exhaustive : 95+ endpoints, 16 modules, documentation Swagger/OpenAPI",
        "Cache LRU Redis, rate limiting Sliding Window Counter, SQLAlchemy 2.0 async",
        "Interface d\'administration complète : 18 pages, RBAC, audit logs",
        "Pipeline CI/CD GitHub Actions en 12 étapes (6 minutes)",
    ]:
        _list_item(doc, c)

    doc.add_heading("Résultats obtenus", level=2)
    for r in [
        "95+ endpoints API, 16 modules, 19 services, 8 repositories, 9 modèles ORM",
        "Frontend React 19 : 40+ pages, 18 pages admin, Leaflet, Recharts",
        "Pipeline IA : 85 % accuracy classification, détection anomalies, prédiction tendances",
        "Notifications multi-canaux : Email, SMS, WhatsApp, Push avec retry exponentiel",
        "87 tests automatisés, 100 % réussite, temps réponse API < 150 ms",
        "Docker Compose avec 3 services, health checks, volumes persistants",
    ]:
        _list_item(doc, r)

    doc.add_heading("Perspectives et améliorations futures", level=2)
    for p in [
        "Application mobile native Android (Kotlin) et iOS (Swift)",
        "Intégration IoT avec capteurs urbains (qualité air, niveau eaux, trafic)",
        "Modèles Transformers CamemBERT/BERT pour le français et l\'arabe",
        "Chatbot IA conversationnel pour guider les citoyens",
        "Analyse d\'images par vision par ordinateur",
        "Blockchain pour enregistrement immutable des signalements",
        "Jumeau numérique (Digital Twin) 3D de la ville",
        "Moteur de recommandations prédictif pour maintenance proactive",
    ]:
        _list_item(doc, p)

    _para(doc, ("En conclusion, ce projet a démontré la faisabilité d\'une plateforme intelligente de gestion "
        "urbaine alliant technologies web modernes, intelligence artificielle et notifications multi-canaux. "
        "La plateforme Urbain Sustainability System se positionne comme une alternative open source crédible "
        "aux solutions propriétaires onéreuses."))

    # ═══ BIBLIOGRAPHIE ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Bibliographie")
    doc.add_heading("BIBLIOGRAPHIE", level=1)

    refs = [
        "[1] R. C. Martin, Clean Architecture: A Craftsman\'s Guide to Software Structure and Design. Prentice Hall, 2017.",
        "[2] S. Habib, FastAPI: Modern Python Web Development. O\'Reilly Media, 2023.",
        "[3] S. Bird, E. Klein, and E. Loper, Natural Language Processing with Python. O\'Reilly Media, 2009.",
        "[4] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.",
        "[5] United Nations, World Urbanization Prospects: The 2018 Revision. New York: United Nations, 2019.",
        "[6] M. Fowler, Patterns of Enterprise Application Architecture. Addison-Wesley, 2002.",
        "[7] E. Gamma, R. Helm, R. Johnson, and J. Vlissides, Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley, 1994.",
        "[8] A. Paszke et al., \"PyTorch: An Imperative Style, High-Performance Deep Learning Library,\" NeurIPS 2019.",
        "[9] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of Deep Bidirectional Transformers,\" NAACL 2019.",
        "[10] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" KDD 2016.",
        "[11] McKinsey Global Institute, Smart Cities: Digital Solutions for a More Livable Future, 2018.",
        "[12] ITU, Smart Sustainable Cities: An Analysis of Definitions, 2015.",
        "[13] Banque Mondiale, Urban Development Overview, 2023.",
        "[14] Mordor Intelligence, Smart Cities Market - Growth, Trends, and Forecasts, 2024.",
        "[15] OCDE, Enhancing the Contribution of Digitalisation to Smart Cities, 2021.",
    ]
    for ref in refs:
        _mkp(doc, ref, before=2, after=2, lsp=1.3)

    # ═══ ANNEXES ═══
    section = _section_break(doc)
    _setup_footer(section)
    _setup_header(section, "Annexes")
    doc.add_heading("ANNEXES", level=1)

    doc.add_heading("Annexe A : Guide d\'installation", level=2)
    _para(doc, "Prérequis : Python 3.11+, Node.js 20+, Docker, PostgreSQL 15, Redis 7.")
    _para(doc, "Installation backend :")
    for s in [
        "Cloner le dépôt : git clone https://github.com/username/urbain-sustainability.git",
        "Installer les dépendances : pip install -r requirements.txt",
        "Configurer le fichier .env (base de données, SMTP, JWT secret)",
        "Lancer les migrations : alembic upgrade head",
        "Démarrer le serveur : uvicorn app.main:app --reload",
    ]:
        _list_item(doc, s)
    _para(doc, "Installation frontend :")
    for s in [
        "cd frontend && npm install",
        "Configurer le fichier .env (VITE_API_URL)",
        "Lancer le développement : npm run dev",
        "Build production : npm run build",
    ]:
        _list_item(doc, s)

    doc.add_heading("Annexe B : Variables d\'environnement", level=2)
    _make_table(doc, ["Variable","Description","Défaut"],
        [["DATABASE_URL","URL de connexion PostgreSQL","postgresql+asyncpg://..."],
         ["SECRET_KEY","Clé secrète JWT","(obligatoire)"],
         ["SMTP_HOST","Serveur SMTP","smtp.gmail.com"],
         ["SMTP_PORT","Port SMTP","587"],
         ["SMTP_USER","Utilisateur SMTP","(optionnel)"],
         ["SMTP_PASSWORD","Mot de passe SMTP","(optionnel)"],
         ["REDIS_URL","URL de connexion Redis","redis://localhost:6379"],
         ["FCM_CREDENTIALS","Credentials Firebase","(optionnel)"]]
    )

    doc.add_heading("Annexe C : Structure du projet", level=2)
    project_structure = [
        "urbain-sustainability/",
        "├── backend/",
        "│   ├── app/",
        "│   │   ├── api/v1/ (16 routeurs)",
        "│   │   ├── core/ (config, security, cache, database)",
        "│   │   ├── models/ (9 modèles ORM)",
        "│   │   ├── schemas/ (Pydantic)",
        "│   │   ├── services/ (19 services)",
        "│   │   ├── repositories/ (8 repositories)",
        "│   │   └── ai/ (pipeline ML)",
        "│   ├── alembic/ (migrations)",
        "│   └── tests/",
        "├── frontend/",
        "│   ├── src/",
        "│   │   ├── api/ (Axios client)",
        "│   │   ├── components/",
        "│   │   ├── contexts/",
        "│   │   └── pages/ (40+ pages)",
        "│   └── public/",
        "├── docker-compose.yml",
        "└── README.md",
    ]
    for s in project_structure:
        _mkp(doc, s, before=0, after=0, size=10 if s.startswith("├") or s.startswith("└") else 11)

    doc.add_heading("Annexe D : Diagrammes UML", level=2)
    _para(doc, "Cette annexe contient les diagrammes UML complets du système.")
    for fig in [
        "Figure 1 : Architecture Globale du Système",
        "Figure 2 : Diagramme de Cas d\'Utilisation Général",
        "Figure 3 : Diagramme de Classes UML",
        "Figure 4 : Diagramme de Séquence - Notification",
        "Figure 5 : Diagramme d\'États - Cycle de Vie",
        "Figure 6 : Diagramme de Déploiement",
        "Figure 7 : Pipeline IA",
        "Figure 8 : Tableau de Bord Administrateur",
        "Figure 9 : Schéma de la Base de Données",
        "Figure 10 : Architecture Notification Multicanal",
        "Figure 11 : Architecture Événementielle",
        "Figure 12 : Diagramme de Gantt",
        "Figure 13 : Flux d\'authentification JWT",
        "Figure 14 : Captures d\'Écran",
    ]:
        _mkp(doc, fig, before=1, after=1, lsp=1.2)

    # ═══ SAVE ═══
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RAPPORT_PFE_URBAIN.docx")
    doc.save(output_path)
    print(f"Document saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_rapport()

