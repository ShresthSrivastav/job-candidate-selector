# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| v1.1.0-final | Yes |
| < v1.1.0 | No |

## Reporting a Vulnerability

This project processes candidate profile data locally. No data is transmitted externally.

If you discover a security vulnerability, please open a GitHub issue with the label "security". Do not disclose security issues publicly until they have been addressed.

## Data Handling

- All candidate data is processed locally on CPU
- No data leaves the local environment
- No API calls are made to external services
- Cache files are stored locally in `outputs/`
- Release artifacts are verified via SHA256 hashes
