# Suivi d’un changement — conception, interface et hygiène

> À intégrer dans le ticket, la PR ou le suivi existant. Pour un petit changement, une entrée courte suffit. Ce modèle n’impose pas un nouveau fichier par commit. Utilise les états du protocole ; les identifiants ci-dessous sont locaux à ce changement.

- Tâche / PR / identifiant du changement : <référence>
- Objectif et critère d’acceptation : <besoin actuel>
- Référence fonctionnelle : <SHA ou working tree décrit>
- Auteur / date et fuseau : <à renseigner>
- Source des preuves : <journal ou suivi retenu>
- Autorisations et seuil de purge applicable : <source>

| ID | Action | Critère | État | Preuve / décision |
| --- | --- | --- | --- | --- |
| CHG-01 | Concevoir et relire | Besoin respecté, arbitrages de simplicité et responsabilités expliqués si utiles. | À examiner | — |
| CHG-02 | Stabiliser la modification | Contrôles pertinents exécutés sur l’état fonctionnel identifié ; limites explicites. | À examiner | — |
| CHG-03 | Auditer l’obsolescence | Zone et usages affectés inspectés ; candidats ou absence justifiée consignés. | À examiner | — |
| CHG-04 | Traiter le nettoyage | Candidats autorisés traités ou dispositions explicites ; cas ambigus et seuil respectés. | À examiner | — |
| CHG-05 | Revalider | Preuves sur l’état après nettoyage, ou absence de modification depuis CHG-02 explicitée. | À examiner | — |
| CHG-06 | Conseiller et transmettre | Dette révélée évaluée ; proposition si justifiée, sauvegarde et prochaine action exactes. | À examiner | — |

## Volet interface — si le changement affecte l’expérience utilisateur

À exécuter avant de considérer `CHG-02` vérifié. En l’absence d’impact sur l’interface, marquer ces lignes Sans objet avec la raison. Pour une interface modifiée, l’absence d’outil visuel n’est pas une non-applicabilité : noter la validation bloquée ou non exécutée.

| ID | Action | Critère | État | Preuve / limite |
| --- | --- | --- | --- | --- |
| UI-CHG-01 | Comprendre et concevoir | Parcours, références de design, états et critère de réussite identifiés. | À examiner | — |
| UI-CHG-02 | Examiner le rendu | Interface ouverte ; hiérarchie, textes et tailles pertinentes examinés sur l’état du code concerné. | À examiner | — |
| UI-CHG-03 | Essayer les interactions | Parcours et états pertinents réellement essayés ; résultats constatés, pas seulement captures. | À examiner | — |
| UI-CHG-04 | Vérifier l’accessibilité | Clavier, focus, sémantique et autres contrôles applicables exécutés ; limites explicites. | À examiner | — |

### Preuves UI

| Écran/parcours et état | Référence code / environnement / date | Viewport ou appareil | Contrôle effectué | Attendu / observé | Capture ou preuve expurgée / limite |
| --- | --- | --- | --- | --- | --- |
| <à renseigner> | — | — | — | — | — |

Réutiliser cette preuve depuis les lignes ci-dessus. Après correction ou nettoyage affectant l’interface, refaire les contrôles concernés et lier les nouvelles preuves à `CHG-05`. Une capture seule ne valide pas les interactions ; un essai de l’agent ne constitue pas une recherche utilisateur.

## Volet intégrations et coût — selon l’impact du changement

| ID | Action | Critère | État | Preuve / limite |
| --- | --- | --- | --- | --- |
| MCP-CHG-01 | Examiner les capacités et effets | Si intégration modifiée : cible, droits, données sortantes, test et reprise vérifiés dans le périmètre autorisé. | À examiner | — |
| CST-CHG-01 | Estimer avant exécution | Si consommation affectée : ressources, unités, prix datés, budget et limite identifiés ; inconnues explicites avant opération coûteuse. | À examiner | — |
| CST-CHG-02 | Mesurer et transmettre | Consommation/coût après exécution consignés si accessibles, échecs/retries inclus ; écart à l’estimation expliqué et sources mises à jour. | À examiner | — |

- Budget / payeur / autorisation de dépense : <source>
- Estimation avant, nature et hypothèses : <montant/devise ou unités, ou inconnu>
- Limites de temps/volume/tentatives et effet réel : <à renseigner>
- Usage et coût après / source / période / écart : <mesuré, estimé, facturé ou inconnu>
- Opération distante ambiguë / référence expurgée / prochaine vérification : <si nécessaire>

Sans effet économique ou d’intégration identifié, justifie Sans objet. Une donnée inaccessible reste inconnue, pas zéro. Une consommation non mesurée ne peut pas être présentée comme vérifiée.

## Volet contrats, droits et risques — selon l’impact

| ID | Action | Critère | État | Preuve / limite |
| --- | --- | --- | --- | --- |
| API-CHG-01 | Vérifier le contrat | Producteurs/consommateurs et impact compatible/incompatible/inconnu examinés ; validation et migration nécessaires tracées. | À examiner | — |
| ACC-CHG-01 | Revoir les accès | Droits et isolation affectés revalidés, cas permis/refusés couverts dans le périmètre autorisé. | À examiner | — |
| CYB-CHG-01 | Réexaminer le risque | Security by design : données/classes et risques du changement évalués avant implémentation ; règles de gestion, contrôles, résiduel et décisions tracés. | À examiner | — |
| MAP-CHG-01 | Maintenir la cartographie | Composants/flux/données/classes/droits/fournisseurs affectés mis à jour dans la source maintenue, liés aux contrats/risques ; ou absence d’impact justifiée. | À examiner | — |
| LEG-CHG-01 | Revoir l’applicabilité | Changements de données/finalités/marché/fournisseur ou engagements examinés ; qualification et blocages explicites. | À examiner | — |

Pour un volet non affecté, justifier Sans objet. Un accès inaccessible ou une qualification inconnue ne se transforme pas en preuve de conformité. Les détails sensibles restent dans leur support approprié.

## Inventaire et décisions d’hygiène

| Candidat / emplacement | Pourquoi il semble obsolète | Usages inspectés et preuve | Décision / autorisation / ticket |
| --- | --- | --- | --- |
| <à renseigner, ou aucun candidat avec périmètre inspecté> | — | — | — |

## Vérifications

<Preuves datées : commandes ou inspections, environnement, état testé, résultats et limites. Lier les entrées plutôt que copier des logs.>

## Reprise et résultat

<Actions restantes, autorisations attendues, état local/commité/poussé et liens. Ne pas annoncer l’hygiène terminée si des candidats pertinents restent non examinés. Un report explicite ne supprime pas le blocage.>

## Budget à demander si nécessaire

<Lien vers demande et décision réelle, plafond/période/périmètre, consommé et engagé, reste estimé et prévision de fin. Tant que l’accord manque, seules les opérations indépendantes et déjà autorisées avancent. L’absence de réponse ne vaut pas accord.>

## Préparation sécurité avant implémentation

<Données et classes affectées, flux/frontières/acteurs, risques et règles de traitement, exigences/contrôles et validation prévue. Liens vers carte et registre. Après réalisation : nouvelle référence de carte, preuves de contrôles et traitement du résiduel. Pour un petit changement sans impact, un constat bref suffit.>
