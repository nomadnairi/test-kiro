export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

export interface LogContext {
  service?: string;
  requestId?: string;
  userId?: string;
  scanId?: string;
  [key: string]: any;
}

export class Logger {
  private context: LogContext;
  private level: LogLevel;

  constructor(context: LogContext = {}, level: LogLevel = LogLevel.INFO) {
    this.context = context;
    this.level = level;
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
    return levels.indexOf(level) >= levels.indexOf(this.level);
  }

  private formatMessage(level: LogLevel, message: string, meta?: any) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...this.context,
      ...(meta && { meta }),
    };

    if (process.env.LOG_FORMAT === 'json') {
      return JSON.stringify(logEntry);
    }

    const contextStr = Object.entries(this.context)
      .map(([k, v]) => `${k}=${v}`)
      .join(' ');
    const metaStr = meta ? ` ${JSON.stringify(meta)}` : '';
    return `[${timestamp}] ${level.toUpperCase()} ${contextStr} - ${message}${metaStr}`;
  }

  debug(message: string, meta?: any) {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(this.formatMessage(LogLevel.DEBUG, message, meta));
    }
  }

  info(message: string, meta?: any) {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.formatMessage(LogLevel.INFO, message, meta));
    }
  }

  warn(message: string, meta?: any) {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(this.formatMessage(LogLevel.WARN, message, meta));
    }
  }

  error(message: string, error?: Error | any, meta?: any) {
    if (this.shouldLog(LogLevel.ERROR)) {
      const errorMeta = error instanceof Error
        ? { error: error.message, stack: error.stack, ...meta }
        : { error, ...meta };
      console.error(this.formatMessage(LogLevel.ERROR, message, errorMeta));
    }
  }

  child(context: LogContext): Logger {
    return new Logger({ ...this.context, ...context }, this.level);
  }
}

export const createLogger = (context: LogContext = {}): Logger => {
  const level = (process.env.LOG_LEVEL as LogLevel) || LogLevel.INFO;
  return new Logger(context, level);
};
