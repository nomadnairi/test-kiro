import { spawn } from 'child_process';
import { createLogger } from '@cyberintel/shared';

export interface ToolConfig {
  name: string;
  command: string;
  args?: string[];
  timeout?: number;
  rateLimit?: number;
}

export interface ToolResult {
  success: boolean;
  data?: any;
  error?: string;
  stdout?: string;
  stderr?: string;
  executionTime: number;
}

export abstract class BaseTool {
  protected logger: ReturnType<typeof createLogger>;
  protected config: ToolConfig;

  constructor(config: ToolConfig) {
    this.config = config;
    this.logger = createLogger({ service: `tool-${config.name}` });
  }

  async execute(target: string, options: Record<string, any> = {}): Promise<ToolResult> {
    const startTime = Date.now();
    
    try {
      this.logger.info('Executing tool', { tool: this.config.name, target });

      const result = await this.runCommand(target, options);
      const executionTime = Date.now() - startTime;

      this.logger.info('Tool execution complete', { 
        tool: this.config.name, 
        executionTime,
        success: result.success 
      });

      return { ...result, executionTime };
    } catch (error: any) {
      const executionTime = Date.now() - startTime;
      this.logger.error('Tool execution failed', error);
      
      return {
        success: false,
        error: error.message,
        executionTime,
      };
    }
  }

  protected async runCommand(target: string, options: Record<string, any>): Promise<ToolResult> {
    return new Promise((resolve) => {
      const args = this.buildArgs(target, options);
      const timeout = this.config.timeout || 300000; // 5 minutes default

      let stdout = '';
      let stderr = '';

      const process = spawn(this.config.command, args);

      const timer = setTimeout(() => {
        process.kill();
        resolve({
          success: false,
          error: 'Command timeout',
          stdout,
          stderr,
          executionTime: timeout,
        });
      }, timeout);

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        clearTimeout(timer);
        
        if (code === 0) {
          const parsed = this.parseOutput(stdout);
          resolve({
            success: true,
            data: parsed,
            stdout,
            stderr,
            executionTime: 0,
          });
        } else {
          resolve({
            success: false,
            error: `Command exited with code ${code}`,
            stdout,
            stderr,
            executionTime: 0,
          });
        }
      });

      process.on('error', (error) => {
        clearTimeout(timer);
        resolve({
          success: false,
          error: error.message,
          stdout,
          stderr,
          executionTime: 0,
        });
      });
    });
  }

  protected abstract buildArgs(target: string, options: Record<string, any>): string[];
  protected abstract parseOutput(output: string): any;

  async checkAvailability(): Promise<boolean> {
    try {
      const result = await this.runCommand('--version', {});
      return result.success;
    } catch {
      return false;
    }
  }
}
