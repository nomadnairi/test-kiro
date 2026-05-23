import { createLogger } from '@cyberintel/shared';
import axios from 'axios';
import PDFDocument from 'pdfkit';
import { createWriteStream } from 'fs';

const logger = createLogger({ service: 'report-generator' });

export interface ReportConfig {
  scanId: string;
  type: 'executive' | 'technical' | 'full';
  format: 'pdf' | 'html' | 'json';
  includeGraphs: boolean;
  includeTimeline: boolean;
}

export class ReportGenerator {
  private aiRouterUrl: string;

  constructor(aiRouterUrl: string) {
    this.aiRouterUrl = aiRouterUrl;
  }

  async generateReport(config: ReportConfig, data: any): Promise<Buffer | string> {
    logger.info('Generating report', { scanId: config.scanId, type: config.type });

    switch (config.format) {
      case 'pdf':
        return this.generatePDF(config, data);
      case 'html':
        return this.generateHTML(config, data);
      case 'json':
        return JSON.stringify(data, null, 2);
      default:
        throw new Error(`Unsupported format: ${config.format}`);
    }
  }

  private async generatePDF(config: ReportConfig, data: any): Promise<Buffer> {
    return new Promise(async (resolve, reject) => {
      const doc = new PDFDocument({ size: 'A4', margin: 50 });
      const chunks: Buffer[] = [];

      doc.on('data', (chunk) => chunks.push(chunk));
      doc.on('end', () => resolve(Buffer.concat(chunks)));
      doc.on('error', reject);

      // Title page
      doc.fontSize(24).text('CyberIntel Intelligence Report', { align: 'center' });
      doc.moveDown();
      doc.fontSize(14).text(`Scan ID: ${config.scanId}`, { align: 'center' });
      doc.fontSize(12).text(`Generated: ${new Date().toLocaleString()}`, { align: 'center' });
      doc.moveDown(2);

      // Executive Summary
      if (config.type === 'executive' || config.type === 'full') {
        doc.addPage();
        doc.fontSize(18).text('Executive Summary', { underline: true });
        doc.moveDown();
        
        const summary = await this.generateExecutiveSummary(data);
        doc.fontSize(11).text(summary);
        doc.moveDown();
      }

      // Technical Findings
      if (config.type === 'technical' || config.type === 'full') {
        doc.addPage();
        doc.fontSize(18).text('Technical Findings', { underline: true });
        doc.moveDown();

        // Entities
        doc.fontSize(14).text('Discovered Entities', { underline: true });
        doc.moveDown(0.5);
        doc.fontSize(11).text(`Total: ${data.entities?.length || 0}`);
        doc.moveDown();

        // IOCs
        doc.fontSize(14).text('Indicators of Compromise', { underline: true });
        doc.moveDown(0.5);
        doc.fontSize(11).text(`Total: ${data.iocs?.length || 0}`);
        
        const criticalIOCs = data.iocs?.filter((ioc: any) => ioc.threat_level === 'CRITICAL') || [];
        if (criticalIOCs.length > 0) {
          doc.moveDown();
          doc.fontSize(12).text(`Critical IOCs: ${criticalIOCs.length}`, { color: 'red' });
        }
        doc.moveDown();

        // Vulnerabilities
        const vulns = data.entities?.filter((e: any) => e.type === 'VULNERABILITY') || [];
        if (vulns.length > 0) {
          doc.fontSize(14).text('Vulnerabilities', { underline: true });
          doc.moveDown(0.5);
          doc.fontSize(11).text(`Total: ${vulns.length}`);
          doc.moveDown();
        }
      }

      // Attack Surface
      doc.addPage();
      doc.fontSize(18).text('Attack Surface', { underline: true });
      doc.moveDown();
      
      const attackSurface = this.calculateAttackSurface(data);
      doc.fontSize(11).text(`Subdomains: ${attackSurface.subdomains}`);
      doc.text(`IP Addresses: ${attackSurface.ips}`);
      doc.text(`Exposed Services: ${attackSurface.services}`);
      doc.text(`Vulnerabilities: ${attackSurface.vulnerabilities}`);
      doc.moveDown();

      // Risk Assessment
      doc.addPage();
      doc.fontSize(18).text('Risk Assessment', { underline: true });
      doc.moveDown();
      
      const riskScore = this.calculateRiskScore(data);
      doc.fontSize(14).text(`Overall Risk Score: ${riskScore}/100`);
      doc.moveDown();

      const riskAnalysis = await this.generateRiskAnalysis(data, riskScore);
      doc.fontSize(11).text(riskAnalysis);
      doc.moveDown();

      // Recommendations
      doc.addPage();
      doc.fontSize(18).text('Recommendations', { underline: true });
      doc.moveDown();
      
      const recommendations = await this.generateRecommendations(data);
      doc.fontSize(11).text(recommendations);

      doc.end();
    });
  }

