# Posture cyber — sécurité conçue, données maîtrisées, risques gérés

La posture cyber repose ici sur quatre axes : **security by design**, **classification et gestion des données**, **analyse et gestion des risques**, **cartographie maintenue à jour**. Les contrôles d’exploitation, détection et récupération soutiennent ces axes ; ils ne les remplacent pas.

## 1. Security by design : avant de coder, puis à chaque changement

Dès la conception, identifie actifs, données, opérations sensibles, acteurs, frontières de confiance et scénarios de risque du changement. Définis les exigences qui orientent l’architecture : minimisation des données, autorisations côté serveur, séparation des privilèges et environnements, validation des frontières, comportement en erreur et mécanismes de protection adaptés.

Choisis les contrôles en fonction des risques et classes de données, puis définis comment les vérifier. Préfère une configuration sûre par défaut et des accès explicitement justifiés. Examine les dépendances et services externes avant de leur confier un flux, des données ou des capacités.

Lie besoin, données, risque, décision et preuve de validation. Un choix structurant mérite un ADR ; un risque ou usage incertain peut mériter un spike borné. La revue intervient avant implémentation, avant livraison et lorsque l’architecture évolue, pas seulement après un scan.

Si l’état initial manque de repères, documente ce qui est observé et les exigences proposées sans présenter une intention comme une protection déjà effective.

## 2. Classifier les données et appliquer les règles de gestion

Inventorie les **catégories** de données réellement collectées, produites, stockées et transmises, avec finalité, propriétaire, sources, destinations et copies. Ne collecte pas des valeurs réelles pour remplir ce registre.

Réutilise la classification de l’organisation. À défaut, propose une échelle opérationnelle simple — par exemple public, interne, confidentiel, restreint — avec des critères et règles explicites. Les libellés seuls n’apportent aucune protection. Cette classification opérationnelle ne remplace pas la qualification juridique des données.

Évalue confidentialité, intégrité et disponibilité séparément : une donnée publique peut nécessiter une forte intégrité ; une configuration banale peut être indispensable à la continuité. Les agrégations et copies peuvent avoir une sensibilité différente de celle supposée pour chaque élément isolé.

Pour chaque classe/catégorie, décide et vérifie ce qui s’applique :

| Dimension | Règle à rendre explicite et vérifiable |
| --- | --- |
| Collecte et production | Finalité, données nécessaires, validation, réduction des données et accès à la source. |
| Stockage et accès | Emplacements autorisés, environnements, droits, isolation, chiffrement et gestion des clés adaptés. |
| Transport et partage | Destinataires, canaux, exposition publique, exports, fournisseurs et autorisations. |
| Usage par l’IA/MCP | Données autorisées/interdites, destination et périmètre de traitement ; masque ou transforme lorsque cela répond au besoin. |
| Logs et télémétrie | Champs autorisés, expurgation, accès, durée et tests empêchant les fuites. |
| Tests et développement | Données synthétiques ou transformation réellement évaluée ; ne suppose pas une copie devenue inoffensive après retrait du nom. |
| Sauvegardes et copies | Localisation, protection, restauration, dérivés/caches et gestion de fin de vie. |
| Conservation et effacement | Durée décidée, déclencheurs, responsable, mécanisme et limites, y compris copies et sauvegardes. |

Une donnée non classifiée reste une inconnue à traiter ; ne la considère pas publique. Examine son contexte avant export et évite de l’envoyer vers une destination non autorisée. Les règles approuvées du projet déterminent sa gestion provisoire et son arbitrage.

## 3. Analyser les risques, puis les gérer

Pour chaque scénario pertinent, relie acteur ou événement, actif/données, conditions, faiblesse, conséquence et périmètre. Considère erreurs, abus internes, dépendances, compromission et indisponibilité ; pas seulement un attaquant externe.

Explique vraisemblance/exposition et impact avec les éléments disponibles ; utilise l’échelle existante ou une échelle qualitative définie. Sépare risque initial et risque résiduel après contrôles **réellement vérifiés**. N’abaisse pas le risque au seul motif qu’une remédiation est planifiée.

