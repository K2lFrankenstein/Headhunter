# Headhunter Candidate Ranking Tool

## Overview

The Headhunter Candidate Ranking Tool is designed for recruiters and headhunters to identify, evaluate, and rank the most suitable candidates for specialized roles based on a provided job description. This tool automates the process of finding potential candidates on LinkedIn, extracting and processing their resumes, and ranking them using OpenAI's GPT for detailed relevance analysis.

---

## Features

1. **Candidate Search**

   - Accepts a job description (in PDF format), job title, and location from the user.

2. **Candidate Data Extraction**

   - Utilizes Google Dorking queries to find LinkedIn profiles relevant to the job description and location.
   - Uses Selenium to individually access each LinkedIn profile and download CVs.
   - Extracts text from both job descriptions and candidate CVs.

3. **Automated Ranking**

   - Employs OpenAI's GPT to analyze and rank candidates based on the following parameters:
     - `applicant_background`: Education, field of study, and years of experience.
     - `industry`: Relevant technologies and summary analysis.
     - `skills`: Match between skills and job description.
     - `experiences`: Relevance of past experiences.
     - `company_affiliations`: Value and reputation of companies worked at.
     - `final_score`: Average of all the above scores.
     - `summary`: A concise summary of the candidate's profile.
     - `explanation`: Detailed reasoning behind the `final_score`.

4. **Result Presentation**

   - Returns a comprehensive, ranked list of candidates along with their scores, summaries, and evaluation justifications.

---

## Technologies Used

- **Programming Language:** Python
- **Frameworks:** FastAPI
- **Automation Tools:** Selenium
- **AI/ML:** OpenAI’s GPT

---

## APIs

This particular version has the following APIs:

| Endpoint                   | Description                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| /upload\_Job\_Description/ | Upload the Job Description (ONLY PDF), Job Title, and Location to find suitable candidates. |
| /list\_job\_descriptions/  | Extract the uploaded Job Description Data.                                                  |
| /list\_profile\_data/      | Extract the extracted Candidate Profiles Data.                                              |

---

## Data Cleaning

- Removes extra spacing and wild characters from CVs and job descriptions to optimize token usage.
- Minimizes unnecessary data scraping by focusing on Google's response and LinkedIn profiles for extraction.

---

## Automation Highlights

1. **Candidate Identification**

   - Automated expert finding using Google Dorking queries.

2. **Data Extraction**

   - Streamlined data scraping and CV extraction with Selenium.

3. **Job Description Matching**

   - Automated job description and CV matching using OpenAI's LLM for accurate ranking.

---

## Setup and Usage Instructions

### Prerequisites

- Python 3.8+
- Selenium WebDriver
- OpenAI API Key
- FastAPI framework

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/K2lFrankenstein/Headhunter.git
   cd headhunter
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up OpenAI API Key file and extract cookies for LinkedIn session in `.env`.

### Running the Tool

1. Start the FastAPI server:
   ```bash
   fastapi dev main.py
   ```
2. Access the API at `http://127.0.0.1:8000`.
3. Provide the job description PDF, job title, and location to get the ranked candidate list.
4. After processing, the tool presents the results in JSON format, including ranked candidates with their scores, summaries, and evaluation justifications.

---

