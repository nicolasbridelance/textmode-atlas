# Decisions documentation

Référence à lire uniquement pour les actions correspondantes de la checklist.

## Spikes : explorer avec une question et une limite

Un spike est une exploration temporaire destinée à réduire une incertitude, pas une fonctionnalité prête à livrer.

Pour une inconnue qui justifie une expérimentation, consigne :

```markdown
# Spike : <question à résoudre>
- Statut : prévu / en cours / terminé / abandonné
- Question et décision qu’elle doit éclairer :
- Hypothèses :
- Budget de temps, de calcul ou de coût :
- Expérience et critère de sortie :
- Résultats observés et limites :
- Conclusion et prochaine action :
- Devenir du prototype : supprimer / conserver comme référence / industrialiser
```

Isole le prototype lorsque nécessaire. À la fin du budget, conclus avec les éléments disponibles ou propose une extension motivée. Du code exploratoire doit être revu, testé et intégré proprement avant de devenir du code de production.

## ADR : garder la raison des décisions

Un ADR — Architecture Decision Record — conserve une décision importante et ses conséquences. Utilise-le pour un choix qui affecte durablement architecture, contrats, sécurité, dépendances structurantes ou exploitation. Une petite correction n’a pas besoin d’ADR.

```markdown
# ADR <identifiant> — <décision>
- Date :
- Statut : proposé / accepté / remplacé
- Contexte et contraintes :
- Options réellement envisagées :
- Décision et raison du choix :
- Conséquences, compromis et risques :
- Validation ou éléments de preuve :
- Conditions de réexamen :
- Liens : spike, ticket, PR, ADR remplacé
```

Un agent peut préparer un ADR ; le statut « accepté » doit correspondre à une décision réellement autorisée. Lorsqu’une décision change, conserve son histoire et relie le nouvel ADR à celui qu’il remplace.

## Documentation : peu de sources, des rôles clairs

Réutilise la structure existante. Les noms ci-dessous sont indicatifs, sauf convention déjà imposée par le dépôt.

| Document | Ce qu’il doit permettre |
| --- | --- |
| `README.md` | Comprendre le projet, installer, démarrer et trouver les autres repères. |
| Instructions d’agent, par exemple `AGENTS.md` | Connaître les commandes, contraintes et conventions utiles au travail. |
| `CONTRIBUTING.md` | Contribuer : branches, changements, tests, commits et revue. |
| `SECURITY.md` | Savoir comment signaler une vulnérabilité, avec un canal réel et une politique validée. |
| `LICENSE` et notices | Connaître les droits effectivement accordés et les obligations applicables. |
| Documentation d’architecture | Comprendre composants, interfaces et flux essentiels. |
| ADR et spikes | Retrouver décisions, preuves et explorations. |
| Roadmap ou tickets | Comprendre les priorités, prochaines actions et critères d’acceptation. |
| Passation | Reprendre le travail à partir d’un état concret. |

- Ne crée pas toute cette arborescence pour un petit projet : plusieurs rôles peuvent tenir dans un seul document.
- Évite trois listes concurrentes dans `TODO`, roadmap et tickets. Désigne une source de suivi principale.
- Lie la documentation au changement qu’elle explique et retire les instructions devenues fausses.
- Ne présente pas une intention comme une fonctionnalité déjà disponible.
- N’invente pas une adresse de signalement, une politique de support ou une licence. Propose les éléments manquants pour arbitrage.
- Un wiki généré peut aider à naviguer ; il doit rester vérifiable à partir du code et ne pas remplacer les décisions maintenues dans le dépôt.
- Si un outil documentaire utilise une API externe, vérifie autorisation, confidentialité et coût avant de lui transmettre le code.

## Conventions techniques et graphiques

Observe les usages dominants avant de formaliser les règles : noms des fichiers et symboles, organisation des modules, API, erreurs, logs, migrations et gestion des dépendances.

Pour une interface, repère composants existants, tokens, typographie, couleurs, états interactifs et exigences d’accessibilité. Réutilise-les. Si aucune identité graphique n’est décidée, propose une base cohérente ; ne présente pas tes préférences comme une charte approuvée.

Automatise les conventions qui s’y prêtent avec les outils déjà adoptés. Évite de reformater tout le dépôt au milieu d’un changement ciblé.

## Modèles disponibles à la demande

- [ADR](../templates/ADR.md) et [spike](../templates/SPIKE.md) pour `DEC-01`.
- [README](../templates/README.md) pour `DOC-01`.
- [Architecture](../templates/ARCHITECTURE.md) pour les repères de `REC-02` et `DOC-01`.
- [Contribution](../templates/CONTRIBUTING.md) et [sécurité](../templates/SECURITY.md) pour `GOV-01`.

Ces modèles sont des aides, pas des fichiers à créer obligatoirement. Inspecte l’existant, décide si le rôle est nécessaire, puis complète au bon endroit. Pour une licence manquante, propose un arbitrage ; ce pack ne choisit pas les droits du propriétaire.

## Dette révélée et conservation

Une dette mise en évidence par un changement peut justifier une [proposition de refactoring](../templates/REFACTORING.md), liée au ticket et aux preuves ; un ADR n’est utile que si le choix est structurant. Les TODO, skips et POC conservés pour une raison suivie ne sont pas des rebuts. À la fin d’un spike, consigne le devenir du prototype et applique cette décision lors de l’audit d’hygiène.

## Référence UX/UI

Pour une interface, la [référence design](../templates/DESIGN.md) ou son équivalent lie parcours, composants, tokens, contenu et exigences de validation. Le [module UX/UI](08-ux-ui-design.md) décrit sa reconnaissance et son entretien. Préserve une source principale ; les preuves d’un changement restent dans le suivi de celui-ci.
