import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

class SimpleDatabase:
    
    def __init__(self, db_folder: str = "data"):
        self.db_folder = db_folder
        os.makedirs(db_folder, exist_ok=True)
        
        self.applications_file = os.path.join(db_folder, "applications.json")
        self.job_descriptions_file = os.path.join(db_folder, "job_descriptions.json")
        self.results_file = os.path.join(db_folder, "analysis_results.json")
        
        self._init_files()
    
    def _init_files(self):
        files_to_init = [
            self.applications_file,
            self.job_descriptions_file,
            self.results_file
        ]
        
        for file_path in files_to_init:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def _load_data(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, file_path: str, data: List[Dict[str, Any]]):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def save_application(self, application_data: Dict[str, Any]) -> str:
        applications = self._load_data(self.applications_file)
        
        application_id = str(uuid.uuid4())
        application_data['id'] = application_id
        application_data['created_at'] = datetime.now().isoformat()
        application_data['status'] = 'pending'
        
        applications.append(application_data)
        self._save_data(self.applications_file, applications)
        
        return application_id
    
    def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        applications = self._load_data(self.applications_file)
        for app in applications:
            if app.get('id') == application_id:
                return app
        return None
    
    def get_all_applications(self) -> List[Dict[str, Any]]:
        return self._load_data(self.applications_file)
    
    def update_application_status(self, application_id: str, status: str):
        applications = self._load_data(self.applications_file)
        for app in applications:
            if app.get('id') == application_id:
                app['status'] = status
                app['updated_at'] = datetime.now().isoformat()
                break
        self._save_data(self.applications_file, applications)
    
    def save_job_description(self, job_data: Dict[str, Any]) -> str:
        job_descriptions = self._load_data(self.job_descriptions_file)
        
        job_id = str(uuid.uuid4())
        job_data['id'] = job_id
        job_data['created_at'] = datetime.now().isoformat()
        job_data['is_active'] = True

        for job in job_descriptions:
            job['is_active'] = False
        
        job_descriptions.append(job_data)
        self._save_data(self.job_descriptions_file, job_descriptions)
        
        return job_id
    
    def get_active_job_description(self) -> Optional[Dict[str, Any]]:
        job_descriptions = self._load_data(self.job_descriptions_file)
        for job in job_descriptions:
            if job.get('is_active', False):
                return job
        return None
    
    def get_job_description_by_title(self, job_title: str) -> Optional[Dict[str, Any]]:
        job_descriptions = self._load_data(self.job_descriptions_file)
        for job in job_descriptions:
            if job.get('job_title', '').lower() == job_title.lower() and job.get('is_active', False):
                return job
        return None
    
    def get_all_job_descriptions(self) -> List[Dict[str, Any]]:
        return self._load_data(self.job_descriptions_file)
    
    def save_analysis_results(self, results_data: List[Dict[str, Any]]) -> str:
        all_results = self._load_data(self.results_file)
        
        batch_id = str(uuid.uuid4())
        batch_data = {
            'id': batch_id,
            'created_at': datetime.now().isoformat(),
            'results': results_data,
        }
        
        all_results.append(batch_data)
        self._save_data(self.results_file, all_results)
        
        return batch_id
    
    def get_analysis_results(self, batch_id: str) -> Optional[Dict[str, Any]]:
        all_results = self._load_data(self.results_file)
        for batch in all_results:
            if batch.get('id') == batch_id:
                return batch
        return None
    
    def get_latest_analysis_results(self) -> Optional[Dict[str, Any]]:
        all_results = self._load_data(self.results_file)
        if all_results:
            return max(all_results, key=lambda x: x.get('created_at', ''))
        return None
    
    def get_all_analysis_results(self) -> List[Dict[str, Any]]:
        return self._load_data(self.results_file)

    def get_pending_applications(self) -> List[Dict[str, Any]]:
        applications = self._load_data(self.applications_file)
        return [app for app in applications if app.get('status') == 'pending']
    
    def get_processed_applications(self) -> List[Dict[str, Any]]:
        applications = self._load_data(self.applications_file)
        return [app for app in applications if app.get('status') in ['selected', 'rejected']]
    
    def get_all_analysis_results(self) -> List[Dict[str, Any]]:
        return self._load_data(self.results_file)
    
    def clear_all_data(self):
        self._save_data(self.applications_file, [])
        self._save_data(self.job_descriptions_file, [])
        self._save_data(self.results_file, [])
