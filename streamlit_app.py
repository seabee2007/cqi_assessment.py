import streamlit as st
import streamlit.components.v1 as components
import datetime

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
def sanitize(text):
    """Replace problematic Unicode dashes with a standard hyphen."""
    if isinstance(text, str):
        return text.replace("\u2013", "-").replace("\u2014", "-")
    return text

# -------------------------------------------------------------------
# Handbook Amplifying Info for Items 1–29 (sample text; update as needed)
# -------------------------------------------------------------------
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
# Function to generate the print-friendly HTML
# -------------------------------------------------------------------
def generate_html(form_data, handbook_info):
    html = f"""
    <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          font-size: 12px;
          margin: 20px;
        }}
        .header {{
          text-align: center;
          font-size: 18px;
          font-weight: bold;
          margin-bottom: 20px;
        }}
        .section {{
          margin-bottom: 20px;
        }}
        .item-block {{
          border: 1px solid #333;
          padding: 5px;
          margin-bottom: 10px;
        }}
        .item-title {{
          font-weight: bold;
          text-transform: uppercase;
        }}
        .score {{
          text-align: center;
          font-weight: bold;
          display: inline-block;
          width: 15%;
          vertical-align: top;
          margin-left: 5px;
        }}
        .info {{
          display: inline-block;
          width: 80%;
          vertical-align: top;
        }}
        .comment {{
          border: 1px solid #333;
          padding: 5px;
          margin-top: 5px;
          background-color: #f9f9f9;
        }}
      </style>
    </head>
    <body>
      <div class="header">CQI REPORT</div>
      
      <div class="section">
        <h3>Project Information</h3>
        <p><strong>Project Name:</strong> {form_data.get("Project Name", "")}</p>
        <p><strong>Battalion:</strong> {form_data.get("Battalion", "")}</p>
        <p><strong>Start Date:</strong> {form_data.get("Start Date", "")}</p>
        <p><strong>Planned Start:</strong> {form_data.get("Planned Start", "")}</p>
        <p><strong>Planned Completion:</strong> {form_data.get("Planned Completion", "")}</p>
        <p><strong>Actual Completion:</strong> {form_data.get("Actual Completion", "")}</p>
      </div>
      
      <div class="section">
        <h3>Checklist Items</h3>
    """
    for item, info in handbook_info.items():
        score = form_data.get(item, "")
        comment = form_data.get(f"Comment for {item}", "")
        html += f"""
        <div class="item-block">
          <div>
            <span class="info"><span class="item-title">{item.upper()}:</span> {info}</span>
            <span class="score">{score}</span>
          </div>
        """
        if comment.strip():
            html += f"""
          <div class="comment">COMMENT: {comment}</div>
            """
        html += "</div>"
    
    html += f"""
      </div>
      
      <div class="section">
        <h3>Final Results</h3>
        <p><strong>Final Score:</strong> {form_data.get("Final Score", "")} out of 175</p>
        <p><strong>Final Percentage:</strong> {form_data.get("Final Percentage", "")}%</p>
      </div>
    </body>
    </html>
    """
    return html

# -------------------------------------------------------------------
# Main App – Data Input Section
# -------------------------------------------------------------------
st.title("CQI Assessment Tool - Printable Form")
st.markdown("**DEC 2023 - CONSTRUCTION QUALITY INSPECTION (CQI) HANDBOOK**")
st.write("Fill out your project and checklist data. When ready, click the button below to generate a print-friendly form. Then, use your browser’s print function (Ctrl+P / Cmd+P) to print or save as PDF.")

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

# Item 4 – Project Schedule (sample calculation)
st.subheader("Item 4 – Project Schedule")
st.info(handbook_info["Item 4 – Project Schedule"])
st.markdown("Score is based on the difference between planned and actual work-in-place. Exact = 16 pts; Within deviation = 12 pts; Outside deviation = 4 pts.")
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

# For demonstration, we'll loop through sample items for Items 5–29.
sample_items = [
    "Item 5 – Project Management", "Item 6 – QA for 30 NCR Detail Sites", 
    "Item 7 & 8 – FAR/RFI", "Item 9 – DFOW Sheet", "Item 10 – Turnover Projects",
    "Item 11 – Funds Provided", "Item 12 – Estimate at Completion Cost (EAC)",
    "Item 13 – Current Expenditures", "Item 14 – Project Material Status Report (PMSR)",
    "Item 15 – Report Submission", "Item 16 – Materials On-Hand", "Item 17 – DD Form 200",
    "Item 18 – Borrowed Material Tickler File", "Item 19 – Project Brief",
    "Item 20 – Calculate Manday Capability", "Item 21 – Equipment",
    "Item 22 – CASS Spot Check", "Item 23 – Designation Letters",
    "Item 24 – Job Box Review", "Item 25 – Review QC Package",
    "Item 26 – Submittals", "Item 27a – QC Inspection Plan", "Item 27b – QC Inspection",
    "Item 28 – Job Box Review (QC)", "Item 29 – Job Box Review (Safety)"
]
for item in sample_items:
    st.subheader(item)
    st.info(handbook_info.get(item, ""))
    resp = st.text_input("Response (score):", value="Sample Score", key=item)
    comm = st.text_area("Comment (if any):", key=f"Comment for {item}")
    
# For demonstration, set final scores.
final_score = 166
final_percentage = 94.9

# Build the form_data dictionary.
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
    "Item 4 – Project Schedule": str(item4_score),
    "Comment for Item 4": comment_item4,
    "Final Score": final_score,
    "Final Percentage": final_percentage,
}
# (In your full implementation, ensure form_data includes responses for Items 5–29 as well.)

if st.button("Generate Printable Form"):
    html_output = generate_html(form_data, handbook_info)
    components.html(html_output, height=600, scrolling=True)
    st.markdown("### Use your browser's print function (Ctrl+P / Cmd+P) to print or save as PDF.")
