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
# Update these strings as needed to match your official CQI Handbook.
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
    "Item 11 – Funds Provided": "Are project funds tracked? (4 pts = Monitored; 0 pts = Not tracked)",
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
# Define Perfect Scores for Each Item
# Update these values as required.
# -------------------------------------------------------------------
perfect_scores = {
    "Item 1 – Self Assessment": 2,
    "Item 2 – Self Assessment Submission": 2,
    "Item 3 – Notice to Proceed (NTP)": 4,
    "Item 4 – Project Schedule": 16,
    "Item 5 – Project Management": 2,
    "Item 6 – QA for 30 NCR Detail Sites": 4,
    "Item 7 & 8 – FAR/RFI": 4,
    "Item 9 – DFOW Sheet": 4,
    "Item 10 – Turnover Projects": 4,
    "Item 11 – Funds Provided": 4,
    "Item 12 – Estimate at Completion Cost (EAC)": 4,
    "Item 13 – Current Expenditures": 4,
    "Item 14 – Project Material Status Report (PMSR)": 10,
    "Item 15 – Report Submission": 2,
    "Item 16 – Materials On-Hand": 10,
    "Item 17 – DD Form 200": 2,
    "Item 18 – Borrowed Material Tickler File": 2,
    "Item 19 – Project Brief": 5,
    "Item 20 – Calculate Manday Capability": 6,
    "Item 21 – Equipment": 6,
    "Item 22 – CASS Spot Check": 12,
    "Item 23 – Designation Letters": 5,
    "Item 24 – Job Box Review": 20,
    "Item 25 – Review QC Package": 8,
    "Item 26 – Submittals": 4,
    "Item 27a – QC Inspection Plan": 10,
    "Item 27b – QC Inspection": 5,
    "Item 28 – Job Box Review (QC)": 5,
    "Item 29 – Job Box Review (Safety)": 5,
}

# -------------------------------------------------------------------
# Define Yes/No Items and Their Corresponding Perfect Scores
# -------------------------------------------------------------------
yes_no_items = [
    "Item 1 – Self Assessment",
    "Item 2 – Self Assessment Submission",
    "Item 3 – Notice to Proceed (NTP)",
    "Item 5 – Project Management",
    "Item 11 – Funds Provided",
    "Item 17 – DD Form 200",
    "Item 18 – Borrowed Material Tickler File"
]

yes_no_scores = {
    "Item 1 – Self Assessment": 2,
    "Item 2 – Self Assessment Submission": 2,
    "Item 3 – Notice to Proceed (NTP)": 4,
    "Item 5 – Project Management": 2,
    "Item 11 – Funds Provided": 4,
    "Item 17 – DD Form 200": 2,
    "Item 18 – Borrowed Material Tickler File": 2,
}

# -------------------------------------------------------------------
# Function to generate a print-friendly HTML form (for printing purposes)
# -------------------------------------------------------------------
def generate_html(form_data, handbook_info, perfect_scores):
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
        # Only display the comment block if the numeric score is below the perfect score.
        display_comment = False
        try:
            numeric_score = float(score)
            if numeric_score < perfect_scores.get(item, numeric_score):
                display_comment = bool(comment.strip())
        except (ValueError, TypeError):
            display_comment = False
        
        html += f"""
        <div class="item-block">
          <div>
            <span class="info"><span class="item-title">{item.upper()}:</span> {info}</span>
            <span class="score">{score}</span>
          </div>
        """
        if display_comment:
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
st.title("CQI Assessment Tool")
st.markdown("**DEC 2023 - CONSTRUCTION QUALITY INSPECTION (CQI) HANDBOOK**")
st.write("Fill out your project and checklist data below. For any item that does not achieve the perfect score, a comment is required. First, click the 'Calculate Final Score' button to validate your responses and see your scores. Then, click 'Generate Printable Form' to view a print-friendly version of the assessment.")

# --- Project Information ---
st.header("Project Information")
proj_name = st.text_input("Project Name:", key="proj_name")
battalion = st.text_input("Battalion Name:", key="battalion")
start_date = st.date_input("Start Date:", key="start_date")
planned_start = st.date_input("Planned Start Date:", key="planned_start")
planned_completion = st.date_input("Planned Completion Date:", key="planned_completion")
actual_completion = st.date_input("Actual Completion Date:", key="actual_completion")

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

