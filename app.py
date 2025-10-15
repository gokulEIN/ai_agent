from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import threading
import time
from config import Config
from forms import JobApplicationForm, JobDescriptionForm
from document_processor import DocumentProcessor
from rag_system import ResumeRAGSystem
from email_system import EmailSystem
from csv_exporter import CSVExporter
from database import SimpleDatabase

app = Flask(__name__)
app.config.from_object(Config)

db = SimpleDatabase()
doc_processor = DocumentProcessor()
rag_system = ResumeRAGSystem()
email_system = EmailSystem()
csv_exporter = CSVExporter()

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

processing_lock = threading.Lock()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['pdf', 'doc', 'docx']

def process_single_application(application_id):
    try:
        print(f"=== Processing application {application_id} ===")
        
        applications = db.get_all_applications()
        application = None
        for app in applications:
            if app.get('id') == application_id:
                application = app
                break
        
        if not application:
            print(f"Application {application_id} not found")
            return
        
        print(f"Processing resume for {application['full_name']}...")

        job_description = db.get_job_description_by_title(application['position_applied'])
        if not job_description:
            print(f"No job description found for {application['position_applied']}")
            return
        
        resume_path = application.get('resume_path')
        if not resume_path or not os.path.exists(resume_path):
            print(f"Resume file not found: {resume_path}")
            return
        
        resume_text = doc_processor.extract_text(resume_path)
        if not resume_text:
            print("Could not extract text from resume")
            return
        
        analysis_result = rag_system.analyze_resume_against_job(resume_text, job_description)
        if not analysis_result:
            print("Analysis failed")
            return
        
        analysis_result.update({
            'applicant_id': application_id,
            'full_name': application['full_name'],
            'email': application['email'],
            'position_applied': application['position_applied']
        })
        
        batch_id = db.save_analysis_results([analysis_result])
        
        recommendation = analysis_result.get('recommendation', '').upper()
        status = 'selected' if recommendation.startswith('SELECTED') and not recommendation.startswith('NOT_SELECTED') else 'rejected'
        db.update_application_status(application_id, status)
        
        print(f"Analysis completed for {application['full_name']}: {status}")

        try:
            all_applications = db.get_all_applications()
            all_analysis_results = []
            
            all_batches = db.get_all_analysis_results()
            for batch in all_batches:
                all_analysis_results.extend(batch.get('results', []))
            
            export_job_description = {
                'job_title': 'Multiple Positions',
                'job_description': 'Various positions processed',
                'required_skills': 'Position-specific skills',
                'experience_required': 'Varies by position'
            }
            csv_file = csv_exporter.export_all_candidates_csv(all_applications, all_analysis_results, export_job_description)
            if csv_file:
                print(f"CSV updated: {csv_file}")
        except Exception as e:
            print(f"Error updating CSV: {e}")
        
        try:
            email_data = application.copy()
            email_data.update(analysis_result)
            
            if status == 'selected':
                email_system.send_selection_email(email_data)
            else:
                email_system.send_rejection_email(email_data)
        except Exception as e:
            print(f"Error sending result email: {e}")
            
    except Exception as e:
        print(f"Error processing application {application_id}: {e}")

def process_applications_async():
    if not processing_lock.acquire(blocking=False):
        print("Processing already in progress, skipping...")
        return
    
    try:
        pending_applications = db.get_pending_applications()
        if not pending_applications:
            print("No pending applications to process")
            processing_lock.release()
            return
        
        print(f"Processing {len(pending_applications)} applications...")
        
        resumes_by_position = {}
        for app in pending_applications:
            resume_path = app.get('resume_path')
            if resume_path and os.path.exists(resume_path):
                resume_text = doc_processor.extract_text(resume_path)
                if resume_text:
                    position = app['position_applied']
                    if position not in resumes_by_position:
                        resumes_by_position[position] = []
                    
                    resumes_by_position[position].append({
                        'applicant_id': app['id'],
                        'full_name': app['full_name'],
                        'email': app['email'],
                        'position_applied': app['position_applied'],
                        'resume_text': resume_text
                    })
                    print(f"Processed resume for {app['full_name']} - {position}")
        
        if not resumes_by_position:
            print("No valid resumes found to process")
            processing_lock.release()
            return

        print("Starting AI analysis...")
        all_analysis_results = []
        
        for position, resumes_data in resumes_by_position.items():
            print(f"Analyzing {len(resumes_data)} applications for {position}...")

            job_description = db.get_job_description_by_title(position)
            if not job_description:
                print(f"No job description found for {position}, skipping...")
                continue

            position_results = rag_system.batch_analyze_resumes(resumes_data, job_description)
            all_analysis_results.extend(position_results)
            print(f"Completed analysis for {position}: {len(position_results)} results")
        
        analysis_results = all_analysis_results
        batch_id = db.save_analysis_results(analysis_results)
        print(f"Analysis results saved with batch ID: {batch_id}")

        for result in analysis_results:
            status = 'selected' if result.get('recommendation', '').upper() == 'SELECTED' else 'rejected'
            db.update_application_status(result['applicant_id'], status)
        
        selected_candidates = [r for r in analysis_results if r.get('recommendation', '').upper() == 'SELECTED']
        rejected_candidates = [r for r in analysis_results if r.get('recommendation', '').upper() != 'SELECTED']
        
        print(f"Selected: {len(selected_candidates)}, Rejected: {len(rejected_candidates)}")
        print("Sending emails...")
        email_results = email_system.send_batch_emails(selected_candidates, rejected_candidates)
        print(f"Email results: {email_results}")
        print("Exporting to CSV...")
        all_applications = db.get_all_applications()
        export_job_description = {
            'job_title': 'Multiple Positions',
            'job_description': 'Various positions processed',
            'required_skills': 'Position-specific skills',
            'experience_required': 'Varies by position'
        }
        csv_file = csv_exporter.export_all_candidates_csv(all_applications, analysis_results, export_job_description)
        if csv_file:
            print(f"All candidates exported to CSV: {csv_file}")
        else:
            print("Error exporting to CSV")
        
        print("Application processing completed successfully!")
        
    except Exception as e:
        print(f"Error in background processing: {str(e)}")
    finally:
        processing_lock.release()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = JobApplicationForm()
    
    if form.validate_on_submit():
        try:
            resume_file = form.resume.data
            if resume_file and allowed_file(resume_file.filename):
                filename = secure_filename(resume_file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume_file.save(resume_path)
                
                application_data = {
                    'full_name': form.full_name.data,
                    'email': form.email.data,
                    'phone': form.phone.data,
                    'position_applied': form.position_applied.data,
                    'experience_level': form.experience_level.data,
                    'cover_letter': form.cover_letter.data,
                    'resume_filename': filename,
                    'resume_path': resume_path
                }
                
                application_id = db.save_application(application_data)
                application_data['id'] = application_id
                
                flash('Application submitted successfully! You will receive an email notification within 24 hours.', 'success')

                threading.Timer(2.0, lambda: process_single_application(application_id)).start()
                try:
                    email_system.send_confirmation_email(application_data)
                except Exception as e:
                    print(f"Error sending confirmation email: {e}")
                
                return redirect(url_for('index'))
            else:
                flash('Invalid file format. Please upload a PDF, DOC, or DOCX file.', 'error')
                
        except Exception as e:
            flash(f'Error submitting application: {str(e)}', 'error')
    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
