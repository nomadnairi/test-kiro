import { promises as dns } from 'dns';
import { BaseIntegration, IntegrationResult } from './base';

export class DNSIntegration extends BaseIntegration {
  name = 'dns';

  async resolveA(domain: string): Promise<IntegrationResult> {
    try {
      const addresses = await dns.resolve4(domain);
      return this.createResult({ domain, addresses });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async resolveAAAA(domain: string): Promise<IntegrationResult> {
    try {
      const addresses = await dns.resolve6(domain);
      return this.createResult({ domain, addresses });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async resolveMX(domain: string): Promise<IntegrationResult> {
    try {
      const records = await dns.resolveMx(domain);
      return this.createResult({ domain, records });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async resolveTXT(domain: string): Promise<IntegrationResult> {
    try {
      const records = await dns.resolveTxt(domain);
      return this.createResult({ domain, records });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async resolveNS(domain: string): Promise<IntegrationResult> {
    try {
      const nameservers = await dns.resolveNs(domain);
      return this.createResult({ domain, nameservers });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async resolveCNAME(domain: string): Promise<IntegrationResult> {
    try {
      const cnames = await dns.resolveCname(domain);
      return this.createResult({ domain, cnames });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async reverse(ip: string): Promise<IntegrationResult> {
    try {
      const hostnames = await dns.reverse(ip);
      return this.createResult({ ip, hostnames });
    } catch (error) {
      return this.handleError(error);
    }
  }

  async resolveAll(domain: string): Promise<IntegrationResult> {
    try {
      const [a, aaaa, mx, txt, ns] = await Promise.allSettled([
        this.resolveA(domain),
        this.resolveAAAA(domain),
        this.resolveMX(domain),
        this.resolveTXT(domain),
        this.resolveNS(domain),
      ]);

      return this.createResult({
        domain,
        a: a.status === 'fulfilled' ? a.value.data : null,
        aaaa: aaaa.status === 'fulfilled' ? aaaa.value.data : null,
        mx: mx.status === 'fulfilled' ? mx.value.data : null,
        txt: txt.status === 'fulfilled' ? txt.value.data : null,
        ns: ns.status === 'fulfilled' ? ns.value.data : null,
      });
    } catch (error) {
      return this.handleError(error);
    }
  }
}