  private async generateHTML(config: ReportConfig, data: any): Promise<string> {
    const summary = await this.generateExecutiveSummary(data);
    const attackSurface = this.calculateAttackSurface(data);
    const riskScore = this.calculateRiskScore(data);
    const riskAnalysis = await this.generateRiskAnalysis(data, riskScore);
    const recommendations = await this.generateRecommendations(data);

    return `
<!DOCTYPE html>
<html>
<head>
  <title>CyberIntel Report - ${config.scanId}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      background: #0a0e27;
      color: #e0e0e0;
    }
    h1 { color: #00f0ff; border-bottom: 2px solid #00f0ff; padding-bottom: 10px; }
    h2 { color: #00f0ff; margin-top: 30px; }
    .metric { background: #151932; padding: 15px; margin: 10px 0; border-left: 4px solid #00f0ff; }
    .critical { color: #ff0055; font-weight: bold; }
    .high { color: #ffaa00; font-weight: bold; }
    .risk-score { font-size: 48px; color: ${riskScore > 70 ? '#ff0055' : riskScore > 40 ? '#ffaa00' : '#00ff88'}; }
  </style>
</head>
<body>
  <h1>CyberIntel Intelligence Report</h1>
  <p><strong>Scan ID:</strong> ${config.scanId}</p>
  <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
  <p><strong>Target:</strong> ${data.scan?.target}</p>

  <h2>Executive Summary</h2>
  <div class="metric">${summary.replace(/\n/g, '<br>')}</div>

  <h2>Attack Surface</h2>
  <div class="metric">
    <p><strong>Subdomains:</strong> ${attackSurface.subdomains}</p>
    <p><strong>IP Addresses:</strong> ${attackSurface.ips}</p>
    <p><strong>Exposed Services:</strong> ${attackSurface.services}</p>
    <p><strong>Vulnerabilities:</strong> ${attackSurface.vulnerabilities}</p>
  </div>

  <h2>Risk Assessment</h2>
  <div class="metric">
    <p>Overall Risk Score: <span class="risk-score">${riskScore}/100</span></p>
    <p>${riskAnalysis.replace(/\n/g, '<br>')}</p>
  </div>

  <h2>Indicators of Compromise</h2>
  <div class="metric">
    <p><strong>Total IOCs:</strong> ${data.iocs?.length || 0}</p>
    <p class="critical">Critical: ${data.iocs?.filter((i: any) => i.threat_level === 'CRITICAL').length || 0}</p>
    <p class="high">High: ${data.iocs?.filter((i: any) => i.threat_level === 'HIGH').length || 0}</p>
  </div>

  <h2>Recommendations</h2>
  <div class="metric">${recommendations.replace(/\n/g, '<br>')}</div>
</body>
</html>
    `;
  }

  private async generateExecutiveSummary(data: any): Promise<string> {
    try {
      const response = await axios.post(`${this.aiRouterUrl}/api/chat`, {
        messages: [
          {
            role: 'system',
            content: 'You are a cybersecurity analyst writing executive summaries.',
          },
          {
            role: 'user',
            content: `Generate an executive summary for this scan:

Target: ${data.scan?.target}
Entities: ${data.entities?.length || 0}
IOCs: ${data.iocs?.length || 0}
Critical IOCs: ${data.iocs?.filter((i: any) => i.threat_level === 'CRITICAL').length || 0}

Keep it concise (3-4 paragraphs), non-technical, and focus on business impact.`,
          },
        ],
        temperature: 0.7,
        maxTokens: 500,
      });

      return response.data.content;
    } catch (error) {
      logger.error('Failed to generate executive summary', error);
      return 'Executive summary generation failed.';
    }
  }

  private async generateRiskAnalysis(data: any, riskScore: number): Promise<string> {
    try {
      const response = await axios.post(`${this.aiRouterUrl}/api/chat`, {
        messages: [
          {
            role: 'system',
            content: 'You are a cybersecurity risk analyst.',
          },
          {
            role: 'user',
            content: `Analyze the risk for this scan:

Risk Score: ${riskScore}/100
IOCs: ${data.iocs?.length || 0}
Vulnerabilities: ${data.entities?.filter((e: any) => e.type === 'VULNERABILITY').length || 0}

Provide a brief risk analysis (2-3 paragraphs).`,
          },
        ],
        temperature: 0.7,
        maxTokens: 400,
      });

      return response.data.content;
    } catch (error) {
      logger.error('Failed to generate risk analysis', error);
      return 'Risk analysis generation failed.';
    }
  }

  private async generateRecommendations(data: any): Promise<string> {
    try {
      const response = await axios.post(`${this.aiRouterUrl}/api/chat`, {
        messages: [
          {
            role: 'system',
            content: 'You are a cybersecurity consultant providing actionable recommendations.',
          },
          {
            role: 'user',
            content: `Provide security recommendations based on:

Entities: ${data.entities?.length || 0}
IOCs: ${data.iocs?.length || 0}
Vulnerabilities: ${data.entities?.filter((e: any) => e.type === 'VULNERABILITY').length || 0}

Provide 5-7 prioritized, actionable recommendations.`,
          },
        ],
        temperature: 0.7,
        maxTokens: 600,
      });

      return response.data.content;
    } catch (error) {
      logger.error('Failed to generate recommendations', error);
      return 'Recommendations generation failed.';
    }
  }

  private calculateAttackSurface(data: any): any {
    const entities = data.entities || [];
    
    return {
      subdomains: entities.filter((e: any) => e.type === 'DOMAIN').length,
      ips: entities.filter((e: any) => e.type === 'IP').length,
      services: entities.filter((e: any) => e.type === 'SERVICE').length,
      vulnerabilities: entities.filter((e: any) => e.type === 'VULNERABILITY').length,
    };
  }

  private calculateRiskScore(data: any): number {
    let score = 0;

    const iocs = data.iocs || [];
    const entities = data.entities || [];

    // IOC scoring
    score += iocs.filter((i: any) => i.threat_level === 'CRITICAL').length * 20;
    score += iocs.filter((i: any) => i.threat_level === 'HIGH').length * 10;
    score += iocs.filter((i: any) => i.threat_level === 'MEDIUM').length * 5;

    // Vulnerability scoring
    const vulns = entities.filter((e: any) => e.type === 'VULNERABILITY');
    score += vulns.filter((v: any) => v.severity === 'critical').length * 15;
    score += vulns.filter((v: any) => v.severity === 'high').length * 8;

    return Math.min(score, 100);
  }
}
