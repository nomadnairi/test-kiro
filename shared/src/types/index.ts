import { z } from 'zod';

// ============================================================================
// Core Entity Types
// ============================================================================

export enum EntityType {
  IP = 'IP',
  DOMAIN = 'DOMAIN',
  URL = 'URL',
  EMAIL = 'EMAIL',
  HASH = 'HASH',
  CVE = 'CVE',
  ASN = 'ASN',
  CERTIFICATE = 'CERTIFICATE',
  PHONE = 'PHONE',
  USERNAME = 'USERNAME',
  ORGANIZATION = 'ORGANIZATION',
  PERSON = 'PERSON',
}

export enum ThreatLevel {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
  INFO = 'INFO',
  UNKNOWN = 'UNKNOWN',
}

export enum ScanStatus {
  PENDING = 'PENDING',
  RUNNING = 'RUNNING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
}

export enum TaskStatus {
  QUEUED = 'QUEUED',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  RETRYING = 'RETRYING',
}

export enum AgentType {
  RECON = 'RECON',
  DNS = 'DNS',
  THREAT_INTEL = 'THREAT_INTEL',
  CORRELATION = 'CORRELATION',
  IOC = 'IOC',
  REPORT = 'REPORT',
  GRAPH_ANALYSIS = 'GRAPH_ANALYSIS',
  ATTACK_SURFACE = 'ATTACK_SURFACE',
  ENTITY_RESOLUTION = 'ENTITY_RESOLUTION',
}

// ============================================================================
// Zod Schemas
// ============================================================================

export const EntitySchema = z.object({
  id: z.string().uuid(),
  type: z.nativeEnum(EntityType),
  value: z.string(),
  metadata: z.record(z.any()).optional(),
  threatLevel: z.nativeEnum(ThreatLevel).optional(),
  firstSeen: z.date(),
  lastSeen: z.date(),
  tags: z.array(z.string()).optional(),
});

export const IOCSchema = z.object({
  id: z.string().uuid(),
  type: z.nativeEnum(EntityType),
  value: z.string(),
  source: z.string(),
  confidence: z.number().min(0).max(100),
  threatLevel: z.nativeEnum(ThreatLevel),
  description: z.string().optional(),
  tags: z.array(z.string()),
  firstSeen: z.date(),
  lastSeen: z.date(),
  metadata: z.record(z.any()).optional(),
});

export const ScanSchema = z.object({
  id: z.string().uuid(),
  target: z.string(),
  targetType: z.nativeEnum(EntityType),
  status: z.nativeEnum(ScanStatus),
  progress: z.number().min(0).max(100),
  startedAt: z.date(),
  completedAt: z.date().optional(),
  results: z.record(z.any()).optional(),
  error: z.string().optional(),
  userId: z.string().uuid(),
});

export const TaskSchema = z.object({
  id: z.string().uuid(),
  type: z.string(),
  agentType: z.nativeEnum(AgentType),
  payload: z.record(z.any()),
  status: z.nativeEnum(TaskStatus),
  priority: z.number().min(0).max(10),
  retries: z.number(),
  maxRetries: z.number(),
  createdAt: z.date(),
  startedAt: z.date().optional(),
  completedAt: z.date().optional(),
  result: z.record(z.any()).optional(),
  error: z.string().optional(),
});

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  username: z.string(),
  role: z.enum(['admin', 'analyst', 'viewer']),
  createdAt: z.date(),
  lastLogin: z.date().optional(),
});

// ============================================================================
// TypeScript Types
// ============================================================================

export type Entity = z.infer<typeof EntitySchema>;
export type IOC = z.infer<typeof IOCSchema>;
export type Scan = z.infer<typeof ScanSchema>;
export type Task = z.infer<typeof TaskSchema>;
export type User = z.infer<typeof UserSchema>;

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface CreateScanRequest {
  target: string;
  targetType: EntityType;
  modules?: string[];
  depth?: number;
  autoRecon?: boolean;
}

export interface CreateScanResponse {
  scanId: string;
  status: ScanStatus;
  message: string;
}

export interface ScanResult {
  scanId: string;
  target: string;
  status: ScanStatus;
  progress: number;
  entities: Entity[];
  iocs: IOC[];
  relationships: Relationship[];
  timeline: TimelineEvent[];
  attackSurface: AttackSurface;
}

export interface Relationship {
  id: string;
  sourceId: string;
  targetId: string;
  type: string;
  properties?: Record<string, any>;
  confidence: number;
  createdAt: Date;
}

export interface TimelineEvent {
  id: string;
  timestamp: Date;
  type: string;
  entityId: string;
  description: string;
  metadata?: Record<string, any>;
}

export interface AttackSurface {
  domains: number;
  subdomains: number;
  ips: number;
  ports: number;
  services: number;
  vulnerabilities: number;
  exposedAssets: ExposedAsset[];
}

export interface ExposedAsset {
  type: string;
  value: string;
  severity: ThreatLevel;
  description: string;
  recommendations: string[];
}

// ============================================================================
// WebSocket Message Types
// ============================================================================

export enum WSMessageType {
  SCAN_UPDATE = 'SCAN_UPDATE',
  ENTITY_DISCOVERED = 'ENTITY_DISCOVERED',
  IOC_DETECTED = 'IOC_DETECTED',
  TASK_UPDATE = 'TASK_UPDATE',
  AGENT_MESSAGE = 'AGENT_MESSAGE',
  SYSTEM_ALERT = 'SYSTEM_ALERT',
}

export interface WSMessage {
  type: WSMessageType;
  payload: any;
  timestamp: Date;
}

// ============================================================================
// Integration Types
// ============================================================================

export interface IntegrationConfig {
  name: string;
  enabled: boolean;
  apiKey?: string;
  rateLimit?: number;
  timeout?: number;
}

export interface IntegrationResult {
  source: string;
  success: boolean;
  data?: any;
  error?: string;
  timestamp: Date;
}

// ============================================================================
// AI Agent Types
// ============================================================================

export interface AgentMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
}

export interface AgentContext {
  scanId?: string;
  target?: string;
  entities?: Entity[];
  iocs?: IOC[];
  history?: AgentMessage[];
}

export interface AgentResponse {
  agentType: AgentType;
  message: string;
  actions?: AgentAction[];
  confidence: number;
  reasoning?: string;
}

export interface AgentAction {
  type: string;
  target: string;
  parameters?: Record<string, any>;
}

// ============================================================================
// Graph Types
// ============================================================================

export interface GraphNode {
  id: string;
  label: string;
  type: EntityType;
  properties: Record<string, any>;
  threatLevel?: ThreatLevel;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  properties?: Record<string, any>;
}

export interface GraphQuery {
  startNode?: string;
  nodeTypes?: EntityType[];
  relationshipTypes?: string[];
  depth?: number;
  limit?: number;
}

export interface GraphResult {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: {
    totalNodes: number;
    totalEdges: number;
    queryTime: number;
  };
}
