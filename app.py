import streamlit as st
from jinja2 import Environment, FileSystemLoader
from backend import generate_cv, parse_cv_to_json

# --- Page Configuration ---
st.set_page_config(
    page_title="Trad CV - Dynamic Editor",
    page_icon="🛠️",
    layout="wide",
)

# --- Initialize Session State ---
if 'app_state' not in st.session_state:
    st.session_state.app_state = {"armory": {}, "armory_built": False, "api_key": None}

# --- Load Jinja2 Template (still needed for PDF generation) ---
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

# ==============================================================================
# PHASE 1: SETUP (Main Screen) - No changes here
# ==============================================================================
if not st.session_state.app_state.get("armory_built"):
    st.title("Trad CV 📄 Setup")
    st.markdown("Welcome. Let's build your Armory by importing your existing CV. This is a one-time setup.")
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_cv = st.file_uploader("Upload Your CV (PDF or DOCX)", type=['pdf', 'docx'])
    with col2:
        api_key_input = st.text_input("Enter Your Google Gemini API Key", type="password")

    if st.button("Parse CV & Open Editor", use_container_width=True, type="primary"):
        if uploaded_cv and api_key_input:
            with st.spinner("Analyzing your CV..."):
                try:
                    st.session_state.app_state['api_key'] = api_key_input
                    file_bytes = uploaded_cv.getvalue()
                    file_type = uploaded_cv.type.split('/')[1]
                    if 'wordprocessingml' in file_type: file_type = 'docx'
                    parsed_armory = parse_cv_to_json(file_bytes, file_type, api_key_input)
                    st.session_state.app_state['armory'] = parsed_armory
                    st.session_state.app_state['armory_built'] = True
                    st.success("Armory Built! Opening Editor...")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to parse CV. Error: {e}")
        else:
            st.error("Please upload your CV and enter your API key.")
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: grey;'>Built by Dhruvil Raval</p>", unsafe_allow_html=True)

# ==============================================================================
# PHASE 2: THE DYNAMIC EDITOR
# ==============================================================================
else:
    st.title("Trad CV 🛠️ Dynamic Editor")
    st.markdown("---")

    # Create a two-column layout
    col1, col2 = st.columns(2)

    # --- LEFT COLUMN: Target Job and Actions ---
    with col1:
        st.header("🎯 Target Role")
        job_description = st.text_area("Paste the job description here", height=400, label_visibility="collapsed")

        if st.button("🚀 Forge & Update Armory", type="primary", use_container_width=True):
            if not job_description:
                st.error("Please paste a job description.")
            else:
                api_key = st.session_state.app_state['api_key']
                armory = st.session_state.app_state['armory']
                with st.spinner("Executing protocol..."):
                    try:
                        updated_armory_json = generate_cv(armory, job_description, api_key, return_json=True)
                        st.session_state.app_state['armory'] = updated_armory_json
                        st.success("Armory Updated!")
                        st.rerun() # Rerun to reflect AI changes immediately
                    except Exception as e:
                        st.error(f"Forge Failed: {e}")

        pdf_bytes = generate_cv(st.session_state.app_state['armory'], "Final PDF",
                                st.session_state.app_state['api_key'], return_json=False)
        st.download_button(
            label="📄 Download as PDF", data=pdf_bytes,
            file_name=f"{st.session_state.app_state['armory'].get('candidate_name', 'CV').replace(' ', '')}_TradCV.pdf",
            mime="application/pdf", use_container_width=True
        )

    # --- RIGHT COLUMN: The Armory Editor ---
    with col2:
        st.header("✏️ Your Armory (Fully Editable)")
        armory = st.session_state.app_state['armory']

        # Ensure armory substructures exist to prevent errors
        if 'competencies' not in armory: armory['competencies'] = []
        if 'professional_history' not in armory: armory['professional_history'] = []
        if 'awards_leadership' not in armory: armory['awards_leadership'] = {}

        if armory:
            # --- STATIC INFO ---
            armory['candidate_name'] = st.text_input("Full Name", value=armory.get('candidate_name', ''))
            armory['contact'] = st.text_input("Contact Info", value=armory.get('contact', ''))
            armory['education'] = st.text_input("Education", value=armory.get('education', ''))
            st.markdown("---")

            # --- COMPETENCIES (Add/Remove) ---
            st.subheader("Competencies")
            for i, competency in enumerate(armory['competencies']):
                c1, c2 = st.columns([4, 1])
                with c1:
                    competency['title'] = st.text_input("Competency Title", value=competency.get('title', ''), key=f"comp_title_{i}")
                    competency['description'] = st.text_area("Description", value=competency.get('description', ''), key=f"comp_desc_{i}", height=100)
                with c2:
                    st.write(" ") # Spacer for alignment
                    st.write(" ")
                    if st.button("Remove", key=f"remove_comp_{i}", use_container_width=True):
                        armory['competencies'].pop(i)
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Add Competency", use_container_width=True):
                armory['competencies'].append({'title': 'New Competency', 'description': ''})
                st.rerun()
            st.markdown("---")


            # --- PROFESSIONAL HISTORY (Add/Remove) ---
            st.subheader("Professional History")
            for i, job in enumerate(armory['professional_history']):
                p1, p2 = st.columns([4, 1])
                with p1:
                    job['role'] = st.text_input("Role", value=job.get('role', ''), key=f"role_{i}")
                    job['company'] = st.text_input("Company", value=job.get('company', ''), key=f"company_{i}")
                    job['dates'] = st.text_input("Dates", value=job.get('dates', ''), key=f"dates_{i}")
                    accomplishments_text = "\n".join(job.get('accomplishments', []))
                    updated_text = st.text_area("Accomplishments (one per line)", value=accomplishments_text, height=120, key=f"acc_{i}")
                    job['accomplishments'] = [line.strip() for line in updated_text.split('\n') if line.strip()]
                with p2:
                    st.write(" ") # Spacer
                    st.write(" ")
                    if st.button("Remove", key=f"remove_role_{i}", use_container_width=True):
                        armory['professional_history'].pop(i)
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Add Role", use_container_width=True):
                armory['professional_history'].append({'role': '', 'company': '', 'dates': '', 'accomplishments': []})
                st.rerun()
            st.markdown("---")

            # --- AWARDS & LEADERSHIP (Add/Remove) ---
            st.subheader("Awards & Leadership")
            # Iterate over a copy of keys so we can delete from the original dict
            for category in list(armory['awards_leadership'].keys()):
                a1, a2 = st.columns([4, 1])
                with a1:
                    armory['awards_leadership'][category] = st.text_area(
                        label=category, value=armory['awards_leadership'][category], key=f"award_{category}"
                    )
                with a2:
                    st.write(" ") # Spacer
                    st.write(" ")
                    if st.button("Remove", key=f"remove_award_{category}", use_container_width=True):
                        del armory['awards_leadership'][category]
                        st.rerun()

            st.write("Add a new category:")
            n1, n2 = st.columns([3, 1])
            with n1:
                new_category = st.text_input("New Category Name", key="new_award_category_name", label_visibility="collapsed")
            with n2:
                if st.button("Add Category", use_container_width=True):
                    if new_category and new_category not in armory['awards_leadership']:
                        armory['awards_leadership'][new_category] = "Description..."
                        st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: grey; padding-top: 2rem;'>Built with 🚀 by <a href='https://www.linkedin.com/in/dhruvilraval/' target='_blank'>Dhruvil Raval</a></p>",
        unsafe_allow_html=True)