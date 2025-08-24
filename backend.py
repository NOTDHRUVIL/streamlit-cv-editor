import os
import io
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import PyPDF2
import docx

# --- STATIC CONSTANTS ---
CV_CSS = """
@page { size: A4; margin: 1cm; }
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.4; color: #1a1a1a; }
h1 { font-size: 22pt; text-align: left; margin-bottom: 0px; font-weight: 600; letter-spacing: 0; }
p.contact-info { font-size: 9.5pt; text-align: left; margin-top: 0; margin-bottom: 8px; color: #333; }
h2 { font-size: 10.5pt; font-weight: 700; color: #000; border-bottom: 1.5px solid #000; padding-bottom: 1px; margin-top: 12px; margin-bottom: 6px; letter-spacing: 1.5px; text-transform: uppercase; }
p.summary-text { text-align: justify; margin-top: 0; font-size: 10pt; }
ul { padding-left: 17px; margin-top: 3px; list-style-type: disc; }
li { margin-bottom: 5px; padding-left: 3px; text-align: justify; }
li strong { font-weight: 700; }
p.job-header { font-size: 10.5pt; font-weight: 700; margin-top: 8px; margin-bottom: 3px; }
span.company { font-weight: 400; }
"""

STRATEGIC_INTELLIGENCE_MATRIX_TEXT = """
Big Tech / Enterprise (PM Roles):
DNA: User empathy, data-driven decisions, cross-functional leadership, shipping products at scale. Keywords: Roadmap, User Stories, A/B Testing, KPIs, Stakeholders, GTM, Scale. Archetype: "Mini-CEO."
Venture-Backed Startups:
DNA: Ownership, 0-to-1 execution, speed, scrappiness. Keywords: Launch, Iterate, Growth, MVP, User Feedback, Ambiguity, Hustle. Archetype: "Founder-Builder."
Specialized AI Research & Development:
DNA: Technical depth, scientific rigor, novel contributions, pushing state-of-the-art. Keywords: Benchmark, Model, Algorithm, Prototype, Paper, Experiment, SOTA. Archetype: "Pioneer."
Quantitative, HFT, & Proprietary Trading:
DNA: First-principles thinking, quantitative rigor, probabilistic mindset, finding "edge" or "alpha." Keywords: Model, Signal, Probability, Statistics, Alpha, Latency, Python, C++. Archetype: "Intellectual Killer."
Hedge Funds & Investment Management:
DNA: Analytical depth, thesis-driven research, data analysis, generating returns. Keywords: Thesis, Analysis, Valuation, Model, Risk, Portfolio, SQL. Archetype: "Rigorous Thinker."
Investment Banking:
DNA: Extreme work ethic, financial modeling, attention to detail, executing high-stakes transactions. Keywords: DCF, LBO, Valuation, Pitch Deck, M&A, Excel, Transaction. Archetype: "Grinder."
Elite Management & Strategy Consulting:
DNA: Structured problem-solving, hypothesis-led thinking, client-facing communication, driving business impact. Keywords: Framework, Hypothesis, Impact, Case, Deck, Client, Recommendation, MECE. Archetype: "Intellectual Athlete."
Turnaround & Restructuring Consulting:
DNA: Comfort with distress, P&L analysis, operational rigor, making tough decisions under pressure. Keywords: Turnaround, Restructuring, Profitability, Liquidity, Operations. Archetype: "Corporate Surgeon."
"""


# --- CORE FUNCTIONS ---

