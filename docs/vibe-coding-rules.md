# Règles de Vibe Coding

Le tableau est scindé en deux volets indissociables :

- **L'Artisanat du Code (Micro-Design)** : comment l'agent doit concevoir la modification.
- **L'Écologie du Dépôt (Hygiène Post-Commit & Dé-bloat)** : ce que l'agent doit élaguer et auditer immédiatement après chaque stabilisation.

## Volet 1 : L'Artisanat du Code (Micro-Design & Pureté de la Feature)

| Principe | L'objectif (Ce qu'on veut) | Le biais de l'IA (Ce qu'elle fait mal) | Le "Prompt Magique" |
|---|---|---|---|
| Complexité Cyclomatique | Réduire les chemins et conditions imbriquées. | Génère du code "spaghetti" (cascades de if/else). | "Réduis la complexité cyclomatique, utilise des retours anticipés (early returns)." |
| KISS (Keep It Simple, Stupid) | Viser la solution la plus simple et directe. | Produit de l'over-engineering (abstractions excessives). | "Applique KISS : retire les couches d'abstraction spéculatives et privilégie le chemin direct." |
| YAGNI (You Aren't Gonna Need It) | Ne développer que le strict nécessaire, rien "au cas où". | Ajoute des paramètres et de la flexibilité spéculative non demandée. | "Applique YAGNI : retire la configurabilité inutile, résous uniquement le besoin actuel." |
| DRY (Don't Repeat Yourself) | Centraliser la logique pour faciliter la maintenance. | Copie-colle des blocs entiers par paresse contextuelle. | "Applique DRY : identifie la logique dupliquée et extrais-la dans une fonction réutilisable." |
| SRP (Single Responsibility) | Un module / fonction = une seule responsabilité précise. | Crée des "God functions" mixant validation, métier et transport. | "Applique SRP : découpe cette fonction pour séparer validation, logique métier et effets de bord." |
| No Magic Numbers / Strings | Donner un sens explicite à chaque valeur brute. | Hardcode des constantes et des chaînes magiques dans la logique. | "Élimine les magic numbers et strings : remplace-les par des constantes nommées ou des enums." |
| Fail Fast | Valider les invariants et planter immédiatement en amont. | Laisse le code invalide progresser et masque les erreurs sous un gros catch. | "Applique Fail Fast : valide les arguments dès la première ligne et rejette explicitement les cas invalides." |
| Fonctions Pures & Immutabilité | Empêcher les effets de bord indésirables. | Mute discrètement les arguments reçus ou altère l'état global. | "Utilise des fonctions pures : ne mute aucun paramètre, retourne une nouvelle structure de données." |
| Injection de Dépendances | Fournir les dépendances (BDD, API) depuis l'extérieur. | Instancie en dur les services externes au cœur du domaine métier. | "Applique l'injection de dépendances : passe les services externes en paramètres ou constructeur." |
| Loi de Déméter | Limiter le couplage à la structure interne des objets (le chaînage n'est pas fautif en soi — API fluentes et builders restent légitimes). | Chaîne des appels profonds sur la structure interne d'un objet (`user.getOrder().getPayment().process()`). | "Respecte la Loi de Déméter : élimine le couplage à la structure interne, délègue à l'objet direct — sans proscrire les API fluentes volontaires." |
| Code Auto-Documenté | Rendre le code lisible par lui-même. | Nomme mal ses variables (`tmp`, `res`) et surcompense par des commentaires triviaux. | "Écris du code auto-documenté : utilise des noms explicites et supprime les commentaires paraphrasant le code." |

## Volet 2 : L'Écologie du Dépôt (Hygiène Post-Commit & Élagage Organique)

> **Règle d'or de ce volet** : Le commit fonctionnel valide un nouvel état de référence. Immédiatement après, l'agent doit se poser la question : « Maintenant que ce commit est intégré, qu'est-ce qui dans l'ensemble du projet n'a plus de raison d'exister ? »

| Principe | L'objectif (Ce qu'on veut) | Le biais de l'IA (Ce qu'elle fait mal) | Le "Prompt Magique" |
|---|---|---|---|
| Obsolescence Induite par le Commit (Post-Commit Pruning) | Élaguer instantanément tout ce que la nouvelle implémentation rend caduc. | Empile la nouvelle logique à côté de l'ancienne sans détruire les chemins obsolètes. | "Le commit fonctionnel est posé : identifie et détruis tout ce qu'il rend obsolète (anciens adaptateurs, routes désuètes, wrappers temporaires)." |
| Dead Code Elimination (Code Mort & Orphelin) | Ne conserver strictement que le code branché et accessible. | Conserve des blocs commentés ou des fonctions orphelines "par précaution". | "Supprime tout le code mort et orphelin. Ne commente rien : Git conserve l'historique intégral." |
| Scaffolding & POC Cleanup (Démontage d'Échafaudage) | Effacer les traces d'expérimentation dès qu'une solution est trouvée. | Laisse traîner des `_v2`, des scripts de test ad hoc et des fichiers d'exploration. | "Démonte l'échafaudage : supprime les fichiers temporaires, scripts de spike et helpers créés durant la recherche." |
| Test & Fixture Decay (Cohérence du Harnais de Test) | Maintenir un ensemble de tests qui reflète l'état réel du système. | Laisse des tests ignorés (skip), des mocks obsolètes ou des snapshots devenus faux. | "Purge les tests obsolètes, les fixtures inutilisées et les mocks orphelins liés aux comportements disparus. Si un test `skip` porte une raison documentée (bug tiers, flakiness connue), signale-le au lieu de le supprimer." |
| Dependency & Config Hygiene (Légèreté du Manifeste) | Garantir que chaque ligne de config et dépendance sert le présent. | Ajoute des packages pour tester une idée sans jamais désinstaller les rejetés. | "Vérifie `package.json`/`requirements.txt` et `.env` : désinstalle les dépendances orphelines et purge les variables d'environnement mortes." |
| Silence Radio Post-Debug (Propreté Télémétrique) | Préserver la lisibilité de la console et des métriques en production. | Sème des `console.log("here")` ou `print(res)` partout sans les retirer. | "Supprime tous les logs de debug et prints d'investigation. Ne conserve que les logs structurels d'erreur." |
| Backlog Decay (Synchronisation de la Réalité) | Garder la documentation et les listes de tâches alignées sur le réel. | Laisse s'accumuler des `// TODO` vieux de six mois et des checklists désynchronisées. | "Purge les `// TODO`/`// FIXME` devenus caducs (résolus ou couverts par le commit). Laisse intacts ceux qui référencent une dette suivie ailleurs (ticket, issue) — signale-les plutôt que de les supprimer." |
| Dette Révélée & Proactivité de Refactoring (Devoir d'alerte) | Détecter activement la pourriture du code et proposer le bon refactoring au bon moment. | Conservatisme passif : n'ose jamais suggérer un refactor par peur de déranger ou de casser, laissant la gangrène s'installer. | "Ne sois pas conservateur : audite la zone touchée. Si le code est devenu plus lourd ou fragile, propose spontanément le refactoring nécessaire, chiffre le gain (lignes/complexité) et défends ton plan." |
| Découplage Sémantique des Commits (Deux Temps, Deux Commits) | Préserver la traçabilité Git (bisect, reverts propres). | Mélange dans un même commit la modification métier, le nettoyage de fichiers et du formatage. | "Isole strictement : valide d'abord le commit fonctionnel (`feat`/`fix`), puis valide l'élagage dans un second commit (`chore(hygiene)`)." |

## Garde-fous : Autonomie encadrée

Ces principes gagnent en fiabilité s'ils s'accompagnent de limites claires, pour éviter que l'agent ne franchisse la ligne entre « hygiène » et « décision arbitraire irréversible » :

- **Validation avant qualification de "code mort"** : dans un code dynamique (réflexion, injection de dépendances, dispatch piloté par configuration/feature flag), l'absence de référence directe ne suffit pas à prouver l'inutilité. Fais tourner la suite de tests avant de purger, et signale les cas ambigus plutôt que de trancher seul.
- **Seuil de confirmation** : au-delà d'un certain volume de purge (ex. plus de quelques dizaines de lignes ou plusieurs fichiers touchés), liste les éléments visés et attends une validation explicite avant de committer, même pour un `chore(hygiene)`.
- **Distinction dette intentionnelle vs dette oubliée** : un `// TODO` ou un test `skip` référençant un ticket ou une raison documentée n'est pas un rebut — signale-le au lieu de le supprimer.
- **Proposition de refactoring ≠ exécution automatique** : le « devoir de proposition » (dernière ligne du tableau ci-dessus) reste une *suggestion argumentée* soumise à validation, jamais une exécution silencieuse — pour ne pas entrer en contradiction avec YAGNI/KISS (Volet 1).

## Répartition Hook vs Prompt : la frontière du mécanisable

**Critère de décision** : une règle appartient au **hook** (linter, CI, `pre-commit`) si elle est *décidable sans comprendre l'intention métier* — un outil peut trancher oui/non par analyse syntaxique, comptage ou pattern matching. Elle reste dans le **prompt** (jugement de l'agent) dès qu'elle exige de comprendre *pourquoi* le code existe, ce qui reste acceptable dans son contexte, ou d'arbitrer un compromis.

### Volet 1 — ce qui est mécanisable

| Principe | Déterministe / outillable (hook, CI) | Reste du jugement (prompt) |
|---|---|---|
| Complexité Cyclomatique | Seuil de complexité cyclomatique/cognitive mesuré par l'outil (ESLint `complexity`, `radon cc`, `lizard`) → échec de build si dépassé. | Choisir *où* et *comment* réduire (early return vs extraction de fonction) sans casser la lisibilité. |
| KISS | Aucune mesure directe fiable ; les proxys (complexité, profondeur d'imbrication `max-depth`) donnent une alerte. | Juger si une abstraction est réellement spéculative ou justifiée par le contexte. |
| YAGNI | Détection des exports/paramètres jamais utilisés (`ts-prune`, `vulture`, `eslint no-unused-vars`). | Décider si une option "flexible" répond à un besoin réel ou anticipé à tort. |
| DRY | Détection de duplication par similarité de blocs (`jscpd`, PMD CPD, `flake8` + plugins). | Décider si factoriser vaut la complexité ajoutée (parfois 2 duplications valent mieux qu'une mauvaise abstraction). |
| SRP | Proxys mécaniques : lignes par fonction/classe, nombre de méthodes (`max-lines-per-function`, `radon cc`). | Jugement sémantique : la fonction mélange-t-elle vraiment plusieurs responsabilités métier ? |
| No Magic Numbers / Strings | 100 % mécanisable : `eslint no-magic-numbers`, `ruff PLR2004`. Auto-fix possible. | Choisir un nom de constante ou d'enum pertinent. |
| Fail Fast | Détection des `catch` vides ou des validations manquantes en tête de fonction (règles de lint dédiées). | Décider quel invariant vérifier et quel message d'erreur est utile. |
| Fonctions Pures & Immutabilité | Partiellement outillable (`eslint-plugin-functional`, interdiction de réassignation `no-param-reassign`). | Juger si une mutation locale est acceptable ou si elle fuit hors du scope. |
| Injection de Dépendances | Non mécanisable directement. | Entièrement du jugement architectural. |
| Loi de Déméter | Partiellement outillable via règles de lint personnalisées (comptage des `.` chaînés). | Distinguer couplage fautif et API fluente volontaire (builder, chaînage de promesses). |
| Code Auto-Documenté | Détection de noms courts/génériques par regex (`tmp`, `data\d?`, `res`) — bruyant, beaucoup de faux positifs. | Juger si un commentaire est réellement redondant avec le code. |

### Volet 2 — ce qui est mécanisable

| Principe | Déterministe / outillable (hook, CI) | Reste du jugement (prompt) |
|---|---|---|
| Dead Code Elimination | Détection de candidats (`ts-prune`, `vulture`, `deptrac`, `unused-imports`) — liste ce qui n'est référencé nulle part statiquement. | Confirmer qu'un candidat n'est pas atteint dynamiquement (réflexion, DI, config, plugin) avant suppression. |
| Scaffolding & POC Cleanup | Détection de patterns de nommage (`_v2`, `.spike.`, `.tmp.`, `.bak`) par recherche de fichiers. | Décider si le fichier est vraiment un déchet d'expérimentation ou une variante encore utile. |
| Test & Fixture Decay | Liste mécanique des tests `skip`/`xfail` et leur ancienneté (`git blame`, rapport de couverture). | Décider si un test skip a une raison encore valable (bug tiers ouvert) ou est mort. |
| Dependency & Config Hygiene | 100 % mécanisable : `depcheck`, `npm outdated`, `pip-autoremove`, variables d'env non référencées (grep croisé code/`.env`). | Arbitrer une dépendance gardée volontairement pour une version future proche. |
| Silence Radio Post-Debug | 100 % mécanisable : `eslint no-console`, `ruff` règle `T201` (print). Auto-fix possible. | Distinguer un log de debug d'un log structurel de production. |
| Backlog Decay | Liste mécanique des `TODO`/`FIXME` avec ancienneté via `git blame` (`leasot` ou équivalent). | Décider si le TODO référence une dette suivie ailleurs (ticket) ou est simplement oublié. |
| Dette Révélée & Refactoring | Déclencheur mécanique possible : seuil de complexité/duplication franchi entre deux commits (delta de métriques en CI, ex. SonarQube quality gate). | Le pitch de refactoring (cible, signal, gain, plan) reste une production de jugement pure. |
| Découplage Sémantique des Commits | Vérifiable a posteriori : un commit qui mélange suppressions massives et logique métier peut être détecté par un hook `commitlint`/`pre-commit` (ratio ajouts/suppressions, fichiers touchés). | Décider comment scinder proprement les deux commits. |

### Ce que ça implique concrètement

- **Le hook est un filtre, pas un juge final.** Il produit une *liste de candidats* (dead code, TODO anciens, dépendances inutilisées) — c'est toujours l'agent (ou l'humain) qui décide de la suppression, conformément aux garde-fous ci-dessus.
- **Tout ce qui est 100 % mécanisable** (magic numbers, `console.log`/`print`, dépendances orphelines, duplication détectée) **doit sortir du prompt** : le répéter à chaque session gaspille du contexte pour un résultat qu'un `pre-commit` obtient de façon fiable et gratuite.
- **Le prompt se concentre sur l'irréductible** : SRP, YAGNI, Loi de Déméter, arbitrage dette/refactoring — tout ce qui suppose de comprendre l'intention du code, pas seulement sa forme.

## Synthèse : Le Déclencheur Automatique à intégrer dans l'Agent

Si tu veux injecter cette logique dans le prompt de ton agent (ou son `CLAUDE.md` / `.cursorrules`), utilise cette consigne globale :

### Protocole Post-Commit : L'Incinérateur d'Obsolescence & Devoir de Proposition

Dès qu'un commit fonctionnel est validé :

1. **Incinération mécanique (Autonome, sous garde-fou) :**
   Examine le diff et supprime le code mort, les fichiers temporaires,
   les logs de debug et les fixtures orphelines — après validation par les tests
   et sous réserve de rester sous le seuil de confirmation (voir Garde-fous ci-dessus).
   Au-delà de ce seuil, ou en cas de doute, liste les éléments visés et attends
   le feu vert avant de committer.
   Commit dédié : `chore(hygiene): purge post-[commit]`.

2. **Audit & Proposition proactive (Brise le conservatisme) :**
   Tu as un **devoir de conseil**. Ne sois pas passif : ne suppose JAMAIS que l'état
   actuel doit rester tel quel par défaut.
   
   Pose-toi systématiquement ces questions :
   - "Est-ce que ce commit a augmenté la friction pour la suite ?"
   - "Est-ce qu'on commence à accumuler trop de cas particuliers dans ce module ?"
   - "Est-ce qu'une abstraction s'impose maintenant (Règle de 3) ?"

   👉 **Si un seuil est franchi, PROPOSE SPONTANÉMENT le refactoring.**
   Ne te contente pas d'un timide "tout va bien". Présente ton pitch de refactoring :
   - **La cible :** Module / fonction concerné(e).
   - **Le signal d'alerte :** Duplication, complexité cyclomatique, couplage fort.
   - **Le gain projeté :** "Supprime ~40 lignes, isole la dépendance X, simplifie les tests futurs".
   - **L'action proposée :** Un plan en 2-3 étapes claires, prêt à être exécuté au prochain feu vert.