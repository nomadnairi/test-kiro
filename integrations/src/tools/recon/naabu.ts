import { BaseTool, ToolResult } from '../base-tool';

export class NaabuTool extends BaseTool {
  constructor() {
    super({
      name: 'naabu',
      command: 'naabu',
      timeout: 300000, // 5 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push('-host', target);

    // JSON output
    args.push('-json');

    // Options
    if (options.ports) {
      args.push('-p', options.ports);
    } else {
      args.push('-top-ports', '1000'); // Default to top 1000 ports
    }

    if (options.rate) {
      args.push('-rate', options.rate.toString());
    }

    if (options.threads) {
      args.push('-c', options.threads.toString());
    }

    if (options.excludePorts) {
      args.push('-exclude-ports', options.excludePorts);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const ports: any[] = [];

    output.split('\n').forEach((line) => {
      if (line.trim()) {
        try {
          const data = JSON.parse(line);
          ports.push(data);
        } catch (e) {
          // Skip invalid JSON lines
        }
      }
    });

    return {
      ports,
      count: ports.length,
      open: ports.filter((p) => p.status === 'open').length,
    };
  }
}
