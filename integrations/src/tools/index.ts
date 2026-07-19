// Base classes
import { BaseTool } from './base-tool';
import { AmassTool } from './recon/amass';
import { SubfinderTool } from './recon/subfinder';
import { AssetfinderTool } from './recon/assetfinder';
import { NucleiTool } from './recon/nuclei';
import { HttpxTool } from './recon/httpx';
import { NaabuTool } from './recon/naabu';
import { DnsxTool } from './recon/dnsx';
import { KatanaTool } from './recon/katana';
import { GauTool } from './recon/gau';
import { WaybackurlsTool } from './recon/waybackurls';
import { TheHarvesterTool } from './recon/theharvester';
import { WhatWebTool } from './recon/whatweb';
import { WappalyzerTool } from './recon/wappalyzer';
import { MasscanTool } from './recon/masscan';
import { PhotonTool } from './recon/photon';
import { AquatoneTool } from './recon/aquatone';
import { SherlockTool } from './social/sherlock';
import { HoleheTool } from './social/holehe';
import { MaigretTool } from './social/maigret';
import { SocialscanTool } from './social/socialscan';
import { TruffleHogTool } from './code/trufflehog';
import { GitleaksTool } from './code/gitleaks';

// Re-export the public surface so consumers can import from the barrel.
export { BaseTool, ToolConfig, ToolResult } from './base-tool';
export { ToolOrchestrator } from './tool-orchestrator';
export {
  AmassTool,
  SubfinderTool,
  AssetfinderTool,
  NucleiTool,
  HttpxTool,
  NaabuTool,
  DnsxTool,
  KatanaTool,
  GauTool,
  WaybackurlsTool,
  TheHarvesterTool,
  WhatWebTool,
  WappalyzerTool,
  MasscanTool,
  PhotonTool,
  AquatoneTool,
  SherlockTool,
  HoleheTool,
  MaigretTool,
  SocialscanTool,
  TruffleHogTool,
  GitleaksTool,
};

// Tool registry
export const AVAILABLE_TOOLS = {
  // Recon
  amass: AmassTool,
  subfinder: SubfinderTool,
  assetfinder: AssetfinderTool,
  nuclei: NucleiTool,
  httpx: HttpxTool,
  naabu: NaabuTool,
  dnsx: DnsxTool,
  katana: KatanaTool,
  gau: GauTool,
  waybackurls: WaybackurlsTool,
  theharvester: TheHarvesterTool,
  whatweb: WhatWebTool,
  wappalyzer: WappalyzerTool,
  masscan: MasscanTool,
  photon: PhotonTool,
  aquatone: AquatoneTool,
  
  // Social
  sherlock: SherlockTool,
  holehe: HoleheTool,
  maigret: MaigretTool,
  socialscan: SocialscanTool,
  
  // Code
  trufflehog: TruffleHogTool,
  gitleaks: GitleaksTool,
};

export type ToolName = keyof typeof AVAILABLE_TOOLS;

export function getTool(name: ToolName): BaseTool {
  const ToolClass = AVAILABLE_TOOLS[name];
  if (!ToolClass) {
    throw new Error(`Tool ${name} not found`);
  }
  return new ToolClass();
}

export function getAllTools(): BaseTool[] {
  return Object.values(AVAILABLE_TOOLS).map(ToolClass => new ToolClass());
}

export async function checkToolAvailability(): Promise<Record<string, boolean>> {
  const tools = getAllTools();
  const availability: Record<string, boolean> = {};
  
  await Promise.all(
    tools.map(async (tool) => {
      const available = await tool.checkAvailability();
      availability[tool['config'].name] = available;
    })
  );
  
  return availability;
}
