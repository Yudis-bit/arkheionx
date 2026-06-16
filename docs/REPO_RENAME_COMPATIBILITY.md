# Repository Rename Compatibility

Public project name: **ArkheionX**.

Current public GitHub repository: `Yudis-bit/arkheionx`.

The public repository has been renamed to `Yudis-bit/arkheionx`.

New users should use <https://github.com/Yudis-bit/arkheionx>.

The old `DeFi-Exploit-PoCs` slug may remain in historical documents, archived
material, generated artifacts, migration notes, compatibility notes, or local
folder cleanup instructions.

## Expected GitHub behavior

GitHub repository renames usually redirect old repository URLs to the new slug.
That redirect is useful for compatibility, but active public docs, installers,
GitHub Action examples, workflow contact links, and SARIF metadata should use
the new canonical repository URL.

## Active references

Use `Yudis-bit/arkheionx` in:

- root `install.sh`;
- `site/public/install.sh`;
- GitHub Action examples under `docs/`;
- `.github/ISSUE_TEMPLATE/config.yml`;
- `scripts/github_surface_setup.sh`;
- generated website assets if they are tracked;
- PDFs or generated papers only in a deliberate publication pass.

Run:

```bash
grep -R "DeFi-Exploit-PoCs\|defi-exploit-pocs" -n \
  README.md docs site metadata templates .github scripts pyproject.toml
```

Do not treat old links inside explicitly historical files as current brand guidance.
