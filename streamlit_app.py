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
# Mapping dictionary with amplifying info from the CQI Handbook for items 1–29.
# (This sample text is based on the handbook excerpt; adjust as needed.)
handbook_info = {
    "Item 1 – Self Assessment": (
        "Has the unit completed an initial self-assessment CQI checklist? "
        "Yes = 2 points or No = 0 points."
    ),
    "Item 2 – Self Assessment Submission": (
        "Were the results of the self-assessment submitted to 30 NCR SharePoint "
        "no later than 7-days prior to inspection? Yes = 2 points or No = 0 points."
    ),
    "Item 3 – Notice to Proceed (NTP)": (
        "Has a project confirmation or turnover brief been conducted with 30 NCR "
        "resulting in receiving a NTP? Yes = 4 points or No = 0 points."
    ),
    "Item 4 – Project Schedule": (
        "Is the unit achieving the given tasking? Project on exact schedule = 16 points; "
        "Within allowable deviation = 12 points; Outside allowable deviation = 4 points; "
        "Not monitored = 0 points. Allowable deviations are based on total project Mandays."
    ),
    "Item 5 – Project Management": (
        "Is a project management tool/CPM being utilized to track progress and scheduling? "
        "Yes = 2 points or No = 0 points."
    ),
    "Item 6 – QA for 30 NCR Detail Sites": (
        "QA involvement: Zero discrepancies = 4 points; Acceptable or recommendations = 3 points; "
        "Reports not detailed or multiple discrepancies = 2 points; No QA involvement = 0 points."
    ),
    "Item 7 & 8 – FAR/RFI": (
        "Inspect FAR/RFI log for continuity over the project’s life. "
        "100% up-to-date/all logged = 4 points; Acceptable with recommendations = 3 points; "
        "Missing/not logged = 2 points; Not tracked = 0 points."
    ),
    "Item 9 – DFOW Sheet": (
        "Ensure the DFOW sheet is accurate and updated. "
        "Accurate/up-to-date = 4 points; Acceptable with recommendations = 3 points; "
        "Missing/incorrect = 2 points; Blank/missing = 0 points."
    ),
    "Item 10 – Turnover Projects": (
        "Review turnover memorandum: All discrepancies identified post-turnover must be validated and classified. "
        "If validated and rework plan established = 4 points; No documentation = 0 points."
    ),
    "Item 11 – Funds Provided": (
        "Validate that project funding is tracked via funding documents. "
        "Monitored = 4 points; Not monitored = 0 points."
    ),
    "Item 12 – Estimate at Completion Cost (EAC)": (
        "EAC must include all expenditures and estimates. "
        "Monitored and accurate = 4 points; Acceptable (89%-80% accuracy) = 3 points; "
        "Within 79%-60% accuracy = 2 points; ≤59% accuracy = 0 points."
    ),
    "Item 13 – Current Expenditures": (
        "Verify exact amounts expended on the project. "
        "Accurate = 4 points; Acceptable = 3 points; Discrepancies = 2 points; ≤59% accuracy = 0 points."
    ),
    "Item 14 – Project Material Status Report (PMSR)": (
        "Inspect PMSR for completeness and accuracy. "
        "Updated and accurate = 10 points; Acceptable (99%-90% validity) = 8 points; "
        "Multiple discrepancies = 4 points; Class IV not tracked = 2 points; ≤59% validity = 0 points."
    ),
    "Item 15 – Report Submission": (
        "Confirm PMSR and EAC reports are routed monthly. "
        "Routed = 2 points; Not routed = 0 points."
    ),
    "Item 16 – Materials On-Hand": (
        "Ensure materials on-hand are managed and verified. "
        "Organized and verified = 10 points; Minor discrepancies = 8 points; "
        "Multiple discrepancies = 4 points; Unsatisfactory = 0 points."
    ),
    "Item 17 – DD Form 200": (
        "Verify DD Form 200’s are correct and valid. "
        "Correct = 2 points; Not maintained = 0 points."
    ),
    "Item 18 – Borrowed Material Tickler File": (
        "Inspect borrowed material files for proper approval and documentation. "
        "Valid and approved = 2 points; Not managed properly = 0 points."
    ),
    "Item 19 – Project Brief": (
        "Review the project brief for detail and ownership. "
        "Detailed and comprehensive = 5 points; Acceptable = 3 points; "
        "Not detailed = 2 points; Substandard = 0 points."
    ),
    "Item 20 – Calculate Manday Capability": (
        "Verify that crew composition and MD capability meet tasking requirements. "
        "Match = 6 points; Acceptable = 4 points; Not appropriate = 2 points; No alignment = 0 points."
    ),
    "Item 21 – Equipment": (
        "Validate that required equipment is onsite and scheduled appropriately. "
        "All required equipment onsite = 6 points; Acceptable = 4 points; Inadequate = 2 points; Not onsite = 0 points."
    ),
    "Item 22 – CASS Spot Check": (
        "Inspect CASS for adherence to prints and specifications. "
        "100% IAW = 12 points; Acceptable = 8 points; Multiple discrepancies = 4 points; Not documented = 0 points."
    ),
    "Item 23 – Designation Letters": (
        "Check that designation letters are up-to-date and signed. "
        "Current and signed = 5 points; Not up-to-date = 3 points; Missing = 0 points."
    ),
    "Item 24 – Job Box Review": (
        "Review jobsite board items per NTRP guidelines. "
        "All items accurate/up-to-date = 20 points; For discrepancies, subtract specified points (e.g., LVIII=6, etc.)."
    ),
    "Item 25 – Review QC Package": (
        "Ensure QC reports are comprehensive and follow approved specifications. "
        "Comprehensive = 8 points; Acceptable = 6 points; Not detailed = 4 points; No QC evidence = 0 points."
    ),
    "Item 26 – Submittals": (
        "Validate that material submittals are current and properly logged. "
        "Current and logged = 4 points; Not current = 2 points; Not submitted = 0 points."
    ),
    "Item 27a – QC Inspection Plan": (
        "Check that the QC inspection plan includes quantifiable measures. "
        "100% quantifiable = 10 points; 99%-85% = 7 points; 84%-70% = 3 points; >70% = 0 points."
    ),
    "Item 27b – QC Inspection": (
        "On-site QC inspection: No discrepancies = 5 points; Discrepancies = 0 points."
    ),
    "Item 28 – Job Box Review (QC)": (
        "Review QC plan and daily QC reports for completeness. "
        "Up-to-date = 5 points; For discrepancies, subtract (QC plan missing = 3, gaps = 2)."
    ),
    "Item 29 – Job Box Review (Safety)": (
        "Review safety plan, daily safety reports, and emergency contacts. "
        "Emergency contacts up-to-date = 5 points; For discrepancies, subtract (Safety plan missing = 3, reports gaps = 1, missing emergency data = 1)."
    )
}

