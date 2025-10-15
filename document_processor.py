import os
import PyPDF2
import docx2txt
from docx import Document
import re
from typing import Optional, Dict, Any

class DocumentProcessor:

    def __init__(self):
        self.supported_formats = ['.pdf', '.doc', '.docx']
    
    def extract_text(self, file_path: str) -> Optional[str]:
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension in ['.doc', '.docx']:
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None
    
    def _extract_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            raise
        
        return self._clean_text(text)
    
    def _extract_from_docx(self, file_path: str) -> str:
        try:
            text = docx2txt.process(file_path)
            if not text.strip():
                doc = Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX: {str(e)}")
            raise
        
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)

        text = re.sub(r'[^\w\s\n\-\.,@()]+', '', text)
        
        return text.strip()
    
    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        contact_info = {
            'emails': [],
            'phones': [],
            'linkedin': None,
            'github': None
        }
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        contact_info['emails'] = re.findall(email_pattern, text)

        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        contact_info['phones'] = re.findall(phone_pattern, text)

        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()

        github_pattern = r'github\.com/[\w\-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact_info['github'] = github_match.group()
        
        return contact_info
    
    def extract_skills(self, text: str) -> list:
        skill_keywords = [
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'spring', 'laravel', 'rails',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'git', 'github', 'gitlab', 'bitbucket',
            'machine learning', 'deep learning', 'ai', 'data science',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'agile', 'scrum', 'devops', 'ci/cd', 'testing', 'unit testing'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))
