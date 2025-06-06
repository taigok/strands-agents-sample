from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import json
from enum import Enum

from strands_agents import Agent
from strands_agents.tools import ToolDefinition, tool
from strands_agents.models.bedrock import BedrockModel
from strands_agents.memory import ConversationBufferMemory
from strands_agents.protocols import Agent2AgentProtocol

from .data_analyst import DataAnalystAgent
from .research_agent import ResearchAgent
from .report_generator import ReportGeneratorAgent
from ..config.settings import settings
import structlog

logger = structlog.get_logger()


class TaskStatus(Enum):
    """Status of a task in the workflow"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowTask:
    """Represents a task in the multi-agent workflow"""
    
    def __init__(
        self,
        task_id: str,
        agent_type: str,
        description: str,
        parameters: Dict[str, Any],
        dependencies: Optional[List[str]] = None
    ):
        self.task_id = task_id
        self.agent_type = agent_type
        self.description = description
        self.parameters = parameters
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None


class CoordinatorAgent(Agent):
    """
    Coordinator Agent that manages multi-agent workflows and orchestrates
    task distribution among specialized agents.
    """
    
    def __init__(self, agent_id: str = "coordinator"):
        # Initialize the Bedrock model
        bedrock_config = settings.get_bedrock_config()
        model = BedrockModel(**bedrock_config)
        
        # Initialize memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create the agent2agent tool for inter-agent communication
        self.agent2agent_tool = self._create_agent2agent_tool()
        
        # Define the agent's tools
        tools = [
            ToolDefinition(tool=self.agent2agent_tool),
            ToolDefinition(tool=self._get_workflow_status),
            ToolDefinition(tool=self._create_workflow_plan),
        ]
        
        # Define the agent's system prompt
        system_prompt = """You are a Coordinator Agent responsible for orchestrating multi-agent workflows.
        
Your responsibilities include:
1. Understanding complex user requests and breaking them down into tasks
2. Assigning tasks to appropriate specialized agents
3. Managing task dependencies and execution order
4. Monitoring task progress and handling failures
5. Aggregating results from multiple agents
6. Ensuring quality and completeness of deliverables

Available specialized agents:
- Data Analyst Agent: Data processing, analysis, and insights
- Research Agent: Web research, fact-checking, market analysis
- Report Generator Agent: Creating reports, presentations, and documents

When coordinating tasks:
- Analyze the request to identify required capabilities
- Create a logical workflow with proper dependencies
- Assign tasks to the most appropriate agents
- Monitor progress and adapt as needed
- Aggregate and synthesize results
- Ensure all requirements are met

Focus on efficiency, quality, and delivering comprehensive results."""
        
        # Initialize the parent Agent class
        super().__init__(
            agent_id=agent_id,
            model=model,
            tools=tools,
            memory=memory,
            system_prompt=system_prompt,
            max_iterations=settings.agent_max_iterations,
            verbose=True
        )
        
        # Initialize specialized agents
        self.agents = {
            "data_analyst": DataAnalystAgent(),
            "research": ResearchAgent(),
            "report_generator": ReportGeneratorAgent()
        }
        
        # Workflow management
        self.workflows = {}
        self.current_workflow = None
        
        # Initialize Agent2Agent protocol
        self.a2a_protocol = Agent2AgentProtocol()
        
        logger.info("Coordinator Agent initialized", agent_id=agent_id)
    
    def _create_agent2agent_tool(self):
        """Create the agent2agent communication tool"""
        
        @tool
        def communicate_with_agent(
            agent_type: str,
            task_description: str,
            parameters: Dict[str, Any]
        ) -> Dict[str, Any]:
            """
            Communicate with a specialized agent to perform a task.
            
            Args:
                agent_type: Type of agent (data_analyst, research, report_generator)
                task_description: Description of the task
                parameters: Parameters for the task
                
            Returns:
                Task result from the agent
            """
            try:
                if agent_type not in self.agents:
                    raise ValueError(f"Unknown agent type: {agent_type}")
                
                agent = self.agents[agent_type]
                
                # Create a structured prompt for the agent
                prompt = f"""Task: {task_description}

Parameters:
{json.dumps(parameters, indent=2)}

