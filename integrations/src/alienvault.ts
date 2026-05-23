import axios from 'axios';
import { BaseIntegration, IntegrationResult } from './base';

export class AlienVaultIntegration extends BaseIntegration {
  name = 'alienvault';
  private baseUrl = 'https://otx.alienvault.com/api/v1';

  async getIPReputation(ip: string): Promise<IntegrationResult> {
    try {
      const [general, reputation, malware] = await Promise.all([
        axios.get(`${this.baseUrl}/indicators/IPv4/${ip}/general`, {
          headers: { 'X-OTX-API-KEY': this.config.apiKey },
        }),
        axios.get(`${this.baseUrl}/indicators/IPv4/${ip}/reputation`, {
          headers: { 'X-OTX-API-KEY': this.config.apiKey },
        }),
        axios.get(`${this.baseUrl}/indicators/IPv4/${ip}/malware`, {
          headers: { 'X-OTX-API-KEY': this.config.apiKey },
        }),
      ]);

      return this.createResult({
        ip,
        pulseCount: general.data.pulse_info?.count || 0,
        reputation: reputation.data.reputation,
        malware: malware.data.data,
        country: general.data.country_name,
        asn: general.data.asn,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getDomainReputation(domain: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/indicators/domain/${domain}/general`, {
        headers: { 'X-OTX-API-KEY': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        domain,
        pulseCount: response.data.pulse_info?.count || 0,
        alexa: response.data.alexa,
        whois: response.data.whois,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
