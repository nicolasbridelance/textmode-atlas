# Protocole d’exécution

## 1. Le suivi fait foi

- `CHECKLIST.md` : état courant et critères d’acceptation des actions. Une ligne par action, identifiant stable.
- `JOURNAL.md` : historique daté des constats, changements et vérifications, avec le même identifiant.
- `REPRISE.md` : position courante, action interrompue et prochaine étape ; une courte vue de reprise.
- `modules/` : références consultées à la demande ; pas de suivi dans ces fichiers.

Réutilise un suivi existant s’il assure les mêmes fonctions. Dans ce cas, remplace ces fichiers par des liens explicites vers les emplacements retenus : ne maintiens pas deux états concurrents. Le kit contient des modèles, pas un audit déjà réalisé.

## 2. Initialise avant les changements techniques

Lis le cadre et effectue la reconnaissance. Renseigne contexte et baseline. Après `REC-01`, traite `INS-01` avec le fragment d’amorçage pour relier le kit aux instructions réellement utilisées. Les lignes initiales sont des points à examiner : précise leur portée, leurs dépendances et leurs critères selon le projet. Ne coche rien par supposition.

Définis le périmètre et un budget raisonnable d’installation. La reconnaissance précède les corrections ; les actions suivantes se choisissent selon leurs dépendances et leur utilité.

Le champ « Exigence » prend les valeurs `essentiel`, `utile` ou `optionnel`. Les exigences initiales sont des valeurs de départ : leur adaptation doit être justifiée dans le journal. Ne dégrade pas une exigence uniquement pour pouvoir clôturer.

## 3. États autorisés

| État | Signification | Condition |
| --- | --- | --- |
| À examiner | Applicabilité et état réel encore inconnus | État initial du modèle. |
| À faire | Besoin confirmé et critère précisé | Action dans le périmètre, dépendances connues. |
| En cours | Action commencée | Journal ouvert ; prochaine vérification connue. |
| À vérifier | Changement réalisé mais non validé | Ne pas présenter comme terminé. |
| Vérifié | Critère satisfait | Preuve datée, état du code et périmètre vérifié. |
| Bloqué | Impossible de progresser | Cause, dépendance ou arbitrage ; action de déblocage. |
| Différé | Report volontaire | Justification, ticket ou déclencheur de reprise. |
| Sans objet | Non applicable à ce dépôt | Justification concrète ; absence d’accès ne suffit pas. |

Transitions habituelles : `À examiner → À faire → En cours → À vérifier → Vérifié`. Une vérification peut se faire immédiatement. Un mécanisme déjà présent peut passer directement de `À examiner` à `Vérifié`, après contrôle et preuve. Un échec renvoie à `En cours` ou `Bloqué`. Une preuve devenue invalide rouvre l’action à `À vérifier`.

## 4. Boucle pour chaque action

1. **Choisir** une action dont les dépendances sont satisfaites. Préférer les blocages puis les améliorations utiles au prochain travail.
2. **Lire** son critère, le module indiqué et les instructions applicables aux fichiers concernés. Inscrire les lectures utiles dans le journal, avec leur version ou commit si disponible.
3. **Préparer** : confirmer autorisation, état initial et risques concrets. Passer à `En cours`, ouvrir une entrée datée et noter le résultat attendu.
4. **Exécuter** un changement limité. Noter les fichiers touchés et la raison du changement. Si aucun changement n’est nécessaire, le dire.
5. **Vérifier** le critère avec une commande ou une inspection adaptée. Consigner le résultat réel, y compris échec ou non-exécution. Séparer les défauts préexistants des régressions.
6. **Tracer** : compléter l’entrée avec preuve, résultat, état du code et limites. Lier cette entrée depuis la checklist, puis mettre à jour son état.
7. **Préparer la suite** : actualiser `REPRISE.md` avec la prochaine action, ou les actions indépendantes si blocage. Continuer tant que le périmètre le permet.

Avant une opération longue, un changement d’action ou une interruption, enregistre un checkpoint. Le travail et la mise à jour du suivi ne sont pas atomiques : après un arrêt inattendu, confronte journal et diff avant de reprendre.

## 5. Une preuve exploitable

Pour une commande : commande exacte sans secret, répertoire, date/heure avec fuseau, environnement utile, code de sortie, résultat et durée si utile. Pour une inspection : fichier ou configuration inspectée, constat précis et version observée.

