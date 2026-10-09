# Coûts et consommation — où passe l’argent ?

Objectif : savoir **qui paie quoi, ce qui est mesuré, ce que coûte un run ou un usage et ce qui peut continuer à coûter au repos**. Ce volet concerne le projet et les ressources de développement, y compris le travail de l’agent. Il ne constitue pas une comptabilité complète de l’organisation.

## 1. Cartographier les postes et les payeurs

Renseigne le [registre de coûts](../templates/COUTS.md) avec les ressources réellement utilisées ou nécessaires. Cherche notamment :

| Famille | Postes à examiner |
| --- | --- |
| Développement | Codespaces/VM, stockage persistant, volumes, outils et licences nécessaires au travail. |
| CI et livraison | Minutes de calcul, runners, matrices, builds, tests lourds, artefacts et previews. |
| Infrastructure | Serveurs, fonctions, conteneurs, BDD, cache, GPU, stockage, sauvegardes, réseau et trafic sortant. |
| Services métier | API, recherche, paiements ou traitements externes, abonnements et engagements minimums. |
| IA et agent | Tokens selon catégories réellement facturées, modèles, images/audio, outils, indexation, embeddings et appels répétés. |
| MCP et intégrations | Hébergement du serveur, abonnement d’accès et services déclenchés derrière chaque outil. |
| Exploitation | Logs, métriques, traces, conservation, domaines et ressources conservées après fin d’une expérimentation. |

Pour chaque poste : fournisseur/service, ressource, environnement, compte payeur sous une désignation non sensible, responsable, devise, unité, source de prix datée, consommation et périmètre de facturation. Lie les tableaux de bord privés sans exposer identifiants sensibles ou accès signés.

Vérifie si la facturation est propre au projet ou partagée. Une ressource absente du code peut encore être facturée. Une ressource présente dans la configuration peut ne pas être déployée. Sans accès aux comptes, consigne la limite et la donnée à obtenir ; n’annonce pas « coût zéro ».

## 2. Séparer les natures de chiffres

| Nature | Ce qu’elle démontre |
| --- | --- |
| Facturé | Montant émis pour une période et un périmètre identifiés. |
| Mesuré | Usage observé dans un compteur ; pas nécessairement déjà facturé. |
| Estimé | Usage multiplié par un tarif ou modèle de coût explicite, avec hypothèses. |
| Prévisionnel | Scénario futur fondé sur volumes, architecture et utilisation supposés. |
| Inconnu | Donnée inaccessible ou non mesurée ; action nécessaire pour la connaître. |

Documente décalages de remontée, crédits, quotas inclus, remise, engagements, taxes et autres éléments lorsqu’ils sont pertinents et connus. Ne mélange pas un prix catalogue avec un prix contractuel. Un quota inclus réduit éventuellement le montant supplémentaire ; il reste une consommation finie.

Ne somme pas des devises différentes sans conversion datée et justifiée. Ne double-compte pas un poste déjà inclus dans une facture agrégée. Les frais d’abonnement sont distincts des unités marginales : ne suppose pas qu’un abonnement couvre une API ou une autre plateforme.

Toute source tarifaire externe doit être consultée et datée avant estimation ; les exports et conditions du compte sont préférés lorsque disponibles. N’invente pas un prix. Ce pack ne contient aucun tarif fournisseur.

## 3. Combien coûte le projet, un run et un usage ?

Distingue fixe/périodique et variable. Un modèle minimal est :

`Coût de période estimé = frais fixes + somme(unités consommées × tarif applicable) + autres frais identifiés − crédits applicables`

Adapte ce modèle aux paliers, minimums et engagements réellement connus ; indique ses omissions. Présente séparément décaissement facturé, estimation de consommation et allocation éventuelle des frais fixes.

Définis ce qu’est un run : build CI, job batch, session de développement, traitement ou run d’agent. Définis aussi l’unité utile au produit : requête, document produit, minute traitée ou tâche réussie. Un « utilisateur » seul ne définit pas un coût si ses usages varient.

Pour un run ou un usage : relève les ressources déclenchées, consommation, prix applicables et durée. Inclue échecs, retries, appels internes, indexation et stockage induit. Pour le coût par succès, donne `coût total du périmètre / nombre de résultats réussis` sur une période comparable ; si zéro succès, le ratio est non défini, pas nul.

Présente si nécessaire coût marginal et coût complet alloué séparément. L’allocation des ressources partagées doit avoir une règle visible ; les parts non attribuables restent « non allouées ».

Pour une prévision, montre plusieurs volumes utiles avec hypothèses : trafic, fréquence, cache, durée, rétention et disponibilité. Ne transforme pas un petit échantillon en garantie de coût à grande échelle.

## 4. Mesurer sans créer une nouvelle usine

Réutilise compteurs, exports de facturation et télémétrie existants. Pour les dépenses importantes, identifie projet/environnement et corrèle run ou opération avec les unités consommées lorsque possible. Les tags aident l’allocation mais ne garantissent pas une facture complète.

Compare période, total fournisseur et estimation locale. Explique les écarts connus et le reste non attribué. Mesure aussi le coût de la télémétrie : logs, cardinalité et rétention peuvent être des postes significatifs. N’enregistre pas prompts, réponses ou données personnelles intégrales pour compter des unités.

