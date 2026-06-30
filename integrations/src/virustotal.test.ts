import axios from 'axios';
import { VirusTotalIntegration } from './virustotal';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('VirusTotalIntegration', () => {
  let integration: VirusTotalIntegration;

  beforeEach(() => {
    integration = new VirusTotalIntegration({ apiKey: 'test-api-key' });
    jest.clearAllMocks();
  });

  describe('analyzeIP', () => {
    it('should handle API errors and call handleError', async () => {
      const errorMessage = 'Network error';
      mockedAxios.get.mockRejectedValue(new Error(errorMessage));

      const result = await integration.analyzeIP('1.1.1.1');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        'https://www.virustotal.com/api/v3/ip_addresses/1.1.1.1',
        {
          headers: { 'x-apikey': 'test-api-key' },
          timeout: 30000,
        }
      );

      expect(result).toEqual({
        success: false,
        error: errorMessage,
        source: 'virustotal',
        timestamp: expect.any(Date),
      });
    });
  });
});