La gestion donne une disposition : éviter l’activité risquée, réduire le risque, encadrer un transfert contractuel ou accepter un résiduel par décision habilitée. Externaliser un service ne fait pas disparaître ses risques. L’agent propose et documente ; il ne s’auto-attribue pas l’acceptation.

Chaque risque a ID stable, propriétaire, action, priorité motivée, échéance décidée, preuve de traitement et condition de réexamen. Lie tâches, ADR, exceptions et budgets. Une action terminée ne clôt le risque qu’après vérification de son effet et disposition du résiduel. Une acceptation limitée ou expirée se revoit ; elle ne permet pas d’écarter une obligation applicable.

## 4. Maintenir la cartographie

La cartographie est une vue maintenue des actifs et de leurs relations, pas un schéma de présentation isolé. Utilise l’[architecture](../templates/ARCHITECTURE.md) existante comme source ou lie le support autorisé ; ne recrée pas une carte concurrente.

Elle couvre, à la profondeur utile : composants/services, environnements et exposition, interfaces/API/événements, flux et magasins de données avec catégories/classes, identités/rôles, fournisseurs/IA/MCP, frontières de confiance, dépendances critiques et responsables. Identifiants de composants, contrats, données et risques se relient entre registres.

Pour une partie inconnue ou inaccessible, marque la limite et l’action à mener. Garde le détail sensible dans un support approprié ; un repo public ne doit pas devenir une carte d’accès exploitable. La preuve conserve date, référence du code/configuration et périmètre réellement inspecté.

Chaque changement de composant, flux, données, fournisseur, environnement, exposition ou droit doit faire comparer le diff à la cartographie et mettre à jour les vues affectées **dans le même chantier**. Si la carte est générée, vérifie son actualité et complète les informations que le code ne révèle pas. Si le changement n’a pas d’impact, consigne brièvement ce constat.

Désigne un responsable et une fréquence de revue pour les dérives hors code, en plus des déclencheurs par changement. Un diagramme présent sans référence actuelle ne démontre pas une carte à jour.

## 5. Défense en profondeur et exploitation en soutien

Relie plusieurs barrières utiles aux scénarios : identité, autorisation applicative, validation, isolation runtime/réseau, protection des données, chaîne de livraison, détection et récupération. Analyse leur dépendance commune : deux barrières reposant sur le même accès compromis ne sont pas nécessairement indépendantes.

Un chiffrement ne corrige pas des permissions excessives ; un filtre réseau ne remplace pas le contrôle métier. Vérifie les couches choisies et le risque restant. Conserve détection, responsables d’incident, préservation des traces, révocation/containment autorisés et restauration lorsque pertinents. Une sauvegarde présente ne démontre pas une restauration possible.

En incident suspecté, sépare observations et hypothèses, préserve les traces et ne publie ni secret ni notification hors autorisation. Les obligations de notification se qualifient avec les responsables concernés et les sources actuelles.

## 6. Suivi et références

Le [registre de posture](../templates/POSTURE_CYBER.md) rassemble classes/règles de données et risques, ou référence les sources déjà maintenues. Le [suivi de changement](../templates/CHANGEMENT.md) vérifie conception, classification, risques et actualisation de carte. Les preuves portent sur l’état réel ; proposé, configuré et vérifié restent distincts.

Repères consultés le 9 octobre 2026 : [ANSSI, défense en profondeur](https://messervices.cyber.gouv.fr/guides/essentiels-defense-profondeur), [ANSSI, hygiène informatique](https://messervices.cyber.gouv.fr/guides/guide-dhygiene-informatique), [NIST CSF 2.0](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20), [OWASP ASVS](https://owasp.org/projects/asvs). Le CSF offre un cadre de résultats ; ASVS fournit des exigences de vérification applicative. Si un référentiel est retenu, fixe sa version et les exigences choisies ; la mention du nom n’est ni conformité ni certification. Voir aussi le [cadre lois/normes](14-lois-normes-et-conformite.md).
