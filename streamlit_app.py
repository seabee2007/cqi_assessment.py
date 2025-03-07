import streamlit as st
from fpdf import FPDF
import io

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def sanitize(text):
    """Replace problematic Unicode dashes with a standard hyphen."""
    if isinstance(text, str):
        return text.replace("\u2013", "-").replace("\u2014", "-")
    return text

# Custom PDF class with header and footer.
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, sanitize("Construction Quality Inspection (CQI) Checklist"), 0, 1, "C")
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")


import os
from fpdf import FPDF

def generate_pdf(form_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Adjust path if the font is inside a subfolder, e.g., "fonts/DejaVuSans.ttf"
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)
    
    # Your PDF generation logic
    items = list(form_data.items())
    for i, (key, value) in enumerate(items):
        pdf.cell(0, 10, f"{key}: {value}", ln=1)
        if (i + 1) % 10 == 0 and (i + 1) < len(items):
            pdf.add_page()
    
    return pdf.output(dest="S").encode("latin1")



    
    # --- Project Information ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, sanitize("Project Information"), ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, sanitize(f"Project Name: {form_data['Project Name']}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Battalion: {form_data['Battalion']}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Start Date: {form_data['Start Date']}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Planned Start: {form_data['Planned Start']}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Planned Completion: {form_data['Planned Completion']}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Actual Completion: {form_data['Actual Completion']}"), ln=True)
    pdf.ln(5)
    
    # --- Assessment Inputs ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, sanitize("Assessment Inputs"), ln=True)
    pdf.set_font("Arial", size=12)
    
    # List of tuples: (item_key, comment_key)
    items = [
        ("Item 1 – Self Assessment", "Comment for Item 1"),
        ("Item 2 – Self Assessment Submission", "Comment for Item 2"),
        ("Item 3 – Notice to Proceed (NTP)", "Comment for Item 3"),
        ("Item 4 – Project Schedule", "Comment for Item 4"),
        ("Item 5 – Project Management", "Comment for Item 5"),
        ("Item 6 – QA for 30 NCR Detail Sites", "Comment for Item 6"),
        ("Item 7 – FAR/RFI Log", "Comment for Item 7"),
        ("Item 8 – DFOW Sheet", "Comment for Item 8"),
        ("Item 9 – Turnover Projects", "Comment for Item 9"),
        ("Item 10 – Funds Provided", "Comment for Item 10"),
        ("Item 11 – Estimate at Completion Cost (EAC)", "Comment for Item 11"),
        ("Item 12 – Current Expenditures", "Comment for Item 12"),
        ("Item 13 – Project Material Status Report (PMSR)", "Comment for Item 13"),
        ("Item 14 – Report Submission", "Comment for Item 14"),
        ("Item 15 – Materials On-Hand", "Comment for Item 15"),
        ("Item 16 – DD Form 200", "Comment for Item 16"),
        ("Item 17 – Borrowed Material Tickler File", "Comment for Item 17"),
        ("Item 18 – Project Brief", "Comment for Item 18"),
        ("Item 19 – Calculate Manday Capability", "Comment for Item 19"),
        ("Item 20 – Equipment", "Comment for Item 20"),
        ("Item 21 – CASS Spot Check", "Comment for Item 21"),
        ("Item 22 – Designation Letters", "Comment for Item 22"),
        ("Item 23 – Job Box Review – Project Info Board", "Comment for Item 23"),
        ("Item 24 – QC Package Review – Follow-on & Continuity", "Comment for Item 24"),
        ("Item 25 – Submittals", "Comment for Item 25"),
        ("Item 26 – QC Inspection Plan (Item 27a)", "Comment for Item 26"),
        ("Item 27 – QC Inspection (Item 27b)", "Comment for Item 27"),
        ("Item 28 – Job Box Review – QC Plan & Daily QC Reports", "Comment for Item 28"),
        ("Item 29 – Job Box Review – Safety Plan & Daily Safety Reports", "Comment for Item 29"),
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
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, sanitize(f"Final Score: {form_data['Final Score']} out of 175"), ln=True)
    pdf.cell(0, 10, sanitize(f"Final Percentage: {form_data['Final Percentage']}%"), ln=True)
    
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

# Item 1 – Self Assessment (Yes/No, perfect = "Yes")
st.subheader("Item 1 – Self Assessment")
item1 = st.radio("Has the unit completed an initial self-assessment CQI checklist? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item1")
comment_item1 = ""
if item1 != "Yes":
    comment_item1 = st.text_area("Enter comment for Item 1 (required):", key="comment_item1")

