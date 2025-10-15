import os
import csv
from datetime import datetime
from typing import List, Dict, Any
from config import Config

class CSVExporter:
    
    def __init__(self):
        self.config = Config()
        self.results_folder = self.config.RESULTS_FOLDER
    
        os.makedirs(self.results_folder, exist_ok=True)
    
    def _adjust_column_widths(self, ws):

        try:
            for col_num in range(1, ws.max_column + 1):
                max_length = 0
                column_letter = ws.cell(row=1, column=col_num).column_letter
                
                for row_num in range(1, ws.max_row + 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
        except Exception as e:
            print(f"Warning: Could not adjust column widths: {e}")
    
    def export_all_candidates(self, applications: List[Dict[str, Any]], 
                             analysis_results: List[Dict[str, Any]], 
                             job_description: Dict[str, Any]) -> str:

        try:
            wb = Workbook()
            wb.remove(wb.active)
 
            self._create_all_candidates_sheet(wb, applications, analysis_results, job_description)
            self._create_summary_sheet(wb, analysis_results, job_description)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_candidates_{timestamp}.xlsx"
            filepath = os.path.join(self.results_folder, filename)
            
            wb.save(filepath)
            print(f"All candidates exported to: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"Error exporting all candidates: {str(e)}")
            return None
    
    def export_results(self, analysis_results: List[Dict[str, Any]], 
                      job_description: Dict[str, Any]) -> str:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_screening_results_{timestamp}.xlsx"
        filepath = os.path.join(self.results_folder, filename)

        wb = Workbook()

        self._create_summary_sheet(wb, analysis_results, job_description)
        self._create_detailed_sheet(wb, analysis_results)
        selected_candidates = [r for r in analysis_results if r.get('recommendation') == 'SELECTED']
        self._create_selected_sheet(wb, selected_candidates)
        rejected_candidates = [r for r in analysis_results if r.get('recommendation') == 'REJECTED']
        self._create_rejected_sheet(wb, rejected_candidates)
        
        wb.save(filepath)
        
        return filepath
    
    def export_all_candidates_csv(self, applications: List[Dict[str, Any]], 
                                 analysis_results: List[Dict[str, Any]], 
                                 job_description: Dict[str, Any]) -> str:

        try:
            analysis_lookup = {result.get('applicant_id'): result for result in analysis_results}

            all_data = []
            for app in applications:
                analysis = analysis_lookup.get(app.get('id'), {})
                skills_match = analysis.get('skills_match', {})
                
                all_data.append({
                    'Application_ID': app.get('id', 'N/A'),
                    'Full_Name': app.get('full_name', 'N/A'),
                    'Email': app.get('email', 'N/A'),
                    'Phone': app.get('phone', 'N/A'),
                    'Position_Applied': app.get('position_applied', 'N/A'),
                    'Experience_Level': app.get('experience_level', 'N/A'),
                    'Application_Date': app.get('created_at', 'N/A'),
                    'Status': app.get('status', 'Pending'),
                    'AI_Score': analysis.get('overall_score', 'N/A'),
                    'Recommendation': analysis.get('recommendation', 'Pending'),
                    'Matched_Skills': '; '.join(skills_match.get('matched_skills', [])),
                    'Missing_Skills': '; '.join(skills_match.get('missing_skills', [])),
                    'Strengths': '; '.join(analysis.get('strengths', [])),
                    'Areas_for_Improvement': '; '.join(analysis.get('weaknesses', [])),
                    'Experience_Assessment': analysis.get('experience_assessment', 'N/A'),
                    'AI_Reasoning': analysis.get('reasoning', 'N/A'),
                    'Resume_File': app.get('resume_filename', 'N/A')
                })
            
            filename = "all_candidates_results.csv"
            filepath = os.path.join(self.results_folder, filename)

            if all_data:
                df = pd.DataFrame(all_data)
                df.to_csv(filepath, index=False, encoding='utf-8')
            else:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Application_ID', 'Full_Name', 'Email', 'Phone', 'Position_Applied', 
                                   'Experience_Level', 'Application_Date', 'Status', 'AI_Score', 
                                   'Recommendation', 'Matched_Skills', 'Missing_Skills', 'Strengths', 
                                   'Areas_for_Improvement', 'Experience_Assessment', 'AI_Reasoning', 
                                   'Resume_File', 'Job_Title'])
                    writer.writerow(['No candidate data available'])
            
            return filepath
            
        except Exception as e:
            print(f"Error exporting candidates to CSV: {str(e)}")
            return None
    
    def export_results_csv(self, analysis_results: List[Dict[str, Any]], 
                          job_description: Dict[str, Any]) -> str:
        try:
            csv_data = []
            for result in analysis_results:
                skills_match = result.get('skills_match', {})
                csv_data.append({
                    'Full_Name': result.get('full_name', 'N/A'),
                    'Email': result.get('email', 'N/A'),
                    'Position_Applied': result.get('position_applied', 'N/A'),
                    'Overall_Score': result.get('overall_score', 0),
                    'Recommendation': result.get('recommendation', 'N/A'),
                    'Matched_Skills': '; '.join(skills_match.get('matched_skills', [])),
                    'Missing_Skills': '; '.join(skills_match.get('missing_skills', [])),
                    'Experience_Assessment': result.get('experience_assessment', 'N/A'),
                    'Strengths': '; '.join(result.get('strengths', [])),
                    'Weaknesses': '; '.join(result.get('weaknesses', [])),
                    'Reasoning': result.get('reasoning', 'N/A'),
                    'Applicant_ID': result.get('applicant_id', 'N/A')
                })
            
            filename = "resume_screening_results.csv"
            filepath = os.path.join(self.results_folder, filename)

            if csv_data:
                df = pd.DataFrame(csv_data)
                df.to_csv(filepath, index=False, encoding='utf-8')
            else:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Full_Name', 'Email', 'Position_Applied', 'Overall_Score', 
                                   'Recommendation', 'Matched_Skills', 'Missing_Skills', 
                                   'Experience_Assessment', 'Strengths', 'Weaknesses', 
                                   'Reasoning', 'Job_Title', 'Applicant_ID'])
                    writer.writerow(['No results available'])
            
            return filepath
            
        except Exception as e:
            print(f"Error exporting results to CSV: {str(e)}")
            return None
    
    def _create_summary_sheet(self, wb: Workbook, results: List[Dict[str, Any]], 
                             job_description: Dict[str, Any]) -> None:
        ws = wb.active
        ws.title = "Summary"
        
        header_font = Font(bold=True, size=14, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

        ws['A1'] = "Resume Screening Results Summary"
        ws['A1'].font = Font(bold=True, size=16)
        ws.merge_cells('A1:D1')
        
        ws['A3'] = "Job Title:"
        ws['B3'] = job_description.get('job_title', 'N/A')
        ws['A4'] = "Total Applications:"
        ws['B4'] = len(results)
        
        ws['A5'] = "Selected:"
        ws['B5'] = selected_count
        ws['A6'] = "Rejected:"
        ws['B6'] = rejected_count
        
        if results:
            avg_score = sum(r.get('overall_score', 0) for r in results) / len(results)
            ws['A7'] = "Average Score:"
            ws['B7'] = f"{avg_score:.2f}/10"
        
        ws['A9'] = "Score Distribution"
        ws['A9'].font = header_font
        ws['A9'].fill = header_fill
        
        score_ranges = [
            ("9-10 (Excellent)", len([r for r in results if r.get('overall_score', 0) >= 9])),
            ("7-8 (Good)", len([r for r in results if 7 <= r.get('overall_score', 0) < 9])),
            ("5-6 (Average)", len([r for r in results if 5 <= r.get('overall_score', 0) < 7])),
            ("0-4 (Below Average)", len([r for r in results if r.get('overall_score', 0) < 5]))
        ]
        
        for i, (range_name, count) in enumerate(score_ranges, 10):
            ws[f'A{i}'] = range_name
            ws[f'B{i}'] = count
        
        self._adjust_column_widths(ws)
    
    def _create_detailed_sheet(self, wb: Workbook, results: List[Dict[str, Any]]) -> None:
        ws = wb.create_sheet("Detailed Results")
        
        detailed_data = []
        for result in results:
            skills_match = result.get('skills_match', {})
            detailed_data.append({
                'Full Name': result.get('full_name', 'N/A'),
                'Email': result.get('email', 'N/A'),
                'Position Applied': result.get('position_applied', 'N/A'),
                'Overall Score': result.get('overall_score', 0),
                'Recommendation': result.get('recommendation', 'N/A'),
                'Matched Skills': ', '.join(skills_match.get('matched_skills', [])),
                'Missing Skills': ', '.join(skills_match.get('missing_skills', [])),
                'Experience Assessment': result.get('experience_assessment', 'N/A'),
                'Strengths': ', '.join(result.get('strengths', [])),
                'Weaknesses': ', '.join(result.get('weaknesses', [])),
                'Reasoning': result.get('reasoning', 'N/A')
            })
        
        df = pd.DataFrame(detailed_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            recommendation_cell = row[4] 
            if recommendation_cell.value == 'SELECTED':
                for cell in row:
                    cell.fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
            elif recommendation_cell.value == 'REJECTED':
                for cell in row:
                    cell.fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
        
        self._adjust_column_widths(ws)
    
    def _create_selected_sheet(self, wb: Workbook, selected_results: List[Dict[str, Any]]) -> None:
        ws = wb.create_sheet("Selected Candidates")
        
        selected_data = []
        for result in selected_results:
            selected_data.append({
                'Full Name': result.get('full_name', 'N/A'),
                'Email': result.get('email', 'N/A'),
                'Position Applied': result.get('position_applied', 'N/A'),
                'Score': result.get('overall_score', 0),
                'Key Strengths': ', '.join(result.get('strengths', [])),
                'Reasoning': result.get('reasoning', 'N/A')
            })
        
        if selected_data:
            df = pd.DataFrame(selected_data)

            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)
            
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="28A745", end_color="28A745", fill_type="solid")
            
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
        else:
            ws['A1'] = "No candidates were selected for this position."
            ws['A1'].font = Font(bold=True, size=12)
        
        self._adjust_column_widths(ws)
    
    def _create_rejected_sheet(self, wb: Workbook, rejected_results: List[Dict[str, Any]]) -> None:
        ws = wb.create_sheet("Rejected Candidates")
        
        rejected_data = []
        for result in rejected_results:
            skills_match = result.get('skills_match', {})
            rejected_data.append({
                'Full Name': result.get('full_name', 'N/A'),
                'Email': result.get('email', 'N/A'),
                'Position Applied': result.get('position_applied', 'N/A'),
                'Score': result.get('overall_score', 0),
                'Missing Skills': ', '.join(skills_match.get('missing_skills', [])),
                'Areas for Improvement': ', '.join(result.get('weaknesses', [])),
                'Reasoning': result.get('reasoning', 'N/A')
            })
        
        if rejected_data:
            df = pd.DataFrame(rejected_data)
            
            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)
 
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="DC3545", end_color="DC3545", fill_type="solid")
            
            for cell in ws[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
        else:
            ws['A1'] = "All candidates were selected for this position."
            ws['A1'].font = Font(bold=True, size=12)

        self._adjust_column_widths(ws)
    
    def _create_all_candidates_sheet(self, wb: Workbook, applications: List[Dict[str, Any]], 
                                   analysis_results: List[Dict[str, Any]], 
                                   job_description: Dict[str, Any]) -> None:
        ws = wb.create_sheet("All Candidates", 0)

        analysis_lookup = {result.get('applicant_id'): result for result in analysis_results}

        all_data = []
        for app in applications:
            analysis = analysis_lookup.get(app.get('id'), {})
            skills_match = analysis.get('skills_match', {})
            
            all_data.append({
                'Application ID': app.get('id', 'N/A'),
                'Full Name': app.get('full_name', 'N/A'),
                'Email': app.get('email', 'N/A'),
                'Phone': app.get('phone', 'N/A'),
                'Position Applied': app.get('position_applied', 'N/A'),
                'Experience Level': app.get('experience_level', 'N/A'),
                'Application Date': app.get('created_at', 'N/A'),
                'Status': app.get('status', 'Pending'),
                'AI Score': analysis.get('overall_score', 'N/A'),
                'Recommendation': analysis.get('recommendation', 'Pending'),
                'Matched Skills': ', '.join(skills_match.get('matched_skills', [])),
                'Missing Skills': ', '.join(skills_match.get('missing_skills', [])),
                'Strengths': '; '.join(analysis.get('strengths', [])),
                'Areas for Improvement': '; '.join(analysis.get('weaknesses', [])),
                'AI Reasoning': analysis.get('reasoning', 'N/A'),
                'Resume File': app.get('resume_filename', 'N/A')
            })
        
        if all_data:
            df = pd.DataFrame(all_data)

            for col_num, column_title in enumerate(df.columns, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.value = column_title
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            for row_num, row_data in enumerate(df.values, 2):
                for col_num, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = value
                    
                    status = row_data[7]
                    if status == 'selected':
                        cell.fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
                    elif status == 'rejected':
                        cell.fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
        else:
            ws['A1'] = "No candidate data available."
            ws['A1'].font = Font(bold=True, size=12)
        
        self._adjust_column_widths(ws)
