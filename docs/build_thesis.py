#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_thesis.py
Generates DIPLOMA_MIKE_FORMATTED.docx from source paragraphs.
"""

import json
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ---------------------------------------------------------------------------
# Load source paragraphs
# ---------------------------------------------------------------------------
SRC = "C:/Projects/MIKE_DIPLOMA/docs/source_paragraphs.json"
with open(SRC, encoding="utf-8") as f:
    RAW = json.load(f)

def par(idx):
    """Return full text of source paragraph by index."""
    return RAW.get(str(idx), "")

def clean(text):
    """Remove publisher notes in parentheses at end of paragraphs."""
    # Remove trailing notes like (Springer), (ACM Digital Library), etc.
    text = re.sub(r'\s*\([A-Za-z][^)]{0,60}\)\s*$', '', text.strip())
    return text.strip()

# ---------------------------------------------------------------------------
# Document setup
# ---------------------------------------------------------------------------
doc = Document()

# Page margins: top/bottom 2.5cm, left 3cm, right 2.5cm
from docx.oxml.ns import qn
section = doc.sections[0]
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(3.0)
section.right_margin = Cm(2.5)

# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def set_body_format(para, first_indent=True):
    """Apply standard body text formatting."""
    pf = para.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)
    if first_indent:
        pf.first_line_indent = Cm(0.5)
    else:
        pf.first_line_indent = Cm(0)
    for run in para.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(11)


def add_body(text, first_indent=True):
    """Add a justified body paragraph."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)
    if first_indent:
        pf.first_line_indent = Cm(0.5)
    else:
        pf.first_line_indent = Cm(0)
    return p


def add_heading1(text):
    """Chapter heading — 16pt bold dark blue."""
    p = doc.add_heading(text, level=1)
    for run in p.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(31, 73, 125)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_heading2(text):
    """Section heading — 13pt bold."""
    p = doc.add_heading(text, level=2)
    for run in p.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    return p


def add_heading3(text):
    """Subsection heading — 11pt bold."""
    p = doc.add_heading(text, level=3)
    for run in p.runs:
        run.font.name = "Calibri"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    return p


def add_code_block(text):
    """Add a code block paragraph — Courier New 9pt, no indent."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Courier New"
    run.font.size = Pt(9)
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf.space_after = Pt(3)
    pf.space_before = Pt(3)
    pf.first_line_indent = Cm(0)
    pf.left_indent = Cm(1)
    # Grey shading
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "E8E8E8")
    pPr.append(shd)
    return p


def add_center(text, size=12, bold=False, italic=False, color=None):
    """Add a centered paragraph."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.space_before = Pt(4)
    return p


def add_blank():
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    return p


def page_break():
    doc.add_page_break()


# ===========================================================================
# PAGE 1 — COVER PAGE
# ===========================================================================
add_blank()
add_blank()
add_center("ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΑΤΡΩΝ", size=16, bold=True)
add_center("ΠΟΛΥΤΕΧΝΙΚΗ ΣΧΟΛΗ", size=14, bold=True)
add_center("ΤΜΗΜΑ ΜΗΧΑΝΙΚΩΝ ΗΛΕΚΤΡΟΝΙΚΩΝ ΥΠΟΛΟΓΙΣΤΩΝ ΚΑΙ ΠΛΗΡΟΦΟΡΙΚΗΣ", size=12, bold=True)
add_blank()
add_blank()
add_center("Διπλωματική Εργασία", size=13, italic=True)
add_blank()
add_center("Σύστημα Διαχείρισης Γεω-Στοχευμένων Διαφημίσεων", size=16, bold=True)
add_center("Αθλητικών Εγκαταστάσεων σε Πραγματικό Χρόνο", size=16, bold=True)
add_blank()
add_center("Real-Time Geo-Targeted Advertising Management System", size=13)
add_center("for Sports Facilities", size=13)
add_blank()
add_blank()
add_center("Μιχάλης Δέμης", size=13, bold=True)
add_center("Α.Μ. 1080958", size=12)
add_blank()
add_blank()
add_center("Επιβλέπων", size=12)
add_center("Σιούτας Σπυρίδων, Καθηγητής", size=12, bold=True)
add_blank()
add_blank()
add_blank()
add_blank()
add_center("Πάτρα, 2025", size=12)