Please complete this task and return the results."""
                
                # Execute the task
                result = agent.run(prompt)
                
                return {
                    "agent_type": agent_type,
                    "task_description": task_description,
                    "status": "completed",
                    "result": result
                }
                
            except Exception as e:
                logger.error(
                    "Agent communication failed",
                    agent_type=agent_type,
                    error=str(e)
                )
                return {
                    "agent_type": agent_type,
                    "task_description": task_description,
                    "status": "failed",
                    "error": str(e)
                }
        
        return communicate_with_agent
    
    @tool
    def _get_workflow_status(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: ID of the workflow (uses current if not specified)
            
        Returns:
            Workflow status information
        """
        workflow_id = workflow_id or self.current_workflow
        
        if not workflow_id or workflow_id not in self.workflows:
            return {"error": "No workflow found"}
        
        workflow = self.workflows[workflow_id]
        
        status = {
            "workflow_id": workflow_id,
            "total_tasks": len(workflow),
            "completed": sum(1 for t in workflow.values() if t.status == TaskStatus.COMPLETED),
            "in_progress": sum(1 for t in workflow.values() if t.status == TaskStatus.IN_PROGRESS),
            "pending": sum(1 for t in workflow.values() if t.status == TaskStatus.PENDING),
            "failed": sum(1 for t in workflow.values() if t.status == TaskStatus.FAILED),
            "tasks": {}
        }
        
        for task_id, task in workflow.items():
            status["tasks"][task_id] = {
                "agent_type": task.agent_type,
                "description": task.description,
                "status": task.status.value,
                "dependencies": task.dependencies
            }
        
        return status
    
    @tool
    def _create_workflow_plan(
        self,
        user_request: str,
        requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Create a workflow plan for a user request.
        
        Args:
            user_request: The user's request
            requirements: List of specific requirements
            
        Returns:
            Workflow plan with tasks and dependencies
        """
        # This is a simplified workflow creation
        # In a real implementation, this would use more sophisticated planning
        
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tasks = []
        
        # Analyze the request to determine needed agents
        request_lower = user_request.lower()
        
        task_counter = 1
        
        # Determine if data analysis is needed
        if any(word in request_lower for word in ['data', 'analyze', 'csv', 'excel', 'statistics']):
            tasks.append({
                "task_id": f"task_{task_counter}",
                "agent_type": "data_analyst",
                "description": "Analyze data and provide insights",
                "dependencies": []
            })
            task_counter += 1
        
        # Determine if research is needed
        if any(word in request_lower for word in ['research', 'market', 'competitor', 'trend', 'search']):
            tasks.append({
                "task_id": f"task_{task_counter}",
                "agent_type": "research",
                "description": "Conduct research and gather information",
                "dependencies": []
            })
            task_counter += 1
        
        # Report generation is usually needed at the end
        if any(word in request_lower for word in ['report', 'document', 'summary', 'presentation']):
            dependencies = [t["task_id"] for t in tasks]  # Depends on all previous tasks
            tasks.append({
                "task_id": f"task_{task_counter}",
                "agent_type": "report_generator",
                "description": "Generate comprehensive report",
                "dependencies": dependencies
            })
        
        return {
            "workflow_id": workflow_id,
            "user_request": user_request,
            "requirements": requirements,
            "tasks": tasks,
            "estimated_duration": len(tasks) * 2  # Rough estimate in minutes
        }
    
    def execute_workflow(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete multi-agent workflow.
        
        Args:
            user_request: The user's request
            context: Optional context information
            
        Returns:
            Workflow execution results
        """
        try:
            logger.info("Starting workflow execution", request=user_request)
            
            # Create workflow plan
            prompt = f"""Analyze this request and create a workflow plan:

User Request: {user_request}

Context: {json.dumps(context, indent=2) if context else 'None'}

Break down the request into tasks for our specialized agents:
1. Identify what data analysis is needed (if any)
2. Identify what research is required (if any)
3. Determine what reports or documents to generate
4. Plan the task dependencies

Create a detailed workflow plan."""
            
            # Run the coordinator to plan the workflow
            workflow_plan = self.run(prompt)
            
            # Execute the workflow based on the plan
            results = {
                "workflow_plan": workflow_plan,
                "user_request": user_request,
                "context": context,
                "execution_time": datetime.now().isoformat(),
                "status": "completed"
            }
            
            logger.info("Workflow execution completed")
            return results
            
        except Exception as e:
            logger.error("Workflow execution failed", error=str(e))
            return {
                "user_request": user_request,
                "status": "failed",
                "error": str(e)
            }
    
    def process_complex_request(
        self,
        request: str,
        data_files: Optional[List[str]] = None,
        output_format: str = "pdf",
        additional_requirements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a complex request requiring multiple agents.
        
        Args:
            request: The complex request
            data_files: Optional data files to analyze
            output_format: Desired output format
            additional_requirements: Additional requirements
            
        Returns:
            Processing results
        """
        try:
            # Build context
            context = {
                "data_files": data_files or [],
                "output_format": output_format,
                "additional_requirements": additional_requirements or []
            }
            
            # Create detailed prompt for coordination
            prompt = f"""Process this complex request using our multi-agent system:

Request: {request}

Available Resources:
- Data files: {data_files if data_files else 'None'}
- Desired output format: {output_format}
- Additional requirements: {additional_requirements if additional_requirements else 'None'}

Coordinate the following:
1. If data files are provided, use the Data Analyst Agent to analyze them
2. Use the Research Agent for any market research or external information needs
3. Use the Report Generator Agent to create the final deliverable
4. Ensure all agents work together to fulfill the complete request

Manage the workflow to deliver comprehensive results."""
            
            # Execute the coordination
            result = self.run(prompt)
            
            return {
                "request": request,
                "context": context,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Complex request processing failed", error=str(e))
            raise
    
    def generate_multi_source_report(
        self,
        topic: str,
        data_sources: List[str],
        research_queries: List[str],
        report_sections: List[str],
        output_path: str
    ) -> Dict[str, Any]:
        """
        Generate a report using multiple data sources and research.
        
        Args:
            topic: Report topic
            data_sources: List of data file paths
            research_queries: Research queries to execute
            report_sections: Sections to include in report
            output_path: Path for final report
            
        Returns:
            Report generation results
        """
        try:
            prompt = f"""Generate a comprehensive report on "{topic}" using multiple agents:

Data Sources to Analyze:
{json.dumps(data_sources, indent=2)}

Research Queries:
{json.dumps(research_queries, indent=2)}

Report Sections Required:
{json.dumps(report_sections, indent=2)}

Output Path: {output_path}

Workflow:
1. Use Data Analyst Agent to analyze all data sources
2. Use Research Agent to investigate all research queries
3. Synthesize findings from both agents
4. Use Report Generator Agent to create a professional report
5. Ensure all sections are covered with insights from both data and research

Coordinate this multi-agent workflow to produce a high-quality report."""
            
            result = self.run(prompt)
            
            return {
                "topic": topic,
                "data_sources": data_sources,
                "research_queries": research_queries,
                "report_sections": report_sections,
                "output_path": output_path,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Multi-source report generation failed", topic=topic, error=str(e))
            raise
    
    def handle_iterative_analysis(
        self,
        initial_request: str,
        iteration_limit: int = 3,
        refinement_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Handle iterative analysis with refinement loops.
        
        Args:
            initial_request: Initial analysis request
            iteration_limit: Maximum iterations
            refinement_criteria: Criteria for refinement
            
        Returns:
            Iterative analysis results
        """
        try:
            criteria_str = ""
            if refinement_criteria:
                criteria_str = f"\nRefinement criteria: {json.dumps(refinement_criteria, indent=2)}"
            
            prompt = f"""Perform iterative analysis for: {initial_request}

Maximum iterations: {iteration_limit}{criteria_str}

Process:
1. Start with initial analysis using appropriate agents
2. Review results against requirements
3. If refinement is needed, identify gaps
4. Iterate with targeted analysis to fill gaps
5. Continue until satisfactory or iteration limit reached

For each iteration:
- Clearly state what was found
- Identify what's missing or needs improvement
- Plan the next iteration's focus

Coordinate multiple agents as needed for comprehensive analysis."""
            
            result = self.run(prompt)
            
            return {
                "initial_request": initial_request,
                "iteration_limit": iteration_limit,
                "refinement_criteria": refinement_criteria,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Iterative analysis failed", error=str(e))
            raise