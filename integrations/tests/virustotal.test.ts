import { VirusTotalIntegration } from '../src/virustotal';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('VirusTotalIntegration', () => {
  let integration: VirusTotalIntegration;

  beforeEach(() => {
    integration = new VirusTotalIntegration({ apiKey: 'test-api-key' });
    jest.clearAllMocks();
  });

  describe('analyzeHash', () => {
    it('should handle missing names and tags properties gracefully', async () => {
      const mockResponse = {
        data: {
          data: {
            attributes: {
              last_analysis_stats: {
                malicious: 0,
                suspicious: 0,
                harmless: 10,
                undetected: 50,
              },
              type_description: 'Win32 EXE',
              size: 1024,
              // Missing names and tags
            },
          },
        },
      };

      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const result = await integration.analyzeHash('fakehash');

      expect(result.data.names).toEqual([]);
      expect(result.data.tags).toEqual([]);
      expect(result.error).toBeUndefined();
      expect(result.success).toBe(true);
    });
  });
});
