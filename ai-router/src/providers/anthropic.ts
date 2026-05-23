import Anthropic from '@anthropic-ai/sdk';
import { AIProvider, ChatRequest, ChatResponse, ChatMessage } from './base';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'anthropic-provider' });

export class AnthropicProvider extends AIProvider {
  name = 'anthropic';
  available = true;
  private client: Anthropic;

  constructor(apiKey: string) {
    super();
    this.client = new Anthropic({ apiKey });
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      // Extract system message
      const systemMessage = request.messages.find(m => m.role === 'system');
      const messages = request.messages.filter(m => m.role !== 'system');

      const response = await this.client.messages.create({
        model: request.model || 'claude-3-5-sonnet-20241022',
        max_tokens: request.maxTokens || 4096,
        temperature: request.temperature || 0.7,
        system: systemMessage?.content,
        messages: messages.map(m => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
        })),
      });

      const content = response.content[0];
      const text = content.type === 'text' ? content.text : '';

      return {
        content: text,
        model: response.model,
        provider: this.name,
        usage: {
          promptTokens: response.usage.input_tokens,
          completionTokens: response.usage.output_tokens,
          totalTokens: response.usage.input_tokens + response.usage.output_tokens,
        },
        finishReason: response.stop_reason || undefined,
      };
    } catch (error) {
      logger.error('Anthropic chat failed', error);
      throw error;
    }
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<any> {
    try {
      const systemMessage = request.messages.find(m => m.role === 'system');
      const messages = request.messages.filter(m => m.role !== 'system');

      const stream = await this.client.messages.create({
        model: request.model || 'claude-3-5-sonnet-20241022',
        max_tokens: request.maxTokens || 4096,
        temperature: request.temperature || 0.7,
        system: systemMessage?.content,
        messages: messages.map(m => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
        })),
        stream: true,
      });

      for await (const event of stream) {
        if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
          yield {
            content: event.delta.text,
            done: false,
          };
        } else if (event.type === 'message_stop') {
          yield {
            content: '',
            done: true,
          };
        }
      }
    } catch (error) {
      logger.error('Anthropic stream failed', error);
      throw error;
    }
  }

  async checkAvailability(): Promise<boolean> {
    try {
      // Simple check - try to create a minimal message
      await this.client.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1,
        messages: [{ role: 'user', content: 'test' }],
      });
      this.available = true;
      return true;
    } catch (error) {
      this.available = false;
      return false;
    }
  }
}
