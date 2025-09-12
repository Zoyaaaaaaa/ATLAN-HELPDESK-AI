def get_custom_css() -> str:
    """Return custom CSS styles for the application"""
    return """
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .ticket-card {
            background: linear-gradient(145deg, #f8f9fa, #e9ecef);
            padding: 1.5rem;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .ticket-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .classification-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .tag {
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .topic-tag { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .sentiment-frustrated { background: linear-gradient(135deg, #ff6b6b, #ee5a52); color: white; }
        .sentiment-angry { background: linear-gradient(135deg, #ff8a80, #ff5722); color: white; }
        .sentiment-curious { background: linear-gradient(135deg, #42a5f5, #1976d2); color: white; }
        .sentiment-neutral { background: linear-gradient(135deg, #9c27b0, #673ab7); color: white; }
        .priority-p0-high { background: linear-gradient(135deg, #f44336, #d32f2f); color: white; }
        .priority-p1-medium { background: linear-gradient(135deg, #ff9800, #f57c00); color: white; }
        .priority-p2-low { background: linear-gradient(135deg, #4caf50, #388e3c); color: white; }
        
        .analysis-section {
            background: linear-gradient(145deg, #e3f2fd, #bbdefb);
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #2196f3;
            margin: 1rem 0;
        }
        
        .response-section {
            background: linear-gradient(145deg, #e8f5e8, #c8e6c9);
            padding: 1.5rem;
            border-radius: 12px;
            border: 2px solid #4caf50;
            margin: 1rem 0;
        }
        
        .verbose-output {
            background: #263238;
            color: #00e676;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            max-height: 400px;
            overflow-y: auto;
            margin: 1rem 0;
            border: 1px solid #37474f;
        }
        
        .source-citation {
            background: linear-gradient(145deg, #fff3e0, #ffe0b2);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #ff9800;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-success { background: #4caf50; }
        .status-error { background: #f44336; }
        .status-warning { background: #ff9800; }
        
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-top: 3px solid #667eea;
        }
        
        .error-container {
            background: linear-gradient(145deg, #ffebee, #ffcdd2);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #f44336;
            margin: 1rem 0;
        }
        
        .success-container {
            background: linear-gradient(145deg, #e8f5e8, #c8e6c9);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #4caf50;
            margin: 1rem 0;
        }
    </style>
    """
