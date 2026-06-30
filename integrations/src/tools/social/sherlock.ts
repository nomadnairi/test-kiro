import { BaseTool } from '../base-tool';

export class SherlockTool extends BaseTool {
  constructor() {
    super({
      name: 'sherlock',
      command: 'sherlock',
      timeout: 180000, // 3 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args = [target, '--json', '--print-found'];

    if (options.timeout) {
      args.push('--timeout', options.timeout.toString());
    }

    if (options.sites) {
      args.push('--site', ...options.sites);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const profiles: any[] = [];

    try {
      const data = JSON.parse(output);

      for (const [platform, info] of Object.entries(data)) {
        if (typeof info === 'object' && info !== null) {
          const profileInfo = info as any;
          if (profileInfo.url_user) {
            profiles.push({
              platform,
              url: profileInfo.url_user,
              status: profileInfo.status?.status_code,
              found: profileInfo.status?.status_code === 200,
            });
          }
        }
      }
    } catch (e) {
      // Parse line by line if JSON parsing fails
      const lines = output.split('\n');
      for (const line of lines) {
        if (line.includes('http')) {
          const match = line.match(/\[(.*?)\].*?(https?:\/\/[^\s]+)/);
          if (match) {
            profiles.push({
              platform: match[1],
              url: match[2],
              found: true,
            });
          }
        }
      }
    }

    return {
      username: profiles[0]?.platform ? output.split('\n')[0] : 'unknown',
      profiles: profiles.filter((p) => p.found),
      total: profiles.filter((p) => p.found).length,
    };
  }
}
