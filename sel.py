from openai import OpenAI
import os,json
from spm_org import OPEN_PATH
from utils import JOB_FOLDER,PROFILE_FOLDER,EXTRACT_TEXT_FROM_PDF
client = OpenAI(
    api_key=OPEN_PATH,
)

# response = client.chat.completions.create(
#     model="gpt-3.5-turbo-16k",
#     messages=[
#         {"role": "system", "content": "You are an expert in evaluating resumes against job descriptions and providing a detailed scoring JSON."},
#         {"role": "user", "content": ("How are you")}
#     ],
# )

def LLM_call_test(jd_data,cv_data):
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
        messages=[
        {
            "role": "system",
            "content": (
                "You are an expert in evaluating resumes against job descriptions. Your task is to analyze the provided CV "
                "against the job description and return a detailed scoring JSON strictly following the requested format."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Job Description:\n{jd_data}\n\n"
                f"Candidate CV:\n{cv_data}\n\n"
                "Evaluate the CV against the job description and provide a JSON object with the following fields:\n\n"
                "1. `name`: Applicant's full name from the CV. If unavailable, return `null`.\n"
                "2. `linkedin_id`: LinkedIn profile link from the CV. If unavailable, return `null`.\n"
                "3. `applicant_background`: Score (0-100) based on education, field of study, and years of experience.\n"
                "4. `industry`: Score (0-100) based on relevant technologies and summary analysis.\n"
                "5. `skills`: Score (0-100) for skills matching the job description.\n"
                "6. `experiences`: Score (0-100) for relevance of past experiences.\n"
                "7. `company_affiliations`: Score (0-100) for reputation and value of companies worked at and role importance.\n"
                "8. `final_score`: Average of all the above scores.\n"
                "9. `summary`: A 100-word summary of the applicant's profile.\n"
                "10. `explanation`: Justification for the `final_score` and overall evaluation.\n\n"
                "### Format:\n"
                "{\n"
                "  \"name\": \"<applicant name>\",\n"
                "  \"linkedin_id\": \"<LinkedIn profile link>\",\n"
                "  \"applicant_background\": <score out of 100>,\n"
                "  \"industry\": <score out of 100>,\n"
                "  \"skills\": <score out of 100>,\n"
                "  \"experiences\": <score out of 100>,\n"
                "  \"company_affiliations\": <score out of 100>,\n"
                "  \"final_score\": <score out of 100>,\n"
                "  \"summary\": \"<100-word summary>\",\n"
                "  \"explanation\": \"<justification for the final score>\"\n"
                "}\n\n"
                "### Notes:\n"
                "- Return `null` for unavailable fields like `name` or `linkedin_id`.\n"
                "- Ensure scores are integers and align with the evaluation criteria.\n"
                "- Output only the JSON object, with no additional text or explanations."
            ),
        },
        ],
    )

    # print(response.choices[0].message.content.strip())
    # print("\n\n")
    
    try:
        output = response.choices[0].message.content
        json_data = json.loads(output)  # Validate the JSON format
        print(json_data)
        return output
    except json.JSONDecodeError:
        print("The model's output is not valid JSON.")
        return response.choices[0].message.content

def driver_code(file_path,job_description,location):

    jd_content = EXTRACT_TEXT_FROM_PDF(file_path)

    extracted_data = {}

    for file_name in os.listdir(PROFILE_FOLDER):
        file_path = os.path.join(PROFILE_FOLDER, file_name)
        
        # Check if it's a file and ends with .pdf
        if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
            try:
                extracted_text = EXTRACT_TEXT_FROM_PDF(file_path)
                # extracted_data[file_name] = extracted_text

                extracted_data[file_name] = LLM_call_test(jd_data=jd_content,cv_data=extracted_text)
                print(file_name,"extracted \n")
            except Exception as e:
                print(f"Error processing file {file_name}: {str(e)}")

    return extracted_data


extracted_data = driver_code('job_descriptions\JD_1.pdf',job_description="Principal Engineer",location="Texas")
print(extracted_data)
