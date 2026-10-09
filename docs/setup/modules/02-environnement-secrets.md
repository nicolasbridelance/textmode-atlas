# Environnement secrets

Référence à lire uniquement pour les actions correspondantes de la checklist.

## Installe un environnement reproductible

Objectif : un nouvel environnement peut installer, démarrer et vérifier le projet avec une procédure documentée.

- Utilise le gestionnaire de paquets et le lockfile du projet. N’introduis pas un second gestionnaire.
- Rends explicites les versions nécessaires au bon fonctionnement et réutilise le mécanisme existant pour les fixer.
- Centralise les commandes usuelles dans les scripts déjà adoptés : installation, démarrage, contrôle rapide, tests et build.
- Explique les prérequis, ports, services locaux et données de démonstration indispensables.
- Rends les scripts relançables lorsque c’est possible ; évite les installations globales et les modifications de machine non nécessaires.
- Si Codespaces ou un devcontainer existe, vérifie son bootstrap. N’en ajoute un que s’il simplifie réellement la reproduction du projet.
- Les commandes automatiques de création ou démarrage d’environnement ne doivent ni publier ni modifier la production.

**Vérification :** teste la procédure dans un environnement isolé lorsque c’est raisonnable. Sinon, précise ce que tu as effectivement vérifié et ce qui reste à confirmer. Une documentation relue ne prouve pas qu’un bootstrap fonctionne.

## Secrets, configuration et données

- Sépare configuration publique, configuration locale et secrets.
- Si nécessaire, fournis un `.env.example` avec noms, descriptions et valeurs factices ; ne copie jamais un `.env` réel.
- Documente les variables obligatoires, les valeurs par défaut et l’endroit où les secrets doivent être provisionnés, sans leurs valeurs.
- Vérifie les exclusions Git. Un fichier ignoré peut avoir déjà été suivi : inspecte les chemins concernés, pas les valeurs des secrets.
- Vérifie que tests, logs, captures, rapports et artefacts ne divulguent pas de secrets ou de données personnelles.
- Utilise des données synthétiques pour les tests et démonstrations.
- Limite les droits des jetons et des workflows à ce qui est nécessaire ; ne change pas les droits distants sans autorisation.
- Si un secret semble exposé, signale son emplacement sans le reproduire. Retirer le fichier ne révoque pas le secret : la rotation et une éventuelle correction d’historique sont des actions distinctes à coordonner.

Un scan de secrets ou de dépendances apporte une vérification ciblée, pas une garantie globale de sécurité.

## Services externes et coût de l’environnement

Repère les configurations d’intégrations sans exposer leurs secrets ; applique le [module MCP](09-mcp-integrations.md) avant activation ou test. VM/Codespaces, stockage et services locaux hébergés peuvent consommer même sans trafic produit : relève leur état et leur payeur dans le [suivi des coûts](10-couts-et-consommation.md). Ne change pas un plan ou un service payant au seul motif du bootstrap.

Les secrets ne sont qu’une catégorie de données à protéger. Pour jeux de données, logs, exports, caches et copies, applique aussi la [classification et les règles de gestion](13-posture-cyber.md) définies pour le projet.
