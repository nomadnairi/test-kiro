import { BaseTool, ToolResult } from '../base-tool';

export class MaigretTool extends BaseTool {
  constructor() {
    super({
      name: 'maigret',
      command: 'maigret',
      timeout: 300000, // 5 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target username
    args.push(target);

    // JSON output
    args.push('--json', 'simple');

    // Options
    if (options.timeout) {
      args.push('--timeout', options.timeout.toString());
    }

    if (options.retries) {
      args.push('--retries', options.retries.toString());
    }

    if (options.tags) {
      args.push('--tags', options.tags.join(','));
    }

    if (options.allSites) {
      args.push('--all-sites');
    }

    return args;
  }

  protected parseOutput(output: string): any {
    try {
      const results = JSON.parse(output);
      
      const profiles: any[] = [];
      
      Object.keys(results).forEach(site => {
        const data = results[site];
        if (data.status && data.status.status === 'Claimed') {
          profiles.push({
            site,
            url: data.url_user,
            status: data.status.status,
            ids: data.ids || {},
          });
        }
      });

      return {
        username: target,
        profiles,
        count: profiles.length,
        sites: profiles.map(p => p.site),
      };
    } catch (e) {
      return {
        username: target,
        profiles: [],
        count: 0,
        sites: [],
      };
    }
  }
}
