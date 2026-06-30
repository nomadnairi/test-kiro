import axios from 'axios';
import { BaseIntegration, IntegrationResult } from './base';

export class URLScanIntegration extends BaseIntegration {
  name = 'urlscan';
  private baseUrl = 'https://urlscan.io/api/v1';

  async scanURL(
    url: string,
    visibility: 'public' | 'unlisted' | 'private' = 'unlisted'
  ): Promise<IntegrationResult> {
    try {
      // Submit scan
      const submitResponse = await axios.post(
        `${this.baseUrl}/scan/`,
        { url, visibility },
        {
          headers: {
            'API-Key': this.config.apiKey,
            'Content-Type': 'application/json',
          },
          timeout: this.config.timeout || 30000,
        }
      );

      const uuid = submitResponse.data.uuid;

      // Wait for scan to complete
      await new Promise((resolve) => setTimeout(resolve, 10000));

      // Get results
      const resultResponse = await axios.get(`${this.baseUrl}/result/${uuid}/`, {
        timeout: this.config.timeout || 30000,
      });

      const data = resultResponse.data;

      return this.createResult({
        url,
        uuid,
        screenshot: data.task.screenshotURL,
        verdicts: data.verdicts,
        page: {
          domain: data.page.domain,
          ip: data.page.ip,
          country: data.page.country,
          server: data.page.server,
          asn: data.page.asn,
          asnname: data.page.asnname,
        },
        stats: data.stats,
        lists: data.lists,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async searchDomain(domain: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/search/`, {
        params: {
          q: `domain:${domain}`,
          size: 100,
        },
        timeout: this.config.timeout || 30000,
      });

      return this.createResult({
        domain,
        total: response.data.total,
        results: response.data.results.map((result: any) => ({
          url: result.page.url,
          domain: result.page.domain,
          ip: result.page.ip,
          country: result.page.country,
          screenshot: result.screenshot,
          time: result.task.time,
        })),
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