# ===========================================================================
# PAGE 2 — ΤΡΙΜΕΛΗΣ ΕΠΙΤΡΟΠΗ
# ===========================================================================
page_break()
add_blank()
add_blank()
add_center("Τριμελής Επιτροπή Αξιολόγησης", size=14, bold=True)
add_blank()
add_blank()
add_center("Σιούτας Σπυρίδων, Καθηγητής", size=12)
add_center("Γιαννούκου Ιωάννα", size=12)
add_center("Χαλκιόπουλος Κωνσταντίνος Θ.", size=12)

# ===========================================================================
# PAGE 3 — COPYRIGHT + ΥΠΕΥΘΥΝΗ ΔΗΛΩΣΗ
# ===========================================================================
page_break()
add_blank()
add_body("Copyright, all rights reserved, 2025", first_indent=False)
add_body("Με την επιφύλαξη παντός δικαιώματος.", first_indent=False)
add_blank()
add_body(
    "Απαγορεύεται η αντιγραφή, αποθήκευση και διανομή της παρούσας εργασίας, εξ' ολοκλήρου "
    "ή τμήματος αυτής, για εμπορικό σκοπό. Επιτρέπεται η ανατύπωση, αποθήκευση και διανομή "
    "για σκοπό μη κερδοσκοπικό, εκπαιδευτικής ή ερευνητικής φύσης, υπό την προϋπόθεση να "
    "αναφέρεται η πηγή προέλευσης.",
    first_indent=False
)
add_blank()

p_decl = doc.add_paragraph()
run = p_decl.add_run("Υπεύθυνη Δήλωση")
run.font.bold = True
run.font.name = "Calibri"
run.font.size = Pt(11)
p_decl.paragraph_format.space_after = Pt(6)

add_body(
    "Βεβαιώνω ότι είμαι συγγραφέας αυτής της διπλωματικής εργασίας, και ότι κάθε βοήθεια "
    "την οποία είχα για την προετοιμασία της είναι πλήρως αναγνωρισμένη και αναφέρεται στη "
    "διπλωματική εργασία. Επίσης έχω αναφέρει τις όποιες πηγές από τις οποίες έκανα χρήση "
    "δεδομένων, ιδεών ή λέξεων, είτε αυτές αναφέρονται ακριβώς είτε παραφρασμένες.",
    first_indent=False
)
add_blank()
add_blank()
add_blank()
add_body("(  Υπογραφή  )", first_indent=False)
add_body("…………………", first_indent=False)
add_body("Μιχάλης Δέμης", first_indent=False)

# ===========================================================================
# PAGE 4 — ΠΕΡΙΛΗΨΗ
# ===========================================================================
page_break()
add_heading1("Περίληψη")

add_body(clean(par(1)))
add_body(clean(par(2)))
add_body(clean(par(3)))
add_body(clean(par(4)))

add_blank()
p_kw_label = doc.add_paragraph()
run = p_kw_label.add_run("Λέξεις-Κλειδιά")
run.font.bold = True
run.font.name = "Calibri"
run.font.size = Pt(11)
p_kw_label.paragraph_format.space_after = Pt(3)

add_body(
    "Γεω-Στόχευση, Χωρική Ευρετηρίαση, R-Tree, WebSocket, Ασφάλεια Διαδικτύου, "
    "Ανίχνευση Απειλών, Real-time Συστήματα, Ψηφιακή Διαφήμιση, FastAPI, PostgreSQL/PostGIS",
    first_indent=False
)

# ===========================================================================
# PAGE 5 — ABSTRACT
# ===========================================================================
page_break()
add_heading1("Abstract")

