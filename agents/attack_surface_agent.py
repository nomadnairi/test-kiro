from base_agent import BaseAgent
from typing import Dict, Any, List


class AttackSurfaceAgent(BaseAgent):
    """Attack Surface Agent - Map and analyze attack surface"""
    
    def __init__(self, ai_router_url: str):
        super().__init__("ATTACK_SURFACE", ai_router_url)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute attack surface mapping"""
        scan_id = context.get("scanId")
        
        self.log_action("Mapping attack surface", {"scan_id": scan_id})
        
        results = {
            "scanId": scan_id,
            "exposed_assets": [],
            "entry_points": [],
            "vulnerabilities": [],
            "risk_score": 0,
            "analysis": ""
        }
        
        # Identify exposed assets
        results["exposed_assets"] = await self.identify_exposed_assets(scan_id)
        
        # Find entry points
        results["entry_points"] = await self.find_entry_points(scan_id)
        
        # Correlate vulnerabilities
        results["vulnerabilities"] = await self.correlate_vulnerabilities(scan_id, results.get("exposed_assets", []))
        
        # Calculate risk score
        results["risk_score"] = await self.calculate_risk_score(results)
        
        # AI analysis
        results["analysis"] = await self.analyze_attack_surface(results)
        
        self.log_action("Attack surface mapping complete", {
            "scan_id": scan_id,
            "exposed_assets": len(results["exposed_assets"]),
            "risk_score": results["risk_score"]
        })
        
        return results
    
    async def identify_exposed_assets(self, scan_id: str) -> List[Dict[str, Any]]:
        """Identify exposed assets"""
        # TODO: Query database for exposed assets
        return []
    
    async def find_entry_points(self, scan_id: str) -> List[Dict[str, Any]]:
        """Find potential entry points"""
        # TODO: Identify entry points from scan data
        return []
    
    async def correlate_vulnerabilities(self, scan_id: str, exposed_assets: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Correlate known vulnerabilities"""
        vulnerabilities = []
        if not exposed_assets:
            return vulnerabilities

        try:
            for asset in exposed_assets:
                # Build keyword search string from asset data defensively
                keywords = []
                for field in ["technology", "vendor", "name", "version", "product", "service"]:
                    val = asset.get(field)
                    if val:
                        keywords.append(str(val))

                if not keywords:
                    # Try using type or value if present
                    val = asset.get("value") or asset.get("type")
                    if val:
                        keywords.append(str(val))

                if not keywords:
                    continue

                keyword_str = " ".join(keywords)
                self.log_action("Querying NVD for asset", {"keywords": keyword_str})

                response = await self.client.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={"keywordSearch": keyword_str, "resultsPerPage": 5}
                )

                if response.status_code == 200:
                    data = response.json()

                    for cve_item in data.get('vulnerabilities', []):
                        cve = cve_item.get('cve', {})
                        cve_id = cve.get('id')
                        if not cve_id:
                            continue

                        # Extract severity
                        severity = "UNKNOWN"
                        metrics = cve.get('metrics', {})
                        if 'cvssMetricV31' in metrics:
                            severity = metrics['cvssMetricV31'][0].get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                        elif 'cvssMetricV30' in metrics:
                            severity = metrics['cvssMetricV30'][0].get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                        elif 'cvssMetricV2' in metrics:
                            severity = metrics['cvssMetricV2'][0].get('baseSeverity', 'UNKNOWN')

                        desc = ""
                        for description in cve.get('descriptions', []):
                            if description.get('lang') == 'en':
                                desc = description.get('value', '')
                                break

                        vulnerabilities.append({
                            "cve_id": cve_id,
                            "severity": severity,
                            "description": desc,
                            "asset": asset
                        })
        except Exception as e:
            self.log_action("Error correlating vulnerabilities", {"error": str(e)})

        return vulnerabilities
    
    async def calculate_risk_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall risk score (0-100)"""
        score = 0
        
        # Factor in exposed assets
        score += min(len(results["exposed_assets"]) * 5, 40)
        
        # Factor in entry points
        score += min(len(results["entry_points"]) * 3, 30)
        
        # Factor in vulnerabilities
        score += min(len(results["vulnerabilities"]) * 10, 30)
        
        return min(score, 100)
    
    async def analyze_attack_surface(self, results: Dict[str, Any]) -> str:
        """AI-powered attack surface analysis"""
        prompt = f"""Analyze the following attack surface:
        
        Exposed Assets: {len(results['exposed_assets'])}
        Entry Points: {len(results['entry_points'])}
        Vulnerabilities: {len(results['vulnerabilities'])}
        Risk Score: {results['risk_score']}/100
        
        Provide:
        1. Attack surface summary
        2. Critical exposures
        3. Attack vectors
        4. Mitigation priorities
        5. Hardening recommendations
        """
        
        return await self.analyze_with_ai(prompt, results)
