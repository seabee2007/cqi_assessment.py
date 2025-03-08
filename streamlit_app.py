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
# Mapping dictionary with amplifying info from the handbook for each item.
# (This is a sample; adjust the text to match the full handbook as needed.)
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
        "Is the unit achieving the given tasking? "
        "Project on exact schedule = 16 points; "
        "Within allowable deviation = 12 points; "
        "Outside allowable deviation = 4 points; "
        "Not monitored = 0 points. Allowable deviations are based on total project Mandays."
    ),
    # ... (add the rest of your items here)
    "Item 29 – Job Box Review (Safety)": (
        "Emergency contacts up-to-date = 5 points; "
        "Subtract for discrepancies: Safety plan missing = 3, safety reports gaps = 1, missing emergency data = 1."
    )
}

# -------------------------------------------------------------------
# Custom PDF class
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

def generate_pdf(handbook_details, form_data):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    
    # --- Handbook Amplifying Info Table ---
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    question_width = effective_width * 0.45    # 45% for the item title
    details_width = effective_width * 0.55     # 55% for the amplifying info
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
    
    # Define items and comments as list of tuples
    items = [
        ("Item 1 – Self Assessment", "Comment for Item 1"),
        ("Item 2 – Self Assessment Submission", "Comment for Item 2"),
        ("Item 3 – Notice to Proceed (NTP)", "Comment for Item 3"),
        ("Item 4 – Project Schedule", "Comment for Item 4"),
        # ... add the rest of your items here ...
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

# ... Continue with your other items similarly ...

# For example, Item 29:
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
    # Validate comments for non-perfect items...
    # (Validation code remains unchanged)
    
    # If no errors, compute the score
    if not errors:
        # (Score calculations remain unchanged)
        total_score = 150  # Example; replace with actual calculation
        final_percentage = round(total_score / 175 * 100, 1)
        
        # Build the form_data dictionary
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
            # ... include all other items similarly ...
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
    else:
        for err in errors:
            st.error(err)
