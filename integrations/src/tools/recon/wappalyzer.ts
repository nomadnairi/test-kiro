import { BaseTool, ToolResult } from '../base-tool';

export class WappalyzerTool extends BaseTool {
  constructor() {
    super({
      name: 'wappalyzer',
      command: 'wappalyzer',
      timeout: 120000, // 2 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Target
    args.push(target);

    // Options
    if (options.recursive) {
      args.push('--recursive');
    }

    if (options.maxDepth) {
      args.push('--max-depth', options.maxDepth.toString());
    }

    if (options.maxUrls) {
      args.push('--max-urls', options.maxUrls.toString());
    }

    if (options.delay) {
      args.push('--delay', options.delay.toString());
    }

    return args;
  }

  protected parseOutput(output: string): any {
    try {
      const results = JSON.parse(output);
      
      const technologies: any[] = [];
      const categories: string[] = [];

      if (results.technologies) {
        results.technologies.forEach((tech: any) => {
          technologies.push({
            name: tech.name,
            version: tech.version,
            categories: tech.categories,
            confidence: tech.confidence,
          });
          
          if (tech.categories) {
            categories.push(...tech.categories.map((c: any) => c.name));
          }
        });
      }

      return {
        url: results.url,
        technologies,
        categories: [...new Set(categories)],
        count: technologies.length,
      };
    } catch (e) {
      return {
        technologies: [],
        categories: [],
        count: 0,
      };
    }
  }
}