# -------------------------------------------------------------------
# Custom PDF class with header and footer.
# -------------------------------------------------------------------
class PDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base_dir = os.path.dirname(__file__)
        normal_font_path = os.path.join(base_dir, "DejaVuSans.ttf")
        self.add_font("DejaVu", "", normal_font_path, uni=True)
    
    def header(self):
        self.set_font('DejaVu', '', 16)
        self.cell(0, 10, "CQI Report", ln=1, align='C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# -------------------------------------------------------------------
# Function to generate the PDF.
# -------------------------------------------------------------------
def generate_pdf(handbook_details, form_data):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    
    # --- Handbook Amplifying Info Table ---
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    question_width = effective_width * 0.45    # 45% for item title
    details_width = effective_width * 0.55     # 55% for amplifying info
    line_height = 8

    # Header row for the handbook table
    pdf.cell(question_width, line_height, "Item", border=1, align='C')
    pdf.cell(details_width, line_height, "Amplifying Info", border=1, align='C')
    pdf.ln(line_height)
    
    for item, info in handbook_details.items():
        item_lines = wrap_text(pdf, item, question_width)
        info_lines = wrap_text(pdf, info, details_width)
        max_lines = max(len(item_lines), len(info_lines))
        for i in range(max_lines):
            item_text = item_lines[i] if i < len(item_lines) else ""
            info_text = info_lines[i] if i < len(info_lines) else ""
            pdf.cell(question_width, line_height, item_text, border=1)
            pdf.cell(details_width, line_height, info_text, border=1)
            pdf.ln(line_height)
    
    # --- Project Information Section ---
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, sanitize("Project Information"), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, sanitize(f"Project Name: {form_data.get('Project Name', '')}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Battalion: {form_data.get('Battalion', '')}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Start Date: {form_data.get('Start Date', '')}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Planned Start: {form_data.get('Planned Start', '')}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Planned Completion: {form_data.get('Planned Completion', '')}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Actual Completion: {form_data.get('Actual Completion', '')}"), ln=True)
    pdf.ln(5)
    
    # --- Assessment Inputs Section ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, sanitize("Assessment Inputs"), ln=True)
    pdf.set_font("Arial", "", 12)
    
    # List of tuples: (item_key, comment_key)
    items = [
        ("Item 1 – Self Assessment", "Comment for Item 1"),
        ("Item 2 – Self Assessment Submission", "Comment for Item 2"),
        ("Item 3 – Notice to Proceed (NTP)", "Comment for Item 3"),
        ("Item 4 – Project Schedule", "Comment for Item 4"),
        ("Item 5 – Project Management", "Comment for Item 5"),
        ("Item 6 – QA for 30 NCR Detail Sites", "Comment for Item 6"),
        ("Item 7 & 8 – FAR/RFI", "Comment for Item 7 & 8"),
        ("Item 9 – DFOW Sheet", "Comment for Item 9"),
        ("Item 10 – Turnover Projects", "Comment for Item 10"),
        ("Item 11 – Funds Provided", "Comment for Item 11"),
        ("Item 12 – Estimate at Completion Cost (EAC)", "Comment for Item 12"),
        ("Item 13 – Current Expenditures", "Comment for Item 13"),
        ("Item 14 – Project Material Status Report (PMSR)", "Comment for Item 14"),
        ("Item 15 – Report Submission", "Comment for Item 15"),
        ("Item 16 – Materials On-Hand", "Comment for Item 16"),
        ("Item 17 – DD Form 200", "Comment for Item 17"),
        ("Item 18 – Borrowed Material Tickler File", "Comment for Item 18"),
        ("Item 19 – Project Brief", "Comment for Item 19"),
        ("Item 20 – Calculate Manday Capability", "Comment for Item 20"),
        ("Item 21 – Equipment", "Comment for Item 21"),
        ("Item 22 – CASS Spot Check", "Comment for Item 22"),
        ("Item 23 – Designation Letters", "Comment for Item 23"),
        ("Item 24 – Job Box Review", "Comment for Item 24"),
        ("Item 25 – Review QC Package", "Comment for Item 25"),
        ("Item 26 – Submittals", "Comment for Item 26"),
        ("Item 27a – QC Inspection Plan", "Comment for Item 27a"),
        ("Item 27b – QC Inspection", "Comment for Item 27b"),
        ("Item 28 – Job Box Review (QC)", "Comment for Item 28"),
        ("Item 29 – Job Box Review (Safety)", "Comment for Item 29"),
    ]
    
    for item_key, comment_key in items:
        response = form_data.get(item_key, "")
        pdf.multi_cell(0, 10, sanitize(f"{item_key}: {response}"))
        comment = form_data.get(comment_key, "")
        if comment:
            pdf.multi_cell(0, 10, sanitize(f"--> Comment: {comment}"))
        pdf.ln(1)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, sanitize("Final Results"), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, sanitize(f"Final Score: {form_data.get('Final Score', '')} out of 175"), ln=True)
    pdf.cell(0, 10, sanitize(f"Final Percentage: {form_data.get('Final Percentage', '')}%"), ln=True)
    
    pdf_str = pdf.output(dest="S")
    pdf_bytes = pdf_str.encode("latin1")
    pdf_buffer = io.BytesIO(pdf_bytes)
    pdf_buffer.seek(0)
    return pdf_buffer

