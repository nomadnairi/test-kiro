import axios from 'axios';
import { ReportGenerator } from '../generator';
import { createLogger } from '@cyberintel/shared';

jest.mock('axios');
jest.mock('@cyberintel/shared', () => {
  const mockLogger = {
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
  };
  return {
    createLogger: jest.fn(() => mockLogger),
  };
});

describe('ReportGenerator', () => {
  let generator: ReportGenerator;
  let mockLogger: any;

  beforeEach(() => {
    jest.clearAllMocks();
    mockLogger = createLogger({ service: 'test' });
    generator = new ReportGenerator('http://test-ai-router.local');
  });

  describe('generateRecommendations', () => {
    it('should handle axios failure and return fallback string while logging error', async () => {
      const mockError = new Error('Network Error');
      (axios.post as jest.Mock).mockRejectedValueOnce(mockError);

      const mockData = {
        entities: [],
        iocs: [],
      };

      // Access private method for testing specific error path
      const result = await (generator as any).generateRecommendations(mockData);

      expect(result).toBe('Recommendations generation failed.');
      expect(mockLogger.error).toHaveBeenCalledWith('Failed to generate recommendations', mockError);
    });
  });
});
