import { BaseTool, ToolResult } from '../base-tool';

export class SocialscanTool extends BaseTool {
  constructor() {
    super({
      name: 'socialscan',
      command: 'socialscan',
      timeout: 180000, // 3 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target (username or email)
    args.push(target);

    // JSON output
    args.push('--json');

    // Options
    if (options.platforms) {
      args.push('--platforms', options.platforms.join(','));
    }

    if (options.timeout) {
      args.push('--timeout', options.timeout.toString());
    }

    if (options.showUnavailable) {
      args.push('--show-unavailable');
    }

    return args;
  }

  protected parseOutput(output: string): any {
    try {
      const results = JSON.parse(output);

      const available: any[] = [];
      const unavailable: any[] = [];

      Object.keys(results).forEach((platform) => {
        const status = results[platform];
        if (status.available) {
          available.push({ platform, ...status });
        } else {
          unavailable.push({ platform, ...status });
        }
      });

      return {
        target,
        available,
        unavailable,
        availableCount: available.length,
        unavailableCount: unavailable.length,
      };
    } catch (e) {
      return {
        target,
        available: [],
        unavailable: [],
        availableCount: 0,
        unavailableCount: 0,
      };
    }
  }
}
