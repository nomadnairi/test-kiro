import { test, describe } from 'node:test';
import assert from 'node:assert';
import { ReportGenerator } from './generator';

describe('ReportGenerator', () => {
  describe('calculateAttackSurface', () => {
    test('handles empty data', () => {
      // Create an instance, casting it to any to access the private method
      const generator = new ReportGenerator('http://localhost') as any;

      const result = generator.calculateAttackSurface({});

      assert.deepStrictEqual(result, {
        subdomains: 0,
        ips: 0,
        services: 0,
        vulnerabilities: 0
      });
    });
  });
});
