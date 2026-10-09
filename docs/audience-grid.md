<!--
SPDX-FileCopyrightText: 2026 textmode-atlas contributors
SPDX-License-Identifier: CC-BY-4.0
-->
# Audience grid (v1)

[Version française](audience-grid.fr.md)

What the museum shows to whom. Adapted from PEGI, the European consensus on what is acceptable for protected audiences; not PEGI itself, which rates games and whose marks belong to it. Generated from [corpus/ratings/grid.yaml](../corpus/ratings/grid.yaml) by `tm corpus ratings`: edit the grid, not this page. Decided in [ADR 0020](adr/0020-the-audience-grid.md).

## Levels

| | Level | What it means |
| --- | --- | --- |
| <img src="../corpus/ratings/badges/level-3.svg" alt="Every audience" height="32"> | **Every audience** | Nothing on this grid. A work that has been reviewed and carries no descriptor. |
| <img src="../corpus/ratings/badges/level-7.svg" alt="7 and over" height="32"> | **7 and over** | Cartoon violence, images that may frighten young children. |
| <img src="../corpus/ratings/badges/level-12.svg" alt="12 and over" height="32"> | **12 and over** | Horror imagery, violence against fantasy figures, innuendo, mild swearing, alcohol, the warez scene. |
| <img src="../corpus/ratings/badges/level-16.svg" alt="16 and over" height="32"> | **16 and over** | Realistic violence and blood, erotic nudity, strong obscenities, illegal drugs, how-tos for illegal acts, hateful words shown without endorsement. |
| <img src="../corpus/ratings/badges/level-18.svg" alt="Adults only" height="32"> | **Adults only** | Gross violence, explicit sex, drug use glamorised, works that promote hatred (shown only with a curator's text). |
| <img src="../corpus/ratings/badges/level-withheld.svg" alt="Withheld" height="32"> | **Withheld** | Never shown or exported. Kept in the archive for a decision by the owner and the lawyer. |

## Descriptors

| Descriptor | <img src="../corpus/ratings/badges/level-7.svg" alt="7 and over" height="32"> | <img src="../corpus/ratings/badges/level-12.svg" alt="12 and over" height="32"> | <img src="../corpus/ratings/badges/level-16.svg" alt="16 and over" height="32"> | <img src="../corpus/ratings/badges/level-18.svg" alt="Adults only" height="32"> | <img src="../corpus/ratings/badges/level-withheld.svg" alt="Withheld" height="32"> |
| --- | --- | --- | --- | --- | --- |
| <img src="../corpus/ratings/badges/violence.svg" alt="Violence" height="32"> **Violence** | Implied or cartoon violence, without detail (a fight between fantasy figures). | Visible violence against fantasy creatures; unrealistic violence against people; weapons shown as a threat. | Realistic violence against people, wounds, blood. | Gross violence (gore, mutilation, torture), violence against the defenceless, killing glamorised. |  |
| <img src="../corpus/ratings/badges/fear.svg" alt="Fear" height="32"> **Fear** | Images that may frighten young children (skulls, monsters, darkness) in an unrealistic style. | Horror imagery (demons, the undead, occult symbols, disturbing faces). | Graphic horror (body horror, realistic disturbing images). |  |  |
| <img src="../corpus/ratings/badges/sexual.svg" alt="Sex and nudity" height="32"> **Sex and nudity** |  | Innuendo, suggestive poses, kissing; partial nudity that is not sexual. | Erotic nudity; sexual activity implied, not shown. | Explicit sexual activity or explicit genitals, between adults. | Any sexual depiction that involves or appears to involve a minor, drawn or not. |
| <img src="../corpus/ratings/badges/language.svg" alt="Language" height="32"> **Language** |  | Mild swearing and insults. | Strong obscenities, sexual insults. |  |  |
| <img src="../corpus/ratings/badges/drugs.svg" alt="Drugs" height="32"> **Drugs** |  | Alcohol or tobacco shown or named. | Illegal drugs shown or named. | Illegal drug use glamorised, or instructions for it. |  |
| <img src="../corpus/ratings/badges/discrimination.svg" alt="Discrimination" height="32"> **Discrimination** |  |  | Slurs or hate symbols shown in a work that does not endorse them (quoted, mocked, part of a scene's history). | A work that promotes hatred of people for who they are; shown only with a text written by a curator. | A work that would be unlawful to publish, even in an archive (incitement, denial of crimes against humanity; to verify with the lawyer). |
| <img src="../corpus/ratings/badges/crime.svg" alt="Crime" height="32"> **Crime** |  | The warez and cracking scene named or advertised (groups, couriers, elite boards), as history. | How-tos for illegal acts (carding, phreaking, intrusion). |  | Usable stolen data (card numbers, calling codes, passwords) or a private person's details. |
| <img src="../corpus/ratings/badges/real_people.svg" alt="Real people" height="32"> **Real people** |  | Caricature of a public figure. | Insulting or degrading depiction of an identifiable person, a scener's handle included. | Sexualised depiction of a public figure. | Sexualised or degrading depiction of a private person. |

## Notices

- <img src="../corpus/ratings/badges/flashing.svg" alt="Flashing" height="32"> **Flashing**: Blinking cells or fast redraws, which may affect photosensitive visitors. Playback can be paused, and reduced motion is honoured.

## Rules

1. A work's level is the highest level among its descriptors. A cartel can explain a work, never lower its level.
2. The grid rates what a work shows, in its time and its context, not the person who made it. A descriptor applies to a work, never to a person.
3. Every descriptor is an assertion with its author. A program may infer it; a named reviewer confirms or rejects it; the artist may declare it. Nothing is erased, so the history of a rating stays visible.
4. Until a person has reviewed it, a descriptor inferred by a program counts. A work no one has reviewed is "not rated yet" and is shown only where 16 is.
5. Levels are applied by the server when it exports and serves works, never by the page in the browser.
6. Anyone can ask for a work to be rated again, with the same form as for withdrawal.
