from base_agent import BaseAgent
from typing import Dict, Any, List
import hashlib


class BreachIntelligenceAgent(BaseAgent):
    """Breach Intelligence Agent - Analyze exposure and leaked credentials"""
    
    def __init__(self, ai_router_url: str, integrations_config: Dict[str, Any]):
        super().__init__("BREACH_INTELLIGENCE", ai_router_url)
        self.integrations = integrations_config
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute breach intelligence analysis"""
        target = context.get("target")
        target_type = context.get("targetType")
        
        self.log_action("Breach intelligence analysis started", {"target": target})
        
        results = {
            "target": target,
            "targetType": target_type,
            "exposures": [],
            "breaches": [],
            "credentials": [],
            "riskScore": 0,
            "timeline": [],
            "analysis": ""
        }
        
        # Check different breach sources
        if target_type == "EMAIL":
            results["exposures"] = await self.check_email_exposure(target)
        elif target_type == "DOMAIN":
            results["exposures"] = await self.check_domain_exposure(target)
        elif target_type == "USERNAME":
            results["exposures"] = await self.check_username_exposure(target)
        
        # Analyze breaches
        results["breaches"] = await self.analyze_breaches(results["exposures"])
        
        # Build timeline
        results["timeline"] = await self.build_exposure_timeline(results["breaches"])
        
        # Calculate risk
        results["riskScore"] = await self.calculate_risk_score(results)
        
        # AI analysis
        results["analysis"] = await self.ai_analysis(results)
        
        self.log_action("Breach intelligence complete", {
            "exposures": len(results["exposures"]),
            "breaches": len(results["breaches"]),
            "riskScore": results["riskScore"]
        })
        
        return results
    
    async def check_email_exposure(self, email: str) -> List[Dict[str, Any]]:
        """Check email exposure across breach databases"""
        exposures = []
        
        # HaveIBeenPwned
        hibp_result = await self.query_haveibeenpwned(email)
        if hibp_result:
            exposures.extend(hibp_result)
        
        # DeHashed (if API key available)
        if self.integrations.get("dehashed_api_key"):
            dehashed_result = await self.query_dehashed_email(email)
            if dehashed_result:
                exposures.extend(dehashed_result)
        
        # LeakCheck (if API key available)
        if self.integrations.get("leakcheck_api_key"):
            leakcheck_result = await self.query_leakcheck(email)
            if leakcheck_result:
                exposures.extend(leakcheck_result)
        
        return exposures
    
    async def check_domain_exposure(self, domain: str) -> List[Dict[str, Any]]:
        """Check domain exposure"""
        exposures = []
        
        # DeHashed domain search
        if self.integrations.get("dehashed_api_key"):
            result = await self.query_dehashed_domain(domain)
            if result:
                exposures.extend(result)
        
        return exposures
    
    async def check_username_exposure(self, username: str) -> List[Dict[str, Any]]:
        """Check username exposure"""
        exposures = []
        
        # DeHashed username search
        if self.integrations.get("dehashed_api_key"):
            result = await self.query_dehashed_username(username)
            if result:
                exposures.extend(result)
        
        return exposures
    
    async def query_haveibeenpwned(self, email: str) -> List[Dict[str, Any]]:
        """Query HaveIBeenPwned API"""
        # TODO: Implement actual API call
        return []
    
    async def query_dehashed_email(self, email: str) -> List[Dict[str, Any]]:
        """Query DeHashed for email"""
        # TODO: Implement actual API call
        return []
    
    async def query_dehashed_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Query DeHashed for domain"""
        # TODO: Implement actual API call
        return []
    
    async def query_dehashed_username(self, username: str) -> List[Dict[str, Any]]:
        """Query DeHashed for username"""
        # TODO: Implement actual API call
        return []
    
    async def query_leakcheck(self, email: str) -> List[Dict[str, Any]]:
        """Query LeakCheck API"""
        # TODO: Implement actual API call
        return []
    
    async def analyze_breaches(self, exposures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze breach data"""
        breaches = []
        
        # Group exposures by breach
        breach_map = {}
        for exposure in exposures:
            breach_name = exposure.get("breach") or exposure.get("database")
            if breach_name:
                if breach_name not in breach_map:
                    breach_map[breach_name] = {
                        "name": breach_name,
                        "date": exposure.get("date"),
                        "dataTypes": set(),
                        "records": 0,
                    }
                
                if exposure.get("dataTypes"):
                    breach_map[breach_name]["dataTypes"].update(exposure["dataTypes"])
                
                breach_map[breach_name]["records"] += 1
        
        # Convert to list
        for breach_name, breach_data in breach_map.items():
            breaches.append({
                "name": breach_name,
                "date": breach_data["date"],
                "dataTypes": list(breach_data["dataTypes"]),
                "records": breach_data["records"],
            })
        
        return breaches
    
    async def build_exposure_timeline(self, breaches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build timeline of exposures"""
        timeline = []
        
        for breach in breaches:
            if breach.get("date"):
                timeline.append({
                    "date": breach["date"],
                    "event": f"Exposed in {breach['name']}",
                    "dataTypes": breach.get("dataTypes", []),
                })
        
        # Sort by date
        timeline.sort(key=lambda x: x["date"], reverse=True)
        
        return timeline
    
    async def calculate_risk_score(self, results: Dict[str, Any]) -> int:
        """Calculate exposure risk score (0-100)"""
        score = 0
        
        # Factor in number of exposures
        exposures = len(results.get("exposures", []))
        score += min(exposures * 10, 40)
        
        # Factor in breach severity
        breaches = results.get("breaches", [])
        for breach in breaches:
            data_types = breach.get("dataTypes", [])
            if "Passwords" in data_types:
                score += 20
            if "Credit cards" in data_types:
                score += 15
            if "SSN" in data_types or "Social security numbers" in data_types:
                score += 15
        
        # Factor in recency
        timeline = results.get("timeline", [])
        if timeline:
            # Recent breaches are more concerning
            # TODO: Implement date-based scoring
            pass
        
        return min(score, 100)
    
    async def ai_analysis(self, results: Dict[str, Any]) -> str:
        """AI-powered breach analysis"""
        prompt = f"""Analyze the following breach intelligence data:

Target: {results['target']}
Type: {results['targetType']}
Exposures: {len(results['exposures'])}
Breaches: {len(results['breaches'])}
Risk Score: {results['riskScore']}/100

Breaches:
{self._format_breaches(results['breaches'])}

Timeline:
{self._format_timeline(results['timeline'])}

Provide:
1. Exposure summary
2. Risk assessment
3. Data types exposed
4. Password reuse risks
5. Recommended actions
6. Monitoring recommendations

Be specific and actionable."""

        return await self.analyze_with_ai(prompt, results)
    
    def _format_breaches(self, breaches: List[Dict[str, Any]]) -> str:
        """Format breaches for AI prompt"""
        if not breaches:
            return "None"
        
        lines = []
        for breach in breaches[:10]:  # Limit to 10
            lines.append(f"- {breach['name']}: {', '.join(breach.get('dataTypes', []))}")
        
        return "\n".join(lines)
    
    def _format_timeline(self, timeline: List[Dict[str, Any]]) -> str:
        """Format timeline for AI prompt"""
        if not timeline:
            return "None"
        
        lines = []
        for event in timeline[:10]:  # Limit to 10
            lines.append(f"- {event['date']}: {event['event']}")
        
        return "\n".join(lines)
