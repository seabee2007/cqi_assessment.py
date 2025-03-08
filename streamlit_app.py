import streamlit as st
from fpdf import FPDF
import io
import os

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def sanitize(text):
    """Replace problematic Unicode dashes with a standard hyphen."""
    if isinstance(text, str):
        return text.replace("\u2013", "-").replace("\u2014", "-")
    return text

def wrap_text(pdf, text, cell_width):
    """
    Splits text into a list of lines that fit within the given cell width.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        if pdf.get_string_width(test_line) <= cell_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# -------------------------------------------------------------------
# Mapping dictionary with amplifying info for items 1–29.
# (Sample text; update as needed to match your CQI Handbook.)
handbook_info = {
    "Item 1 – Self Assessment": "Has the unit completed an initial self-assessment CQI checklist? (Yes = 2 pts, No = 0 pts)",
    "Item 2 – Self Assessment Submission": "Were the self-assessment results submitted to 30 NCR SharePoint at least 7 days prior to inspection? (Yes = 2 pts, No = 0 pts)",
    "Item 3 – Notice to Proceed (NTP)": "Has a project confirmation/turnover brief been conducted with 30 NCR resulting in receiving a NTP? (Yes = 4 pts, No = 0 pts)",
    "Item 4 – Project Schedule": "Is the unit achieving the given tasking? (Exact = 16 pts; Within deviation = 12 pts; Outside deviation = 4 pts; Not monitored = 0 pts)",
    "Item 5 – Project Management": "Is a project management tool/CPM being utilized? (Yes = 2 pts, No = 0 pts)",
    "Item 6 – QA for 30 NCR Detail Sites": "QA involvement: (4 pts = Zero discrepancies; 3 pts = Acceptable; 2 pts = Multiple discrepancies; 0 pts = No QA involvement)",
    "Item 7 & 8 – FAR/RFI": "Inspect FAR/RFI log for continuity. (4 pts = 100% logged; 3 pts = Acceptable; 2 pts = Missing; 0 pts = Not tracked)",
    "Item 9 – DFOW Sheet": "Ensure the DFOW sheet is accurate and updated. (4 pts = Accurate; 3 pts = Acceptable; 2 pts = Incorrect; 0 pts = Blank)",
    "Item 10 – Turnover Projects": "Review turnover memorandum. (4 pts = Validated discrepancies with rework plan; 0 pts = No documentation)",
    "Item 11 – Funds Provided": "Are project funds tracked? (4 pts = Monitored; 0 pts = Not monitored)",
    "Item 12 – Estimate at Completion Cost (EAC)": "EAC accuracy. (4 pts = Accurate; 3 pts = Acceptable; 2 pts = Low accuracy; 0 pts = ≤59% accuracy)",
    "Item 13 – Current Expenditures": "Verify current expenditures. (4 pts = Accurate; 3 pts = Acceptable; 2 pts = Discrepancies; 0 pts = ≤59% accuracy)",
    "Item 14 – Project Material Status Report (PMSR)": "Inspect PMSR. (10 pts = 100% valid; 8 pts = Acceptable; 4 pts = Discrepancies; 2 or 0 pts otherwise)",
    "Item 15 – Report Submission": "Are PMSR and EAC reports routed monthly? (2 pts = Yes; 0 pts = No)",
    "Item 16 – Materials On-Hand": "Materials on-hand verification. (10 pts = Organized; 8 pts = Minor issues; 4 pts = Multiple issues; 0 pts = Unsatisfactory)",
    "Item 17 – DD Form 200": "DD Form 200 status. (2 pts = Correct; 0 pts = Not maintained)",
    "Item 18 – Borrowed Material Tickler File": "Borrow log verification. (2 pts = Valid; 0 pts = Not managed)",
    "Item 19 – Project Brief": "Project brief quality. (5 pts = Detailed; 3 pts = Acceptable; 2 or 0 pts otherwise)",
    "Item 20 – Calculate Manday Capability": "Crew composition & MD capability. (6 pts = Matches; 4/2/0 pts otherwise)",
    "Item 21 – Equipment": "Equipment adequacy. (6 pts = All onsite; 4 pts = Acceptable; 2 or 0 pts otherwise)",
    "Item 22 – CASS Spot Check": "CASS review. (12 pts = 100% compliant; 8/4/0 pts otherwise)",
    "Item 23 – Designation Letters": "Designation letters status. (5 pts = Current; 3 pts = Not up-to-date; 0 pts = Missing)",
    "Item 24 – Job Box Review": "Review jobsite board items. (20 pts maximum; deductions apply)",
    "Item 25 – Review QC Package": "QC package review. (8 pts = Comprehensive; 6/4/0 pts otherwise)",
    "Item 26 – Submittals": "Material submittals. (4 pts = Current; 2 pts = Not current; 0 pts = Not submitted)",
    "Item 27a – QC Inspection Plan": "QC Inspection Plan. (10 pts = 100% quantifiable; 7/3/0 pts otherwise)",
    "Item 27b – QC Inspection": "On-site QC inspection. (5 pts = No discrepancies; 0 pts otherwise)",
    "Item 28 – Job Box Review (QC)": "Review QC plan and daily QC reports. (5 pts = Up-to-date; deductions apply)",
    "Item 29 – Job Box Review (Safety)": "Review safety plan, daily safety reports, and emergency contacts. (5 pts = Up-to-date; deductions apply)"
}

# -------------------------------------------------------------------
# Custom PDF class
# -------------------------------------------------------------------
class PDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base_dir = os.path.dirname(__file__)
        font_path = os.path.join(base_dir, "DejaVuSans.ttf")
        self.add_font("DejaVu", "", font_path, uni=True)
    
    def header(self):
        self.set_font("DejaVu", "", 16)
        self.cell(0, 10, "CQI REPORT", ln=1, align="C")
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

# -------------------------------------------------------------------
# Function to generate the PDF.
# -------------------------------------------------------------------
def generate_pdf(handbook_details, form_data):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    left_width = effective_width * 0.8   # 80% for item question + amplifying info
    score_width = effective_width * 0.2  # 20% for score (centered)
    line_height = 8
    
    # Table header (optional)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(left_width, line_height, "ITEM & INFO", border=1, align="C")
    pdf.cell(score_width, line_height, "SCORE", border=1, align="C")
    pdf.ln(line_height)
    pdf.set_font("DejaVu", "", 12)
    
    # For each item, print the item with its amplifying info and score.
    for item, info in handbook_details.items():
        # Prepare left cell: item question (uppercase) and amplifying info.
        left_text = f"{item.upper()}: {info}"
        # Prepare right cell: score from form_data.
        score = form_data.get(item, "")
        right_text = f"{score}"
        
        # Determine required height for left cell.
        left_lines = wrap_text(pdf, left_text, left_width)
        left_cell_height = len(left_lines) * line_height
        # Determine required height for right cell.
        right_lines = wrap_text(pdf, right_text, score_width)
        right_cell_height = len(right_lines) * line_height
        cell_height = max(left_cell_height, right_cell_height)
        
        # Save current positions.
        start_x = pdf.get_x()
        start_y = pdf.get_y()
        
        # Left cell: Print the text without border.
        pdf.set_xy(start_x, start_y)
        pdf.multi_cell(left_width, line_height, left_text, border=0)
        # Draw a single rectangle around the entire left cell.
        pdf.rect(start_x, start_y, left_width, cell_height)
        
        # Right cell: Print the score (centered).
        pdf.set_xy(start_x + left_width, start_y)
        pdf.multi_cell(score_width, line_height, right_text, border=0, align="C")
        pdf.rect(start_x + left_width, start_y, score_width, cell_height)
        
        # Move to the next row.
        pdf.set_xy(start_x, start_y + cell_height)
        
        # If there is a comment, print a full-width row below.
        comment = form_data.get(f"Comment for {item}", "")
        if comment.strip():
            comment_text = f"COMMENT: {comment}"
            comment_lines = wrap_text(pdf, comment_text, effective_width)
            comment_height = len(comment_lines) * line_height
            pdf.multi_cell(effective_width, line_height, comment_text, border=1)
    
    # --- Final Results Section ---
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, sanitize("FINAL RESULTS"), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, sanitize(f"Final Score: {form_data.get('Final Score', '')} out of 175"), ln=True)
    pdf.cell(0, 10, sanitize(f"Final Percentage: {form_data.get('Final Percentage', '')}%"), ln=True)
    
    pdf_str = pdf.output(dest="S")
    pdf_bytes = pdf_str.encode("latin1")
    pdf_buffer = io.BytesIO(pdf_bytes)
    pdf_buffer.seek(0)
    return pdf_buffer

# -------------------------------------------------------------------
# Main App – Data Input Section
# -------------------------------------------------------------------
st.title("Construction Quality Inspection (CQI) Assessment Tool")
st.markdown("**DEC 2023 - CONSTRUCTION QUALITY INSPECTION (CQI) HANDBOOK**")
st.write("Fill out the fields below. For any item that does not achieve the perfect score, a comment is required. The final PDF will display each item with its amplifying info (in uppercase) along with your score and any comment.")

# --- Project Information ---
st.header("Project Information")
proj_name = st.text_input("Project Name:", key="proj_name")
battalion = st.text_input("Battalion Name:", key="battalion")
start_date = st.date_input("Start Date:", key="start_date")
planned_start = st.date_input("Planned Start Date:", key="planned_start")
planned_completion = st.date_input("Planned Completion Date:", key="planned_completion")
actual_completion = st.date_input("Actual Completion Date:", key="actual_completion")

# --- Assessment Inputs ---
st.header("Assessment Inputs")

# For each item, display the item, its amplifying info (using st.info), then input widgets.
# The key for each score is the same as the handbook_info key.
# The comment will be stored under the key "Comment for {item}".
# Item 1
st.subheader("Item 1 – Self Assessment")
st.info(handbook_info["Item 1 – Self Assessment"])
item1 = st.radio("Response:", options=["Yes", "No"], key="item1")
comment_item1 = st.text_area("Comment (if not perfect):", key="Comment for Item 1") if item1 != "Yes" else ""
# Item 2
st.subheader("Item 2 – Self Assessment Submission")
st.info(handbook_info["Item 2 – Self Assessment Submission"])
item2 = st.radio("Response:", options=["Yes", "No"], key="item2")
comment_item2 = st.text_area("Comment (if not perfect):", key="Comment for Item 2") if item2 != "Yes" else ""
# Item 3
st.subheader("Item 3 – Notice to Proceed (NTP)")
st.info(handbook_info["Item 3 – Notice to Proceed (NTP)"])
item3 = st.radio("Response:", options=["Yes", "No"], key="item3")
comment_item3 = st.text_area("Comment (if not perfect):", key="Comment for Item 3") if item3 != "Yes" else ""
# Item 4 – Project Schedule (calculated score)
st.subheader("Item 4 – Project Schedule")
st.info(handbook_info["Item 4 – Project Schedule"])
st.markdown(
    "Score is based on the difference between planned and actual work-in-place.\n"
    "Exact = 16 pts; Within deviation = 12 pts; Outside deviation = 4 pts."
)
total_md = st.number_input("Total Project Mandays:", value=1000, step=1, key="total_md")
planned_wip = st.number_input("Planned Work-in-Place (%)", value=100, step=1, key="planned_wip")
actual_wip = st.number_input("Actual Work-in-Place (%)", value=100, step=1, key="actual_wip")
if total_md < 1000:
    allowed = 10
elif total_md < 2000:
    allowed = 5
else:
    allowed = 2.5
diff = abs(actual_wip - planned_wip)
if diff == 0:
    item4_score = 16
elif diff <= allowed:
    item4_score = 12
else:
    item4_score = 4
st.write(f"Calculated Score for Item 4: {item4_score}")
comment_item4 = st.text_area("Comment (if not perfect):", key="Comment for Item 4") if item4_score != 16 else ""
# Item 5
st.subheader("Item 5 – Project Management")
st.info(handbook_info["Item 5 – Project Management"])
item5 = st.radio("Response:", options=["Yes", "No"], key="item5")
comment_item5 = st.text_area("Comment (if not perfect):", key="Comment for Item 5") if item5 != "Yes" else ""
# Item 6
st.subheader("Item 6 – QA for 30 NCR Detail Sites")
st.info(handbook_info["Item 6 – QA for 30 NCR Detail Sites"])
item6 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item6")
comment_item6 = st.text_area("Comment (if not perfect):", key="Comment for Item 6") if item6 != 4 else ""
# Item 7 & 8
st.subheader("Item 7 & 8 – FAR/RFI")
st.info(handbook_info["Item 7 & 8 – FAR/RFI"])
item78 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item78")
comment_item78 = st.text_area("Comment (if not perfect):", key="Comment for Item 7 & 8") if item78 != 4 else ""
# Item 9
st.subheader("Item 9 – DFOW Sheet")
st.info(handbook_info["Item 9 – DFOW Sheet"])
item9 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item9")
comment_item9 = st.text_area("Comment (if not perfect):", key="Comment for Item 9") if item9 != 4 else ""
# Item 10
st.subheader("Item 10 – Turnover Projects")
st.info(handbook_info["Item 10 – Turnover Projects"])
item10 = st.selectbox("Select score:", options=["N/A", 4, 0], key="item10")
comment_item10 = st.text_area("Comment (if not perfect):", key="Comment for Item 10") if item10 not in ["N/A", 4] else ""
# Item 11
st.subheader("Item 11 – Funds Provided")
st.info(handbook_info["Item 11 – Funds Provided"])
item11 = st.radio("Response:", options=["Yes", "No"], key="item11")
comment_item11 = st.text_area("Comment (if not perfect):", key="Comment for Item 11") if item11 != "Yes" else ""
# Item 12
st.subheader("Item 12 – Estimate at Completion Cost (EAC)")
st.info(handbook_info["Item 12 – Estimate at Completion Cost (EAC)"])
item12 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item12")
comment_item12 = st.text_area("Comment (if not perfect):", key="Comment for Item 12") if item12 != 4 else ""
# Item 13
st.subheader("Item 13 – Current Expenditures")
st.info(handbook_info["Item 13 – Current Expenditures"])
item13 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item13")
comment_item13 = st.text_area("Comment (if not perfect):", key="Comment for Item 13") if item13 != 4 else ""
# Item 14
st.subheader("Item 14 – Project Material Status Report (PMSR)")
st.info(handbook_info["Item 14 – Project Material Status Report (PMSR)"])
item14 = st.selectbox("Select score:", options=[10, 8, 4, 2, 0], key="item14")
comment_item14 = st.text_area("Comment (if not perfect):", key="Comment for Item 14") if item14 != 10 else ""
# Item 15
st.subheader("Item 15 – Report Submission")
st.info(handbook_info["Item 15 – Report Submission"])
item15 = st.radio("Response:", options=["Yes", "No"], key="item15")
comment_item15 = st.text_area("Comment (if not perfect):", key="Comment for Item 15") if item15 != "Yes" else ""
# Item 16
st.subheader("Item 16 – Materials On-Hand")
st.info(handbook_info["Item 16 – Materials On-Hand"])
item16 = st.selectbox("Select score:", options=[10, 8, 4, 0], key="item16")
comment_item16 = st.text_area("Comment (if not perfect):", key="Comment for Item 16") if item16 != 10 else ""
# Item 17
st.subheader("Item 17 – DD Form 200")
st.info(handbook_info["Item 17 – DD Form 200"])
item17 = st.radio("Response:", options=["Yes", "No"], key="item17")
comment_item17 = st.text_area("Comment (if not perfect):", key="Comment for Item 17") if item17 != "Yes" else ""
# Item 18
st.subheader("Item 18 – Borrowed Material Tickler File")
st.info(handbook_info["Item 18 – Borrowed Material Tickler File"])
item18 = st.radio("Response:", options=["Yes", "No"], key="item18")
comment_item18 = st.text_area("Comment (if not perfect):", key="Comment for Item 18") if item18 != "Yes" else ""
# Item 19
st.subheader("Item 19 – Project Brief")
st.info(handbook_info["Item 19 – Project Brief"])
item19 = st.selectbox("Select score:", options=[5, 3, 2, 0], key="item19")
comment_item19 = st.text_area("Comment (if not perfect):", key="Comment for Item 19") if item19 != 5 else ""
# Item 20
st.subheader("Item 20 – Calculate Manday Capability")
st.info(handbook_info["Item 20 – Calculate Manday Capability"])
item20 = st.selectbox("Select score:", options=[6, 4, 2, 0], key="item20")
comment_item20 = st.text_area("Comment (if not perfect):", key="Comment for Item 20") if item20 != 6 else ""
# Item 21
st.subheader("Item 21 – Equipment")
st.info(handbook_info["Item 21 – Equipment"])
item21 = st.selectbox("Select score:", options=[6, 4, 2, 0], key="item21")
comment_item21 = st.text_area("Comment (if not perfect):", key="Comment for Item 21") if item21 != 6 else ""
# Item 22
st.subheader("Item 22 – CASS Spot Check")
st.info(handbook_info["Item 22 – CASS Spot Check"])
item22 = st.selectbox("Select score:", options=[12, 8, 4, 0], key="item22")
comment_item22 = st.text_area("Comment (if not perfect):", key="Comment for Item 22") if item22 != 12 else ""
# Item 23
st.subheader("Item 23 – Designation Letters")
st.info(handbook_info["Item 23 – Designation Letters"])
item23 = st.selectbox("Select score:", options=[5, 3, 0], key="item23")
comment_item23 = st.text_area("Comment (if not perfect):", key="Comment for Item 23") if item23 != 5 else ""
# Item 24
st.subheader("Item 24 – Job Box Review")
st.info(handbook_info["Item 24 – Job Box Review"])
item24 = st.selectbox("Select score (20 is perfect; deductions apply):", options=[20, 0], key="item24")
deduction24 = st.number_input("Enter deduction for Item 24 (0 to 20):", min_value=0, max_value=20, value=0, step=1, key="deduction24")
calculated_item24 = 20 - deduction24
comment_item24 = st.text_area("Comment (if deduction applied):", key="Comment for Item 24") if deduction24 != 0 else ""
# Item 25
st.subheader("Item 25 – Review QC Package")
st.info(handbook_info["Item 25 – Review QC Package"])
item25 = st.selectbox("Select score:", options=[8, 6, 4, 0], key="item25")
comment_item25 = st.text_area("Comment (if not perfect):", key="Comment for Item 25") if item25 != 8 else ""
# Item 26
st.subheader("Item 26 – Submittals")
st.info(handbook_info["Item 26 – Submittals"])
item26 = st.selectbox("Select score:", options=[4, 2, 0], key="item26")
comment_item26 = st.text_area("Comment (if not perfect):", key="Comment for Item 26") if item26 != 4 else ""
# Item 27a
st.subheader("Item 27a – QC Inspection Plan")
st.info(handbook_info["Item 27a – QC Inspection Plan"])
item27a = st.selectbox("Select score:", options=[10, 7, 3, 0], key="item27a")
comment_item27a = st.text_area("Comment (if not perfect):", key="Comment for Item 27a") if item27a != 10 else ""
# Item 27b
st.subheader("Item 27b – QC Inspection")
st.info(handbook_info["Item 27b – QC Inspection"])
item27b = st.selectbox("Select score:", options=[5, 0], key="item27b")
comment_item27b = st.text_area("Comment (if not perfect):", key="Comment for Item 27b") if item27b != 5 else ""
# Item 28
st.subheader("Item 28 – Job Box Review (QC)")
st.info(handbook_info["Item 28 – Job Box Review (QC)"])
deduction28 = st.number_input("Enter deduction for Item 28 (0 to 5):", min_value=0, max_value=5, value=0, step=1, key="deduction28")
item28 = 5 - deduction28
comment_item28 = st.text_area("Comment (if deduction applied):", key="Comment for Item 28") if deduction28 != 0 else ""
# Item 29
st.subheader("Item 29 – Job Box Review (Safety)")
st.info(handbook_info["Item 29 – Job Box Review (Safety)"])
deduction29 = st.number_input("Enter deduction for Item 29 (0 to 5):", min_value=0, max_value=5, value=0, step=1, key="deduction29")
item29 = 5 - deduction29
comment_item29 = st.text_area("Comment (if deduction applied):", key="Comment for Item 29") if deduction29 != 0 else ""

# -------------------------------------------------------------------
# Calculate Final Score and Generate PDF
# -------------------------------------------------------------------
if st.button("Calculate Final Score"):
    errors = []
    # Sample validations (extend for all items as needed)
    if item1 != "Yes" and not comment_item1.strip():
        errors.append("Item 1 requires a comment.")
    if item2 != "Yes" and not comment_item2.strip():
        errors.append("Item 2 requires a comment.")
    if item3 != "Yes" and not comment_item3.strip():
        errors.append("Item 3 requires a comment.")
    if item4_score != 16 and not comment_item4.strip():
        errors.append("Item 4 requires a comment.")
    if item5 != "Yes" and not comment_item5.strip():
        errors.append("Item 5 requires a comment.")
    if item6 != 4 and not comment_item6.strip():
        errors.append("Item 6 requires a comment.")
    if item78 != 4 and not comment_item78.strip():
        errors.append("Items 7 & 8 require a comment.")
    if item9 != 4 and not comment_item9.strip():
        errors.append("Item 9 requires a comment.")
    if item10 not in ["N/A", 4] and not comment_item10.strip():
        errors.append("Item 10 requires a comment.")
    if item11 != "Yes" and not comment_item11.strip():
        errors.append("Item 11 requires a comment.")
    if item12 != 4 and not comment_item12.strip():
        errors.append("Item 12 requires a comment.")
    if item13 != 4 and not comment_item13.strip():
        errors.append("Item 13 requires a comment.")
    if item14 != 10 and not comment_item14.strip():
        errors.append("Item 14 requires a comment.")
    if item15 != "Yes" and not comment_item15.strip():
        errors.append("Item 15 requires a comment.")
    if item16 != 10 and not comment_item16.strip():
        errors.append("Item 16 requires a comment.")
    if item17 != "Yes" and not comment_item17.strip():
        errors.append("Item 17 requires a comment.")
    if item18 != "Yes" and not comment_item18.strip():
        errors.append("Item 18 requires a comment.")
    if item19 != 5 and not comment_item19.strip():
        errors.append("Item 19 requires a comment.")
    if item20 != 6 and not comment_item20.strip():
        errors.append("Item 20 requires a comment.")
    if item21 != 6 and not comment_item21.strip():
        errors.append("Item 21 requires a comment.")
    if item22 != 12 and not comment_item22.strip():
        errors.append("Item 22 requires a comment.")
    if item23 != 5 and not comment_item23.strip():
        errors.append("Item 23 requires a comment.")
    if deduction24 != 0 and not comment_item24.strip():
        errors.append("Item 24 requires a comment for the deduction.")
    if item25 != 8 and not comment_item25.strip():
        errors.append("Item 25 requires a comment.")
    if item26 != 4 and not comment_item26.strip():
        errors.append("Item 26 requires a comment.")
    if item27a != 10 and not comment_item27a.strip():
        errors.append("Item 27a requires a comment.")
    if item27b != 5 and not comment_item27b.strip():
        errors.append("Item 27b requires a comment.")
    if deduction28 != 0 and not comment_item28.strip():
        errors.append("Item 28 requires a comment for the deduction.")
    if deduction29 != 0 and not comment_item29.strip():
        errors.append("Item 29 requires a comment for the deduction.")
    
    if errors:
        for err in errors:
            st.error(err)
    else:
        # Convert Yes/No responses to numeric scores.
        score1 = 2 if item1 == "Yes" else 0
        score2 = 2 if item2 == "Yes" else 0
        score3 = 4 if item3 == "Yes" else 0
        score5 = 2 if item5 == "Yes" else 0
        score11 = 4 if item11 == "Yes" else 0
        score15 = 2 if item15 == "Yes" else 0
        score17 = 2 if item17 == "Yes" else 0
        score18 = 2 if item18 == "Yes" else 0
        
        # Sample total score calculation (extend as needed).
        total_score = (
            score1 + score2 + score3 + item4_score + score5 +
            item6 + item78 + item9 +
            (item10 if item10 != "N/A" else 0) +
            score11 + item12 + item13 + item14 + score15 + item16 +
            score17 + score18 + item19 + item20 + item21 + item22 +
            item23 + calculated_item24 + item25 + item26 + item27a + item27b +
            item28 + item29
        )
        final_percentage = round(total_score / 175 * 100, 1)
        
        # Build form_data for PDF generation.
        form_data = {
            "Project Name": proj_name,
            "Battalion": battalion,
            "Start Date": str(start_date),
            "Planned Start": str(planned_start),
            "Planned Completion": str(planned_completion),
            "Actual Completion": str(actual_completion),
            "Item 1 – Self Assessment": item1,
            "Comment for Item 1": comment_item1,
            "Item 2 – Self Assessment Submission": item2,
            "Comment for Item 2": comment_item2,
            "Item 3 – Notice to Proceed (NTP)": item3,
            "Comment for Item 3": comment_item3,
            "Item 4 – Project Schedule": f"Planned: {planned_wip}%, Actual: {actual_wip}%, Score: {item4_score}",
            "Comment for Item 4": comment_item4,
            "Item 5 – Project Management": item5,
            "Comment for Item 5": comment_item5,
            "Item 6 – QA for 30 NCR Detail Sites": item6,
            "Comment for Item 6": comment_item6,
            "Item 7 & 8 – FAR/RFI": item78,
            "Comment for Item 7 & 8": comment_item78,
            "Item 9 – DFOW Sheet": item9,
            "Comment for Item 9": comment_item9,
            "Item 10 – Turnover Projects": item10,
            "Comment for Item 10": comment_item10,
            "Item 11 – Funds Provided": item11,
            "Comment for Item 11": comment_item11,
            "Item 12 – Estimate at Completion Cost (EAC)": item12,
            "Comment for Item 12": comment_item12,
            "Item 13 – Current Expenditures": item13,
            "Comment for Item 13": comment_item13,
            "Item 14 – Project Material Status Report (PMSR)": item14,
            "Comment for Item 14": comment_item14,
            "Item 15 – Report Submission": item15,
            "Comment for Item 15": comment_item15,
            "Item 16 – Materials On-Hand": item16,
            "Comment for Item 16": comment_item16,
            "Item 17 – DD Form 200": item17,
            "Comment for Item 17": comment_item17,
            "Item 18 – Borrowed Material Tickler File": item18,
            "Comment for Item 18": comment_item18,
            "Item 19 – Project Brief": item19,
            "Comment for Item 19": comment_item19,
            "Item 20 – Calculate Manday Capability": item20,
            "Comment for Item 20": comment_item20,
            "Item 21 – Equipment": item21,
            "Comment for Item 21": comment_item21,
            "Item 22 – CASS Spot Check": item22,
            "Comment for Item 22": comment_item22,
            "Item 23 – Designation Letters": item23,
            "Comment for Item 23": comment_item23,
            "Item 24 – Job Box Review": f"Deduction: {deduction24}, Score: {calculated_item24}",
            "Comment for Item 24": comment_item24,
            "Item 25 – Review QC Package": item25,
            "Comment for Item 25": comment_item25,
            "Item 26 – Submittals": item26,
            "Comment for Item 26": comment_item26,
            "Item 27a – QC Inspection Plan": item27a,
            "Comment for Item 27a": comment_item27a,
            "Item 27b – QC Inspection": item27b,
            "Comment for Item 27b": comment_item27b,
            "Item 28 – Job Box Review (QC)": f"Deduction: {deduction28}, Score: {item28}",
            "Comment for Item 28": comment_item28,
            "Item 29 – Job Box Review (Safety)": f"Deduction: {deduction29}, Score: {item29}",
            "Comment for Item 29": comment_item29,
            "Final Score": total_score,
            "Final Percentage": final_percentage,
        }
        st.session_state.form_data = form_data
        st.session_state.final_score = total_score
        st.session_state.final_percentage = final_percentage
        st.success("Final Score Calculated!")
        st.write("**Final Score:**", total_score, "out of 175")
        st.write("**Final Percentage:**", final_percentage, "%")
        
        pdf_file = generate_pdf(handbook_info, form_data)
        st.download_button(
            label="Download PDF Report",
            data=pdf_file,
            file_name="CQI_Report.pdf",
            mime="application/pdf"
        )
