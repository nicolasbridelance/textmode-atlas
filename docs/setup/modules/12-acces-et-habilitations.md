# Accès et habilitations — droits voulus, effectifs et vérifiés

Trois plans sont à examiner séparément : permissions de l’agent, accès infrastructure/CI/services, et autorisations des utilisateurs du produit. Un accès technique disponible ne confère pas l’autorisation de réaliser une action.

## Inventorier

Le [registre des droits](../templates/DROITS.md) décrit sujets ou rôles, ressources, actions, environnement, droits attendus et droits effectifs, source directe ou héritée, justification et responsable. Identifie comptes humains, comptes de service, bots, accès publics et privilèges d’administration sans reproduire secrets ou données privées dans le dépôt.

Inspecte les paramètres accessibles : dépôt et branches, organisations/groupes, workflows, cloud, BDD, stockage, API/MCP et application. Ne déduis pas les droits effectifs du seul fichier de configuration local ; les règles distantes et héritages peuvent différer.

Sépare « conforme à l’attendu », « écart confirmé » et « non vérifié ». L’absence d’accès est un obstacle, jamais une preuve de sécurité. Un registre sensible doit rester dans un support à visibilité appropriée ; le repo peut contenir un résumé et le lien autorisé.

## Vérifier les autorisations du produit

Les restrictions d’UI ne protègent pas une ressource côté serveur. Examine l’autorisation sur l’action et sur l’objet effectivement demandé, notamment entre utilisateurs, organisations ou tenants. Authentication et autorisation sont des contrôles distincts.

Avec identités/données de test et périmètre autorisé, vérifie des accès permis et refusés : utilisateur anonyme, rôle insuffisant, objet d’un autre utilisateur/tenant, privilège retiré et session/jeton expiré lorsque pertinents. Le refus doit aussi éviter de divulguer les données concernées. Ne teste pas la production ou des comptes tiers sans autorisation.

## Cycle de vie des droits

Documente attribution, validation, expiration, rotation pertinente, départ/changement de rôle et révocation. Préfère des périmètres limités, identités distinctes et accès temporaires lorsque les besoins et outils le permettent. Réutilise les mécanismes d’authentification sécurisés existants ; ne construis pas une crypto ou gestion de jetons ad hoc.

Pour tout écart, prépare la remédiation, l’impact et la vérification. Une modification peut couper un service ou le seul accès d’administration : prévois récupération et continuité avant exécution. Modifier les droits distants, révoquer un compte ou changer une visibilité suit les autorisations existantes.

## Revoir et tracer

Désigne responsable, fréquence adaptée et événements de revue : intégration/déploiement, nouveau rôle, accès partagé, changement de fournisseur, départ, incident ou exposition de secret. Une fréquence proposée n’est pas un contrôle planifié déjà actif.

Chaque revue conserve date, périmètre, configuration observée, preuves expurgées, écarts, décision et prochaine revue. La [posture cyber](13-posture-cyber.md) consolide les risques ; le [suivi de changement](../templates/CHANGEMENT.md) revalide les droits affectés. Ne coche pas une revue sur la seule présence d’un principe de moindre privilège.
