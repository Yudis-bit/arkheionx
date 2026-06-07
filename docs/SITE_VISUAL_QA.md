# Site visual QA checklist

Manual visual QA for the Arkheionx website (`site/`). Run `npm run build` first;
preview with `npm run preview` and check each viewport.

## Viewports to test

- 390px (mobile)
- 768px (tablet portrait)
- 1024px (tablet landscape / small laptop)
- 1280px (desktop)
- 1440px (wide desktop)

## Pages to inspect

- `/` (home)
- `/docs`, `/docs/quickstart`, `/docs/how-it-works`, `/docs/cli-reference`
- `/docs/bug-bounty`, `/docs/pre-audit`, `/docs/v4`, `/docs/safety-model`
- `/docs/faq`, `/docs/troubleshooting`
- `/examples`, `/install`, `/roadmap`, `/releases`, `/security`

## Checklist (per page, per viewport)

- [ ] No clipped or cut-off headings (`clamp()` sizes scale down on mobile).
- [ ] No terminal/command output clipped — long lines scroll horizontally inside
      the block (`.ax-copy-shell pre` has `overflow-x: auto`), not the page.
- [ ] No unreadable card grids — process/step grids use `auto-fit minmax()` and
      never render as 5–7 narrow text columns on desktop.
- [ ] Copy buttons do not overlap command text (the `<pre>` reserves right padding).
- [ ] No horizontal page overflow except inside code blocks.
- [ ] All CTA links/buttons are visible and reachable.
- [ ] Safety boundary text is present and legible.
- [ ] Command blocks are readable and copyable.
- [ ] Cards stack to a single column on mobile and never squeeze on tablet.
- [ ] Body text line-height is comfortable; no text wraps one word per line.

## Known responsive rules

- Card/step grids: `repeat(auto-fit, minmax(min(100%, 200–260px), 1fr))`.
- Headings: `clamp()` with mobile floors.
- Terminals: `.ax-copy-shell pre { overflow-x: auto; white-space: pre }` with a
  right-padded copy button injected by `public/copy-command.js`.
- Global guard: `html, body { max-width: 100%; overflow-x: hidden }`.

This is a manual checklist. There is no automated visual-regression suite; the
`npm run build` must pass and the pages must be inspected at the viewports above
before a public deploy.