# Item 2 – Self Assessment Submission (Yes/No, perfect = "Yes")
st.subheader("Item 2 – Self Assessment Submission")
item2 = st.radio("Were the self-assessment results submitted to 30 NCR SharePoint at least 7 days prior to inspection? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item2")
comment_item2 = ""
if item2 != "Yes":
    comment_item2 = st.text_area("Enter comment for Item 2 (required):", key="comment_item2")

# Item 3 – Notice to Proceed (NTP) (Yes/No, perfect = "Yes")
st.subheader("Item 3 – Notice to Proceed (NTP)")
item3 = st.radio("Has a project confirmation/turnover brief been conducted with 30 NCR resulting in receiving a NTP? (Yes = 4 pts, No = 0 pts)", options=["Yes", "No"], key="item3")
comment_item3 = ""
if item3 != "Yes":
    comment_item3 = st.text_area("Enter comment for Item 3 (required):", key="comment_item3")

# Item 4 – Project Schedule (calculated score, perfect = 16)
st.subheader("Item 4 – Project Schedule")
st.markdown(
    "Is the unit achieving the given tasking? Score is based on the actual percent of work-in-place vs scheduled. "
    "Allowable deviations based on total project Mandays (MD):\n• 0–1,000 MD = ±10%\n• 1,000–2,000 MD = ±5%\n• 2,000+ MD = ±2.5%\n\n"
    "Scoring:\n• Exact schedule = 16 pts\n• Within deviation = 12 pts\n• Outside deviation = 4 pts\n• Not monitored = 0 pts"
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

# Item 5 – Project Management (Yes/No, perfect = "Yes")
st.subheader("Item 5 – Project Management")
item5 = st.radio("Is a project management tool/CPM being utilized? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item5")
comment_item5 = ""
if item5 != "Yes":
    comment_item5 = st.text_area("Enter comment for Item 5 (required):", key="comment_item5")

# Item 6 – QA for 30 NCR Detail Sites (Select, perfect = 4)
st.subheader("Item 6 – QA for 30 NCR Detail Sites")
item6 = st.selectbox("Select score for Item 6 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item6")
comment_item6 = ""
if item6 != 4:
    comment_item6 = st.text_area("Enter comment for Item 6 (required):", key="comment_item6")

# Item 7 – FAR/RFI Log (Select, perfect = 4)
st.subheader("Item 7 – FAR/RFI Log")
item7 = st.selectbox("Select score for Item 7 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item7")
comment_item7 = ""
if item7 != 4:
    comment_item7 = st.text_area("Enter comment for Item 7 (required):", key="comment_item7")

# Item 8 – DFOW Sheet (Select, perfect = 4)
st.subheader("Item 8 – DFOW Sheet")
item8 = st.selectbox("Select score for Item 8 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item8")
comment_item8 = ""
if item8 != 4:
    comment_item8 = st.text_area("Enter comment for Item 8 (required):", key="comment_item8")

# Item 9 – Turnover Projects (Select, perfect = 4; if "N/A" then no comment required)
st.subheader("Item 9 – Turnover Projects")
item9 = st.selectbox("Select score for Item 9 (Options: N/A, 4, 0):", options=["N/A", 4, 0], key="item9")
comment_item9 = ""
if item9 not in ["N/A", 4]:
    comment_item9 = st.text_area("Enter comment for Item 9 (required):", key="comment_item9")

# Item 10 – Funds Provided (Yes/No, perfect = "Yes")
st.subheader("Item 10 – Funds Provided")
item10 = st.radio("Is project funding tracked via documents? (Yes = 4 pts, No = 0 pts)", options=["Yes", "No"], key="item10")
comment_item10 = ""
if item10 != "Yes":
    comment_item10 = st.text_area("Enter comment for Item 10 (required):", key="comment_item10")

# Item 11 – Estimate at Completion Cost (EAC) (Select, perfect = 4)
st.subheader("Item 11 – Estimate at Completion Cost (EAC)")
item11 = st.selectbox("Select score for Item 11 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item11")
comment_item11 = ""
if item11 != 4:
    comment_item11 = st.text_area("Enter comment for Item 11 (required):", key="comment_item11")

# Item 12 – Current Expenditures (Select, perfect = 4)
st.subheader("Item 12 – Current Expenditures")
item12 = st.selectbox("Select score for Item 12 (4, 3, 2, 0):", options=[4, 3, 2, 0], key="item12")
comment_item12 = ""
if item12 != 4:
    comment_item12 = st.text_area("Enter comment for Item 12 (required):", key="comment_item12")

# Item 13 – Project Material Status Report (PMSR) (Select, perfect = 10)
st.subheader("Item 13 – Project Material Status Report (PMSR)")
item13 = st.selectbox("Select score for Item 13 (10, 8, 4, 2, 0):", options=[10, 8, 4, 2, 0], key="item13")
comment_item13 = ""
if item13 != 10:
    comment_item13 = st.text_area("Enter comment for Item 13 (required):", key="comment_item13")

# Item 14 – Report Submission (Yes/No, perfect = "Yes")
st.subheader("Item 14 – Report Submission")
item14 = st.radio("Are PMSR and EAC routed to NMCB HQ monthly? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item14")
comment_item14 = ""
if item14 != "Yes":
    comment_item14 = st.text_area("Enter comment for Item 14 (required):", key="comment_item14")

# Item 15 – Materials On-Hand (Select, perfect = 10)
st.subheader("Item 15 – Materials On-Hand")
item15 = st.selectbox("Select score for Item 15 (10, 8, 4, 0):", options=[10, 8, 4, 0], key="item15")
comment_item15 = ""
if item15 != 10:
    comment_item15 = st.text_area("Enter comment for Item 15 (required):", key="comment_item15")

# Item 16 – DD Form 200 (Yes/No, perfect = "Yes")
st.subheader("Item 16 – DD Form 200")
item16 = st.radio("Are DD Form 200's maintained? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item16")
comment_item16 = ""
if item16 != "Yes":
    comment_item16 = st.text_area("Enter comment for Item 16 (required):", key="comment_item16")

# Item 17 – Borrowed Material Tickler File (Yes/No, perfect = "Yes")
st.subheader("Item 17 – Borrowed Material Tickler File")
item17 = st.radio("Are borrows properly executed? (Yes = 2 pts, No = 0 pts)", options=["Yes", "No"], key="item17")
comment_item17 = ""
if item17 != "Yes":
    comment_item17 = st.text_area("Enter comment for Item 17 (required):", key="comment_item17")

# Item 18 – Project Brief (Select, perfect = 5)
st.subheader("Item 18 – Project Brief")
item18 = st.selectbox("Select score for Item 18 (5, 3, 2, 0):", options=[5, 3, 2, 0], key="item18")
comment_item18 = ""
if item18 != 5:
    comment_item18 = st.text_area("Enter comment for Item 18 (required):", key="comment_item18")

# Item 19 – Calculate Manday Capability (Select, perfect = 6)
st.subheader("Item 19 – Calculate Manday Capability")
item19 = st.selectbox("Select score for Item 19 (6, 4, 2, 0):", options=[6, 4, 2, 0], key="item19")
comment_item19 = ""
if item19 != 6:
    comment_item19 = st.text_area("Enter comment for Item 19 (required):", key="comment_item19")

# Item 20 – Equipment (Select, perfect = 6)
st.subheader("Item 20 – Equipment")
item20 = st.selectbox("Select score for Item 20 (6, 4, 2, 0):", options=[6, 4, 2, 0], key="item20")
comment_item20 = ""
if item20 != 6:
    comment_item20 = st.text_area("Enter comment for Item 20 (required):", key="comment_item20")

# Item 21 – CASS Spot Check (Select, perfect = 12)
st.subheader("Item 21 – CASS Spot Check")
item21 = st.selectbox("Select score for Item 21 (12, 8, 4, 0):", options=[12, 8, 4, 0], key="item21")
comment_item21 = ""
if item21 != 12:
    comment_item21 = st.text_area("Enter comment for Item 21 (required):", key="comment_item21")

# Item 22 – Designation Letters (Select, perfect = 5)
st.subheader("Item 22 – Designation Letters")
item22 = st.selectbox("Select score for Item 22 (5, 3, 0):", options=[5, 3, 0], key="item22")
comment_item22 = ""
if item22 != 5:
    comment_item22 = st.text_area("Enter comment for Item 22 (required):", key="comment_item22")

# Item 23 – Job Box Review – Project Info Board (Deduction from 20, perfect = 0 deduction)
st.subheader("Item 23 – Job Box Review – Project Info Board")
deduction23 = st.number_input("Enter deduction for Item 23 (0 to 20):", min_value=0, max_value=20, value=0, step=1, key="deduction23")
item23 = 20 - deduction23
comment_item23 = ""
if deduction23 != 0:
    comment_item23 = st.text_area("Enter comment for Item 23 (required):", key="comment_item23")

# Item 24 – QC Package Review – Follow-on & Continuity (Select, perfect = 8)
st.subheader("Item 24 – QC Package Review – Follow-on & Continuity")
item24 = st.selectbox("Select score for Item 24 (8, 6, 4, 0):", options=[8, 6, 4, 0], key="item24")
comment_item24 = ""
if item24 != 8:
    comment_item24 = st.text_area("Enter comment for Item 24 (required):", key="comment_item24")

# Item 25 – Submittals (Select, perfect = 4)
st.subheader("Item 25 – Submittals")
item25 = st.selectbox("Select score for Item 25 (4, 2, 0):", options=[4, 2, 0], key="item25")
comment_item25 = ""
if item25 != 4:
    comment_item25 = st.text_area("Enter comment for Item 25 (required):", key="comment_item25")

# Item 26 – QC Inspection Plan (Item 27a) (Select, perfect = 10)
st.subheader("Item 26 – QC Inspection Plan (Item 27a)")
item26 = st.selectbox("Select score for Item 26 (10, 7, 3, 0):", options=[10, 7, 3, 0], key="item26")
comment_item26 = ""
if item26 != 10:
    comment_item26 = st.text_area("Enter comment for Item 26 (required):", key="comment_item26")

# Item 27 – QC Inspection (Item 27b) (Select, perfect = 5)
st.subheader("Item 27 – QC Inspection (Item 27b)")
item27 = st.selectbox("Select score for Item 27 (5, 0):", options=[5, 0], key="item27")
comment_item27 = ""
if item27 != 5:
    comment_item27 = st.text_area("Enter comment for Item 27 (required):", key="comment_item27")

# Item 28 – Job Box Review – QC Plan & Daily QC Reports (Deduction from 5, perfect = 0 deduction)
st.subheader("Item 28 – Job Box Review – QC Plan & Daily QC Reports")
deduction28 = st.number_input("Enter deduction for Item 28 (0 to 5):", min_value=0, max_value=5, value=0, step=1, key="deduction28")
item28 = 5 - deduction28
comment_item28 = ""
if deduction28 != 0:
    comment_item28 = st.text_area("Enter comment for Item 28 (required):", key="comment_item28")

# Item 29 – Job Box Review – Safety Plan & Daily Safety Reports (Deduction from 5, perfect = 0 deduction)
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
    # Validate that all non-perfect items have a comment.
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
    if item7 != 4 and not comment_item7.strip():
        errors.append("Item 7 requires a comment.")
    if item8 != 4 and not comment_item8.strip():
        errors.append("Item 8 requires a comment.")
    if item9 not in ["N/A", 4] and not comment_item9.strip():
        errors.append("Item 9 requires a comment.")
    if item10 != "Yes" and not comment_item10.strip():
        errors.append("Item 10 requires a comment.")
    if item11 != 4 and not comment_item11.strip():
        errors.append("Item 11 requires a comment.")
    if item12 != 4 and not comment_item12.strip():
        errors.append("Item 12 requires a comment.")
    if item13 != 10 and not comment_item13.strip():
        errors.append("Item 13 requires a comment.")
    if item14 != "Yes" and not comment_item14.strip():
        errors.append("Item 14 requires a comment.")
    if item15 != 10 and not comment_item15.strip():
        errors.append("Item 15 requires a comment.")
    if item16 != "Yes" and not comment_item16.strip():
        errors.append("Item 16 requires a comment.")
    if item17 != "Yes" and not comment_item17.strip():
        errors.append("Item 17 requires a comment.")
    if item18 != 5 and not comment_item18.strip():
        errors.append("Item 18 requires a comment.")
    if item19 != 6 and not comment_item19.strip():
        errors.append("Item 19 requires a comment.")
    if item20 != 6 and not comment_item20.strip():
        errors.append("Item 20 requires a comment.")
    if item21 != 12 and not comment_item21.strip():
        errors.append("Item 21 requires a comment.")
    if item22 != 5 and not comment_item22.strip():
        errors.append("Item 22 requires a comment.")
    if deduction23 != 0 and not comment_item23.strip():
        errors.append("Item 23 requires a comment for the deduction.")
    if item24 != 8 and not comment_item24.strip():
        errors.append("Item 24 requires a comment.")
    if item25 != 4 and not comment_item25.strip():
        errors.append("Item 25 requires a comment.")
    if item26 != 10 and not comment_item26.strip():
        errors.append("Item 26 requires a comment.")
    if item27 != 5 and not comment_item27.strip():
        errors.append("Item 27 requires a comment.")
    if deduction28 != 0 and not comment_item28.strip():
        errors.append("Item 28 requires a comment for the deduction.")
    if deduction29 != 0 and not comment_item29.strip():
        errors.append("Item 29 requires a comment for the deduction.")
        
    if errors:
        for err in errors:
            st.error(err)
    else:
        # Convert Yes/No scores to numeric values.
        score1 = 2 if item1 == "Yes" else 0
        score2 = 2 if item2 == "Yes" else 0
        score3 = 4 if item3 == "Yes" else 0
        score5 = 2 if item5 == "Yes" else 0
        score10 = 4 if item10 == "Yes" else 0
        score16 = 2 if item16 == "Yes" else 0
        score17 = 2 if item17 == "Yes" else 0
        score14 = 2 if item14 == "Yes" else 0
        
        score9 = 0
        if item9 != "N/A":
            score9 = item9
        
        total_score = (
            score1 + score2 + score3 + item4_score + score5 +
            item6 + item7 + item8 + score9 + score10 + item11 +
            item12 + item13 + score14 + item15 + score16 +
            score17 + item18 + item19 + item20 + item21 + item22 +
            item23 + item24 + item25 + item26 + item27 + item28 + item29
        )
        final_percentage = round(total_score / 175 * 100, 1)
        
        # Build the form_data dictionary using keys matching the PDF generation mapping.
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
            "Item 7 – FAR/RFI Log": item7,
            "Comment for Item 7": comment_item7,
            "Item 8 – DFOW Sheet": item8,
            "Comment for Item 8": comment_item8,
            "Item 9 – Turnover Projects": item9,
            "Comment for Item 9": comment_item9,
            "Item 10 – Funds Provided": item10,
            "Comment for Item 10": comment_item10,
            "Item 11 – Estimate at Completion Cost (EAC)": item11,
            "Comment for Item 11": comment_item11,
            "Item 12 – Current Expenditures": item12,
            "Comment for Item 12": comment_item12,
            "Item 13 – Project Material Status Report (PMSR)": item13,
            "Comment for Item 13": comment_item13,
            "Item 14 – Report Submission": item14,
            "Comment for Item 14": comment_item14,
            "Item 15 – Materials On-Hand": item15,
            "Comment for Item 15": comment_item15,
            "Item 16 – DD Form 200": item16,
            "Comment for Item 16": comment_item16,
            "Item 17 – Borrowed Material Tickler File": item17,
            "Comment for Item 17": comment_item17,
            "Item 18 – Project Brief": item18,
            "Comment for Item 18": comment_item18,
            "Item 19 – Calculate Manday Capability": item19,
            "Comment for Item 19": comment_item19,
            "Item 20 – Equipment": item20,
            "Comment for Item 20": comment_item20,
            "Item 21 – CASS Spot Check": item21,
            "Comment for Item 21": comment_item21,
            "Item 22 – Designation Letters": item22,
            "Comment for Item 22": comment_item22,
            "Item 23 – Job Box Review – Project Info Board": f"Deduction: {deduction23}, Score: {item23}",
            "Comment for Item 23": comment_item23,
            "Item 24 – QC Package Review – Follow-on & Continuity": item24,
            "Comment for Item 24": comment_item24,
            "Item 25 – Submittals": item25,
            "Comment for Item 25": comment_item25,
            "Item 26 – QC Inspection Plan (Item 27a)": item26,
            "Comment for Item 26": comment_item26,
            "Item 27 – QC Inspection (Item 27b)": item27,
            "Comment for Item 27": comment_item27,
            "Item 28 – Job Box Review – QC Plan & Daily QC Reports": f"Deduction: {deduction28}, Score: {item28}",
            "Comment for Item 28": comment_item28,
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
        
        pdf_file = generate_pdf(form_data)
        st.download_button(
            label="Download PDF Report",
            data=pdf_file,
            file_name="CQI_Report.pdf",
            mime="application/pdf"
        )

