# API et interfaces — contrats et évolution

À lire pour les API exposées/consommées et les frontières internes modifiées : HTTP, RPC, événements, fichiers, CLI, bibliothèques ou schémas persistés. Ne réduis pas « interface » à l’écran utilisateur.

## Cartographier les contrats

Dans le [registre de contrats](../templates/CONTRATS.md), identifie producteur, consommateurs connus, propriétaire, environnement et source maintenue : schéma, types, specification ou documentation réelle. Une API exposée publiquement peut avoir des consommateurs inconnus.

Pour chaque frontière importante, relève entrées/sorties, types, unités, formats, champs obligatoires/optionnels, erreurs, garanties et effets de bord. Pour les interfaces externes, complète avec authentification et autorisation, données sensibles, timeout, limites, pagination, retry, idempotence réellement disponible et coût. Pour événements et traitements asynchrones, explicite livraison, ordre, doublons et rejeu lorsque pertinents.

N’introduis pas une spécification parallèle si le projet possède déjà une source de contrat. Ne suppose pas qu’une validation de types locale protège la frontière d’entrée en production.

## Faire évoluer sans casser silencieusement

Avant changement, examine consommateurs et garanties. Classe l’impact : compatible, incompatible ou inconnu. Renommer un champ, modifier une erreur, retirer une route ou changer une sémantique peut casser même si le build du producteur réussit.

Pour une rupture, prépare migration, coexistence/versionnement lorsque utiles, dépréciation et retour arrière. Les délais et engagements sont ceux décidés par le projet, pas une politique inventée. Informe les responsables selon les instructions autorisées ; préparer le message n’autorise pas son envoi.

Évite les adaptations « juste pour le test » qui rendent le contrat plus permissif. Pour une API tierce, consulte la documentation officielle actuelle avant de changer son usage et date les exigences observées. Coordonne droits et coût avec les modules correspondants.

## Vérifier les frontières

Teste les comportements pertinents : cas normal, entrée invalide, champs manquants et limites, erreurs, refus d’accès, répétition et scénario de compatibilité. Les tests de contrat doivent vérifier une promesse utile au consommateur ; ils ne doivent pas simplement recopier les types du producteur.

Pour une intégration distante, respecte cible, droits, données et budget. Des mocks peuvent valider la logique locale mais ne démontrent pas que le fournisseur actuel respecte le contrat. Une vérification non exécutée reste visible.

Consigne référence du code et du contrat, consommateurs couverts, commandes/observations, résultats et limites. En cas de changement, lie ces preuves au [suivi de changement](../templates/CHANGEMENT.md). Rouvre les contrôles affectés après modification.
