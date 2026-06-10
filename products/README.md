# Product Context Packs

One file per Number Pii product, loaded on demand and only when a session is
working on that product. This is the progressive-loading pattern used by
`INITIALIZE.md` and `WRITING.md`, applied to product knowledge: shared context
stays small, and products never compete for space in the always-loaded contract.

## Rules

- **Load a pack only when working on its product.** Never load packs wholesale.
- **One product, one file**, named in kebab-case: `products/<product-name>.md`.
- **Packs hold durable product facts**, not project state. Project state lives in
  the consuming project's `doc/` folder; a pack holds what stays true across
  projects (positioning, stack, environments, constraints, key decisions).
- **Product Neutrality applies.** A pack describes its product; it never ranks
  products. No pack may call its product flagship, primary, or priority.
- **The founders own pack content.** Agents update packs through normal PRs when
  durable facts change, and record the change in the pack's decision log.

## Creating a pack

Copy `_template.md` to `<product-name>.md` and fill it in. Keep a pack under
4KB; if it grows past that, move detail into the product's own repository and
link to it.

## Current packs

| Product | Pack |
|---|---|
| *(none yet)* | Copy `_template.md` to add the first one |
