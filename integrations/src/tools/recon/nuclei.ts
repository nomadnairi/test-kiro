import { BaseTool } from '../base-tool';

export class NucleiTool extends BaseTool {
  constructor() {
    super({
      name: 'nuclei',
      command: 'nuclei',
      timeout: 900000, // 15 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args = ['-u', target, '-json'];

    if (options.templates) {
      args.push('-t', options.templates);
    }

    if (options.severity) {
      args.push('-severity', options.severity);
    }

    if (options.tags) {
      args.push('-tags', options.tags);
    }

    if (options.silent) {
      args.push('-silent');
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const vulnerabilities: any[] = [];
    const lines = output.split('\n').filter(line => line.trim());

    for (const line of lines) {
      try {
        const data = JSON.parse(line);
        vulnerabilities.push({
          templateId: data['template-id'],
          name: data.info?.name,
          severity: data.info?.severity,
          description: data.info?.description,
          matched: data['matched-at'],
          extractedResults: data['extracted-results'],
          timestamp: data.timestamp,
        });
      } catch (e) {
        // Skip invalid JSON
      }
    }

    return {
      vulnerabilities,
      total: vulnerabilities.length,
      critical: vulnerabilities.filter(v => v.severity === 'critical').length,
      high: vulnerabilities.filter(v => v.severity === 'high').length,
      medium: vulnerabilities.filter(v => v.severity === 'medium').length,
      low: vulnerabilities.filter(v => v.severity === 'low').length,
    };
  }
}
