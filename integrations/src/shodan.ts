import axios from 'axios';
import { BaseIntegration, IntegrationResult } from './base';

export class ShodanIntegration extends BaseIntegration {
  name = 'shodan';
  private baseUrl = 'https://api.shodan.io';

  async searchIP(ip: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/shodan/host/${ip}`, {
        params: { key: this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        ip: response.data.ip_str,
        ports: response.data.ports,
        hostnames: response.data.hostnames,
        organization: response.data.org,
        isp: response.data.isp,
        asn: response.data.asn,
        country: response.data.country_name,
        city: response.data.city,
        vulns: response.data.vulns || [],
        services: response.data.data?.map((service: any) => ({
          port: service.port,
          protocol: service.transport,
          product: service.product,
          version: service.version,
          banner: service.data,
        })),
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async search(query: string, limit = 100): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/shodan/host/search`, {
        params: {
          key: this.config.apiKey,
          query,
          limit,
        },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        total: response.data.total,
        matches: response.data.matches.map((match: any) => ({
          ip: match.ip_str,
          port: match.port,
          organization: match.org,
          hostnames: match.hostnames,
          location: {
            country: match.location?.country_name,
            city: match.location?.city,
          },
        })),
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
