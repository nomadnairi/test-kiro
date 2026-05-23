import whois from 'whois';
import { BaseIntegration, IntegrationResult } from './base';

export class WhoisIntegration extends BaseIntegration {
  name = 'whois';

  async lookup(domain: string): Promise<IntegrationResult> {
    return new Promise((resolve) => {
      whois.lookup(domain, (err: Error | null, data: string) => {
        if (err) {
          resolve(this.handleError(err));
        } else {
          const parsed = this.parseWhois(data);
          resolve(this.createResult({ domain, raw: data, parsed }));
        }
      });
    });
  }

  private parseWhois(data: string): any {
    const lines = data.split('\n');
    const result: any = {};

    for (const line of lines) {
      const match = line.match(/^([^:]+):\s*(.+)$/);
      if (match) {
        const key = match[1].trim().toLowerCase().replace(/\s+/g, '_');
        const value = match[2].trim();
        result[key] = value;
      }
    }

    return result;
  }
}
