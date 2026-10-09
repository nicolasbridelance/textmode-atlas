<!-- SPDX-FileCopyrightText: 2026 textmode-atlas contributors -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Mets-toi bien — point d’entrée

Tu arrives dans un dépôt. Prépare un environnement fiable et laisse un état de travail reprenable. L’installation est un chantier limité : adapte-la au projet et préserve les travaux existants.

## Première arrivée

1. Lis les instructions applicables au dépôt et aux dossiers concernés.
2. Lis le [protocole](docs/setup/PROTOCOLE.md) et le [cadre](docs/setup/modules/00-cadre.md).
3. Ouvre la [checklist](docs/setup/CHECKLIST.md). Renseigne son contexte, ses exigences et ses dépendances à partir du dépôt réel.
4. Commence par `REC-01`, puis intègre les instructions avec `INS-01`. Pour chaque action, lis uniquement son module, puis applique la boucle du protocole.
5. Consigne les preuves dans le [journal](docs/setup/JOURNAL.md). Maintiens la [reprise](docs/setup/REPRISE.md) après chaque action.

## Reprise de session

Lis les instructions applicables, puis `REPRISE.md`, `CHECKLIST.md` et les entrées du journal liées aux actions ouvertes. Vérifie branche, commit, diff et environnement : l’état enregistré peut être ancien. Relis le protocole si tu ne le connais pas. Reprends l’action indiquée ; ne recommence pas toute l’installation.

## Règle de travail

**Choisir → lire → exécuter → vérifier → tracer → mettre à jour → continuer.**

Une action vérifiée possède une preuve liée à son identifiant. Un blocage possède une cause et une prochaine action. Une lecture seule ne termine pas une mise en place.

Le suivi dans les fichiers fait foi ; ton plan temporaire et ta mémoire conversationnelle ne le remplacent pas. N’effectue les opérations Git ou distantes que dans le cadre des autorisations existantes.

## Activation dans ton outil

Utilise le [fragment d’amorçage](docs/setup/templates/AGENTS.fragment.md) pour référencer ce fichier depuis les instructions que ton outil lit réellement. S’il existe déjà un `AGENTS.md` ou un équivalent, ajoute une référence ; ne l’écrase pas. Exemple de consigne à y intégrer :

> Pour préparer le dépôt ou reprendre son installation, lis `METS_TOI_BIEN.md` et suis le protocole ainsi que la checklist dans `docs/setup/`.

Prompt utilisateur :

> Lis `METS_TOI_BIEN.md`, analyse le dépôt et mets-toi bien. Exécute les actions utiles et autorisées ; mets à jour la checklist, les preuves et la reprise à chaque action. Continue les actions indépendantes si une autre est bloquée.

Pour un petit projet, garde des entrées courtes. N’ajoute ADR, spike ou nouvel outil que pour un besoin concret.

## Après l’installation : travailler et maintenir

Pour chaque changement de code, applique la [revue de conception](docs/setup/modules/06-conception-du-code.md), puis l’[audit d’hygiène après stabilisation](docs/setup/modules/07-hygiene-apres-stabilisation.md). Ces déclencheurs sont intégrés au fragment d’instructions d’agent.

Le [suivi de changement](docs/setup/templates/CHANGEMENT.md) se place dans le ticket, la PR ou le support déjà adopté. La checklist d’installation reste distincte de cette routine. Les [propositions de refactoring](docs/setup/templates/REFACTORING.md) sont argumentées et soumises à validation de leur périmètre.

Pour les changements d’interface, consulte aussi le [module UX/UI et design](docs/setup/modules/08-ux-ui-design.md). Les preuves de rendu, d’interaction et d’accessibilité rejoignent le suivi du changement ; la [référence design](docs/setup/templates/DESIGN.md) conserve les conventions et leurs sources.

Pour les capacités externes, consulte le [module MCP et intégrations](docs/setup/modules/09-mcp-integrations.md). Pour les dépenses, utilise le [module coûts et consommation](docs/setup/modules/10-couts-et-consommation.md) : payeurs, postes, consommation, coût par run/usage et limites. Les registres [MCP](docs/setup/templates/MCP.md) et [COUTS](docs/setup/templates/COUTS.md) sont à adapter ou à remplacer par la source existante.

Si une dépense utile n’est pas couverte, prépare une [demande de budget](docs/setup/templates/DEMANDE_BUDGET.md) chiffrée et bornée. Attends l’accord pour cette dépense, poursuis les travaux indépendants, puis suis consommé, engagé, reste et besoin d’extension.

Pour les frontières et risques, les modules [API/contrats](docs/setup/modules/11-api-et-contrats.md), [accès](docs/setup/modules/12-acces-et-habilitations.md), [posture cyber](docs/setup/modules/13-posture-cyber.md) et [lois/normes](docs/setup/modules/14-lois-normes-et-conformite.md) définissent les revues, preuves et décisions. Réutilise les registres existants, et garde les informations sensibles dans un support approprié.

La posture cyber du kit est centrée sur **security by design**, **classification et gestion des données**, **analyse et gestion des risques**, et **cartographie à jour**. Chaque changement vérifie ces impacts avant implémentation et actualise les sources concernées avant clôture.
