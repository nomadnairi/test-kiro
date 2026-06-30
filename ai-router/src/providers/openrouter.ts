import axios from 'axios';
import { AIProvider, ChatRequest, ChatResponse } from './base';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'openrouter-provider' });

export class OpenRouterProvider extends AIProvider {
  name = 'openrouter';
  available = true;
  private apiKey: string;
  private baseUrl = 'https://openrouter.ai/api/v1';

  constructor(apiKey: string) {
    super();
    this.apiKey = apiKey;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/chat/completions`,
        {
          model: request.model || 'anthropic/claude-3.5-sonnet',
          messages: request.messages,
          temperature: request.temperature || 0.7,
          max_tokens: request.maxTokens || 4096,
        },
        {
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
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
      logger.error('OpenRouter chat failed', error);
      throw error;
    }
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<any> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/chat/completions`,
        {
          model: request.model || 'anthropic/claude-3.5-sonnet',
          messages: request.messages,
          temperature: request.temperature || 0.7,
          max_tokens: request.maxTokens || 4096,
          stream: true,
        },
        {
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          responseType: 'stream',
        }
      );

      for await (const chunk of response.data) {
        const lines = chunk
          .toString()
          .split('\n')
          .filter((line: string) => line.trim());

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;

            try {
              const parsed = JSON.parse(data);
              const content = parsed.choices[0]?.delta?.content;
              if (content) {
                yield {
                  content,
                  done: parsed.choices[0].finish_reason !== null,
                };
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      logger.error('OpenRouter stream failed', error);
      throw error;
    }
  }

  async checkAvailability(): Promise<boolean> {
    try {
      await axios.get(`${this.baseUrl}/models`, {
        headers: { Authorization: `Bearer ${this.apiKey}` },
      });
      this.available = true;
      return true;
    } catch (error) {
      this.available = false;
      return false;
    }
  }
}
