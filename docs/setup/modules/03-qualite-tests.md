# Qualite tests

Référence à lire uniquement pour les actions correspondantes de la checklist.

## Des contrôles qui vivent hors de ta mémoire

Les règles importantes doivent être exécutables et compréhensibles par un humain comme par un agent.

| Niveau | Rôle | Exemples selon le projet |
| --- | --- | --- |
| Boucle locale | Retour rapide pendant le travail | Format, lint ciblé, types, tests unitaires concernés. |
| Hook local | Détecter tôt les erreurs simples | Contrôle des fichiers modifiés, scan de secrets, format. |
| CI de PR | Référence partagée avant intégration | Contrôles complets utiles, build, tests, scans adaptés. |
| Contrôle planifié | Vérifications plus longues ou périodiques | Audit de dépendances, tests étendus, mutation ciblée. |
| Déploiement | Publier un résultat identifié | Artefact vérifié, environnement explicite, contrôle après déploiement, retour arrière. |

- Les hooks locaux peuvent être absents ou contournés : les règles nécessaires à l’intégration doivent aussi être vérifiées en CI.
- Documente l’installation des hooks et garde-les rapides. Ne lance pas tous les scanners à chaque commit par principe.
- Réutilise les mêmes scripts localement et en CI pour limiter les divergences.
- Inspecte les effets des workflows : certains pushs ou tags peuvent publier automatiquement.
- Ne confonds pas la présence d’un workflow avec son caractère obligatoire : vérifie les règles distantes si tu as accès.
- N’affaiblis pas un contrôle pour obtenir du vert. Justifie toute exception, son périmètre et son échéance de réexamen.
- Un test instable doit être diagnostiqué ; une quarantaine temporaire doit être visible et suivie.
- Corrige les dépendances de manière ciblée et vérifie les effets des mises à jour ; évite les corrections forcées aveugles.

Si la CI est déjà rouge, conserve un état initial précis et propose une remise en état séparée des changements fonctionnels lorsque cela aide la revue.

## Une stratégie de test adaptée

Protège les comportements et contrats importants : cas normaux, limites, erreurs, permissions et compatibilité pertinente. Chaque correction de bug doit, lorsque c’est praticable, s’accompagner d’un test qui révèle le défaut avant correction.

- Tests unitaires pour la logique isolable.
- Tests d’intégration pour les échanges entre composants et services.
- Tests de bout en bout pour les parcours essentiels.
- Vérifications manuelles explicites lorsque l’automatisation n’apporte pas assez de valeur.

Évite les tests qui recopient l’implémentation et les objectifs de couverture arbitraires. Documente les données de test et la manière de les réinitialiser.

### Tests de mutation

Un outil de mutation modifie temporairement le programme, par exemple en inversant une condition. Il relance les tests pour vérifier s’ils détectent cette modification. Un mutant « tué » est détecté ; un mutant « survivant » demande une analyse.

Commence, si le projet s’y prête, sur une petite zone de logique métier importante. Mesure durée et utilité avant d’étendre. Certains mutants sont équivalents ou hors du comportement attendu : leur survie ne prouve pas automatiquement un mauvais test.

Ne mets pas une mutation complète dans chaque hook local. N’impose pas un score global sans mesure initiale et analyse du périmètre. Consigne les lacunes pertinentes et améliore les tests de comportement.

## Répartition entre checks et jugement

Automatise les critères définis que l’outil peut effectivement vérifier. Les proxys sémantiques produisent des signaux ; ils ne décident pas de la conception ou de la suppression. Adapte les règles à la stack et mesure le bruit avant de rendre un seuil bloquant.

| Sujet | Contrôle outillable | Jugement à conserver |
| --- | --- | --- |
| Complexité, imbrication, longueur | Mesures et delta sur la zone modifiée ; seuil convenu. | Où simplifier et si l’extraction améliore vraiment la lisibilité. |
| KISS, SRP, injection | Quelques proxys de taille et de couplage. | Intention, responsabilités et besoin d’abstraction ; aucune mesure directe complète. |
| YAGNI et code mort | Candidats : imports, paramètres ou exports statiquement inutilisés. | Usages dynamiques, API publiques et options réellement nécessaires. |
| DRY | Similarité de blocs. | Duplication de connaissance et coût d’une factorisation. |
| Constantes et valeurs brutes | Littéraux concernés par une règle de lint configurée. | Signification, exceptions et nommage ; nombres et chaînes ne sont pas tous détectés. |
| Fail fast | Catchs vides et patterns couverts par les règles disponibles. | Invariants métier et traitement d’erreur ; le lint ne prouve pas leur exhaustivité. |
| Mutation | Réassignations et certaines mutations détectables selon l’outil. | Pureté effective, portée des effets et mutation locale acceptable. |
| Loi de Déméter et nommage | Signaux structurels éventuellement bruyants. | Couplage réel, API fluentes et pertinence sémantique des noms. |
| POC et temporaires | Recherche de patterns ou inventaire des fichiers de travail. | Statut réel du fichier et politique de conservation. |
| Tests ignorés et fixtures | Inventaire des skips/xfails, références et dates. | Validité des raisons, garanties encore utiles et usages indirects. |
| Dépendances et environnement | Candidats sans référence dans le périmètre analysé. | Usages CLI, build, plugins et provisioning externe ; ne pas lire ou afficher les valeurs de .env pour croiser les noms. |
| Logs et prints | Appels aux APIs visées par une règle. | Différence entre debug temporaire, sortie CLI et télémétrie opérationnelle. |
| TODO et backlog | Inventaire et ancienneté. | Dette intentionnelle, tickets et résolution réelle. |
| Découpage des commits | Message et composition du diff, signaux de mélange. | Cohérence sémantique ; le titre ou un ratio ajouts/suppressions ne suffit pas. |

Un auto-fix doit être revu et vérifié. Ne supprime pas automatiquement une dépendance, un log ou une constante sur la seule base d’un signal. Les contrôles rapides adaptés vont dans les hooks ; les mêmes checks essentiels sont exécutés en CI. Les analyses lourdes peuvent être planifiées. N’ajoute pas un scanner par ligne de cette table.

Les règles de jugement demeurent dans les instructions et la revue. Les commandes déterministes validées sont référencées une fois, plutôt que répétées dans chaque prompt. Voir [conception](06-conception-du-code.md) et [hygiène](07-hygiene-apres-stabilisation.md).

## Vérification des interfaces

Les contrôles de build, types et tests ne suffisent pas à démontrer la qualité du rendu ou l’utilisabilité. Pour un changement d’interface, applique le [module UX/UI](08-ux-ui-design.md) et garde des preuves du rendu et des interactions. Les audits automatiques d’accessibilité et comparaisons visuelles sont complémentaires des contrôles manuels ; leur périmètre et leurs limites doivent être explicites.

## Coût des contrôles et tests d’intégration

CI, matrices, tests de mutation, environnements de preview et appels externes entrent dans le [suivi des coûts](10-couts-et-consommation.md). Examine fréquence, durée, stockage et retries ; distingue contrôles rapides et runs lourds. Un test distant suit les [règles d’intégration](09-mcp-integrations.md), avec cible, accès et budget définis. Ne réduis pas une garantie utile sans arbitrage pour obtenir un coût plus faible.


Pour les frontières et permissions, vérifie les comportements de [contrat](11-api-et-contrats.md) et les cas d’[accès refusés](12-acces-et-habilitations.md). Les scans ne remplacent pas le modèle de [risques](13-posture-cyber.md) ou la qualification d’[obligations](14-lois-normes-et-conformite.md).
