from base_agent import BaseAgent
from typing import Dict, Any, List
from neo4j import AsyncGraphDatabase


class GraphAnalysisAgent(BaseAgent):
    """Graph Analysis Agent - Analyze entity relationships and attack chains"""
    
    def __init__(self, ai_router_url: str, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        super().__init__("GRAPH_ANALYSIS", ai_router_url)
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = AsyncGraphDatabase.driver(
            self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute graph analysis"""
        scan_id = context.get("scanId")
        
        self.log_action("Analyzing graph", {"scan_id": scan_id})
        
        results = {
            "scanId": scan_id,
            "clusters": [],
            "paths": [],
            "centrality": {},
            "analysis": ""
        }
        
        # Identify clusters
        results["clusters"] = await self.identify_clusters(scan_id)
        
        # Find attack paths
        results["paths"] = await self.find_attack_paths(scan_id)
        
        # Calculate centrality
        results["centrality"] = await self.calculate_centrality(scan_id)
        
        # AI analysis
        results["analysis"] = await self.analyze_graph(results)
        
        self.log_action("Graph analysis complete", {
            "clusters": len(results["clusters"]),
            "paths": len(results["paths"])
        })
        
        return results
    
    async def identify_clusters(self, scan_id: str) -> List[Dict[str, Any]]:
        """Identify entity clusters"""
        query = """
        MATCH (n)-[r]-(m)
        WITH n, count(m) as degree, collect(m.id) as connected
        WHERE degree >= 2
        RETURN n.id as center, connected, degree
        ORDER BY degree DESC
        LIMIT 10
        """
        clusters = []
        try:
            async with self.driver.session() as session:
                result = await session.run(query)
                async for record in result:
                    clusters.append({
                        "center": record.get("center"),
                        "connected": record.get("connected", []),
                        "size": record.get("degree", 0) + 1
                    })
        except Exception as e:
            self.log_action("Error identifying clusters", {"error": str(e)})
        return clusters
    
    async def find_attack_paths(self, scan_id: str) -> List[Dict[str, Any]]:
        """Find potential attack paths"""
        query = """
        MATCH path = (start)-[*1..5]->(end)
        WHERE end:VULNERABILITY OR end:EXPOSED_SERVICE
        RETURN path
        LIMIT 10
        """
        paths = []
        try:
            async with self.driver.session() as session:
                result = await session.run(query)
                async for record in result:
                    path = record.get("path")
                    if path:
                        paths.append({
                            "nodes": [node.get("id") for node in path.nodes if node],
                            "length": len(path.relationships)
                        })
        except Exception as e:
            self.log_action("Error finding attack paths", {"error": str(e)})
        return paths
    
    async def calculate_centrality(self, scan_id: str) -> Dict[str, Any]:
        """Calculate node centrality metrics"""
        query = """
        MATCH (n)-[r]-()
        WITH n, count(r) as degree
        RETURN n.id as node_id, degree
        ORDER BY degree DESC
        LIMIT 50
        """
        centrality = {}
        try:
            async with self.driver.session() as session:
                result = await session.run(query)
                async for record in result:
                    node_id = record.get("node_id")
                    if node_id:
                        centrality[node_id] = record.get("degree", 0)
        except Exception as e:
            self.log_action("Error calculating centrality", {"error": str(e)})
        return centrality
    
    async def analyze_graph(self, results: Dict[str, Any]) -> str:
        """AI-powered graph analysis"""
        prompt = f"""Analyze the following graph structure:
        
        Clusters: {len(results['clusters'])}
        Attack Paths: {len(results['paths'])}
        
        Provide:
        1. Key infrastructure nodes
        2. Attack chain analysis
        3. Pivot opportunities
        4. Defensive recommendations
        """
        
        return await self.analyze_with_ai(prompt, results)

    async def close(self):
        """Cleanup resources"""
        if hasattr(self, 'driver'):
            await self.driver.close()
        await super().close()
