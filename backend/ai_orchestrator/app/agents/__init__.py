from .base_agent import BaseAgent, AgentResult
from .resume_optimizer import ResumeOptimizerAgent
from .job_match_engine import JobMatchEngineAgent
from .outreach_agent import OutreachAgent
from .career_intelligence import CareerIntelligenceAgent

__all__ = [
    "BaseAgent",
    "AgentResult",
    "ResumeOptimizerAgent",
    "JobMatchEngineAgent",
    "OutreachAgent",
    "CareerIntelligenceAgent",
]

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "resume_optimizer": ResumeOptimizerAgent,
    "job_match_engine": JobMatchEngineAgent,
    "outreach": OutreachAgent,
    "career_intelligence": CareerIntelligenceAgent,
}