Indique le commit testé ou « working tree de <commit>, modifications locales : <fichiers> ». Une preuve avant modification ne valide pas le code après modification. Un run distant doit avoir un lien et son SHA. Un log local non sauvegardé doit être présenté comme local.

Ne colle pas tous les logs. Conserve un résumé et un lien vers une sortie expurgée si elle est nécessaire. N’inscris jamais de jeton, valeur de secret ou URL authentifiée dans le suivi.

Les exemples et placeholders ne sont pas des preuves. « Lu », « configuré » et « testé » sont trois résultats différents.

## 6. Dépendances et nouvelles actions

Garde les identifiants stables. Si un constat nécessite du travail distinct, crée une nouvelle ligne avec un nouvel ID, critère, exigence, dépendance et lien vers le constat d’origine. Une correction importante ne se cache pas dans le journal d’une autre action.

Une décision humaine possède une proposition concrète et une question précise. Un blocage n’arrête que les actions qui en dépendent. Un spike ou ADR est lié aux actions qu’il éclaire ; le journal ne remplace pas son contenu.

## 7. Clôture et entretien

`FIN-01` peut être `Vérifié` lorsque toutes les actions essentielles sont `Vérifié` ou `Sans objet` justifié, et que les autres ont une disposition explicite. Si une essentielle reste bloquée ou différée, conclus « installation partielle » avec son effet concret ; ne déclare pas le dépôt prêt.

La clôture concerne la préparation du travail, pas une garantie de qualité globale du produit. Le journal est conservé ; la checklist présente l’état actuel. À chaque reprise, vérifie les dérives avant de réutiliser les preuves. Rouvre les lignes concernées par une modification de runtime, bootstrap, CI ou autre dépendance ; n’invalide pas tout sans raison.

Dans Git, versionne le suivi avec les changements correspondants lorsque les commits sont autorisés. Distingue toujours local, commité, poussé et publié. Si une sauvegarde distante n’est pas autorisée, signale le travail seulement local.

Plusieurs intervenants doivent se répartir explicitement les actions et éviter d’écraser le même fichier de suivi. Ce protocole n’autorise pas à lui seul l’exécution parallèle ou la délégation.

## 8. Après l’installation : routine de changement

La checklist d’installation mesure la préparation du dépôt. La routine de code dure au-delà de sa clôture : lis [conception](modules/06-conception-du-code.md) avant le travail et la validation, puis [hygiène](modules/07-hygiene-apres-stabilisation.md) après stabilisation fonctionnelle.

Trace chaque occurrence dans le suivi de sa tâche ou PR avec le [modèle de changement](templates/CHANGEMENT.md), sans remettre toute l’installation à zéro. Le fragment d’instructions active ces déclencheurs. Les actions `COD-01`, `HYG-01` et `MEC-01` vérifient leur installation ; elles ne prétendent pas que tous les futurs changements ont été contrôlés.

Lie les décisions importantes au journal ou au suivi principal. Si une interruption laisse un audit ou une validation en attente, indique la référence du changement et l’action restante dans la reprise. Chaque nouveau nettoyage a ses propres preuves.

Pour une interface, les actions `UX-01`, `UI-01` à `UI-03` et `A11Y-01` établissent les repères et une vérification initiale. Leur non-applicabilité doit être justifiée pour un projet sans interface. Les preuves de changements ultérieurs sont conservées dans le volet UI du modèle de changement. Ne rejoue pas toute la reconnaissance, mais revalide ce que le diff affecte.

Les actions `MCP-01` à `MCP-03` et `CST-01` à `CST-04` rendent visibles capacités, dépenses et limites. Une donnée économique inaccessible reste inconnue et liée à une action ; l’agent ne prétend pas à un audit complet des comptes. Les changements ultérieurs utilisent le volet intégrations/coûts de CHANGEMENT et rouvrent les actions de préparation uniquement si leurs critères deviennent invalides.

Les actions API/ACC/CYB/LEG vérifient la connaissance des contrats, accès, risques et obligations. La qualification peut rester incomplète si les informations manquent, mais les inconnues doivent être attribuées et leur effet sur la livraison visible. Une preuve de scan n’est pas une certification. Les revues récurrentes vivent dans le suivi du changement et les registres, sans rejouer toute l’installation.

La posture cyber privilégie conception sûre, classification/gestion des données, analyse/traitement des risques et cartographie actuelle. CYB-03 à CYB-05 vérifient ces axes ; CYB-02 couvre l’exploitation complémentaire. Les changements mettent à jour données/risques/carte avant leur clôture, avec preuves ou limites explicites.
