import { BaseTool, ToolResult } from '../base-tool';

export class WaybackurlsTool extends BaseTool {
  constructor() {
    super({
      name: 'waybackurls',
      command: 'waybackurls',
      timeout: 180000, // 3 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push(target);

    // Options
    if (options.dates) {
      args.push('-dates');
    }

    if (options.noSubs) {
      args.push('-no-subs');
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const urls = output
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);

    return {
      urls,
      count: urls.length,
      unique: [...new Set(urls)].length,
    };
  }
}
