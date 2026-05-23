from base_agent import BaseAgent
from typing import Dict, Any, List
import json


class AIReconPlanner(BaseAgent):
    """AI Recon Planner - Autonomous reconnaissance planning and execution"""
    
    def __init__(self, ai_router_url: str, tool_orchestrator_url: str):
        super().__init__("AI_RECON_PLANNER", ai_router_url)
        self.tool_orchestrator_url = tool_orchestrator_url
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomous reconnaissance"""
        target = context.get("target")
        target_type = context.get("targetType")
        depth = context.get("depth", 2)
        
        self.log_action("AI Recon Planning started", {"target": target, "type": target_type})
        
        # Phase 1: AI Planning
        plan = await self.create_recon_plan(target, target_type, depth)
        
        # Phase 2: Tool Selection
        tools = await self.select_tools(plan)
        
        # Phase 3: Execution
        results = await self.execute_tools(target, tools, plan)
        
        # Phase 4: Analysis & Enrichment
        enriched = await self.enrich_results(results)
        
        # Phase 5: Pivoting
        pivots = await self.identify_pivots(enriched)
        
        # Phase 6: Graph Correlation
        graph_data = await self.correlate_graph(enriched)
        
        # Phase 7: AI Reasoning
        analysis = await self.ai_reasoning(enriched, graph_data, pivots)
        
        return {
            "target": target,
            "plan": plan,
            "tools_used": tools,
            "results": enriched,
            "pivots": pivots,
            "graph": graph_data,
            "analysis": analysis,
        }
    
    async def create_recon_plan(self, target: str, target_type: str, depth: int) -> Dict[str, Any]:
        """Use AI to create reconnaissance plan"""
        prompt = f"""You are an expert OSINT analyst. Create a reconnaissance plan for:

Target: {target}
Type: {target_type}
Depth: {depth}

Available tool categories:
- Subdomain enumeration (amass, subfinder, assetfinder)
- Port scanning (naabu, masscan)
- Web analysis (httpx, whatweb, wappalyzer)
- Vulnerability scanning (nuclei)
- Social media (sherlock, holehe, maigret)
- Code analysis (trufflehog, gitleaks)
- Threat intelligence (virustotal, shodan, censys)

Create a JSON plan with:
1. phases: ordered list of reconnaissance phases
2. tools: tools to use in each phase
3. parallel: whether tools can run in parallel
4. pivots: what to look for to pivot investigation
5. priorities: what findings are most important

