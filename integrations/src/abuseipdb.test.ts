import axios from 'axios';
import { AbuseIPDBIntegration } from './abuseipdb';
import { createLogger } from '@cyberintel/shared';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

jest.mock('@cyberintel/shared', () => ({
  createLogger: jest.fn(() => ({
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
  })),
}));

describe('AbuseIPDBIntegration', () => {
  let integration: AbuseIPDBIntegration;

  beforeEach(() => {
    integration = new AbuseIPDBIntegration({ apiKey: 'test-key' });
    jest.clearAllMocks();
  });

  describe('checkIP', () => {
    it('should handle API errors and return an error result', async () => {
      const errorMessage = 'API Error';
      mockedAxios.get.mockRejectedValue(new Error(errorMessage));

      const result = await integration.checkIP('1.1.1.1');

      expect(mockedAxios.get).toHaveBeenCalledTimes(1);
      expect(result.success).toBe(false);
      expect(result.error).toBe(errorMessage);
      expect(result.source).toBe('abuseipdb');
      expect(result.data).toBeUndefined();
    });
  });
});
