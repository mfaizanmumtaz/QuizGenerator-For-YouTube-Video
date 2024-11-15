from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os, re, time
import tiktoken
import tempfile
from fastapi import UploadFile
from pydantic import BaseModel, Field
from typing import List

from dotenv import load_dotenv
load_dotenv()

class QuizQuestion(BaseModel):
    question: str = Field(description="The quiz question")
    options: List[str] = Field(description="List of possible answers")
    correct_answer: str = Field(description="The correct answer")
    reference_text: str = Field(description="The reference text for the question if possible maximum 100 words")

class Quiz(BaseModel):
    questions: List[QuizQuestion] = Field(description="List of quiz questions")

class IncomingFileProcessor:
    async def process_file_and_generate_quiz(self, files: List[UploadFile], num_questions: int = 5) -> List[str]:
        text = ''
        for file in files:
            file_extension = file.filename.lower().split('.')[-1]
            suffix = f'.{file_extension}'
            temp_file = None
            
            try:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                await file.seek(0)
                content = await file.read()
                temp_file.write(content)
                temp_file.flush()
                temp_file.close()
                
                loader = PyMuPDFLoader(temp_file.name)
                pages = loader.load()
                for page in pages:
                    text += page.page_content
                
            finally:
                if temp_file:
                    try:
                        time.sleep(0.1)
                        
                        if os.path.exists(temp_file.name):
                            os.unlink(temp_file.name)
                    except Exception as e:
                        pass
        
        text = self.clean_text(text)
        return self.generate_quiz(text, num_questions)
    

    def clean_text(self, text):
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = cleaned.strip()
        return cleaned
    
    def generate_quiz(self, text: str, num_questions: int = 5) -> dict:
        model = ChatOpenAI(temperature=0.3, model="gpt-4o-mini")
        structured_llm = model.with_structured_output(Quiz)
        prompt = PromptTemplate.from_template(
            "Based on the following content, generate a quiz with exactly {num_questions} multiple-choice questions. "
            "Each question should have 4 options, with one correct answer. "
            "Ensure the questions cover key points from the content.\n\n"
            "Content:\n{text}\n\n"
            "make sure always return response in **english** language"
        )
        chain = prompt | structured_llm

        # Get the appropriate tokenizer for the model
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        
        # Convert text to tokens to check length
        tokens = encoding.encode(text)
        
        # Handle case where text is too long for single API call
        if len(tokens) > 122000:
            # Split tokens into chunks of 122000 (max model context)
            chunks = [tokens[i:i + 122000] for i in range(0, len(tokens), 122000)]
            
            # Initialize list to store all generated questions
            all_questions = []
            
            # Calculate how many questions to generate per chunk
            questions_per_chunk = max(1, num_questions // len(chunks))
            # Handle remaining questions that don't divide evenly
            remaining_questions = num_questions % len(chunks)
            
            # Process each chunk separately
            for i, chunk in enumerate(chunks):
                # Convert token chunk back to text
                chunk_text = encoding.decode(chunk)
                
                # Determine number of questions for this chunk
                chunk_questions = questions_per_chunk
                if remaining_questions > 0:
                    # Distribute remaining questions across early chunks
                    chunk_questions += 1
                    remaining_questions -= 1
                
                # Recursively generate questions for this chunk
                chunk_result = chain.invoke({"text": chunk_text, "num_questions": chunk_questions})
                all_questions.extend(chunk_result.model_dump()["questions"])
            
            # Return combined questions from all chunks
            return all_questions
        
        # If text is short enough, generate questions directly
        num_questions = max(1, min(20, num_questions))  # Ensure between 1 and 20
        
        result = chain.invoke({"text": text, "num_questions": num_questions})
        return result.model_dump()["questions"]