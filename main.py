from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import time

# Initialize the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to LinkedIn login page
driver.get('https://www.linkedin.com/login')

# Enter your LinkedIn credentials
email_input = driver.find_element(By.ID, 'username')
password_input = driver.find_element(By.ID, 'password')

# Replace the keys "ENTER YOUR EMAIL" and "ENTER YOUR PASSWORD" with your LinkedIn credentials
email_input.send_keys('ENTER YOUR EMAIL')
password_input.send_keys('ENTER YOUR PASSWORD')

password_input.send_keys(Keys.ENTER)

# Allow time for login to complete
time.sleep(3)

start = 0 # Start at the first page


# Create an empty list to store the job details
jobs_data = []

# Define the fieldnames including 'Application Date'
fieldnames = ['Job Title', 'Company Name', 'Location Type', 'Linkedin Link', 'Hiring Manager', 'Application Date']


# Create a function to calculate the date
def calculate_date(time_ago):
    today = datetime.now()
    if "minutes" in time_ago:
        minutes = int(time_ago.split(" ")[0])
        return (today - timedelta(minutes=minutes)).strftime('%Y-%m-%d')
    elif "hour" in time_ago:
        hours = int(time_ago.split(" ")[0])
        return (today - timedelta(hours=hours)).strftime('%Y-%m-%d')
    elif "day" in time_ago:
        days = int(time_ago.split(" ")[0])
        return (today - timedelta(days=days)).strftime('%Y-%m-%d')
    elif "month" in time_ago:
        months = int(time_ago.split(" ")[0])
        return (today - timedelta(days=30*months)).strftime('%Y-%m-%d')
    else:
        return "Unknown"

# Create a CSV file to store the job details
with open ('jobs.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Job Title', 'Company Name', 'Location Type', 'Linkedin Link', 'Hiring Manager', 'Application Date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

while True:
    # Navigate to 'Applied Jobs' tab
    driver.get(f'https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED&start={start}') 

    # Allow time for the page to load
    time.sleep(3)
    # Extract job details
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    applied_jobs = soup.find_all('li', class_='reusable-search__result-container')  # Adjust class name as needed

 

    print(f"Found {len(applied_jobs)} applied jobs.")  # Debugging line
    if len (applied_jobs) == 0:
        print("No more jobs to scrape.")
        break

    for job in applied_jobs:
        job_link_element = job.find('a', class_='app-aware-link')
        company_name_element = job.find('div', class_='entity-result__primary-subtitle')
        location_type_element = job.find('div', class_='entity-result__secondary-subtitle')
        job_link_data = job_link_element['href']

        if job_link_element and company_name_element and location_type_element:
            # Click the job to go to the details page
            job_link = job_link_element['href']
            driver.get(job_link)
            time.sleep(2)  # Wait for the details page to load
            try:
                # Grab the job title from the details page
                job_title_element = driver.find_element(By.CLASS_NAME, 't-24')
                job_title = job_title_element.text.strip()
            except:
                job_title = "Not Available"
                break
            try:
                hiring_manager = driver.execute_script("return document.body.innerText.match(/(.+) is hiring for this job/)[1];").strip()
            except:
                try:
                    #Try To find the hiring manager using the class name
                    hiring_manager_element = driver.find_element(By.CLASS_NAME, 'jobs-poster__name')
                    hiring_manager = hiring_manager_element.text.strip()
                except:
                    hiring_manager = "Not Avaialble"
                try:
                    application_time_element = driver.find_element(By.CLASS_NAME, 'post-apply-timeline__entity-time')
                    application_time = application_time_element.text.strip()
                    application_date = calculate_date(application_time)
                except:
                    application_date = "Not Available"

            # Navigate back to the list of applied jobs
            driver.get('https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED')
            time.sleep(2)  # Wait for the list page to load

            # Continue with your existing code to grab company name and location
            company_name = company_name_element.text.strip()
            location_type = location_type_element.text.strip()

            jobs_data.append({
                'Job Title': job_title,
                'Company Name': company_name,
                'Location Type': location_type,
                'Linkedin Link': job_link,
                'Hiring Manager': hiring_manager,
                'Application Date': application_date
            })

            print(f'Job Title: {job_title}\nCompany Name: {company_name}\nLocation Type: {location_type}\nHiring Manager: {hiring_manager}\nDate Applied: {application_date}\n')
            
                # Open the CSV file in append mode and write the entry
            with open('jobs.csv', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({
                    'Job Title': job_title,
                    'Company Name': company_name,
                    'Location Type': location_type,
                    'Linkedin Link': job_link,
                    'Hiring Manager': hiring_manager,
                    'Application Date': application_date
                })
        else:
            print("One of the elements was not found.")  # Debugging line
    # Go to the next page
    start += 10

# Close the browser
driver.quit()

# Print the extracted data
for job in jobs_data:
    print(job)

