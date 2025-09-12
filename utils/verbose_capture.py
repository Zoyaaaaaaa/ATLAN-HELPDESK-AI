import sys
from typing import List
from contextlib import contextmanager

class VerboseCapture:
    """Enhanced verbose output capture with better formatting"""
    
    def __init__(self):
        self.output: List[str] = []
        self.original_stdout = None
    
    def write(self, text: str) -> int:
        """Write text to capture buffer"""
        if text.strip():
            # Clean and format the text
            cleaned_text = text.strip()
            if cleaned_text:
                self.output.append(cleaned_text)
        return len(text)
    
    def flush(self):
        """Flush method for stdout compatibility"""
        pass
    
    def get_output(self) -> str:
        """Get formatted output as string"""
        if not self.output:
            return "No verbose output captured"
        
        formatted_output = []
        for line in self.output:
            # Add timestamp-like prefix for better readability
            formatted_output.append(f"[AGENT] {line}")
        
        return '\n'.join(formatted_output)
    
    def get_output_list(self) -> List[str]:
        """Get output as list of strings"""
        return self.output.copy()
    
    def clear(self):
        """Clear captured output"""
        self.output.clear()
    
    def is_empty(self) -> bool:
        """Check if capture is empty"""
        return len(self.output) == 0
    
    @contextmanager
    def capture_stdout(self):
        """Context manager to capture stdout"""
        original_stdout = sys.stdout
        try:
            sys.stdout = self
            yield self
        finally:
            sys.stdout = original_stdout
