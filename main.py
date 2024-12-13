import os,fitz
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from utils import driver_code,JOB_FOLDER,PROFILE_FOLDER,EXTRACT_TEXT_FROM_PDF

description = """ 
                    🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊

                        This APIs are created to show a quick demo operations of a JOB Description matching with the best Profile  
                                        
                        
                        This particular version has following APIs:

                        | Endpoint                                       | Description                                                                                      |
                        |------------------------------------------------|--------------------------------------------------------------------------------------------------|
                        | /upload_Job_Description/                       | Upload the Job Description (ONLY PDF),Job Tittle and Location to find suitable candidates.       |
                        | /list_job_descriptions/                        | Extract the uploaded Job Description Data.                                                       |
                        | /list_profile_data/                            | Extract the extracted Candidate Profiles Data.                                                   |
                        

                    🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊---🧊

👨‍💻️👨‍💻️👨‍💻️ By :- `Ketul Patel`  

Find the Source code at: `https://github.com/K2lFrankenstein/Headhunter/` 
"""

app = FastAPI(title=" Headhumter automation API",
    description=description,
    version="1.0.4",openapi_url="/base_schema",docs_url="/")

@app.post("/upload_Job_Description/")
async def upload_job_description(
    file: UploadFile = File(...),
    job_role: str = Form(...),
    location: str = Form(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        os.makedirs(JOB_FOLDER, exist_ok=True)
        file_path = os.path.join(JOB_FOLDER, file.filename)
        
        # Check if file with the same name already exists
        if os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"A file with the name {file.filename} already exists")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        extr_data,jd_content = driver_code(file_path,job_role,location)   
        
        return {
            "message": f"File {file.filename} uploaded successfully",
            "Profile_Scores": extr_data,
            "jd_content": jd_content,
            "Job_Role": job_role,
            "Location": location
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/list_job_descriptions/")
async def list_job_descriptions():
    try:
        files = [f for f in os.listdir(JOB_FOLDER) if f.endswith('.pdf')]

        extracted_texts = {}
        for file in files:
            file_path = os.path.join(JOB_FOLDER, file)
            extracted_texts[file] = EXTRACT_TEXT_FROM_PDF(file_path)

        return JSONResponse(status_code=200, content={"job_descriptions": extracted_texts})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})

@app.get("/list_profile_data/")
async def list_profile_data():
    try:
        # List all PDF files in PROFILE_FOLDER
        files = [f for f in os.listdir(PROFILE_FOLDER) if f.endswith('.pdf')]

        # Extract text from each PDF
        extracted_texts = {}
        for file in files:
            file_path = os.path.join(PROFILE_FOLDER, file)
            extracted_texts[file] = EXTRACT_TEXT_FROM_PDF(file_path)

        return JSONResponse(status_code=200, content={"extracted_texts": extracted_texts})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})   
