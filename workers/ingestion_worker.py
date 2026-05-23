import asyncio
import feedparser
import httpx
from typing import Dict, Any, List
from redis import Redis
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IngestionWorker:
    """Real-time intelligence ingestion worker"""
    
    def __init__(self, redis_url: str, db_url: str):
        self.redis = Redis.from_url(redis_url)
        self.db_url = db_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.running = False
    
    async def start(self):
        """Start ingestion worker"""
        self.running = True
        logger.info("Ingestion worker started")
        
        # Start ingestion pipelines
        await asyncio.gather(
            self.ingest_rss_feeds(),
            self.ingest_cve_feeds(),
            self.ingest_ioc_feeds(),
            self.monitor_telegram_channels(),
        )
    
    async def ingest_rss_feeds(self):
        """Ingest RSS threat feeds"""
        feeds = [
            "https://www.cert.gov.ua/rss.xml",
            "https://www.us-cert.gov/ncas/current-activity.xml",
            "https://www.bleepingcomputer.com/feed/",
            "https://threatpost.com/feed/",
        ]
        
        while self.running:
            try:
                for feed_url in feeds:
                    logger.info(f"Ingesting RSS feed: {feed_url}")
                    
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:10]:  # Process last 10 entries
                        await self.process_rss_entry(entry, feed_url)
                
                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"RSS ingestion error: {e}")
                await asyncio.sleep(60)
    
    async def process_rss_entry(self, entry: Any, source: str):
        """Process RSS feed entry"""
        try:
            # Check if already processed
            entry_id = entry.get('id') or entry.get('link')
            if self.redis.exists(f"ingestion:rss:{entry_id}"):
                return
            
            # Extract IOCs from content
            content = entry.get('summary', '') + ' ' + entry.get('title', '')
            iocs = await self.extract_iocs(content)
            
            # Store in database
            data = {
                "source": source,
                "title": entry.get('title'),
                "link": entry.get('link'),
                "published": entry.get('published'),
                "content": entry.get('summary'),
                "iocs": iocs,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Publish to Redis
            self.redis.publish('intelligence:feed', json.dumps(data))
            
            # Mark as processed
            self.redis.setex(f"ingestion:rss:{entry_id}", 86400, "1")
            
            logger.info(f"Processed RSS entry: {entry.get('title')}")
            
        except Exception as e:
            logger.error(f"Failed to process RSS entry: {e}")
    
    async def ingest_cve_feeds(self):
        """Ingest CVE feeds"""
        while self.running:
            try:
                logger.info("Ingesting CVE feed")
                
                # NVD Recent CVEs
                response = await self.client.get(
                    "https://services.nvd.nist.gov/rest/json/cves/2.0",
                    params={"resultsPerPage": 20}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for cve in data.get('vulnerabilities', []):
                        await self.process_cve(cve)
                
                # Wait before next cycle
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"CVE ingestion error: {e}")
                await asyncio.sleep(300)
    
    async def process_cve(self, cve_data: Dict[str, Any]):
        """Process CVE entry"""
        try:
            cve = cve_data.get('cve', {})
            cve_id = cve.get('id')
            
            # Check if already processed
            if self.redis.exists(f"ingestion:cve:{cve_id}"):
                return
            
            data = {
                "type": "CVE",
                "cve_id": cve_id,
                "description": cve.get('descriptions', [{}])[0].get('value'),
                "published": cve.get('published'),
                "severity": self.extract_severity(cve),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Publish to Redis
            self.redis.publish('intelligence:cve', json.dumps(data))
            
            # Mark as processed
            self.redis.setex(f"ingestion:cve:{cve_id}", 86400 * 7, "1")
            
            logger.info(f"Processed CVE: {cve_id}")
            
        except Exception as e:
            logger.error(f"Failed to process CVE: {e}")
    
    async def ingest_ioc_feeds(self):
        """Ingest IOC feeds"""
        feeds = [
            "https://feodotracker.abuse.ch/downloads/ipblocklist.txt",
            "https://sslbl.abuse.ch/blacklist/sslipblacklist.txt",
        ]
        
        while self.running:
            try:
                for feed_url in feeds:
                    logger.info(f"Ingesting IOC feed: {feed_url}")
                    
                    response = await self.client.get(feed_url)
                    
                    if response.status_code == 200:
                        lines = response.text.split('\n')
                        
                        for line in lines:
                            if line.strip() and not line.startswith('#'):
                                await self.process_ioc(line.strip(), feed_url)
                
                # Wait before next cycle
                await asyncio.sleep(1800)  # 30 minutes
                
            except Exception as e:
                logger.error(f"IOC ingestion error: {e}")
                await asyncio.sleep(300)
    
    async def process_ioc(self, ioc: str, source: str):
        """Process IOC"""
        try:
            # Check if already processed
            if self.redis.exists(f"ingestion:ioc:{ioc}"):
                return
            
            data = {
                "type": "IOC",
                "value": ioc,
                "source": source,
                "threat_level": "MEDIUM",
                "timestamp": datetime.now().isoformat(),
            }
            
            # Publish to Redis
            self.redis.publish('intelligence:ioc', json.dumps(data))
            
            # Mark as processed
            self.redis.setex(f"ingestion:ioc:{ioc}", 86400, "1")
            
        except Exception as e:
            logger.error(f"Failed to process IOC: {e}")
    
    async def monitor_telegram_channels(self):
        """Monitor Telegram channels for threat intelligence"""
        # TODO: Implement Telegram monitoring
        # This requires Telegram API credentials and channel access
        pass
    
    async def extract_iocs(self, text: str) -> List[str]:
        """Extract IOCs from text"""
        import re
        
        iocs = []
        
        # IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        iocs.extend(re.findall(ip_pattern, text))
        
        # Domains
        domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
        iocs.extend(re.findall(domain_pattern, text, re.IGNORECASE))
        
        # Hashes (MD5, SHA1, SHA256)
        hash_pattern = r'\b[a-fA-F0-9]{32,64}\b'
        iocs.extend(re.findall(hash_pattern, text))
        
        return list(set(iocs))
    
    def extract_severity(self, cve: Dict[str, Any]) -> str:
        """Extract CVE severity"""
        metrics = cve.get('metrics', {})
        
        if 'cvssMetricV31' in metrics:
            score = metrics['cvssMetricV31'][0].get('cvssData', {}).get('baseScore', 0)
        elif 'cvssMetricV2' in metrics:
            score = metrics['cvssMetricV2'][0].get('cvssData', {}).get('baseScore', 0)
        else:
            return 'UNKNOWN'
        
        if score >= 9.0:
            return 'CRITICAL'
        elif score >= 7.0:
            return 'HIGH'
        elif score >= 4.0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def stop(self):
        """Stop ingestion worker"""
        self.running = False
        logger.info("Ingestion worker stopped")


async def main():
    worker = IngestionWorker(
        redis_url="redis://localhost:6379",
        db_url="postgresql://cyberintel:cyberintel@localhost:5432/cyberintel"
    )
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        worker.stop()


if __name__ == '__main__':
    asyncio.run(main())
