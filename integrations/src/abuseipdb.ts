import axios from 'axios';
import { BaseIntegration, IntegrationResult } from './base';

export class AbuseIPDBIntegration extends BaseIntegration {
  name = 'abuseipdb';
  private baseUrl = 'https://api.abuseipdb.com/api/v2';

  async checkIP(ip: string): Promise<IntegrationResult> {
    try {
      const response = await axios.get(`${this.baseUrl}/check`, {
        params: {
          ipAddress: ip,
          maxAgeInDays: 90,
          verbose: true,
        },
        headers: {
          'Key': this.config.apiKey,
          'Accept': 'application/json',
        },
        timeout: this.config.timeout || 30000,
      });

      const data = response.data.data;

      return this.createResult({
        ip: data.ipAddress,
        abuseConfidenceScore: data.abuseConfidenceScore,
        usageType: data.usageType,
        isp: data.isp,
        domain: data.domain,
        country: data.countryName,
        isWhitelisted: data.isWhitelisted,
        totalReports: data.totalReports,
        numDistinctUsers: data.numDistinctUsers,
        lastReportedAt: data.lastReportedAt,
        reports: data.reports?.map((report: any) => ({
          reportedAt: report.reportedAt,
          comment: report.comment,
          categories: report.categories,
        })),
      });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async reportIP(ip: string, categories: number[], comment: string): Promise<IntegrationResult> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/report`,
        {
          ip,
          categories: categories.join(','),
          comment,
        },
        {
          headers: {
            'Key': this.config.apiKey,
            'Accept': 'application/json',
          },
          timeout: this.config.timeout || 30000,
        }
      );

      return this.createResult({
        success: true,
        abuseConfidenceScore: response.data.data.abuseConfidenceScore,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
