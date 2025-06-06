"""
Demo version of the multi-agent system without AWS Strands SDK dependencies.
This demonstrates the core functionality using mock agents.
"""

import pandas as pd
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()


class MockAgent:
    """Base class for mock agents"""
    
    def __init__(self, agent_id: str, description: str):
        self.agent_id = agent_id
        self.description = description
        self.history = []
    
    def log_action(self, action: str, result: Any):
        """Log agent actions"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
        })


class MockDataAnalystAgent(MockAgent):
    """Mock Data Analyst Agent for demonstration"""
    
    def __init__(self):
        super().__init__("data_analyst", "Processes and analyzes data files")
    
    def analyze_file(self, file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze a data file"""
        try:
            # Load the file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            # Perform analysis
            analysis = {
                "file_info": {
                    "path": file_path,
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict()
                },
                "data_quality": {
                    "missing_values": df.isnull().sum().to_dict(),
                    "duplicate_rows": df.duplicated().sum()
                },
                "summary_statistics": {},
                "insights": []
            }
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                analysis["summary_statistics"] = df[numeric_cols].describe().to_dict()
                
                # Generate insights
                for col in numeric_cols:
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    analysis["insights"].append(
                        f"Column '{col}' has mean {mean_val:.2f} with standard deviation {std_val:.2f}"
                    )
            
            # Categorical analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols[:3]:  # Limit to first 3
                unique_count = df[col].nunique()
                analysis["insights"].append(
                    f"Column '{col}' has {unique_count} unique values"
                )
            
            # Overall insights
            analysis["insights"].extend([
                f"Dataset contains {df.shape[0]} rows and {df.shape[1]} columns",
                f"Data quality: {(1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100:.1f}% complete",
                f"Memory usage: approximately {df.memory_usage(deep=True).sum() / 1024:.1f} KB"
            ])
            
            result = {
                "agent": self.agent_id,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "analysis": analysis
            }
            
            self.log_action("analyze_file", result)
            logger.info("Data analysis completed", file_path=file_path, shape=df.shape)
            
            return result
            
        except Exception as e:
            error_result = {
                "agent": self.agent_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.log_action("analyze_file_error", error_result)
            logger.error("Data analysis failed", error=str(e))
            return error_result


class MockResearchAgent(MockAgent):
    """Mock Research Agent for demonstration"""
    
    def __init__(self):
        super().__init__("research_agent", "Conducts research and gathers information")
    
    def conduct_market_research(self, topic: str, aspects: List[str], num_sources: int = 5) -> Dict[str, Any]:
        """Conduct market research on a topic"""
        
        # Mock research findings
        research_findings = {
            "topic": topic,
            "aspects_analyzed": aspects,
            "sources_consulted": num_sources,
            "findings": {}
        }
        
        for aspect in aspects:
            if "market size" in aspect.lower():
                research_findings["findings"][aspect] = {
                    "summary": f"The {topic} market is valued at approximately $X billion",
                    "growth_rate": "Expected to grow at Y% CAGR",
                    "key_factors": ["Factor 1", "Factor 2", "Factor 3"]
                }
            elif "competition" in aspect.lower() or "players" in aspect.lower():
                research_findings["findings"][aspect] = {
                    "summary": f"The {topic} market has several key players",
                    "top_companies": ["Company A", "Company B", "Company C"],
                    "market_share": {"Company A": "30%", "Company B": "25%", "Others": "45%"}
                }
            elif "trend" in aspect.lower():
                research_findings["findings"][aspect] = {
                    "summary": f"Current trends in {topic} include technology advancement",
                    "emerging_trends": ["Trend 1", "Trend 2", "Trend 3"],
                    "future_outlook": "Positive growth expected"
                }
            else:
                research_findings["findings"][aspect] = {
                    "summary": f"Research insights for {aspect} in {topic}",
                    "key_points": ["Point 1", "Point 2", "Point 3"]
                }
        
        # Add overall insights
        research_findings["overall_insights"] = [
            f"The {topic} market shows strong potential for growth",
            "Technology innovation is a key driver",
            "Competition is intensifying with new entrants",
            "Regulatory changes may impact future development"
        ]
        
        result = {
            "agent": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "research": research_findings
        }
        
        self.log_action("market_research", result)
        logger.info("Market research completed", topic=topic, aspects=len(aspects))
        
        return result


class MockReportGeneratorAgent(MockAgent):
    """Mock Report Generator Agent for demonstration"""
    
    def __init__(self):
        super().__init__("report_generator", "Creates reports and documents")
    
    def create_comprehensive_report(self, title: str, data_insights: Dict, research_findings: Dict) -> Dict[str, Any]:
        """Create a comprehensive report"""
        
        # Generate report content
        report_content = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "sections": {}
        }
        
        # Executive Summary
        report_content["sections"]["executive_summary"] = {
            "title": "Executive Summary",
            "content": f"This report analyzes {title} based on data analysis and market research. "
                      f"Key findings indicate significant opportunities for growth and optimization."
        }
        
        # Data Analysis Section
        if data_insights and data_insights.get("status") == "completed":
            analysis = data_insights.get("analysis", {})
            report_content["sections"]["data_analysis"] = {
                "title": "Data Analysis",
                "content": f"Analysis of the provided dataset reveals {len(analysis.get('insights', []))} key insights.",
                "key_metrics": analysis.get("file_info", {}),
                "insights": analysis.get("insights", [])
            }
        
        # Research Findings Section
        if research_findings and research_findings.get("status") == "completed":
            research = research_findings.get("research", {})
            report_content["sections"]["market_research"] = {
                "title": "Market Research",
                "content": f"Market research on {research.get('topic', 'the subject')} reveals important trends.",
                "findings": research.get("findings", {}),
                "insights": research.get("overall_insights", [])
            }
        
        # Recommendations
        recommendations = []
        if data_insights and data_insights.get("status") == "completed":
            recommendations.append("Leverage data insights to optimize operations")
            recommendations.append("Address data quality issues identified in the analysis")
        
        if research_findings and research_findings.get("status") == "completed":
            recommendations.append("Capitalize on identified market opportunities")
            recommendations.append("Monitor competitive landscape developments")
        
        report_content["sections"]["recommendations"] = {
            "title": "Recommendations",
            "content": "Based on our analysis, we recommend the following actions:",
            "items": recommendations
        }
        
        # Conclusion
        report_content["sections"]["conclusion"] = {
            "title": "Conclusion",
            "content": f"This comprehensive analysis of {title} provides valuable insights for strategic decision-making. "
                      f"The combination of data analysis and market research offers a solid foundation for future planning."
        }
        
        result = {
            "agent": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "report": report_content,
            "format": "structured_json"
        }
        
        self.log_action("create_report", result)
        logger.info("Report generation completed", title=title)
        
        return result


