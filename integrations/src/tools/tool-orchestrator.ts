import { createLogger } from '@cyberintel/shared';
import { AmassTool } from './recon/amass';
import { SubfinderTool } from './recon/subfinder';
import { NucleiTool } from './recon/nuclei';
import { SherlockTool } from './social/sherlock';
import { HoleheTool } from './social/holehe';
import { TruffleHogTool } from './code/trufflehog';
import { BaseTool, ToolResult } from './base-tool';

const logger = createLogger({ service: 'tool-orchestrator' });

export interface ToolExecutionPlan {
  tools: string[];
  parallel: boolean;
  timeout?: number;
}

export class ToolOrchestrator {
  private tools: Map<string, BaseTool>;
  private availableTools: Set<string>;

  constructor() {
    this.tools = new Map();
    this.availableTools = new Set();
    this.registerTools();
  }

  private registerTools() {
    const toolInstances = [
      new AmassTool(),
      new SubfinderTool(),
      new NucleiTool(),
      new SherlockTool(),
      new HoleheTool(),
      new TruffleHogTool(),
    ];

    for (const tool of toolInstances) {
      this.tools.set(tool['config'].name, tool);
    }

    logger.info('Tools registered', { count: this.tools.size });
  }

  async checkToolAvailability(): Promise<void> {
    logger.info('Checking tool availability...');

    const checks = Array.from(this.tools.entries()).map(async ([name, tool]) => {
      const available = await tool.checkAvailability();
      if (available) {
        this.availableTools.add(name);
      }
      return { name, available };
    });

    const results = await Promise.all(checks);
    
    logger.info('Tool availability check complete', {
      available: results.filter(r => r.available).map(r => r.name),
      unavailable: results.filter(r => !r.available).map(r => r.name),
    });
  }

  async executeTool(
    toolName: string,
    target: string,
    options: Record<string, any> = {}
  ): Promise<ToolResult> {
    const tool = this.tools.get(toolName);

    if (!tool) {
      return {
        success: false,
        error: `Tool ${toolName} not found`,
        executionTime: 0,
      };
    }

    if (!this.availableTools.has(toolName)) {
      return {
        success: false,
        error: `Tool ${toolName} not available`,
        executionTime: 0,
      };
    }

    return await tool.execute(target, options);
  }

  async executeParallel(
    tools: string[],
    target: string,
    options: Record<string, any> = {}
  ): Promise<Record<string, ToolResult>> {
    logger.info('Executing tools in parallel', { tools, target });

    const executions = tools.map(async (toolName) => {
      const result = await this.executeTool(toolName, target, options);
      return { toolName, result };
    });

    const results = await Promise.all(executions);

    const resultMap: Record<string, ToolResult> = {};
    for (const { toolName, result } of results) {
      resultMap[toolName] = result;
    }

    logger.info('Parallel execution complete', {
      total: tools.length,
      successful: Object.values(resultMap).filter(r => r.success).length,
    });

    return resultMap;
  }

  async executeSequential(
    tools: string[],
    target: string,
    options: Record<string, any> = {}
  ): Promise<Record<string, ToolResult>> {
    logger.info('Executing tools sequentially', { tools, target });

    const results: Record<string, ToolResult> = {};

    for (const toolName of tools) {
      results[toolName] = await this.executeTool(toolName, target, options);
    }

    logger.info('Sequential execution complete', {
      total: tools.length,
      successful: Object.values(results).filter(r => r.success).length,
    });

    return results;
  }

  getAvailableTools(): string[] {
    return Array.from(this.availableTools);
  }

  getAllTools(): string[] {
    return Array.from(this.tools.keys());
  }
}