add_body(
    "This diploma thesis presents the design and implementation of GEO-ADS, a real-time "
    "geo-targeted advertising management system for sports facilities. The problem addressed "
    "concerns the efficient and secure assignment of advertising content to multiple digital "
    "screens within a stadium, based on spectator geolocation, in an environment where "
    "requirements for low latency, scalability, and communication security are particularly demanding."
)
add_body(
    "The objective of this work is to develop a comprehensive software system supporting the "
    "display of advertisements on 28 digital stadium screens, leveraging geospatial data, "
    "real-time mechanisms, and multi-layered security. To this end, an architecture based on "
    "FastAPI and PostgreSQL/PostGIS for the backend, React for the frontend, and Electron for "
    "desktop packaging was implemented. In parallel, six security layers were integrated to "
    "protect endpoints, communication channels, and the overall system operation."
)
add_body(
    "The evaluation of GEO-ADS focused on two main axes: the efficiency of spatial indexing "
    "methods and the speed of threat detection. Experimental results demonstrated that R-Tree "
    "is 8.09x faster than Linear Scan for n=100,000, achieving 1.799ms versus 14.551ms. "
    "Furthermore, the hybrid threat detection mechanism, combining rule-based logic and Z-score "
    "statistical analysis, achieves a detection time of approximately 0.014ms."
)
add_body(
    "In conclusion, the proposed system demonstrates that safe and efficient management of "
    "geo-targeted advertising in sports facilities is feasible, combining spatial intelligence, "
    "real-time communication, and security mechanisms in a unified platform."
)

add_blank()
p_kw2 = doc.add_paragraph()
run = p_kw2.add_run("Keywords")
run.font.bold = True
run.font.name = "Calibri"
run.font.size = Pt(11)
p_kw2.paragraph_format.space_after = Pt(3)

add_body(
    "Geo-Targeting, Spatial Indexing, R-Tree, WebSocket, Web Security, Threat Detection, "
    "Real-time Systems, Digital Advertising, FastAPI, PostgreSQL/PostGIS",
    first_indent=False
)

# ===========================================================================
# PAGE 6 — ΕΥΡΕΤΗΡΙΟ ΕΙΚΟΝΩΝ
# ===========================================================================
page_break()
add_heading1("Ευρετήριο Εικόνων")
add_body("[ΣΥΜΠΛΗΡΩΝΕΤΑΙ ΜΕΤΑ ΤΗΝ ΕΙΣΑΓΩΓΗ ΟΛΩΝ ΤΩΝ ΕΙΚΟΝΩΝ]", first_indent=False)
add_blank()

figures = [
    "Εικόνα 1: Αρχιτεκτονική Συστήματος GEO-ADS\t[σελίδα]",
    "Εικόνα 2: Ζώνες Γηπέδου — GlassFloor, Surrounding Screens, Megatron\t[σελίδα]",
    "Εικόνα 3: ER Diagram Βάσης Δεδομένων\t[σελίδα]",
    "Εικόνα 4: Δομή R-Tree και Minimum Bounding Rectangles\t[σελίδα]",
    "Εικόνα 5: WebSocket Handshake Διαδικασία\t[σελίδα]",
    "Εικόνα 6: Auth Flow — Login, Token Scopes\t[σελίδα]",
    "Εικόνα 7: Screenshot VisualBoard — Προβολή 28 Οθονών\t[σελίδα]",
    "Εικόνα 8: Screenshot SecurityDashboard — Threat Detection\t[σελίδα]",
    "Εικόνα 9: Γράφημα Χρόνου vs N — Σύγκριση Μεθόδων\t[σελίδα]",
    "Εικόνα 10: Γράφημα Speedup vs N\t[σελίδα]",
]
for fig in figures:
    add_body(fig, first_indent=False)

# ===========================================================================
# PAGE 7 — ΑΦΙΕΡΩΣΗ
# ===========================================================================
page_break()
add_blank()
add_blank()
add_blank()
add_blank()
p_ded = doc.add_paragraph()
run = p_ded.add_run("Στην οικογένειά μου")
run.font.italic = True
run.font.name = "Calibri"
run.font.size = Pt(13)
p_ded.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_ded.paragraph_format.space_after = Pt(6)