def parse_cv_to_json(cv_file_bytes, file_type, api_key):
    """
    Uses a robust "Few-Shot" prompt with Gemini's JSON Mode for guaranteed, high-quality parsing,
    including a dictionary for awards_leadership.
    """
    if not api_key: raise ValueError("API Key is required for parsing.")
    genai.configure(api_key=api_key)
    raw_text = ""
    if file_type == "pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(cv_file_bytes))
        for page in pdf_reader.pages: raw_text += page.extract_text()
    elif file_type == "docx":
        doc = docx.Document(io.BytesIO(cv_file_bytes))
        for para in doc.paragraphs: raw_text += para.text + "\n"
    if not raw_text or len(raw_text) < 50: raise ValueError(
        "Could not extract sufficient text from the uploaded CV file.")

    model = genai.GenerativeModel('gemini-2.5-flash')

    parsing_prompt = f"""
    You are an expert, precise CV parsing system. Your only task is to analyze raw CV text and convert it into a valid JSON object. Follow the comprehensive example provided exactly.
    --- EXAMPLE START ---
    CV TEXT:
    '''
    Alex Chen
    London, UK • +44 123 456 7890 • alex.chen@email.com • linkedin.com/in/alexchen
    AWARDS & VENTURES
    Technology: 1st Place, National Cyber Challenge; Top 5%, Kaggle Data Science Bowl.
    Business & Growth: Co-founded a social app, achieving 1M+ downloads.
    EDUCATION
    Imperial College London — MEng Computing (AI), 2024
    EXPERIENCE
    AI Research Intern, QuantumLeap AI, London, UK
    June 2023 - September 2023
    - Designed and implemented a novel reinforcement learning algorithm.
    '''
    JSON OUTPUT:
    {{
      "candidate_name": "Alex Chen",
      "contact": "+44 123 456 7890 | alex.chen@email.com | linkedin.com/in/alexchen",
      "education": "Imperial College London — MEng Computing (AI), 2024",
      "awards_leadership": {{
          "Technology": "1st Place, National Cyber Challenge; Top 5%, Kaggle Data Science Bowl.",
          "Business & Growth": "Co-founded a social app, achieving 1M+ downloads."
      }},
      "professional_history": [
        {{
          "role": "AI Research Intern",
          "company": "QuantumLeap AI",
          "dates": "June 2023 - September 2023",
          "accomplishments": ["- Designed and implemented a novel reinforcement learning algorithm."]
        }}
      ]
    }}
    --- EXAMPLE END ---
    Now, apply the exact same thought process to the following CV text. Your output must be ONLY the final JSON object.
    For the "awards_leadership" key, identify logical categories from the CV text and group achievements. If no awards are found, return an empty dictionary {{}}.
    For "accomplishments", always return a list of strings.
    --- ACTUAL CV TEXT TO PARSE ---
    '''
    {raw_text}
    '''
    """

    generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    try:
        response = model.generate_content(parsing_prompt, generation_config=generation_config,
                                          safety_settings=safety_settings)
        return json.loads(response.text)
    except Exception as e:
        if 'response' in locals():
            try:
                print("AI Response Parts:", response.parts)
            except:
                print("Could not retrieve AI response parts.")
        raise ValueError(f"The AI failed to generate a valid JSON response during parsing. Error: {e}")


def format_armory_for_prompt(armory_data):
    """Helper function to format the user's current armory into a string for the AI prompt."""
    output = f"Candidate Name: {armory_data.get('candidate_name', '')}\n"
    output += f"Contact: {armory_data.get('contact', '')}\n"
    output += f"Education: {armory_data.get('education', '')}\n"

    awards = armory_data.get('awards_leadership', {})
    if isinstance(awards, dict):
        awards_text = "\n".join([f"{cat}: {val}" for cat, val in awards.items()])
    else:
        awards_text = str(awards)
    output += f"Awards & Leadership:\n{awards_text}\n"

    output += "Professional History (Verifiable Ground Truth):\n"
    if armory_data.get('professional_history'):
        for job in armory_data.get('professional_history', []):
            accomplishments = job.get('accomplishments', [])
            accomplishments_text = "\n".join(accomplishments)
            output += f"Company: {job.get('company', '')} | Official Role: {job.get('role', '')} | Dates: {job.get('dates', '')} | Accomplishments: {accomplishments_text}\n"
    return output.strip()


