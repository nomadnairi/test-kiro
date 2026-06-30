import { BaseTool, ToolResult } from '../base-tool';

export class WhatWebTool extends BaseTool {
  constructor() {
    super({
      name: 'whatweb',
      command: 'whatweb',
      timeout: 120000, // 2 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push(target);

    // JSON output
    args.push('--log-json=-');

    // Aggression level
    if (options.aggression) {
      args.push('-a', options.aggression.toString());
    } else {
      args.push('-a', '3'); // Default aggression level
    }

    // Options
    if (options.followRedirect) {
      args.push('--follow-redirect=always');
    }

    if (options.userAgent) {
      args.push('--user-agent', options.userAgent);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    try {
      const results = JSON.parse(output);

      const technologies: string[] = [];
      const plugins: any[] = [];

      if (Array.isArray(results)) {
        results.forEach((result: any) => {
          if (result.plugins) {
            Object.keys(result.plugins).forEach((plugin) => {
              technologies.push(plugin);
              plugins.push({
                name: plugin,
                data: result.plugins[plugin],
              });
            });
          }
        });
      }

      return {
        technologies: [...new Set(technologies)],
        plugins,
        count: technologies.length,
      };
    } catch (e) {
      return {
        technologies: [],
        plugins: [],
        count: 0,
      };
    }
  }
}
