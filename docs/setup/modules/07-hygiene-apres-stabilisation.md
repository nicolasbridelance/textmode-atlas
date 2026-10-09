# Hygiène après stabilisation — audit d’obsolescence et devoir de proposition

## Déclencheur

Après validation d’un changement fonctionnel, demande-toi : **qu’est-ce que ce nouvel état rend inutile, incohérent ou plus difficile à maintenir ?**

Si un commit fonctionnel est autorisé, utilise son SHA comme référence. Un commit local n’est pas nécessairement intégré à la branche principale ; indique son état réel. Si aucun commit n’est autorisé, déclenche l’audit sur le diff fonctionnel stabilisé et testé. L’audit n’autorise ni commit, ni push, ni suppression de travaux d’autrui.

L’inspection vise d’abord la zone touchée, puis les usages, configurations, tests et documents que le changement peut affecter dans le reste du dépôt. Évite un audit intégral coûteux après chaque petite modification.

## Candidats à examiner

| Famille | Recherche et décision attendues |
| --- | --- |
| Obsolescence induite | Anciens adaptateurs, routes, wrappers et branches de compatibilité remplacés. Vérifie consommateurs et obligations de compatibilité avant suppression. |
| Code mort et orphelin | Imports, fonctions et blocs commentés devenus inutiles. Recherche usages statiques et dynamiques, points d’entrée publics et configuration. |
| Échafaudage et POC | Helpers d’investigation, scripts ad hoc, variantes temporaires, traces de spike. Une variante nommée `_v2` n’est pas une preuve d’inutilité. Respecte le devenir du prototype décidé dans le spike. |
| Tests et fixtures | Mocks, fixtures et snapshots liés à des comportements disparus. Garde les tests des comportements maintenus et les garanties de non-régression ; ne mets pas à jour un snapshot pour masquer un défaut. |
| Dépendances et configuration | Packages exploratoires, variables et options sans usage démontré. Examine les usages de build, test, CLI, plugins et déploiement ; mets manifest et lockfile en cohérence. |
| Debug et télémétrie | Prints et logs d’investigation introduits pendant le travail. Conserve la journalisation opérationnelle, de sécurité ou d’audit utile, y compris les niveaux autres qu’erreur. |
| Documentation et backlog | Instructions, TODO/FIXME et tâches rendus caducs. Mets à jour la source de suivi retenue ; conserve l’historique des décisions. |
| Dette révélée | Duplication, cas particuliers, complexité ou couplage désormais gênants. Prépare une proposition de refactoring lorsque le signal est réel. |
| Découpage Git | Distingue le changement fonctionnel stabilisé et le nettoyage additionnel pour faciliter revue et retour arrière. |

## Garde-fous

- L’absence de référence statique ne prouve pas l’inutilité. Inspecte réflexion, dispatch, injection, flags, plugins, interfaces publiques et consommateurs externes pertinents. Des tests verts seuls ne prouvent pas qu’un code est mort.
- Un TODO, test `skip` ou `xfail` avec ticket ou raison documentée est une dette suivie. Vérifie sa validité, signale son état ; ne le supprime pas pour nettoyer une liste.
- Avant toute purge, liste les candidats, la justification et les preuves attendues. Ne touche ni aux changements préexistants ni aux données utilisateur.
- Respecte le seuil de purge décidé pour le dépôt. À défaut, applique un seuil de prudence : **plus de 50 lignes suivies supprimées ou au moins 3 fichiers suivis affectés par le nettoyage** nécessitent une validation explicite avant le commit d’hygiène. Le volume est celui du diff de nettoyage, hors fichiers générés dont le traitement suit les conventions du projet.
- Un doute sur un contrat public, une suppression irréversible, des données ou le périmètre impose un arbitrage indépendamment du volume. La petite taille d’un diff n’est pas une autorisation générale.
- Les autorisations déjà accordées qui couvrent explicitement cette purge ou son seuil restent valables : consigne leur source et ne redemande pas la même validation.
- Prépare un diff réversible et revu avant de demander une validation lorsque c’est possible sans franchir le périmètre autorisé. Si la modification elle-même n’est pas autorisée, prépare une liste et un plan précis.
- Git ne protège que ce qui a réellement été enregistré. Ne suppose pas qu’un fichier non suivi ou des changements non commités sont récupérables dans son historique.

## Boucle et traçabilité

Utilise le [modèle de changement](../templates/CHANGEMENT.md), intégré au suivi existant ou à la PR ; ne recommence pas la checklist d’installation pour chaque commit.

1. **Référence fonctionnelle** : SHA ou état précis du working tree, critère et preuve de validation.
2. **Inventaire** : candidats supprimables, éléments à conserver, cas ambigus et justification. « Aucun candidat » est une conclusion valide avec périmètre inspecté.
3. **Décision** : supprimer / conserver / proposer / différer, avec autorisation et éventuel ticket.
4. **Nettoyage autorisé** : modifications limitées et diff séparé de l’évolution métier lorsque possible.
5. **Revalidation** : contrôles pertinents après nettoyage, y compris installation ou build si dépendances/configuration affectées. Ne réutilise pas la preuve antérieure pour ce nouvel état.
6. **Enregistrement** : preuves avant/après, fichiers concernés, disposition des candidats, SHA si commit autorisé, état local/poussé et prochaine action.

Si une interruption survient entre stabilisation et audit, inscris l’audit en prochaine action de reprise. S’il survient pendant la purge, inspecte le diff avant de continuer.

## Deux temps, commits cohérents

Lorsqu’il y a effectivement du nettoyage additionnel et que les commits sont autorisés, conserve un commit fonctionnel validé puis un commit d’hygiène validé. Exemple si les conventions le permettent : `chore(hygiene): nettoyage après <SHA>`.

N’ajoute pas un commit vide lorsqu’il n’y a rien à retirer. Les suppressions indispensables au bon fonctionnement de la fonctionnalité appartiennent au changement fonctionnel : ne laisse pas volontairement un état cassé pour imposer deux commits. Garde le formatage sans rapport hors de ces diffs. Une règle de message ou un ratio de lignes ne prouve pas la séparation sémantique.

## Devoir de conseil

Ne conserve pas une structure fragile par inertie. Demande-toi si le changement augmente la friction, multiplie les cas particuliers ou révèle une connaissance dupliquée.

Lorsqu’un refactoring supplémentaire paraît utile, utilise le [modèle de proposition](../templates/REFACTORING.md) : cible, signal observé, gain mesuré ou estimation explicitement annoncée, plan court, risques et validation. Propose-le spontanément ; l’exécuter nécessite une validation couvrant son périmètre. N’invente pas un gain chiffré et ne refactorise pas sans besoin sous couvert d’hygiène.

## Hygiène économique

L’inventaire inclut les ressources créées par le changement : previews, serveurs MCP, index, environnements, volumes et stockage. Consulte le [module coûts](10-couts-et-consommation.md) avant de proposer leur arrêt ou suppression. Documente consommation évitable, données à préserver, autorisations et effet réel ; une suppression locale de configuration n’arrête pas nécessairement une ressource distante.
