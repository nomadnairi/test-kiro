import { BaseTool, ToolResult } from '../base-tool';

export class AmassTool extends BaseTool {
  constructor() {
    super({
      name: 'amass',
      command: 'amass',
      timeout: 600000, // 10 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args = ['enum', '-d', target];

    if (options.passive) {
      args.push('-passive');
    }

    if (options.bruteforce) {
      args.push('-brute');
    }

    if (options.timeout) {
      args.push('-timeout', options.timeout.toString());
    }

    args.push('-json', '-');

    return args;
  }

  protected parseOutput(output: string): any {
    const results = {
      subdomains: [] as string[],
      ips: [] as string[],
      asns: [] as string[],
    };

    const lines = output.split('\n').filter((line) => line.trim());

    for (const line of lines) {
      try {
        const data = JSON.parse(line);

        if (data.name) {
          results.subdomains.push(data.name);
        }

        if (data.addresses) {
          data.addresses.forEach((addr: any) => {
            if (addr.ip) results.ips.push(addr.ip);
            if (addr.asn) results.asns.push(addr.asn.toString());
          });
        }
      } catch (e) {
        // Skip invalid JSON lines
      }
    }

    return {
      subdomains: [...new Set(results.subdomains)],
      ips: [...new Set(results.ips)],
      asns: [...new Set(results.asns)],
      total: results.subdomains.length,
    };
  }
}