Return ONLY valid JSON, no explanation."""

        response = await self.analyze_with_ai(prompt, {"target": target, "type": target_type})
        
        try:
            plan = json.loads(response)
            return plan
        except:
            # Fallback to default plan
            return self.get_default_plan(target_type)
    
    def get_default_plan(self, target_type: str) -> Dict[str, Any]:
        """Get default reconnaissance plan based on target type"""
        if target_type == "DOMAIN":
            return {
                "phases": [
                    {
                        "name": "subdomain_enum",
                        "tools": ["amass", "subfinder"],
                        "parallel": True,
                    },
                    {
                        "name": "web_analysis",
                        "tools": ["httpx", "whatweb"],
                        "parallel": True,
                    },
                    {
                        "name": "vulnerability_scan",
                        "tools": ["nuclei"],
                        "parallel": False,
                    },
                ],
                "pivots": ["subdomains", "ips", "technologies"],
                "priorities": ["vulnerabilities", "exposed_services", "subdomains"],
            }
        elif target_type == "IP":
            return {
                "phases": [
                    {
                        "name": "port_scan",
                        "tools": ["naabu"],
                        "parallel": False,
                    },
                    {
                        "name": "service_detection",
                        "tools": ["httpx"],
                        "parallel": False,
                    },
                ],
                "pivots": ["open_ports", "services"],
                "priorities": ["exposed_services", "vulnerabilities"],
            }
        elif target_type == "USERNAME":
            return {
                "phases": [
                    {
                        "name": "social_media",
                        "tools": ["sherlock", "maigret"],
                        "parallel": True,
                    },
                ],
                "pivots": ["profiles", "emails"],
                "priorities": ["social_profiles", "leaked_data"],
            }
        else:
            return {
                "phases": [],
                "pivots": [],
                "priorities": [],
            }
    
    async def select_tools(self, plan: Dict[str, Any]) -> List[str]:
        """Select tools based on plan"""
        tools = []
        for phase in plan.get("phases", []):
            tools.extend(phase.get("tools", []))
        return list(set(tools))
    
    async def execute_tools(self, target: str, tools: List[str], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tools according to plan"""
        results = {}
        
        for phase in plan.get("phases", []):
            phase_name = phase.get("name")
            phase_tools = phase.get("tools", [])
            parallel = phase.get("parallel", False)
            
            self.log_action(f"Executing phase: {phase_name}", {"tools": phase_tools})
            
            # TODO: Call tool orchestrator API
            # For now, return mock results
            for tool in phase_tools:
                results[tool] = {
                    "success": True,
                    "data": {},
                }
        
        return results
    
    async def enrich_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich results with additional intelligence"""
        enriched = {
            "entities": [],
            "relationships": [],
            "metadata": {},
        }
        
        # Extract entities from tool results
        for tool, result in results.items():
            if result.get("success"):
                data = result.get("data", {})
                
                # Extract subdomains
                if "subdomains" in data:
                    for subdomain in data["subdomains"]:
                        enriched["entities"].append({
                            "type": "DOMAIN",
                            "value": subdomain,
                            "source": tool,
                        })
                
                # Extract IPs
                if "ips" in data:
                    for ip in data["ips"]:
                        enriched["entities"].append({
                            "type": "IP",
                            "value": ip,
                            "source": tool,
                        })
                
                # Extract vulnerabilities
                if "vulnerabilities" in data:
                    for vuln in data["vulnerabilities"]:
                        enriched["entities"].append({
                            "type": "VULNERABILITY",
                            "value": vuln.get("name"),
                            "severity": vuln.get("severity"),
                            "source": tool,
                        })
        
        return enriched
    
    async def identify_pivots(self, enriched: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify pivot opportunities"""
        pivots = []
        
        entities = enriched.get("entities", [])
        
        # Group by type
        by_type = {}
        for entity in entities:
            entity_type = entity.get("type")
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append(entity)
        
        # Suggest pivots
        if "DOMAIN" in by_type and len(by_type["DOMAIN"]) > 5:
            pivots.append({
                "type": "subdomain_expansion",
                "reason": f"Found {len(by_type['DOMAIN'])} subdomains, investigate further",
                "targets": [e["value"] for e in by_type["DOMAIN"][:5]],
            })
        
        if "IP" in by_type:
            pivots.append({
                "type": "ip_investigation",
                "reason": f"Found {len(by_type['IP'])} IPs, scan for services",
                "targets": [e["value"] for e in by_type["IP"]],
            })
        
        if "VULNERABILITY" in by_type:
            critical = [e for e in by_type["VULNERABILITY"] if e.get("severity") == "critical"]
            if critical:
                pivots.append({
                    "type": "vulnerability_analysis",
                    "reason": f"Found {len(critical)} critical vulnerabilities",
                    "targets": [e["value"] for e in critical],
                })
        
        return pivots
    
    async def correlate_graph(self, enriched: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate entities in graph"""
        # TODO: Call graph engine API
        return {
            "nodes": len(enriched.get("entities", [])),
            "edges": 0,
            "clusters": [],
        }
    
    async def ai_reasoning(
        self,
        enriched: Dict[str, Any],
        graph_data: Dict[str, Any],
        pivots: List[Dict[str, Any]]
    ) -> str:
        """AI reasoning over collected data"""
        prompt = f"""Analyze the following reconnaissance results:

Entities found: {len(enriched.get('entities', []))}
Graph nodes: {graph_data.get('nodes', 0)}
Pivot opportunities: {len(pivots)}

Entities by type:
{self._summarize_entities(enriched)}

Pivots:
{json.dumps(pivots, indent=2)}

Provide:
1. Key findings summary
2. Risk assessment
3. Suspicious patterns
4. Recommended next steps
5. Investigation priorities

Be specific and actionable. Focus on security implications."""

        return await self.analyze_with_ai(prompt, {
            "enriched": enriched,
            "graph": graph_data,
            "pivots": pivots,
        })
    
    def _summarize_entities(self, enriched: Dict[str, Any]) -> str:
        """Summarize entities by type"""
        by_type = {}
        for entity in enriched.get("entities", []):
            entity_type = entity.get("type")
            by_type[entity_type] = by_type.get(entity_type, 0) + 1
        
        return "\n".join([f"- {t}: {c}" for t, c in by_type.items()])
