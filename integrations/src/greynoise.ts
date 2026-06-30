import axios from 'axios';
import { BaseIntegration, IntegrationResult } from './base';

export class GreyNoiseIntegration extends BaseIntegration {
  name = 'greynoise';
  private baseUrl = 'https://api.greynoise.io/v3';

  async lookupIP(ip: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/community/${ip}`, {
        headers: { key: this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        ip: response.data.ip,
        noise: response.data.noise,
        riot: response.data.riot,
        classification: response.data.classification,
        name: response.data.name,
        link: response.data.link,
        lastSeen: response.data.last_seen,
        message: response.data.message,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async contextIP(ip: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/noise/context/${ip}`, {
        headers: { key: this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      const data = response.data;

      return this.createResult({
        ip: data.ip,
        seen: data.seen,
        classification: data.classification,
        firstSeen: data.first_seen,
        lastSeen: data.last_seen,
        actor: data.actor,
        tags: data.tags,
        metadata: data.metadata,
        rawData: data.raw_data,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
