# UX, UI et design — comprendre, concevoir et vérifier

À lire lors de la reconnaissance d’un produit avec interface, puis pour tout changement affectant ce que l’utilisateur voit, comprend ou fait : composants, navigation, texte, styles, formulaire, permissions ou comportement visible. Adapte aux interfaces web, desktop, mobile ou CLI ; marque les contrôles réellement sans objet avec justification.

Le résultat attendu est une interface cohérente, compréhensible et utilisable pour les tâches visées. Un build vert ne prouve pas l’utilisabilité ; une capture ne prouve pas le fonctionnement d’un parcours.

## 1. Reconnaissance UX et sources du design

- Identifie utilisateurs, tâches essentielles, contexte d’usage et plateformes prises en charge. Distingue faits établis, contraintes et hypothèses ; n’invente pas de recherche utilisateur.
- Repère les parcours existants et leur critère de réussite : point d’entrée, étapes, choix, sortie et récupération après erreur. Examine ce qui doit rester compatible.
- Retrouve la source de vérité : composants, styles, tokens, charte, maquettes, textes et éventuel catalogue de composants. Les chemins ou liens doivent être réels et accessibles ; une maquette non consultée n’est pas une référence vérifiée.
- Inspecte l’interface effectivement rendue et ses comportements, lorsque les outils et l’environnement le permettent. Si c’est impossible, note l’obstacle et laisse la validation ouverte.
- Retrouve les exigences d’accessibilité et de support du projet. En leur absence, documente les vérifications de base et propose un objectif ; ne prétends pas à une conformité formelle.
- Renseigne la [référence design](../templates/DESIGN.md) au bon endroit ou lie son équivalent existant. Ne crée pas de charte concurrente à partir de préférences personnelles.

## 2. Concevoir à partir du parcours

Pour la tâche concernée, décris le besoin et le résultat attendu avant de choisir la mise en page. Réduis les étapes et les demandes d’informations inutiles sans cacher les conséquences ou supprimer une confirmation utile.

Rends visibles l’action principale, l’état courant et la manière de revenir ou de récupérer une erreur. Préserve la saisie lorsque c’est pertinent. Évite les contrôles décoratifs, actions muettes, données fictives présentées comme réelles et promesses non implémentées.

Un changement local compatible avec les conventions n’exige pas une nouvelle charte. Une refonte de parcours, d’identité ou de système de composants se propose avec périmètre et raison ; applique les autorisations existantes avant de l’exécuter. Une esquisse peut éclairer le choix sans constituer une décision approuvée.

## 3. UI et système de design

| Sujet | Règle de travail |
| --- | --- |
| Hiérarchie visuelle | Titre, contenu, action et aide se distinguent ; les priorités du parcours guident la mise en page. |
| Typographie et contenu | Échelle et vocabulaire cohérents ; longueur réelle des textes prise en compte, unités et libellés explicites. |
| Couleurs | Réutilise la palette et les rôles sémantiques ; ne fais pas reposer une information uniquement sur la couleur. |
| Espacements et mise en page | Réutilise les tokens et rythmes existants ; évite les valeurs isolées sans raison. |
| Composants | Réutilise composant et variante existants avant d’en créer un. Une différence visuelle locale ne justifie pas une seconde version indépendante. |
| Iconographie et effets | Fonction et sens compréhensibles ; icônes seules avec nom accessible ; animations et effets servent l’usage. |
| Responsive | Adapte organisation et priorités aux tailles supportées, sans perte d’action ou de contenu essentiel. Ne te limite pas à réduire les dimensions. |
| Navigation et formulaires | Contrôles cohérents, labels explicites, validation compréhensible et récupération adaptée. |

Si aucun système n’existe, pars d’une base limitée et cohérente adaptée au produit. Documente les choix, leur statut proposé ou approuvé, puis extrais des tokens/composants lorsque la réutilisation le justifie. N’ajoute pas une bibliothèque de composants uniquement pour formaliser une petite interface.

## 4. États à couvrir

Pour chaque composant ou parcours touché, examine les états applicables :

