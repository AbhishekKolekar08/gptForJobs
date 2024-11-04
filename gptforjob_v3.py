import dearpygui.dearpygui as dpg
from pdfminer.high_level import extract_text
import cohere
import re
import requests
from bs4 import BeautifulSoup
import os
import markdown

co = cohere.Client("")  

pdf_path = None

def extract_text_from_pdf(pdf_path):
    try:
        return extract_text(pdf_path)
    except Exception as e:
        dpg.set_value("output_text", f"Error: {e}")
        return None

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)  # Remove newlines
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = re.sub(r'Page \d+ of \d+', '', text)  # Remove page numbers
    text = text.replace('•', ' ')  # Replace bullets with space
    text = re.sub(r'\+46-\d{9}', lambda x: x.group().replace('-', ''), text)  # Clean phone numbers
    return text.strip()  # Trim redundant spaces

def extract_skills(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        dpg.set_value("output_text", f"Failed to retrieve the page: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('span', {'itemprop': 'title'})
    description = soup.find('span', {'class': 'jobdescription'})
    
    if title and description:
        job_title_text = title.get_text(separator="\n", strip=True)
        job_description_text = description.get_text(separator="\n", strip=True)

        try:
            response = co.chat(
                message=f"Following is a job description of a role I want to apply to:\nTitle: {job_title_text}\n"
                        f"Job Description: {job_description_text}\n<end of description>\n\n"
                        "Imagine you are a seasoned hiring manager. List the main keywords you would put in this job "
                        "description that candidates need to fulfill. Give those keywords a weighing score from 1 to 10 in "
                        "order of relevance. Feel free to merge similar keywords and aggregate their score. Output the main "
                        "keywords and their scores as a dictionary, only keep the dictionary, no extra word."
            )
            return response.text
        except Exception as e:
            dpg.set_value("output_text", f"Failed to get skills: {e}")
            return None
    else:
        dpg.set_value("output_text", "Job description section not found.")
        return None

def skills_match(resume_text, reqs):
    response = co.chat(
        message=f"Following is my resume:\n{resume_text}\n<end of resume>\n"
                f"I am applying for a job which has the keywords and their respective relevance in this dictionary:\n{reqs}\n"
                "Please provide a score out of 100 indicating how well my skills and projects match the job requirements, "
                "without any sugarcoating. Additionally, offer recommendations for changes I can make to my resume to maximize "
                "my chances of an interview, excluding any suggestions related to work experience, roles, responsibilities, "
                "proofreading, cover letter tailoring, or English proficiency. Use markdown for formatting."
    )
    return response.text

def display_results(sender, app_data):
    url = dpg.get_value("url_input")
    if not url:
        dpg.set_value("output_text", "Please enter a job description URL.")
        return
    
    skills_req = extract_skills(url)
    if skills_req is None:
        return
    
    if not pdf_path:
        dpg.set_value("output_text", "Please upload a resume PDF.")
        return
    
    resume_text = extract_text_from_pdf(pdf_path)
    if resume_text is None:
        return
    resume_text = clean_text(resume_text)
    
    markdown_output = skills_match(resume_text, skills_req)
    
    html_output = markdown.markdown(markdown_output)
    dpg.set_value("output_text", html_output)  # Display HTML content

def reset_fields():
    global pdf_path
    pdf_path = None
    dpg.set_value("pdf_filename", "No file selected")
    dpg.set_value("url_input", "")
    dpg.set_value("output_text", "") 

def upload_pdf(sender, app_data):
    global pdf_path
    pdf_path = app_data[0] 
    if pdf_path:
        dpg.set_value("pdf_filename", f"Selected file: {os.path.basename(pdf_path)}")

def main():
    dpg.create_context()
    dpg.create_viewport(title='Resume and Job Matching Tool', width=700, height=500)

    with dpg.window(label="Resume and Job Matching Tool", width=700, height=500):
        dpg.add_text("Upload your resume PDF:")
        dpg.add_button(label="Import PDF", callback=lambda: dpg.file_dialog(upload_pdf, extensions=".pdf"))
        dpg.add_text("No file selected", tag="pdf_filename")
        
        dpg.add_text("Enter Job Description URL:")
        dpg.add_input_text(tag="url_input", width=300)
        
        dpg.add_button(label="Analyze Resume for Job", callback=display_results)
        dpg.add_button(label="Reset", callback=reset_fields)
        
        dpg.add_text("Output:")
        dpg.add_text("", tag="output_text", wrap=200)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
