# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# from typing import Dict, List, Any
# import numpy as np

# class TicketAnalytics:
#     def __init__(self):
#         self.response_time_targets = {
#             'P0 (High)': 4,    # 4 hours
#             'P1 (Medium)': 24,  # 24 hours
#             'P2 (Low)': 72      # 72 hours
#         }
    
#     def generate_topic_trends(self, tickets: List[Dict]) -> Dict:
#         """Generate topic trend analysis"""
#         df = pd.DataFrame([
#             {
#                 'topic': topic,
#                 'ticket_id': ticket['id'],
#                 'created_at': ticket.get('created_at', datetime.now().isoformat()),
#                 'priority': ticket['classification']['priority']
#             }
#             for ticket in tickets
#             for topic in ticket['classification']['topic_tags']
#         ])
        
#         # Topic frequency
#         topic_counts = df['topic'].value_counts().to_dict()
        
#         # Priority distribution by topic
#         priority_by_topic = df.groupby(['topic', 'priority']).size().unstack(fill_value=0)
        
#         return {
#             'topic_frequency': topic_counts,
#             'priority_distribution': priority_by_topic.to_dict(),
#             'trending_topics': list(topic_counts.keys())[:5]
#         }
    
#     def calculate_satisfaction_metrics(self, tickets: List[Dict]) -> Dict:
#         """Calculate customer satisfaction metrics"""
#         sentiment_scores = {
#             'Frustrated': 1,
#             'Angry': 0,
#             'Neutral': 3,
#             'Curious': 4
#         }
        
#         sentiments = [ticket['classification']['sentiment'] for ticket in tickets]
#         avg_satisfaction = np.mean([sentiment_scores.get(s, 2) for s in sentiments])
        
#         return {
#             'average_satisfaction': round(avg_satisfaction, 2),
#             'satisfaction_distribution': pd.Series(sentiments).value_counts().to_dict(),
#             'satisfaction_trend': 'stable',  # Would need historical data
#             'nps_score': round((avg_satisfaction / 4) * 100, 1)
#         }
    
#     def generate_workload_distribution(self, tickets: List[Dict]) -> Dict:
#         """Analyze workload distribution"""
#         priority_counts = {}
#         for ticket in tickets:
#             priority = ticket['classification']['priority']
#             priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
#         # Calculate estimated effort hours
#         effort_multipliers = {'P0 (High)': 4, 'P1 (Medium)': 2, 'P2 (Low)': 1}
#         total_effort = sum(priority_counts.get(p, 0) * effort_multipliers[p] for p in effort_multipliers)
        
#         return {
#             'priority_distribution': priority_counts,
#             'estimated_total_effort_hours': total_effort,
#             'high_priority_percentage': round((priority_counts.get('P0 (High)', 0) / len(tickets)) * 100, 1),
#             'workload_balance': 'high' if total_effort > 50 else 'normal'
#         }
    
#     def create_plotly_charts(self, tickets: List[Dict]) -> Dict:
#         """Create interactive Plotly charts"""
#         # Topic distribution pie chart
#         topic_counts = {}
#         for ticket in tickets:
#             for topic in ticket['classification']['topic_tags']:
#                 topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
#         topic_pie = px.pie(
#             values=list(topic_counts.values()),
#             names=list(topic_counts.keys()),
#             title="Topic Distribution",
#             color_discrete_sequence=px.colors.qualitative.Set3
#         )
        
#         # Sentiment timeline
#         sentiment_data = []
#         for i, ticket in enumerate(tickets):
#             sentiment_data.append({
#                 'ticket_number': i + 1,
#                 'sentiment': ticket['classification']['sentiment'],
#                 'priority': ticket['classification']['priority']
#             })
        
#         df = pd.DataFrame(sentiment_data)
#         sentiment_timeline = px.scatter(
#             df, 
#             x='ticket_number', 
#             y='sentiment',
#             color='priority',
#             title="Sentiment Timeline",
#             color_discrete_map={
#                 'P0 (High)': '#FF6B6B',
#                 'P1 (Medium)': '#FFD93D',
#                 'P2 (Low)': '#6BCF7F'
#             }
#         )
        
#         # Priority heatmap
#         priority_topic_data = []
#         for ticket in tickets:
#             for topic in ticket['classification']['topic_tags']:
#                 priority_topic_data.append({
#                     'topic': topic,
#                     'priority': ticket['classification']['priority']
#                 })
        
#         heatmap_df = pd.DataFrame(priority_topic_data)
#         heatmap_pivot = heatmap_df.groupby(['topic', 'priority']).size().unstack(fill_value=0)
        