# -------------------------------------------------------------------
# Main App – fields update in real time.
# -------------------------------------------------------------------
st.title("Construction Quality Inspection (CQI) Assessment Tool")
st.markdown("**DEC 2023 - CONSTRUCTION QUALITY INSPECTION (CQI) HANDBOOK**")
st.write(
    "Fill out the information below. All grades will be summed and divided by 175 to yield a final percentage. "
    "Rounding is applied for values > 0.5%. For any item that does not achieve the perfect score, a comment is required."
)

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

# Example for Item 1 – Self Assessment
st.subheader("Item 1 – Self Assessment")
item1 = st.radio("Has the unit completed an initial self-assessment CQI checklist? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item1")
comment_item1 = ""
if item1 != "Yes":
    comment_item1 = st.text_area("Enter comment for Item 1 (required):", key="comment_item1")

# Example for Item 2 – Self Assessment Submission
st.subheader("Item 2 – Self Assessment Submission")
item2 = st.radio("Were the self-assessment results submitted to 30 NCR SharePoint at least 7 days prior to inspection? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item2")
comment_item2 = ""
if item2 != "Yes":
    comment_item2 = st.text_area("Enter comment for Item 2 (required):", key="comment_item2")

# ... Continue with the remaining items similarly ...
# For brevity, only a few items are shown here.
# Make sure to include all items from 1 to 29 in your actual app.
# Example for Item 29 – Job Box Review (Safety)
st.subheader("Item 29 – Job Box Review – Safety Plan & Daily Safety Reports")
deduction29 = st.number_input("Enter deduction for Item 29 (0 to 5):", min_value=0, max_value=5, value=0, step=1, key="deduction29")
item29 = 5 - deduction29
comment_item29 = ""
if deduction29 != 0:
    comment_item29 = st.text_area("Enter comment for Item 29 (required):", key="comment_item29")

# -------------------------------------------------------------------
# Calculate Final Score and Generate PDF
# -------------------------------------------------------------------
if st.button("Calculate Final Score"):
    errors = []
    # Validate comments for non-perfect items (sample validations)
    if item1 != "Yes" and not comment_item1.strip():
        errors.append("Item 1 requires a comment.")
    if item2 != "Yes" and not comment_item2.strip():
        errors.append("Item 2 requires a comment.")
    # ... add validations for all other items as needed ...
    if deduction29 != 0 and not comment_item29.strip():
        errors.append("Item 29 requires a comment for the deduction.")
    
    if errors:
        for err in errors:
            st.error(err)
    else:
        # Convert Yes/No to scores and compute totals (sample calculation)
        score1 = 2 if item1 == "Yes" else 0
        score2 = 2 if item2 == "Yes" else 0
        # ... compute scores for all items ...
        score29 = item29  # For item 29
        
        # For demonstration, assume a total score (replace with actual calculation)
        total_score = score1 + score2 + score29  # Extend with all items
        final_percentage = round(total_score / 175 * 100, 1)
        
        # Build form_data dictionary
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
            # ... include all items 3 to 28 similarly ...
            "Item 29 – Job Box Review – Safety Plan & Daily Safety Reports": f"Deduction: {deduction29}, Score: {item29}",
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
