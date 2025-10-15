import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List
from config import Config
import os

class EmailSystem:
    
    def __init__(self):
        self.config = Config()
        self.smtp_server = self.config.SMTP_SERVER
        self.smtp_port = self.config.SMTP_PORT
        self.email_address = self.config.EMAIL_ADDRESS
        self.email_password = self.config.EMAIL_PASSWORD
        self.calendly_link = self.config.CALENDLY_LINK
    
    def send_confirmation_email(self, candidate_data: Dict[str, Any]) -> bool:

        try:
            subject = f"Application Received - {candidate_data.get('position_applied', 'Position')}"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2>Thank you for your application!</h2>
                        
                        <p>Dear {candidate_data.get('full_name', 'Candidate')},</p>
                        
                        <p>We have successfully received your application for the <strong>{candidate_data.get('position_applied', 'position')}</strong> role.</p>
                        
                        <div>
                            <h4>Application Details:</h4>
                            <p><strong>Name:</strong> {candidate_data.get('full_name', 'N/A')}</p>
                            <p><strong>Email:</strong> {candidate_data.get('email', 'N/A')}</p>
                            <p><strong>Position:</strong> {candidate_data.get('position_applied', 'N/A')}</p>
                            <p><strong>Experience Level:</strong> {candidate_data.get('experience_level', 'N/A')}</p>
                            <p><strong>Application ID:</strong> {candidate_data.get('id', 'N/A')}</p>
                        </div>
                        
                        <p>Our team will review your application and you will receive an email with our decision within 24-48 hours.</p>
                        
                        <p>Thank you for your interest in joining our team!</p>
                        
                        <p>Best regards,<br>
                        HR Team</p>
                    </div>
                </body>
            </html>
            """
            
            return self._send_email(candidate_data.get('email'), subject, html_body)
            
        except Exception as e:
            print(f"Error sending confirmation email to {candidate_data.get('email', 'unknown')}: {str(e)}")
            return False
    
    def send_selection_email(self, candidate_data: Dict[str, Any]) -> bool:

        try:
            subject = f"Congratulations! You've been selected for {candidate_data.get('position_applied', 'the position')}"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #28a745;">Congratulations!</h2>
                        
                        <p>Dear {candidate_data.get('full_name', 'Candidate')},</p>
                        
                        <p>We are pleased to inform you that you have been <strong>selected</strong> for the <strong>{candidate_data.get('position_applied', 'position')}</strong> role.</p>
                        
                        <h4>Next Steps:</h4>
                        <p>Please schedule an interview using the link below:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{self.calendly_link}" 
                               style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; 
                                      border-radius: 5px; font-weight: bold; display: inline-block;">
                                Schedule Interview
                            </a>
                        </div>
                        
                        <p><strong>Important:</strong> Please schedule your interview within 48 hours.</p>
                        
                        <p>We look forward to meeting you!</p>
                        
                        <p>Best regards,<br>
                        HR Team</p>
                    </div>
                </body>
            </html>
            """
            
            return self._send_email(candidate_data.get('email'), subject, html_body)
            
        except Exception as e:
            print(f"Error sending selection email to {candidate_data.get('email', 'unknown')}: {str(e)}")
            return False
    
    def send_rejection_email(self, candidate_data: Dict[str, Any]) -> bool:
        try:
            print(f"Sending rejection email to: {candidate_data.get('email', 'unknown')}")
            print(f"Candidate data keys: {list(candidate_data.keys())}")
            subject = f"Application Update - {candidate_data.get('position_applied', 'Position')}"
            
            missing_skills = candidate_data.get('skills_match', {}).get('missing_skills', [])
            strengths = candidate_data.get('strengths', [])
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2>Thank you for your application</h2>
                        
                        <p>Dear {candidate_data.get('full_name', 'Candidate')},</p>
                        
                        <p>Thank you for applying for the <strong>{candidate_data.get('position_applied', 'position')}</strong> role. After careful review, we have decided to move forward with other candidates for this position.</p>
                        
                        {f'''<div>
                            <h4>Skills to develop for future opportunities:</h4>
                            <ul style="margin: 10px 0;">
                                {chr(10).join([f'<li><strong>{skill}</strong></li>' for skill in missing_skills[:5]])}
                            </ul>
                            <p style="margin-top: 15px;">Developing these skills will significantly improve your chances for similar roles in the future.</p>
                        </div>''' if missing_skills else ''}
                        
                        
                        <p>We encourage you to continue developing your skills and apply for future positions that match your experience level.</p>
                        
                        <p>Best regards,<br>
                        HR Team</p>
                    </div>
                </body>
            </html>
            """
            
            return self._send_email(candidate_data.get('email'), subject, html_body)
            
        except Exception as e:
            print(f"Error sending rejection email to {candidate_data.get('email', 'unknown')}: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_address
            message["To"] = to_email
            
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, to_email, message.as_string())
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_batch_emails(self, selected_candidates: List[Dict[str, Any]], 
                         rejected_candidates: List[Dict[str, Any]]) -> Dict[str, int]:
        results = {
            'selected_sent': 0,
            'selected_failed': 0,
            'rejected_sent': 0,
            'rejected_failed': 0
        }
        
        for candidate in selected_candidates:
            if self.send_selection_email(candidate):
                results['selected_sent'] += 1
            else:
                results['selected_failed'] += 1
        
        print(f"Processing {len(rejected_candidates)} rejected candidates for emails...")
        for candidate in rejected_candidates:
            print(f"Processing rejection email for: {candidate.get('full_name', 'Unknown')}")
            if self.send_rejection_email(candidate):
                results['rejected_sent'] += 1
                print(f"✓ Rejection email sent successfully")
            else:
                results['rejected_failed'] += 1
                print(f"✗ Rejection email failed")
        
        return results
