import streamlit as st
import streamlit.components.v1 as components
import datetime

# -------------------------------------------------------------------
# Helper Function
# -------------------------------------------------------------------
def sanitize(text):
    """Replace problematic Unicode dashes with a standard hyphen."""
    if isinstance(text, str):
        return text.replace("\u2013", "-").replace("\u2014", "-")
    return text

# -------------------------------------------------------------------
# Handbook Amplifying Info for Items 1–29
# (Update these strings as needed to match your official CQI Handbook.)
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
# Function to generate a print-friendly HTML form
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
        if str(comment).strip():
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
# Main App – Data Input
# -------------------------------------------------------------------
st.title("CQI Assessment Tool - Printable Form")
st.markdown("**DEC 2023 - CONSTRUCTION QUALITY INSPECTION (CQI) HANDBOOK**")
st.write("Enter your project and checklist data below. When finished, click the 'Generate Printable Form' button and then use your browser's print function (Ctrl+P / Cmd+P) to print or save as PDF.")

# --- Project Information ---
st.header("Project Information")
proj_name = st.text_input("Project Name:")
battalion = st.text_input("Battalion Name:")
start_date = st.date_input("Start Date:")
planned_start = st.date_input("Planned Start Date:")
planned_completion = st.date_input("Planned Completion Date:")
actual_completion = st.date_input("Actual Completion Date:")

# Initialize form_data with project info.
form_data = {
    "Project Name": proj_name,
    "Battalion": battalion,
    "Start Date": str(start_date),
    "Planned Start": str(planned_start),
    "Planned Completion": str(planned_completion),
    "Actual Completion": str(actual_completion)
}

# --- Assessment Inputs ---
st.header("Assessment Inputs")
# Loop through each checklist item defined in handbook_info.
for item in handbook_info:
    st.subheader(item)
    st.info(handbook_info[item])
    # Use number_input for numeric score.
    score = st.number_input(f"Enter score for {item}:", key=item, format="%g")
    comment = st.text_area(f"Enter comment for {item} (if any):", key="Comment for " + item)
    form_data[item] = score
    form_data["Comment for " + item] = comment

# Calculate final score.
# (This calculation assumes that each score is numeric.
# Adjust the logic as needed for your business rules.)
total_score = sum(form_data[item] for item in handbook_info if isinstance(form_data[item], (int, float)))
final_percentage = round(total_score / 175 * 100, 1)
form_data["Final Score"] = total_score
form_data["Final Percentage"] = final_percentage

st.write(f"Final Score: {total_score} out of 175")
st.write(f"Final Percentage: {final_percentage}%")

if st.button("Generate Printable Form"):
    html_output = generate_html(form_data, handbook_info)
    components.html(html_output, height=600, scrolling=True)
    st.markdown("### Use your browser's print function (Ctrl+P / Cmd+P) to print or save as PDF.")
