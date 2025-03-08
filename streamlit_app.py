import streamlit as st
import streamlit.components.v1 as components
import datetime
import io
import base64
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# -------------------------------------------------------------------
# Print-specific CSS (injected at the top)
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Only hide elements with the "no-print" class when printing */
    @media print {
        .no-print {
            display: none;
        }
        body {
            margin: 20px;
            font-size: 12pt;
        }
        .reportview-container .main .block-container {
            padding: 0;
        }
        /* Force a page break before each comment page */
        .page-break {
            page-break-before: always;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Top Section: Display Final Score Data if Available
# -------------------------------------------------------------------
if "final_score" in st.session_state:
    st.markdown(
        f"""
        <div style="background-color:#f0f2f6; padding:10px; margin-bottom:20px;">
            <h3>Final Score: {st.session_state.final_score} out of 175</h3>
            <h4>Final Percentage: {st.session_state.final_percentage}%</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
def sanitize(text):
    """Replace problematic Unicode dashes with a standard hyphen."""
    if isinstance(text, str):
        return text.replace("\u2013", "-").replace("\u2014", "-")
    return text

def image_to_base64(image_array):
    """Convert a NumPy image array to a base64 encoded PNG."""
    if image_array is None:
        return ""
    im = Image.fromarray((image_array).astype('uint8'))
    buff = io.BytesIO()
    im.save(buff, format="PNG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

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
# Main App – Data Input Section
# -------------------------------------------------------------------
st.title("Construction Quality Inspection (CQI) Assessment Tool")
st.markdown("**DEC 2023 - CONSTRUCTION QUALITY INSPECTION (CQI) HANDBOOK**")
st.write("Fill out the fields below. For any item that does not achieve the perfect score, a comment is required. In the final PDF, each item will display its question and amplifying info in one box with your numerical score in a narrow, centered column. If you provide any comments, they will appear on a separate page by line item.")

# --- Project Information ---
st.header("Project Information")
proj_name_input = st.text_input("Project Name:", key="proj_name_input")
battalion_input = st.text_input("Battalion:", key="battalion_input")
oic_name_input = st.text_input("OIC:", key="oic_name_input")
aoic_input = st.text_input("AOIC:", key="aoic_input")
start_date = st.date_input("Start Date:", key="start_date_input")
planned_start = st.date_input("Planned Start Date:", key="planned_start_input")
planned_completion = st.date_input("Planned Completion Date:", key="planned_completion_input")
actual_completion = st.date_input("Actual Completion Date:", key="actual_completion_input")

# --- Assessment Inputs ---
st.header("Assessment Inputs")

# Item 1
st.subheader("Item 1 – Self Assessment")
st.info(handbook_info["Item 1 – Self Assessment"])
item1 = st.radio("Response:", options=["Yes", "No"], key="item1_response")
comment_item1 = st.text_area("Comment (if not perfect):", key="item1_comment") if item1 != "Yes" else ""

# Item 2
st.subheader("Item 2 – Self Assessment Submission")
st.info(handbook_info["Item 2 – Self Assessment Submission"])
item2 = st.radio("Response:", options=["Yes", "No"], key="item2_response")
comment_item2 = st.text_area("Comment (if not perfect):", key="item2_comment") if item2 != "Yes" else ""

# Item 3
st.subheader("Item 3 – Notice to Proceed (NTP)")
st.info(handbook_info["Item 3 – Notice to Proceed (NTP)"])
item3 = st.radio("Response:", options=["Yes", "No"], key="item3_response")
comment_item3 = st.text_area("Comment (if not perfect):", key="item3_comment") if item3 != "Yes" else ""

# Item 4 – Project Schedule (calculated score)
st.subheader("Item 4 – Project Schedule")
st.info(handbook_info["Item 4 – Project Schedule"])
st.markdown(
    "Score is based on the difference between planned and actual work-in-place.\n"
    "Exact = 16 pts; Within deviation = 12 pts; Outside deviation = 4 pts."
)
total_md = st.number_input("Total Project Mandays:", value=1000, step=1, key="total_md_input")
planned_wip = st.number_input("Planned Work-in-Place (%)", value=100, step=1, key="planned_wip_input")
actual_wip = st.number_input("Actual Work-in-Place (%)", value=100, step=1, key="actual_wip_input")
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
comment_item4 = st.text_area("Comment (if not perfect):", key="item4_comment") if item4_score != 16 else ""

# Item 5 – Project Management
st.subheader("Item 5 – Project Management")
st.info(handbook_info["Item 5 – Project Management"])
item5 = st.radio("Response:", options=["Yes", "No"], key="item5_response")
comment_item5 = st.text_area("Comment (if not perfect):", key="item5_comment") if item5 != "Yes" else ""

# Item 6 – QA for 30 NCR Detail Sites
st.subheader("Item 6 – QA for 30 NCR Detail Sites")
st.info(handbook_info["Item 6 – QA for 30 NCR Detail Sites"])
item6 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item6_score")
comment_item6 = st.text_area("Comment (if not perfect):", key="item6_comment") if item6 != 4 else ""

# Item 7 & 8 – FAR/RFI
st.subheader("Item 7 & 8 – FAR/RFI")
st.info(handbook_info["Item 7 & 8 – FAR/RFI"])
item78 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item78_score")
comment_item78 = st.text_area("Comment (if not perfect):", key="item78_comment") if item78 != 4 else ""

# Item 9 – DFOW Sheet
st.subheader("Item 9 – DFOW Sheet")
st.info(handbook_info["Item 9 – DFOW Sheet"])
item9 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item9_score")
comment_item9 = st.text_area("Comment (if not perfect):", key="item9_comment") if item9 != 4 else ""

# Item 10 – Turnover Projects
st.subheader("Item 10 – Turnover Projects")
st.info(handbook_info["Item 10 – Turnover Projects"])
item10 = st.selectbox("Select score:", options=["N/A", 4, 0], key="item10_score")
comment_item10 = st.text_area("Comment (if not perfect):", key="item10_comment") if item10 not in ["N/A", 4] else ""

# Item 11 – Funds Provided
st.subheader("Item 11 – Funds Provided")
st.info(handbook_info["Item 11 – Funds Provided"])
item11 = st.radio("Response:", options=["Yes", "No"], key="item11_response")
comment_item11 = st.text_area("Comment (if not perfect):", key="item11_comment") if item11 != "Yes" else ""

# Item 12 – Estimate at Completion Cost (EAC)
st.subheader("Item 12 – Estimate at Completion Cost (EAC)")
st.info(handbook_info["Item 12 – Estimate at Completion Cost (EAC)"])
item12 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item12_score")
comment_item12 = st.text_area("Comment (if not perfect):", key="item12_comment") if item12 != 4 else ""

# Item 13 – Current Expenditures
st.subheader("Item 13 – Current Expenditures")
st.info(handbook_info["Item 13 – Current Expenditures"])
item13 = st.selectbox("Select score:", options=[4, 3, 2, 0], key="item13_score")
comment_item13 = st.text_area("Comment (if not perfect):", key="item13_comment") if item13 != 4 else ""

# Item 14 – Project Material Status Report (PMSR)
st.subheader("Item 14 – Project Material Status Report (PMSR)")
st.info(handbook_info["Item 14 – Project Material Status Report (PMSR)"])
item14 = st.selectbox("Select score:", options=[10, 8, 4, 2, 0], key="item14_score")
comment_item14 = st.text_area("Comment (if not perfect):", key="item14_comment") if item14 != 10 else ""

# Item 15 – Report Submission
st.subheader("Item 15 – Report Submission")
st.info(handbook_info["Item 15 – Report Submission"])
item15 = st.radio("Response:", options=["Yes", "No"], key="item15_response")
comment_item15 = st.text_area("Comment (if not perfect):", key="item15_comment") if item15 != "Yes" else ""

# Item 16 – Materials On-Hand
st.subheader("Item 16 – Materials On-Hand")
st.info(handbook_info["Item 16 – Materials On-Hand"])
item16 = st.selectbox("Select score:", options=[10, 8, 4, 0], key="item16_score")
comment_item16 = st.text_area("Comment (if not perfect):", key="item16_comment") if item16 != 10 else ""

# Item 17 – DD Form 200
st.subheader("Item 17 – DD Form 200")
st.info(handbook_info["Item 17 – DD Form 200"])
item17 = st.radio("Response:", options=["Yes", "No"], key="item17_response")
comment_item17 = st.text_area("Comment (if not perfect):", key="item17_comment") if item17 != "Yes" else ""

# Item 18 – Borrowed Material Tickler File
st.subheader("Item 18 – Borrowed Material Tickler File")
st.info(handbook_info["Item 18 – Borrowed Material Tickler File"])
item18 = st.radio("Response:", options=["Yes", "No"], key="item18_response")
comment_item18 = st.text_area("Comment (if not perfect):", key="item18_comment") if item18 != "Yes" else ""

# Item 19 – Project Brief
st.subheader("Item 19 – Project Brief")
st.info(handbook_info["Item 19 – Project Brief"])
item19 = st.selectbox("Select score:", options=[5, 3, 2, 0], key="item19_score")
comment_item19 = st.text_area("Comment (if not perfect):", key="item19_comment") if item19 != 5 else ""

# Item 20 – Calculate Manday Capability
st.subheader("Item 20 – Calculate Manday Capability")
st.info(handbook_info["Item 20 – Calculate Manday Capability"])
item20 = st.selectbox("Select score:", options=[6, 4, 2, 0], key="item20_score")
comment_item20 = st.text_area("Comment (if not perfect):", key="item20_comment") if item20 != 6 else ""

# Item 21 – Equipment
st.subheader("Item 21 – Equipment")
st.info(handbook_info["Item 21 – Equipment"])
item21 = st.selectbox("Select score:", options=[6, 4, 2, 0], key="item21_score")
comment_item21 = st.text_area("Comment (if not perfect):", key="item21_comment") if item21 != 6 else ""

# Item 22 – CASS Spot Check
st.subheader("Item 22 – CASS Spot Check")
st.info(handbook_info["Item 22 – CASS Spot Check"])
item22 = st.selectbox("Select score:", options=[12, 8, 4, 0], key="item22_score")
comment_item22 = st.text_area("Comment (if not perfect):", key="item22_comment") if item22 != 12 else ""

# Item 23 – Designation Letters
st.subheader("Item 23 – Designation Letters")
st.info(handbook_info["Item 23 – Designation Letters"])
item23 = st.selectbox("Select score:", options=[5, 3, 0], key="item23_score")
comment_item23 = st.text_area("Comment (if not perfect):", key="item23_comment") if item23 != 5 else ""

# Item 24 – Job Box Review
st.subheader("Item 24 – Job Box Review")
st.info(handbook_info["Item 24 – Job Box Review"])
item24 = st.selectbox("Select score (20 is perfect; deductions apply):", options=[20, 0], key="item24_score")
deduction24 = st.number_input("Enter deduction for Item 24 (0 to 20):", min_value=0, max_value=20, value=0, step=1, key="deduction24_input")
comment_item24 = st.text_area("Comment (if deduction applied):", key="item24_comment") if deduction24 != 0 else ""

# Item 25 – Review QC Package
st.subheader("Item 25 – Review QC Package")
st.info(handbook_info["Item 25 – Review QC Package"])
item25 = st.selectbox("Select score:", options=[8, 6, 4, 0], key="item25_score")
comment_item25 = st.text_area("Comment (if not perfect):", key="item25_comment") if item25 != 8 else ""

# Item 26 – Submittals
st.subheader("Item 26 – Submittals")
st.info(handbook_info["Item 26 – Submittals"])
item26 = st.selectbox("Select score:", options=[4, 2, 0], key="item26_score")
comment_item26 = st.text_area("Comment (if not perfect):", key="item26_comment") if item26 != 4 else ""

# Item 27a – QC Inspection Plan
st.subheader("Item 27a – QC Inspection Plan")
st.info(handbook_info["Item 27a – QC Inspection Plan"])
item27a = st.selectbox("Select score:", options=[10, 7, 3, 0], key="item27a_score")
comment_item27a = st.text_area("Comment (if not perfect):", key="item27a_comment") if item27a != 10 else ""

# Item 27b – QC Inspection
st.subheader("Item 27b – QC Inspection")
st.info(handbook_info["Item 27b – QC Inspection"])
item27b = st.selectbox("Select score:", options=[5, 0], key="item27b_score")
comment_item27b = st.text_area("Comment (if not perfect):", key="item27b_comment") if item27b != 5 else ""

# Item 28 – Job Box Review (QC)
st.subheader("Item 28 – Job Box Review (QC)")
st.info(handbook_info["Item 28 – Job Box Review (QC)"])
deduction28 = st.number_input("Enter deduction for Item 28 (0 to 5):", min_value=0, max_value=5, value=0, step=1, key="deduction28_input")
comment_item28 = st.text_area("Comment (if deduction applied):", key="item28_comment") if deduction28 != 0 else ""

# Item 29 – Job Box Review (Safety)
st.subheader("Item 29 – Job Box Review (Safety)")
st.info(handbook_info["Item 29 – Job Box Review (Safety)"])
deduction29 = st.number_input("Enter deduction for Item 29 (0 to 5):", min_value=0, max_value=5, value=0, step=1, key="deduction29_input")
comment_item29 = st.text_area("Comment (if deduction applied):", key="item29_comment") if deduction29 != 0 else ""

# --- Calculate Final Score ---
if st.button("Calculate Final Score", key="calculate_final_score"):
    errors = []
    if item1 != "Yes" and not comment_item1.strip():
        errors.append("Item 1 requires a comment.")
    # ... additional validations for other items ...
    
    if errors:
        for err in errors:
            st.error(err)
    else:
        score1 = 2 if item1 == "Yes" else 0
        score2 = 2 if item2 == "Yes" else 0
        score3 = 4 if item3 == "Yes" else 0
        score5 = 2 if item5 == "Yes" else 0
        # For items 6, 7&8, assume numeric values are selected:
        score6 = item6
        score78 = item78
        # For demonstration, the total score will be calculated with available items:
        total_score = (
            score1 + score2 + score3 + item4_score + score5 +
            score6 + score78 +
            0  # Placeholder for items 9-29, you should adjust accordingly.
        )
        final_percentage = round(total_score / 175 * 100, 1)
       
        st.session_state.final_score = total_score
        st.session_state.final_percentage = final_percentage
        
        st.success("Final Score Calculated!")
        st.write("**Final Score:**", total_score, "out of 175")
        st.write("**Final Percentage:**", final_percentage, "%")

# --- Signature Blocks Section ---
default_canvas = {"background": "#FFF", "objects": []}

with st.form("signature_form"):
    st.header("Signatures")
    
    st.markdown("#### OIC Signature")
    canvas_result_oic = st_canvas(
        fill_color="rgba(255,165,0,0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFF",
        height=150,
        width=500,
        drawing_mode="freedraw",
        key="oic_signature",
        initial_drawing=st.session_state.get("oic_signature_data", default_canvas)
    )
    
    st.markdown("#### 30 NCR Signature")
    canvas_result_30ncr = st_canvas(
        fill_color="rgba(255,165,0,0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFF",
        height=150,
        width=500,
        drawing_mode="freedraw",
        key="ncr_signature",
        initial_drawing=st.session_state.get("ncr_signature_data", default_canvas)
    )
    
    submit_signatures = st.form_submit_button("Save Signatures")
    
    if submit_signatures:
        st.session_state.oic_signature_data = canvas_result_oic.json_data
        st.session_state.ncr_signature_data = canvas_result_30ncr.json_data
        st.success("Signatures Saved!")

if st.button("Print Full Report", key="print_full_report"):
    # Retrieve final score data
    final_score = st.session_state.get("final_score", "N/A")
    final_percentage = st.session_state.get("final_percentage", "N/A")
    
    # Retrieve project information
    project_name = proj_name_input if proj_name_input else "N/A"
    battalion = battalion_input if battalion_input else "N/A"
    oic_name = oic_name_input if oic_name_input else "N/A"
    aoic = aoic_input if aoic_input else "N/A"
    start = start_date.strftime("%Y-%m-%d") if isinstance(start_date, datetime.date) else start_date
    planned_start_str = planned_start.strftime("%Y-%m-%d") if isinstance(planned_start, datetime.date) else planned_start
    planned_completion_str = planned_completion.strftime("%Y-%m-%d") if isinstance(planned_completion, datetime.date) else planned_completion
    actual_completion_str = actual_completion.strftime("%Y-%m-%d") if isinstance(actual_completion, datetime.date) else actual_completion
    
    # Convert signature canvas image data to base64 images
    oic_base64 = image_to_base64(canvas_result_oic.image_data)
    ncr_base64 = image_to_base64(canvas_result_30ncr.image_data)
    
    # Build an HTML table for assessment items (Items 1-29)
    assessment_rows = f"""
      <tr>
        <td>Item 1 – Self Assessment</td>
        <td>{'2' if item1=='Yes' else '0'}</td>
        
      </tr>
      <tr>
        <td>Item 2 – Self Assessment Submission</td>
        <td>{'2' if item2=='Yes' else '0'}</td>
        
      </tr>
      <tr>
        <td>Item 3 – Notice to Proceed (NTP)</td>
        <td>{'4' if item3=='Yes' else '0'}</td>
        
      </tr>
      <tr>
        <td>Item 4 – Project Schedule</td>
        <td>{item4_score}</td>
        
      </tr>
      <tr>
        <td>Item 5 – Project Management</td>
        <td>{'2' if item5=='Yes' else '0'}</td>
        
      </tr>
      <tr>
        <td>Item 6 – QA for 30 NCR Detail Sites</td>
        <td>{item6}</td>
        
      </tr>
      <tr>
        <td>Item 7 &amp; 8 – FAR/RFI</td>
        <td>{item78}</td>
        
      </tr>
      <tr>
        <td>Item 9 – DFOW Sheet</td>
        <td>{item9}</td>
        
      </tr>
      <tr>
        <td>Item 10 – Turnover Projects</td>
        <td>{item10 if item10!="N/A" else "N/A"}</td>
        
      </tr>
      <tr>
        <td>Item 11 – Funds Provided</td>
        <td>{'4' if item11=='Yes' else '0'}</td>
        
      </tr>
      <tr>
        <td>Item 12 – Estimate at Completion Cost (EAC)</td>
        <td>{item12}</td>
        
      </tr>
      <tr>
        <td>Item 13 – Current Expenditures</td>
        <td>{item13}</td>
        
      </tr>
      <tr>
        <td>Item 14 – Project Material Status Report (PMSR)</td>
        <td>{item14}</td>
        
      </tr>
      <tr>
        <td>Item 15 – Report Submission</td>
        <td>{'2' if item15=='Yes' else '0'}</td>
       
      </tr>
      <tr>
        <td>Item 16 – Materials On-Hand</td>
        <td>{item16}</td>
       
      </tr>
      <tr>
        <td>Item 17 – DD Form 200</td>
        <td>{'2' if item17=='Yes' else '0'}</td>
        
      </tr>
      <tr>
        <td>Item 18 – Borrowed Material Tickler File</td>
        <td>{'2' if item18=='Yes' else '0'}</td>
        
      </tr>
      <tr>
        <td>Item 19 – Project Brief</td>
        <td>{item19}</td>
       
      </tr>
      <tr>
        <td>Item 20 – Calculate Manday Capability</td>
        <td>{item20}</td>
      
      </tr>
      <tr>
        <td>Item 21 – Equipment</td>
        <td>{item21}</td>
        
      </tr>
      <tr>
        <td>Item 22 – CASS Spot Check</td>
        <td>{item22}</td>
       
      </tr>
      <tr>
        <td>Item 23 – Designation Letters</td>
        <td>{item23}</td>
        
      </tr>
      <tr>
        <td>Item 24 – Job Box Review</td>
        <td>{20 - deduction24}</td>
       
      </tr>
      <tr>
        <td>Item 25 – Review QC Package</td>
        <td>{item25}</td>
        
      </tr>
      <tr>
        <td>Item 26 – Submittals</td>
        <td>{item26}</td>
       
      </tr>
      <tr>
        <td>Item 27a – QC Inspection Plan</td>
        <td>{item27a}</td>
       
      </tr>
      <tr>
        <td>Item 27b – QC Inspection</td>
        <td>{item27b}</td>
      
      </tr>
      <tr>
        <td>Item 28 – Job Box Review (QC)</td>
        <td>{5 - deduction28}</td>
        
      </tr>
      <tr>
        <td>Item 29 – Job Box Review (Safety)</td>
        <td>{5 - deduction29}</td>
        
      </tr>
    """
    
    # Build the comments section: each comment will start on a new page.
    # Only include comments that are non-empty.
    comment_sections = ""
    comments_list = [
        ("Item 1 – Self Assessment", comment_item1),
        ("Item 2 – Self Assessment Submission", comment_item2),
        ("Item 3 – Notice to Proceed (NTP)", comment_item3),
        ("Item 4 – Project Schedule", comment_item4),
        ("Item 5 – Project Management", comment_item5),
        ("Item 6 – QA for 30 NCR Detail Sites", comment_item6),
        ("Item 7 &amp; 8 – FAR/RFI", comment_item78),
        ("Item 9 – DFOW Sheet", comment_item9),
        ("Item 10 – Turnover Projects", comment_item10),
        ("Item 11 – Funds Provided", comment_item11),
        ("Item 12 – Estimate at Completion Cost (EAC)", comment_item12),
        ("Item 13 – Current Expenditures", comment_item13),
        ("Item 14 – Project Material Status Report (PMSR)", comment_item14),
        ("Item 15 – Report Submission", comment_item15),
        ("Item 16 – Materials On-Hand", comment_item16),
        ("Item 17 – DD Form 200", comment_item17),
        ("Item 18 – Borrowed Material Tickler File", comment_item18),
        ("Item 19 – Project Brief", comment_item19),
        ("Item 20 – Calculate Manday Capability", comment_item20),
        ("Item 21 – Equipment", comment_item21),
        ("Item 22 – CASS Spot Check", comment_item22),
        ("Item 23 – Designation Letters", comment_item23),
        ("Item 24 – Job Box Review", comment_item24),
        ("Item 25 – Review QC Package", comment_item25),
        ("Item 26 – Submittals", comment_item26),
        ("Item 27a – QC Inspection Plan", comment_item27a),
        ("Item 27b – QC Inspection", comment_item27b),
        ("Item 28 – Job Box Review (QC)", comment_item28),
        ("Item 29 – Job Box Review (Safety)", comment_item29)
    ]
    for item, comment in comments_list:
        if comment and comment.strip():
            comment_sections += f"""
            <div class="page-break">
              <h3>{item} - Comment</h3>
              <p>{comment}</p>
            </div>
            """
    
    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 20px; }}
          table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
          th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
          th {{ background-color: #f2f2f2; }}
          .signature {{ border: 1px solid #000; width: 500px; height: 150px; display: block; margin-bottom: 20px; }}
          h2, h3, h4 {{ text-align: center; }}
          .page-break {{ page-break-before: always; }}
        </style>
      </head>
      <body>
        <h2>Construction Quality Inspection Report</h2>
        <h3>Project Information</h3>
        <p><strong>Project Name:</strong> {project_name}</p>
        <p><strong>Battalion:</strong> {battalion}</p>
        <p><strong>OIC:</strong> {oic_name}</p>
        <p><strong>AOIC:</strong> {aoic}</p>
        <p><strong>Start Date:</strong> {start}</p>
        <p><strong>Planned Start:</strong> {planned_start_str}</p>
        <p><strong>Planned Completion:</strong> {planned_completion_str}</p>
        <p><strong>Actual Completion:</strong> {actual_completion_str}</p>
        
        <h3>Assessment Details</h3>
        <table>
          <tr>
            <th>Item</th>
            <th>Score</th>
            <th>Comment</th>
          </tr>
          {assessment_rows}
        </table>
        
        <h3>Final Score</h3>
        <p><strong>Final Score:</strong> {final_score} out of 175</p>
        <p><strong>Final Percentage:</strong> {final_percentage}%</p>
        
        <h3>Signatures</h3>
        <h4>OIC Signature:</h4>
        <img src="data:image/png;base64,{oic_base64}" class="signature"/>
        <h4>30 NCR Signature:</h4>
        <img src="data:image/png;base64,{ncr_base64}" class="signature"/>
        
        <!-- Page break before starting comments -->
        <div class="page-break"></div>
        
        <h3>Comments</h3>
        {comment_sections}
        
        <script>
          window.onload = function() {{
             window.print();
          }};
        </script>
      </body>
    </html>
    """
    components.html(html_content, height=900)

