import { BaseTool, ToolResult } from '../base-tool';

export class AquatoneTool extends BaseTool {
  constructor() {
    super({
      name: 'aquatone',
      command: 'aquatone',
      timeout: 600000, // 10 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Aquatone reads from stdin, so we'll need to handle that differently
    // For now, we'll use the scan-timeout and other options

    // Options
    if (options.ports) {
      args.push('-ports', options.ports);
    }

    if (options.threads) {
      args.push('-threads', options.threads.toString());
    }

    if (options.scanTimeout) {
      args.push('-scan-timeout', options.scanTimeout.toString());
    }

    if (options.httpTimeout) {
      args.push('-http-timeout', options.httpTimeout.toString());
    }

    if (options.screenshotTimeout) {
      args.push('-screenshot-timeout', options.screenshotTimeout.toString());
    }

    if (options.out) {
      args.push('-out', options.out);
    }

    if (options.chromeOptions) {
      args.push('-chrome-options', options.chromeOptions);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    // Aquatone generates HTML report and screenshots
    // Parse console output for summary
    const hosts: string[] = [];
    const screenshots: string[] = [];

    output.split('\n').forEach((line) => {
      const trimmed = line.trim();

      if (trimmed.includes('http://') || trimmed.includes('https://')) {
        const match = trimmed.match(/(https?:\/\/[^\s]+)/);
        if (match) {
          hosts.push(match[1]);
        }
      }

      if (trimmed.includes('.png')) {
        screenshots.push(trimmed);
      }
    });

    return {
      hosts: [...new Set(hosts)],
      screenshots,
      hostCount: hosts.length,
      screenshotCount: screenshots.length,
    };
  }
}
