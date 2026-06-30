import { describe, it, mock } from 'node:test';
import assert from 'node:assert';
import axios from 'axios';
import { Logger } from '@cyberintel/shared';
import { ReportGenerator } from './generator';

describe('ReportGenerator', () => {
  describe('generateExecutiveSummary', () => {
    it('should return fallback string and log error on failure', async () => {
      const errorMsg = 'API Error';
      mock.method(axios, 'post', async () => {
        throw new Error(errorMsg);
      });

      let logErrorCalled = false;
      let loggedMessage = '';
      mock.method(Logger.prototype, 'error', (msg: string) => {
        logErrorCalled = true;
        loggedMessage = msg;
      });

      const generator = new ReportGenerator('http://test');

      // Accessing private method for testing
      const result = await (generator as any).generateExecutiveSummary({ scan: { target: 'test' } });

      assert.strictEqual(result, 'Executive summary generation failed.');
      assert.strictEqual(logErrorCalled, true);
      assert.ok(loggedMessage.includes('Failed to generate executive summary'));

      mock.restoreAll();
    });

    it('should return executive summary on success', async () => {
      mock.method(axios, 'post', async () => {
        return { data: { content: 'Successful summary' } };
      });

      const generator = new ReportGenerator('http://test');
      const result = await (generator as any).generateExecutiveSummary({ scan: { target: 'test' } });

      assert.strictEqual(result, 'Successful summary');

      mock.restoreAll();
    });
  });
});
