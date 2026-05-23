# Security Guide

## Overview

Security is a top priority for the CyberIntel Platform.

## Authentication

### JWT Tokens
- Tokens expire after 7 days (configurable)
- Refresh tokens for long-lived sessions
- Secure token storage in httpOnly cookies

### Password Requirements
- Minimum 8 characters
- Bcrypt hashing with salt rounds: 10
- Password reset via email

## Authorization

### Role-Based Access Control (RBAC)

**Roles:**
- **Admin**: Full system access
- **Analyst**: Create scans, view all data
- **Viewer**: Read-only access

**Permissions:**
```
Admin: *
Analyst: scans.*, entities.read, iocs.read, graph.read
Viewer: *.read
```

## API Security

### Rate Limiting
- 100 requests per 15 minutes (unauthenticated)
- 1000 requests per 15 minutes (authenticated)
- Configurable per endpoint

### Input Validation
- Zod schema validation
- SQL injection prevention
- XSS protection
- CSRF tokens

## Data Security

### Encryption
- **At Rest**: Database encryption (configure in PostgreSQL/Neo4j)
- **In Transit**: TLS 1.3 for all connections
- **Secrets**: Environment variables, never in code

### Database Security
- Parameterized queries
- Least privilege access
- Connection pooling
- Regular backups

## Network Security

### Firewall Rules
```
Allow: 443 (HTTPS)
Allow: 22 (SSH, admin only)
Deny: All other inbound
```

### Docker Network
- Isolated bridge network
- No direct external access to databases
- Gateway as single entry point

## Secrets Management

### Environment Variables
```bash
# Never commit .env files
# Use strong random secrets
JWT_SECRET=$(openssl rand -base64 32)
```

### Production Secrets
- Use AWS Secrets Manager / HashiCorp Vault
- Rotate secrets regularly
- Audit secret access

## Audit Logging

All actions are logged:
- User authentication
- Scan creation
- Data access
- Configuration changes

Log format:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "user_id": "uuid",
  "action": "scan.create",
  "resource_id": "uuid",
  "ip_address": "1.2.3.4",
  "details": {}
}
```

## Security Headers

```
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

## Vulnerability Management

### Dependency Scanning
```bash
npm audit
pip-audit
```

### Container Scanning
```bash
docker scan cyberintel/gateway
```

### Regular Updates
- Weekly dependency updates
- Monthly security patches
- Quarterly security audits

## Incident Response

### Detection
- Monitor audit logs
- Alert on suspicious activity
- Track failed login attempts

### Response Plan
1. Identify incident
2. Contain threat
3. Investigate root cause
4. Remediate vulnerability
5. Document lessons learned

## Compliance

### Data Protection
- GDPR compliant
- Data retention policies
- Right to deletion
- Data export

### Security Standards
- OWASP Top 10
- CIS Benchmarks
- NIST Cybersecurity Framework

## Security Checklist

### Pre-Production
- [ ] Change all default credentials
- [ ] Set strong JWT_SECRET
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Enable audit logging
- [ ] Configure backups
- [ ] Review permissions
- [ ] Scan for vulnerabilities
- [ ] Test incident response

### Post-Production
- [ ] Monitor logs daily
- [ ] Review access weekly
- [ ] Update dependencies monthly
- [ ] Security audit quarterly
- [ ] Penetration test annually

## Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

Email: security@cyberintel.local

Include:
- Description
- Steps to reproduce
- Impact assessment
- Suggested fix (if any)

We will respond within 48 hours.
