import os
import re
import shutil
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls

# 1. Setup paths
base_dir = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\source-code"
images_dir = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\images"
orig_doc_path = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\New-journal-formet-v2.docx"
backup_path = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\New-journal-formet-v2_Backup.docx"
output_doc_path = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\New-journal-formet-v2_Updated.docx"

# Make backup copy of original file
shutil.copyfile(orig_doc_path, backup_path)
print(f"Created backup of original paper at: {backup_path}")

doc = docx.Document(orig_doc_path)

# Helper function to delete a paragraph safely
def delete_paragraph(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    paragraph._p = paragraph._element = None

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

# Helper function to center align and replace image in a paragraph
def replace_image(p, img_path, width_inches):
    p.text = "" # Clears existing runs and drawing elements
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(img_path, width=Inches(width_inches))

# Helper function to insert an image with caption
def add_figure(after_para, img_path, caption_text, width_inches=5.0):
    # Image paragraph
    img_p_xml = OxmlElement('w:p')
    after_para._p.addnext(img_p_xml)
    img_p = docx.text.paragraph.Paragraph(img_p_xml, after_para._parent)
    img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_p.add_run()
    run.add_picture(img_path, width=Inches(width_inches))
    
    # Caption paragraph
    cap_p_xml = OxmlElement('w:p')
    img_p_xml.addnext(cap_p_xml)
    cap_p = docx.text.paragraph.Paragraph(cap_p_xml, after_para._parent)
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cap = cap_p.add_run(caption_text)
    run_cap.font.name = 'Times New Roman'
    run_cap.font.size = Pt(11)
    run_cap.font.bold = True
    
    # Spacer paragraph
    space_p_xml = OxmlElement('w:p')
    cap_p_xml.addnext(space_p_xml)
    space_p = docx.text.paragraph.Paragraph(space_p_xml, after_para._parent)
    return space_p

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
    tbl = OxmlElement('w:tbl')
    after_para._p.addnext(tbl)
    table = docx.table.Table(tbl, after_para._parent)
    
    row = table.add_row()
    # 2 columns: left is centered equation, right is right-aligned equation number
    row.cells[0].width = Inches(5.5)
    row.cells[1].width = Inches(1.0)
    
    # Borderless
    tblPr = tbl.tblPr
    tblBorders = parse_xml(
        r'<w:tblBorders %s>'
        r'<w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        r'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        r'</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(tblBorders)
    
    # Cell 1: Centered equation text
    p1 = row.cells[0].paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = p1.add_run(eq_text)
    run1.font.italic = True
    run1.font.name = 'Times New Roman'
    run1.font.size = Pt(12)
    
    # Cell 2: Right-aligned equation number
    p2 = row.cells[1].paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run2 = p2.add_run(eq_num)
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(12)
    
    spacing_p = OxmlElement('w:p')
    tbl.addnext(spacing_p)
    return docx.text.paragraph.Paragraph(spacing_p, after_para._parent)

# Helper function to add the 10-fold cross-validation table
def add_cross_val_table(after_para, cv_data):
    tbl = OxmlElement('w:tbl')
    after_para._p.addnext(tbl)
    table = docx.table.Table(tbl, after_para._parent)
    
    # Header row
    headers = ["Fold", "Accuracy (%)", "Precision", "Recall", "F1-Score"]
    row = table.add_row()
    for col_idx, text in enumerate(headers):
        row.cells[col_idx].text = text
        p = row.cells[col_idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.bold = True
        p.runs[0].font.name = 'Times New Roman'
        
    # Data rows
    for fold, acc, prec, rec, f1 in cv_data:
        row = table.add_row()
        if isinstance(fold, str):
            row.cells[0].text = fold
            row.cells[0].paragraphs[0].runs[0].font.bold = True
        else:
            row.cells[0].text = f"Fold {fold}"
            
        row.cells[1].text = f"{acc:.2f}%"
        row.cells[2].text = f"{prec:.4f}"
        row.cells[3].text = f"{rec:.4f}"
        row.cells[4].text = f"{f1:.4f}"
        
        # Bold formatting for Mean and Std
        if isinstance(fold, str):
            for cell in row.cells:
                p = cell.paragraphs[0]
                if p.runs:
                    p.runs[0].font.bold = True
                    
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.paragraphs[0].runs[0].font.name = 'Times New Roman'
            
    format_table_borders(table)
    
    spacing_p = OxmlElement('w:p')
    tbl.addnext(spacing_p)
    return docx.text.paragraph.Paragraph(spacing_p, after_para._parent)

# Helper function to add the comparison table in Section 6
def add_comparison_table(after_para, table_data):
    tbl = OxmlElement('w:tbl')
    after_para._p.addnext(tbl)
    table = docx.table.Table(tbl, after_para._parent)
    
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
        
        # Bold formatting for proposed model row (ours)
        is_proposed = "Ours" in ref or "AppleNetV1" in model_name or "proposed" in ref.lower()
        for col_idx, cell in enumerate(row.cells):
            p = cell.paragraphs[0]
            # Center alignment except for first column
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
    tbl.addnext(spacing_p)
    return docx.text.paragraph.Paragraph(spacing_p, after_para._parent)

# --- PHASE 1: TRACING CITATIONS AND PREPARING MAP ---
ref_pattern = re.compile(r'^\[(\d+)\]\s*(.*)$')
orig_references = {}
for i in range(67, 115):
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
                    if num == 0 or num == 255:
                        continue
                    if 1 <= num <= 48:
                        if num not in seen:
                            seen.add(num)
                            citation_seq.append(num)
                except ValueError:
                    pass

# Scan paragraphs 5 to 65 (Introduction to Discussion), skipping Abstract & Contributions list
for idx in range(5, 66):
    if idx == 12: # Skip contributions bullet points
        continue
    scan_text_for_citations(doc.paragraphs[idx].text)

# Scan tables
for idx, table in enumerate(doc.tables):
    for row in table.rows:
        for cell in row.cells:
            scan_text_for_citations(cell.text)

print(f"Traced {len(citation_seq)} cited references. Citation sequence: {citation_seq}")

# Create ref_map: orig_number -> new_number
ref_map = {orig_num: new_num for new_num, orig_num in enumerate(citation_seq, 1)}

# Helper function to substitute references inside text
def replace_citations_text(text, r_map):
    def subst(match):
        content = match.group(1)
        if "255" in content or "." in content or "0" in content:
            return match.group(0)
        parts = re.split(r'[\s,]+', content)
        new_parts = []
        for p in parts:
            p_clean = p.strip()
            if p_clean:
                try:
                    num = int(p_clean)
                    if 1 <= num <= 48:
                        if num in r_map:
                            new_parts.append(str(r_map[num]))
                except ValueError:
                    pass
        if new_parts:
            new_parts = sorted(list(set(int(x) for x in new_parts)))
            return "[" + ", ".join(str(x) for x in new_parts) + "]"
        return match.group(0)
    
    return re.sub(r'\[([0-9,\s\-]+)\]', subst, text)

# Helper function to strip citations entirely (for Abstract and Contributions)
def strip_citations(text):
    def subst(match):
        content = match.group(1)
        if "255" in content or "." in content or "0" in content:
            return match.group(0)
        return ""
    cleaned = re.sub(r'\s*\[([0-9,\s\-]+)\]', subst, text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s+([.,])', r'\1', cleaned)
    return cleaned.strip()

# --- PHASE 2: PROCESSING TEXT & BIBLIOGRAPHY UPDATES ---

# 1. Clean Abstract
print("Cleaning Abstract...")
doc.paragraphs[3].text = strip_citations(doc.paragraphs[3].text)

# 2. Clean Contributions
print("Cleaning Main Contributions section...")
contrib_lines = doc.paragraphs[12].text.split("\n")
cleaned_contrib = [strip_citations(line) for line in contrib_lines]
doc.paragraphs[12].text = "\n".join(cleaned_contrib)

# 3. Update all other body paragraph references (excluding references section)
print("Updating citation numbers in body paragraphs...")
for idx in range(5, 66):
    if idx == 12:
        continue
    doc.paragraphs[idx].text = replace_citations_text(doc.paragraphs[idx].text, ref_map)

# 4. Update and Sort Table 1 (Related Literature)
print("Sorting Related Literature table and updating cells...")
lit_table = doc.tables[0]
rows_data = []
for row in lit_table.rows[1:]:
    cell_texts = [cell.text for cell in row.cells]
    match = re.search(r'\[(\d+)\]', cell_texts[0])
    if match:
        orig_num = int(match.group(1))
        new_num = ref_map.get(orig_num, 999)
    else:
        new_num = 999
    rows_data.append((new_num, cell_texts))

rows_data.sort(key=lambda x: x[0])

for idx, (new_num, cell_texts) in enumerate(rows_data, 1):
    row = lit_table.rows[idx]
    for col_idx, text in enumerate(cell_texts):
        row.cells[col_idx].text = replace_citations_text(text, ref_map)
format_table_borders(lit_table)

# 5. Sort Related Works paragraph text discussion (Paragraph 17)
print("Sorting Related Works text discussion (Paragraph 17)...")
studies = {
    1: "Albahli et al. [1] used a DenseNet-based model for multi-class plant disease classification. They achieved an overall accuracy of 98.70%. The major limitation of their work was the high computational overhead during training due to dense layer concatenations.",
    4: "Bi and Wang [4] analyzed the performance of ResNet50 for identifying apple diseases. The architecture obtained a classification accuracy of 97.80%. Despite the good results, the heavy model size and parameter count limited its applicability for edge computing.",
    5: "Chen et al. [5] proposed using a VGG19-based transfer learning framework for crop disease detection. They achieved a high accuracy of 98.24%. The main drawback of this model is its massive file size (~500MB), which prevents local smartphone deployment.",
    6: "Howard et al. [6] introduced the MobileNet architecture utilizing depthwise separable convolutions to build lightweight networks. They proved that MobileNet could run efficiently on mobile devices with minimal accuracy drop. However, it was prone to lower accuracies on fine-grained target classes.",
    7: "Jiang et al. [7] introduced a custom architecture called IN-ResNet by inserting inception modules into a ResNet base structure. The model achieved an accuracy of 94.65% on five types of apple diseases. The main limitation was its lower classification accuracy compared to modern lightweight models.",
    8: "Liu et al. [8] developed an improved CNN based on AlexNet for apple leaf disease detection. By introducing a new preprocessing layer, they achieved a classification accuracy of 97.62% on four main diseases. However, their model's accuracy degraded significantly when faced with complex leaf shadows and noisy backgrounds.",
    9: "Mohanty et al. [9] trained standard AlexNet and GoogLeNet architectures on the PlantVillage dataset to classify 26 crop diseases. Although they achieved a high accuracy of 99.35%, the models are computationally heavy. Their study was limited by the lack of testing on real-world backgrounds.",
    10: "Sladojevic et al. [10] proposed a deep CNN model trained on internet-sourced images to classify 15 different plant diseases. The model achieved a test accuracy of 96.3%. However, the training phase was highly time-consuming, and the model was susceptible to overfitting on small sample sizes.",
    11: "Yan et al. [11] proposed an improved ResNet50 model with modified residual connections. This model achieved an accuracy of 96.55% for apple leaf diseases. The main limitation remained its slow inference speed and high model complexity.",
    12: "Zhong and Zhao [12] evaluated DenseNet121 on apple leaf disease classification. The model achieved a testing accuracy of 93.71%. However, the dense connections resulted in high memory access costs, making it difficult to run on low-resource hardware."
}
sorted_keys = sorted(list(studies.keys()), key=lambda k: ref_map[k])
sorted_texts = []
for k in sorted_keys:
    sorted_texts.append(replace_citations_text(studies[k], ref_map))

p17_text = "To better understand the literature, we summarize the methodologies and constraints of the aforementioned studies. " + " ".join(sorted_texts)
doc.paragraphs[17].text = p17_text

# 6. Rebuild Bibliography
print("Rebuilding sequentially renumbered bibliography...")
for idx in range(67, 115):
    doc.paragraphs[idx].text = ""

for idx, orig_num in enumerate(citation_seq):
    new_num = idx + 1
    detail = orig_references[orig_num]
    doc.paragraphs[67 + idx].text = f"[{new_num}] {detail}"

# Delete remaining unused reference paragraphs
paragraphs_to_delete = []
for idx in range(67 + len(citation_seq), 115):
    paragraphs_to_delete.append(doc.paragraphs[idx])

for p in paragraphs_to_delete:
    delete_paragraph(p)

# Save intermediate changes
doc.save(output_doc_path)
print("Saved bibliography, abstract, introduction, and related work updates.")
