# MCQ Generator from PDF, DOCX, and TXT Files

## Overview

This project is a FastAPI application that allows users to generate multiple-choice questions (MCQs) from PDF, DOCX, and TXT files. It processes the uploaded files and generates a specified number of quiz questions based on the content.

## Features

- Upload files in PDF, DOCX, and TXT formats.
- Specify the number of quiz questions to generate (between 1 and 20).
- CORS support for cross-origin requests.
- Custom error handling for unsupported file types and other exceptions.

## Requirements

- Python 3.10 or higher
- FastAPI
- Langchain
- Uvicorn
- Other dependencies as specified in `requirements.txt`

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/mfaizanmumtaz/QuizGenerator-Using-LangChain-and-FastAPI.git
   cd QuizGenerator-Using-LangChain-and-FastAPI
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**

   ```bash
   uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Access the API:**

   Open your web browser and navigate to `http://127.0.0.1:8000/docs` to view the interactive API documentation provided by FastAPI.

3. **Upload files and generate MCQs:**

   - Use the `/process_file` endpoint to upload your files and specify the number of questions.
   - The request should be a `POST` request with form data containing:
     - `num_questions`: An integer between 1 and 20.
     - `files`: The files you want to upload (PDF, DOCX, or TXT).

   Example using `curl`:

   ```bash
   curl -X POST "http://127.0.0.1:8000/process_file" -F "num_questions=5" -F "files=@path/to/your/file.pdf"
   ```

## Error Handling

- If the number of questions is not between 1 and 20, a `400 Bad Request` error will be returned.
- If an unsupported file type is uploaded, a `400 Bad Request` error will be returned with a message indicating the issue.
- Any other exceptions during processing will also return a `400 Bad Request` error with the error message.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.
