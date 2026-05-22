# Metadata

This directory holds the canonical registry for Arkheionx Vault PoCs.

## Files

| File | Purpose |
|---|---|
| `schema.json` | JSON Schema (draft-07) for a registry entry. |
| `registry.json` | The registry itself. One entry per PoC. |

The registry is the single source of truth. The README registry table is
**generated** from it. Do not hand-edit the generated surface.

## Editing

1. Add or update an entry in `registry.json`.
2. Validate:

   ```sh
   python scripts/validate_metadata.py
   ```

3. Regenerate downstream artifacts:

   ```sh
   python scripts/generate_registry.py
   ```

   This rewrites the README's vulnerability registry section.

4. Commit `registry.json` and the regenerated files together.

## Schema

See [docs/METADATA_SCHEMA.md](../docs/METADATA_SCHEMA.md) for the field-by-field
specification, allowed enum values, and validation rules.
