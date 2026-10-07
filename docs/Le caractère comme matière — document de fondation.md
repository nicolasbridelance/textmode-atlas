# Musée numérique des arts du caractère — spécification d'implémentation

Oct 7, 2026 · @Nicolas

## Objet

Ce document spécifie comment construire le projet : une base de données, un pipeline d'ingestion et de rendu, une couche d'analyse et un site. Il reprend tout le périmètre de la vision initiale et fixe les choix techniques nécessaires pour commencer.

Le système se résume en une chaîne :

```
source → acquisition → hash → décodage en grille → features → rendus → API → site
```

Les choix marqués « proposé » sont des valeurs par défaut à confirmer. Les capacités des API tierces (16colo.rs, Demozoo) sont à vérifier avant de coder contre elles.

Le projet est dédié à celles et ceux qui ont fait la scène textmode. Cela se traduit par des règles concrètes de crédit, de pseudonymat et de retrait, décrites plus bas.

## Invariants

Neuf règles sont vérifiées par le code, pas seulement par convention.

| Règle | Mise en œuvre |
| --- | --- |
| Un original n'est jamais modifié | stockage adressé par SHA-256, bucket en écriture unique |
| Source, rendu et interprétation sont séparés | table `representation` avec un champ `level` obligatoire |
| Tout rendu est reproductible | recette JSON complète, test de déterminisme en CI |
| Toute relation a une origine | table `assertion` en ajout seul, champs `nature` et `asserted_by` obligatoires |
| Un calcul n'est jamais présenté comme un fait | contrainte SQL : `nature = 'inferred'` exige `asserted_by` de type `algo:` |
| Aucun fichier affiché ni joué sans droit | fonction `can_display()` appliquée par `tm export` et par l'API, jamais par le frontend ; elle couvre l'image comme le son |
| Aucun lien pseudo → état civil sans consentement | table `person` hors de l'API publique |
| Tout contenu généré par un modèle est marqué | `level = 'interpretation'` et `asserted_by = 'algo:…'` |
| Aucune œuvre n'est générée « à la manière de » | les modèles mesurent et prédisent ; une grille produite par un modèle n'est jamais rendue ni exportée (`tm export` refuse toute `representation` sans `sha256` d'artefact acquis) |

## Stack et dépôt

La stack proposée tient en sept composants, tous standards et remplaçables.

| Composant | Choix proposé | Rôle |
| --- | --- | --- |
| Base | PostgreSQL 16 + pgvector | modèle, assertions, droits, embeddings |
| Originaux et rendus | stockage objet compatible S3, clé = SHA-256 | fichiers, hors Git |
| Ingestion et analyse | Python 3.12, un CLI unique `tm` | connecteurs, décodeurs, features |
| Rendu ANSI, XBIN, ASCII | ansilove, version épinglée | PNG de conservation et profils |
| Rendu PETSCII, ATASCII, télétexte | moteurs maison à partir de la grille | un module par système |
| API | FastAPI, service minimal | formulaires, recherche, modération |
| Site | SvelteKit, lecteur ANSI en JavaScript | timeline, fiches, lecture temporisée |

Le dépôt garde l'arborescence initiale, avec quatre ajouts :

```
corpus/assertions/    exports versionnés des assertions documentées
corpus/profiles/      un fichier YAML par profil de rendu
corpus/collections/   un fichier YAML par collection
corpus/radios.yaml    stations partenaires : flux HTTPS, accord, date de vérification
```

Les quinze familles du corpus ne sont pas des tables. Chaque œuvre porte des facettes (`usage`, `system`, `scene`, `channel`, `function`), et une collection est une requête enregistrée :

```yaml
# corpus/collections/ansi-artscene.yaml
title: ANSI et artscene BBS
where:
  system: [ansi-cp437, xbin]
  channel: [bbs, artpack]
order_by: date_min
```

Une œuvre peut ainsi apparaître dans plusieurs collections, et en ajouter une ne demande aucune migration.

## Bibliothèques

Le détail du stack, couche par couche. Tout est libre et courant ; rien n'est exotique.

| Couche | Outils | Usage |
| --- | --- | --- |
| Socle Python | Python 3.12, `uv` (workspace et verrouillage) | un seul environnement pour `ingest`, `renderers`, `analysis` |
| CLI et modèles | Typer, Pydantic | commandes `tm`, validation des YAML et des recettes |
| Base | SQLAlchemy, Alembic, psycopg | schéma, migrations versionnées |
| Données tabulaires | PyArrow, Polars, DuckDB | grilles et features en Parquet, requêtes locales |
| Apprentissage | PyTorch, scikit-learn, umap-learn | modèle de grilles, stylométrie, projection 2D |
| Statistiques | lifelines (survie), ruptures (points de rupture), statsmodels | chantiers 4, 5 et 6 |
| API | FastAPI, Uvicorn | formulaires, recherche, modération |
| Site | SvelteKit, TypeScript, `pnpm`, export statique | pages, parcours, fiches |
| Langues | Paraglide (inlang) ; locale dans l'URL (`/` anglais, `/fr/` français) | interface et textes du visiteur, multilingues |
| Affichage des œuvres | Canvas 2D avec atlas de police bitmap | la grille est dessinée dans le navigateur, nette à toute échelle |
| Visualisations | D3 pour les échelles et axes, Canvas ou WebGL (regl) pour les nuages de points | les six vues |
| Son | Web Audio API ; flux Icecast d'une radio partenaire ; libopenmpt compilé en WebAssembly | échantillons du mode contemplatif, radio de la scène, modules des packs |
| Recherche | Pagefind (index statique), puis recherche par similarité via l'API | titre, auteur, groupe, pack ; « œuvres proches » |
| Orchestration | `just` et les commandes `tm` idempotentes | pas d'ordonnanceur tant que le volume ne l'exige pas |
| Local | Docker Compose : PostgreSQL + pgvector, Garage (stockage S3) | environnement de développement complet hors ligne |
| Notebooks | marimo (fichiers Python), DuckDB, Altair | recherche dans `research/`, sur les datasets construits |

Point notable : l'œuvre n'est pas servie en image. Le navigateur reçoit la grille (quelques kilo-octets) et la dessine lui-même. Les PNG de conservation servent au téléchargement, aux aperçus de partage et à l'embedding visuel.

## Architecture de production et hébergement

Le site public est statique. C'est le choix qui le rend rapide, peu coûteux et capable de durer : des fichiers derrière un CDN, sans base de données exposée.

```
            PRIVÉ                                   PUBLIC
  ┌──────────────────────────┐          ┌───────────────────────────┐
  │ PostgreSQL + pgvector    │  export  │ bucket public + CDN       │
  │ bucket des originaux     │ ───────► │  site statique            │
  │ jobs tm (conteneur)      │          │  grilles, PNG, JSON       │
  └──────────────────────────┘          └───────────────────────────┘
               ▲                                     │
               │        ┌──────────────────┐         │
               └────────│ API minimale     │◄────────┘
                        │ formulaires,     │
                        │ recherche, modér.│
                        └──────────────────┘
```

La commande `tm export` applique `can_display()` et ne copie vers le bucket public que ce qui peut être montré. Un retrait supprime l'objet, purge le cache du CDN et relance l'export de la fiche.

Hébergement cible, à partir de M4 : tout chez Scaleway, région Paris. Un seul fournisseur français simplifie le dossier RGPD.

| Besoin | Service | Remarque |
| --- | --- | --- |
| Originaux (privé) et fichiers publics | Object Storage, deux buckets | compatible S3 ; versionnement activé sur les originaux |
| Base | Managed Database for PostgreSQL | l'extension pgvector est proposée par le service ([Scaleway](https://www.scaleway.com/en/managed-postgresql-mysql/)) |
| API | Serverless Containers | s'éteint sans trafic |
| Jobs `tm` | Serverless Jobs, ou une instance lancée à la demande | même image que la CI, référencée par digest |
| CDN et DNS | Edge Services devant le bucket public | purge par chemin lors d'un retrait |
| Entraînement des modèles | instance GPU louée à l'heure | ponctuel ; rien de permanent |
| Infrastructure décrite en code | OpenTofu, dossier `infra/` | trois environnements : local, préproduction, production |

Alternatives : OVHcloud (français, offre équivalente), Hetzner (allemand, moins cher, moins de services gérés), ou une seule machine virtuelle avec Docker Compose pour démarrer. Les tarifs sont à chiffrer avant décision ; au volume du V0, le poste principal sera la base gérée.

Services annexes :

- **Mesure d'audience** sans cookie (Plausible ou équivalent auto-hébergé), pour suivre les quatre indicateurs de visite sans bandeau de consentement.
- **Connexion des modérateurs** par compte GitHub.
- **Surveillance** : sonde de disponibilité externe et alertes par e-mail.

Sauvegarde et pérennité :

- Les originaux existent en trois copies : bucket principal, bucket chez un second fournisseur, copie hors ligne.
- La base est sauvegardée chaque jour par le service géré, avec un export SQL hebdomadaire vers le second fournisseur.
- Le code est archivé par Software Heritage, et chaque version du jeu de métadonnées est déposée sur Zenodo avec un DOI.

## Datasets

La recherche et la data science ne lisent pas la base de production : elles lisent des **datasets** construits par `tm`, figés et versionnés.

- Un dataset est **défini** dans `datasets/<nom>/` (requête, colonnes, fiche descriptive `DATASHEET.md` sur le modèle des *Datasheets for Datasets*) et **construit** dans `datasets/build/`, hors Git, puis publié dans le stockage.
- Chaque build consigne la migration de la base, les versions des extracteurs, la requête et le SHA-256 de chaque fichier. Deux builds donnent des fichiers identiques à l'octet.
- Les découpes entraînement / test sont faites **par pack** et livrées avec le dataset.
- Chaque dataset publie son taux de couverture du corpus connu (`lost_item`).
- Contenu : métadonnées, assertions, features, embeddings (CC0). Les œuvres elles-mêmes n'y entrent que si `can_display()` l'autorise, et la fiche le dit.
- Chaque version publique est déposée sur Zenodo avec un DOI.

## Phasage de l'hébergement

L'hébergement monte en quatre paliers. Le code ne change pas d'un palier à l'autre : seules la destination de `tm export` et l'URL de base des fichiers changent.

| Palier | Jalons | Où tourne quoi | Contenu autorisé |
| --- | --- | --- | --- |
| 0. Développement | M1, M2 | GitHub Codespaces ou machine locale : PostgreSQL, Garage, site et API en Docker Compose | œuvres de test, packs téléchargés pour le travail |
| 1. Prototype public | M3 | GitHub Pages pour le site statique ; base toujours en Codespaces ou en local | œuvres de test et œuvres autorisées uniquement |
| 2. Passage à l'échelle | M4 | Pages pour le site ; bucket Scaleway + CDN pour grilles et PNG ; API minimale en conteneur ; PostgreSQL géré | selon `can_display()` |
| 3. Ouverture large | M5 | bascule complète chez l'hébergeur européen si le juriste le demande | selon `can_display()` |

Limites de GitHub Pages à garder en tête :

- **Pas de serveur.** Au palier 1, les demandes (revendiquer, corriger, retirer) passent par une adresse e-mail et des formulaires d'issues GitHub.
- **Volume.** La taille d'un site et la bande passante mensuelle sont plafonnées ; les valeurs exactes sont à vérifier dans la documentation GitHub. Le V0 tient largement, tout 16colo avec ses PNG non.
- **Retrait.** Supprimer une œuvre demande un redéploiement de quelques minutes.
- **Hébergeur américain.** Une plainte adressée à GitHub peut suspendre le site entier. C'est la raison du palier 3.

## Environnement de développement

Le développement se fait dans GitHub Codespaces, avec l'extension Claude Code. Le dépôt fournit un conteneur de développement qui démarre tout l'environnement en une commande.

```json
// .devcontainer/devcontainer.json (point de départ)
{
  "name": "textmode-atlas",
  "dockerComposeFile": ["../compose.yaml", "compose.dev.yaml"],
  "service": "dev",
  "workspaceFolder": "/workspaces/textmode-atlas",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "just setup",
  "forwardPorts": [5173, 8000, 5432, 9001],
  "customizations": {
    "vscode": {
      "extensions": ["anthropic.claude-code", "charliermarsh.ruff", "svelte.svelte-vscode"]
    }
  }
}
```

`just setup` installe `uv` et `pnpm`, résout les dépendances, applique les migrations et charge les artefacts de test. La même configuration fonctionne en local avec VS Code et Docker.

Trois règles propres à Codespaces :

- **Un codespace est jetable.** Il peut être supprimé après inactivité. Rien d'unique n'y vit : le schéma est dans les migrations, les métadonnées sont exportées dans `corpus/`, et les originaux se retéléchargent depuis leur source par `tm ingest`, qui vérifie les hash.
- **Les secrets** (clés du bucket, jetons d'API) sont des secrets Codespaces, jamais des fichiers du dépôt.
- **La CI utilise la même image** que le conteneur de développement, pour qu'un test vert en Codespaces le soit aussi sur GitHub Actions.

Un fichier `CLAUDE.md` à la racine donne à Claude Code les conventions du projet. Il reprend les neuf invariants, la liste des commandes `just` et `tm`, et quatre interdits : ne jamais commiter un fichier d'œuvre, ne jamais modifier un original, ne jamais écrire une assertion sans `nature` ni `asserted_by`, ne jamais contourner `can_display()`.

## Dépôt et licences

Le musée s'appelle **Musée numérique des arts du caractère** (*Digital Museum of Character Arts*). Le dépôt GitHub s'appelle `textmode-atlas` et le CLI `tm`.

### Langues

- **Le dépôt est en anglais** : code, commentaires, messages de la CLI et de la base, commits, documentation des contributeurs. La scène est internationale.
- **Le musée est multilingue à tous les niveaux.** Interface, cartels, parcours, titres des profils et des collections existent au moins en anglais et en français (`tm.i18n.REQUIRED_LOCALES`) ; d'autres langues s'ajoutent sans migration. Les cartels sont une table, une ligne par langue.
- Les titres des œuvres ne se traduisent pas : ils font partie de l'œuvre.
- Une traduction indique sa source. Une traduction automatique est signée `algo:` et affichée comme une interprétation.
- `README` et `TAKEDOWN` ont une version française à côté de l'anglaise, qui fait référence. Ce document de fondation et les rapports de `docs/research/` restent en français.

Quatre régimes de licence, déclarés fichier par fichier selon la convention REUSE (dossier `LICENSES/`, en-têtes SPDX).

| Contenu | Licence | Raison |
| --- | --- | --- |
| Code | Apache-2.0 | permissive, avec clause de brevets |
| Métadonnées, assertions, features, profils | CC0 1.0 | réutilisation sans condition ; renonce aussi au droit des bases de données |
| Textes : documentation, cartels, parcours | CC BY 4.0 | les auteurs restent crédités |
| Œuvres et témoignages | aucune licence accordée par le projet | ils appartiennent à leurs auteurs et ne sont pas dans le dépôt |

Le `README` énonce cette séparation dès le premier écran. Le dépôt contient aussi `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` et `TAKEDOWN.md`, ce dernier décrivant la procédure de retrait et l'adresse de contact.

## CI/CD et garanties de code

GitHub Actions exécute onze contrôles à chaque pull request. Tous sont bloquants.

| Domaine | Contrôle | Outil |
| --- | --- | --- |
| Python | style et format | `ruff` |
| Python | typage strict | `pyright` |
| Python | tests et couverture minimale | `pytest`, `pytest-cov` |
| Base | migrations sur un PostgreSQL vierge, puis tests des contraintes SQL | Alembic, service `postgres` du workflow |
| Corpus | validation des YAML de `profiles/`, `collections/` et de `radios.yaml` | JSON Schema |
| Rendu | déterminisme sur les artefacts de référence | `tm check --golden` |
| Web | style, typage, tests unitaires | `eslint`, `tsc`, `vitest` |
| Web | parcours de bout en bout et budget de performance | Playwright ; première œuvre en moins de 2 s |
| Licences | chaque fichier a sa licence | `reuse lint` |
| Sécurité | secrets et dépendances vulnérables | `gitleaks`, Dependabot |
| Dépôt | aucun fichier d'œuvre commité | script : extensions interdites, taille maximale |

Déploiement :

- Une fusion sur `main` construit l'image, la publie avec son digest et déploie en préproduction.
- Un tag `vX.Y.Z` déploie en production après approbation manuelle.
- Les migrations de base sont appliquées par un job dédié, avant le déploiement de l'API.
- Le pipeline de données ne tourne pas en CI. Ce sont des jobs lancés avec l'image publiée.

Garanties propres au projet :

- **Décodeurs robustes.** Tests par propriétés (`hypothesis`) : aucun flux d'octets ne fait planter un décodeur. Une entrée illisible produit une erreur classée.
- **Ingestion sûre.** Les archives sont extraites en bac à sable : chemins `../` refusés, taille et nombre de fichiers plafonnés.
- **Droits.** Le module `can_display()` est couvert à 100 % des branches, et `tm export` a un test qui vérifie qu'une œuvre retirée n'atteint jamais le bucket public.
- **Idempotence.** Chaque commande `tm` est exécutée deux fois en test ; l'état final doit être identique.
- **Fichiers de test.** Les artefacts de référence sont des œuvres créées pour le projet, sous CC0.
- **Branche protégée.** `main` exige une revue et une CI verte ; les dépendances sont verrouillées (`uv.lock`, `pnpm-lock.yaml`).
- **Reproductibilité.** L'image de conteneur fixe les versions d'ansilove et des polices ; son digest figure dans chaque recette de rendu.

## Scaffold

Le dépôt est un monorepo : un workspace `uv` pour le Python, `pnpm` pour le web.

```
gh repo create textmode-atlas --public --clone && cd textmode-atlas

# Python : un workspace, trois paquets
uv init --package ingest
uv init --package renderers
uv init --package analysis
uv add --dev ruff pyright pytest pytest-cov hypothesis reuse

# Web
npx sv create apps/museum

# Corpus, recherche, infrastructure
mkdir -p corpus/{schema,profiles,collections,assertions,rights,sources}
mkdir -p research docs exhibitions infra tests/golden LICENSES

# Environnement local
docker compose up -d          # PostgreSQL + pgvector, Garage
uv run alembic upgrade head   # crée le schéma
uv run tm --help
```

Arborescence de départ :

```
textmode-atlas/
├── apps/museum/            site SvelteKit
├── api/                    FastAPI : formulaires, recherche, modération
├── ingest/                 paquet tm : connecteurs, CLI, export
├── renderers/              décodeurs et moteurs de rendu
├── analysis/               features, embeddings, chantiers 1 à 6
├── corpus/                 schémas, profils, collections, radios, polices, assertions (CC0)
├── datasets/               définitions et fiches des datasets publiés (les builds sont hors Git)
├── migrations/             Alembic
├── exhibitions/            parcours (CC BY)
├── research/               hypothèses déposées, notebooks
├── docs/                   document de fondation ; docs/research/ : rapports préalables (M0)
├── infra/                  OpenTofu
├── tests/golden/           artefacts de référence (CC0)
├── .github/workflows/      ci.yml, deploy.yml
├── .devcontainer/          conteneur de développement (Codespaces)
├── CLAUDE.md               conventions pour Claude Code
├── compose.yaml
├── justfile
├── pyproject.toml          workspace uv
├── LICENSES/               Apache-2.0, CC0-1.0, CC-BY-4.0
└── README.md  CONTRIBUTING.md  SECURITY.md  TAKEDOWN.md
```

Les commandes exactes de `uv` et de SvelteKit évoluent ; elles sont à vérifier contre leur documentation au moment de l'exécution.

Écarts constatés au scaffold (2026-10-07) :

- **MinIO n'est plus distribué en image publique.** Il est remplacé par **Garage** (Deuxfleurs, association française), compatible S3. Garage ne gère pas le versionnement d'objets : l'écriture unique des originaux est garantie par `tm.storage.put_original`, qui n'écrit jamais sur une clé existante. Le versionnement reste activé côté Scaleway en production.
- **Garage n'a pas de console web.** Le bucket public est servi en lecture par son point d'accès web (port 3902), que le serveur de développement du site atteint par un proxy `/files`, comme le CDN en production.
- **SvelteKit 3** déclare ses variables d'environnement dans `src/env.ts` (`defineEnvVars`) et les expose par `$app/env/public`.
- Le site est créé par `sv create` avec les modules officiels : TypeScript, Prettier, ESLint, Vitest, Playwright, `adapter-static`, Paraglide.

## Schéma : œuvres et fichiers

L'entité `Work` unique devient quatre tables, parce qu'une œuvre a plusieurs versions et qu'une version existe en plusieurs fichiers.

```sql
create table work (
  id        uuid primary key,
  kind      text not null check (kind in ('single','set')),  -- set = pack, disquette, BBS
  title     text,
  usage     text[],   -- image, signature, emblem, world, place, interface, tool
  system    text[],   -- ansi-cp437, petscii, atascii, teletext, unicode...
  scene     text[],
  channel   text[],   -- bbs, artpack, usenet, broadcast, web, irc
  function  text[]
);

create table version (
  id         uuid primary key,
  work_id    uuid not null references work,
  label      text,                -- 'original', 'v1.0', '3.4.3'
  date_min   date,
  date_max   date,
  date_basis text,                -- sauce | pack | mtime | testimony
  behavior   text not null        -- static | animated | interactive | generative | performative
);

create table artifact (
  sha256      char(64) primary key,
  version_id  uuid references version,
  bytes       bigint not null,
  format      text,               -- ans, xb, asc, nfo, prg, tti, z5, txt, mod, xm, s3m, it
  charset     text,
  cols        int,
  rows        int,
  sauce       jsonb,              -- enregistrement SAUCE brut, si présent
  source_id   uuid references source,
  source_path text,
  acquired_at timestamptz not null
);

create table set_member (
  set_work_id uuid references work,
  sha256      char(64) references artifact,
  path        text not null,      -- chemin dans le ZIP
  position    int not null,       -- ordre éditorial conservé
  primary key (set_work_id, path)
);

create table representation (
  id            uuid primary key,
  sha256        char(64) references artifact,
  level         text not null check (level in ('authentic','conservation','interpretation')),
  profile       text,             -- nom d'un fichier de corpus/profiles/
  recipe        jsonb not null,
  output_sha256 char(64) not null
);

create table trace (
  id       uuid primary key,
  work_id  uuid references work,
  kind     text check (kind in ('log','capture','recording','testimony')),
  sha256   char(64) references artifact,
  note     text
);
```

Compléments au schéma, consignés lors de la première migration :

- `source` : origine d'une acquisition (`archive`, `api`, `deposit`, `manual`, `golden`), référencée par `artifact.source_id` mais absente du schéma initial.
- `decoding` : résultat du décodage de chaque artefact par chaque version de décodeur, une grille ou une erreur classée, jamais rien (contrainte SQL).
- `work.rights` et `work.privacy` : blocs JSON validés par `tm.rights`.
- `assertion.role` : précise `had_role` (artiste, codeur, sysop…).
- `lost_item`, `ticket` (file de modération) et `cartel` (textes du musée, une ligne par langue).
- Déclencheurs : `assertion` en ajout seul (seule la pose de `superseded_by` est permise), `artifact` immuable et jamais supprimé.
- Les tables d'embeddings attendent les chantiers : leur dimension dépend des modèles.

Trois points d'usage :

- Un artpack est un `work` de type `set`. Le ZIP est stocké entier comme artefact, et ses fichiers sont listés dans `set_member`.
- Le même fichier présent dans deux packs est un seul `artifact` et deux lignes `set_member`. La déduplication vient du hash.
- Une œuvre sans fichier survivant (un MUD, un BBS) existe par ses lignes `trace`.
- Un module musical (MOD, XM, S3M, IT) trouvé dans un pack est un `artifact` comme un autre, relié au pack par `set_member`. Il n'a pas de grille ; il est soumis à `can_display()` comme une image.

## Schéma : acteurs

Cinq tables décrivent qui a fait quoi, où et avec quoi. Le pseudonyme est l'entité publique ; la personne civile est une table séparée, jamais exposée.

```sql
create table identity (            -- le pseudonyme, tel que signé
  id      uuid primary key,
  handle  text not null,
  aliases text[]
);

create table person (              -- privé, hors API publique
  id           uuid primary key,
  identity_ids uuid[],
  consent      text not null default 'none'   -- none | self_declared
);

create table collective (          -- groupe : ACiD, iCE, Blocktronics...
  id   uuid primary key,
  name text not null
);

create table place (               -- BBS, newsgroup, FTP, canal IRC, demoparty
  id   uuid primary key,
  kind text not null,
  name text not null,
  meta jsonb                       -- indicatif, pays, sysop, URL d'archive
);

create table tool (                -- TheDraw, ACiDDraw, PabloDraw, Moebius...
  id       uuid primary key,
  name     text not null,
  version  text,
  released date,
  features text[]                  -- ex. ice_colors, wide_canvas, halfblocks
);
```

Les rôles (artiste, codeur, sysop, coursier, éditeur de pack, auteur de FAQ, archiviste) ne sont pas des colonnes. Ce sont des relations dans la table `assertion`, donc datées et sourcées comme le reste.

## Schéma : assertions

Tout le graphe tient dans une seule table en ajout seul. Une relation n'est jamais une clé étrangère nue : c'est une ligne qui dit qui l'affirme et sur quelle preuve.

```sql
create table assertion (
  id            uuid primary key,
  subject_type  text not null,     -- identity | work | collective | place | tool
  subject_id    uuid not null,
  relation      text not null,
  object_type   text not null,
  object_id     uuid not null,
  date_min      date,
  date_max      date,
  nature        text not null check (nature in ('documented','testified','inferred')),
  evidence      char(64) references artifact,   -- le fichier qui le prouve
  evidence_note text,
  confidence    real check (confidence between 0 and 1),
  asserted_by   text not null,     -- 'human:<login>' ou 'algo:<nom>@<version>'
  asserted_at   timestamptz not null default now(),
  superseded_by uuid references assertion,
  check (nature <> 'inferred' or asserted_by like 'algo:%'),
  check (nature <> 'documented' or evidence is not null)
);
```

Relations admises au départ : `created`, `member_of`, `collaborated_with`, `released_in`, `references`, `made_for`, `made_with`, `distributed_by`, `competed_with`, `moved_to`, `had_role`, `similar_to`.

Règles de fonctionnement :

- **Pas de mise à jour.** Une correction est une nouvelle ligne, et l'ancienne pointe vers elle par `superseded_by`.
- **Les contradictions restent.** Deux attributions concurrentes sont deux lignes actives. L'API renvoie les deux.
- **Trois vues SQL** (`edge_documented`, `edge_testified`, `edge_inferred`) alimentent le site, qui les affiche avec trois styles distincts.
- **Extraction automatique.** Les listes de membres et crédits des packs sont analysés par script. Le résultat entre en `documented`, avec le hash du fichier NFO comme preuve et une relecture humaine par échantillon.

## Pipeline de rendu

Tout part d'un format intermédiaire unique, la grille, produite une fois par artefact.

**Étape 1, décodage.** Un décodeur par format lit les octets et écrit `grid.parquet` : une ligne par cellule, avec `row`, `col`, `codepoint`, `fg`, `bg`, `blink`, et `t` (rang de l'octet qui a écrit la cellule, pour rejouer l'apparition). Décodeurs du V0 : ANSI/CP437, ASCII brut, XBIN. L'enregistrement SAUCE (128 derniers octets) est lu à part et stocké dans `artifact.sauce`.

**Limite du modèle de grille.** La grille suppose une police à chasse fixe. C'est vrai pour l'ANSI, le PETSCII, l'ATASCII, le télétexte et le Minitel, mais pas pour l'art AA japonais, composé pour une police proportionnelle (MS P Gothic) : la position d'un caractère y dépend de la largeur de ceux qui le précèdent. Ces œuvres sont stockées comme texte avec leur police de référence, rendues par un moteur à métrique proportionnelle, et n'entrent que dans les mesures qui ne supposent pas de grille (histogrammes de glyphes, dimensions en pixels). La décision est consignée ici pour qu'aucun décodeur ne force une grille fausse.

**Étape 2, rendu.** Un profil YAML fixe les paramètres d'affichage :

```yaml
# corpus/profiles/pc-vga-bbs-1994.yaml
grid: 80x25
cell: 9x16
font: { file: ibm_vga_9x16.fnt, sha256: "..." }
high_bg: blink            # ou ice
pixel_aspect: 1.35        # 720x400 affiché en 4:3
baud: 2400
sources: ["<référence matérielle>"]
```

```
tm render <sha256> --profile pc-vga-bbs-1994     # niveau authentic
tm render <sha256> --level conservation --scale 4 # entier, sans interpolation
```

Il existe plusieurs profils par système (carte, police, clignotement ou couleurs iCE, débit). Le site permet de passer de l'un à l'autre ; aucun n'est déclaré « le vrai ».

**Étape 3, recette.** Chaque rendu écrit sa recette dans `representation.recipe` :

```json
{
  "renderer": "ansilove", "renderer_version": "<x.y.z>",
  "container_digest": "sha256:...",
  "profile": "pc-vga-bbs-1994", "font_sha256": "...",
  "scale": 4, "interpolation": "none"
}
```

**Test de déterminisme.** Un jeu de 50 artefacts de référence est rendu à chaque build. Les `output_sha256` doivent être identiques, sinon la CI échoue.

**Lecture temporisée (mode contemplatif).** Elle se fait dans le navigateur, sans vidéo. Le lecteur JavaScript rejoue le flux d'octets à `baud / 10` caractères par seconde, soit 240 par seconde à 2400 bauds. Les sons sont des échantillons déclenchés par le lecteur. L'écran affiche titre, auteur, groupe, année, dimensions et encodage, tirés de la base.

## Pipeline d'analyse

Les mesures sont calculées sur la grille, pas sur les pixels. Elles sont stockées dans `features.parquet`, avec pour clé le hash de l'artefact et la version de l'extracteur.

| Famille | Mesures | Calcul |
| --- | --- | --- |
| Géométrie | `cols`, `rows`, `fill_ratio`, `center_of_mass`, `symmetry_h`, `symmetry_v` | cellules non vides sur total ; corrélation de la grille avec son miroir |
| Glyphes | `glyph_hist`, `glyph_entropy`, `class_ratio`, `bigram_top` | histogramme des codepoints ; entropie de Shannon ; parts par classe (blocs, demi-blocs, ombrages, filets, alphanumérique, ponctuation) |
| Couleur | `n_colors`, `fg_hist`, `bg_hist`, `high_bg_ratio`, `fg_bg_pairs` | comptages sur `fg` et `bg` ; part des cellules à fond intense |
| Séquence | `cursor_jumps`, `draw_order` | à partir de `t` : dessin linéaire ou par zones |

Trois embeddings sont stockés séparément dans pgvector :

- `emb_symbolic` : vecteur dérivé des histogrammes et n-grammes de la grille ;
- `emb_visual` : modèle de vision appliqué au rendu de conservation ;
- `emb_meta` : modèle de texte appliqué au titre, aux crédits et au NFO.

Avant usage, `emb_visual` est évalué sur une tâche simple : retrouver l'auteur ou le groupe d'une œuvre sur un échantillon étiqueté. S'il ne fait pas mieux que `emb_symbolic`, il n'entre pas dans les calculs de style.

Les résultats dérivés entrent dans la table `assertion` en `inferred` : voisinages (`similar_to`), clusters, scores d'atypie. Quatre garde-fous sont codés dans les requêtes :

1. **Antériorité.** « A précède B » n'est émis que si `A.date_max < B.date_min`.
2. **Effet d'outil.** Toute nouveauté formelle est croisée avec `tool.released` et `tool.features` avant d'être attribuée à un artiste.
3. **Lacunes.** Une table `lost_item` recense packs et BBS connus mais absents. Chaque statistique publie son taux de couverture.
4. **Retour terrain.** Chaque résultat publié a une page avec données, code et un formulaire de réponse. Les réponses entrent en `testified`.

La timeline du site lit un fichier précalculé (`timeline.json`) : par œuvre, une date, une position 2D issue d'une projection des embeddings et un identifiant de cluster. Les trois canons sont trois listes : `historical` (citations et classements d'époque), `computational` (scores), `curatorial` (sélections signées).

Les entretiens avec les anciens de la scène sont stockés comme `trace` de type `testimony`, avec transcription et accord écrit. Ils sont à lancer tôt : c'est la seule donnée qui ne se retrouvera dans aucune archive.

## Programme de recherche

Six chantiers, chacun avec une méthode établie et un test qui peut échouer.

| Chantier | Méthode | Test de validité |
| --- | --- | --- |
| 1. Représenter le style | modèle auto-supervisé sur les grilles : prédire des cellules masquées (glyphe, `fg`, `bg`) | l'embedding retrouve l'auteur et le groupe d'œuvres jamais vues, mieux qu'un histogramme de glyphes |
| 2. Attribuer et dédoublonner | stylométrie : probabilité calibrée d'auteur pour les œuvres non signées, détection d'alias | précision mesurée sur des œuvres signées dont on masque la signature |
| 3. Mesurer la nouveauté | distance de chaque œuvre à ce qui la précède (nouveauté) et à ce qui la suit (persistance) ; résonance = écart entre les deux, d'après Barron et al., PNAS 2018 | les œuvres citées comme marquantes à l'époque ont une résonance supérieure à un tirage au hasard |
| 4. Suivre la diffusion | détecteurs de techniques (dégradés ░▒▓, demi-blocs, couleurs iCE, styles de lettrage), puis analyse de survie de l'adoption par groupe | la proximité dans le réseau prédit l'adoption après contrôle de la date de sortie des outils |
| 5. Effet des transferts | différence de différences : style du groupe d'accueil avant et après l'arrivée d'un artiste, contre des groupes témoins | pas d'effet avant la date du transfert (tendances parallèles) |
| 6. Ruptures et convergences | détection de points de rupture sur les distributions mensuelles ; distance PC / Amiga par année | les ruptures détectées résistent au rééchantillonnage par pack |

Quatre règles de méthode s'appliquent à tous :

- **Découpe par pack.** Les jeux d'entraînement et de test ne partagent jamais un pack, sinon les logos et gabarits communs faussent les scores.
- **Modèle nul.** Chaque résultat est comparé au même calcul sur des dates ou des étiquettes permutées.
- **Incertitude.** Les intervalles viennent d'un rééchantillonnage par pack, et chaque chiffre publie son taux de couverture du corpus connu.
- **Questions écrites d'avance.** Les hypothèses sont déposées dans `research/` avant de regarder les données.

Le canon computationnel est le classement par résonance du chantier 3. Il est comparé au canon historique par corrélation de rangs, et les écarts les plus forts sont renvoyés aux témoins.

## Vues

Six écrans de visualisation, tous atteints depuis une œuvre et jamais présentés comme page d'accueil.

| Vue | Ce qu'elle montre | Données | Interaction |
| --- | --- | --- | --- |
| Carte des styles dans le temps | un point par œuvre, date en abscisse, position de style en ordonnée ; une technique apparaît puis se répand | `timeline.json` | curseur temporel, surbrillance d'une technique, repère « vous êtes ici » |
| Mémoire contre calcul | notoriété d'époque en abscisse, résonance calculée en ordonnée | canons `historical` et `computational` | clic sur un quadrant : liste des œuvres peu citées mais très reprises |
| Calques d'analyse | l'œuvre elle-même, recouverte par classes de glyphes, palette ou ordre de dessin | `grid.parquet`, `features.parquet` | bascule des calques, relecture du tracé |
| Flux artistes–groupes | diagramme alluvial par année : arrivées, départs, scissions | assertions `member_of`, `moved_to` | clic sur un flux : les œuvres avant et après le transfert |
| Courbes d'adoption | pour une technique, une courbe par groupe, sur le même axe de temps | chantier 4 | choix de la technique, marqueur de sortie des outils |
| Carte des lacunes | par année et par scène, ce qui est conservé et ce qui est connu mais perdu | `lost_item` | appel à contribution sur chaque case vide |

Règles communes : les relations calculées sont dessinées en pointillé, les relations documentées en trait plein. Chaque vue a un lien « méthode » vers le code et les données.

## Expérience du visiteur

Le projet a un avantage que les musées de peinture en ligne n'ont pas : ces œuvres sont nées pour l'écran. Un ANSI affiché au pixel près n'est pas une reproduction, c'est l'œuvre. L'interface doit donc s'effacer devant elle.

Les musées numériques échouent le plus souvent pour quatre raisons : ils imitent un bâtiment (couloirs 3D), ils ouvrent sur une grille de vignettes avec filtres, ils noient l'œuvre sous le texte, et ils ne proposent aucune suite. Les règles ci-dessous répondent à chacune.

**Arriver**

- La page d'entrée est une œuvre en plein écran, pas un menu. Elle est affichée en moins de deux secondes. Elle est tirée parmi les œuvres que `can_display()` autorise à montrer, comme l'œuvre du jour.
- Aucun compte, aucune fenêtre modale, aucun tutoriel. L'aide tient sur une touche (`?`).
- Le son est coupé par défaut et s'active d'une touche (`s`). Il joue alors la radio de la scène, décrite plus bas.

**Regarder**

- Une seule œuvre à la fois, à l'échelle entière, sur fond noir.
- Le cartel fait cinq lignes. Le reste s'ouvre par niveaux : contexte, analyse, octets.
- Les œuvres longues se font défiler. Un ANSI de 500 lignes est un format natif du défilement ; c'est le geste d'origine.
- Le zoom descend jusqu'à la cellule, pour voir comment c'est fait.
- Sur téléphone, une œuvre de 80 colonnes (720 pixels à l'échelle 1) ne tient pas à l'échelle entière. Elle s'affiche en pleine largeur, redessinée depuis la grille avec la police bitmap la plus proche de la taille de cellule obtenue, jamais par réduction d'une image. Un pincement ramène à l'échelle entière avec défilement horizontal.

**Continuer**

- Chaque œuvre propose trois à cinq sorties calculées depuis le graphe : la suivante du pack, une autre du même artiste, la plus proche en style, la réponse d'un groupe rival, ce qui sortait ailleurs le même mois.
- Tout se fait au clavier (flèches, espace, une lettre par sortie) ou au balayage sur mobile.
- Les fichiers pèsent quelques kilo-octets : les sorties sont préchargées, la transition est instantanée.

**Prendre du recul**

L'entrée est une œuvre, et c'est un choix assumé contre la recommandation courante de l'« aperçu d'abord » (Whitelaw, interfaces généreuses). L'aperçu existe, mais il est à une touche (`m`) de n'importe quelle œuvre : la carte des styles, où la position de l'œuvre courante est marquée. Une salle des archives, index à facettes (système, année, groupe, pack, outil), sert les chercheurs et les visiteurs qui savent ce qu'ils cherchent. Ni l'une ni l'autre n'est la page d'entrée.

**Le son**

La scène a ses propres radios en ligne. Le musée s'appuie sur elles d'abord, et ne joue la musique d'une œuvre que plus tard.

| Mode | Source | Quand |
| --- | --- | --- |
| Radio de la scène | flux Icecast d'une station partenaire (candidates : Nectarine, BitJam, SLAY Radio, Ericade, Kohina), avec son nom et un lien bien visibles | dès M3, pour la visite libre |
| Musique de l'œuvre | modules du pack ou du groupe, joués dans le navigateur par libopenmpt (WebAssembly) | M5, pour les œuvres dont les droits sont réglés |

Règles :

- **Accord préalable.** Le flux consomme la bande passante d'une station tenue par des bénévoles. Chaque station est contactée avant d'être branchée ; sans réponse favorable, elle n'est pas utilisée.
- **HTTPS obligatoire.** Une page en HTTPS ne lit pas un flux HTTP. Seuls les flux HTTPS vérifiés entrent dans la liste, qui vit dans `corpus/radios.yaml` avec la date de vérification.
- **Une seule source à la fois.** La radio, les échantillons du mode contemplatif et la musique d'une œuvre s'excluent ; démarrer l'un coupe l'autre.
- **Le lien œuvre–musique, quand il existe.** Si la station publie le titre en cours (métadonnées Icecast, file de Nectarine) et que l'auteur ou le groupe est dans la base, le lecteur propose une sortie : « œuvres de ce groupe ». Sinon la radio reste une ambiance, présentée comme telle.
- **Pas de copie.** Le musée ne stocke ni ne relaie aucun flux. Les modules du mode 2 sont des artefacts soumis à `can_display()`.

**Accessibilité**

Une œuvre dessinée dans un canvas est muette pour un lecteur d'écran, et la lire caractère par caractère serait du bruit. Le canvas est donc masqué aux technologies d'assistance ; le cartel, en HTML, porte le titre, l'auteur, la date et une description courte. Les textes lisibles d'une œuvre (lettrages, NFO, crédits) sont extraits de la grille et proposés à part. Les descriptions écrites par une personne sont signées ; celles produites par un modèle sont marquées comme interprétations. L'interface vise le niveau AA des WCAG 2.1, vérifié par `axe` dans les tests Playwright.

**Ce qui donne envie de rester**

Quatre ressorts, tous fondés sur la curiosité et aucun sur la contrainte.

| Ressort | Mise en œuvre |
| --- | --- |
| Anticipation | l'œuvre se dessine ligne à ligne à vitesse de modem ; on devine avant de voir. Vitesse réglable, espace pour afficher d'un coup |
| Découverte | les sorties mènent toujours ailleurs ; une touche « au hasard » ; une œuvre du jour, la même pour tous |
| Collection | le visiteur compose son propre pack : une sélection ordonnée, avec son `FILE_ID.DIZ`, partageable par lien |
| Achèvement | des parcours de 12 à 20 œuvres, 5 à 8 minutes, écrits par une personne nommée, avec un début et une fin |

Sont exclus : fil infini, notifications, badges, points, séries de jours consécutifs.

Sites à étudier avant le prototype : Radio Garden (errance sans barre de recherche, récompense immédiate), The Public Domain Review (une voix éditoriale assumée), Rijksstudio (le visiteur compose sa propre sélection, proche du pack personnel), et les prototypes de *slow looking* de Cogapp.

**La trace de la visite.** Le chemin parcouru se dessine sur la carte des styles. C'est le lien entre la promenade et les données : le visiteur voit où il est allé et ce qu'il n'a pas encore vu.

**Validation.** L'écran d'œuvre et ses sorties sont prototypés en premier, avant toute visualisation, et testés sur cinq personnes extérieures à la scène, dont deux sur téléphone. Quatre mesures : délai avant la première œuvre, nombre d'œuvres vues par visite, part des parcours terminés, retour dans les sept jours.

## Droits et vie privée

Les droits sont appliqués à l'export et par l'API, à partir de deux blocs par œuvre. Le bloc `rights` du schéma initial est repris tel quel ; un bloc `privacy` s'y ajoute.

```yaml
privacy:
  person_link: private          # public seulement si person.consent = self_declared
  mask_real_names: true         # noms et adresses e-mail des posts Usenet
  sensitive_membership: period_source_only   # scène warez
  withdrawn: false
```

L'affichage est décidé par une fonction unique :

```python
def can_display(work) -> str:
    if work.privacy.withdrawn:
        return "none"                 # fiche masquée
    if work.rights.permission.display:
        return "file"                 # fichier et rendus
    if policy.allows(work):           # politique écrite, validée par un juriste ;
        return "file"                 # renvoie False tant qu'elle ne l'est pas
    return "metadata"                 # fiche, relations, lien vers l'archive source
```

Aucun fichier n'est copié vers le bucket public quand le résultat est `metadata` ou `none`. Les mesures et relations restent consultables dans le cas `metadata`.

Quatre actions sont disponibles sur chaque fiche. Chacune crée un ticket dans une file de modération.

| Action | Effet |
| --- | --- |
| Revendiquer | vérification, puis `person.consent = self_declared` si la personne le souhaite |
| Corriger | nouvelle ligne `assertion`, l'ancienne est marquée remplacée |
| Témoigner | nouvelle `trace` de type `testimony` |
| Retirer | `withdrawn = true` immédiatement, sans justification demandée |

Le code est publié sous licence libre et les métadonnées sous licence ouverte. Les corrections d'attribution sont renvoyées aux archives sources.

### Stratégie juridique

Le rapport préalable ([docs/research/03_juridique.md](research/03_juridique.md)) classe les usages par risque. Le projet en tire la ligne suivante.

| Usage | Risque | Position du projet |
| --- | --- | --- |
| Archiver (copies privées) | faible | bucket privé, aucun accès public |
| Analyser (mesures, embeddings, graphe) | faible à modéré | exception de fouille de textes et de données (art. L. 122-5-3 CPI), au plus solide si la structure porteuse est un organisme de recherche ; les résultats sont publiés, pas le corpus |
| Afficher ou faire écouter | élevé | voir ci-dessous |
| Publier des dérivés (génération « à la manière de ») | ligne rouge | interdit par invariant |

**L'affichage est la question qui conditionne tout le reste.** Le rapport recommande le statut d'hébergeur (LCEN, DSA), qui protège jusqu'à notification. Ce bouclier ne couvre que ce que des tiers déposent, dans un rôle neutre et passif. Or le musée ingère lui-même ses sources, écrit des parcours, choisit l'œuvre du jour et calcule des sorties : c'est un travail d'éditeur, et la requalification est probable pour tout ce que `tm ingest` a rapatrié. Le statut d'hébergeur ne vaut donc que pour les dépôts faits par les auteurs ou par des archivistes, sous des conditions d'utilisation qui leur font accorder une licence non exclusive.

L'affichage suit donc trois voies, dans cet ordre :

1. **La permission.** La scène est vivante : beaucoup d'artistes et de groupes sont joignables. Une campagne de prise de contact commence en M0 et ne s'arrête pas. Un artiste qui revendique ses œuvres peut accorder l'affichage en un geste ; c'est aussi la meilleure façon d'entrer dans la communauté.
2. **Le dépôt.** Un auteur ou un archiviste verse lui-même des fichiers ; le musée agit alors en hébergeur, avec procédure de retrait.
3. **La fiche sans fichier.** Pour tout le reste, `can_display()` renvoie `metadata` : cartel, mesures, relations et lien vers l'archive source (16colo.rs, Demozoo). L'œuvre existe dans le musée, et on la voit chez ceux qui l'hébergent déjà.

`policy.allows()` renvoie `False` tant qu'une règle écrite n'a pas été validée par un juriste. Le site doit être beau même quand une majorité de fiches est en `metadata` ; c'est une contrainte de conception, pas un cas d'erreur.

Questions à poser au juriste, en plus des dix du rapport :

- La curation (parcours, œuvre du jour, sorties calculées) fait-elle perdre le statut d'hébergeur pour les dépôts de tiers, ou seulement pour les contenus ingérés par le projet ?
- Intégrer dans le lecteur du musée le flux d'une radio tierce est-il une simple mise en lien au sens de la jurisprudence européenne (Svensson, BestWater), ou une communication au public propre au musée ?
- La règle `policy.allows()` pour les œuvres orphelines, le traitement des pseudonymes au regard du RGPD (registre, article 89), et la réutilisation des métadonnées de Demozoo (droit des producteurs de bases de données).

## Jalons

Six jalons, chacun avec un livrable et un critère de sortie vérifiable. Le périmètre complet est conservé ; seul l'ordre est fixé.

| Jalon | Livrable | Critère de sortie |
| --- | --- | --- |
| M0 Cadrage | contacts pris avec 16colo.rs, Demozoo, IF Archive et les radios de la scène ; capacités d'API et flux HTTPS vérifiés ; premiers contacts avec des artistes pour la permission d'affichage | une note par source : accès, limites, conditions ; `corpus/radios.yaml` à jour |
| M1 Test du schéma | environ 180 objets (12 par famille) saisis à la main, sans rendu | chaque objet entre dans le schéma sans champ libre ; les modifications du schéma sont consignées |
| M2 Chaîne ANSI | `tm ingest`, `tm decode`, `tm render`, `tm features` sur 20 packs | test de déterminisme vert ; 100 % des fichiers ont une grille ou une erreur classée |
| M3 Site minimal | fiche d'œuvre, bascule de profils, lecture temporisée, timeline, radio de la scène | une œuvre consultable de la source à l'analyse ; `can_display()` couvert par des tests ; le parcours tient sur téléphone |
| M4 Passage à l'échelle | tout 16colo en métadonnées ; extraction des crédits depuis les NFO | taux de couverture publié ; précision de l'extraction mesurée sur 200 lignes relues |
| M5 Extensions | Usenet, demoscene, PETSCII et ATASCII, télétexte, Minitel, AA japonais, FAQ, jeux ; musique des œuvres | un décodeur, un profil et une collection par système ajouté ; modules joués seulement pour les œuvres autorisées |

M1 et M2 peuvent avancer en parallèle. Le prototype de l'écran d'œuvre commence dès M2, sur les artefacts de référence (CC0) et les premières œuvres autorisées, sans attendre le reste de M3. Les cinq premiers entretiens se font pendant M2 et M3.

## Parcours d'un pack, de bout en bout

Voici ce que M2 doit permettre d'exécuter sur un artpack.

```
tm ingest sixteen-colors --pack <nom>
    # télécharge le ZIP, calcule les SHA-256, stocke le ZIP et chaque fichier,
    # crée work(kind=set), set_member, artifact, lit les enregistrements SAUCE

tm decode --pack <nom>
    # écrit grid.parquet par artefact ; les formats inconnus sont listés, pas ignorés

tm credits --pack <nom>
    # analyse NFO, FILE_ID.DIZ et liste de membres
    # crée identity, collective et les assertions 'documented' avec leur preuve

tm features --pack <nom>
    # écrit features.parquet et les embeddings

tm render --pack <nom> --level conservation --scale 4
tm render --pack <nom> --profile pc-vga-bbs-1994
    # écrit les PNG et les recettes dans representation

tm check --pack <nom>
    # vérifie hash, recettes, contraintes SQL et droits
```

Chaque commande est relançable sans effet de bord : une clé déjà présente n'est pas réécrite.

Décisions à prendre avant M0 :

- [x] le nom : Musée numérique des arts du caractère, dépôt `textmode-atlas`
- [x] les licences : Apache-2.0, CC0, CC BY 4.0 (à confirmer par le juriste)
- [ ] la structure porteuse (association, laboratoire, fondation) ; proposé : association loi 1901 dont l'objet statutaire est la recherche et la conservation, pour relever de l'exception de fouille des organismes de recherche
- [ ] l'hébergeur : Scaleway proposé, à confirmer après chiffrage
- [ ] le nom de domaine
- [ ] le juriste qui valide la politique d'affichage
- [ ] la ou les radios partenaires

## Recherches préalables

Quatre requêtes à lancer dans Gemini Deep Research pendant M0. Chacune se colle telle quelle. La première vise explicitement ce que le projet n'a pas encore vu.

**1. Angles morts et état de l'art**

```
Je prépare un musée numérique et une base de recherche sur l'art fait de
caractères (ASCII, ANSI, PETSCII, ATASCII, télétexte, Minitel, NFO, roguelikes,
MUD, fiction interactive, art Unicode de terminal).
Recense tout ce qui existe déjà et tout ce que cette liste oublie :
- scènes non occidentales et non anglophones : art Shift_JIS et AA japonais,
  BBS taïwanais et coréens, pseudographiques soviétiques et FidoNet russe,
  vidéotex hors Europe (Telidon, NAPLPS, CAPTAIN), Amérique latine ;
- pratiques voisines : RTTY art des radioamateurs, art braille, machine à écrire,
  SMS, sous-titres, enseignes à caractères, tout autre usage graphique du texte ;
- archives, collections de musées, projets de préservation, jeux de données ;
- travaux universitaires, livres, documentaires, entretiens déjà publiés ;
- communautés actives aujourd'hui, événements, personnes ressources.
Consulte des sources en anglais, japonais, allemand, russe et chinois.
Rends : un tableau par source (URL, volume estimé, format, licence, accès par
API ou non), puis une liste « ce que votre périmètre ne mentionne pas »,
classée par importance, avec une phrase de justification par ligne.
```

**2. Méthodes computationnelles**

```
Quelles méthodes quantitatives ont été utilisées pour étudier l'histoire d'une
culture visuelle ou d'une scène créative à partir d'un grand corpus ?
Couvre : cultural analytics, histoire de l'art computationnelle, stylométrie
visuelle, mesures de nouveauté et de résonance (Barron et al. 2018 et suites),
diffusion des innovations dans des réseaux de créateurs, études de la demoscene,
et tout travail de machine learning portant sur l'ASCII ou l'ANSI art.
Pour chaque méthode : article de référence, données requises, limites connues,
critiques publiées, code ou jeu de données disponible.
Rends : 20 lectures prioritaires classées, les 5 pièges méthodologiques les plus
documentés (biais de survie, datation, fuite entre entraînement et test), et les
méthodes transposables à des grilles de caractères colorés.
```

**3. Cadre juridique**

```
Un projet basé en France veut archiver, analyser et afficher des œuvres
numériques des années 1985-2000, souvent pseudonymes et sans ayant droit
identifiable (artpacks ANSI, fichiers NFO, posts Usenet).
Analyse : le régime des œuvres orphelines (directive 2012/28/UE), les exceptions
de fouille de textes et de données (directive 2019/790, articles 3 et 4, et leur
transposition française), l'exception pour les institutions du patrimoine
culturel, le RGPD appliqué aux pseudonymes et aux noms dans les posts Usenet.
Compare avec les pratiques d'Internet Archive, 16colo.rs, Demozoo et textfiles.com
(politiques de retrait, contentieux connus).
Rends : une matrice de risque par usage (archiver, analyser, afficher, publier
des dérivés), les statuts juridiques qui ouvrent le plus d'exceptions, et dix
questions à poser à un avocat.
```

**4. Muséographie numérique**

```
Pourquoi la plupart des musées et expositions en ligne sont-ils désagréables,
et qu'est-ce qui fonctionne réellement ?
Couvre : les études de comportement des visiteurs de collections en ligne (durée,
profondeur, retour), les « generous interfaces » de Mitchell Whitelaw et leurs
suites, le slow looking, les critiques des musées virtuels en 3D, et les
interfaces d'exploration réussies hors du monde muséal (encyclopédies, archives,
cartes, sites de curiosité).
Identifie aussi ce que la muséographie physique sait faire (rythme, séquence,
accrochage, cartel) et comment cela a été traduit à l'écran, avec succès ou non.
Rends : 10 principes appuyés sur des preuves, 10 erreurs fréquentes, 8 sites à
étudier avec ce que chacun réussit, et les mécanismes d'engagement fondés sur la
curiosité plutôt que sur la contrainte.
```

Les résultats de la requête 1 servent à réviser la liste des collections et le schéma. Ceux de la requête 4 servent à corriger la section « Expérience du visiteur » avant le prototype.

## Ce que les recherches ont changé

Les quatre rapports sont dans [docs/research/](research/). Ce sont des pistes, pas des sources : ils mêlent des faits solides et des affirmations inexactes (par exemple, le style d'un artiste n'est pas protégé en tant que tel par le droit d'auteur français, contrairement à ce que laisse entendre le rapport juridique ; le risque d'un dérivé tient au droit moral et à la contrefaçon de la forme). Toute affirmation reprise dans un cartel, un parcours ou une décision est vérifiée à sa source primaire.

Modifications apportées à ce document :

| Rapport | Effet |
| --- | --- |
| 1. Cartographie | systèmes ajoutés au périmètre de M5 (Minitel, AA japonais) ; limite du modèle de grille pour les polices proportionnelles ; liste ci-dessous des pratiques voisines |
| 2. Méthodes | confirme le modèle sur la grille plutôt que sur les pixels (tenseur glyphe, `fg`, `bg`), la découpe par pack et le contrôle de la date ; rien à changer dans les chantiers |
| 3. Juridique | stratégie d'affichage en trois voies ; `policy.allows()` fermée par défaut ; invariant contre les dérivés ; structure porteuse proposée |
| 4. Muséographie | carte des styles à une touche de chaque œuvre ; salle des archives à facettes ; accessibilité ; affichage sur téléphone ; sites à étudier |

Pratiques voisines relevées par la cartographie, classées par proximité avec le cœur du projet :

| Pratique | Décision |
| --- | --- |
| AA japonais (Shift_JIS, 2channel), pseudographie soviétique et FidoNet, BBS asiatiques et sud-américains | dans le périmètre ; ce sont des scènes du même art, sous-représentées dans les archives occidentales |
| Vidéotex hors Europe (Telidon, NAPLPS, CAPTAIN), Minitel | dans le périmètre ; un décodeur par norme, NAPLPS et CAPTAIN étant en partie vectoriels, à évaluer |
| RTTY art, art de la machine à écrire, FIGlet, bannières | dans le périmètre comme collections ; la machine à écrire relève de la numérisation d'objets physiques, donc d'un niveau `conservation` sans original numérique |
| Code source graphique (IOCCC), sizecoding, polices des ROM de caractères | collections secondaires ; les polices ROM entrent d'abord comme données des profils de rendu |
| Notation des trackers, musique de téléscripteur | liées au son ; à reconsidérer avec la musique des œuvres |
| Tissage Jacquard, cartes perforées | hors périmètre ; un parcours peut les évoquer comme ancêtres |

## Risques principaux

| Risque | Parade |
| --- | --- |
| L'affichage reste bloqué juridiquement | le site est conçu pour être beau avec des fiches `metadata` ; la permission des artistes est recherchée dès M0 |
| L'infrastructure avance et personne ne voit d'œuvre | l'écran d'œuvre est prototypé dès M2, sur des artefacts CC0 |
| Le périmètre (six chantiers, quinze familles) dilue l'effort | le V0 est l'ANSI et l'artscene BBS ; un système n'entre qu'avec son décodeur, son profil et sa collection |
| Les témoins de la scène vieillissent | les entretiens commencent pendant M2 |
| Un résultat calculé est pris pour un fait | invariants sur `nature` et `asserted_by`, trait pointillé, lien « méthode » partout |
