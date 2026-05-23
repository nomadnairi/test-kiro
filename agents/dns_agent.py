from base_agent import BaseAgent
from typing import Dict, Any, List
import dns.resolver
import dns.reversename


class DNSAgent(BaseAgent):
    """DNS Intelligence Agent - Deep DNS analysis and enumeration"""
    
    def __init__(self, ai_router_url: str):
        super().__init__("DNS", ai_router_url)
        self.resolver = dns.resolver.Resolver()
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DNS intelligence gathering"""
        target = context.get("target")
        
        self.log_action("DNS analysis started", {"target": target})
        
        results = {
            "target": target,
            "records": {},
            "nameservers": [],
            "mail_servers": [],
            "txt_records": [],
            "subdomains": [],
            "analysis": ""
        }
        
        # Gather DNS records
        results["records"]["A"] = await self.get_a_records(target)
        results["records"]["AAAA"] = await self.get_aaaa_records(target)
        results["records"]["MX"] = await self.get_mx_records(target)
        results["records"]["TXT"] = await self.get_txt_records(target)
        results["records"]["NS"] = await self.get_ns_records(target)
        results["records"]["CNAME"] = await self.get_cname_records(target)
        
        # Extract specific data
        results["nameservers"] = results["records"]["NS"]
        results["mail_servers"] = results["records"]["MX"]
        results["txt_records"] = results["records"]["TXT"]
        
        # AI-powered analysis
        results["analysis"] = await self.analyze_dns(results)
        
        self.log_action("DNS analysis complete", {
            "target": target,
            "records_found": sum(len(v) if isinstance(v, list) else 1 for v in results["records"].values())
        })
        
        return results
    
    async def get_a_records(self, domain: str) -> List[str]:
        """Get A records"""
        try:
            answers = self.resolver.resolve(domain, 'A')
            return [str(rdata) for rdata in answers]
        except Exception as e:
            self.log_action("A record lookup failed", {"domain": domain, "error": str(e)})
            return []
    
    async def get_aaaa_records(self, domain: str) -> List[str]:
        """Get AAAA records"""
        try:
            answers = self.resolver.resolve(domain, 'AAAA')
            return [str(rdata) for rdata in answers]
        except Exception:
            return []
    
    async def get_mx_records(self, domain: str) -> List[Dict[str, Any]]:
        """Get MX records"""
        try:
            answers = self.resolver.resolve(domain, 'MX')
            return [{"priority": rdata.preference, "exchange": str(rdata.exchange)} for rdata in answers]
        except Exception:
            return []
    
    async def get_txt_records(self, domain: str) -> List[str]:
        """Get TXT records"""
        try:
            answers = self.resolver.resolve(domain, 'TXT')
            return [str(rdata) for rdata in answers]
        except Exception:
            return []
    
    async def get_ns_records(self, domain: str) -> List[str]:
        """Get NS records"""
        try:
            answers = self.resolver.resolve(domain, 'NS')
            return [str(rdata) for rdata in answers]
        except Exception:
            return []
    
    async def get_cname_records(self, domain: str) -> List[str]:
        """Get CNAME records"""
        try:
            answers = self.resolver.resolve(domain, 'CNAME')
            return [str(rdata) for rdata in answers]
        except Exception:
            return []
    
    async def analyze_dns(self, results: Dict[str, Any]) -> str:
        """AI-powered DNS analysis"""
        prompt = f"""Analyze the following DNS configuration:
        
        Domain: {results['target']}
        A Records: {len(results['records'].get('A', []))}
        MX Records: {len(results['records'].get('MX', []))}
        TXT Records: {len(results['records'].get('TXT', []))}
        Nameservers: {len(results['nameservers'])}
        
        Provide:
        1. DNS configuration assessment
        2. Security concerns (SPF, DMARC, DNSSEC)
        3. Potential misconfigurations
        4. Recommendations
        """
        
        return await self.analyze_with_ai(prompt, results)
