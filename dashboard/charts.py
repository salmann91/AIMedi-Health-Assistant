import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict

class DashboardCharts:
    @staticmethod
    def create_risk_gauge(risk_score: int, risk_level: str):
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Overall Risk: {risk_level}"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgreen"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': risk_score
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
    
    @staticmethod
    def create_parameter_comparison(results: List[Dict]):
        abnormal_params = [r for r in results if r['status'] != 'Normal']
        
        if not abnormal_params:
            return None
        
        params = [r['parameter'].replace('_', ' ').title() for r in abnormal_params]
        values = [r['value'] for r in abnormal_params]
        colors = [r.get('color', 'gray') for r in abnormal_params]
        
        fig = go.Figure(data=[
            go.Bar(
                x=params,
                y=values,
                marker_color=colors,
                text=values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Abnormal Parameters",
            xaxis_title="Parameter",
            yaxis_title="Value",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_severity_pie(results: List[Dict]):
        severity_counts = {}
        for r in results:
            severity = r.get('severity', 'Normal')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(severity_counts.keys()),
            values=list(severity_counts.values()),
            hole=.3
        )])
        
        fig.update_layout(
            title="Results by Severity",
            height=350
        )
        
        return fig
    
    @staticmethod
    def create_risk_breakdown(risks: Dict):
        detected_risks = {k: v for k, v in risks.items() if v.get('detected', False)}
        
        if not detected_risks:
            return None
        
        risk_names = [k.replace('_', ' ').title() for k in detected_risks.keys()]
        risk_scores = [v['score'] for v in detected_risks.values()]
        risk_severities = [v.get('severity', 'Unknown') for v in detected_risks.values()]
        
        colors = {
            'High': 'red',
            'Moderate': 'orange',
            'Low': 'yellow',
            'Unknown': 'gray'
        }
        
        bar_colors = [colors.get(s, 'gray') for s in risk_severities]
        
        fig = go.Figure(data=[
            go.Bar(
                y=risk_names,
                x=risk_scores,
                orientation='h',
                marker_color=bar_colors,
                text=risk_severities,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Risk Category Breakdown",
            xaxis_title="Risk Score",
            yaxis_title="Risk Category",
            height=300
        )
        
        return fig
