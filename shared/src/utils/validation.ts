import { EntityType } from '../types';

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export const validateIP = (ip: string): boolean => {
  const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
  return ipv4Regex.test(ip) || ipv6Regex.test(ip);
};

export const validateDomain = (domain: string): boolean => {
  const domainRegex = /^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$/i;
  return domainRegex.test(domain);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateHash = (hash: string, type: 'md5' | 'sha1' | 'sha256'): boolean => {
  const lengths = { md5: 32, sha1: 40, sha256: 64 };
  const hexRegex = /^[a-fA-F0-9]+$/;
  return hash.length === lengths[type] && hexRegex.test(hash);
};

export const detectEntityType = (value: string): EntityType => {
  if (validateIP(value)) return EntityType.IP;
  if (validateEmail(value)) return EntityType.EMAIL;
  if (validateURL(value)) return EntityType.URL;
  if (validateDomain(value)) return EntityType.DOMAIN;
  if (validateHash(value, 'md5') || validateHash(value, 'sha1') || validateHash(value, 'sha256')) {
    return EntityType.HASH;
  }
  if (/^CVE-\d{4}-\d{4,}$/i.test(value)) return EntityType.CVE;
  if (/^AS\d+$/i.test(value)) return EntityType.ASN;
  
  throw new ValidationError(`Unable to detect entity type for: ${value}`);
};

export const sanitizeInput = (input: string): string => {
  return input.trim().toLowerCase();
};

export const validateScanTarget = (target: string, type?: EntityType): void => {
  const detectedType = type || detectEntityType(target);
  
  switch (detectedType) {
    case EntityType.IP:
      if (!validateIP(target)) throw new ValidationError('Invalid IP address');
      break;
    case EntityType.DOMAIN:
      if (!validateDomain(target)) throw new ValidationError('Invalid domain');
      break;
    case EntityType.EMAIL:
      if (!validateEmail(target)) throw new ValidationError('Invalid email');
      break;
    case EntityType.URL:
      if (!validateURL(target)) throw new ValidationError('Invalid URL');
      break;
    default:
      throw new ValidationError(`Unsupported entity type: ${detectedType}`);
  }
};
