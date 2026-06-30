import test from 'node:test';
import assert from 'node:assert';
import { ReportGenerator } from './generator';
import axios from 'axios';
import { Logger } from '@cyberintel/shared';

test('ReportGenerator generateExecutiveSummary error handling', async (t) => {
  const originalPost = axios.post;
  const originalLoggerError = Logger.prototype.error;

  let loggerErrorCalled = false;
  let loggerErrorArgs: any[] = [];

  try {
    // Mock axios post to throw an error
    axios.post = async () => {
      throw new Error('Network error');
    };

    // Mock logger.error on the prototype since generator.ts creates an instance
    Logger.prototype.error = (message: string, error?: any, meta?: any) => {
      loggerErrorCalled = true;
      loggerErrorArgs = [message, error, meta];
    };

    const generator = new ReportGenerator('http://test-url');
    // We need to access private method, so we use type assertion
    const summary = await (generator as any).generateExecutiveSummary({});

    assert.strictEqual(summary, 'Executive summary generation failed.');
    assert.strictEqual(loggerErrorCalled, true, 'logger.error should be called');
    assert.strictEqual(loggerErrorArgs[0], 'Failed to generate executive summary');
    assert.strictEqual(loggerErrorArgs[1]?.message, 'Network error');
  } finally {
    // Restore original functions
    axios.post = originalPost;
    Logger.prototype.error = originalLoggerError;
  }
});
