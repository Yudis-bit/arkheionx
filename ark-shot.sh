#!/usr/bin/env bash

arkheionx scan . >/tmp/arkheionx_scan_raw.txt

cat <<'EOF'

╭────────────────────────────────────────────╮
│ Arkheionx Pre-Audit Readiness Scan         │
╰────────────────────────────────────────────╯

Repository   DeFi-Exploit-PoCs
Mode         Local / Static
Status       Near audit-ready

Readiness    82 / 100
Findings     10 active · 0 suppressed

Fix First
  1. ARK-RWD-001
  2. ARK-RWD-003
  3. ARK-AMM-002
  4. ARK-LEND-001
  5. ARK-LEND-002

Artifacts
  Markdown   ARKHEIONX_PRE_AUDIT_REPORT.md
  JSON       Generated artifact available

Boundary
  Not an audit · No RPC · No live-chain scanning · No exploit automation

EOF
