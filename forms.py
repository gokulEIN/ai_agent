from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, EmailField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class JobApplicationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    
    position_applied = SelectField('Position Applied For', 
                                 choices=[('AI Engineer', 'AI Engineer'),
                                        ('Full Stack Developer', 'Full Stack Developer'),
                                        ('Frontend Developer', 'Frontend Developer'),
                                        ('Backend Developer', 'Backend Developer'),
                                        ('Data Scientist', 'Data Scientist'),
                                        ('DevOps Engineer', 'DevOps Engineer'),
                                        ('Mobile Developer', 'Mobile Developer'),
                                        ('UI/UX Designer', 'UI/UX Designer'),
                                        ('Product Manager', 'Product Manager'),
                                        ('QA Engineer', 'QA Engineer')],
                                 validators=[DataRequired()])
    experience_level = SelectField('Experience Level', 
                                 choices=[('entry', 'Entry Level (0-2 years)'),
                                        ('mid', 'Mid Level (3-5 years)'),
                                        ('senior', 'Senior Level (6+ years)')],
                                 validators=[DataRequired()])
    
    resume = FileField('Resume (PDF/DOC/DOCX)', 
                      validators=[FileRequired(), 
                                FileAllowed(['pdf', 'doc', 'docx'], 
                                          'Only PDF, DOC, and DOCX files are allowed!')])
    
    cover_letter = TextAreaField('Cover Letter (Optional)', 
                               validators=[Length(max=1000)])
    
    submit = SubmitField('Submit Application')

class JobDescriptionForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    job_description = TextAreaField('Job Description', 
                                  validators=[DataRequired(), Length(min=50, max=2000)])
    required_skills = TextAreaField('Required Skills (comma-separated)', 
                                  validators=[DataRequired(), Length(max=500)])
    experience_required = SelectField('Experience Required', 
                                    choices=[('entry', 'Entry Level (0-2 years)'),
                                           ('mid', 'Mid Level (3-5 years)'),
                                           ('senior', 'Senior Level (6+ years)')],
                                    validators=[DataRequired()])
    submit = SubmitField('Save Job Description')
