import { createLogger, AgentType, EntityType } from '@cyberintel/shared';
import { TaskQueue } from './queue';
import { TaskScheduler } from './scheduler';
import { v4 as uuidv4 } from 'uuid';

const logger = createLogger({ service: 'orchestrator-workflow' });

export interface ScanWorkflowConfig {
  scanId: string;
  target: string;
  targetType: EntityType;
  modules?: string[];
  depth: number;
  autoRecon: boolean;
}

export class WorkflowEngine {
  private queue: TaskQueue;
  private scheduler: TaskScheduler;

  constructor(queue: TaskQueue, scheduler: TaskScheduler) {
    this.queue = queue;
    this.scheduler = scheduler;
  }

  async createScanWorkflow(config: ScanWorkflowConfig): Promise<string> {
    const workflowId = uuidv4();

    logger.info('Creating scan workflow', { workflowId, scanId: config.scanId });

    // Phase 1: Initial Reconnaissance
    const reconTaskId = await this.queue.enqueue({
      type: 'recon',
      agentType: AgentType.RECON,
      payload: {
        workflowId,
        scanId: config.scanId,
        target: config.target,
        targetType: config.targetType,
        depth: config.depth,
      },
      priority: 8,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 2: DNS Intelligence
    const dnsTaskId = await this.queue.enqueue({
      type: 'dns_analysis',
      agentType: AgentType.DNS,
      payload: {
        workflowId,
        scanId: config.scanId,
        target: config.target,
        dependsOn: [reconTaskId],
      },
      priority: 7,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 3: Threat Intelligence Gathering
    const threatIntelTaskId = await this.queue.enqueue({
      type: 'threat_intel',
      agentType: AgentType.THREAT_INTEL,
      payload: {
        workflowId,
        scanId: config.scanId,
        target: config.target,
        dependsOn: [reconTaskId],
      },
      priority: 7,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 4: IOC Detection
    const iocTaskId = await this.queue.enqueue({
      type: 'ioc_detection',
      agentType: AgentType.IOC,
      payload: {
        workflowId,
        scanId: config.scanId,
        dependsOn: [threatIntelTaskId],
      },
      priority: 6,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 5: Entity Resolution
    const entityTaskId = await this.queue.enqueue({
      type: 'entity_resolution',
      agentType: AgentType.ENTITY_RESOLUTION,
      payload: {
        workflowId,
        scanId: config.scanId,
        dependsOn: [reconTaskId, dnsTaskId, threatIntelTaskId],
      },
      priority: 5,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 6: Graph Analysis
    const graphTaskId = await this.queue.enqueue({
      type: 'graph_analysis',
      agentType: AgentType.GRAPH_ANALYSIS,
      payload: {
        workflowId,
        scanId: config.scanId,
        dependsOn: [entityTaskId],
      },
      priority: 4,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 7: Correlation Analysis
    const correlationTaskId = await this.queue.enqueue({
      type: 'correlation',
      agentType: AgentType.CORRELATION,
      payload: {
        workflowId,
        scanId: config.scanId,
        dependsOn: [iocTaskId, graphTaskId],
      },
      priority: 3,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 8: Attack Surface Mapping
    const attackSurfaceTaskId = await this.queue.enqueue({
      type: 'attack_surface',
      agentType: AgentType.ATTACK_SURFACE,
      payload: {
        workflowId,
        scanId: config.scanId,
        dependsOn: [graphTaskId, correlationTaskId],
      },
      priority: 2,
      retries: 0,
      maxRetries: 3,
    });

    // Phase 9: Report Generation
    const reportTaskId = await this.queue.enqueue({
      type: 'report',
      agentType: AgentType.REPORT,
      payload: {
        workflowId,
        scanId: config.scanId,
        dependsOn: [attackSurfaceTaskId, correlationTaskId],
      },
      priority: 1,
      retries: 0,
      maxRetries: 3,
    });

    logger.info('Scan workflow created', {
      workflowId,
      scanId: config.scanId,
      tasks: [
        reconTaskId,
        dnsTaskId,
        threatIntelTaskId,
        iocTaskId,
        entityTaskId,
        graphTaskId,
        correlationTaskId,
        attackSurfaceTaskId,
        reportTaskId,
      ],
    });

    return workflowId;
  }

  async createCustomWorkflow(tasks: any[]): Promise<string> {
    const workflowId = uuidv4();

    for (const task of tasks) {
      await this.queue.enqueue({
        ...task,
        payload: {
          ...task.payload,
          workflowId,
        },
      });
    }

    return workflowId;
  }
}