# ===========================================================================
# PAGE 8 — ΕΥΧΑΡΙΣΤΙΕΣ
# ===========================================================================
page_break()
add_heading1("Ευχαριστίες")

add_body(
    "Θα ήθελα να εκφράσω τις ειλικρινείς ευχαριστίες μου στον επιβλέποντα καθηγητή μου "
    "κ. Σιούτα Σπυρίδωνα, για την πολύτιμη καθοδήγηση, τις εποικοδομητικές παρατηρήσεις "
    "και την εμπιστοσύνη που έδειξε στο πρόσωπό μου καθ' όλη τη διάρκεια εκπόνησης της "
    "παρούσας εργασίας."
)
add_body(
    "Επιπλέον, ευχαριστώ τα μέλη της τριμελούς επιτροπής, κα. Γιαννούκου Ιωάννα και "
    "κ. Χαλκιόπουλο Κωνσταντίνο Θ., για τον χρόνο που αφιέρωσαν στην αξιολόγηση αυτής "
    "της εργασίας."
)
add_body(
    "Τέλος, εκφράζω την ευγνωμοσύνη μου στην οικογένειά μου και στους φίλους μου, για τη "
    "συνεχή ηθική υποστήριξη και ενθάρρυνση που μου παρείχαν κατά τη διάρκεια των σπουδών μου."
)

# ===========================================================================
# CHAPTER 1 — ΕΙΣΑΓΩΓΗ
# ===========================================================================
page_break()
add_heading1("1. Εισαγωγή")

# 1.1
add_heading2("1.1. Κίνητρο και Πρόβλημα")
add_body(clean(par(7)))
add_body(clean(par(8)))
add_body(clean(par(9)))
add_body(clean(par(10)))

# 1.2
add_heading2("1.2. Στόχοι της Διπλωματικής Εργασίας")
add_body(clean(par(13)))

# Goals as numbered paragraphs
goals_raw = [par(14), par(15), par(16), par(17), par(18), par(19), par(20)]
for i, g in enumerate(goals_raw, 1):
    lines = g.strip().split('\n')
    # first line is the bold title
    title_line = lines[0].strip()
    desc_line = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    p = doc.add_paragraph(style="List Number")
    run_title = p.add_run(title_line)
    run_title.font.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(11)
    if desc_line:
        p.add_run("\n")
        run_desc = p.add_run(desc_line)
        run_desc.font.name = "Calibri"
        run_desc.font.size = Pt(11)
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_after = Pt(4)

add_body(clean(par(21)))

# 1.3
add_heading2("1.3. Ερευνητικές Ερωτήσεις")
add_body(clean(par(24)))

rqs = [par(25), par(26), par(27), par(28), par(29), par(30), par(31), par(32), par(33)]
chapters_map = {
    0: "4, 5",
    1: "3, 5, 6",
    2: "5",
    3: "4, 5",
    4: "4, 5",
    5: "5",
    6: "4, 5",
    7: "5",
    8: "3, 5, 6",
}
for i, rq_text in enumerate(rqs):
    lines = rq_text.strip().split('\n')
    title_line = lines[0].strip()
    desc_line = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    p = doc.add_paragraph()
    run_title = p.add_run(title_line)
    run_title.font.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(11)
    if desc_line:
        p.add_run(" ")
        run_desc = p.add_run(desc_line)
        run_desc.font.name = "Calibri"
        run_desc.font.size = Pt(11)
    p.add_run(" ")
    run_ch = p.add_run(f"Απαντάται στο/στα Κεφάλαιο/α {chapters_map[i]}.")
    run_ch.font.italic = True
    run_ch.font.name = "Calibri"
    run_ch.font.size = Pt(11)
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_after = Pt(5)
    pf.first_line_indent = Cm(0.5)

add_body(clean(par(34)))

# 1.4
add_heading2("1.4. Συνεισφορά της Εργασίας")
for idx in [37, 38, 39, 40, 41, 42, 43]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 1.5
add_heading2("1.5. Δομή της Εργασίας")
for idx in [47, 48, 49, 50, 51, 52, 53, 54, 55]:
    t = clean(par(idx))
    if t:
        add_body(t)

