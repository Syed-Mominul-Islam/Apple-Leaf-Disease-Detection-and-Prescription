import os
import re
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls

# 1. Setup paths
base_dir = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\source-code"
paper_doc_path = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\paper.docx"

doc = docx.Document(paper_doc_path)

# Helper function to delete a paragraph safely
def delete_paragraph(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    paragraph._p = paragraph._element = None

# Helper function to delete a table safely
def delete_table(table):
    tbl = table._tbl
    tbl.getparent().remove(tbl)

# Helper function to insert a paragraph after another paragraph
def insert_paragraph_after(paragraph, text="", style=None):
    new_p = OxmlElement('w:p')
    paragraph._p.addnext(new_p)
    new_para = docx.text.paragraph.Paragraph(new_p, paragraph._parent)
    if text:
        new_para.text = text
    if style:
        new_para.style = style
    return new_para

# Helper function to format tables in professional booktabs / APA style
def format_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblBorders = parse_xml(
        r'<w:tblBorders %s>'
        r'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        r'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        r'<w:left w:val="none"/>'
        r'<w:right w:val="none"/>'
        r'<w:insideH w:val="none"/>'
        r'<w:insideV w:val="none"/>'
        r'</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(tblBorders)
    
    # Header bottom border
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(r'<w:tcBorders %s><w:bottom w:val="single" w:sz="8" w:color="000000"/></w:tcBorders>' % nsdecls('w'))
        tcPr.append(tcBorders)

# Helper function to add a professional centered equation table
def add_equation_table(after_para, eq_text, eq_num):
    table = doc.add_table(rows=1, cols=2)
    after_para._p.addnext(table._tbl)
    
    row = table.rows[0]
    row.cells[0].width = Inches(5.5)
    row.cells[1].width = Inches(1.0)
    
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        r'<w:tblBorders %s>'
        r'<w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        r'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        r'</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(tblBorders)
    
    p1 = row.cells[0].paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = p1.add_run(eq_text)
    run1.font.italic = True
    run1.font.name = 'Times New Roman'
    run1.font.size = Pt(12)
    
    p2 = row.cells[1].paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run2 = p2.add_run(eq_num)
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(12)
    
    spacing_p = OxmlElement('w:p')
    table._tbl.addnext(spacing_p)
    return docx.text.paragraph.Paragraph(spacing_p, after_para._parent)

# Helper function to add comparison table
def add_comparison_table(after_para, table_data):
    table = doc.add_table(rows=0, cols=5)
    after_para._p.addnext(table._tbl)
    
    headers = ["Reference", "Dataset & Size", "Classes", "Model", "Accuracy (%)"]
    row = table.add_row()
    for col_idx, text in enumerate(headers):
        row.cells[col_idx].text = text
        p = row.cells[col_idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.bold = True
        p.runs[0].font.name = 'Times New Roman'
        
    for ref, dataset, classes, model_name, acc in table_data:
        row = table.add_row()
        row.cells[0].text = ref
        row.cells[1].text = dataset
        row.cells[2].text = classes
        row.cells[3].text = model_name
        row.cells[4].text = acc
        
        is_proposed = "Ours" in ref or "AppleNetV1" in model_name or "proposed" in ref.lower()
        for col_idx, cell in enumerate(row.cells):
            p = cell.paragraphs[0]
            if col_idx > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if p.runs:
                p.runs[0].font.name = 'Times New Roman'
                if is_proposed:
                    p.runs[0].font.bold = True
                    
    format_table_borders(table)
    
    spacing_p = OxmlElement('w:p')
    table._tbl.addnext(spacing_p)
    return docx.text.paragraph.Paragraph(spacing_p, after_para._parent)

def find_paragraph_idx(text, is_prefix=False):
    for idx, p in enumerate(doc.paragraphs):
        p_text = p.text.strip()
        if is_prefix:
            if p_text.startswith(text):
                return idx
        else:
            if p_text == text:
                return idx
    return None

# --- PHASE 1: CITATION CORRECTIONS & RESOLVING OVERLAPS ---
print("Phase 1: Resolving citation overlaps and typos...")

# 1. Update Section 1 Introduction (Replace overlaps)
p_intro_idx = find_paragraph_idx("1. Introduction :Referrence sequence maintain")
if p_intro_idx is not None:
    doc.paragraphs[p_intro_idx].text = "1. Introduction"

# Find body paragraphs in Section 1 and perform specific replacements
for idx in range(p_intro_idx + 1, find_paragraph_idx("2. Related Works")):
    p = doc.paragraphs[idx]
    # Replace [20, 27] with [1, 2]
    if "[20, 27]" in p.text:
        p.text = p.text.replace("[20, 27]", "[1, 2]")
    # Replace [30, 34] with [8, 9] (Bottleneck citations)
    if "[30, 34]" in p.text:
        p.text = p.text.replace("[30, 34]", "[8, 9]")

# Replace Sladojevic et al. [10] with Sladojevic et al. [17] in Section 2 body paragraphs
p_related_idx = find_paragraph_idx("2. Related Works")
p_methodology_idx = find_paragraph_idx("3. Methodology: diagram draw korte hobe")
if p_related_idx is not None and p_methodology_idx is not None:
    for idx in range(p_related_idx + 1, p_methodology_idx):
        p = doc.paragraphs[idx]
        if "Sladojevic et al. [10]" in p.text:
            p.text = p.text.replace("Sladojevic et al. [10]", "Sladojevic et al. [17]")

# 2. Update Section 2 (Related Works) Table & Paragraph citation corrections
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            # Replace [5] with [19] for Jiang et al.
            if "[5]" in cell.text:
                cell.text = cell.text.replace("[5]", "[19]")
            # Replace [7] with [16] for Mohanty et al.
            if "[7]" in cell.text:
                cell.text = cell.text.replace("[7]", "[16]")
            # Replace [10] with [17] for Sladojevic et al.
            if "[10]" in cell.text:
                cell.text = cell.text.replace("[10]", "[17]")
            # Replace [28] with [25] for Howard et al.
            if "[28]" in cell.text:
                cell.text = cell.text.replace("[28]", "[25]")

# 3. Create Comparison Table in Section 6
print("Inserting new comparison table in Section 6...")
p_comp_intro_idx = find_paragraph_idx("To benchmark the performance of the proposed AppleNetV1 model, we conduct a comprehensive comparative analysis against leading studies in the existing literature. The comparisons are based on dataset size, number of target classes, models evaluated, and final test accuracy, as detailed in Table 5.")
if p_comp_intro_idx is not None:
    p_comp_intro = doc.paragraphs[p_comp_intro_idx]
    table_data = [
        ("Mohanty et al. [16]", "PlantVillage (38,597)", "14 crop classes", "GoogLeNet", "99.35%"),
        ("Sladojevic et al. [17]", "Internet (4,483)", "15 plant classes", "Custom CNN", "96.30%"),
        ("Liu et al. [18]", "Apple leaf (13,689)", "4 apple classes", "Improved AlexNet", "97.62%"),
        ("Jiang et al. [19]", "Apple leaf (2,637)", "5 apple classes", "IN-ResNet", "94.65%"),
        ("Zhong & Zhao [20]", "PlantVillage (~2,000)", "4 apple classes", "DenseNet121", "93.71%"),
        ("Bi & Wang [21]", "PlantVillage (~2,000)", "4 apple classes", "ResNet50", "97.80%"),
        ("Yan et al. [22]", "PlantVillage (~2,000)", "4 apple classes", "Improved ResNet50", "96.55%"),
        ("Chen et al. [23]", "PlantVillage (~2,000)", "Multi-crop classes", "VGG19 Transfer", "98.24%"),
        ("Albahli et al. [24]", "Custom+PV (~2,000)", "Multi-class leaves", "DenseNet-based", "98.70%"),
        ("Howard et al. [25]", "ImageNet", "Mobile tasks", "MobileNetV1", "High efficiency"),
        ("Proposed AppleNetV1 (Ours)", "Merged Dataset (13,470)", "7 classes (6 apple + 1 background)", "Custom CNN", "99.33%")
    ]
    p_comp_tbl = add_comparison_table(p_comp_intro, table_data)
    
    # Add caption
    p_comp_cap_xml = OxmlElement('w:p')
    p_comp_tbl._p.addnext(p_comp_cap_xml)
    p_comp_cap = docx.text.paragraph.Paragraph(p_comp_cap_xml, p_comp_tbl._parent)
    p_comp_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_comp_tbl = p_comp_cap.add_run("Table 5: Comparison of proposed AppleNetV1 with existing studies in the literature.")
    run_comp_tbl.font.name = 'Times New Roman'
    run_comp_tbl.font.size = Pt(11)
    run_comp_tbl.font.bold = True

# --- PHASE 2: CITATION TRACING AND RE-SEQUENCING ---
print("Phase 2: Scanning citations in text order...")
p_ref_idx = find_paragraph_idx("References")
ref_pattern = re.compile(r'^\[(\d+)\]\s*(.*)$')

orig_references = {}
for i in range(p_ref_idx + 1, len(doc.paragraphs)):
    p_text = doc.paragraphs[i].text.strip()
    match = ref_pattern.match(p_text)
    if match:
        ref_num = int(match.group(1))
        orig_references[ref_num] = match.group(2)

print(f"Loaded {len(orig_references)} original references from bibliography.")

citation_seq = []
seen = set()

def scan_text_for_citations(text):
    for match in re.finditer(r'\[([0-9,\s\-]+)\]', text):
        content = match.group(1)
        parts = re.split(r'[\s,]+', content)
        for p in parts:
            p_clean = p.strip()
            if p_clean:
                if "." in p_clean:
                    continue
                try:
                    num = int(p_clean)
                    if 1 <= num <= 48:
                        if num not in seen:
                            seen.add(num)
                            citation_seq.append(num)
                except ValueError:
                    pass

# Scan paragraphs from Introduction to end (excluding final references section)
for idx in range(p_intro_idx, p_ref_idx):
    if idx == 12: # Skip contributions bullet points if needed
        continue
    scan_text_for_citations(doc.paragraphs[idx].text)

# Scan tables
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            scan_text_for_citations(cell.text)

print(f"Traced citation sequence: {citation_seq}")

# Create ref_map: orig_number -> new_number
ref_map = {orig_num: new_num for new_num, orig_num in enumerate(citation_seq, 1)}

# Helper functions for reference substitution
def replace_citations_text(text, r_map):
    def subst(match):
        content = match.group(1)
        if "." in content:
            return match.group(0)
        parts = re.split(r'[\s,]+', content)
        new_parts = []
        for p in parts:
            p_clean = p.strip()
            if p_clean:
                try:
                    num = int(p_clean)
                    if num in r_map:
                        new_parts.append(str(r_map[num]))
                except ValueError:
                    pass
        if new_parts:
            new_parts = sorted(list(set(int(x) for x in new_parts)))
            return "[" + ", ".join(str(x) for x in new_parts) + "]"
        return match.group(0)
    
    return re.sub(r'\[([0-9,\s\-]+)\]', subst, text)

# Substitute all body paragraphs citation numbers
for idx in range(p_intro_idx, p_ref_idx):
    doc.paragraphs[idx].text = replace_citations_text(doc.paragraphs[idx].text, ref_map)

# Substitute table cell citations
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            cell.text = replace_citations_text(cell.text, ref_map)

# --- PHASE 3: FILL COMPARATIVE MODEL DESCRIPTIONS ---
print("Phase 3: Adding comparative model descriptions...")
p_comp_models_idx = find_paragraph_idx("3.5. Comparative Deep Learning Architectures")
p_placeholder_idx = p_comp_models_idx + 1

# Delete placeholder paragraph
delete_paragraph(doc.paragraphs[p_placeholder_idx])

# Add models with equations
# VGG-16
p_vgg = insert_paragraph_after(
    doc.paragraphs[p_comp_models_idx],
    "1. VGG-16: VGG-16 is a simple and widely used convolutional neural network architecture. "
    "It features a sequential structure utilizing very small (3x3) convolutional filters with a stride of 1, "
    "max-pooling layers, and three fully connected layers at the classification head."
)
p_vgg_eq = add_equation_table(
    p_vgg,
    "y(i, j) = \\sum_{m} \\sum_{n} x(i-m, j-n) \\cdot w(m, n) + b",
    "(5)"
)

# ResNet50
p_resnet = insert_paragraph_after(
    p_vgg_eq,
    "2. ResNet50: ResNet50 (Residual Network) introduces residual skip connections that bypass one or more layers. "
    "This design mitigates the vanishing gradient problem, allowing the training of extremely deep neural networks."
)
p_resnet_eq = add_equation_table(
    p_resnet,
    "H(x) = F(x) + x",
    "(6)"
)

# MobileNetV2
p_mobilenet = insert_paragraph_after(
    p_resnet_eq,
    "3. MobileNetV2: MobileNetV2 is an optimized lightweight architecture designed for resource-constrained edge devices. "
    "It implements depthwise separable convolutions and inverted residual blocks with linear bottlenecks."
)
p_mobilenet_eq1 = add_equation_table(
    p_mobilenet,
    "Conv_{depthwise}(W, X)_{(i,j)} = \\sum_{m,n} W_{(m,n)} \\cdot X_{(i-m, j-n)}",
    "(7)"
)
p_mobilenet_eq2 = add_equation_table(
    p_mobilenet_eq1,
    "Conv_{pointwise}(V, Y)_{(i,j)} = \\sum_{k} V_{k} \\cdot Y_{(i,j,k)}",
    "(8)"
)

# EfficientNetB0
p_efficientnet = insert_paragraph_after(
    p_mobilenet_eq2,
    "4. EfficientNetB0: EfficientNetB0 introduces a compound scaling method that uniformly scales depth, width, "
    "and resolution dimensions using a fixed compound scaling factor, achieving optimal parameter efficiency."
)
p_efficientnet_eq = add_equation_table(
    p_efficientnet,
    "d = \\alpha^\\phi, \\quad w = \\beta^\\phi, \\quad r = \\gamma^\\phi \\quad \\text{s.t. } \\alpha \\cdot \\beta^2 \\cdot \\gamma^2 \\approx 2",
    "(9)"
)

# DenseNet121
p_densenet = insert_paragraph_after(
    p_efficientnet_eq,
    "5. DenseNet121: DenseNet121 connects every layer to every other layer in a dense block in a feed-forward manner. "
    "This enhances feature reuse, improves gradient flow, and reduces the overall parameter footprint."
)
p_densenet_eq = add_equation_table(
    p_densenet,
    "x_l = H_l([x_0, x_1, \\dots, x_{l-1}])",
    "(10)"
)

# AppleNetV1 (Ours)
p_applenet = insert_paragraph_after(
    p_densenet_eq,
    "6. AppleNetV1 (Ours): AppleNetV1 is a custom-designed, optimized sequential CNN architecture containing four "
    "convolutional blocks with filter sizes of 32, 64, 128, and 256. Each block uses Batch Normalization, ReLU6, "
    "and Max Pooling, leading to a lightweight classification head with a dropout rate of 0.5."
)
p_applenet_eq = add_equation_table(
    p_applenet,
    "X_{i+1} = \\text{ReLU6}(\\text{BN}(\\text{Conv2D}(X_i; W_i, b_i)))",
    "(11)"
)

# --- PHASE 4: FILL METRICS TABLE ---
print("Phase 4: Filling performance metrics table...")
table_filled = False
for table in doc.tables:
    if len(table.rows) > 0 and table.rows[0].cells[0].text.strip() == "Models" and table.rows[0].cells[1].text.strip() == "Accuracy":
        metrics = [
            ('MobileNetV2', '99.26%', '0.9928', '0.9926', '0.9927'),
            ('ResNet50', '99.78%', '0.9979', '0.9979', '0.9979'),
            ('DenseNet121', '99.41%', '0.9944', '0.9942', '0.9943'),
            ('EfficientNetB0', '99.70%', '0.9972', '0.9971', '0.9971'),
            ('AppleNetV1 (Ours)', '99.33%', '0.9937', '0.9935', '0.9935')
        ]
        # Re-set table cells
        for r_idx, data in enumerate(metrics, 1):
            for c_idx, val in enumerate(data):
                table.rows[r_idx].cells[c_idx].text = val
                p = table.rows[r_idx].cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
                run = p.runs[0] if p.runs else p.add_run()
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)
                if r_idx == 5:
                    run.font.bold = True
        format_table_borders(table)
        table_filled = True
        break

if table_filled:
    print("Successfully populated performance metrics Table.")
else:
    print("WARNING: Metrics table not found or failed to fill.")

# --- PHASE 4.5: DELETE OLD SPLIT COMPARISON TABLES ---
print("Phase 4.5: Deleting old comparison tables to avoid duplicates...")
tables_to_delete = []
for table in doc.tables:
    if len(table.rows) > 0:
        first_cell = table.rows[0].cells[0].text.strip()
        if (first_cell == "Reference" and table.rows[0].cells[4].text.strip() == "Accuracy (%)" and len(table.rows) < 10) or \
           first_cell.startswith("Sladojevic et al.") or \
           first_cell.startswith("Liu et al.") or \
           first_cell.startswith("Zhong & Zhao") or \
           first_cell.startswith("Yan et al.") or \
           first_cell.startswith("Proposed") or \
           first_cell.startswith("(Ours)"):
            tables_to_delete.append(table)

for t in tables_to_delete:
    delete_table(t)
print(f"Successfully deleted {len(tables_to_delete)} old comparison tables.")

# --- PHASE 5: CORRECT BENGALI TEXT & FONT BOXES ---
print("Phase 5: Fixing Bengali text font box errors...")
# Locate the paragraph under Section 3.5 or Section 5 and replace boxes
target_phrase = "The prescription includes the disease name"
for p in doc.paragraphs:
    if target_phrase in p.text:
        # Replace the entire text with correct Bengali terms
        p.text = (
            "To bridge the gap between complex deep learning models and practical agricultural utility, "
            "a web-based decision support system was developed and deployed using the Streamlit framework. "
            "The application provides an intuitive graphical user interface (GUI) designed for farmers and "
            "extension workers. Users can upload leaf images directly through the web interface, which are then "
            "preprocessed and classified in real-time. Figure 10 displays the application interface under various "
            "prediction scenarios, showing the diagnostic outputs for all seven classes (Alternaria, Apple Mosaic, "
            "Apple Scab, Black Rot, Cedar Apple Rust, Healthy, and Not Apple Leaf). To maximize accessibility for "
            "rural farmers in Bangladesh, the application features a localized Bengali prescription system. Upon "
            "predicting a disease, the system automatically translates the diagnosis and prints a detailed "
            "prescription in Bengali. The prescription includes the disease name (রোগের নাম), symptoms (লক্ষণসমূহ), "
            "biological control (জৈবিক দমন), and chemical control (রাসায়নিক দমন). For instance, when an image with "
            "Apple Scab is uploaded, the model outputs the prediction with high confidence, and the interface "
            "displays the corresponding Bengali treatment guidelines (e.g., spraying Mancozeb or Tebuconazole "
            "fungicides). If a non-apple leaf or background image is uploaded, the application correctly identifies "
            "it as 'Not Apple Leaf' and prompts the user to upload a valid apple leaf image, preventing false alarms."
        )
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
        print("Fixed Bengali font boxes in paragraph text.")

# --- PHASE 6: REBUILD BIBLIOGRAPHY ---
print("Phase 6: Rebuilding sequential bibliography at end...")
p_ref_idx = find_paragraph_idx("References")

# Clear references section
for idx in range(p_ref_idx + 1, len(doc.paragraphs)):
    doc.paragraphs[idx].text = ""

# Write references in order of appearance
for idx, orig_num in enumerate(citation_seq):
    new_num = idx + 1
    detail = orig_references[orig_num]
    doc.paragraphs[p_ref_idx + 1 + idx].text = f"[{new_num}] {detail}"
    doc.paragraphs[p_ref_idx + 1 + idx].runs[0].font.name = 'Times New Roman'
    doc.paragraphs[p_ref_idx + 1 + idx].runs[0].font.size = Pt(11)

# Delete leftover empty reference paragraphs
paragraphs_to_delete = []
for idx in range(p_ref_idx + 1 + len(citation_seq), len(doc.paragraphs)):
    paragraphs_to_delete.append(doc.paragraphs[idx])

for p in paragraphs_to_delete:
    delete_paragraph(p)

print("Bibliography rebuilt successfully.")

# Save modified paper.docx
doc.save(paper_doc_path)
print(f"\nSUCCESS: Updated paper document successfully saved to: {paper_doc_path}")
