import { createLogger } from '@cyberintel/shared';

export interface IntegrationConfig {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;
  rateLimit?: number;
}

export interface IntegrationResult<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  source: string;
  timestamp: Date;
}

export abstract class BaseIntegration {
  protected config: IntegrationConfig;
  protected logger: ReturnType<typeof createLogger>;
  abstract name: string;

  constructor(config: IntegrationConfig) {
    this.config = config;
    this.logger = createLogger({ service: `integration-${this.constructor.name}` });
  }

  protected async handleError(error: any): Promise<IntegrationResult> {
    this.logger.error(`${this.name} integration error`, error);
    return {
      success: false,
      error: error.message || 'Unknown error',
      source: this.name,
      timestamp: new Date(),
    };
  }

  protected createResult<T>(data: T): IntegrationResult<T> {
    return {
      success: true,
      data,
      source: this.name,
      timestamp: new Date(),
    };
  }
}
