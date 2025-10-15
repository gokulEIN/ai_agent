#don't change this file
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    
    CALENDLY_LINK = os.environ.get('CALENDLY_LINK')
    
    UPLOAD_FOLDER = 'uploads/resumes'
    RESULTS_FOLDER = 'results'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL')
    
    SELECTION_THRESHOLD = 5.0
