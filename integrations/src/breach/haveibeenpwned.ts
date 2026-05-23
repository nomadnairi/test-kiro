import axios from 'axios';
import { BaseIntegration, IntegrationResult } from '../base';

export class HaveIBeenPwnedIntegration extends BaseIntegration {
  name = 'haveibeenpwned';
  private baseUrl = 'https://haveibeenpwned.com/api/v3';

  async checkEmail(email: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(
        `${this.baseUrl}/breachedaccount/${encodeURIComponent(email)}`,
        {
          headers: {
            'hibp-api-key': this.config.apiKey,
            'user-agent': 'CyberIntel-Platform',
          },
          params: {
            truncateResponse: false,
          },
          timeout: this.config.timeout || 30000,
        }
      );

      const breaches = response.data.map((breach: any) => ({
        name: breach.Name,
        title: breach.Title,
        domain: breach.Domain,
        breachDate: breach.BreachDate,
        addedDate: breach.AddedDate,
        modifiedDate: breach.ModifiedDate,
        pwnCount: breach.PwnCount,
        description: breach.Description,
        dataClasses: breach.DataClasses,
        isVerified: breach.IsVerified,
        isFabricated: breach.IsFabricated,
        isSensitive: breach.IsSensitive,
        isRetired: breach.IsRetired,
        isSpamList: breach.IsSpamList,
      }));

      return this.createResult({
        email,
        breached: breaches.length > 0,
        breaches,
        totalBreaches: breaches.length,
        totalRecords: breaches.reduce((sum: number, b: any) => sum + b.pwnCount, 0),
        dataTypes: [...new Set(breaches.flatMap((b: any) => b.dataClasses))],
      });
    } catch (error: any) {
      if (error.response?.status === 404) {
        return this.createResult({
          email,
          breached: false,
          breaches: [],
          totalBreaches: 0,
        });
      }
      return this.handleError(error);
    }
  }

  async checkPassword(password: string): Promise<IntegrationResult> {
    try {
      // Use k-anonymity model
      const crypto = require('crypto');
      const hash = crypto.createHash('sha1').update(password).digest('hex').toUpperCase();
      const prefix = hash.substring(0, 5);
      const suffix = hash.substring(5);

      const response = await axios.get(
        `https://api.pwnedpasswords.com/range/${prefix}`,
        {
          headers: {
            'user-agent': 'CyberIntel-Platform',
          },
          timeout: this.config.timeout || 30000,
        }
      );

      const hashes = response.data.split('\n');
      const found = hashes.find((line: string) => line.startsWith(suffix));

      if (found) {
        const count = parseInt(found.split(':')[1]);
        return this.createResult({
          pwned: true,
          count,
          severity: count > 100000 ? 'CRITICAL' : count > 10000 ? 'HIGH' : 'MEDIUM',
        });
      }

      return this.createResult({
        pwned: false,
        count: 0,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getAllBreaches(): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/breaches`, {
        headers: {
          'hibp-api-key': this.config.apiKey,
          'user-agent': 'CyberIntel-Platform',
        },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        breaches: response.data,
        total: response.data.length,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
