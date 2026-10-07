<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# 0009. Show what the scene released freely, credit it, withdraw on request

- Status: Accepted
- Date: 2026-10-07
- Deciders: Nicolas Bridelance, who accepts the legal risk described below
- Supersedes: [0006](0006-display-requires-permission.md)

## Context

ADR 0006 showed a file only with its author's permission. Most authors of 1985–2000 works are
unreachable under their handles, so most records would have stayed without their work: a museum
of absences. The scene's own archives (16colo.rs, Demozoo, scene.org, textfiles.com) work the
other way: they distribute what the scene released, credit it, and withdraw on request, with
very little conflict in decades.

French law has no exception for this: displaying a protected work without consent is, in
principle, infringement, and a museum that selects and stages works acts as an editor, not as a
neutral host. Withdrawal on request limits the practical consequences; it does not make the
display lawful. The likelihood of a claim is low; the larger risk is reputational, if the scene
sees the museum as taking rather than keeping.

## Decision

A file is shown when its author allows it, or, failing that, when **all** of these hold:

1. **The scene released it for free distribution** and a scene archive still holds it
   (`Rights.scene_publication`: 16colo, Demozoo, scene.org or textfiles). Nothing commercial,
   nothing private, no personal Usenet material.
2. **Credit as signed**: handle, group and pack, and a link to the source archive, on every
   record that shows the file.
3. **"Is this your work? Withdraw or claim"**, visible on every record with how to do it.
   Withdrawal is immediate and asks for no justification (`privacy.withdrawn` → `none`).
4. **No commercial use and no generation** (invariant 9). Models trained on the works are not
   distributed; only their measurements and results are.
5. **The scene is told first**: 16colo and Demozoo are informed before the public opening (M3),
   as a courtesy, not to ask permission.

`ScenePublishedPolicy` is the default policy of `can_display()`. A lawyer is still consulted
before the move to scale (M4).

## Alternatives considered

- **Permission only (0006)**: lawful, but leaves most works unseen.
- **Show everything found, withdraw on request**: includes private and commercial material the
  scene never released.

## Consequences

- Ingestion must record where the scene published each work; without it, a work stays
  metadata-only.
- The work screen must show credit, source link and the withdraw / claim action; `tm export`
  must refuse a shown file without credit.
- Withdrawals must reach the public bucket and the CDN quickly (already in the spec).
