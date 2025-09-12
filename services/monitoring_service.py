import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import queue

class SystemMonitor:
    def __init__(self):
        self.metrics_queue = queue.Queue()
        self.alerts = []
        self.performance_history = []
        self.start_time = datetime.now()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'network_io': dict(psutil.net_io_counters()._asdict()),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        uptime = datetime.now() - self.start_time
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0],
            'total_requests': len(self.performance_history),
            'avg_response_time': self._calculate_avg_response_time(),
            'error_rate': self._calculate_error_rate(),
            'active_sessions': 1,  # Placeholder for Streamlit
            'cache_hit_rate': 0.85,  # Simulated
        }
    
    def log_request_metrics(self, endpoint: str, response_time: float, success: bool):
        """Log request performance metrics"""
        metric = {
            'endpoint': endpoint,
            'response_time': response_time,
            'success': success,
            'timestamp': datetime.now()
        }
        
        self.performance_history.append(metric)
        
        # Keep only last 1000 requests
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        
        # Check for performance alerts
        self._check_performance_alerts(metric)
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.performance_history:
            return 0.0
        
        recent_requests = [
            req for req in self.performance_history 
            if req['timestamp'] > datetime.now() - timedelta(minutes=5)
        ]
        
        if not recent_requests:
            return 0.0
        
        return round(sum(req['response_time'] for req in recent_requests) / len(recent_requests), 2)
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if not self.performance_history:
            return 0.0
        
        recent_requests = [
            req for req in self.performance_history 
            if req['timestamp'] > datetime.now() - timedelta(minutes=5)
        ]
        
        if not recent_requests:
            return 0.0
        
        errors = sum(1 for req in recent_requests if not req['success'])
        return round((errors / len(recent_requests)) * 100, 1)
    
    def _check_performance_alerts(self, metric: Dict):
        """Check for performance issues and create alerts"""
        alerts_to_add = []
        
        # High response time alert
        if metric['response_time'] > 5.0:
            alerts_to_add.append({
                'type': 'warning',
                'title': 'High Response Time',
                'message': f"Response time of {metric['response_time']:.2f}s exceeded threshold",
                'timestamp': datetime.now(),
                'endpoint': metric['endpoint']
            })
        
        # System resource alerts
        system_metrics = self.get_system_metrics()
        if 'cpu_percent' in system_metrics and system_metrics['cpu_percent'] > 80:
            alerts_to_add.append({
                'type': 'critical',
                'title': 'High CPU Usage',
                'message': f"CPU usage at {system_metrics['cpu_percent']:.1f}%",
                'timestamp': datetime.now()
            })
        
        if 'memory_percent' in system_metrics and system_metrics['memory_percent'] > 85:
            alerts_to_add.append({
                'type': 'warning',
                'title': 'High Memory Usage',
                'message': f"Memory usage at {system_metrics['memory_percent']:.1f}%",
                'timestamp': datetime.now()
            })
        
        # Add new alerts
        self.alerts.extend(alerts_to_add)
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics()
        
        # Determine health status
        health_score = 100
        status = 'healthy'
        issues = []
        
        if 'cpu_percent' in system_metrics:
            if system_metrics['cpu_percent'] > 90:
                health_score -= 30
                status = 'critical'
                issues.append('High CPU usage')
            elif system_metrics['cpu_percent'] > 70:
                health_score -= 15
                status = 'warning'
                issues.append('Elevated CPU usage')
        
        if 'memory_percent' in system_metrics:
            if system_metrics['memory_percent'] > 90:
                health_score -= 25
                status = 'critical'
                issues.append('High memory usage')
            elif system_metrics['memory_percent'] > 75:
                health_score -= 10
                status = 'warning'
                issues.append('Elevated memory usage')
        
        if app_metrics['error_rate'] > 10:
            health_score -= 20
            status = 'warning'
            issues.append('High error rate')
        
        if app_metrics['avg_response_time'] > 3.0:
            health_score -= 15
            issues.append('Slow response times')
        
        return {
            'status': status,
            'health_score': max(health_score, 0),
            'issues': issues,
            'last_check': datetime.now().isoformat(),
            'uptime': app_metrics['uptime_formatted']
        }
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts"""
        return sorted(self.alerts, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.performance_history:
            return {'message': 'No performance data available'}
        
        # Calculate statistics
        response_times = [req['response_time'] for req in self.performance_history]
        success_rate = (sum(1 for req in self.performance_history if req['success']) / len(self.performance_history)) * 100
        
        # Endpoint statistics
        endpoint_stats = {}
        for req in self.performance_history:
            endpoint = req['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'count': 0, 'total_time': 0, 'errors': 0}
            
            endpoint_stats[endpoint]['count'] += 1
            endpoint_stats[endpoint]['total_time'] += req['response_time']
            if not req['success']:
                endpoint_stats[endpoint]['errors'] += 1
        
        # Format endpoint statistics
        formatted_endpoint_stats = {}
        for endpoint, stats in endpoint_stats.items():
            formatted_endpoint_stats[endpoint] = {
                'request_count': stats['count'],
                'avg_response_time': round(stats['total_time'] / stats['count'], 2),
                'error_rate': round((stats['errors'] / stats['count']) * 100, 1)
            }
        
        return {
            'total_requests': len(self.performance_history),
            'avg_response_time': round(sum(response_times) / len(response_times), 2),
            'min_response_time': round(min(response_times), 2),
            'max_response_time': round(max(response_times), 2),
            'success_rate': round(success_rate, 1),
            'endpoint_statistics': formatted_endpoint_stats,
            'report_generated': datetime.now().isoformat()
        }

# Performance monitoring decorator
def monitor_performance(monitor: SystemMonitor, endpoint_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                end_time = time.time()
                response_time = end_time - start_time
                monitor.log_request_metrics(endpoint_name, response_time, success)
        
        return wrapper
    return decorator