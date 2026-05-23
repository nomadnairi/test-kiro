import axios from 'axios';
import { BaseIntegration, IntegrationResult } from '../base';

export class DehashedIntegration extends BaseIntegration {
  name = 'dehashed';
  private baseUrl = 'https://api.dehashed.com/search';

  async searchEmail(email: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          query: `email:${email}`,
        },
        auth: {
          username: this.config.apiKey || '',
          password: this.config.apiSecret || '',
        },
        timeout: this.config.timeout || 30000,
      });

      const entries = response.data.entries || [];

      return this.createResult({
        email,
        found: entries.length > 0,
        entries: entries.map((entry: any) => ({
          id: entry.id,
          email: entry.email,
          username: entry.username,
          password: entry.password ? '[REDACTED]' : null,
          hashedPassword: entry.hashed_password,
          name: entry.name,
          vin: entry.vin,
          address: entry.address,
          phone: entry.phone,
          database: entry.database_name,
        })),
        total: entries.length,
        databases: [...new Set(entries.map((e: any) => e.database_name))],
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async searchUsername(username: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          query: `username:${username}`,
        },
        auth: {
          username: this.config.apiKey || '',
          password: this.config.apiSecret || '',
        },
        timeout: this.config.timeout || 30000,
      });

      const entries = response.data.entries || [];

      return this.createResult({
        username,
        found: entries.length > 0,
        entries: entries.map((entry: any) => ({
          email: entry.email,
          username: entry.username,
          database: entry.database_name,
        })),
        total: entries.length,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async searchDomain(domain: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          query: `email:@${domain}`,
        },
        auth: {
          username: this.config.apiKey || '',
          password: this.config.apiSecret || '',
        },
        timeout: this.config.timeout || 30000,
      });

      const entries = response.data.entries || [];

      return this.createResult({
        domain,
        found: entries.length > 0,
        exposedEmails: [...new Set(entries.map((e: any) => e.email))],
        total: entries.length,
        databases: [...new Set(entries.map((e: any) => e.database_name))],
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
