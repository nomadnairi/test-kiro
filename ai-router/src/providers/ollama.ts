import axios from 'axios';
import { AIProvider, ChatRequest, ChatResponse } from './base';
import { createLogger } from '@cyberintel/shared';

const logger = createLogger({ service: 'ollama-provider' });

export class OllamaProvider extends AIProvider {
  name = 'ollama';
  available = true;
  private baseUrl: string;

  constructor(baseUrl: string) {
    super();
    this.baseUrl = baseUrl;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await axios.post(`${this.baseUrl}/api/chat`, {
        model: request.model || 'llama3.1:8b',
        messages: request.messages,
        stream: false,
        options: {
          temperature: request.temperature || 0.7,
          num_predict: request.maxTokens || 4096,
        },
      });

      return {
        content: response.data.message.content,
        model: response.data.model,
        provider: this.name,
        usage: {
          promptTokens: response.data.prompt_eval_count || 0,
          completionTokens: response.data.eval_count || 0,
          totalTokens: (response.data.prompt_eval_count || 0) + (response.data.eval_count || 0),
        },
        finishReason: response.data.done_reason,
      };
    } catch (error) {
      logger.error('Ollama chat failed', error);
      throw error;
    }
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<any> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/api/chat`,
        {
          model: request.model || 'llama3.1:8b',
          messages: request.messages,
          stream: true,
          options: {
            temperature: request.temperature || 0.7,
            num_predict: request.maxTokens || 4096,
          },
        },
        { responseType: 'stream' }
      );

      for await (const chunk of response.data) {
        const lines = chunk.toString().split('\n').filter((line: string) => line.trim());
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.message?.content) {
              yield {
                content: data.message.content,
                done: data.done,
              };
            }
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    } catch (error) {
      logger.error('Ollama stream failed', error);
      throw error;
    }
  }

  async checkAvailability(): Promise<boolean> {
    try {
      await axios.get(`${this.baseUrl}/api/tags`);
      this.available = true;
      return true;
    } catch (error) {
      this.available = false;
      return false;
    }
  }
}
