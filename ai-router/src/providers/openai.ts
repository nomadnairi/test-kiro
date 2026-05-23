import OpenAI from 'openai';
import { AIProvider, ChatRequest, ChatResponse } from './base';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'openai-provider' });

export class OpenAIProvider extends AIProvider {
  name = 'openai';
  available = true;
  private client: OpenAI;

  constructor(apiKey: string) {
    super();
    this.client = new OpenAI({ apiKey });
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const completion = await this.client.chat.completions.create({
        model: request.model || 'gpt-4-turbo-preview',
        messages: request.messages,
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 4096,
      });

      const message = completion.choices[0].message;

      return {
        content: message.content || '',
        model: completion.model,
        provider: this.name,
        usage: {
          promptTokens: completion.usage?.prompt_tokens || 0,
          completionTokens: completion.usage?.completion_tokens || 0,
          totalTokens: completion.usage?.total_tokens || 0,
        },
        finishReason: completion.choices[0].finish_reason,
      };
    } catch (error) {
      logger.error('OpenAI chat failed', error);
      throw error;
    }
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<any> {
    try {
      const stream = await this.client.chat.completions.create({
        model: request.model || 'gpt-4-turbo-preview',
        messages: request.messages,
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 4096,
        stream: true,
      });

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          yield {
            content,
            done: chunk.choices[0].finish_reason !== null,
          };
        }
      }
    } catch (error) {
      logger.error('OpenAI stream failed', error);
      throw error;
    }
  }

  async checkAvailability(): Promise<boolean> {
    try {
      await this.client.models.list();
      this.available = true;
      return true;
    } catch (error) {
      this.available = false;
      return false;
    }
  }
}
