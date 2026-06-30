import { BaseTool, ToolResult } from '../base-tool';

export class MasscanTool extends BaseTool {
  constructor() {
    super({
      name: 'masscan',
      command: 'masscan',
      timeout: 600000, // 10 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push(target);

    // Ports
    if (options.ports) {
      args.push('-p', options.ports);
    } else {
      args.push('-p', '1-1000'); // Default to first 1000 ports
    }

    // Rate
    if (options.rate) {
      args.push('--rate', options.rate.toString());
    } else {
      args.push('--rate', '1000'); // Default rate
    }

    // Output format
    args.push('-oJ', '-'); // JSON output to stdout

    // Options
    if (options.banners) {
      args.push('--banners');
    }

    if (options.excludeFile) {
      args.push('--excludefile', options.excludeFile);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    try {
      // Masscan outputs multiple JSON objects, one per line
      const ports: any[] = [];

      output.split('\n').forEach((line) => {
        if (line.trim() && line.includes('"ip"')) {
          try {
            const data = JSON.parse(line);
            if (data.ports) {
              data.ports.forEach((port: any) => {
                ports.push({
                  ip: data.ip,
                  port: port.port,
                  protocol: port.proto,
                  status: port.status,
                  reason: port.reason,
                  ttl: port.ttl,
                });
              });
            }
          } catch (e) {
            // Skip invalid JSON
          }
        }
      });

      return {
        ports,
        count: ports.length,
        ips: [...new Set(ports.map((p) => p.ip))],
        openPorts: [...new Set(ports.map((p) => p.port))],
      };
    } catch (e) {
      return {
        ports: [],
        count: 0,
        ips: [],
        openPorts: [],
      };
    }
  }
}
