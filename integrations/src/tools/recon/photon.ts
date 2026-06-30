import { BaseTool, ToolResult } from '../base-tool';

export class PhotonTool extends BaseTool {
  constructor() {
    super({
      name: 'photon',
      command: 'python3',
      timeout: 300000, // 5 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Photon script path (assuming it's in PATH or specify full path)
    args.push('-m', 'photon');

    // Target URL
    args.push('-u', target);

    // Options
    if (options.level) {
      args.push('-l', options.level.toString());
    }

    if (options.threads) {
      args.push('-t', options.threads.toString());
    }

    if (options.delay) {
      args.push('-d', options.delay.toString());
    }

    if (options.timeout) {
      args.push('--timeout', options.timeout.toString());
    }

    if (options.clone) {
      args.push('--clone');
    }

    if (options.keys) {
      args.push('--keys');
    }

    if (options.dns) {
      args.push('--dns');
    }

    if (options.ninja) {
      args.push('--ninja');
    }

    // Output directory
    if (options.output) {
      args.push('-o', options.output);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    // Photon outputs to files, so we parse the console output
    const urls: string[] = [];
    const emails: string[] = [];
    const files: string[] = [];
    const intel: string[] = [];

    output.split('\n').forEach((line) => {
      const trimmed = line.trim();

      if (trimmed.includes('http://') || trimmed.includes('https://')) {
        urls.push(trimmed);
      } else if (trimmed.includes('@') && !trimmed.includes('http')) {
        emails.push(trimmed);
      } else if (trimmed.match(/\.(pdf|doc|docx|xls|xlsx|zip|rar)$/i)) {
        files.push(trimmed);
      }
    });

    return {
      urls: [...new Set(urls)],
      emails: [...new Set(emails)],
      files: [...new Set(files)],
      urlCount: urls.length,
      emailCount: emails.length,
      fileCount: files.length,
    };
  }
}
