from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd
import json
from datetime import datetime
from typing import Dict
import io

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def generate_pdf_report(self, analysis: Dict, ai_summary: str, patient_info: Dict = None) -> bytes:
        """Generate PDF report"""
        buffer = io.BytesIO()
        try:
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
            story = []
        
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph("🏥 AI Health Diagnostics Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Patient Information
            if patient_info and any(patient_info.values()):
                story.append(Paragraph("Patient Information", self.styles['Heading2']))
                
                patient_data = []
                if patient_info.get('name'):
                    patient_data.append(['Name:', patient_info['name']])
                if patient_info.get('age'):
                    patient_data.append(['Age:', f"{patient_info['age']} years"])
                if patient_info.get('gender'):
                    patient_data.append(['Gender:', patient_info['gender']])
                if patient_info.get('report_date'):
                    patient_data.append(['Report Date:', patient_info['report_date']])
                if patient_info.get('report_id'):
                    patient_data.append(['Report ID:', patient_info['report_id']])
                
                if patient_data:
                    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
                    patient_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('PADDING', (0, 0), (-1, -1), 8),
                    ]))
                    story.append(patient_table)
                    story.append(Spacer(1, 0.3*inch))
            
            # Risk Assessment
            risk_data = analysis.get('risk_assessment', {})
            story.append(Paragraph("Risk Assessment", self.styles['Heading2']))
            
            risk_table_data = [
                ['Overall Risk Score', f"{risk_data.get('overall_risk_score', 0)}/100"],
                ['Risk Level', risk_data.get('risk_level', 'Unknown')],
                ['Critical Findings', str(len(analysis.get('critical_findings', [])))]
            ]
            
            risk_table = Table(risk_table_data, colWidths=[3*inch, 3*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0f0f0')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(risk_table)
            story.append(Spacer(1, 0.3*inch))
            
            # AI Summary
            story.append(Paragraph("AI-Generated Health Summary", self.styles['Heading2']))
            summary_style = ParagraphStyle(
                'Summary',
                parent=self.styles['BodyText'],
                fontSize=10,
                leading=14,
                spaceAfter=10
            )
            
            # Split summary into paragraphs
            for para in ai_summary.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.replace('\n', '<br/>'), summary_style))
            
            story.append(Spacer(1, 0.3*inch))
            
            # Test Results Table
            story.append(Paragraph("Detailed Test Results", self.styles['Heading2']))
            
            results_data = [['Parameter', 'Value', 'Status', 'Severity', 'Reference Range']]
            
            for r in analysis.get('results', []):
                results_data.append([
                    r['parameter'].replace('_', ' ').title(),
                    f"{r['value']} {r.get('unit', '')}",
                    r['status'],
                    r.get('severity', 'Normal'),
                    f"{r['reference_min']}-{r['reference_max']}"
                ])
            
            results_table = Table(results_data, colWidths=[1.8*inch, 1.2*inch, 1*inch, 1*inch, 1.5*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(results_table)
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            story.append(Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                f"AI Health Diagnostics Assistant | Powered by Groq AI<br/>"
                f"<b>Disclaimer:</b> This report is for informational purposes only. "
                f"Consult a healthcare professional for medical advice.",
                footer_style
            ))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        finally:
            buffer.close()
    
    def generate_csv_report(self, analysis: Dict, patient_info: Dict = None) -> str:
        """Generate CSV report"""
        # Create DataFrame
        results_df = pd.DataFrame([
            {
                'Parameter': r['parameter'].replace('_', ' ').title(),
                'Value': r['value'],
                'Unit': r.get('unit', ''),
                'Status': r['status'],
                'Severity': r.get('severity', 'Normal'),
                'Reference Min': r['reference_min'],
                'Reference Max': r['reference_max']
            }
            for r in analysis.get('results', [])
        ])
        
        # Add metadata rows
        metadata_rows = []
        
        if patient_info:
            if patient_info.get('name'):
                metadata_rows.append({'Parameter': 'Patient Name', 'Value': patient_info['name'], 'Unit': '', 'Status': '', 'Severity': '', 'Reference Min': '', 'Reference Max': ''})
            if patient_info.get('age'):
                metadata_rows.append({'Parameter': 'Age', 'Value': patient_info['age'], 'Unit': 'years', 'Status': '', 'Severity': '', 'Reference Min': '', 'Reference Max': ''})
            if patient_info.get('gender'):
                metadata_rows.append({'Parameter': 'Gender', 'Value': patient_info['gender'], 'Unit': '', 'Status': '', 'Severity': '', 'Reference Min': '', 'Reference Max': ''})
            if patient_info.get('report_date'):
                metadata_rows.append({'Parameter': 'Report Date', 'Value': patient_info['report_date'], 'Unit': '', 'Status': '', 'Severity': '', 'Reference Min': '', 'Reference Max': ''})
        
        risk_data = analysis.get('risk_assessment', {})
        metadata_rows.extend([
            {'Parameter': 'Overall Risk Score', 'Value': risk_data.get('overall_risk_score', 0), 'Unit': '/100', 'Status': '', 'Severity': '', 'Reference Min': '', 'Reference Max': ''},
            {'Parameter': 'Risk Level', 'Value': risk_data.get('risk_level', 'Unknown'), 'Unit': '', 'Status': '', 'Severity': '', 'Reference Min': '', 'Reference Max': ''},
            {'Parameter': '', 'Value': '', 'Unit': '', 'Status': '', 'Severity': '', 'Reference Min': '', 'Reference Max': ''},  # Empty row
        ])
        
        metadata_df = pd.DataFrame(metadata_rows)
        
        # Combine
        final_df = pd.concat([metadata_df, results_df], ignore_index=True)
        
        return final_df.to_csv(index=False)
    
    def generate_json_report(self, analysis: Dict, ai_summary: str, patient_info: Dict = None) -> str:
        """Generate JSON report"""
        report = {
            'report_metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'generator': 'AI Health Diagnostics Assistant',
                'version': '2.0'
            },
            'patient_information': patient_info or {},
            'risk_assessment': analysis.get('risk_assessment', {}),
            'ai_summary': ai_summary,
            'test_results': analysis.get('results', []),
            'critical_findings': analysis.get('critical_findings', [])
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)
