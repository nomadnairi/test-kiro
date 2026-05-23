import { BaseTool, ToolResult } from '../base-tool';

export class GauTool extends BaseTool {
  constructor() {
    super({
      name: 'gau',
      command: 'gau',
      timeout: 180000, // 3 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push(target);

    // Options
    if (options.providers) {
      args.push('--providers', options.providers.join(','));
    }

    if (options.blacklist) {
      args.push('--blacklist', options.blacklist.join(','));
    }

    if (options.threads) {
      args.push('--threads', options.threads.toString());
    }

    if (options.subs) {
      args.push('--subs');
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
