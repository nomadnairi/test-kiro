from base_agent import BaseAgent
from typing import Dict, Any, List


class CorrelationAgent(BaseAgent):
    """Correlation Agent - Correlate data across multiple sources"""
    
    def __init__(self, ai_router_url: str):
        super().__init__("CORRELATION", ai_router_url)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute correlation analysis"""
        scan_id = context.get("scanId")
        
        self.log_action("Starting correlation analysis", {"scan_id": scan_id})
        
        results = {
            "scanId": scan_id,
            "correlations": [],
            "patterns": [],
            "anomalies": [],
            "insights": [],
            "analysis": ""
        }
        
        # Find correlations
        results["correlations"] = await self.find_correlations(scan_id)
        
        # Identify patterns
        results["patterns"] = await self.identify_patterns(scan_id)
        
        # Detect anomalies
        results["anomalies"] = await self.detect_anomalies(scan_id)
        
        # Generate insights
        results["insights"] = await self.generate_insights(results)
        
        # AI analysis
        results["analysis"] = await self.analyze_correlations(results)
        
        self.log_action("Correlation analysis complete", {
            "scan_id": scan_id,
            "correlations": len(results["correlations"]),
            "patterns": len(results["patterns"])
        })
        
        return results
    
    async def _get_scan_dataset(self, scan_id: str) -> List[Dict[str, Any]]:
        """Fetch dataset for anomaly detection"""
        # TODO: Implement actual database query to fetch scan dataset
        return []

    async def find_correlations(self, scan_id: str) -> List[Dict[str, Any]]:
        """Find correlations between entities"""
        # TODO: Implement correlation logic
        return []
    
    async def identify_patterns(self, scan_id: str) -> List[Dict[str, Any]]:
        """Identify patterns in data"""
        # TODO: Implement pattern identification
        return []
    
    async def detect_anomalies(self, scan_id: str) -> List[Dict[str, Any]]:
        """Detect anomalies"""
        dataset = await self._get_scan_dataset(scan_id)
        if not dataset:
            return []

        anomalies = []

        categorical_frequencies = {}
        numerical_stats = {}

        # Calculate frequencies and collect numerical values
        for entry in dataset:
            for key, value in entry.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if key not in numerical_stats:
                        numerical_stats[key] = []
                    numerical_stats[key].append(value)
                elif isinstance(value, str):
                    if key not in categorical_frequencies:
                        categorical_frequencies[key] = {}
                    categorical_frequencies[key][value] = categorical_frequencies[key].get(value, 0) + 1

        # Establish baselines (mean, std_dev) for numerical stats
        baselines = {}
        for key, values in numerical_stats.items():
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            baselines[key] = {"mean": mean, "std_dev": std_dev}

        # Analyze each entry for anomalies based on baselines and frequencies
        total_entries = len(dataset)
        for entry in dataset:
            reasons = []
            anomaly_score = 0.0

            for key, value in entry.items():
                if key in baselines and isinstance(value, (int, float)) and not isinstance(value, bool):
                    stats = baselines[key]
                    if stats["std_dev"] > 0:
                        z_score = abs(value - stats["mean"]) / stats["std_dev"]
                        if z_score > 2.0:
                            reasons.append(f"Statistically significant deviation in '{key}' (Z-score: {z_score:.2f})")
                            anomaly_score += z_score * 0.1

                elif key in categorical_frequencies and isinstance(value, str):
                    frequency = categorical_frequencies[key][value]
                    prevalence = frequency / total_entries
                    if prevalence < 0.2:
                        reasons.append(f"Rare value for '{key}': {value} (Prevalence: {prevalence:.0%})")
                        anomaly_score += (1.0 - prevalence) * 0.2

            if reasons:
                anomalies.append({
                    "entity": entry,
                    "reasons": reasons,
                    "anomaly_score": min(anomaly_score, 1.0)
                })

        anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)
        return anomalies
    
    async def generate_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        if len(results["correlations"]) > 10:
            insights.append("High number of correlations detected - possible infrastructure cluster")
        
        if len(results["anomalies"]) > 0:
            insights.append(f"{len(results['anomalies'])} anomalies detected - requires investigation")
        
        return insights
    
    async def analyze_correlations(self, results: Dict[str, Any]) -> str:
        """AI-powered correlation analysis"""
        prompt = f"""Analyze the following correlation data:
        
        Correlations: {len(results['correlations'])}
        Patterns: {len(results['patterns'])}
        Anomalies: {len(results['anomalies'])}
        
        Provide:
        1. Key correlations
        2. Pattern analysis
        3. Anomaly assessment
        4. Threat implications
        5. Investigation priorities
        """
        
        return await self.analyze_with_ai(prompt, results)