Un dashboard sans alimentation récente n’est pas une mesure. Consigne source, date de collecte, période et fréquence de rafraîchissement. Si aucun compteur n’existe, propose l’instrumentation minimale utile au prochain arbitrage.

## 5. Budgets et garde-fous

Retrouve les budgets et autorisations existants. Documente seuil, période/devise, responsable de la réponse et portée : projet, environnement, run ou opération. Les seuils sans valeur validée restent proposés.

Une alerte n’est pas un plafond dur. Un quota n’est pas toujours un plafond financier. Vérifie l’effet réel du mécanisme : notification, ralentissement, blocage, arrêt ou aucune action automatique. N’annonce pas un budget garanti sur la seule présence d’une alerte.

Avant une opération nouvelle, longue, payante ou susceptible de boucler : estime son périmètre, fixe une limite de temps/volume/tentatives adaptée et vérifie l’autorisation de dépense. Un budget inconnu n’autorise pas une dépense illimitée. Continue les travaux indépendants et prépare un arbitrage concret si nécessaire.

Ne modifie pas moyens de paiement, plan, plafond ou abonnement sans autorisation. Pour une tâche à coût variable, prévois un arrêt maîtrisé sans perte de travail. La documentation d’un seuil n’active pas une limite technique : contrôle sa configuration si elle est dans le périmètre.

## 6. Hygiène et entretien

Lors de l’[audit d’hygiène](07-hygiene-apres-stabilisation.md), repère ressources de POC, previews, environnements idle, volumes et stockage orphelins, doublons et rétention devenue inutile. Propose un gain estimé avec source et limites.

Une ressource inutilisée peut contenir du travail non sauvegardé, des données ou un contrat de conservation. Prépare inventaire et sauvegarde ; arrêt, réduction et suppression suivent les autorisations existantes. N’optimise pas en supprimant une garantie de disponibilité ou des données par défaut.

Un changement de modèle, fournisseur, trafic, CI, rétention, cache ou architecture doit déclencher une revue des coûts. Consigne estimation avant, mesure après lorsque possible, plafond réel et limites dans le [suivi de changement](../templates/CHANGEMENT.md). La checklist d’installation ne valide pas automatiquement les dépenses futures.

## 7. Demander un budget, puis piloter l’enveloppe

**L’agent a le devoir de préparer une demande lorsqu’une dépense utile n’est pas couverte par une autorisation existante.** Il ne doit ni renoncer silencieusement à une option pertinente, ni lancer la dépense et demander après coup.

1. **Chercher l’autorisation existante** : enveloppe, payeur, période, opérations et conditions. Une enveloppe générale ne couvre que son périmètre ; si elle couvre l’action, ne redemande pas la même validation.
2. **Préparer le résultat reviewable sans dépenser** : plan, configuration proposée, critères de réussite et estimation sourcée. Continue l’analyse locale et les travaux indépendants. Si un pilote lui-même est payant, demande d’abord une petite enveloppe d’expérimentation.
3. **Chiffrer une demande** avec le [modèle de budget](../templates/DEMANDE_BUDGET.md) : objectif, livrable, cible, payeur, durée, coût prévu et plafond, unités, retries, hypothèses et alternative moins coûteuse. Un chiffre central n’est pas un plafond.
4. **Soumettre un arbitrage précis** au décideur habilité. Si le prix ou la consommation est inconnu, propose un pilote borné avec sources et mécanismes de limite, plutôt qu’un montant inventé ou une autorisation illimitée.
5. **Attendre la décision pour la dépense dépendante**. Silence, délai écoulé ou reprise de session ne valent pas accord. L’agent n’approuve pas sa propre demande sauf délégation explicite et vérifiable couvrant cet arbitrage. Un accord budgétaire n’autorise pas, à lui seul, une publication, l’envoi de données ou une suppression.
6. **Enregistrer l’accord réel**, ses conditions et sa source. Les opérations autorisées peuvent ensuite avancer sans validation à chaque appel tant qu’elles restent dans l’enveloppe et le périmètre.
7. **Suivre et anticiper** : consommation, dépenses engagées ou runs en cours, décalage des compteurs, reste estimé et prévision de fin. Une lecture de compteur ancienne ne justifie pas de dépenser tout le reste apparent.
8. **Arrêter ou redemander avant dépassement prévisible**. N’augmente pas le plafond et ne bascule pas vers un autre compte pour continuer. Préserve le travail, informe du résultat partiel et prépare une demande d’extension avec le coût de la suite.
9. **Clore l’enveloppe** : résultat, consommation réellement connue, facture si disponible, écarts, ressources encore actives et dépenses résiduelles. Une fin de run ne ferme pas automatiquement l’infrastructure qui lui survit.

Les alertes de fournisseur ou plafonds applicatifs peuvent réagir trop tard pour garantir un maximum strict. Pour un plafond exigeant, documente le contrôle réellement disponible, les coûts déjà engagés et le risque résiduel ; si la garantie n’est pas démontrable, dis-le dans la demande avant lancement.

Pour éviter les interruptions inutiles, privilégie une enveloppe limitée mais suffisante pour une tâche ou un spike, plutôt qu’une demande à chaque requête. Le budget en temps/calcul du spike et le budget financier doivent être cohérents. Un quota inclus est aussi une enveloppe à suivre, avec sa date de renouvellement et son risque de consommation supplémentaire.
