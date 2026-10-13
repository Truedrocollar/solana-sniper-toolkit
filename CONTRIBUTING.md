# Contributing to solana-sniper-toolkit

Thanks for wanting to push the tater forward. This repo is a modular Solana sniper stack: pool listeners, rug heuristics, Jito bundle submission, and per-DEX adapters. It is a hobbyist / research project maintained in public.

## Ground rules

- Target Python 3.11+. Type hints required on public functions.
- One feature = one module under `src/solana_sniper/`.
- Every new DEX adapter gets a fixture under `tests/fixtures/` and at least one unit test.
- No live mainnet keys in PRs. Ever. Use `.env.example` as the template.

## Local setup

```bash
git clone https://github.com/<you>/solana-sniper-toolkit
cd solana-sniper-toolkit
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp .env.example .env
pytest -q
```

## Adding a DEX adapter

1. Drop a new module in `src/solana_sniper/dex/` — subclass `BaseDex`.
2. Implement `parse_pool_event`, `build_buy_tx`, `build_sell_tx`.
3. Register it in `dex/__init__.py::REGISTRY`.
4. Add a fixture and a test.

## Style

- `ruff check .` and `ruff format .` must pass.
- `mypy src` must pass.
- Prefer `structlog` over `print`. Prefer `httpx.AsyncClient` over `requests`.

## PR checklist

- [ ] Tests added / updated
- [ ] `pytest -q` green
- [ ] `ruff check .` clean
- [ ] No secrets committed
- [ ] Changelog entry under `## Unreleased`

## Reporting bugs

Open an issue with: OS, Python version, RPC provider, DEX, and the exact command you ran. Paste the traceback.