import os
import json
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer
import numpy as np
import google.generativeai as genai
from config import Config

class ResumeRAGSystem:
    
    def __init__(self):
        self.config = Config()

        genai.configure(api_key=self.config.GEMINI_API_KEY)
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config.EMBEDDING_MODEL
        )
        self.gemini_model = genai.GenerativeModel(self.config.GEMINI_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vector_store = None
        
    def create_resume_embeddings(self, resume_texts: List[str], applicant_ids: List[str]) -> None:

        all_chunks = []
        metadatas = []
        
        for idx, (resume_text, applicant_id) in enumerate(zip(resume_texts, applicant_ids)):
            chunks = self.text_splitter.split_text(resume_text)
            all_chunks.extend(chunks)
            
            for chunk_idx, chunk in enumerate(chunks):
                metadatas.append({
                    'applicant_id': applicant_id,
                    'chunk_index': chunk_idx,
                    'source': f'resume_{applicant_id}'
                })
        
        if all_chunks:
            self.vector_store = FAISS.from_texts(
                texts=all_chunks,
                embedding=self.embeddings,
                metadatas=metadatas
            )
    
    def analyze_resume_against_job(self, resume_text: str, job_description: Dict[str, Any]) -> Dict[str, Any]:

        prompt_text = f"""You are an experienced HR manager conducting a thorough resume review. Analyze this candidate's application with empathy and provide constructive, human-like feedback.

POSITION DETAILS:
Job Title: {job_description.get('job_title', '')}
Job Description: {job_description.get('job_description', '')}
Required Skills: {job_description.get('required_skills', '')}
Experience Level: {job_description.get('experience_required', '')}

CANDIDATE'S RESUME:
{resume_text[:4000]}

Please provide a comprehensive evaluation as if you were personally reviewing this candidate. Be encouraging yet honest, specific yet constructive.

IMPORTANT: Respond with ONLY valid JSON in this exact format:

{{
    "overall_score": 7.2,
    "skills_match": {{
        "matched_skills": ["Python", "Machine Learning", "Data Analysis"],
        "missing_skills": ["Docker", "Kubernetes", "MLOps"]
    }},
    "experience_assessment": "The candidate shows 2+ years of relevant experience in data science with hands-on Python development. While they have solid fundamentals, they would benefit from more exposure to production ML systems and DevOps practices.",
    "strengths": [
        "Strong foundation in Python programming and data manipulation",
        "Demonstrated experience with machine learning algorithms and model development", 
        "Good analytical thinking evident from project descriptions",
        "Shows initiative in learning new technologies independently"
    ],
    "weaknesses": [
        "Limited experience with containerization and deployment technologies like Docker",
        "Could benefit from more exposure to cloud platforms and MLOps workflows",
        "Resume could better highlight specific business impact of technical projects",
        "Would benefit from more collaborative team project experience"
    ],
    "recommendation": "SELECTED",
    "reasoning": "This candidate demonstrates strong technical fundamentals and genuine passion for AI/ML. While they may need some mentoring in production systems and DevOps practices, their solid programming skills and eagerness to learn make them a great fit for a growing team. I believe they would thrive in our collaborative environment and contribute meaningfully to our AI initiatives within 3-6 months."
}}"""
        
        try:
            response = self.gemini_model.generate_content(prompt_text)
            result = response.text
            
            result_text = result.strip()
            
            if '```json' in result_text:
                start = result_text.find('```json') + 7
                end = result_text.find('```', start)
                result_text = result_text[start:end].strip()
            elif '```' in result_text:
                start = result_text.find('```') + 3
                end = result_text.find('```', start)
                result_text = result_text[start:end].strip()
            
            if result_text.startswith('{') and result_text.endswith('}'):
                analysis_result = json.loads(result_text)
            else:
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_text = result_text[start_idx:end_idx]
                    analysis_result = json.loads(json_text)
                else:
                    raise ValueError("No valid JSON found in response")
            
            required_fields = ['overall_score', 'skills_match', 'experience_assessment', 
                             'strengths', 'weaknesses', 'recommendation', 'reasoning']
            
            for field in required_fields:
                if field not in analysis_result:
                    analysis_result[field] = "Not provided"
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in resume analysis: {str(e)}")
            return {
                "overall_score": 5.0,
                "skills_match": {
                    "matched_skills": [],
                    "missing_skills": []
                },
                "experience_assessment": "Unable to assess due to processing error",
                "strengths": ["Unable to determine"],
                "weaknesses": ["Processing error occurred"],
                "recommendation": "REJECTED",
                "reasoning": f"Analysis failed due to error: {str(e)}"
            }
    
    def batch_analyze_resumes(self, resumes_data: List[Dict[str, Any]], job_description: Dict[str, Any]) -> List[Dict[str, Any]]:

        results = []
        
        for resume_data in resumes_data:
            try:
                analysis = self.analyze_resume_against_job(
                    resume_data['resume_text'], 
                    job_description
                )

                analysis.update({
                    'applicant_id': resume_data['applicant_id'],
                    'full_name': resume_data['full_name'],
                    'email': resume_data['email'],
                    'position_applied': resume_data['position_applied']
                })
                
                results.append(analysis)
                
            except Exception as e:
                print(f"Error analyzing resume for {resume_data.get('full_name', 'Unknown')}: {str(e)}")
                results.append({
                    'applicant_id': resume_data['applicant_id'],
                    'full_name': resume_data['full_name'],
                    'email': resume_data['email'],
                    'position_applied': resume_data['position_applied'],
                    'overall_score': 0.0,
                    'recommendation': 'REJECTED',
                    'reasoning': f'Analysis failed: {str(e)}'
                })
        
        return results
    
    def get_similar_resumes(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:

        if not self.vector_store:
            return []
        
        try:
            similar_docs = self.vector_store.similarity_search_with_score(query_text, k=k)
            
            results = []
            for doc, score in similar_docs:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score)
                })
            
            return results
            
        except Exception as e:
            print(f"Error in similarity search: {str(e)}")
            return []
