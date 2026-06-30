import { createLogger } from '@cyberintel/shared';
import axios from 'axios';

const logger = createLogger({ service: 'ai-planner' });

export interface ReconPlan {
  phases: ReconPhase[];
  pivots: string[];
  priorities: string[];
}

export interface ReconPhase {
  name: string;
  tools: string[];
  parallel: boolean;
  dependencies?: string[];
}

export class AIReconPlanner {
  private aiRouterUrl: string;
  private toolOrchestratorUrl: string;

  constructor(aiRouterUrl: string, toolOrchestratorUrl: string) {
    this.aiRouterUrl = aiRouterUrl;
    this.toolOrchestratorUrl = toolOrchestratorUrl;
  }

  async createPlan(target: string, targetType: string, depth: number): Promise<ReconPlan> {
    logger.info('Creating AI recon plan', { target, targetType, depth });

    try {
      const response = await axios.post(`${this.aiRouterUrl}/api/chat`, {
        messages: [
          {
            role: 'system',
            content: 'You are an expert OSINT analyst creating reconnaissance plans.',
          },
          {
            role: 'user',
            content: this.buildPlanPrompt(target, targetType, depth),
          },
        ],
        temperature: 0.3,
        maxTokens: 2000,
      });

      const plan = this.parsePlan(response.data.content);
      logger.info('AI recon plan created', { phases: plan.phases.length });

      return plan;
    } catch (error) {
      logger.error('Failed to create AI plan', error);
      return this.getDefaultPlan(targetType);
    }
  }

  private buildPlanPrompt(target: string, targetType: string, depth: number): string {
    return `Create a reconnaissance plan for:

Target: ${target}
Type: ${targetType}
Depth: ${depth}

Available tools:
- Subdomain: amass, subfinder, assetfinder
- Port scan: naabu, masscan
- Web: httpx, whatweb, wappalyzer
- Vuln: nuclei
- Social: sherlock, holehe, maigret
- Code: trufflehog, gitleaks
- Intel: virustotal, shodan, censys

Return JSON with:
{
  "phases": [
    {
      "name": "phase_name",
      "tools": ["tool1", "tool2"],
      "parallel": true/false
    }
  ],
  "pivots": ["what to look for"],
  "priorities": ["most important findings"]
}

Return ONLY valid JSON.`;
  }

  private parsePlan(content: string): ReconPlan {
    try {
      // Extract JSON from response
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      logger.error('Failed to parse AI plan', error);
    }

    return this.getDefaultPlan('DOMAIN');
  }

  private getDefaultPlan(targetType: string): ReconPlan {
    const plans: Record<string, ReconPlan> = {
      DOMAIN: {
        phases: [
          {
            name: 'subdomain_enumeration',
            tools: ['amass', 'subfinder'],
            parallel: true,
          },
          {
            name: 'web_analysis',
            tools: ['httpx', 'whatweb'],
            parallel: true,
          },
          {
            name: 'vulnerability_scan',
            tools: ['nuclei'],
            parallel: false,
          },
        ],
        pivots: ['subdomains', 'ips', 'technologies'],
        priorities: ['vulnerabilities', 'exposed_services'],
      },
      IP: {
        phases: [
          {
            name: 'port_scan',
            tools: ['naabu'],
            parallel: false,
          },
          {
            name: 'service_detection',
            tools: ['httpx'],
            parallel: false,
          },
        ],
        pivots: ['open_ports', 'services'],
        priorities: ['exposed_services'],
      },
      USERNAME: {
        phases: [
          {
            name: 'social_media',
            tools: ['sherlock', 'holehe'],
            parallel: true,
          },
        ],
        pivots: ['profiles', 'emails'],
        priorities: ['social_profiles'],
      },
    };

    return plans[targetType] || plans.DOMAIN;
  }

  async executePlan(target: string, plan: ReconPlan): Promise<any> {
    logger.info('Executing recon plan', { target, phases: plan.phases.length });

    const results: any = {
      phases: [],
      entities: [],
      pivots: [],
    };

    for (const phase of plan.phases) {
      logger.info('Executing phase', { phase: phase.name, tools: phase.tools });

      const phaseResults = await this.executePhase(target, phase);
      results.phases.push({
        name: phase.name,
        results: phaseResults,
      });

      // Extract entities
      const entities = this.extractEntities(phaseResults);
      results.entities.push(...entities);
    }

    // Identify pivots
    results.pivots = await this.identifyPivots(results.entities, plan.pivots);

    logger.info('Recon plan execution complete', {
      entities: results.entities.length,
      pivots: results.pivots.length,
    });

    return results;
  }

  private async executePhase(target: string, phase: ReconPhase): Promise<any> {
    try {
      const endpoint = phase.parallel ? '/execute-parallel' : '/execute-sequential';

      const response = await axios.post(`${this.toolOrchestratorUrl}${endpoint}`, {
        tools: phase.tools,
        target,
      });

      return response.data;
    } catch (error) {
      logger.error('Phase execution failed', error);
      return {};
    }
  }

  private extractEntities(phaseResults: any): any[] {
    const entities: any[] = [];

    for (const [tool, result] of Object.entries(phaseResults)) {
      if (typeof result === 'object' && result !== null) {
        const data = (result as any).data || {};

        // Extract subdomains
        if (data.subdomains) {
          data.subdomains.forEach((subdomain: string) => {
            entities.push({
              type: 'DOMAIN',
              value: subdomain,
              source: tool,
            });
          });
        }

        // Extract IPs
        if (data.ips) {
          data.ips.forEach((ip: string) => {
            entities.push({
              type: 'IP',
              value: ip,
              source: tool,
            });
          });
        }

        // Extract vulnerabilities
        if (data.vulnerabilities) {
          data.vulnerabilities.forEach((vuln: any) => {
            entities.push({
              type: 'VULNERABILITY',
              value: vuln.name || vuln.templateId,
              severity: vuln.severity,
              source: tool,
            });
          });
        }
      }
    }

    return entities;
  }

  private async identifyPivots(entities: any[], pivotTypes: string[]): Promise<any[]> {
    const pivots: any[] = [];

    // Group entities by type
    const byType: Record<string, any[]> = {};
    entities.forEach((entity) => {
      if (!byType[entity.type]) {
        byType[entity.type] = [];
      }
      byType[entity.type].push(entity);
    });

    // Suggest pivots based on findings
    if (byType.DOMAIN && byType.DOMAIN.length > 5) {
      pivots.push({
        type: 'subdomain_expansion',
        reason: `Found ${byType.DOMAIN.length} subdomains`,
        targets: byType.DOMAIN.slice(0, 5).map((e) => e.value),
      });
    }

    if (byType.IP) {
      pivots.push({
        type: 'ip_investigation',
        reason: `Found ${byType.IP.length} IPs`,
        targets: byType.IP.map((e) => e.value),
      });
    }

    if (byType.VULNERABILITY) {
      const critical = byType.VULNERABILITY.filter((v) => v.severity === 'critical');
      if (critical.length > 0) {
        pivots.push({
          type: 'vulnerability_analysis',
          reason: `Found ${critical.length} critical vulnerabilities`,
          targets: critical.map((v) => v.value),
        });
      }
    }

    return pivots;
  }
}
