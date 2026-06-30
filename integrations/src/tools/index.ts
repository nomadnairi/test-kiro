// Base classes
export { BaseTool, ToolConfig, ToolResult } from './base-tool';
export { ToolOrchestrator } from './tool-orchestrator';

// Recon tools
export { AmassTool } from './recon/amass';
export { SubfinderTool } from './recon/subfinder';
export { AssetfinderTool } from './recon/assetfinder';
export { NucleiTool } from './recon/nuclei';
export { HttpxTool } from './recon/httpx';
export { NaabuTool } from './recon/naabu';
export { DnsxTool } from './recon/dnsx';
export { KatanaTool } from './recon/katana';
export { GauTool } from './recon/gau';
export { WaybackurlsTool } from './recon/waybackurls';
export { TheHarvesterTool } from './recon/theharvester';
export { WhatWebTool } from './recon/whatweb';
export { WappalyzerTool } from './recon/wappalyzer';
export { MasscanTool } from './recon/masscan';
export { PhotonTool } from './recon/photon';
export { AquatoneTool } from './recon/aquatone';

// Social media tools
export { SherlockTool } from './social/sherlock';
export { HoleheTool } from './social/holehe';
export { MaigretTool } from './social/maigret';
export { SocialscanTool } from './social/socialscan';

// Code analysis tools
export { TruffleHogTool } from './code/trufflehog';
export { GitleaksTool } from './code/gitleaks';

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
