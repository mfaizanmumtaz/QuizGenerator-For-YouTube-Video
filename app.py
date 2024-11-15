from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils import IncomingFileProcessor
from typing import List
import uvicorn

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Generate Quiz from PDF, DOCX,TXT"}

file_processor = IncomingFileProcessor()

@app.post("/process_file")
async def process_file(
    num_questions: int = Form(description="Number of quiz questions to generate"),
    files: List[UploadFile] = File(...)
):  
    if not 1 <= num_questions <= 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of questions must be between 1 and 20"
        )

    supported_extensions = {'docx', 'pdf', 'txt', 'doc'}
        
    for file in files:
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type for {file.filename}. Please upload only PDF, DOCX, video, or audio files."
            )

    try:
        all_mcqs = await file_processor.process_file_and_generate_quiz(files, num_questions)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
                
    return JSONResponse(
        content={
            "questions": all_mcqs
        },
        status_code=status.HTTP_200_OK
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "succeeded": False,
            "message": str(exc.detail),
            "httpStatusCode": exc.status_code
        }
    )