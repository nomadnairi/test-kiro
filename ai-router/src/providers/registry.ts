import { AIProvider } from './base';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'ai-provider-registry' });

export class ProviderRegistry {
  private providers: Map<string, AIProvider> = new Map();

  register(provider: AIProvider): void {
    this.providers.set(provider.name, provider);
    logger.info('Provider registered', { provider: provider.name });
  }

  getProvider(name: string): AIProvider | undefined {
    return this.providers.get(name);
  }

  listProviders(): Array<{ name: string; available: boolean }> {
    return Array.from(this.providers.values()).map((p) => ({
      name: p.name,
      available: p.available,
    }));
  }

  async checkAvailability(): Promise<void> {
    for (const provider of this.providers.values()) {
      try {
        await provider.checkAvailability();
      } catch (error) {
        logger.error('Provider availability check failed', error, { provider: provider.name });
      }
    }
  }
}
