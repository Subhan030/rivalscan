from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class AgentState(TypedDict):
    competitor_id: int
    competitor_name: str
    competitor_domain: str
    
    plan: Optional[Dict[str, Any]] 
    raw_findings: List[Dict[str, Any]] 
    insights: Optional[Dict[str, Any]] 
    recommendations: Optional[Dict[str, Any]] 
    report_summary: Optional[str] 
    report_id: Optional[int] 
