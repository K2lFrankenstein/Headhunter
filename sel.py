from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import os
from spm_org import ck_list
from main import PROFILE_FOLDER

def setup_driver(cookies_list):
    """
    Setup the Selenium WebDriver with options for headless browsing.
    """

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration

    options = webdriver.ChromeOptions()

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
    params = {"q": query, "num": 5}  # 'num' specifies the number of results per page

    response = requests.get(base_url, headers=headers, params=params)

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
            print(f"more button not found or clickable: {e}")
         
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    
    cookies_list = ck_list
    driver = setup_driver(cookies_list)

    try:
        results = search_google_dorking(job_description="Principal Data Enginner", location="USA")

        for idx, result in enumerate(results, start=0):
            print(f"Result {idx}:")
            print(f"Title: {result['title']}")
            print(f"Link: {result['link']}")
            print(f"Snippet: {result['snippet']}")
            fetch_linkedin_profile(driver, result['link'],result['title'])
            print("-" * 40)

    finally:
        driver.quit()
