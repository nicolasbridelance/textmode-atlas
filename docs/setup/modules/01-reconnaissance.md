# Reconnaissance

Référence à lire uniquement pour les actions correspondantes de la checklist.

## Reconnaissance : regarde où tu mets les pieds

Avant toute modification, établis une photographie de départ.

### Dépôt et travail en cours

- Identifie la racine, les instructions applicables, la branche courante, le commit de départ, les remotes et l’état du working tree.
- Repère les modifications suivies et les fichiers non suivis sans afficher leur éventuel contenu sensible.
- Vérifie si d’autres travaux sont en cours. Utilise une branche ou un worktree isolé si cela facilite la cohabitation.
- Si Git n’est pas disponible, note la limite et adapte la traçabilité ; ne l’initialise pas automatiquement dans un projet existant.

### Produit et architecture

- Que fait le projet ? Pour qui ? Quel comportement doit rester stable ?
- Où sont les points d’entrée, les composants principaux et les données ?
- Quelles sont les interfaces externes, les contraintes de compatibilité et les zones sensibles ?
- Quelle est la stack réellement utilisée, d’après les manifests, lockfiles, scripts et configurations ?
- Où sont les conventions de nommage, de structure, d’API et, si pertinent, les règles graphiques ?
- Qu’est-ce qui est explicitement hors périmètre ?

Ne remplace pas une stack ou une architecture simplement parce que tu en connais mieux une autre.

### Environnement et exploitation

- Identifie OS, versions des runtimes, gestionnaire de paquets, outils disponibles, services requis et contraintes réseau.
- Repère conteneurs, devcontainers, scripts de bootstrap et environnements de test.
- Lis les workflows CI/CD et identifie les commandes qu’ils exécutent réellement.
- Distingue développement, test, staging et production ; vérifie les destinations avant toute commande ayant des effets externes.
- Pour GitHub, vérifie les paramètres accessibles si tu y es autorisé. Une absence d’accès signifie « non vérifié », pas « non configuré ».

### État initial mesuré

Lance les contrôles existants pertinents, après examen des scripts : installation reproductible, build, lint, types et tests selon la stack. Évite une suite longue ou coûteuse sans en avoir estimé l’utilité.

Consigne commande, environnement, résultat et durée approximative. Sépare les échecs préexistants des régressions que tu introduiras. Un test non exécuté n’est pas un test réussi.

À ce stade, donne un point de situation court : fonctionnement compris, état initial, obstacles, puis les quelques améliorations que tu vas réaliser. Ne t’arrête pas à ce rapport si la suite est autorisée.


Pour approfondir les frontières, droits et exposition, consulte les modules [contrats](11-api-et-contrats.md), [accès](12-acces-et-habilitations.md), [posture cyber](13-posture-cyber.md) et [applicabilité](14-lois-normes-et-conformite.md).