def build_intelligent_json_prompt(armory_data, job_description):
    """Builds the intelligent 'Chain-of-Thought' prompt for the AI."""
    armory_text = format_armory_for_prompt(armory_data)
    latest_two_roles = armory_data.get('professional_history', [])[:2]
    latest_roles_text = " and ".join(
        [f"'{job.get('role', '')} at {job.get('company', '')}'" for job in latest_two_roles])
    return f"""
    You are an ELITE career strategist. Your task is to analyze the provided data and generate a single JSON object to build a one-page CV.
    YOUR THOUGHT PROCESS (Mental Sandbox):
    1. Analyze Target: Read the Target Job Description. Identify its core archetype from the Strategic Intelligence Matrix and extract the top 3-5 most critical keywords/skills.
    2. Formulate Narrative: Based on this analysis, create a unique "Candidate Narrative."
    3. Select Experiences: The two most recent roles ({latest_roles_text}) are mandatory. From the rest of the Armory, select ONLY 2-3 additional experiences that most powerfully support the unique Candidate Narrative.
    4. Weaponize Accomplishments: For every selected experience, rewrite the accomplishment bullet points to aggressively highlight the Key Skills and prove the Candidate Narrative.
    FINAL OUTPUT: After your thought process, generate a single JSON object that executes your strategy.

    NON-NEGOTIABLE RULES FOR THE JSON:
    1. The "summary_text" MUST be a single, dense, one-line sentence that embodies the Candidate Narrative.
    2. "professional_history" MUST include the mandatory latest two roles, plus your other strategic selections.
    3. Each job in "professional_history" MUST have a maximum of TWO accomplishment bullet points as a list of strings.
    4. For "awards_leadership", autonomously create 1-3 logical category names and group achievements from the Armory.

    JSON OUTPUT STRUCTURE:
    {{
      "summary_text": "A powerful, tailored one-line summary.",
      "competencies": [ {{ "title": "...", "description": "..." }} ],
      "professional_history": [ {{ "role": "...", "company": "...", "dates": "...", "accomplishments": ["...", "..."] }} ],
      "awards_leadership": {{ "Category 1": "...", "Category 2": "..." }}
    }}
    [STRATEGIC INTELLIGENCE MATRIX]
    {STRATEGIC_INTELLIGENCE_MATRIX_TEXT}
    [THE ARMORY - VERIFIED CANDIDATE HISTORY]
    {armory_text}
    [TARGET JOB DESCRIPTION]
    {job_description}
    """


def generate_cv(armory_data, job_description, api_key, return_json=False):
    """
    Handles both forging new JSON content and rendering a given armory to PDF.
    """
    if not api_key: raise ValueError("API Key is required.")
    genai.configure(api_key=api_key)
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')

    try:
        if return_json:
            # --- AI FORGING LOGIC ---
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = build_intelligent_json_prompt(armory_data, job_description)
            generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            response = model.generate_content(prompt, generation_config=generation_config,
                                              safety_settings=safety_settings)
            updated_json_content = json.loads(response.text)

            # Merge AI content with user's static info to create the final armory
            final_armory = {
                "candidate_name": armory_data.get('candidate_name'),
                "contact": armory_data.get('contact'),
                "education": armory_data.get('education'),
                "summary_text": updated_json_content.get("summary_text"),
                "competencies": updated_json_content.get("competencies"),
                "professional_history": updated_json_content.get("professional_history"),
                "awards_leadership": updated_json_content.get("awards_leadership"),
            }
            return final_armory
        else:
            # --- PDF RENDERING LOGIC ---
            # Ensure accomplishments are always a list before rendering
            if armory_data.get("professional_history"):
                for job in armory_data["professional_history"]:
                    if isinstance(job.get("accomplishments"), str):
                        job["accomplishments"] = [line.strip().lstrip('- ') for line in
                                                  job["accomplishments"].split('\n') if line.strip()]

            render_data = {
                "summary": {
                    "name": armory_data.get('candidate_name'), "contact": armory_data.get('contact'),
                    "education": armory_data.get('education'), "summary_text": armory_data.get('summary_text')
                },
                "competencies": armory_data.get('competencies', []),
                "professional_history": armory_data.get('professional_history', []),
                "awards_leadership": armory_data.get('awards_leadership', {})
            }
            html_content = template.render(**render_data)
            html = HTML(string=html_content)
            css = CSS(string=CV_CSS)
            return html.write_pdf(stylesheets=[css])
    except Exception as e:
        if 'response' in locals():
            try:
                print("AI Response Parts:", response.parts)
            except:
                print("Could not retrieve AI response parts.")
        raise e