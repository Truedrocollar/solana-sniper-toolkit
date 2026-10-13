# Security Policy

## Reporting a vulnerability

Email `security@<your-domain>` with a description, repro steps, and impact. Do not open a public issue for exploitable bugs. We aim to acknowledge within 72 hours.

## Scope

In scope:
- RPC endpoint handling and signature verification
- Wallet loader (`src/solana_sniper/services/wallet_loader.py`)
- Jito bundle submission and tip logic
- Rug-check heuristics (false negatives that let a honeypot through)

Out of scope:
- Losses from user-chosen snipe targets. This is a tool, not financial advice.
- Mainnet MEV outcomes. Sniping is adversarial by nature.

## Key handling

- Private keys are read from env or a local keypair file, never logged.
- `structlog` processors redact any field matching `(?i)secret|key|mnemonic|seed`.
- Never paste real keypairs into issues.

## Dependencies

We pin `solders`, `solana`, and `anchorpy`. Run `pip-audit` before cutting a release.