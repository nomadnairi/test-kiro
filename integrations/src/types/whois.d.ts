// Local type declarations for the `whois` package, which ships no types
// and has no maintained @types/whois package on the npm registry.
declare module 'whois' {
  export interface WhoisOptions {
    server?: string;
    follow?: number;
    timeout?: number;
    verbose?: boolean;
    bind?: string | null;
    proxy?: { ipaddress: string; port: number; type?: number } | false;
  }

  type LookupCallback = (err: Error | null, data: string) => void;

  export function lookup(
    domain: string,
    callback: LookupCallback,
  ): void;
  export function lookup(
    domain: string,
    options: WhoisOptions,
    callback: LookupCallback,
  ): void;

  const whois: {
    lookup: typeof lookup;
  };
  export default whois;
}
