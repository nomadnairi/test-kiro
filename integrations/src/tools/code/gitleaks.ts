import { BaseTool, ToolResult } from '../base-tool';

export class GitleaksTool extends BaseTool {
  constructor() {
    super({
      name: 'gitleaks',
      command: 'gitleaks',
      timeout: 300000, // 5 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args: string[] = [];

    // Command
    args.push('detect');

    // Source (repo path or URL)
    if (options.source) {
      args.push('--source', options.source);
    } else {
      args.push('--source', target);
    }

    // Report format
    args.push('--report-format', 'json');
    args.push('--report-path', '/dev/stdout');

    // Options
    if (options.verbose) {
      args.push('--verbose');
    }

    if (options.noGit) {
      args.push('--no-git');
    }

    if (options.config) {
      args.push('--config', options.config);
    }

    return args;
  }

  protected parseOutput(output: string): any {
    try {
      const results = JSON.parse(output);
      
      const secrets: any[] = [];
      
      if (Array.isArray(results)) {
        results.forEach((finding: any) => {
          secrets.push({
            description: finding.Description,
            file: finding.File,
            line: finding.StartLine,
            commit: finding.Commit,
            author: finding.Author,
            email: finding.Email,
            date: finding.Date,
            ruleId: finding.RuleID,
            secret: finding.Secret ? '***REDACTED***' : undefined,
          });
        });
      }

      return {
        secrets,
        count: secrets.length,
        files: [...new Set(secrets.map(s => s.file))],
        ruleIds: [...new Set(secrets.map(s => s.ruleId))],
      };
    } catch (e) {
      return {
        secrets: [],
        count: 0,
        files: [],
        ruleIds: [],
      };
    }
  }
}
