# Fragment d’amorçage des instructions d’agent

Ce fichier est un modèle à intégrer, pas un fichier d’instructions actif. Adapte le nom et l’emplacement à l’outil réellement utilisé. Les chemins du bloc supposent un fichier d’instructions à la racine du dépôt.

## Intégration

1. Identifie les instructions effectivement chargées et leur portée. Lis l’existant, y compris les règles des sous-dossiers.
2. Si le fichier existe, ajoute ou fusionne uniquement la section ci-dessous ; préserve ses règles. S’il n’existe pas et que l’outil prend ce nom en charge, crée `AGENTS.md` avec cette section.
3. Si l’outil utilise un autre mécanisme, adapte la référence. Ne crée pas plusieurs sources concurrentes.
4. Vérifie que les chemins existent et note le mécanisme d’activation observé dans `INS-01`. Si tu n’as pas confirmé le chargement automatique, indique cette limite et utilise le prompt explicite.
5. Complète les règles propres au repo à partir des preuves. Aucun placeholder ne doit passer pour une commande valide.

## Section à intégrer

```markdown
## Installation et reprise du travail

Pour préparer le dépôt ou reprendre son installation, lis `METS_TOI_BIEN.md`.
Suis `docs/setup/PROTOCOLE.md` et maintiens :
- `docs/setup/CHECKLIST.md` pour l’état courant des actions ;
- `docs/setup/JOURNAL.md` pour les constats et preuves datés ;
- `docs/setup/REPRISE.md` pour la prochaine action et les interruptions.

Lis les modules indiqués par les actions, au moment où tu en as besoin.
Ne marque une action Vérifié que lorsque son critère possède une preuve.
Après chaque action, actualise le suivi ; avant interruption, laisse un checkpoint.
À la reprise, confronte le suivi à l’état réel du dépôt avant de poursuivre.
Préserve les changements préexistants et applique les autorisations déjà données.
Pour les fichiers concernés, respecte aussi les instructions locales applicables.

Ces règles s’appliquent à l’installation et à son entretien.

## À chaque changement de code

Avant de modifier et avant validation, applique la revue de conception de
`docs/setup/modules/06-conception-du-code.md` : simplicité, besoin actuel,
responsabilités, couplage, effets de bord et lisibilité.
Après stabilisation fonctionnelle, applique
`docs/setup/modules/07-hygiene-apres-stabilisation.md` : audite l’obsolescence
induite, distingue candidats et preuves, respecte les seuils et autorisations,
puis vérifie à nouveau tout nettoyage réalisé.
Si les commits sont autorisés et qu’un nettoyage additionnel existe, sépare
le commit fonctionnel et celui d’hygiène sans laisser un état intermédiaire cassé.
Propose spontanément les refactorings supplémentaires justifiés ; ne les
exécute pas silencieusement. Préserve les dettes intentionnelles documentées.
Trace ce cycle dans le ticket, la PR ou le suivi existant, avec
`docs/setup/templates/CHANGEMENT.md` si utile. Il ne faut pas rejouer la
checklist d’installation à chaque commit.
Les contrôles outillés définis par le projet filtrent les problèmes détectables ;
ils ne remplacent pas le jugement sur la conception ou les suppressions.
Pour tout changement affectant l’interface, ses textes ou son comportement,
lis `docs/setup/modules/08-ux-ui-design.md`. Comprends le parcours,
réutilise les sources de design, couvre les états pertinents, ouvre l’interface
et vérifie rendu, interactions, responsive et accessibilité selon le périmètre.
Trace les preuves dans le volet UI de `docs/setup/templates/CHANGEMENT.md`.
Si un contrôle est impossible, explicite l’obstacle et garde sa validation ouverte.
Pour configurer ou utiliser une intégration, lis
`docs/setup/modules/09-mcp-integrations.md`. Vérifie capacité, cible, droits,
effets et données sortantes ; ne répète pas une écriture à résultat ambigu
sans vérifier l’état distant. Les capacités disponibles ne valent pas autorisation.
Pour une opération ou modification affectant les dépenses, lis
`docs/setup/modules/10-couts-et-consommation.md`. Identifie payeur,
ressources, consommation, budget et limite ; distingue facturé, mesuré,
estimé et inconnu. Un quota ou une alerte ne vaut pas plafond garanti.
Trace intégrations et coûts dans le suivi du changement, et maintiens les
registres ou leurs équivalents. N’invente ni tarif ni coût nul faute d’accès.
Si la dépense utile n’est pas couverte, prépare une demande avec
`docs/setup/templates/DEMANDE_BUDGET.md` : objectif, estimation sourcée,
plafond, payeur, durée et arrêt. Attends l’accord réel pour les dépenses
concernées et continue les travaux indépendants. Respecte les enveloppes
approuvées ; redemande avant dépassement prévisible, sans t’auto-autoriser.
Pour une frontière/API modifiée, lis `docs/setup/modules/11-api-et-contrats.md`
et vérifie contrat, consommateurs, compatibilité et migration pertinente.
Pour les droits, lis `docs/setup/modules/12-acces-et-habilitations.md` : distingue
agent, infrastructure et produit, droits voulus/effectifs et preuves d’accès refusés.
Pour l’exposition ou les données sensibles, lis `docs/setup/modules/13-posture-cyber.md`
et applique security by design avant implémentation : classe les données,
définis leur gestion, analyse et traite les risques, puis maintiens la cartographie
des composants/flux/frontières/droits/fournisseurs dans le même chantier.
Relie décisions, contrôles et preuves ; garde détection et récupération en complément.
Pour les obligations, lis `docs/setup/modules/14-lois-normes-et-conformite.md` :
qualifie contexte et références actuelles, distingue loi/norme/contrat/guide,
fais attribuer les arbitrages et n’annonce aucune conformité sans preuves.
Une absence d’accès signifie non vérifié. Ne modifie pas les droits distants,
n’accepte pas un risque et n’engage pas le propriétaire hors autorisation.
Le travail courant suit aussi les conventions ci-dessous et le suivi retenu.
```

## Règles propres au dépôt, à ajouter après reconnaissance

Conserve cette partie ici comme aide, puis rédige des instructions courtes et factuelles dans le fichier actif :

- Installation, démarrage, contrôle rapide et tests : commandes vérifiées, répertoire et limites.
- Zones du code et contraintes : points d’entrée, interfaces à préserver, fichiers générés à ne pas éditer directement.
- Conventions : nommage, style, erreurs, composants graphiques ; liens vers la source maintenue.
- Git et livraison : politique réellement autorisée, checks attendus, effets externes.
- Sources de vérité : tâches, décisions, documentation et passation.

Évite de recopier les modules. Si une information manque, indique la limite ou l’action qui la résout plutôt que d’inventer la règle.
