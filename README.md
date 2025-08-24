# Trad CV - Dynamic AI-Powered CV Editor

> Stop editing a document. Start managing an armory.

Trad CV is a Streamlit web application that transforms the traditional resume-writing process. Instead of a static document, your professional history becomes a structured "Armory." An AI strategist then forges a bespoke, one-page CV from this armory, tailored specifically to the job you want.


*(You should replace this with a screenshot of your app in action!)*

## Introduction

The standard approach to CVs is broken. Manually tailoring a document for every job application is tedious, error-prone, and inefficient. This tool introduces a new paradigm:

1.  **The Armory:** Your complete professional history—every role, skill, and accomplishment—is parsed into a structured database. This is your ground truth.
2.  **The Strategist:** Google's Gemini AI acts as an elite career strategist. It analyzes a target job description, understands its core requirements, and formulates a winning narrative.
3.  **The Forged CV:** The AI selects the most relevant experiences from your Armory and rewrites them to perfectly align with the target role, producing a powerful, interview-winning CV in seconds.

## Core Features

*   **🤖 AI-Powered Parsing:** Upload your existing CV (`.pdf` or `.docx`), and the app will automatically parse it into a structured, editable armory.
*   **🎯 Strategic Generation:** Paste a job description, and the AI will generate a new summary, select the most relevant roles, and rewrite accomplishment bullet points to match the target.
*   **🛠️ Fully Dynamic Editor:** Manually add, remove, or edit any part of your armory. You have full control to add new roles, competencies, awards, or remove entire sections.
*   **📄 PDF Export:** Download the final, perfectly formatted one-page CV as a PDF, ready to be submitted.
*   **✨ Clean Interface:** A simple, two-column layout provides a focused workspace for targeting roles and editing your master profile.

## Tech Stack

*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **Backend:** Python
*   **AI & Language Model:** [Google Gemini API](https://ai.google.dev/)
*   **PDF Generation:** [WeasyPrint](https://weasyprint.org/)
*   **File Parsing:** `PyPDF2`, `python-docx`
*   **Templating:** `Jinja2`

## How It Works

1.  **One-Time Setup:** On first launch, you upload your most recent CV. The AI parses it into the "Armory."
2.  **Target a Role:** In the left column, paste the full job description for a role you are interested in.
3.  **Forge the CV:** Click the "Forge & Update Armory" button. The Gemini AI analyzes your entire armory against the job description and updates the data in the editor on the right.
4.  **Review & Refine:** Manually adjust any of the AI-generated content in the editor. Add or remove roles or awards to perfect the narrative.
5.  **Download:** Click "Download as PDF" to get the final document.

## Local Setup & Installation

To run this project on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    You will need a Google Gemini API key. The app will prompt you for this key when you first run it.

5.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

## Deployment

This application is designed for deployment on [Streamlit Community Cloud](https://streamlit.io/cloud). The `requirements.txt` file ensures that all necessary dependencies are installed in the cloud environment.