# Conception du code — revue avant validation

Ces règles s’appliquent aux changements de code après l’installation. Lis-les lors de la préparation d’une modification, puis examine le diff avant de valider. Leur objectif est un code simple à comprendre et à faire évoluer, pas une conformité mécanique à tous les principes.

## Revue de conception

| Principe | Ce que tu examines | Ce que tu évites |
| --- | --- | --- |
| Complexité cyclomatique et cognitive | Chemins, imbrication et lisibilité ; retours anticipés ou extraction lorsque cela clarifie. | Réduire une métrique en déplaçant la complexité ailleurs sans gain de compréhension. |
| KISS | Solution la plus directe qui satisfait le besoin et les contraintes. | Couches, factories et abstractions sans rôle démontré. |
| YAGNI | Paramètres, options et extensions nécessaires au besoin actuel. | Flexibilité spéculative, nouvelles fonctionnalités « au cas où ». |
| DRY | Duplication de connaissance ou de logique qui doit évoluer ensemble. | Factorisation prématurée de blocs seulement ressemblants. Une duplication limitée peut être préférable à une mauvaise abstraction. |
| Responsabilité unique, SRP | Séparation utile entre validation, métier, transport et effets externes. | Une fonction qui porte plusieurs raisons indépendantes de changer ; découpage artificiel en microfonctions. |
| Valeurs explicites | Constantes ou enums lorsqu’une valeur porte une signification métier répétée ou difficile à lire. | Littéraux inexpliqués ; constante artificielle pour chaque zéro, chaîne ou valeur évidente. |
| Fail fast | Invariants vérifiés aux frontières appropriées, erreur explicite et traitement adapté au contrat. | Erreurs avalées par un catch général ; arrêt brutal d’un service lorsque le contrat appelle une réponse contrôlée. |
| Pureté et immutabilité | Logique métier isolable, mutation des entrées et effets de bord clairement maîtrisés. | Mutation implicite des paramètres ou de l’état global. Une mutation locale justifiée n’est pas automatiquement fautive. |
| Injection de dépendances | Services externes fournis aux frontières pour découpler et tester le domaine. | Instanciation cachée d’une API ou BDD dans le métier ; framework d’injection ajouté sans besoin. |
| Loi de Déméter | Dépendance à la structure interne d’autres objets ; possibilité de déléguer à une interface directe. | Couplage profond. Le chaînage volontaire d’une API fluente ou d’un builder reste légitime. |
| Lisibilité et noms | Noms qui expriment les concepts ; commentaires expliquant le pourquoi, les contraintes ou les surprises. | Noms ambigus et commentaires paraphrasant le code ; suppression de commentaires utiles au seul motif que le code devrait tout expliquer. |

Une règle de trois peut déclencher une réflexion sur une abstraction ; elle ne commande pas automatiquement une factorisation. Le comportement, les contrats publics et la compréhension priment sur une métrique isolée.

## Avant de modifier

1. Relie la modification à un besoin et un critère de réussite.
2. Observe les conventions et composants existants ; choisis la solution minimale cohérente.
3. Identifie les invariants et les tests utiles. Lis les scripts avant de les lancer.
4. Repère les éléments que la nouvelle solution pourrait rendre obsolètes pour l’audit après stabilisation.

## Avant validation

Relis le diff avec la table ci-dessus. Note uniquement les arbitrages significatifs : pas onze paragraphes obligatoires pour une petite correction. Exécute les contrôles pertinents et enregistre les preuves dans le suivi de la tâche ou de la PR, selon le [modèle de changement](../templates/CHANGEMENT.md).

Un refactoring nécessaire et autorisé au changement peut faire partie de son périmètre. Un refactoring supplémentaire découvert pendant la revue relève du devoir de proposition décrit dans l’[audit d’hygiène](07-hygiene-apres-stabilisation.md), sans exécution silencieuse.

## Outils et jugement

Réutilise les outils de la stack. Leur présence ne dispense pas de la revue sémantique. La [répartition des contrôles](03-qualite-tests.md) précise ce qui peut devenir un check, un signal ou une décision.
