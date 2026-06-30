import { BaseTool } from '../base-tool';

export class TruffleHogTool extends BaseTool {
  constructor() {
    super({
      name: 'trufflehog',
      command: 'trufflehog',
      timeout: 600000, // 10 minutes
    });
  }

  protected buildArgs(target: string, options: Record<string, any>): string[] {
    const args = ['git', target, '--json'];

    if (options.since) {
      args.push('--since-commit', options.since);
    }

    if (options.branch) {
      args.push('--branch', options.branch);
    }

    if (options.maxDepth) {
      args.push('--max-depth', options.maxDepth.toString());
    }

    return args;
  }

  protected parseOutput(output: string): any {
    const secrets: any[] = [];
    const lines = output.split('\n').filter((line) => line.trim());

    for (const line of lines) {
      try {
        const data = JSON.parse(line);
        secrets.push({
          detector: data.DetectorName,
          raw: data.Raw,
          redacted: data.Redacted,
          file: data.SourceMetadata?.Data?.Git?.file,
          commit: data.SourceMetadata?.Data?.Git?.commit,
          email: data.SourceMetadata?.Data?.Git?.email,
          timestamp: data.SourceMetadata?.Data?.Git?.timestamp,
          verified: data.Verified,
        });
      } catch (e) {
        // Skip invalid JSON
      }
    }

    return {
      secrets,
      total: secrets.length,
      verified: secrets.filter((s) => s.verified).length,
      types: [...new Set(secrets.map((s) => s.detector))],
    };
  }
}
