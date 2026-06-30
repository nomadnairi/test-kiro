import { BaseTool, ToolResult } from '../base-tool';

export class HttpxTool extends BaseTool {
  constructor() {
    super({
      name: 'httpx',
      command: 'httpx',
      timeout: 180000, // 3 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push('-u', target);

    // JSON output
    args.push('-json');

    // Options
    if (options.followRedirects) {
      args.push('-follow-redirects');
    }

    if (options.statusCode) {
      args.push('-status-code');
    }

    if (options.title) {
      args.push('-title');
    }

    if (options.techDetect) {
      args.push('-tech-detect');
    }

    if (options.threads) {
      args.push('-threads', options.threads.toString());
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const results: any[] = [];

    output.split('\n').forEach((line) => {
      if (line.trim()) {
        try {
          results.push(JSON.parse(line));
        } catch (e) {
          // Skip invalid JSON lines
        }
      }
    });

    return {
      hosts: results,
      count: results.length,
      alive: results.filter((r) => r.status_code >= 200 && r.status_code < 400).length,
    };
  }
}
