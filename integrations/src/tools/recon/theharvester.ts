import { BaseTool, ToolResult } from '../base-tool';

export class TheHarvesterTool extends BaseTool {
  constructor() {
    super({
      name: 'theharvester',
      command: 'theHarvester',
      timeout: 300000, // 5 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target domain
    args.push('-d', target);

    // Data sources
    if (options.sources) {
      args.push('-b', options.sources.join(','));
    } else {
      args.push('-b', 'all'); // Use all sources by default
    }

    // Limit results
    if (options.limit) {
      args.push('-l', options.limit.toString());
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const emails: string[] = [];
    const hosts: string[] = [];
    const ips: string[] = [];

    const lines = output.split('\n');
    let section = '';

    lines.forEach((line) => {
      const trimmed = line.trim();

      if (trimmed.includes('[*] Emails found:')) {
        section = 'emails';
      } else if (trimmed.includes('[*] Hosts found:')) {
        section = 'hosts';
      } else if (trimmed.includes('[*] IPs found:')) {
        section = 'ips';
      } else if (trimmed && section) {
        if (section === 'emails' && trimmed.includes('@')) {
          emails.push(trimmed);
        } else if (section === 'hosts') {
          hosts.push(trimmed);
        } else if (section === 'ips') {
          ips.push(trimmed);
        }
      }
    });

    return {
      emails: [...new Set(emails)],
      hosts: [...new Set(hosts)],
      ips: [...new Set(ips)],
      emailCount: emails.length,
      hostCount: hosts.length,
      ipCount: ips.length,
    };
  }
}
