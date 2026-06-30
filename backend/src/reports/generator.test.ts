import test from 'node:test';
import assert from 'node:assert';
import { ReportGenerator } from './generator';

test('ReportGenerator', async (t) => {
  await t.test('calculateRiskScore should not exceed 100', () => {
    const generator = new ReportGenerator('http://dummy');

    const data = {
      iocs: Array(20).fill({ threat_level: 'CRITICAL' }), // 20 * 20 = 400
      entities: Array(20).fill({ type: 'VULNERABILITY', severity: 'critical' }) // 20 * 15 = 300
    };

    const score = (generator as any).calculateRiskScore(data);
    assert.strictEqual(score, 100);
  });
});
