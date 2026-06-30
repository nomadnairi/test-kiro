import { describe, it } from 'node:test';
import * as assert from 'node:assert';
import { ReportGenerator } from './generator';

describe('ReportGenerator', () => {
  describe('calculateAttackSurface', () => {
    it('should return 0 for all fields when entities is empty or undefined', () => {
      const generator = new ReportGenerator('http://localhost:3000');

      const dataWithEmptyEntities = { entities: [] };
      const result1 = (generator as any).calculateAttackSurface(dataWithEmptyEntities);
      assert.deepStrictEqual(result1, {
        subdomains: 0,
        ips: 0,
        services: 0,
        vulnerabilities: 0
      });

      const dataWithNoEntities = {};
      const result2 = (generator as any).calculateAttackSurface(dataWithNoEntities);
      assert.deepStrictEqual(result2, {
        subdomains: 0,
        ips: 0,
        services: 0,
        vulnerabilities: 0
      });
    });
  });
});