class MockCoordinatorAgent(MockAgent):
    """Mock Coordinator Agent for demonstration"""
    
    def __init__(self):
        super().__init__("coordinator", "Orchestrates multi-agent workflows")
        self.data_analyst = MockDataAnalystAgent()
        self.research_agent = MockResearchAgent()
        self.report_generator = MockReportGeneratorAgent()
    
    def execute_workflow(self, request: str, data_file: Optional[str] = None) -> Dict[str, Any]:
        """Execute a multi-agent workflow"""
        
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        workflow_results = {
            "workflow_id": workflow_id,
            "request": request,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "agents_used": [],
            "results": {}
        }
        
        try:
            # Step 1: Data Analysis (if file provided)
            if data_file:
                print("🔍 Step 1: Analyzing data...")
                data_result = self.data_analyst.analyze_file(data_file)
                workflow_results["results"]["data_analysis"] = data_result
                workflow_results["agents_used"].append("data_analyst")
                print(f"   ✅ Data analysis completed: {data_result['status']}")
            else:
                data_result = None
                print("   ⚠️  No data file provided, skipping data analysis")
            
            # Step 2: Market Research
            print("🌐 Step 2: Conducting market research...")
            # Extract topic from request
            topic = request.split("about")[-1].strip() if "about" in request else request[:50]
            research_result = self.research_agent.conduct_market_research(
                topic=topic,
                aspects=["Market Size", "Key Players", "Trends"]
            )
            workflow_results["results"]["market_research"] = research_result
            workflow_results["agents_used"].append("research_agent")
            print(f"   ✅ Market research completed: {research_result['status']}")
            
            # Step 3: Report Generation
            print("📝 Step 3: Generating comprehensive report...")
            report_result = self.report_generator.create_comprehensive_report(
                title=f"Analysis Report: {topic}",
                data_insights=data_result,
                research_findings=research_result
            )
            workflow_results["results"]["final_report"] = report_result
            workflow_results["agents_used"].append("report_generator")
            print(f"   ✅ Report generation completed: {report_result['status']}")
            
            workflow_results["status"] = "completed"
            workflow_results["summary"] = {
                "total_agents": len(workflow_results["agents_used"]),
                "data_analyzed": data_file is not None,
                "research_conducted": True,
                "report_generated": True
            }
            
            self.log_action("execute_workflow", workflow_results)
            logger.info("Workflow completed successfully", workflow_id=workflow_id)
            
        except Exception as e:
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            logger.error("Workflow failed", error=str(e))
        
        return workflow_results
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "coordinator": {
                "id": self.agent_id,
                "status": "active",
                "history_count": len(self.history)
            },
            "data_analyst": {
                "id": self.data_analyst.agent_id,
                "status": "ready",
                "history_count": len(self.data_analyst.history)
            },
            "research_agent": {
                "id": self.research_agent.agent_id,
                "status": "ready", 
                "history_count": len(self.research_agent.history)
            },
            "report_generator": {
                "id": self.report_generator.agent_id,
                "status": "ready",
                "history_count": len(self.report_generator.history)
            }
        }


