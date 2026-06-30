import { BaseTool, ToolResult } from '../base-tool';

export class DnsxTool extends BaseTool {
  constructor() {
    super({
      name: 'dnsx',
      command: 'dnsx',
      timeout: 120000, // 2 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push('-d', target);

    // JSON output
    args.push('-json');

    // Options
    if (options.recordTypes) {
      args.push('-a', '-aaaa', '-cname', '-mx', '-ns', '-txt', '-srv');
    } else {
      args.push('-a'); // Default to A records
    }

    if (options.wildcard) {
      args.push('-wildcard');
    }

    if (options.threads) {
      args.push('-t', options.threads.toString());
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const records: any[] = [];

    output.split('\n').forEach((line) => {
      if (line.trim()) {
        try {
          records.push(JSON.parse(line));
        } catch (e) {
          // Skip invalid JSON lines
        }
      }
    });

    return {
      records,
      count: records.length,
      types: [...new Set(records.map((r) => r.type))],
    };
  }
}
