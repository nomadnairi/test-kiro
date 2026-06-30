import { DNSIntegration } from './dns';
import { IntegrationResult } from './base';

describe('DNSIntegration', () => {
  let integration: DNSIntegration;

  beforeEach(() => {
    integration = new DNSIntegration({});
    jest.clearAllMocks();

    // Silence logger during tests
    jest.spyOn(integration as any, 'handleError').mockImplementation(async (error: any) => {
        return {
            success: false,
            error: error.message || 'Unknown error',
            source: integration.name,
            timestamp: new Date(),
        };
    });
  });

  describe('resolveAll', () => {
    it('should correctly map all successfully resolved data', async () => {
      const mockResult = (data: any): IntegrationResult => ({
        success: true,
        data,
        source: 'dns',
        timestamp: new Date()
      });

      jest.spyOn(integration, 'resolveA').mockResolvedValue(mockResult(['1.1.1.1']));
      jest.spyOn(integration, 'resolveAAAA').mockResolvedValue(mockResult(['::1']));
      jest.spyOn(integration, 'resolveMX').mockResolvedValue(mockResult([{ exchange: 'mail.example.com', priority: 10 }]));
      jest.spyOn(integration, 'resolveTXT').mockResolvedValue(mockResult([['v=spf1 -all']]));
      jest.spyOn(integration, 'resolveNS').mockResolvedValue(mockResult(['ns1.example.com']));

      const result = await integration.resolveAll('example.com');

      expect(result.success).toBe(true);
      expect(result.data).toEqual({
        domain: 'example.com',
        a: ['1.1.1.1'],
        aaaa: ['::1'],
        mx: [{ exchange: 'mail.example.com', priority: 10 }],
        txt: [['v=spf1 -all']],
        ns: ['ns1.example.com'],
      });

      expect(integration.resolveA).toHaveBeenCalledWith('example.com');
      expect(integration.resolveAAAA).toHaveBeenCalledWith('example.com');
      expect(integration.resolveMX).toHaveBeenCalledWith('example.com');
      expect(integration.resolveTXT).toHaveBeenCalledWith('example.com');
      expect(integration.resolveNS).toHaveBeenCalledWith('example.com');
    });

    it('should handle partial rejections and map to null values', async () => {
      const mockResult = (data: any): IntegrationResult => ({
        success: true,
        data,
        source: 'dns',
        timestamp: new Date()
      });

      // Some resolve successfully
      jest.spyOn(integration, 'resolveA').mockResolvedValue(mockResult(['1.1.1.1']));
      jest.spyOn(integration, 'resolveTXT').mockResolvedValue(mockResult([['v=spf1 -all']]));

      // Some are rejected
      jest.spyOn(integration, 'resolveAAAA').mockRejectedValue(new Error('Failed to resolve AAAA'));
      jest.spyOn(integration, 'resolveMX').mockRejectedValue(new Error('Failed to resolve MX'));
      jest.spyOn(integration, 'resolveNS').mockRejectedValue(new Error('Failed to resolve NS'));

      const result = await integration.resolveAll('example.com');

      expect(result.success).toBe(true);
      expect(result.data).toEqual({
        domain: 'example.com',
        a: ['1.1.1.1'],
        aaaa: null,
        mx: null,
        txt: [['v=spf1 -all']],
        ns: null,
      });
    });

    it('should handle complete failure in resolveAll outer catch block', async () => {
      const error = new Error('Unexpected error in Promise.allSettled');
      jest.spyOn(Promise, 'allSettled').mockRejectedValueOnce(error);

      const result = await integration.resolveAll('example.com');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Unexpected error in Promise.allSettled');
      expect(result.source).toBe('dns');
    });
  });
});
