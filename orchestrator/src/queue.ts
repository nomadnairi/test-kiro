import Redis from 'ioredis';
import { createLogger, Task, TaskStatus, AgentType } from '@cyberintel/shared';
import { v4 as uuidv4 } from 'uuid';

const logger = createLogger({ service: 'orchestrator-queue' });

export class TaskQueue {
  private redis: Redis;
  private queueName: string;

  constructor(redis: Redis, queueName = 'cyberintel:tasks') {
    this.redis = redis;
    this.queueName = queueName;
  }

  async enqueue(task: Omit<Task, 'id' | 'createdAt' | 'status'>): Promise<string> {
    const taskId = uuidv4();
    const fullTask: Task = {
      ...task,
      id: taskId,
      status: TaskStatus.QUEUED,
      createdAt: new Date(),
    };

    // Store task
    await this.redis.set(
      `task:${taskId}`,
      JSON.stringify(fullTask),
      'EX',
      86400 // 24 hours
    );

    // Add to priority queue
    const score = this.calculatePriority(fullTask);
    await this.redis.zadd(this.queueName, score, taskId);

    logger.info('Task enqueued', { taskId, type: task.type, agentType: task.agentType });

    // Publish event
    await this.redis.publish('task:updates', JSON.stringify({
      taskId,
      status: TaskStatus.QUEUED,
      timestamp: new Date().toISOString(),
    }));

    return taskId;
  }

  async dequeue(): Promise<Task | null> {
    // Get highest priority task
    const result = await this.redis.zpopmin(this.queueName);
    
    if (!result || result.length === 0) {
      return null;
    }

    const taskId = result[0];
    const taskData = await this.redis.get(`task:${taskId}`);

    if (!taskData) {
      return null;
    }

    const task = JSON.parse(taskData) as Task;
    task.status = TaskStatus.PROCESSING;
    task.startedAt = new Date();

    await this.redis.set(`task:${taskId}`, JSON.stringify(task), 'EX', 86400);

    logger.info('Task dequeued', { taskId, type: task.type });

    return task;
  }

  async complete(taskId: string, result: any): Promise<void> {
    const taskData = await this.redis.get(`task:${taskId}`);
    if (!taskData) return;

    const task = JSON.parse(taskData) as Task;
    task.status = TaskStatus.COMPLETED;
    task.completedAt = new Date();
    task.result = result;

    await this.redis.set(`task:${taskId}`, JSON.stringify(task), 'EX', 86400);

    logger.info('Task completed', { taskId, type: task.type });

    await this.redis.publish('task:updates', JSON.stringify({
      taskId,
      status: TaskStatus.COMPLETED,
      result,
      timestamp: new Date().toISOString(),
    }));
  }

  async fail(taskId: string, error: string): Promise<void> {
    const taskData = await this.redis.get(`task:${taskId}`);
    if (!taskData) return;

    const task = JSON.parse(taskData) as Task;

    // Retry logic
    if (task.retries < task.maxRetries) {
      task.retries++;
      task.status = TaskStatus.RETRYING;
      
      await this.redis.set(`task:${taskId}`, JSON.stringify(task), 'EX', 86400);
      
      // Re-queue with exponential backoff
      const delay = Math.pow(2, task.retries) * 1000;
      const score = Date.now() + delay;
      await this.redis.zadd(this.queueName, score, taskId);

      logger.warn('Task retrying', { taskId, retries: task.retries, delay });
    } else {
      task.status = TaskStatus.FAILED;
      task.completedAt = new Date();
      task.error = error;

      await this.redis.set(`task:${taskId}`, JSON.stringify(task), 'EX', 86400);

      logger.error('Task failed', { taskId, error });

      await this.redis.publish('task:updates', JSON.stringify({
        taskId,
        status: TaskStatus.FAILED,
        error,
        timestamp: new Date().toISOString(),
      }));
    }
  }

  async getTask(taskId: string): Promise<Task | null> {
    const taskData = await this.redis.get(`task:${taskId}`);
    return taskData ? JSON.parse(taskData) : null;
  }

  async cancelTask(taskId: string): Promise<void> {
    await this.redis.zrem(this.queueName, taskId);
    await this.redis.del(`task:${taskId}`);
    logger.info('Task cancelled', { taskId });
  }

  async getStats(): Promise<any> {
    const queueSize = await this.redis.zcard(this.queueName);
    const keys = await this.redis.keys('task:*');
    
    const tasks = await Promise.all(
      keys.map(async (key) => {
        const data = await this.redis.get(key);
        return data ? JSON.parse(data) : null;
      })
    );

    const statusCounts = tasks.reduce((acc, task) => {
      if (task) {
        acc[task.status] = (acc[task.status] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

    return {
      queueSize,
      totalTasks: tasks.length,
      statusCounts,
    };
  }

  private calculatePriority(task: Task): number {
    // Lower score = higher priority
    // Priority: 0-10 (10 = highest)
    // Timestamp ensures FIFO for same priority
    const priorityWeight = (10 - task.priority) * 1000000;
    const timestamp = Date.now();
    return priorityWeight + timestamp;
  }
}