# For each item, display the item subheader, then show the amplifying info (via st.info),
# then provide input widgets for score and comment.
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
# Calculate Final Score Button
# -------------------------------------------------------------------
if st.button("Calculate Final Score"):
    errors = []
    # Validate required comments for items with score below perfect.
    if form_data["Item 1 – Self Assessment"] != 2 and not form_data.get("Comment for Item 1", "").strip():
        errors.append("Item 1 requires a comment.")
    if form_data["Item 2 – Self Assessment Submission"] != 2 and not form_data.get("Comment for Item 2", "").strip():
        errors.append("Item 2 requires a comment.")
    if form_data["Item 3 – Notice to Proceed (NTP)"] != 4 and not form_data.get("Comment for Item 3", "").strip():
        errors.append("Item 3 requires a comment.")
    # For Item 4, using calculated score (item4_score)
    if 'item4_score' not in st.session_state:
        # Calculate Item 4 score
        total_md = st.session_state.get("total_md", 1000)
        planned_wip = st.session_state.get("planned_wip", 100)
        actual_wip = st.session_state.get("actual_wip", 100)
        if total_md < 1000:
            allowed = 10
        elif total_md < 2000:
            allowed = 5
        else:
            allowed = 2.5
        diff = abs(actual_wip - planned_wip)
        if diff == 0:
            st.session_state.item4_score = 16
        elif diff <= allowed:
            st.session_state.item4_score = 12
        else:
            st.session_state.item4_score = 4
    if st.session_state.item4_score != 16 and not st.session_state.get("Comment for Item 4", "").strip():
        errors.append("Item 4 requires a comment.")
    if form_data["Item 5 – Project Management"] != 2 and not form_data.get("Comment for Item 5", "").strip():
        errors.append("Item 5 requires a comment.")
    if form_data["Item 6 – QA for 30 NCR Detail Sites"] != 4 and not form_data.get("Comment for Item 6", "").strip():
        errors.append("Item 6 requires a comment.")
    if form_data["Item 7 & 8 – FAR/RFI"] != 4 and not form_data.get("Comment for Item 7 & 8", "").strip():
        errors.append("Items 7 & 8 require a comment.")
    if form_data["Item 9 – DFOW Sheet"] != 4 and not form_data.get("Comment for Item 9", "").strip():
        errors.append("Item 9 requires a comment.")
    if form_data["Item 10 – Turnover Projects"] not in [4, "N/A"] and not form_data.get("Comment for Item 10", "").strip():
        errors.append("Item 10 requires a comment.")
    if form_data["Item 11 – Funds Provided"] != 4 and not form_data.get("Comment for Item 11", "").strip():
        errors.append("Item 11 requires a comment.")
    if form_data["Item 12 – Estimate at Completion Cost (EAC)"] != 4 and not form_data.get("Comment for Item 12", "").strip():
        errors.append("Item 12 requires a comment.")
    if form_data["Item 13 – Current Expenditures"] != 4 and not form_data.get("Comment for Item 13", "").strip():
        errors.append("Item 13 requires a comment.")
    if form_data["Item 14 – Project Material Status Report (PMSR)"] != 10 and not form_data.get("Comment for Item 14", "").strip():
        errors.append("Item 14 requires a comment.")
    if form_data["Item 15 – Report Submission"] != 2 and not form_data.get("Comment for Item 15", "").strip():
        errors.append("Item 15 requires a comment.")
    if form_data["Item 16 – Materials On-Hand"] != 10 and not form_data.get("Comment for Item 16", "").strip():
        errors.append("Item 16 requires a comment.")
    if form_data["Item 17 – DD Form 200"] != 2 and not form_data.get("Comment for Item 17", "").strip():
        errors.append("Item 17 requires a comment.")
    if form_data["Item 18 – Borrowed Material Tickler File"] != 2 and not form_data.get("Comment for Item 18", "").strip():
        errors.append("Item 18 requires a comment.")
    if form_data["Item 19 – Project Brief"] != 5 and not form_data.get("Comment for Item 19", "").strip():
        errors.append("Item 19 requires a comment.")
    if form_data["Item 20 – Calculate Manday Capability"] != 6 and not form_data.get("Comment for Item 20", "").strip():
        errors.append("Item 20 requires a comment.")
    if form_data["Item 21 – Equipment"] != 6 and not form_data.get("Comment for Item 21", "").strip():
        errors.append("Item 21 requires a comment.")
    if form_data["Item 22 – CASS Spot Check"] != 12 and not form_data.get("Comment for Item 22", "").strip():
        errors.append("Item 22 requires a comment.")
    if form_data["Item 23 – Designation Letters"] != 5 and not form_data.get("Comment for Item 23", "").strip():
        errors.append("Item 23 requires a comment.")
    if st.session_state.get("deduction24", 0) != 0 and not form_data.get("Comment for Item 24", "").strip():
        errors.append("Item 24 requires a comment for the deduction.")
    if form_data["Item 25 – Review QC Package"] != 8 and not form_data.get("Comment for Item 25", "").strip():
        errors.append("Item 25 requires a comment.")
    if form_data["Item 26 – Submittals"] != 4 and not form_data.get("Comment for Item 26", "").strip():
        errors.append("Item 26 requires a comment.")
    if form_data["Item 27a – QC Inspection Plan"] != 10 and not form_data.get("Comment for Item 27a", "").strip():
        errors.append("Item 27a requires a comment.")
    if form_data["Item 27b – QC Inspection"] != 5 and not form_data.get("Comment for Item 27b", "").strip():
        errors.append("Item 27b requires a comment.")
    if st.session_state.get("deduction28", 0) != 0 and not form_data.get("Comment for Item 28", "").strip():
        errors.append("Item 28 requires a comment for the deduction.")
    if st.session_state.get("deduction29", 0) != 0 and not form_data.get("Comment for Item 29", "").strip():
        errors.append("Item 29 requires a comment for the deduction.")
    
    if errors:
        for err in errors:
            st.error(err)
    else:
        # Convert Yes/No responses to numeric scores.
        score1 = 2 if form_data["Item 1 – Self Assessment"] == "Yes" else 0
        score2 = 2 if form_data["Item 2 – Self Assessment Submission"] == "Yes" else 0
        score3 = 4 if form_data["Item 3 – Notice to Proceed (NTP)"] == "Yes" else 0
        score5 = 2 if form_data["Item 5 – Project Management"] == "Yes" else 0
        score11 = 4 if form_data["Item 11 – Funds Provided"] == "Yes" else 0
        score17 = 2 if form_data["Item 17 – DD Form 200"] == "Yes" else 0
        score18 = 2 if form_data["Item 18 – Borrowed Material Tickler File"] == "Yes" else 0
        
        # Calculate total score (numeric items already stored in form_data).
        total_score = (
            score1 + score2 + score3 + st.session_state.item4_score + score5 +
            form_data["Item 6 – QA for 30 NCR Detail Sites"] + form_data["Item 7 & 8 – FAR/RFI"] + form_data["Item 9 – DFOW Sheet"] +
            (form_data["Item 10 – Turnover Projects"] if form_data["Item 10 – Turnover Projects"] != "N/A" else 0) +
            score11 + form_data["Item 12 – Estimate at Completion Cost (EAC)"] + form_data["Item 13 – Current Expenditures"] +
            form_data["Item 14 – Project Material Status Report (PMSR)"] + score15 + form_data["Item 16 – Materials On-Hand"] +
            score17 + score18 + form_data["Item 19 – Project Brief"] + form_data["Item 20 – Calculate Manday Capability"] +
            form_data["Item 21 – Equipment"] + form_data["Item 22 – CASS Spot Check"] + form_data["Item 23 – Designation Letters"] +
            (20 - st.session_state.get("deduction24", 0)) + form_data["Item 25 – Review QC Package"] +
            form_data["Item 26 – Submittals"] + form_data["Item 27a – QC Inspection Plan"] + form_data["Item 27b – QC Inspection"] +
            (5 - st.session_state.get("deduction28", 0)) + (5 - st.session_state.get("deduction29", 0))
        )
        final_percentage = round(total_score / 175 * 100, 1)
        form_data["Final Score"] = total_score
        form_data["Final Percentage"] = final_percentage

        st.session_state.form_data = form_data
        st.session_state.final_score = total_score
        st.session_state.final_percentage = final_percentage
        st.success("Final Score Calculated!")
        st.write("**Final Score:**", total_score, "out of 175")
        st.write("**Final Percentage:**", final_percentage, "%")

# -------------------------------------------------------------------
# Generate Printable HTML Form Button
# -------------------------------------------------------------------
if st.button("Generate Printable Form"):
    if "form_data" not in st.session_state:
        st.error("Please calculate the final score first.")
    else:
        html_output = generate_html(st.session_state.form_data, handbook_info, perfect_scores)
        components.html(html_output, height=600, scrolling=True)
        st.markdown("### Use your browser's print function (Ctrl+P / Cmd+P) to print or save as PDF.")
