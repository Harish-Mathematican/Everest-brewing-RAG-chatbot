# 🛡️ #Gyan Labs — Zero-Trust Security, SOC 2 & Data Governance

## Compliance & Governance Framework
**#Gyan Labs** adheres to stringent North American data privacy and zero-trust security standards, ensuring complete protection for enterprise RAG pipelines and proprietary AI model weights.

### Key Governance Policies:
1. **Zero-Trust Access Architecture:**
   - Every internal service request is cryptographically authenticated using **YubiKey 5C NFC hardware tokens** and mTLS (Mutual TLS 1.3).
   - No implicit trust is granted based on network location or IP subnet.

2. **Cross-Border Privacy Compliance:**
   - **Canada:** Full adherence to **PIPEDA** (Personal Information Protection and Electronic Documents Act) and Quebec Law 25.
   - **United States:** SOC 2 Type II compliance, California CCPA/CPRA, and NIST SP 800-207 guidelines.

3. **Data Loss Prevention (DLP) & Prompt Sanitization:**
   - All input documents and scraped web URLs undergo automated PII redaction (anonymizing phone numbers, social security/SIN numbers, and confidential API tokens) prior to vector embedding.