#         heatmap = px.imshow(
#             heatmap_pivot.values,
#             x=heatmap_pivot.columns,
#             y=heatmap_pivot.index,
#             title="Topic vs Priority Heatmap",
#             aspect="auto",
#             color_continuous_scale="Viridis"
#         )
        
#         return {
#             'topic_pie': topic_pie.to_json(),
#             'sentiment_timeline': sentiment_timeline.to_json(),
#             'priority_heatmap': heatmap.to_json()
#         }
    
#     def generate_performance_metrics(self, tickets: List[Dict]) -> Dict:
#         """Generate performance and efficiency metrics"""
#         total_tickets = len(tickets)
        
#         # Classification accuracy (simulated)
#         classification_confidence = np.random.uniform(0.85, 0.98, total_tickets)
#         avg_confidence = round(np.mean(classification_confidence), 3)
        
#         # Processing efficiency
#         processing_times = np.random.uniform(1.2, 4.5, total_tickets)  # Simulated processing times
#         avg_processing_time = round(np.mean(processing_times), 2)
        
#         # Auto-resolution rate
#         rag_topics = ["How-to", "Product", "Best practices", "API/SDK", "SSO"]
#         auto_resolvable = sum(1 for ticket in tickets 
#                             if any(topic in rag_topics for topic in ticket['classification']['topic_tags']))
#         auto_resolution_rate = round((auto_resolvable / total_tickets) * 100, 1)
        
#         return {
#             'total_processed': total_tickets,
#             'avg_classification_confidence': avg_confidence,
#             'avg_processing_time_seconds': avg_processing_time,
#             'auto_resolution_rate_percent': auto_resolution_rate,
#             'efficiency_score': round((avg_confidence * 100 + auto_resolution_rate) / 2, 1)
#         }
    
#     def generate_recommendations(self, tickets: List[Dict]) -> List[Dict]:
#         """Generate actionable recommendations"""
#         recommendations = []
        
#         # Analyze topic patterns
#         topic_counts = {}
#         frustrated_topics = {}
        
#         for ticket in tickets:
#             sentiment = ticket['classification']['sentiment']
#             for topic in ticket['classification']['topic_tags']:
#                 topic_counts[topic] = topic_counts.get(topic, 0) + 1
#                 if sentiment in ['Frustrated', 'Angry']:
#                     frustrated_topics[topic] = frustrated_topics.get(topic, 0) + 1
        
#         # High volume topics
#         most_common_topic = max(topic_counts, key=topic_counts.get)
#         if topic_counts[most_common_topic] > len(tickets) * 0.3:
#             recommendations.append({
#                 'type': 'Knowledge Base',
#                 'priority': 'High',
#                 'title': f'Expand {most_common_topic} Documentation',
#                 'description': f'{most_common_topic} accounts for {round((topic_counts[most_common_topic]/len(tickets))*100, 1)}% of tickets. Consider expanding documentation.',
#                 'action': f'Add more detailed guides for {most_common_topic.lower()} topics'
#             })
        
#         # High frustration topics
#         if frustrated_topics:
#             most_frustrating = max(frustrated_topics, key=frustrated_topics.get)
#             recommendations.append({
#                 'type': 'Process Improvement',
#                 'priority': 'Medium',
#                 'title': f'Address {most_frustrating} Frustration',
#                 'description': f'{most_frustrating} topics cause high frustration. Review user experience.',
#                 'action': f'Investigate common pain points in {most_frustrating.lower()} workflows'
#             })
        
#         # Priority distribution
#         high_priority = sum(1 for ticket in tickets if ticket['classification']['priority'] == 'P0 (High)')
#         if high_priority > len(tickets) * 0.4:
#             recommendations.append({
#                 'type': 'Resource Allocation',
#                 'priority': 'High',
#                 'title': 'High Priority Ticket Volume',
#                 'description': f'{round((high_priority/len(tickets))*100, 1)}% of tickets are high priority. Consider resource allocation.',
#                 'action': 'Increase support team capacity or implement triage process'
#             })
        
#         return recommendations

# # Create a global instance for module-level access
# _analytics_instance = TicketAnalytics()

# # Module-level functions that delegate to the class instance
# def generate_topic_trends(tickets: List[Dict]) -> Dict:
#     return _analytics_instance.generate_topic_trends(tickets)

# def calculate_satisfaction_metrics(tickets: List[Dict]) -> Dict:
#     return _analytics_instance.calculate_satisfaction_metrics(tickets)

