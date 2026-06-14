import json
import logging
from typing import cast, Any 
from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.agents.planner import run_planner
from app.agents.researcher import run_researcher
from app.agents.analyzer import run_analyzer
from app.agents.strategist import run_strategist
from app.agents.reporter import run_reporter
from app.tools.web_search import search_web
from app.crud.report import create_report
from app.crud.job import update_job_status
from app.crud.competitor import update_competitor
import datetime

logger = logging.getLogger(__name__)

def planner_node(state: AgentState):
    plan = run_planner(state["competitor_name"], state["competitor_domain"])
    return {"plan": plan.model_dump()}

def researcher_node(state: AgentState):
    plan = state.get("plan") or {}
    items = plan.get("items", [])
    raw_findings = []
    
    for item in items:
        try:
            
            search_results = search_web(item["task"], num_results=3)
            findings_str = json.dumps(search_results)
            
            summary = run_researcher(task=item["task"], findings=findings_str)
            raw_findings.append(summary.model_dump())
        except Exception as e:
            logger.error(f"Error researching item '{item.get('task')}': {e}")
            raw_findings.append({
                "summary": f"Failed to gather research for task: {item.get('task')} due to error.",
                "sources_used": []
            })
            
    return {"raw_findings": raw_findings}

def analyzer_node(state: AgentState):
    raw_findings = state.get("raw_findings", [])
    findings_str = json.dumps(raw_findings)
    insights = run_analyzer(findings_str)
    return {"insights": insights.model_dump()}

def strategist_node(state: AgentState):
    insights = state.get("insights", {})
    insights_str = json.dumps(insights)
    recommendations = run_strategist(insights_str)
    return {"recommendations": recommendations.model_dump()}

def reporter_node(state: AgentState):
    all_data = {
        "competitor": state["competitor_name"],
        "findings": state.get("raw_findings", []),
        "insights": state.get("insights", {}),
        "recommendations": state.get("recommendations", {})
    }
    all_data_str = json.dumps(all_data)
    report = run_reporter(all_data_str)
    return {"report_summary": report.executive_summary}

def build_workflow():
    workflow = StateGraph(AgentState) # type: ignore
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("reporter", reporter_node)
    
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "analyzer")
    workflow.add_edge("analyzer", "strategist")
    workflow.add_edge("strategist", "reporter")
    workflow.add_edge("reporter", END)
    
    return workflow.compile()

def run_pipeline(competitor_id: int, competitor_name: str, competitor_domain: str, job_id: int):
    
    try:
        update_job_status(job_id, "running")
        
        workflow = build_workflow()
        initial_state = {
            "competitor_id": competitor_id,
            "competitor_name": competitor_name,
            "competitor_domain": competitor_domain,
            "plan": None,
            "raw_findings": [],
            "insights": None,
            "recommendations": None,
            "report_summary": None,
            "report_id": None
        }
        
        final_state = workflow.invoke(cast(Any, initial_state))
        
        findings_payload = {
            "insights": final_state.get("insights", {}).get("insights", []),
            "recommendations": final_state.get("recommendations", {}).get("recommendations", [])
        }
        raw_sources = [url for f in final_state.get("raw_findings", []) for url in f.get("sources_used", [])]
        
        db_report = create_report(
            competitor_id=competitor_id, 
            summary=final_state.get("report_summary") or "",
            findings=findings_payload,
            raw_sources=raw_sources
        )
        
        update_job_status(job_id, "completed", report_id=db_report.id)
        
        update_competitor(competitor_id, {"last_scraped_at": datetime.datetime.now(datetime.timezone.utc)})
        
    except Exception as e:
        import traceback
        error_msg = str(e) + "\n" + traceback.format_exc()
        logger.error(f"Pipeline failed for job {job_id}: {error_msg}")
        update_job_status(job_id, "failed", error_message=error_msg)