# ===========================================================================
# CHAPTER 2 — ΒΙΒΛΙΟΓΡΑΦΙΚΗ ΑΝΑΣΚΟΠΗΣΗ
# ===========================================================================
page_break()
add_heading1("2. Βιβλιογραφική Ανασκόπηση")
add_body(clean(par(59)))

# 2.1
add_heading2("2.1. Ψηφιακή Διαφήμιση και Γεω-Στόχευση")
for idx in [63, 64, 65, 66, 67, 68, 69, 70]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 2.2
add_heading2("2.2. Χωρικά Ευρετήρια")
add_body(clean(par(74)))

add_heading3("2.2.1. Από τα B-trees στα R-trees")
for idx in [76, 77]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading3("2.2.2. Παραλλαγές της οικογένειας R-tree")
for idx in [79, 80, 81, 82]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading3("2.2.3. PostGIS και GiST Ευρετήρια")
for idx in [84, 85]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading3("2.2.4. Κατανεμημένη Χωρική Επεξεργασία")
for idx in [87, 88]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading3("2.2.5. Σύγκριση και Κενό Γνώσης")
for idx in [90, 91]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 2.3
add_heading2("2.3. Real-time Αρχιτεκτονικές και WebSocket")
for idx in [94, 95, 96, 97, 98, 99, 100, 101, 102]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 2.4
add_heading2("2.4. Ασφάλεια Web Εφαρμογών")
for idx in [106, 107, 108, 109, 110, 111, 112, 113, 114]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 2.5
add_heading2("2.5. Ανίχνευση Ανωμαλιών")
for idx in [118, 119, 120, 121, 122, 123, 124, 125]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 2.6
add_heading2("2.6. Σύνοψη Κεφαλαίου")
for idx in [127, 128]:
    t = clean(par(idx))
    if t:
        add_body(t)

# ===========================================================================
# CHAPTER 3 — ΘΕΩΡΗΤΙΚΟ ΠΛΑΙΣΙΟ
# ===========================================================================
page_break()
add_heading1("3. Θεωρητικό Πλαίσιο")

# 3.1
add_heading2("3.1. Χωρικά Ευρετήρια — Αλγοριθμική Ανάλυση")

add_heading3("3.1.1. Linear Scan — Πολυπλοκότητα O(n)")
for idx in [132, 133, 134, 135]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading3("3.1.2. R-Tree — Πολυπλοκότητα O(log n + k)")
for idx in [139, 140, 141, 142, 143, 144, 145]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading3("3.1.3. PostGIS και GiST Ευρετήρια")
for idx in [147, 148]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_body("Στην πράξη, η δημιουργία δείκτη πραγματοποιείται με εντολή της μορφής:", first_indent=False)
add_code_block("CREATE INDEX idx_screens_location\nON screens\nUSING GIST(location);")

for idx in [155, 156]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_body("Στο GEO-ADS, ένα τυπικό query έχει τη μορφή:", first_indent=False)
add_code_block("ST_DWithin(\n  location,\n  ST_MakePoint(lon, lat)::geography,\n  radius_meters\n)")

t166 = clean(par(166))
if t166:
    add_body(t166)

add_heading3("3.1.4. Κατανεμημένη Χωρική Ευρετηρίαση")
for idx in [169, 170, 171, 172, 173]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading3("3.1.5. Σύγκριση Μεθόδων")
for idx in [177, 178, 179, 180, 181]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 3.2
add_heading2("3.2. WebSocket Protocol")
for idx in [185, 186, 187, 188, 189, 190]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 3.3
add_heading2("3.3. JWT και HMAC")
for idx in [194, 195, 196, 197, 198]:
    t = clean(par(idx))
    if t:
        add_body(t)