# def generate_workload_distribution(tickets: List[Dict]) -> Dict:
#     return _analytics_instance.generate_workload_distribution(tickets)

# def create_plotly_charts(tickets: List[Dict]) -> Dict:
#     return _analytics_instance.create_plotly_charts(tickets)

# def generate_performance_metrics(tickets: List[Dict]) -> Dict:
#     return _analytics_instance.generate_performance_metrics(tickets)

# def generate_recommendations(tickets: List[Dict]) -> List[Dict]:
#     return _analytics_instance.generate_recommendations(tickets)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np

class TicketAnalytics:
    def __init__(self):
        self.response_time_targets = {
            'P0 (High)': 4,    # 4 hours
            'P1 (Medium)': 24,  # 24 hours
            'P2 (Low)': 72      # 72 hours
        }
    
    def generate_topic_trends(self, tickets: List[Dict]) -> Dict:
        """Generate topic trend analysis"""
        df = pd.DataFrame([
            {
                'topic': topic,
                'ticket_id': ticket['id'],
                'created_at': ticket.get('created_at', datetime.now().isoformat()),
                'priority': ticket['classification']['priority']
            }
            for ticket in tickets
            for topic in ticket['classification']['topic_tags']
        ])
        
        # Topic frequency
        topic_counts = df['topic'].value_counts().to_dict()
        
        # Priority distribution by topic
        priority_by_topic = df.groupby(['topic', 'priority']).size().unstack(fill_value=0)
        
        return {
            'topic_frequency': topic_counts,
            'priority_distribution': priority_by_topic.to_dict(),
            'trending_topics': list(topic_counts.keys())[:5]
        }
    
    def calculate_satisfaction_metrics(self, tickets: List[Dict]) -> Dict:
        """Calculate customer satisfaction metrics"""
        sentiment_scores = {
            'Frustrated': 1,
            'Angry': 0,
            'Neutral': 3,
            'Curious': 4
        }
        
        sentiments = [ticket['classification']['sentiment'] for ticket in tickets]
        avg_satisfaction = np.mean([sentiment_scores.get(s, 2) for s in sentiments])
        
        return {
            'average_satisfaction': round(avg_satisfaction, 2),
            'satisfaction_distribution': pd.Series(sentiments).value_counts().to_dict(),
            'satisfaction_trend': 'stable',  # Would need historical data
            'nps_score': round((avg_satisfaction / 4) * 100, 1)
        }
    
    def generate_workload_distribution(self, tickets: List[Dict]) -> Dict:
        """Analyze workload distribution"""
        priority_counts = {}
        for ticket in tickets:
            priority = ticket['classification']['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Calculate estimated effort hours
        effort_multipliers = {'P0 (High)': 4, 'P1 (Medium)': 2, 'P2 (Low)': 1}
        total_effort = sum(priority_counts.get(p, 0) * effort_multipliers[p] for p in effort_multipliers)
        
        return {
            'priority_distribution': priority_counts,
            'estimated_total_effort_hours': total_effort,
            'high_priority_percentage': round((priority_counts.get('P0 (High)', 0) / len(tickets)) * 100, 1),
            'workload_balance': 'high' if total_effort > 50 else 'normal'
        }
    
    def create_plotly_charts(self, tickets: List[Dict]) -> Dict:
        """Create interactive Plotly charts"""
        # Topic distribution pie chart
        topic_counts = {}
        for ticket in tickets:
            for topic in ticket['classification']['topic_tags']:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        topic_pie = px.pie(
            values=list(topic_counts.values()),
            names=list(topic_counts.keys()),
            title="Topic Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        # Sentiment timeline
        sentiment_data = []
        for i, ticket in enumerate(tickets):
            sentiment_data.append({
                'ticket_number': i + 1,
                'sentiment': ticket['classification']['sentiment'],
                'priority': ticket['classification']['priority']
            })
        
        df = pd.DataFrame(sentiment_data)
        sentiment_timeline = px.scatter(
            df, 
            x='ticket_number', 
            y='sentiment',
            color='priority',
            title="Sentiment Timeline",
            color_discrete_map={
                'P0 (High)': '#FF6B6B',
                'P1 (Medium)': '#FFD93D',
                'P2 (Low)': '#6BCF7F'
            }
        )
        
        # Priority heatmap
        priority_topic_data = []
        for ticket in tickets:
            for topic in ticket['classification']['topic_tags']:
                priority_topic_data.append({
                    'topic': topic,
                    'priority': ticket['classification']['priority']
                })
        
        heatmap_df = pd.DataFrame(priority_topic_data)
        heatmap_pivot = heatmap_df.groupby(['topic', 'priority']).size().unstack(fill_value=0)
        
        heatmap = px.imshow(
            heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            title="Topic vs Priority Heatmap",
            aspect="auto",
            color_continuous_scale="Viridis"
        )
        
        return {
            'topic_pie': topic_pie.to_json(),
            'sentiment_timeline': sentiment_timeline.to_json(),
            'priority_heatmap': heatmap.to_json()
        }
    
    def generate_performance_metrics(self, tickets: List[Dict]) -> Dict:
        """Generate performance and efficiency metrics"""
        total_tickets = len(tickets)
        
        # Classification accuracy (simulated)
        classification_confidence = np.random.uniform(0.85, 0.98, total_tickets)
        avg_confidence = round(np.mean(classification_confidence), 3)
        
        # Processing efficiency
        processing_times = np.random.uniform(1.2, 4.5, total_tickets)  # Simulated processing times
        avg_processing_time = round(np.mean(processing_times), 2)
        
        # Auto-resolution rate
        rag_topics = ["How-to", "Product", "Best practices", "API/SDK", "SSO"]
        auto_resolvable = sum(1 for ticket in tickets 
                            if any(topic in rag_topics for topic in ticket['classification']['topic_tags']))
        auto_resolution_rate = round((auto_resolvable / total_tickets) * 100, 1)
        
        return {
            'total_processed': total_tickets,
            'avg_classification_confidence': avg_confidence,
            'avg_processing_time_seconds': avg_processing_time,
            'auto_resolution_rate_percent': auto_resolution_rate,
            'efficiency_score': round((avg_confidence * 100 + auto_resolution_rate) / 2, 1)
        }
    
    def generate_recommendations(self, tickets: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Analyze topic patterns
        topic_counts = {}
        frustrated_topics = {}
        
        for ticket in tickets:
            sentiment = ticket['classification']['sentiment']
            for topic in ticket['classification']['topic_tags']:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
                if sentiment in ['Frustrated', 'Angry']:
                    frustrated_topics[topic] = frustrated_topics.get(topic, 0) + 1
        
        # High volume topics
        most_common_topic = max(topic_counts, key=topic_counts.get)
        if topic_counts[most_common_topic] > len(tickets) * 0.3:
            recommendations.append({
                'type': 'Knowledge Base',
                'priority': 'High',
                'title': f'Expand {most_common_topic} Documentation',
                'description': f'{most_common_topic} accounts for {round((topic_counts[most_common_topic]/len(tickets))*100, 1)}% of tickets. Consider expanding documentation.',
                'action': f'Add more detailed guides for {most_common_topic.lower()} topics'
            })
        
        # High frustration topics
        if frustrated_topics:
            most_frustrating = max(frustrated_topics, key=frustrated_topics.get)
            recommendations.append({
                'type': 'Process Improvement',
                'priority': 'Medium',
                'title': f'Address {most_frustrating} Frustration',
                'description': f'{most_frustrating} topics cause high frustration. Review user experience.',
                'action': f'Investigate common pain points in {most_frustrating.lower()} workflows'
            })
        
        # Priority distribution
        high_priority = sum(1 for ticket in tickets if ticket['classification']['priority'] == 'P0 (High)')
        if high_priority > len(tickets) * 0.4:
            recommendations.append({
                'type': 'Resource Allocation',
                'priority': 'High',
                'title': 'High Priority Ticket Volume',
                'description': f'{round((high_priority/len(tickets))*100, 1)}% of tickets are high priority. Consider resource allocation.',
                'action': 'Increase support team capacity or implement triage process'
            })
        
        return recommendations

# Create a global instance for module-level access
_analytics_instance = TicketAnalytics()

# Module-level functions that delegate to the class instance
def generate_topic_trends(tickets: List[Dict]) -> Dict:
    return _analytics_instance.generate_topic_trends(tickets)

def calculate_satisfaction_metrics(tickets: List[Dict]) -> Dict:
    return _analytics_instance.calculate_satisfaction_metrics(tickets)

def generate_workload_distribution(tickets: List[Dict]) -> Dict:
    return _analytics_instance.generate_workload_distribution(tickets)

def create_plotly_charts(tickets: List[Dict]) -> Dict:
    return _analytics_instance.create_plotly_charts(tickets)

def generate_performance_metrics(tickets: List[Dict]) -> Dict:
    return _analytics_instance.generate_performance_metrics(tickets)

