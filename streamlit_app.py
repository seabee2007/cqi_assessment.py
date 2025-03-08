import streamlit as st
import st_components as components  # For st.components.v1.html (or use st.components.v1 directly)
import datetime

# For demonstration, here's some sample form_data and handbook_info.
# In your actual app, these would come from user inputs.
form_data = {
    "Project Name": "Sample Project",
    "Battalion": "1st Battalion",
    "Start Date": "2023-12-01",
    "Planned Start": "2023-12-05",
    "Planned Completion": "2024-03-01",
    "Actual Completion": "2024-02-28",
    "Item 1 – Self Assessment": "Yes",
    "Comment for Item 1": "",
    "Item 2 – Self Assessment Submission": "Yes",
    "Comment for Item 2": "",
    "Item 3 – Notice to Proceed (NTP)": "Yes",
    "Comment for Item 3": "",
    "Item 4 – Project Schedule": "16",
    "Comment for Item 4": "",
    "Item 5 – Project Management": "No",
    "Comment for Item 5": "No CPM is used.",
    "Item 6 – QA for 30 NCR Detail Sites": "3",
    "Comment for Item 6": "Some discrepancies noted.",
    "Item 7 & 8 – FAR/RFI": "4",
    "Comment for Item 7 & 8": "",
    "Item 9 – DFOW Sheet": "4",
    "Comment for Item 9": "",
    "Item 10 – Turnover Projects": "N/A",
    "Comment for Item 10": "",
    "Item 11 – Funds Provided": "Yes",
    "Comment for Item 11": "",
    "Item 12 – Estimate at Completion Cost (EAC)": "4",
    "Comment for Item 12": "",
    "Item 13 – Current Expenditures": "4",
    "Comment for Item 13": "",
    "Item 14 – Project Material Status Report (PMSR)": "10",
    "Comment for Item 14": "",
    "Item 15 – Report Submission": "Yes",
    "Comment for Item 15": "",
    "Item 16 – Materials On-Hand": "10",
    "Comment for Item 16": "",
    "Item 17 – DD Form 200": "Yes",
    "Comment for Item 17": "",
    "Item 18 – Borrowed Material Tickler File": "Yes",
    "Comment for Item 18": "",
    "Item 19 – Project Brief": "3",
    "Comment for Item 19": "Brief is not detailed enough.",
    "Item 20 – Calculate Manday Capability": "6",
    "Comment for Item 20": "",
    "Item 21 – Equipment": "6",
    "Comment for Item 21": "",
    "Item 22 – CASS Spot Check": "12",
    "Comment for Item 22": "",
    "Item 23 – Designation Letters": "5",
    "Comment for Item 23": "",
    "Item 24 – Job Box Review": "Deduction: 0, Score: 20",
    "Comment for Item 24": "",
    "Item 25 – Review QC Package": "8",
    "Comment for Item 25": "",
    "Item 26 – Submittals": "4",
    "Comment for Item 26": "",
    "Item 27a – QC Inspection Plan": "10",
    "Comment for Item 27a": "",
    "Item 27b – QC Inspection": "5",
    "Comment for Item 27b": "",
    "Item 28 – Job Box Review (QC)": "Deduction: 0, Score: 5",
    "Comment for Item 28": "",
    "Item 29 – Job Box Review (Safety)": "Deduction: 1, Score: 4",
    "Comment for Item 29": "Missing one emergency contact.",
    "Final Score": 166,
    "Final Percentage": 94.9
}

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
    "Item 14 – Project Material Status Report (PMSR)": "Inspect PMSR. (10 pts = 100% valid; 8 pts = Acceptable; 4 pts = Discrepancies; 2/0 pts otherwise)",
    "Item 15 – Report Submission": "Are PMSR and EAC reports routed monthly? (2 pts = Yes; 0 pts = No)",
    "Item 16 – Materials On-Hand": "Materials on-hand verification. (10 pts = Organized; 8 pts = Minor issues; 4 pts = Multiple issues; 0 pts = Unsatisfactory)",
    "Item 17 – DD Form 200": "DD Form 200 status. (2 pts = Correct; 0 pts = Not maintained)",
    "Item 18 – Borrowed Material Tickler File": "Borrow log verification. (2 pts = Valid; 0 pts = Not managed)",
    "Item 19 – Project Brief": "Project brief quality. (5 pts = Detailed; 3 pts = Acceptable; 2/0 pts otherwise)",
    "Item 20 – Calculate Manday Capability": "Crew composition & MD capability. (6 pts = Matches; 4/2/0 pts otherwise)",
    "Item 21 – Equipment": "Equipment adequacy. (6 pts = All onsite; 4 pts = Acceptable; 2/0 pts otherwise)",
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
# Generate HTML for printing
# -------------------------------------------------------------------
def generate_html(form_data, handbook_info):
    effective_width = 800  # example pixel width for the content area
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
          width: 15%;
          display: inline-block;
          vertical-align: top;
        }}
        .info {{
          width: 80%;
          display: inline-block;
          vertical-align: top;
        }}
        .comment {{
          border: 1px solid #333;
          padding: 5px;
          margin-top: 5px;
        }}
        table {{
          width: 100%;
          border-collapse: collapse;
        }}
        td, th {{
          border: 1px solid #333;
          padding: 5px;
        }}
      </style>
    </head>
    <body>
      <div class="header">CQI REPORT</div>
      <div class="section">
        <h3>Project Information</h3>
        <p><strong>Project Name:</strong> {form_data.get("Project Name")}</p>
        <p><strong>Battalion:</strong> {form_data.get("Battalion")}</p>
        <p><strong>Start Date:</strong> {form_data.get("Start Date")}</p>
        <p><strong>Planned Start:</strong> {form_data.get("Planned Start")}</p>
        <p><strong>Planned Completion:</strong> {form_data.get("Planned Completion")}</p>
        <p><strong>Actual Completion:</strong> {form_data.get("Actual Completion")}</p>
      </div>
      
      <div class="section">
        <h3>Checklist Items</h3>
    """
    # For each checklist item, add a block with item + info on the left, score on the right, and a comment row if available.
    for item, info in handbook_info.items():
        score = form_data.get(item, "")
        comment = form_data.get(f"Comment for {item}", "")
        html += f"""
        <div class="item-block">
          <div>
            <span class="item-title">{item.upper()}:</span> {info}
            <span class="score"><strong>{score}</strong></span>
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
        <p><strong>Final Score:</strong> {form_data.get("Final Score")} out of 175</p>
        <p><strong>Final Percentage:</strong> {form_data.get("Final Percentage")}%</p>
      </div>
    </body>
    </html>
    """
    return html

# -------------------------------------------------------------------
# Main App – Data Input Section (sample demo)
# -------------------------------------------------------------------
st.title("CQI Assessment Tool - Printable Form")
st.write("This demo generates a print-friendly HTML form. Fill out your project and checklist data, then click 'Generate Printable Form'. You can then use your browser’s print function to print or save as PDF.")

# (In your real app, you'd collect all inputs here; for demo purposes we use the sample form_data above.)
# For demonstration, we assume form_data and handbook_info are already available.
# You might replace this with your Streamlit form code.

if st.button("Generate Printable Form"):
    html_out = generate_html(form_data, handbook_info)
    st.components.v1.html(html_out, height=600, scrolling=True)
    st.markdown("### Use your browser's print functionality (Ctrl+P / Cmd+P) to print or save as PDF.")
