# Lois, normes et engagements — applicabilité et preuves

Ce module impose une démarche de qualification, pas une liste d’obligations universelles. Le dépôt seul ne suffit pas à déterminer le cadre légal de l’organisation. L’agent prépare l’analyse ; les arbitrages et déclarations de conformité relèvent des responsables compétents.

## 1. Qualifier le contexte

Identifie pays et marchés visés, exploitant, utilisateurs, données et finalités, secteur, modalités de distribution, hébergement/prestataires, rôle contractuel et exigences clients. Marque les informations absentes et qui doit les confirmer. Le fait que le développeur soit en France ne tranche pas tout le périmètre.

Examine les familles pertinentes : données personnelles et confidentialité, traceurs, droits sur contenus et logiciels, accessibilité, obligations sectorielles, cybersécurité des organisations/produits, systèmes d’IA et engagements contractuels. Le RGPD, des cadres comme NIS2/CRA ou les règles sur l’IA sont des sujets à qualifier selon le produit et l’organisation, jamais des obligations présumées à partir d’un mot-clé.

Ne résume pas des calendriers ou seuils réglementaires de mémoire. Consulte les textes officiels et autorités compétentes dans leur état actuel avant toute conclusion d’applicabilité, échéance ou exigence précise. Une norme payante non consultée ne peut pas être présentée comme entièrement évaluée.

## 2. Séparer les catégories

| Catégorie | Ce qu’il faut enregistrer |
| --- | --- |
| Loi ou règlement | Texte/version, juridiction, critères d’application, exigences et dates pertinentes vérifiées. |
| Norme ou référentiel | Version, périmètre choisi, exigences retenues et motif : volontaire, contrat ou exigence applicable vérifiée. |
| Contrat ou politique interne | Clause ou règle réellement acceptée, périmètre, propriétaire et engagements. |
| Guide de bonnes pratiques | Référence utile à la conception ; pas une obligation légale par simple citation. |
| Certification ou attestation | Périmètre, organisme/preuve, validité et restrictions ; ne pas en inventer une. |

Une norme volontaire peut être rendue pertinente par un contrat ou une règle applicable : vérifie ce lien. « Inspiré de », « contrôlé sur quelques exigences », « conforme » et « certifié » sont des affirmations différentes.

## 3. Registre d’applicabilité et exigences

Dans le [registre conformité](../templates/CONFORMITE.md), note pour chaque sujet : source officielle datée, contexte, statut applicable/non applicable/à confirmer avec justification, responsable de validation, exigence précise et preuve attendue. En cas d’applicabilité inconnue, prépare la question et les éléments disponibles ; ne tranche pas arbitrairement.

Si des données personnelles sont traitées, examine avec les responsables concernés rôle des acteurs, finalités, données nécessaires, durées, destinataires/prestataires, droits et mesures de sécurité ; transforme les obligations effectivement qualifiées en actions. Ne collecte pas les données sensibles pour remplir la documentation.

Pour les droits de contenu/licences, relie provenance, autorisations et notices aux éléments distribués. Pour l’accessibilité et les autres normes, relie exigences retenues et contrôles exécutés. Une dépendance réputée libre n’est pas automatiquement compatible avec tout usage ; une mention LICENSE ne suffit pas à vérifier tout le corpus.

## 4. Remédiation et revue

Chaque écart a action, responsable, échéance validée et preuve de clôture. Une analyse juridique manquante peut bloquer la mise en production concernée sans arrêter les travaux locaux indépendants. Documente ce blocage ; ne cherche pas à le masquer sous une exception technique.

Revois l’applicabilité lors de nouveaux marchés, utilisateurs/données, finalités, fournisseurs, contrats, fonctionnalités IA, redistribution ou changement de texte. Désigne le responsable et la fréquence de veille adaptée. Ne prétends pas qu’une veille est active si seul un document la décrit.

Repères officiels consultés le 9 octobre 2026 : [CNIL, guide sécurité](https://www.cnil.fr/fr/guide-de-la-securite-des-donnees-personnelles) et [CNIL, qualification des rôles](https://www.cnil.fr/fr/rgpd-comment-bien-identifier-son-role). Ces ressources aident à qualifier mesures et responsabilités ; elles ne déterminent pas automatiquement les obligations d’un projet inconnu. Les sources spécifiques devront être consultées lorsque son contexte est établi.
