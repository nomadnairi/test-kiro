import { BaseTool, ToolResult } from '../base-tool';

export class AssetfinderTool extends BaseTool {
  constructor() {
    super({
      name: 'assetfinder',
      command: 'assetfinder',
      timeout: 120000, // 2 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Assetfinder only takes domain as argument
    args.push(target);

    // Options
    if (options.subsOnly) {
      args.push('--subs-only');
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const subdomains = output
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);

    return {
      subdomains,
      count: subdomains.length,
    };
  }
}