# Demo function
def run_demo():
    """Run a demonstration of the multi-agent system"""
    print("🤖 Starting Strands Multi-Agent System Demo")
    print("=" * 50)
    
    # Initialize coordinator
    coordinator = MockCoordinatorAgent()
    
    # Show agent status
    print("\n📊 Agent Status:")
    status = coordinator.get_agent_status()
    for agent_name, agent_info in status.items():
        print(f"   {agent_name}: {agent_info['status']}")
    
    # Execute a workflow
    print(f"\n🚀 Executing Demo Workflow...")
    request = "Create a comprehensive analysis report about electric vehicle market trends"
    
    result = coordinator.execute_workflow(request)
    
    print(f"\n📋 Workflow Results:")
    print(f"   Workflow ID: {result['workflow_id']}")
    print(f"   Status: {result['status']}")
    print(f"   Agents Used: {', '.join(result['agents_used'])}")
    
    if result["status"] == "completed":
        print(f"\n✅ Workflow completed successfully!")
        
        # Show summary of results
        if "data_analysis" in result["results"]:
            data_result = result["results"]["data_analysis"]
            print(f"   📊 Data Analysis: {data_result['status']}")
        
        if "market_research" in result["results"]:
            research_result = result["results"]["market_research"]
            research_data = research_result.get("research", {})
            print(f"   🔍 Market Research: {research_result['status']} - {len(research_data.get('findings', {}))} aspects analyzed")
        
        if "final_report" in result["results"]:
            report_result = result["results"]["final_report"]
            report_data = report_result.get("report", {})
            print(f"   📝 Final Report: {report_result['status']} - {len(report_data.get('sections', {}))} sections generated")
    
    print(f"\n🎉 Demo completed!")
    return result


if __name__ == "__main__":
    run_demo()