- initial, vide et sans résultats ; distinguer absence de données et absence d’accès ;
- chargement et traitement en cours, avec protection contre les actions répétées si nécessaire ;
- succès et confirmation de l’effet réel ;
- erreurs de saisie, réseau et service, avec suite possible ;
- désactivé, permission insuffisante ou session expirée ;
- hover, focus, sélection et activation lorsqu’ils s’appliquent ;
- contenu long, données limites, traduction et format local lorsque le produit les supporte.

Ne crée pas tous ces états dans tous les composants. Consigne ceux qui ont un effet sur le parcours et justifie les non-applicabilités importantes. Simuler un état avec des données synthétiques est acceptable si la simulation et sa portée sont explicites.

## 5. Accessibilité et confort d’usage

Vérifie les contrôles pertinents à l’interface :

- parcours clavier, ordre de focus, focus visible et récupération du focus après une action ou fermeture de dialogue ;
- sémantique des contrôles, titres, noms accessibles, labels, instructions et association des erreurs ;
- lisibilité et contrastes selon les exigences adoptées ; information compréhensible sans couleur seule ;
- zoom, agrandissement du texte et reflow pertinent, sans perte de contenu ou action ;
- cibles interactives adaptées au contexte et alternatives au hover seul ;
- annonces utiles de changements d’état et vérification au lecteur d’écran si le périmètre l’exige ;
- réduction des animations et absence de dépendance à un mouvement pour comprendre l’état ;
- feedback compréhensible et préservation des données saisies lorsque possible.

Utilise les éléments natifs appropriés avant de reconstruire des interactions complexes. Les audits automatiques signalent une partie des problèmes ; ils ne remplacent pas clavier, lecture, parcours et jugement humain. Note exactement les contrôles exécutés et les moyens utilisés. Une exigence inaccessible à tes outils reste non vérifiée, pas validée par approximation.

## 6. Boucle de réalisation et validation

1. **Comprendre** le parcours, ses utilisateurs et le critère d’acceptation.
2. **Concevoir** en réutilisant les références ; lister états et tailles à vérifier.
3. **Implémenter** un changement limité avec composants et tokens existants.
4. **Ouvrir et examiner** l’interface réellement rendue, pas seulement son code.
5. **Essayer** le parcours concerné, ses erreurs utiles, le responsive et les contrôles d’accessibilité pertinents.
6. **Corriger et recontrôler** les problèmes observés ; une capture avant correction ne valide pas l’état après.
7. **Tracer** preuves, limites et arbitrages dans le [suivi de changement](../templates/CHANGEMENT.md). Réexaminer l’obsolescence induite des composants, tokens et documents.

La validation est proportionnée au diff. Pour une correction de texte, vérifie les écrans affectés et la mise en page ; ne relance pas tous les parcours du produit sans raison. Pour un formulaire ou une navigation, teste les interactions et leur résultat.

Si l’environnement ne permet pas l’examen visuel ou une interaction essentielle, indique précisément le manque, les contrôles alternatifs réalisés et la prochaine validation requise. Ne fabrique pas une preuve et ne déclare pas le changement visuellement vérifié.

## 7. Preuves et limites

Consigne pour chaque vérification utile : date/fuseau, commit ou working tree, cible/environnement, écran/parcours, taille de viewport ou appareil, navigateur/runtime utile, état simulé ou réel, action tentée, résultat attendu et observé.

Les captures expurgées soutiennent les constats visuels. Les essais soutiennent les comportements observés. Les tests automatisés soutiennent leur périmètre déclaré. Une comparaison avant/après exige des états et données comparables ; inspecte les différences, ne régénère pas les références aveuglément.

Un parcours essayé par l’agent n’est pas une étude auprès des utilisateurs. Un prototype n’est pas une fonctionnalité livrée. Un scan sans erreur n’est pas une certification d’accessibilité. Indique ces limites lorsque pertinentes.

## 8. Entretien et frontière des outils

Automatise ce qui apporte un retour stable : tests de composants et parcours essentiels, règles de tokens pertinentes, détection ciblée de problèmes d’accessibilité et comparaison visuelle lorsque l’environnement est reproductible. Documente les variations tolérées et le mécanisme de revue des références.

Le jugement conserve parcours, compréhension des textes, hiérarchie, pertinence des composants et arbitrages esthétiques. N’ajoute pas un outil par sujet. Lors d’un changement structurant, actualise la source de design et les décisions ; conserve le lien aux preuves sans dupliquer une nouvelle charte.
