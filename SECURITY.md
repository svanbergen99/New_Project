# Security Policy — New_Project

New_Project is a public standalone-AI/runtime repository. Public means every committed file and reachable Git commit must be treated as publishable.

## AI/runtime boundary

- Do not commit API keys, model-provider secrets, tokens, private keys, private datasets, private prompts, production credentials, internal infrastructure details, or restricted model artifacts.
- Model weights, datasets, adapters, and third-party code must have reviewed provenance and licensing before use or redistribution.
- Training or runtime data must cross an explicit classification/review boundary before use.
- Operational agents may not self-grant tools, credentials, deployment access, filesystem scope, or security authority.
- Execution, deployment, model-loading, and security-sensitive changes must fail closed when provenance, integrity, authorization, or validation is uncertain.

## LCW repository standard — 2026-09-11

This repository is governed by the owner-approved LCW security standard.

- The human owner is the final authority.
- LCW is the independent guardian and emergency-control layer.
- Default deny applies to security-sensitive and privileged actions.
- Destructive, billing, permission, secret, authority-changing, or security-weakening actions require explicit owner approval.
- Operational agents may not grant themselves additional authority, bypass LCW, disable auditing, or modify the controls that constrain them.
- LCW enforcement credentials and control paths must remain outside operational-agent write authority.
- Security failures and unverifiable security state fail closed.
- Secrets must never be committed, logged, returned to clients, or included in model context.
- Only explicitly public material may be committed; uncertainty means the material must be treated as private and withheld.
- Production and security-sensitive changes require a reviewable pull request plus validated checks.
- Documentation is policy, not enforcement; controls must be implemented at repository, credential, deployment, network, runtime, and tool layers where applicable.

## GitHub assurance boundary

For repositories operated under GitHub Free, the required target is to use all security controls technically available to the current account. Any `100%` assurance statement is explicitly scoped to that available-control set and is not an absolute-security claim.

Provider-level protections that are unavailable under the current plan are not considered active merely because they are documented. Until stronger provider-enforced controls are available and independently tested, the human owner remains the compensating control by personally reviewing and merging security-sensitive pull requests after successful CI.

If required CI or equivalent validation is absent or failing, the repository is below the LCW standard for security-sensitive deployment and must fail closed.

## Incident rule

If secret, private, unlicensed, or otherwise restricted material is committed, stop affected deployment/publication paths, rotate credentials where applicable, preserve evidence, assess Git history and downstream copies, and verify the repaired state before resuming.
