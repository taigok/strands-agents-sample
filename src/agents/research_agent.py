from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import asyncio

from strands_agents import Agent
from strands_agents.tools import ToolDefinition
from strands_agents.models.bedrock import BedrockModel
from strands_agents.memory import ConversationBufferMemory

from ..tools.search_tools import (
    web_search,
    fetch_webpage_content,
    fetch_multiple_urls,
    search_academic_papers,
    extract_structured_data,
    search_company_info,
    verify_facts
)
from ..config.settings import settings
import structlog

logger = structlog.get_logger()


class ResearchAgent(Agent):
    """
    Research Agent specialized in gathering external information,
    conducting market research, and verifying facts from various sources.
    """
    
    def __init__(self, agent_id: str = "research_agent"):
        # Initialize the Bedrock model
        bedrock_config = settings.get_bedrock_config()
        model = BedrockModel(**bedrock_config)
        
        # Initialize memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Define the agent's tools
        tools = [
            ToolDefinition(tool=web_search),
            ToolDefinition(tool=fetch_webpage_content),
            ToolDefinition(tool=fetch_multiple_urls),
            ToolDefinition(tool=search_academic_papers),
            ToolDefinition(tool=extract_structured_data),
            ToolDefinition(tool=search_company_info),
            ToolDefinition(tool=verify_facts),
        ]
        
        # Define the agent's system prompt
        system_prompt = """You are a Research Agent specialized in gathering and analyzing information from various sources.
        
Your responsibilities include:
1. Conducting comprehensive web searches for relevant information
2. Gathering data from multiple sources and cross-referencing
3. Performing market research and competitive analysis
4. Verifying facts and claims with reliable sources
5. Extracting structured information from web content
6. Providing well-researched, factual insights with proper citations

When conducting research:
- Always search multiple sources to verify information
- Cross-reference facts from different sources
- Clearly cite your sources with URLs
- Distinguish between facts and opinions
- Highlight any conflicting information found
- Provide confidence levels for your findings
- Summarize complex information clearly

Focus on accuracy, thoroughness, and providing actionable intelligence."""
        
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
        
        logger.info("Research Agent initialized", agent_id=agent_id)
    
    def conduct_market_research(
        self,
        topic: str,
        aspects: List[str],
        num_sources: int = 10
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive market research on a topic.
        
        Args:
            topic: Main topic to research
            aspects: Specific aspects to investigate
            num_sources: Number of sources to consult
            
        Returns:
            Research findings organized by aspects
        """
        try:
            aspects_str = "\n".join([f"- {aspect}" for aspect in aspects])
            
            prompt = f"""Conduct comprehensive market research on: {topic}

Focus on these specific aspects:
{aspects_str}

Please:
1. Search for information from at least {num_sources} different sources
2. For each aspect, gather relevant data and insights
3. Include market size, trends, key players, and opportunities
4. Identify challenges and risks in the market
5. Provide quantitative data where available
6. Cross-reference information from multiple sources
7. Cite all sources with URLs

Structure your findings by aspect and provide a summary of key insights."""
            
            result = self.run(prompt)
            
            logger.info(
                "Market research completed",
                topic=topic,
                aspects=len(aspects)
            )
            
            return {
                "topic": topic,
                "aspects": aspects,
                "num_sources": num_sources,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Market research failed", topic=topic, error=str(e))
            raise
    
    def analyze_competitors(
        self,
        company: str,
        competitors: List[str],
        analysis_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Perform competitive analysis.
        
        Args:
            company: Main company to analyze
            competitors: List of competitor companies
            analysis_criteria: Criteria for comparison
            
        Returns:
            Competitive analysis results
        """
        try:
            criteria_str = "\n".join([f"- {criterion}" for criterion in analysis_criteria])
            competitors_str = ", ".join(competitors)
            
            prompt = f"""Perform a competitive analysis for {company} against these competitors: {competitors_str}

Analyze based on these criteria:
{criteria_str}

For each company:
1. Gather information about their offerings
2. Analyze their strengths and weaknesses
3. Compare them on each criterion
4. Identify their market positioning
5. Find their unique value propositions
6. Look for recent news or developments

Provide:
- A comparison matrix
- Key differentiators for each company
- {company}'s competitive advantages and disadvantages
- Strategic recommendations for {company}

Cite all sources used."""
            
            result = self.run(prompt)
            
            logger.info(
                "Competitive analysis completed",
                company=company,
                num_competitors=len(competitors)
            )
            
            return {
                "company": company,
                "competitors": competitors,
                "analysis_criteria": analysis_criteria,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Competitive analysis failed", company=company, error=str(e))
            raise
    
    def research_industry_trends(
        self,
        industry: str,
        time_horizon: str = "next 5 years",
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Research industry trends and future outlook.
        
        Args:
            industry: Industry to research
            time_horizon: Time period for trends
            focus_areas: Specific areas to focus on
            
        Returns:
            Industry trend analysis
        """
        try:
            focus_str = ""
            if focus_areas:
                focus_str = f"\nFocus particularly on: {', '.join(focus_areas)}"
            
            prompt = f"""Research trends and future outlook for the {industry} industry over the {time_horizon}.{focus_str}

Please investigate:
1. Current state of the industry
2. Emerging trends and technologies
3. Market drivers and growth factors
4. Potential disruptions or challenges
5. Key innovations and breakthroughs
6. Regulatory changes or impacts
7. Investment trends and funding
8. Expert predictions and forecasts

Search for:
- Industry reports and analyses
- Expert opinions and thought leadership
- Recent news and developments
- Academic research and papers
- Market data and statistics

Provide a comprehensive trend analysis with supporting evidence and citations."""
            
            result = self.run(prompt)
            
            logger.info(
                "Industry trend research completed",
                industry=industry,
                time_horizon=time_horizon
            )
            
            return {
                "industry": industry,
                "time_horizon": time_horizon,
                "focus_areas": focus_areas,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Industry trend research failed", industry=industry, error=str(e))
            raise
    
    def fact_check_claims(
        self,
        claims: List[str],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fact-check a list of claims.
        
        Args:
            claims: List of claims to verify
            context: Optional context for the claims
            
        Returns:
            Fact-checking results for each claim
        """
        try:
            context_str = f"\nContext: {context}" if context else ""
            claims_str = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(claims)])
            
            prompt = f"""Fact-check the following claims:{context_str}

Claims to verify:
{claims_str}

For each claim:
1. Search for supporting evidence from reliable sources
2. Search for contradicting evidence
3. Evaluate the credibility of sources
4. Determine if the claim is true, false, partially true, or unverifiable
5. Provide confidence level in your assessment
6. Explain your reasoning
7. Cite all sources used

Be thorough and objective in your fact-checking."""
            
            result = self.run(prompt)
            
            logger.info(
                "Fact-checking completed",
                num_claims=len(claims)
            )
            
            return {
                "claims": claims,
                "context": context,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Fact-checking failed", error=str(e))
            raise
    
    def gather_customer_insights(
        self,
        product_or_service: str,
        aspects: List[str],
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Gather customer insights and feedback.
        
        Args:
            product_or_service: Product or service to research
            aspects: Aspects of customer feedback to focus on
            sources: Specific sources to check (reviews, forums, etc.)
            
        Returns:
            Customer insights and sentiment analysis
        """
        try:
            aspects_str = "\n".join([f"- {aspect}" for aspect in aspects])
            sources_str = ""
            if sources:
                sources_str = f"\nFocus on these sources: {', '.join(sources)}"
            
            prompt = f"""Research customer insights and feedback for: {product_or_service}{sources_str}

Analyze these aspects:
{aspects_str}

Please:
1. Search for customer reviews and ratings
2. Look for discussions in forums and social media
3. Find common complaints and praise
4. Identify customer pain points and desires
5. Analyze sentiment trends
6. Look for feature requests or suggestions
7. Compare feedback across different platforms
8. Identify customer segments and their specific needs

Provide:
- Summary of overall sentiment
- Key themes in customer feedback
- Specific examples and quotes
- Actionable insights for improvement
- Comparison with competitor feedback if available

Cite all sources."""
            
            result = self.run(prompt)
            
            logger.info(
                "Customer insights gathered",
                product_or_service=product_or_service,
                aspects=len(aspects)
            )
            
            return {
                "product_or_service": product_or_service,
                "aspects": aspects,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Customer insights gathering failed", error=str(e))
            raise
    
    def research_best_practices(
        self,
        topic: str,
        industry: Optional[str] = None,
        specific_questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Research best practices for a specific topic.
        
        Args:
            topic: Topic to research best practices for
            industry: Optional industry context
            specific_questions: Specific questions to answer
            
        Returns:
            Best practices and recommendations
        """
        try:
            industry_str = f" in the {industry} industry" if industry else ""
            questions_str = ""
            if specific_questions:
                questions_str = "\n\nSpecific questions to answer:\n" + \
                              "\n".join([f"- {q}" for q in specific_questions])
            
            prompt = f"""Research best practices for {topic}{industry_str}.{questions_str}

Please:
1. Search for industry standards and guidelines
2. Find case studies and success stories
3. Look for expert recommendations
4. Identify common pitfalls to avoid
5. Find frameworks or methodologies
6. Look for tools and resources
7. Compare different approaches
8. Find metrics for measuring success

Provide:
- Clear best practice recommendations
- Examples of successful implementations
- Step-by-step guidance where applicable
- Pros and cons of different approaches
- Resources for further learning

Focus on actionable, proven practices with supporting evidence."""
            
            result = self.run(prompt)
            
            logger.info(
                "Best practices research completed",
                topic=topic,
                industry=industry
            )
            
            return {
                "topic": topic,
                "industry": industry,
                "specific_questions": specific_questions,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Best practices research failed", topic=topic, error=str(e))
            raise