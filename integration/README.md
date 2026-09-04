# Integration Tests

Runs the SDK test suite against real Posit Connect instances. Each test class runs
against its own fresh Connect container, provisioned by the fixture in
`tests/posit/connect/conftest.py`.

## Prerequisites

- Docker
- uv
- A Posit Connect license file at `integration/license.lic`, or set
  `LICENSE=/path/to/file`. License files are gitignored; never commit one.

## Running

All commands below run from the repository root.

Use `-C integration` to target this directory's `Makefile` (it defines its own
`all` and per-version targets, distinct from the root `Makefile`):

```bash
make -C integration                  # latest Connect version
make -C integration 2025.10.0        # a specific version
make -C integration all              # every supported version
make -C integration -j 4 all         # ... in parallel
```

Standard pytest selection also works; set `CONNECT_VERSION` and `LICENSE`:

```bash
CONNECT_VERSION=2026.01.0 LICENSE=integration/license.lic uv run pytest integration/tests/posit/connect/test_groups.py -v
```
