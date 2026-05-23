import { BaseTool, ToolResult } from '../base-tool';

export class KatanaTool extends BaseTool {
  constructor() {
    super({
      name: 'katana',
      command: 'katana',
      timeout: 300000, // 5 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push('-u', target);

    // JSON output
    args.push('-jsonl');

    // Options
    if (options.depth) {
      args.push('-d', options.depth.toString());
    }

    if (options.jsFiles) {
      args.push('-jc'); // JavaScript file crawling
    }

    if (options.formFilling) {
      args.push('-form-fill');
    }

    if (options.headless) {
      args.push('-headless');
    }

    if (options.scope) {
      args.push('-scope', options.scope);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const urls: any[] = [];

    output.split('\n').forEach(line => {
      if (line.trim()) {
        try {
          urls.push(JSON.parse(line));
        } catch (e) {
          // Skip invalid JSON lines
        }
      }
    });

    return {
      urls,
      count: urls.length,
      endpoints: urls.map(u => u.url),
    };
  }
}
