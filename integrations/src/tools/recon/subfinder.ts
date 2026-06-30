import { BaseTool } from '../base-tool';

export class SubfinderTool extends BaseTool {
  constructor() {
    super({
      name: 'subfinder',
      command: 'subfinder',
      timeout: 300000, // 5 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args = ['-d', target, '-json', '-silent'];

    if (options.sources) {
      args.push('-sources', options.sources.join(','));
    }

    if (options.recursive) {
      args.push('-recursive');
    }

    if (options.all) {
      args.push('-all');
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const subdomains: string[] = [];
    const lines = output.split('\n').filter((line) => line.trim());

    for (const line of lines) {
      try {
        const data = JSON.parse(line);
        if (data.host) {
          subdomains.push(data.host);
        }
      } catch (e) {
        // Try plain text format
        if (line.trim()) {
          subdomains.push(line.trim());
        }
      }
    }

    return {
      subdomains: [...new Set(subdomains)],
      total: subdomains.length,
    };
  }
}
