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

  describe('analyzeURL', () => {
    it('should handle POST request error gracefully', async () => {
      mockedAxios.post.mockRejectedValue(new Error('Network error on POST'));

      const result = await integration.analyzeURL('http://example.com');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Network error on POST');
      expect(result.source).toBe('virustotal');
    });

    it('should handle GET request error gracefully', async () => {
      jest.useFakeTimers();

      try {
        // Mock successful POST for submission
        mockedAxios.post.mockResolvedValue({
          data: { data: { id: 'test-analysis-id' } },
        });

        // Mock failing GET for analysis status
        mockedAxios.get.mockRejectedValue(new Error('Network error on GET'));

        const promise = integration.analyzeURL('http://example.com');

        await Promise.resolve(); // Allow the POST request and its then handlers to run
        jest.advanceTimersByTime(5000); // Advance timers by 5000ms

        const result = await promise;

        expect(result.success).toBe(false);
        expect(result.error).toBe('Network error on GET');
        expect(result.source).toBe('virustotal');
      } finally {
        jest.useRealTimers();
      }
    });
  });
});
