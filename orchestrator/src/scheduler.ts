import { createLogger } from '@cyberintel/shared';
import { TaskQueue } from './queue';

const logger = createLogger({ service: 'orchestrator-scheduler' });

export class TaskScheduler {
  private queue: TaskQueue;
  private interval: NodeJS.Timeout | null = null;
  private running = false;

  constructor(queue: TaskQueue) {
    this.queue = queue;
  }

  start(): void {
    if (this.running) return;

    this.running = true;
    logger.info('Task scheduler started');

    // Poll queue every second
    this.interval = setInterval(() => {
      this.processTasks();
    }, 1000);
  }

  stop(): void {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.running = false;
    logger.info('Task scheduler stopped');
  }

  private async processTasks(): Promise<void> {
    try {
      const stats = await this.queue.getStats();
      
      if (stats.queueSize > 0) {
        logger.debug('Processing queued tasks', { queueSize: stats.queueSize });
      }

      // Tasks are processed by workers
      // This scheduler just monitors and manages the queue
    } catch (error) {
      logger.error('Scheduler error', error);
    }
  }
}
