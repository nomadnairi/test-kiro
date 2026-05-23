import axios from 'axios';
import { AIProvider, ChatRequest, ChatResponse } from './base';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'deepseek-provider' });

export class DeepSeekProvider extends AIProvider {
  name = 'deepseek';
  available = true;
  private apiKey: string;
  private baseUrl = 'https://api.deepseek.com/v1';

  constructor(apiKey: string) {
    super();
    this.apiKey = apiKey;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/chat/completions`,
        {
          model: request.model || 'deepseek-chat',
          messages: request.messages,
          temperature: request.temperature || 0.7,
          max_tokens: request.maxTokens || 4096,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const choice = response.data.choices[0];

      return {
        content: choice.message.content,
        model: response.data.model,
        provider: this.name,
        usage: {
          promptTokens: response.data.usage?.prompt_tokens || 0,
          completionTokens: response.data.usage?.completion_tokens || 0,
          totalTokens: response.data.usage?.total_tokens || 0,
        },
        finishReason: choice.finish_reason,
      };
    } catch (error) {
      logger.error('DeepSeek chat failed', error);
      throw error;
    }
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<any> {
    throw new Error('Streaming not yet implemented for DeepSeek');
  }

  async checkAvailability(): Promise<boolean> {
    try {
      await axios.get(`${this.baseUrl}/models`, {
        headers: { 'Authorization': `Bearer ${this.apiKey}` },
      });
      this.available = true;
      return true;
    } catch (error) {
      this.available = false;
      return false;
    }
  }
}
