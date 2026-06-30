import { describe, test, beforeEach, afterEach } from 'node:test';
import * as assert from 'node:assert';
import { DNSIntegration } from '../src/dns';
import * as sinon from 'sinon';

describe('DNSIntegration', () => {
  let dnsIntegration: DNSIntegration;
  let sandbox: sinon.SinonSandbox;

  beforeEach(() => {
    dnsIntegration = new DNSIntegration({});
    sandbox = sinon.createSandbox();
  });

  afterEach(() => {
    sandbox.restore();
  });

  test('resolveAll partial failures are handled correctly', async () => {
    const domain = 'example.com';

    // Stub the individual resolve methods to simulate success for most and rejection for one.
    sandbox.stub(dnsIntegration, 'resolveA').resolves({ success: true, data: { domain, addresses: ['1.2.3.4'] }, source: 'dns', timestamp: new Date() });

    // Simulating rejection allows `allSettled` to have status === 'rejected'
    sandbox.stub(dnsIntegration, 'resolveAAAA').rejects(new Error('Internal failure'));

    sandbox.stub(dnsIntegration, 'resolveMX').resolves({ success: true, data: { domain, records: [{ exchange: 'mail.example.com', priority: 10 }] }, source: 'dns', timestamp: new Date() });
    sandbox.stub(dnsIntegration, 'resolveTXT').resolves({ success: true, data: { domain, records: [['v=spf1 -all']] }, source: 'dns', timestamp: new Date() });
    sandbox.stub(dnsIntegration, 'resolveNS').resolves({ success: true, data: { domain, nameservers: ['ns1.example.com'] }, source: 'dns', timestamp: new Date() });

    const result = await dnsIntegration.resolveAll(domain);

    assert.strictEqual(result.success, true);
    assert.deepStrictEqual(result.data, {
      domain,
      a: { domain, addresses: ['1.2.3.4'] },
      aaaa: null, // this verifies the edge case where the rejected promise's result is mapped to null
      mx: { domain, records: [{ exchange: 'mail.example.com', priority: 10 }] },
      txt: { domain, records: [['v=spf1 -all']] },
      ns: { domain, nameservers: ['ns1.example.com'] }
    });
  });
});
