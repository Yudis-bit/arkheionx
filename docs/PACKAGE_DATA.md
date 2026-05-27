# Package Data

Arkheionx v2.0.0 keeps runtime data source-tree compatible for editable
installs. The installed console command resolves data from the working source
checkout.

Runtime data used by the CLI includes:

- `metadata/`
- `schemas/`
- `templates/`
- selected generated indexes such as `reports/search_index.md`

The old scripts still read the same repository paths. Package helpers in
`arkheionx.core.paths` provide:

- `project_root()`
- `package_root()`
- `resolve_runtime_data_path(...)`
- `resolve_input_path(...)`
- `resolve_output_path(...)`
- `is_editable_source_tree(...)`

## Future Wheel Path

A future non-editable wheel can populate `arkheionx/data/` and keep the same
helper API. v2.0.0 intentionally avoids a large data relocation so the source
tree, GitHub Action, old scripts, and editable CLI keep matching behavior.

## Safety

Runtime data is local metadata and templates only. It does not include secrets,
RPC configuration, remote targets, or live-chain settings.