# 3.4
add_heading2("3.4. Ανίχνευση Απειλών — Z-score & Sliding Windows")
add_body(clean(par(202)))
add_body(
    "z = (rate - mean) / std",
    first_indent=False
)
for idx in [204, 205, 206, 207, 208]:
    t = clean(par(idx))
    if t:
        add_body(t)

# ===========================================================================
# CHAPTER 4 — ΣΧΕΔΙΑΣΜΟΣ ΣΥΣΤΗΜΑΤΟΣ
# ===========================================================================
page_break()
add_heading1("4. Σχεδιασμός Συστήματος")
add_body("Στο κεφάλαιο αυτό παρουσιάζεται ο συνολικός σχεδιασμός του συστήματος GEO-ADS.")

add_heading2("4.1. Αρχιτεκτονική Συστήματος")
for idx in [211, 212, 213, 214, 215, 216, 217]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("4.2. Ζώνες Γηπέδου και Μοντέλο Οθονών")
for idx in [221, 222, 223, 224, 225]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_code_block("screens(id, zone_id FK→zones, row_idx, col_idx, screen_type, location GEOGRAPHY(Point,4326))")

for idx in [227, 228, 229]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_code_block("CREATE INDEX idx_screens_location ON screens USING GIST(location);")

t231 = clean(par(231))
if t231:
    add_body(t231)

add_heading2("4.3. Σχεδιασμός Βάσης Δεδομένων")
for idx in [235, 236]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_code_block("advertisements(id SERIAL PK, name VARCHAR, image_url TEXT, zone VARCHAR, created_at TIMESTAMP)")

for idx in [238, 239]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_code_block("zones(id SERIAL PK, name VARCHAR, type VARCHAR)")

for idx in [241, 242]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_code_block("screens(id SERIAL PK, zone_id FK, row_idx INT, col_idx INT, screen_type VARCHAR, location GEOGRAPHY)")

for idx in [244, 245, 246]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("4.4. Σχεδιασμός Real-time Επικοινωνίας")
for idx in [250, 251, 252, 253, 254, 255]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("4.5. Σχεδιασμός Ασφάλειας")
for idx in [259, 260, 261, 262, 263, 264, 265, 266]:
    t = clean(par(idx))
    if t:
        add_body(t)

# ===========================================================================
# CHAPTER 5 — ΥΛΟΠΟΙΗΣΗ ΣΥΣΤΗΜΑΤΟΣ
# ===========================================================================
page_break()
add_heading1("5. Υλοποίηση Συστήματος")
add_body("Στο κεφάλαιο αυτό παρουσιάζεται η υλοποίηση του συστήματος GEO-ADS.")

add_heading2("5.1. Εργαλεία και Αιτιολόγηση Επιλογών")
for idx in [271, 272, 273, 274, 275, 276, 277]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("5.2. Backend — REST API και WebSocket Handlers")
for idx in [281, 282, 283, 284, 285, 286]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_code_block(
    "@app.get(\"/recommendations\")\nasync def get_recommendations(\n"
    "    lat: float = Query(..., ge=-90, le=90),\n"
    "    lon: float = Query(..., ge=-180, le=180),\n"
    "    radius: float = Query(100.0, ge=1, le=50000),\n"
    "    current_user: dict = Depends(require_scope(\"recommendation:read\"))\n"
    "):\n"
    "    results = layout_service.find_screens_rtree(lat, lon, radius)\n"
    "    return {\"screens\": results, \"count\": len(results)}"
)

for idx in [296, 297, 298]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("5.3. Spatial Indexing — Υλοποίηση 4 Μεθόδων")
for idx in [302, 303, 304]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_code_block(
    "# R-Tree query\ndef find_screens_rtree(self, lat, lon, radius_m):\n"
    "    bbox = self._expand_bbox(lat, lon, radius_m)\n"
    "    candidates = list(self.rtree_idx.intersection(bbox, objects=True))\n"
    "    return [s for s in candidates\n"
    "            if haversine(lat, lon, s.object['lat'], s.object['lon']) <= radius_m]"
)

