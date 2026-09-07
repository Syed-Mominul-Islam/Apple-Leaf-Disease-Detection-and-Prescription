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
output_doc_path = r"c:\Users\Tizaraa\Desktop\Syed Mominul Islam(ID-243059)\New-journal-formet-v2_Updated.docx"

doc = docx.Document(orig_doc_path)

# Helper functions
def delete_paragraph(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    paragraph._p = paragraph._element = None

def insert_paragraph_after(paragraph, text="", style=None):
    new_p = OxmlElement('w:p')
    paragraph._p.addnext(new_p)
    new_para = docx.text.paragraph.Paragraph(new_p, paragraph._parent)
    if text:
        new_para.text = text
    if style:
        new_para.style = style
    return new_para

def replace_image(p, img_path, width_inches):
    p.text = "" # Clears text and drawings
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(img_path, width=Inches(width_inches))

def add_figure(after_para, img_path, caption_text, width_inches=5.0):
    img_p_xml = OxmlElement('w:p')
    after_para._p.addnext(img_p_xml)
    img_p = docx.text.paragraph.Paragraph(img_p_xml, after_para._parent)
    img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_p.add_run()
    run.add_picture(img_path, width=Inches(width_inches))
    
    cap_p_xml = OxmlElement('w:p')
    img_p_xml.addnext(cap_p_xml)
    cap_p = docx.text.paragraph.Paragraph(cap_p_xml, after_para._parent)
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cap = cap_p.add_run(caption_text)
    run_cap.font.name = 'Times New Roman'
    run_cap.font.size = Pt(11)
    run_cap.font.bold = True
    
    space_p_xml = OxmlElement('w:p')
    cap_p_xml.addnext(space_p_xml)
    space_p = docx.text.paragraph.Paragraph(space_p_xml, after_para._parent)
    return space_p

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
    
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(r'<w:tcBorders %s><w:bottom w:val="single" w:sz="8" w:color="000000"/></w:tcBorders>' % nsdecls('w'))
        tcPr.append(tcBorders)

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

def add_cross_val_table(after_para, cv_data):
    table = doc.add_table(rows=0, cols=5)
    after_para._p.addnext(table._tbl)
    
    headers = ["Fold", "Accuracy (%)", "Precision", "Recall", "F1-Score"]
    row = table.add_row()
    for col_idx, text in enumerate(headers):
        row.cells[col_idx].text = text
        p = row.cells[col_idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.bold = True
        p.runs[0].font.name = 'Times New Roman'
        
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
    table._tbl.addnext(spacing_p)
    return docx.text.paragraph.Paragraph(spacing_p, after_para._parent)

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

# --- PHASE 1: TRACING CITATIONS AND PREPARING MAP (Read-only) ---
p_ref_idx = find_paragraph_idx("References")
ref_pattern = re.compile(r'^\[(\d+)\]\s*(.*)$')
orig_references = {}
for i in range(p_ref_idx + 1, len(doc.paragraphs)):
    p_text = doc.paragraphs[i].text.strip()
    match = ref_pattern.match(p_text)
    if match:
        ref_num = int(match.group(1))
        orig_references[ref_num] = match.group(2)

print("Loaded original references from bibliography.")

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

print("Traced cited references.")

# Create ref_map: orig_number -> new_number
ref_map = {orig_num: new_num for new_num, orig_num in enumerate(citation_seq, 1)}

# Helper functions for reference substitution
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

# --- PHASE 2: DYNAMIC HEADING AND STRUCTURE UPDATES ---
print("Phase 2: Structural updates...")

# 1. Update Figure 1
print("Updating Figure 1 (Methodology Flowchart)...")
p_fig1_cap_idx = find_paragraph_idx("Figure 1:", is_prefix=True)
p_fig1_img = doc.paragraphs[p_fig1_cap_idx - 1]
replace_image(p_fig1_img, os.path.join(base_dir, "AppleNetV1_Pipeline_Flowchart.png"), 5.0)

# 2. Expand Section 3.1 Dataset Collection
print("Expanding Section 3.1 (Dataset Collection)...")
p_3_1_idx = find_paragraph_idx("3.1. Dataset Collection")
p_3_1_text = doc.paragraphs[p_3_1_idx + 1]

p_3_1_text.text = (
    "The dataset used in this study consists of a total of 13,470 leaf images. These images are consolidated from two main sources: "
    "the PlantVillage dataset (which provides standardized laboratory images) and the Mendeley Data Apple Leaf Disease Dataset "
    "(which provides natural orchard condition images with complex backgrounds, shadows, and varying light conditions). "
    "To reduce false positive diagnostics, a negative background leaf class (Not_Apple_Leaf) of 1,915 images was collected from "
    "online repositories. All images are in standard JPEG format, with resolutions ranging from 96x126 to 2667x4000 pixels. "
    "During preprocessing, all images are resized to 224x224x3 dimensions. The final dataset is split into training (80%), "
    "validation (10%), and testing (10%) sets. Table 2 details the exact class distribution."
)

p_after_dataset_text = add_figure(
    p_3_1_text, 
    os.path.join(images_dir, "dataset_samples.png"), 
    "Figure 2: Sample leaf images from the merged dataset across the seven classes.",
    width_inches=5.0
)

# 3. Format Equations in Section 3.4
print("Formatting Equations in Section 3.4...")
p_3_4_idx = find_paragraph_idx("3.4. Performance Evaluation Metrics")
p_3_4_text = doc.paragraphs[p_3_4_idx + 1]

p_3_4_text.text = (
    "To evaluate the model quantitatively, we measure four standard classification metrics: Accuracy, Precision, Recall, and F1-Score. "
    "These metrics are defined using True Positives (TP), False Positives (FP), True Negatives (TN), and False Negatives (FN) as follows:"
)

p_eq = insert_paragraph_after(p_3_4_text, "1. Accuracy: The proportion of correctly predicted instances out of all test samples.")
p_eq = add_equation_table(p_eq, "Accuracy = (TP + TN) / (TP + TN + FP + FN)", "(1)")

p_eq = insert_paragraph_after(p_eq, "2. Precision: The ratio of correctly predicted positive cases to the total predicted positive cases.")
p_eq = add_equation_table(p_eq, "Precision = TP / (TP + FP)", "(2)")

p_eq = insert_paragraph_after(p_eq, "3. Recall: The ratio of correctly predicted positive cases to all actual positive cases in the dataset.")
p_eq = add_equation_table(p_eq, "Recall = TP / (TP + FN)", "(3)")

p_eq = insert_paragraph_after(p_eq, "4. F1-Score: The harmonic mean of precision and recall, representing balanced classification performance.")
p_eq = add_equation_table(p_eq, "F1-Score = 2 * (Precision * Recall) / (Precision + Recall)", "(4)")

# 4. Update Figure 4 (Comparative DL Architectures)
print("Updating Figure 4 (Comparative DL Flowchart)...")
p_fig4_cap_idx = find_paragraph_idx("Figure 4:", is_prefix=True)
p_fig4_img = doc.paragraphs[p_fig4_cap_idx - 1]
replace_image(p_fig4_img, os.path.join(images_dir, "unnamed.jpg"), 4.5)
doc.paragraphs[p_fig4_cap_idx].text = "Figure 3: Transfer learning framework flowchart utilized for comparisons."

# 5. Section 3.6 Proposed AppleNetV1 Architecture
print("Updating Section 3.6 (Proposed AppleNetV1)...")
p_3_6_idx = find_paragraph_idx("3.6. AppleNetV1 (Baseline)")
doc.paragraphs[p_3_6_idx].text = "3.6. Proposed AppleNetV1 Architecture"

p_fig2_cap_idx = find_paragraph_idx("Figure 2:", is_prefix=True)
p_fig2_img = doc.paragraphs[p_fig2_cap_idx - 1]

replace_image(p_fig2_img, os.path.join(images_dir, "model_architecture.png"), 5.0)
doc.paragraphs[p_fig2_cap_idx].text = "Figure 4: Layer-wise block architecture of the proposed AppleNetV1 model."

p_after = doc.paragraphs[p_fig2_cap_idx]
p_after = add_figure(
    p_after,
    os.path.join(base_dir, "logs", "appleNetV1", "accuracy_loss_graph.png"),
    "Figure 5: Training accuracy and loss curves over 25 epochs for the AppleNetV1 model.",
    width_inches=5.0
)

p_after = add_figure(
    p_after,
    os.path.join(base_dir, "logs", "appleNetV1", "roc_curve.png"),
    "Figure 6: Receiver Operating Characteristic (ROC) curves of AppleNetV1 across the seven classes.",
    width_inches=5.0
)

p_after = add_figure(
    p_after,
    os.path.join(base_dir, "logs", "appleNetV1", "confusion_matrix.png"),
    "Figure 7: Confusion matrix of the trained AppleNetV1 model on the 7-class test dataset.",
    width_inches=4.8
)

p_after = insert_paragraph_after(p_after, "To ensure that the model generalizes robustly and does not overfit to specific train-test splits, we perform a 10-fold cross-validation analysis on the merged dataset. The fold-wise accuracies, precisions, recalls, and F1-scores are summarized in Table 3.")

cv_data = [
    (1, 99.26, 0.9930, 0.9926, 0.9926),
    (2, 99.26, 0.9930, 0.9926, 0.9927),
    (3, 99.26, 0.9929, 0.9926, 0.9926),
    (4, 98.52, 0.9858, 0.9852, 0.9851),
    (5, 100.00, 1.0000, 1.0000, 1.0000),
    (6, 100.00, 1.0000, 1.0000, 1.0000),
    (7, 100.00, 1.0000, 1.0000, 1.0000),
    (8, 99.26, 0.9929, 0.9926, 0.9926),
    (9, 99.26, 0.9929, 0.9926, 0.9926),
    (10, 98.52, 0.9858, 0.9852, 0.9851),
    ("Mean", 99.33, 0.9936, 0.9933, 0.9933),
    ("Std", 0.52, 0.0050, 0.0052, 0.0052)
]

p_after = add_cross_val_table(p_after, cv_data)

p_tbl_cap_xml = OxmlElement('w:p')
p_after._p.addnext(p_tbl_cap_xml)
p_tbl_cap = docx.text.paragraph.Paragraph(p_tbl_cap_xml, p_after._parent)
p_tbl_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_tbl = p_tbl_cap.add_run("Table 3: 10-Fold Cross-Validation Performance Metrics of AppleNetV1")
run_tbl.font.name = 'Times New Roman'
run_tbl.font.size = Pt(11)
run_tbl.font.bold = True

# 6. Section 4.3 Model Interpretability (Grad-CAM)
print("Adding Section 4.3 (Model Interpretability & Grad-CAM)...")
p_4_2_idx = find_paragraph_idx("4.2. Model Performance Evaluation")
p_boundaries = None
for idx in range(p_4_2_idx + 1, len(doc.paragraphs)):
    if "To analyze the classification boundaries" in doc.paragraphs[idx].text:
        p_boundaries = doc.paragraphs[idx]
        break

p_xai = insert_paragraph_after(p_boundaries, "4.3. Model Interpretability using Explainable AI (Grad-CAM)", style=doc.paragraphs[p_4_2_idx].style)

p_xai_text = insert_paragraph_after(
    p_xai,
    "To establish clinical trust and validate the diagnostic rationale of the custom AppleNetV1 model, "
    "we implemented Gradient-weighted Class Activation Mapping (Grad-CAM). Grad-CAM utilizes the gradient "
    "information flowing into the last convolutional layer (conv2d_3) of the model to produce a coarse localization map "
    "highlighting the important regions in the image for a prediction. "
    "Figure 8 displays the Grad-CAM visualizations for four primary apple leaf pathologies: Alternaria, Apple Scab, Black Rot, "
    "and Cedar Apple Rust. For each category, the figure showcases the input leaf image, the raw heat map, the class activation overlay, "
    "the guided guided backpropagation, and the guided Grad-CAM overlay. "
    "The heatmaps clearly indicate that the model concentrates its activation focus on the actual necrotic spots, lesion boundaries, "
    "and rust pustules on the leaf surfaces, rather than background noise, lighting artifacts, or healthy green regions. "
    "For instance, in Apple Scab, the activation peaks exactly at the dark olive-colored lesions. In Cedar Apple Rust, the model "
    "focuses on the bright orange rust spots. This spatial correlation confirms that the model has learned biologically relevant features "
    "for disease classification, ensuring high diagnostic transparency and trustworthiness for field deployment."
)

p_xai_img = add_figure(
    p_xai_text,
    os.path.join(images_dir, "gradcam_grid.png"),
    "Figure 8: Grad-CAM visual explanation heatmaps highlighting diseased spot lesions for different classes.",
    width_inches=5.0
)

# 7. Section 5 Web app updates
print("Expanding Section 5 (Web Development & Localized Deployment)...")
p_5_idx = find_paragraph_idx("5. Web Development & Localized Deployment")
p_fig3_cap_idx = find_paragraph_idx("Figure 3:", is_prefix=True)
doc.paragraphs[p_fig3_cap_idx].text = "Figure 9: System deployment workflow and execution path of the web application."

p_5_desc = doc.paragraphs[p_fig3_cap_idx + 1]

p_5_desc.text = (
    "To bridge the gap between complex deep learning models and practical agricultural utility, a web-based decision "
    "support system was developed and deployed using the Streamlit framework. The application provides an intuitive "
    "graphical user interface (GUI) designed for farmers and extension workers. Users can upload leaf images directly "
    "through the web interface, which are then preprocessed and classified in real-time. "
    "Figure 10 displays the application interface under various prediction scenarios, showing the diagnostic outputs for "
    "all seven classes (Alternaria, Apple Mosaic, Apple Scab, Black Rot, Cedar Apple Rust, Healthy, and Not Apple Leaf). "
    "To maximize accessibility for rural farmers in Bangladesh, the application features a localized Bengali prescription system. "
    "Upon predicting a disease, the system automatically translates the diagnosis and prints a detailed prescription in Bengali. "
    "The prescription includes the disease name (রোগের নাম), symptoms (লক্ষণসমূহ), biological control (জৈবিক দমন), "
    "and chemical control (রাসায়নিক দমন). For instance, when an image with Apple Scab is uploaded, the model outputs the "
    "prediction with high confidence, and the interface displays the corresponding Bengali treatment guidelines (e.g., spraying Mancozeb "
    "or Tebuconazole fungicides). If a non-apple leaf or background image is uploaded, the application correctly identifies "
    "it as 'Not Apple Leaf' and prompts the user to upload a valid apple leaf image, preventing false alarms."
)

p_after_web = add_figure(
    p_5_desc,
    os.path.join(images_dir, "web_app_screenshots.png"),
    "Figure 10: Streamlit web application interface showing localized Bengali prescriptions for all seven leaf classes.",
    width_inches=5.0
)

# 8. Section 6 Discussion and Comparison Table
print("Expanding Section 6 (Discussion)...")
p_6_idx = find_paragraph_idx("6. Discussion")
p_6 = doc.paragraphs[p_6_idx]

p_comp_intro = insert_paragraph_after(p_6, "To benchmark the performance of the proposed AppleNetV1 model, we conduct a comprehensive comparative analysis against leading studies in the existing literature. The comparisons are based on dataset size, number of target classes, models evaluated, and final test accuracy, as detailed in Table 5.")

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

p_comp_cap_xml = OxmlElement('w:p')
p_comp_tbl._p.addnext(p_comp_cap_xml)
p_comp_cap = docx.text.paragraph.Paragraph(p_comp_cap_xml, p_comp_tbl._parent)
p_comp_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_comp_tbl = p_comp_cap.add_run("Table 5: Comparison of proposed AppleNetV1 with existing studies in the literature.")
run_comp_tbl.font.name = 'Times New Roman'
run_comp_tbl.font.size = Pt(11)
run_comp_tbl.font.bold = True

# --- PHASE 3: TEXT UPDATES AND CITATION RENUMBERING ---
print("Phase 3: Text updates and citation renumbering...")

# 1. Clean Abstract
p_abstract_idx = find_paragraph_idx("Abstract")
p_abstract_text = doc.paragraphs[p_abstract_idx + 1]
p_abstract_text.text = strip_citations(p_abstract_text.text)

# 2. Clean Contributions
p_intro_idx = find_paragraph_idx("1. Introduction")
p_contrib = None
for idx in range(p_intro_idx + 1, len(doc.paragraphs)):
    if "The main contributions" in doc.paragraphs[idx].text:
        p_contrib = doc.paragraphs[idx]
        break

contrib_lines = p_contrib.text.split("\n")
cleaned_contrib = [strip_citations(line) for line in contrib_lines]
p_contrib.text = "\n".join(cleaned_contrib)

# 3. Update all body paragraphs citation numbers
for p in doc.paragraphs:
    if p.text.strip().startswith("[") and not p.text.strip().startswith(("[0", "[255")):
        continue
    if p == p_abstract_text or p == p_contrib:
        continue
    p.text = replace_citations_text(p.text, ref_map)

# Update cell references in all tables
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            cell.text = replace_citations_text(cell.text, ref_map)

# Sort and update Table 1 (Related Literature)
print("Sorting Related Literature table...")
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

# Sort Related Works paragraph text discussion
print("Sorting Related Works text discussion...")
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

for p in doc.paragraphs:
    if p.text.strip().startswith("To better understand the literature"):
        p.text = p17_text
        break

# --- PHASE 4: BIBLIOGRAPHY REBUILD & PARAGRAPH DELETIONS ---
print("Rebuilding sequentially renumbered bibliography...")
p_ref_idx = find_paragraph_idx("References")

# Clear the bibliography paragraphs following the References header
for idx in range(p_ref_idx + 1, len(doc.paragraphs)):
    doc.paragraphs[idx].text = ""

# Write the new references
for idx, orig_num in enumerate(citation_seq):
    new_num = idx + 1
    detail = orig_references[orig_num]
    doc.paragraphs[p_ref_idx + 1 + idx].text = f"[{new_num}] {detail}"

# Delete leftover empty reference paragraphs
paragraphs_to_delete = []
for idx in range(p_ref_idx + 1 + len(citation_seq), len(doc.paragraphs)):
    paragraphs_to_delete.append(doc.paragraphs[idx])

print(f"Deleting leftover reference paragraphs...")
for p in paragraphs_to_delete:
    delete_paragraph(p)

# Delete redundant old figures and captions
print("Deleting redundant old figures and captions...")
delete_paragraph(doc.paragraphs[find_paragraph_idx("Figure 5:", is_prefix=True) - 1])
delete_paragraph(doc.paragraphs[find_paragraph_idx("Figure 5:", is_prefix=True)])

delete_paragraph(doc.paragraphs[find_paragraph_idx("Figure 6:", is_prefix=True) - 1])
delete_paragraph(doc.paragraphs[find_paragraph_idx("Figure 6:", is_prefix=True)])

delete_paragraph(doc.paragraphs[find_paragraph_idx("Figure 7:", is_prefix=True) - 1])
delete_paragraph(doc.paragraphs[find_paragraph_idx("Figure 7:", is_prefix=True)])

# Rename Section 7 Conclusions and sub-sections
print("Renaming Conclusion sections...")
for p in doc.paragraphs:
    if p.text.strip() == "7. Conclusion":
        p.text = "7. Conclusions and Future Work"
    elif p.text.strip() == "7.1. Overall Summary":
        p.text = "7.1. Conclusions"
    elif p.text.strip() == "7.2. Limitations of the Work":
        p.text = "7.2. Limitations"

# Save final document
doc.save(output_doc_path)
print(f"SUCCESS: Final updated paper document saved to: {output_doc_path}")
