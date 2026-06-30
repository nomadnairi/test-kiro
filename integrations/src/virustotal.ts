import axios from 'axios';
import { BaseIntegration, IntegrationResult } from './base';

export class VirusTotalIntegration extends BaseIntegration {
  name = 'virustotal';
  private baseUrl = 'https://www.virustotal.com/api/v3';

  async analyzeIP(ip: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/ip_addresses/${ip}`, {
        headers: { 'x-apikey': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      const data = response.data.data;
      const stats = data.attributes.last_analysis_stats;

      return this.createResult({
        ip,
        reputation: data.attributes.reputation,
        malicious: stats.malicious,
        suspicious: stats.suspicious,
        harmless: stats.harmless,
        undetected: stats.undetected,
        asn: data.attributes.asn,
        country: data.attributes.country,
        network: data.attributes.network,
        tags: data.attributes.tags || [],
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async analyzeDomain(domain: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/domains/${domain}`, {
        headers: { 'x-apikey': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      const data = response.data.data;
      const stats = data.attributes.last_analysis_stats;

      return this.createResult({
        domain,
        reputation: data.attributes.reputation,
        malicious: stats.malicious,
        suspicious: stats.suspicious,
        harmless: stats.harmless,
        undetected: stats.undetected,
        categories: data.attributes.categories,
        tags: data.attributes.tags || [],
        whois: data.attributes.whois,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async analyzeURL(url: string): Promise<IntegrationResult> {
    try {
      // Submit URL for analysis
      const submitResponse = await axios.post(
        `${this.baseUrl}/urls`,
        new URLSearchParams({ url }),
        {
          headers: { 'x-apikey': this.config.apiKey },
          timeout: this.config.timeout || 30000,
        }
      );

      const analysisId = submitResponse.data.data.id;

      // Wait a bit for analysis
      await new Promise((resolve) => setTimeout(resolve, 5000));

      // Get analysis results
      const analysisResponse = await axios.get(`${this.baseUrl}/analyses/${analysisId}`, {
        headers: { 'x-apikey': this.config.apiKey },
      });

      const stats = analysisResponse.data.data.attributes.stats;

      return this.createResult({
        url,
        malicious: stats.malicious,
        suspicious: stats.suspicious,
        harmless: stats.harmless,
        undetected: stats.undetected,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async analyzeHash(hash: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/files/${hash}`, {
        headers: { 'x-apikey': this.config.apiKey },
        timeout: this.config.timeout || 30000,
      });

      const data = response.data.data;
      const stats = data.attributes.last_analysis_stats;

      return this.createResult({
        hash,
        malicious: stats.malicious,
        suspicious: stats.suspicious,
        harmless: stats.harmless,
        undetected: stats.undetected,
        fileType: data.attributes.type_description,
        size: data.attributes.size,
        names: data.attributes.names || [],
        tags: data.attributes.tags || [],
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
