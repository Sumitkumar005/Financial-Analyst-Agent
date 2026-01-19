"""
Multi-Agent Orchestration System
Coordinates multiple specialized AI agents to answer complex queries.
"""

from typing import List, Dict, Any, Optional
from enum import Enum

class AgentType(Enum):
    DATA_RETRIEVAL = "data_retrieval"
    TABLE_EXTRACTION = "table_extraction"
    TREND_ANALYSIS = "trend_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    COMPARISON = "comparison"
    FORECASTING = "forecasting"
    REPORT_GENERATION = "report_generation"

class Agent:
    """Base class for specialized agents."""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.name = agent_type.value
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the query."""
        raise NotImplementedError
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task."""
        raise NotImplementedError

class DataRetrievalAgent(Agent):
    """Retrieves relevant documents and sections."""
    
    def __init__(self):
        super().__init__(AgentType.DATA_RETRIEVAL)
        from backend.app.services.file_service import retrieve_relevant_sections
        self.retrieve = retrieve_relevant_sections
    
    def can_handle(self, query: str) -> bool:
        return True  # Always needed
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        ticker = context.get('ticker', '')
        sections = self.retrieve(query, ticker, limit=10)
        return {
            'agent': self.name,
            'sections': sections,
            'success': len(sections) > 0
        }

class TrendAnalysisAgent(Agent):
    """Analyzes trends in time-series data."""
    
    def __init__(self):
        super().__init__(AgentType.TREND_ANALYSIS)
        from backend.app.services.time_series_extractor import get_time_series_extractor
        self.ts_extractor = get_time_series_extractor()
    
    def can_handle(self, query: str) -> bool:
        keywords = ['trend', 'growth', 'increase', 'decrease', 'over time', 'years', 'historical']
        return any(kw in query.lower() for kw in keywords)
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        ticker = context.get('ticker', '')
        
        # Extract metric from query
        metrics = ['revenue', 'income', 'profit', 'cash flow', 'assets', 'liabilities']
        metric = None
        for m in metrics:
            if m in query.lower():
                metric = m
                break
        
        if not metric:
            return {'agent': self.name, 'error': 'No metric found in query'}
        
        # Get time-series data
        data = self.ts_extractor.get_time_series(ticker, metric)
        trend = self.ts_extractor.get_trend(ticker, metric)
        
        return {
            'agent': self.name,
            'metric': metric,
            'data': data,
            'trend': trend,
            'success': len(data) > 0
        }

class ComparisonAgent(Agent):
    """Compares companies, metrics, or time periods."""
    
    def __init__(self):
        super().__init__(AgentType.COMPARISON)
        from backend.app.services.time_series_extractor import get_time_series_extractor
        self.ts_extractor = get_time_series_extractor()
    
    def can_handle(self, query: str) -> bool:
        keywords = ['compare', 'comparison', 'vs', 'versus', 'difference', 'better', 'worse']
        return any(kw in query.lower() for kw in keywords)
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        tickers = context.get('tickers', [])
        
        if len(tickers) < 2:
            return {'agent': self.name, 'error': 'Need at least 2 companies to compare'}
        
        # Extract metric
        metrics = ['revenue', 'income', 'profit', 'margin', 'growth']
        metric = None
        for m in metrics:
            if m in query.lower():
                metric = m
                break
        
        if not metric:
            return {'agent': self.name, 'error': 'No metric found'}
        
        # Compare companies
        comparison = {}
        for ticker in tickers:
            data = self.ts_extractor.get_time_series(ticker, metric)
            if data:
                comparison[ticker] = data
        
        return {
            'agent': self.name,
            'metric': metric,
            'comparison': comparison,
            'success': len(comparison) > 0
        }

class RiskAssessmentAgent(Agent):
    """Assesses financial risks."""
    
    def __init__(self):
        super().__init__(AgentType.RISK_ASSESSMENT)
    
    def can_handle(self, query: str) -> bool:
        keywords = ['risk', 'risky', 'danger', 'warning', 'concern', 'threat']
        return any(kw in query.lower() for kw in keywords)
    
    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        sections = context.get('sections', [])
        
        # Look for risk-related sections
        risk_sections = [s for s in sections if 'risk' in s.get('section', '').lower()]
        
        # Extract risk factors
        risk_factors = []
        for section in risk_sections:
            text = section.get('text', '')
            # Simple extraction: look for bullet points or numbered lists
            lines = text.split('\n')
            for line in lines:
                if line.strip().startswith(('-', '*', '•', '1.', '2.', '3.')):
                    risk_factors.append(line.strip())
        
        return {
            'agent': self.name,
            'risk_factors': risk_factors[:10],  # Top 10
            'risk_sections_found': len(risk_sections),
            'success': len(risk_factors) > 0
        }

class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents to answer complex queries.
    """
    
    def __init__(self):
        self.agents = [
            DataRetrievalAgent(),
            TrendAnalysisAgent(),
            ComparisonAgent(),
            RiskAssessmentAgent(),
        ]
    
    def process_query(self, query: str, ticker: str, tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process a query using multiple agents.
        """
        if tickers is None:
            tickers = [ticker] if ticker else []
        
        context = {
            'query': query,
            'ticker': ticker,
            'tickers': tickers,
            'sections': [],
            'results': {}
        }
        
        # Step 1: Always retrieve data first
        data_agent = self.agents[0]  # DataRetrievalAgent
        data_result = data_agent.execute(query, context)
        context['sections'] = data_result.get('sections', [])
        
        # Step 2: Determine which agents are needed
        active_agents = []
        for agent in self.agents[1:]:  # Skip data retrieval (already done)
            if agent.can_handle(query):
                active_agents.append(agent)
        
        # Step 3: Execute active agents in parallel (simulated)
        agent_results = {}
        for agent in active_agents:
            try:
                result = agent.execute(query, context)
                agent_results[agent.name] = result
            except Exception as e:
                agent_results[agent.name] = {
                    'agent': agent.name,
                    'error': str(e),
                    'success': False
                }
        
        # Step 4: Combine results
        return {
            'query': query,
            'ticker': ticker,
            'tickers': tickers,
            'data_retrieval': data_result,
            'agent_results': agent_results,
            'active_agents': [a.name for a in active_agents],
            'sections_retrieved': len(context['sections'])
        }
    
    def generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary from agent results."""
        summary_parts = []
        
        # Add data retrieval summary
        data_result = results.get('data_retrieval', {})
        if data_result.get('success'):
            summary_parts.append(f"Retrieved {len(data_result.get('sections', []))} relevant sections.")
        
        # Add agent results
        agent_results = results.get('agent_results', {})
        
        if 'trend_analysis' in agent_results:
            trend_result = agent_results['trend_analysis']
            if trend_result.get('success'):
                trend = trend_result.get('trend', 'unknown')
                metric = trend_result.get('metric', 'metric')
                summary_parts.append(f"Trend analysis: {metric} is {trend}.")
        
        if 'comparison' in agent_results:
            comp_result = agent_results['comparison']
            if comp_result.get('success'):
                comparison = comp_result.get('comparison', {})
                summary_parts.append(f"Comparison: Analyzed {len(comparison)} companies.")
        
        if 'risk_assessment' in agent_results:
            risk_result = agent_results['risk_assessment']
            if risk_result.get('success'):
                risk_count = len(risk_result.get('risk_factors', []))
                summary_parts.append(f"Risk assessment: Found {risk_count} risk factors.")
        
        return " ".join(summary_parts) if summary_parts else "Analysis complete."


# Global instance
_orchestrator = None

def get_orchestrator() -> MultiAgentOrchestrator:
    """Get or create orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
    return _orchestrator
