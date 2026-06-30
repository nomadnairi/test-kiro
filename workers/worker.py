import asyncio
import json
import os
import sys
from redis import Redis
from typing import Dict, Any
import logging

# Add agents to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))

from recon_agent import ReconAgent
from threat_intel_agent import ThreatIntelAgent
from ioc_agent import IOCAgent
from graph_agent import GraphAnalysisAgent
from report_agent import ReportAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Worker:
    def __init__(self):
        self.redis = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        self.ai_router_url = os.getenv('AI_ROUTER_URL', 'http://localhost:8003')
        self.running = False
        
        # Initialize agents
        self.agents = {
            'RECON': ReconAgent(self.ai_router_url, {}),
            'THREAT_INTEL': ThreatIntelAgent(self.ai_router_url, {}),
            'IOC': IOCAgent(self.ai_router_url),
            'GRAPH_ANALYSIS': GraphAnalysisAgent(
                self.ai_router_url,
                os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
                os.getenv('NEO4J_USER', 'neo4j'),
                os.environ['NEO4J_PASSWORD']
            ),
            'REPORT': ReportAgent(self.ai_router_url),
        }
    
    async def start(self):
        """Start worker"""
        self.running = True
        logger.info("Worker started")
        
        while self.running:
            try:
                # Get task from queue
                task_data = self.redis.zpopmin('cyberintel:tasks', 1)
                
                if not task_data:
                    await asyncio.sleep(1)
                    continue
                
                task_id = task_data[0][0].decode('utf-8')
                task_json = self.redis.get(f'task:{task_id}')
                
                if not task_json:
                    continue
                
                task = json.loads(task_json)
                
                # Process task
                await self.process_task(task)
                
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)
    
    async def process_task(self, task: Dict[str, Any]):
        """Process a task"""
        task_id = task['id']
        agent_type = task['agentType']
        
        logger.info(f"Processing task {task_id} with agent {agent_type}")
        
        try:
            # Get agent
            agent = self.agents.get(agent_type)
            if not agent:
                raise Exception(f"Unknown agent type: {agent_type}")
            
            # Execute agent
            result = await agent.execute(task['payload'])
            
            # Mark task as complete
            await self.complete_task(task_id, result)
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            await self.fail_task(task_id, str(e))
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as complete"""
        task_json = self.redis.get(f'task:{task_id}')
        if not task_json:
            return
        
        task = json.loads(task_json)
        task['status'] = 'COMPLETED'
        task['result'] = result
        task['completedAt'] = asyncio.get_event_loop().time()
        
        self.redis.set(f'task:{task_id}', json.dumps(task), ex=86400)
        
        # Publish update
        self.redis.publish('task:updates', json.dumps({
            'taskId': task_id,
            'status': 'COMPLETED',
            'result': result
        }))
        
        logger.info(f"Task {task_id} completed")
    
    async def fail_task(self, task_id: str, error: str):
        """Mark task as failed"""
        task_json = self.redis.get(f'task:{task_id}')
        if not task_json:
            return
        
        task = json.loads(task_json)
        
        # Check retries
        if task['retries'] < task['maxRetries']:
            task['retries'] += 1
            task['status'] = 'RETRYING'
            
            # Re-queue with exponential backoff
            delay = 2 ** task['retries']
            score = asyncio.get_event_loop().time() + delay
            self.redis.zadd('cyberintel:tasks', {task_id: score})
            
            logger.warning(f"Task {task_id} retrying (attempt {task['retries']})")
        else:
            task['status'] = 'FAILED'
            task['error'] = error
            task['completedAt'] = asyncio.get_event_loop().time()
            
            logger.error(f"Task {task_id} failed permanently: {error}")
        
        self.redis.set(f'task:{task_id}', json.dumps(task), ex=86400)
        
        # Publish update
        self.redis.publish('task:updates', json.dumps({
            'taskId': task_id,
            'status': task['status'],
            'error': error
        }))
    
    def stop(self):
        """Stop worker"""
        self.running = False
        logger.info("Worker stopped")


async def main():
    worker = Worker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        worker.stop()


if __name__ == '__main__':
    asyncio.run(main())
