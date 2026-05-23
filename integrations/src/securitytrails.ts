import axios from 'axios';
import { BaseIntegration, IntegrationResult } from './base';

export class SecurityTrailsIntegration extends BaseIntegration {
  name = 'securitytrails';
  private baseUrl = 'https://api.securitytrails.com/v1';

  async getDomainDetails(domain: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/domain/${domain}`, {
        headers: { 'APIKEY': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        domain,
        currentDNS: response.data.current_dns,
        alexa_rank: response.data.alexa_rank,
        endpoint: response.data.endpoint,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getSubdomains(domain: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/domain/${domain}/subdomains`, {
        headers: { 'APIKEY': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        domain,
        subdomains: response.data.subdomains,
        count: response.data.subdomain_count,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getDNSHistory(domain: string, type: string = 'a'): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/history/${domain}/dns/${type}`, {
        headers: { 'APIKEY': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        domain,
        type,
        records: response.data.records,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getWhoisHistory(domain: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/history/${domain}/whois`, {
        headers: { 'APIKEY': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        domain,
        history: response.data.result,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
