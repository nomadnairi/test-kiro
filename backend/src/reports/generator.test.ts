import { ReportGenerator } from './generator';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { createLogger } from '@cyberintel/shared';

jest.mock('@cyberintel/shared', () => ({
  createLogger: jest.fn().mockReturnValue({
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
  }),
}));

describe('ReportGenerator', () => {
  let generator: ReportGenerator;
  let mockAxios: MockAdapter;

  beforeEach(() => {
    generator = new ReportGenerator('http://mock-ai-router');
    mockAxios = new MockAdapter(axios);
    jest.clearAllMocks();
  });

  afterEach(() => {
    mockAxios.restore();
  });

  describe('generateRiskAnalysis', () => {
    it('should return risk analysis content on success', async () => {
      mockAxios.onPost('http://mock-ai-router/api/chat').reply(200, {
        content: 'This is a mocked risk analysis.',
      });

      const data = {
        iocs: [{ threat_level: 'CRITICAL' }],
        entities: [{ type: 'VULNERABILITY' }]
      };
      const riskScore = 80;

      const result = await (generator as any).generateRiskAnalysis(data, riskScore);

      expect(result).toBe('This is a mocked risk analysis.');
      expect(mockAxios.history.post.length).toBe(1);

      const requestData = JSON.parse(mockAxios.history.post[0].data);
      expect(requestData.messages[1].content).toContain(`Risk Score: 80/100`);
      expect(requestData.messages[1].content).toContain(`IOCs: 1`);
      expect(requestData.messages[1].content).toContain(`Vulnerabilities: 1`);
    });

    it('should return default message and log error on failure', async () => {
      mockAxios.onPost('http://mock-ai-router/api/chat').reply(500);

      // Access the private method for testing purposes
      const result = await (generator as any).generateRiskAnalysis({}, 50);

      expect(result).toBe('Risk analysis generation failed.');

      const logger = createLogger({ service: 'report-generator' });
      expect(logger.error).toHaveBeenCalledWith(
        'Failed to generate risk analysis',
        expect.any(Error)
      );
    });
  });
});
