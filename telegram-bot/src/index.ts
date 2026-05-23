import { Telegraf, Context } from 'telegraf';
import { message } from 'telegraf/filters';
import { createLogger } from '@cyberintel/shared';
import axios from 'axios';
import Redis from 'ioredis';
import express from 'express';

const logger = createLogger({ service: 'telegram-bot' });

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '';
const API_URL = process.env.API_URL || 'http://localhost:8000';
const HEALTH_PORT = parseInt(process.env.HEALTH_PORT || '8006', 10);

const bot = new Telegraf(BOT_TOKEN);
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// Health check server
const healthApp = express();

healthApp.get('/health', async (req, res) => {
  try {
    // Check Redis connectivity
    await redis.ping();

    // Check bot status
    const botInfo = await bot.telegram.getMe();

    res.json({
      status: 'healthy',
      service: 'telegram-bot',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      bot: {
        username: botInfo.username,
        id: botInfo.id,
      },
      dependencies: {
        redis: 'up',
        telegram: 'up',
      },
    });
  } catch (error: any) {
    logger.error('Health check failed', error);
    res.status(503).json({
      status: 'unhealthy',
      service: 'telegram-bot',
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
});

healthApp.listen(HEALTH_PORT, () => {
  logger.info(`Health check server listening on port ${HEALTH_PORT}`);
});

// Middleware: Authentication
bot.use(async (ctx, next) => {
  const userId = ctx.from?.id;
  if (!userId) {
    return ctx.reply('❌ Authentication required');
  }

  // Check if user is authorized
  const authorized = await redis.get(`telegram:user:${userId}`);
  if (!authorized) {
    return ctx.reply('❌ You are not authorized. Please contact admin.');
  }

  return next();
});

// Command: /start
bot.command('start', async (ctx) => {
  await ctx.reply(`🤖 CyberIntel AI Assistant

Available commands:
/scan <target> - Start reconnaissance scan
/ioc <indicator> - Check IOC
/entity <value> - Search entity
/report <scanId> - Get scan report
/threatfeed - Subscribe to threat feed
/graph <entityId> - View entity graph
/breach <email> - Check breach exposure
/help - Show this message

Example:
/scan example.com
/ioc 1.2.3.4
/breach user@example.com`);
});

// Command: /scan
bot.command('scan', async (ctx) => {
  const args = ctx.message.text.split(' ').slice(1);
  
  if (args.length === 0) {
    return ctx.reply('❌ Usage: /scan <target>\nExample: /scan example.com');
  }

  const target = args[0];
  
  await ctx.reply(`🔍 Starting scan for: ${target}\nThis may take a few minutes...`);

  try {
    const response = await axios.post(`${API_URL}/api/scans`, {
      target,
      autoRecon: true,
    }, {
      headers: {
        'Authorization': `Bearer ${await getUserToken(ctx.from!.id)}`,
      },
      timeout: 10000, // 10 second timeout
    });

    const scanId = response.data.scanId;
    
    // Store scan for user
    await redis.set(`telegram:scan:${ctx.from!.id}:${scanId}`, target, 'EX', 86400);

    await ctx.reply(`✅ Scan started!
    
Scan ID: ${scanId}
Target: ${target}

You will receive updates as the scan progresses.
Use /report ${scanId} to get the full report.`);

    // Subscribe to scan updates
    subscribeToScanUpdates(ctx, scanId);

  } catch (error: any) {
    logger.error('Scan command failed', error);
    await ctx.reply(`❌ Failed to start scan: ${error.response?.data?.message || error.message}`);
  }
});

// Command: /ioc
bot.command('ioc', async (ctx) => {
  const args = ctx.message.text.split(' ').slice(1);
  
  if (args.length === 0) {
    return ctx.reply('❌ Usage: /ioc <indicator>\nExample: /ioc 1.2.3.4');
  }

  const indicator = args[0];
  
  await ctx.reply(`🔍 Checking IOC: ${indicator}...`);

  try {
    const response = await axios.get(`${API_URL}/api/iocs?q=${indicator}`, {
      headers: {
        'Authorization': `Bearer ${await getUserToken(ctx.from!.id)}`,
      },
      timeout: 5000,
    });

    const iocs = response.data.iocs;

    if (iocs.length === 0) {
      return ctx.reply(`✅ No IOC found for: ${indicator}`);
    }

    const ioc = iocs[0];
    await ctx.reply(`🚨 IOC Found!

Value: ${ioc.value}
Type: ${ioc.type}
Threat Level: ${ioc.threat_level}
Source: ${ioc.source}
Confidence: ${ioc.confidence}%

Description: ${ioc.description || 'N/A'}`);

  } catch (error: any) {
    logger.error('IOC command failed', error);
    await ctx.reply(`❌ Failed to check IOC: ${error.response?.data?.message || error.message}`);
  }
});

// Command: /entity
bot.command('entity', async (ctx) => {
  const args = ctx.message.text.split(' ').slice(1);
  
  if (args.length === 0) {
    return ctx.reply('❌ Usage: /entity <value>\nExample: /entity example.com');
  }

  const value = args[0];
  
  await ctx.reply(`🔍 Searching entity: ${value}...`);

  try {
    const response = await axios.get(`${API_URL}/api/entities?q=${value}`, {
      headers: {
        'Authorization': `Bearer ${await getUserToken(ctx.from!.id)}`,
      },
      timeout: 5000,
    });

    const entities = response.data.entities;

    if (entities.length === 0) {
      return ctx.reply(`❌ No entity found for: ${value}`);
    }

    const entity = entities[0];
    await ctx.reply(`📊 Entity Found!

Value: ${entity.value}
Type: ${entity.type}
Threat Level: ${entity.threat_level || 'UNKNOWN'}
First Seen: ${new Date(entity.first_seen).toLocaleDateString()}
Last Seen: ${new Date(entity.last_seen).toLocaleDateString()}

Use /graph ${entity.id} to view relationships.`);

  } catch (error: any) {
    logger.error('Entity command failed', error);
    await ctx.reply(`❌ Failed to search entity: ${error.response?.data?.message || error.message}`);
  }
});

// Command: /report
bot.command('report', async (ctx) => {
  const args = ctx.message.text.split(' ').slice(1);
  
  if (args.length === 0) {
    return ctx.reply('❌ Usage: /report <scanId>');
  }

  const scanId = args[0];
  
  await ctx.reply(`📄 Generating report for scan: ${scanId}...`);

  try {
    const response = await axios.get(`${API_URL}/api/scans/${scanId}/results`, {
      headers: {
        'Authorization': `Bearer ${await getUserToken(ctx.from!.id)}`,
      },
      timeout: 10000,
    });

    const { scan, entities, iocs } = response.data;

    await ctx.reply(`📊 Scan Report

Target: ${scan.target}
Status: ${scan.status}
Progress: ${scan.progress}%

📈 Results:
• Entities: ${entities.length}
• IOCs: ${iocs.length}

🔍 Top Findings:
${formatTopFindings(entities, iocs)}

View full report: ${API_URL}/scans/${scanId}`);

  } catch (error: any) {
    logger.error('Report command failed', error);
    await ctx.reply(`❌ Failed to generate report: ${error.response?.data?.message || error.message}`);
  }
});

// Command: /breach
bot.command('breach', async (ctx) => {
  const args = ctx.message.text.split(' ').slice(1);
  
  if (args.length === 0) {
    return ctx.reply('❌ Usage: /breach <email>\nExample: /breach user@example.com');
  }

  const email = args[0];
  
  await ctx.reply(`🔍 Checking breach exposure for: ${email}...`);

  try {
    // TODO: Implement breach check API endpoint
    await ctx.reply(`⚠️ Breach check feature coming soon!`);

  } catch (error: any) {
    logger.error('Breach command failed', error);
    await ctx.reply(`❌ Failed to check breach: ${error.message}`);
  }
});

// Command: /threatfeed
bot.command('threatfeed', async (ctx) => {
  const userId = ctx.from!.id;
  
  // Toggle subscription
  const subscribed = await redis.get(`telegram:threatfeed:${userId}`);
  
  if (subscribed) {
    await redis.del(`telegram:threatfeed:${userId}`);
    await ctx.reply('❌ Unsubscribed from threat feed');
  } else {
    await redis.set(`telegram:threatfeed:${userId}`, '1');
    await ctx.reply('✅ Subscribed to threat feed!\n\nYou will receive real-time threat intelligence updates.');
  }
});

// Helper functions
async function getUserToken(userId: number): Promise<string> {
  const token = await redis.get(`telegram:token:${userId}`);
  return token || '';
}

function formatTopFindings(entities: any[], iocs: any[]): string {
  const findings: string[] = [];

  // Top IOCs
  const criticalIOCs = iocs.filter(ioc => ioc.threat_level === 'CRITICAL');
  if (criticalIOCs.length > 0) {
    findings.push(`🚨 ${criticalIOCs.length} Critical IOCs`);
  }

  // Subdomains
  const subdomains = entities.filter(e => e.type === 'DOMAIN');
  if (subdomains.length > 0) {
    findings.push(`🌐 ${subdomains.length} Subdomains`);
  }

  // IPs
  const ips = entities.filter(e => e.type === 'IP');
  if (ips.length > 0) {
    findings.push(`🖥️ ${ips.length} IP Addresses`);
  }

  return findings.join('\n') || 'No significant findings';
}

async function subscribeToScanUpdates(ctx: Context, scanId: string) {
  // Subscribe to Redis pub/sub for scan updates
  const subscriber = redis.duplicate();
  
  subscriber.subscribe('scan:updates', (err) => {
    if (err) {
      logger.error('Failed to subscribe to scan updates', err);
    }
  });

  subscriber.on('message', async (channel, message) => {
    try {
      const data = JSON.parse(message);
      
      if (data.scanId === scanId) {
        await ctx.reply(`📊 Scan Update

Status: ${data.status}
Progress: ${data.progress}%

${data.message || ''}`);

        if (data.status === 'COMPLETED') {
          subscriber.unsubscribe();
          subscriber.quit();
        }
      }
    } catch (error) {
      logger.error('Failed to process scan update', error);
    }
  });
}

// Global error handler
bot.catch((err: any, ctx: Context) => {
  logger.error('Bot error', { error: err.message, update: ctx.update });
  ctx.reply('❌ An error occurred. Please try again later.').catch(() => {});
});

// Start bot
bot.launch()
  .then(() => {
    logger.info('Telegram bot started successfully');
  })
  .catch((error) => {
    logger.error('Failed to start bot', error);
    process.exit(1);
  });

// Graceful shutdown
process.once('SIGINT', () => {
  logger.info('Received SIGINT, shutting down gracefully');
  bot.stop('SIGINT');
  redis.quit();
});

process.once('SIGTERM', () => {
  logger.info('Received SIGTERM, shutting down gracefully');
  bot.stop('SIGTERM');
  redis.quit();
});
