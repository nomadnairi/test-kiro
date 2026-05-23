import { BaseTool } from '../base-tool';

export class HoleheTool extends BaseTool {
  constructor() {
    super({
      name: 'holehe',
      command: 'holehe',
      timeout: 120000, // 2 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args = [target];

    if (options.modules) {
      args.push('--only-used', ...options.modules);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const accounts: any[] = [];
    const lines = output.split('\n');

    for (const line of lines) {
      // Parse format: [+] Email used on: Service
      const match = line.match(/\[\+\]\s+Email used on:\s+(.+)/);
      if (match) {
        accounts.push({
          service: match[1].trim(),
          registered: true,
        });
      }
    }

    return {
      email: accounts.length > 0 ? lines[0] : 'unknown',
      accounts,
      total: accounts.length,
    };
  }
}
