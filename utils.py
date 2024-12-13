import os,fitz,re,time,requests,json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from spm_org import ck_list,OPEN_PATH
from openai import OpenAI


client = OpenAI(
    api_key=OPEN_PATH,
)

# Define the path for the job description folder
JOB_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "job_descriptions")
PROFILE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile")

def remove_newlines(serie):
    serie = serie.replace('\n', ' ')
    serie = serie.replace('\\n', ' ')
    serie = serie.replace('  ', ' ')
    serie = serie.replace('  ', ' ')
    serie = serie.replace('  ', ' ')
    serie = serie.replace('  ', ' ')
    serie = serie.replace('  ', ' ')
    extracted_data = re.sub(r'\s*Page \d+ of \d+\s*$', ' ', serie)

    return extracted_data

def EXTRACT_TEXT_FROM_PDF(filename):

    pdf_file =  fitz.open(filename)
    PDFFILEDATALIST = ""

    for Page_No,page in enumerate(pdf_file):
        ddt  = remove_newlines(page.get_text())
        ddt = ddt[:]
        pymupdf_text = "\n" + ddt
                   
        PDFFILEDATALIST+=pymupdf_text

    return PDFFILEDATALIST

def setup_driver(cookies_list):
    """
    Setup the Selenium WebDriver with options for headless browsing.
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration

    # Set download directory
    prefs = {
        "download.default_directory": PROFILE_FOLDER,  # Set custom download directory
        "download.prompt_for_download": False,  # Disable download prompt
        "download.directory_upgrade": True,  # Automatically overwrite files
        "safebrowsing.enabled": True  # Enable safe browsing
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.linkedin.com")
    for cookie in cookies_list:
        # Convert string boolean values ('true', 'false') to actual booleans
        cookie['secure'] = cookie['secure'] == 'true'
        cookie['httpOnly'] = cookie['httpOnly'] == 'true'
        cookie['session'] = cookie['session'] == 'true'
        # cookie.pop('storeId', None)  # Remove non-essential keys
        if cookie.get('sameSite') not in ['Strict', 'Lax', 'None']:
            cookie.pop('sameSite', None)
        driver.add_cookie(cookie)

    # driver.refresh()    
    return driver

def search_google_dorking(job_description, location):
    query = f'site:linkedin.com "{job_description}" intitle:"LinkedIn" inurl:"linkedin.com/in/" location:"{location}" -intitle:"jobs"'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    base_url = "https://www.google.com/search" 
    params = {"q": query, "num": 3}  # 'num' specifies the number of results per page

    response = requests.get(base_url, headers=headers, params=params)

    print(job_description,location)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        for g in soup.find_all("div", class_="tF2Cxc"):
            title = g.find("h3").text if g.find("h3") else "No title"
            link = g.find("a")["href"] if g.find("a") else "No link"
            if link[-1] != "/":
                link += "/"
            snippet = g.find("span", class_="aCOpRe").text if g.find("span", class_="aCOpRe") else "No snippet"

            results.append({
                "title": title,
                "link": link,
                "snippet": snippet
            })

        return results
    else:
        print(f"Failed to fetch results. HTTP Status Code: {response.status_code}")
        return []

def retry(link):
    flag = False
    driver2 = setup_driver(ck_list)
    try:
            button_xpath = '/html/body/div[2]/div/div/section/button'
            WebDriverWait(driver2, 3).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
            print("Dismiss button clicked.")
    except Exception as e:
        print(f"Dismiss button not found or clickable: {e}")

    try:
        driver2.get(link)
        JOIN_BUTTON_XPATH = '/html/body/header/nav/div/a[1]'
        join_button = WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.XPATH, JOIN_BUTTON_XPATH)))
        if join_button and "Join now" in join_button.text:
            print("Join now button found. Refreshing the page...")
            driver2.refresh()
        else:
            print("no button join")
    except Exception as e:
        print(e,"-ck not work")

    try:
        button_xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[2]/button'
        WebDriverWait(driver2, 5).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
        print("more button clicked.")
        
        button_xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[2]/div/div/ul/li[2]/div'
        WebDriverWait(driver2, 5).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
        print("save pdf clicked button clicked.")
        time.sleep(2)
        flag = True

    except Exception as e:
        print(f"more button not found or clickable: {e}")   


    driver2.quit()  
    return flag   

def fetch_linkedin_profile(driver, link,tittle):
    """
    Fetch and save a LinkedIn profile page as HTML using Selenium.
    """
    try:

        driver.get(link)

        try:
            button_xpath = '/html/body/div[2]/div/div/section/button'
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
            print("Dismiss button clicked.")
        except Exception as e:
            print(f"Dismiss button not found or clickable: {e}")

        try:
                JOIN_BUTTON_XPATH = '/html/body/header/nav/div/a[1]'
                join_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, JOIN_BUTTON_XPATH)))
                if join_button and "Join now" in join_button.text:
                    print("Join now button found. Refreshing the page...")
                    driver.refresh()
                    time.sleep(1)  # Wait for the page to reload
                else:
                    print("no button join")  # Exit the loop if no "Join now" button is found
        except Exception as e:
                
                print(f"'Join now' button not found: {e}")
                
        
        try:
            button_xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[2]/button'
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
            print("more button clicked.")
            
            button_xpath = '/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[2]/div/div/ul/li[2]/div'
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
            print("save pdf clicked button clicked.")

            time.sleep(5) 
        except Exception as e:
            flag = retry(link)        
            print(f"'Retry Work:",flag)
            print(f"more button not found or clickable: {e}")
         
    except Exception as e:
        print(f"An error occurred: {e}")

def run_scrape(job_description="Principal Data Enginner", location="USA"):
    cookies_list = ck_list
    driver = setup_driver(cookies_list)

    try:
        results = search_google_dorking(job_description, location)

        for idx, result in enumerate(results, start=1):
            print(f"Result {idx}:")
            print(f"Title: {result['title']}")
            print(f"Link: {result['link']}")
            # print(f"Snippet: {result['snippet']}")
            fetch_linkedin_profile(driver, result['link'],result['title'])
            print("-" * 40)

    finally:
        driver.quit()

    return results

def LLM_call(jd_data,cv_data):
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

    
    list_results = run_scrape(job_description,location)

    extracted_data = {}

    for file_name in os.listdir(PROFILE_FOLDER):
        file_path = os.path.join(PROFILE_FOLDER, file_name)
        
        # Check if it's a file and ends with .pdf
        if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
            try:
                extracted_text = EXTRACT_TEXT_FROM_PDF(file_path)
                extracted_data[file_name] = LLM_call(jd_data=jd_content,cv_data=extracted_text)
                print(file_name,"extracted \n")
            except Exception as e:
                print(f"Error processing file {file_name}: {str(e)}")

    return extracted_data,jd_content
    
# for file_name in os.listdir(folder_path):
#     file_path = os.path.join(folder_path, file_name)
    
#     # Check if it's a file and ends with .pdf
#     if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
#         try:
#             os.remove(file_path)
#             print(f"Deleted file: {file_name}")
#         except Exception as e:
#             print(f"Error processing file {file_name}: {str(e)}")