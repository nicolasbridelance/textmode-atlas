# Git livraison

Référence à lire uniquement pour les actions correspondantes de la checklist.

## Git, PR et livraison

- Préserve les conventions de branches et de commits existantes.
- Avant un commit, examine le diff et les fichiers indexés ; inclus uniquement le travail voulu.
- Ne supprime, ne stash et ne réinitialise pas les changements d’autrui pour nettoyer ton environnement.
- Prépare des changements cohérents et assez petits pour être relus.
- Dans une PR, explique le problème, le comportement obtenu, les vérifications et les limites matérielles.
- Vérifie les autorisations avant push, PR, fusion, tag ou publication. Une autorisation de push ne vaut pas automatiquement autorisation de déploiement.
- Ne contourne pas les contrôles ou protections de branche.
- Pour une livraison autorisée, identifie version, artefact, cible, éventuelles migrations, contrôle de bon fonctionnement et procédure de retour arrière adaptée.

Dans un environnement éphémère, rends visible ce qui existe uniquement localement. Avant une interruption, privilégie une sauvegarde durable selon les autorisations disponibles ; si elle manque, signale précisément le travail non sauvegardé sans le pousser de ta propre initiative.

## Après stabilisation d’un changement

Déclenche l’[audit d’hygiène](07-hygiene-apres-stabilisation.md). Sépare le nettoyage additionnel de la fonctionnalité lorsqu’il existe et respecte les autorisations de commit. Ne confonds pas validation locale, commit, push et intégration. Réexécute les contrôles concernés après nettoyage et lie les preuves aux états respectifs.


Avant une livraison affectée par un contrat, un risque ou une obligation, vérifie les décisions et blocages dans les modules [contrats](11-api-et-contrats.md), [posture](13-posture-cyber.md) et [conformité](14-lois-normes-et-conformite.md). La présence du pack n’autorise pas la publication.
