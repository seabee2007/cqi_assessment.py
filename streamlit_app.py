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
# (Sample text; adjust as needed.)
handbook_info = {
    "Item 1 – Self Assessment": (
        "Has the unit completed an initial self-assessment CQI checklist? Yes = 2 points or No = 0 points."
    ),
    "Item 2 – Self Assessment Submission": (
        "Were the self-assessment results submitted to 30 NCR SharePoint no later than 7-days prior to inspection? Yes = 2 points or No = 0 points."
    ),
    "Item 3 – Notice to Proceed (NTP)": (
        "Has a project confirmation or turnover brief been conducted with 30 NCR resulting in receiving a NTP? Yes = 4 points or No = 0 points."
    ),
    "Item 4 – Project Schedule": (
        "Is the unit achieving the given tasking? Project on exact schedule = 16 points; Within allowable deviation = 12 points; Outside allowable deviation = 4 points; Not monitored = 0 points. Allowable deviations are based on total project Mandays."
    ),
    "Item 5 – Project Management": (
        "Is a project management tool/CPM being utilized to track progress and scheduling? Yes = 2 points or No = 0 points."
    ),
    "Item 6 – QA for 30 NCR Detail Sites": (
        "QA involvement: Zero discrepancies = 4 points; Acceptable or recommendations = 3 points; Reports not detailed or multiple discrepancies = 2 points; No QA involvement = 0 points."
    ),
    "Item 7 & 8 – FAR/RFI": (
        "Inspect FAR/RFI log for continuity over the project’s life. 100% up-to-date/all logged = 4 points; Acceptable with recommendations = 3 points; Missing/not logged = 2 points; Not tracked = 0 points."
    ),
    "Item 9 – DFOW Sheet": (
        "Ensure the DFOW sheet is accurate and updated. Accurate/up-to-date = 4 points; Acceptable with recommendations = 3 points; Missing/incorrect = 2 points; Blank/missing = 0 points."
    ),
    "Item 10 – Turnover Projects": (
        "Review turnover memorandum: All discrepancies identified post-turnover must be validated and classified. If validated and rework plan established = 4 points; No documentation = 0 points."
    ),
    "Item 11 – Funds Provided": (
        "Validate that project funding is tracked via funding documents. Monitored = 4 points; Not monitored = 0 points."
    ),
    "Item 12 – Estimate at Completion Cost (EAC)": (
        "EAC must include all expenditures and estimates. Monitored and accurate = 4 points; Acceptable (89%-80% accuracy) = 3 points; Within 79%-60% accuracy = 2 points; ≤59% accuracy = 0 points."
    ),
    "Item 13 – Current Expenditures": (
        "Verify exact amounts expended on the project. Accurate = 4 points; Acceptable = 3 points; Discrepancies = 2 points; ≤59% accuracy = 0 points."
    ),
    "Item 14 – Project Material Status Report (PMSR)": (
        "Inspect PMSR for completeness and accuracy. Updated and accurate = 10 points; Acceptable (99%-90% validity) = 8 points; Multiple discrepancies = 4 points; Class IV not tracked = 2 points; ≤59% validity = 0 points."
    ),
    "Item 15 – Report Submission": (
        "Confirm PMSR and EAC reports are routed monthly. Routed = 2 points; Not routed = 0 points."
    ),
    "Item 16 – Materials On-Hand": (
        "Ensure materials on-hand are managed and verified. Organized and verified = 10 points; Minor discrepancies = 8 points; Multiple discrepancies = 4 points; Unsatisfactory = 0 points."
    ),
    "Item 17 – DD Form 200": (
        "Verify DD Form 200’s are correct and valid. Correct = 2 points; Not maintained = 0 points."
    ),
    "Item 18 – Borrowed Material Tickler File": (
        "Inspect borrowed material files for proper approval and documentation. Valid and approved = 2 points; Not managed properly = 0 points."
    ),
    "Item 19 – Project Brief": (
        "Review the project brief for detail and ownership. Detailed and comprehensive = 5 points; Acceptable = 3 points; Not detailed = 2 points; Substandard = 0 points."
    ),
    "Item 20 – Calculate Manday Capability": (
        "Verify that crew composition and MD capability meet tasking requirements. Match = 6 points; Acceptable = 4 points; Not appropriate = 2 points; No alignment = 0 points."
    ),
    "Item 21 – Equipment": (
        "Validate that required equipment is onsite and scheduled appropriately. All required equipment onsite = 6 points; Acceptable = 4 points; Inadequate = 2 points; Not onsite = 0 points."
    ),
    "Item 22 – CASS Spot Check": (
        "Inspect CASS for adherence to prints and specifications. 100% IAW = 12 points; Acceptable = 8 points; Multiple discrepancies = 4 points; Not documented = 0 points."
    ),
    "Item 23 – Designation Letters": (
        "Check that designation letters are up-to-date and signed. Current and signed = 5 points; Not up-to-date = 3 points; Missing = 0 points."
    ),
    "Item 24 – Job Box Review": (
        "Review jobsite board items per NTRP guidelines. All items accurate/up-to-date = 20 points; For discrepancies, subtract specified points."
    ),
    "Item 25 – Review QC Package": (
        "Ensure QC reports are comprehensive and follow approved specifications. Comprehensive = 8 points; Acceptable = 6 points; Not detailed = 4 points; No QC evidence = 0 points."
    ),
    "Item 26 – Submittals": (
        "Validate that material submittals are current and properly logged. Current and logged = 4 points; Not current = 2 points; Not submitted = 0 points."
    ),
    "Item 27a – QC Inspection Plan": (
        "Check that the QC inspection plan includes quantifiable measures. 100% quantifiable = 10 points; 99%-85% = 7 points; 84%-70% = 3 points; >70% = 0 points."
    ),
    "Item 27b – QC Inspection": (
        "On-site QC inspection: No discrepancies = 5 points; Discrepancies = 0 points."
    ),
    "Item 28 – Job Box Review (QC)": (
        "Review QC plan and daily QC reports for completeness. Up-to-date = 5 points; For discrepancies, subtract (QC plan missing = 3, gaps = 2)."
    ),
    "Item 29 – Job Box Review (Safety)": (
        "Review safety plan, daily safety reports, and emergency contacts. Emergency contacts up-to-date = 5 points; For discrepancies, subtract (Safety plan missing = 3, reports gaps = 1, missing emergency data = 1)."
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
# Function to generate the PDF with two columns:
# Left column: Item title + amplifying info.
# Right column: Score and user comments.
# -------------------------------------------------------------------
def generate_pdf(handbook_details, form_data):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    
    # Define column widths.
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    left_width = effective_width * 0.6    # 60% for item + amplifying info
    right_width = effective_width * 0.4   # 40% for score and comments
    line_height = 8
    
    # Table header row.
    pdf.set_font("Arial", "B", 12)
    pdf.cell(left_width, line_height, "Item & Info", border=1, align='C')
    pdf.cell(right_width, line_height, "Score & Comments", border=1, align='C')
    pdf.ln(line_height)
    pdf.set_font("DejaVu", "", 12)
    
    # For each item in handbook_info, build left and right cell content.
    for item, amplifying_info in handbook_details.items():
        # Left cell: item title + amplifying info.
        left_text = f"{item}\n{amplifying_info}"
        # Right cell: build from form_data.
        comment_key = f"Comment for {item}"
        # If the item key is not exactly the same in form_data, try using it directly.
        score = form_data.get(item, "")
        comment = form_data.get(comment_key, "")
        right_text = f"Score: {score}"
        if comment.strip():
            right_text += f"\nComment: {comment}"
        
        # Wrap text for both columns.
        left_lines = wrap_text(pdf, left_text, left_width)
        right_lines = wrap_text(pdf, right_text, right_width)
        max_lines = max(len(left_lines), len(right_lines))
        # For each line, print both cells.
        for i in range(max_lines):
            left_line = left_lines[i] if i < len(left_lines) else ""
            right_line = right_lines[i] if i < len(right_lines) else ""
            pdf.cell(left_width, line_height, left_line, border=1)
            pdf.cell(right_width, line_height, right_line, border=1)
            pdf.ln(line_height)
    
    # --- Final Results Section ---
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
# Display Amplifying Info on the App
# -------------------------------------------------------------------
st.header("Amplifying Info for Each Item")
st.write("Click an item to view its detailed amplifying information from the CQI Handbook.")
for item, info in handbook_info.items():
    with st.expander(item):
        st.write(info)

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

# Item 1 – Self Assessment
st.subheader("Item 1 – Self Assessment")
item1 = st.radio("Has the unit completed an initial self-assessment CQI checklist? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item1")
comment_item1 = ""
if item1 != "Yes":
    comment_item1 = st.text_area("Enter comment for Item 1 (required):", key="comment_item1")

# Item 2 – Self Assessment Submission
st.subheader("Item 2 – Self Assessment Submission")
item2 = st.radio("Were the self-assessment results submitted to 30 NCR SharePoint at least 7 days prior to inspection? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item2")
comment_item2 = ""
if item2 != "Yes":
    comment_item2 = st.text_area("Enter comment for Item 2 (required):", key="comment_item2")

# Item 3 – Notice to Proceed (NTP)
st.subheader("Item 3 – Notice to Proceed (NTP)")
item3 = st.radio("Has a project confirmation/turnover brief been conducted with 30 NCR resulting in receiving a NTP? (Yes = 4 pts, No = 0 pts)", options=["Yes", "No"], key="item3")
comment_item3 = ""
if item3 != "Yes":
    comment_item3 = st.text_area("Enter comment for Item 3 (required):", key="comment_item3")

# Item 4 – Project Schedule
st.subheader("Item 4 – Project Schedule")
st.markdown(
    "Is the unit achieving the given tasking? Score is based on actual percent of work-in-place vs scheduled.\n"
    "Allowable deviations based on total project Mandays:\n"
    "• 0–1,000 MD = ±10%\n"
    "• 1,000–2,000 MD = ±5%\n"
    "• 2,000+ MD = ±2.5%\n\n"
    "Scoring:\n"
    "• Exact schedule = 16 pts\n"
    "• Within deviation = 12 pts\n"
    "• Outside deviation = 4 pts\n"
    "• Not monitored = 0 pts"
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
st.write(f"Calculated Project Schedule Score: {item4_score} points")
comment_item4 = ""
if item4_score != 16:
    comment_item4 = st.text_area("Enter comment for Item 4 (required):", key="comment_item4")

# Item 5 – Project Management
st.subheader("Item 5 – Project Management")
item5 = st.radio("Is a project management tool/CPM being utilized? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item5")
comment_item5 = ""
if item5 != "Yes":
    comment_item5 = st.text_area("Enter comment for Item 5 (required):", key="comment_item5")

# Item 6 – QA for 30 NCR Detail Sites
st.subheader("Item 6 – QA for 30 NCR Detail Sites")
item6 = st.selectbox("Select score for Item 6 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item6")
comment_item6 = ""
if item6 != 4:
    comment_item6 = st.text_area("Enter comment for Item 6 (required):", key="comment_item6")

# Item 7 & 8 – FAR/RFI
st.subheader("Item 7 & 8 – FAR/RFI")
item78 = st.selectbox("Select score for Items 7 & 8 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item78")
comment_item78 = ""
if item78 != 4:
    comment_item78 = st.text_area("Enter comment for Items 7 & 8 (required):", key="comment_item78")

# Item 9 – DFOW Sheet
st.subheader("Item 9 – DFOW Sheet")
item9 = st.selectbox("Select score for Item 9 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item9")
comment_item9 = ""
if item9 != 4:
    comment_item9 = st.text_area("Enter comment for Item 9 (required):", key="comment_item9")

# Item 10 – Turnover Projects
st.subheader("Item 10 – Turnover Projects")
item10 = st.selectbox("Select score for Item 10 (Options: N/A, 4, 0):", options=["N/A", 4, 0], key="item10")
comment_item10 = ""
if item10 not in ["N/A", 4]:
    comment_item10 = st.text_area("Enter comment for Item 10 (required):", key="comment_item10")

# Item 11 – Funds Provided
st.subheader("Item 11 – Funds Provided")
item11 = st.radio("Is project funding tracked via documents? (Yes = 4 pts, No = 0 pts)", options=["Yes", "No"], key="item11")
comment_item11 = ""
if item11 != "Yes":
    comment_item11 = st.text_area("Enter comment for Item 11 (required):", key="comment_item11")

# Item 12 – Estimate at Completion Cost (EAC)
st.subheader("Item 12 – Estimate at Completion Cost (EAC)")
item12 = st.selectbox("Select score for Item 12 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item12")
comment_item12 = ""
if item12 != 4:
    comment_item12 = st.text_area("Enter comment for Item 12 (required):", key="comment_item12")

# Item 13 – Current Expenditures
st.subheader("Item 13 – Current Expenditures")
item13 = st.selectbox("Select score for Item 13 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item13")
comment_item13 = ""
if item13 != 4:
    comment_item13 = st.text_area("Enter comment for Item 13 (required):", key="comment_item13")

# Item 14 – Project Material Status Report (PMSR)
st.subheader("Item 14 – Project Material Status Report (PMSR)")
item14 = st.selectbox("Select score for Item 14 (10, 8, 4, 2, 0):", options=[10, 8, 4, 2, 0], key="item14")
comment_item14 = ""
if item14 != 10:
    comment_item14 = st.text_area("Enter comment for Item 14 (required):", key="comment_item14")

# Item 15 – Report Submission
st.subheader("Item 15 – Report Submission")
item15 = st.radio("Are PMSR and EAC reports routed monthly? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item15")
comment_item15 = ""
if item15 != "Yes":
    comment_item15 = st.text_area("Enter comment for Item 15 (required):", key="comment_item15")

# Item 16 – Materials On-Hand
st.subheader("Item 16 – Materials On-Hand")
item16 = st.selectbox("Select score for Item 16 (10, 8, 4, 0):", options=[10, 8, 4, 0], key="item16")
comment_item16 = ""
if item16 != 10:
    comment_item16 = st.text_area("Enter comment for Item 16 (required):", key="comment_item16")

# Item 17 – DD Form 200
st.subheader("Item 17 – DD Form 200")
item17 = st.radio("Are DD Form 200's maintained? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item17")
comment_item17 = ""
if item17 != "Yes":
    comment_item17 = st.text_area("Enter comment for Item 17 (required):", key="comment_item17")

# Item 18 – Borrowed Material Tickler File
st.subheader("Item 18 – Borrowed Material Tickler File")
item18 = st.radio("Are borrows properly executed? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item18")
comment_item18 = ""
if item18 != "Yes":
    comment_item18 = st.text_area("Enter comment for Item 18 (required):", key="comment_item18")

# Item 19 – Project Brief
st.subheader("Item 19 – Project Brief")
item19 = st.selectbox("Select score for Item 19 (5, 3, 2, 0):", options=[5, 3, 2, 0], key="item19")
comment_item19 = ""
if item19 != 5:
    comment_item19 = st.text_area("Enter comment for Item 19 (required):", key="comment_item19")

# Item 20 – Calculate Manday Capability
st.subheader("Item 20 – Calculate Manday Capability")
item20 = st.selectbox("Select score for Item 20 (6, 4, 2, 0):", options=[6, 4, 2, 0], key="item20")
comment_item20 = ""
if item20 != 6:
    comment_item20 = st.text_area("Enter comment for Item 20 (required):", key="comment_item20")

# Item 21 – Equipment
st.subheader("Item 21 – Equipment")
item21 = st.selectbox("Select score for Item 21 (6, 4, 2, 0):", options=[6, 4, 2, 0], key="item21")
comment_item21 = ""
if item21 != 6:
    comment_item21 = st.text_area("Enter comment for Item 21 (required):", key="comment_item21")

# Item 22 – CASS Spot Check
st.subheader("Item 22 – CASS Spot Check")
item22 = st.selectbox("Select score for Item 22 (12, 8, 4, 0):", options=[12, 8, 4, 0], key="item22")
comment_item22 = ""
if item22 != 12:
    comment_item22 = st.text_area("Enter comment for Item 22 (required):", key="comment_item22")

# Item 23 – Designation Letters
st.subheader("Item 23 – Designation Letters")
item23 = st.selectbox("Select score for Item 23 (5, 3, 0):", options=[5, 3, 0], key="item23")
comment_item23 = ""
if item23 != 5:
    comment_item23 = st.text_area("Enter comment for Item 23 (required):", key="comment_item23")

# Item 24 – Job Box Review
st.subheader("Item 24 – Job Box Review")
item24 = st.selectbox("Select score for Item 24 (20, deduct as needed):", options=[20, 0], key="item24")
deduction24 = st.number_input("Enter deduction for Item 24 (0 to 20):", min_value=0, max_value=20, value=0, step=1, key="deduction24")
calculated_item24 = 20 - deduction24
comment_item24 = ""
if deduction24 != 0:
    comment_item24 = st.text_area("Enter comment for Item 24 (required for deduction):", key="comment_item24")

# Item 25 – Review QC Package
st.subheader("Item 25 – Review QC Package")
item25 = st.selectbox("Select score for Item 25 (8, 6, 4, 0):", options=[8, 6, 4, 0], key="item25")
comment_item25 = ""
if item25 != 8:
    comment_item25 = st.text_area("Enter comment for Item 25 (required):", key="comment_item25")

# Item 26 – Submittals
st.subheader("Item 26 – Submittals")
item26 = st.selectbox("Select score for Item 26 (4, 2, 0):", options=[4, 2, 0], key="item26")
comment_item26 = ""
if item26 != 4:
    comment_item26 = st.text_area("Enter comment for Item 26 (required):", key="comment_item26")

# Item 27a – QC Inspection Plan
st.subheader("Item 27a – QC Inspection Plan")
item27a = st.selectbox("Select score for Item 27a (10, 7, 3, 0):", options=[10, 7, 3, 0], key="item27a")
comment_item27a = ""
if item27a != 10:
    comment_item27a = st.text_area("Enter comment for Item 27a (required):", key="comment_item27a")

# Item 27b – QC Inspection
st.subheader("Item 27b – QC Inspection")
item27b = st.selectbox("Select score for Item 27b (5, 0):", options=[5, 0], key="item27b")
comment_item27b = ""
if item27b != 5:
    comment_item27b = st.text_area("Enter comment for Item 27b (required):", key="comment_item27b")

# Item 28 – Job Box Review (QC)
st.subheader("Item 28 – Job Box Review (QC)")
deduction28 = st.number_input("Enter deduction for Item 28 (0 to 5):", min_value=0, max_value=5, value=0, step=1, key="deduction28")
item28 = 5 - deduction28
comment_item28 = ""
if deduction28 != 0:
    comment_item28 = st.text_area("Enter comment for Item 28 (required):", key="comment_item28")

# Item 29 – Job Box Review (Safety)
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
        # Convert Yes/No responses to scores
        score1 = 2 if item1 == "Yes" else 0
        score2 = 2 if item2 == "Yes" else 0
        score3 = 4 if item3 == "Yes" else 0
        score5 = 2 if item5 == "Yes" else 0
        score11 = 4 if item11 == "Yes" else 0
        score15 = 2 if item15 == "Yes" else 0
        score17 = 2 if item17 == "Yes" else 0
        score18 = 2 if item18 == "Yes" else 0
        
        # Total score calculation (sample; extend to include all items as needed)
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
        
        # Build the form_data dictionary for PDF generation.
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