for idx in [311, 312, 313, 314]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("5.4. Recommendation Engine")
for idx in [318, 319, 320, 321, 322]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("5.5. Frontend — VisualBoard και SecurityDashboard")
for idx in [326, 327, 328, 329, 330, 331, 332]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("5.6. Desktop Εφαρμογή με Electron")
for idx in [336, 337]:
    t = clean(par(idx))
    if t:
        add_body(t)

add_heading2("5.7. Σύστημα Ασφάλειας")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 5.7]", first_indent=False)

# ===========================================================================
# CHAPTER 6 — ΠΕΙΡΑΜΑΤΑ & ΑΞΙΟΛΟΓΗΣΗ
# ===========================================================================
page_break()
add_heading1("6. Πειράματα & Αξιολόγηση")
add_body("Στο κεφάλαιο αυτό παρουσιάζονται τα πειράματα και η αξιολόγηση του συστήματος GEO-ADS.")

add_heading2("6.1. Μεθοδολογία Πειραμάτων")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 6.1]", first_indent=False)

add_heading2("6.2. Πείραμα 1 — Χωρική Ευρετηρίαση (ΕΡ-2)")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 6.2]", first_indent=False)

add_heading2("6.3. Πείραμα 2 — Ανίχνευση Απειλών (ΕΡ-9)")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 6.3]", first_indent=False)

add_heading2("6.4. Συζήτηση Αποτελεσμάτων")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 6.4]", first_indent=False)

# ===========================================================================
# CHAPTER 7 — ΣΥΜΠΕΡΑΣΜΑΤΑ & ΜΕΛΛΟΝΤΙΚΕΣ ΠΡΟΕΚΤΑΣΕΙΣ
# ===========================================================================
page_break()
add_heading1("7. Συμπεράσματα & Μελλοντικές Προεκτάσεις")
add_body("Στο κεφάλαιο αυτό παρουσιάζονται τα συμπεράσματα της εργασίας.")

add_heading2("7.1. Ανακεφαλαίωση")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 7.1]", first_indent=False)

add_heading2("7.2. Απαντήσεις στις Ερευνητικές Ερωτήσεις")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 7.2]", first_indent=False)

add_heading2("7.3. Περιορισμοί")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 7.3]", first_indent=False)

add_heading2("7.4. Μελλοντικές Προεκτάσεις")
add_body("[ΣΥΜΠΛΗΡΩΣΕ — PROMPT 7.4]", first_indent=False)

# ===========================================================================
# BIBLIOGRAPHY
# ===========================================================================
page_break()
add_heading1("Βιβλιογραφία")
add_body(
    "Οι παρακάτω βιβλιογραφικές αναφορές αναφέρονται στο κείμενο με τον αντίστοιχο αριθμό σε αγκύλες."
)
add_blank()

bib_entries = [
    "[1] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 1 [1]]",
    "[2] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 1 [2]]",
    "[3] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 1 [3]]",
    "[4] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 2 [4]]",
    "[5] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 2 [5]]",
    "[6] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 2 [6]]",
    "[7] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 2 [7]]",
    "[8] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 2 [8]]",
    "[9] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 2 [9]]",
    "[10] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 3 [10]]",
    "[11] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 3 [11]]",
    "[12] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 3 [12]]",
    "[13] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 4 [13]]",
    "[14] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 4 [14]]",
    "[15] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 5 [15]]",
    "[16] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 5 [16]]",
    "[17] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 5 [17]]",
    "[18] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 6 [18]]",
    "[19] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 6 [19]]",
    "[20] [ΣΥΜΠΛΗΡΩΣΕ — Βιβλιογραφική αναφορά Κεφ. 7 [20]]",
]
for entry in bib_entries:
    add_body(entry, first_indent=False)

# ===========================================================================
# Save
# ===========================================================================
OUT = "C:/Projects/MIKE_DIPLOMA/docs/DIPLOMA_MIKE_FORMATTED.docx"
doc.save(OUT)
print(f"Saved: {OUT}")

import os
size = os.path.getsize(OUT)
print(f"File size: {size:,} bytes ({size/1024:.1f} KB)")
