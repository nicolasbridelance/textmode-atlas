# Checklist — état courant de l’installation

Installation locale en cours. Les preuves figurent dans JOURNAL.md.

## Contexte

- Dépôt : C:/02_Projets/01_ACTIFS/textmode-atlas
- Date / intervenant : 2026-10-09, Europe/Paris — Codex
- Branche / commit : fix/windows-restoration / 9ca145a (base e8f36933)
- Environnement : Windows 11, PowerShell, Git Bash
- À préserver : quatre fichiers suivis modifiés et deux fichiers non suivis du snapshot principal ; snapshot visualisations dans son worktree séparé.
- Périmètre : restauration locale, kit, dépendances et vérifications ; aucune publication ni dépense de service.
- Autorisation : « carte blanche » de l’utilisateur pour préparer ce dépôt.
- Baseline : [EV-001](JOURNAL.md#ev-001).
- Suivi : CHECKLIST.md, JOURNAL.md, REPRISE.md dans ce dossier.
- État global : développement local validé sous Linux ; audit global encore partiel, ARJ natif Windows absent ([EV-005](JOURNAL.md#ev-005)).

## Actions

Les dépendances indiquent l’ordre de départ ; ajuste-les avec justification selon le dépôt. Une dépendance `Sans objet` justifiée peut être considérée satisfaite ; une dépendance bloquée ne l’est pas.

| ID | Exigence | Dépend de | Référence | Critère d’acceptation | État | Preuve / blocage |
| --- | --- | --- | --- | --- | --- | --- |
| REC-01 | essentiel | — | [Module](modules/01-reconnaissance.md) | Instructions, branche, commit, diff initial et travaux à préserver consignés. | Vérifié | [EV-001](JOURNAL.md#ev-001) |
| INS-01 | essentiel | REC-01 | [Amorçage](templates/AGENTS.fragment.md) | Instructions actives intégrées sans écrasement ; chemin de lecture vérifié, chargement automatique confirmé ou limite explicite. | Vérifié | [EV-001](JOURNAL.md#ev-001) |
| REC-02 | essentiel | REC-01 | [Module](modules/01-reconnaissance.md) | But, points d’entrée, stack, contraintes et périmètre compris à partir des sources. | Vérifié | [EV-001](JOURNAL.md#ev-001) |
| REC-03 | essentiel | REC-01 | [Module](modules/01-reconnaissance.md) | Commandes existantes examinées ; baseline exécutée ou obstacles précisément consignés. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| ENV-01 | essentiel | REC-02, REC-03 | [Module](modules/02-environnement-secrets.md) | Installation existante contrôlée ; versions et commandes reproductibles documentées. | À vérifier | [EV-003](JOURNAL.md#ev-003) ; validation restante détaillée dans la reprise. |
| ENV-02 | essentiel | ENV-01 | [Module](modules/02-environnement-secrets.md) | Démarrage vérifié sur cible locale ; prérequis et arrêt documentés. | Vérifié | [EV-005](JOURNAL.md#ev-005) ; périmètre Linux et explorer local, limites documentées. |
| ENV-03 | optionnel | ENV-01 | [Module](modules/02-environnement-secrets.md) | Si pertinent, bootstrap isolé/devcontainer relancé ; limites consignées. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| SEC-01 | essentiel | REC-01 | [Module](modules/02-environnement-secrets.md) | Configuration, exclusions et fichiers suivis concernés inspectés sans exposer les valeurs. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| SEC-02 | utile | SEC-01 | [Module](modules/02-environnement-secrets.md) | Variables nécessaires et provisioning documentés ; exemple factice si utile. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| SEC-03 | utile | REC-03 | [Module](modules/03-qualite-tests.md) | Scans adaptés contrôlés ; périmètre, constats et remédiations suivis. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| QUA-01 | essentiel | REC-03 | [Module](modules/03-qualite-tests.md) | Commande de contrôle pertinente exécutée ; résultats et écarts à la baseline expliqués. | Vérifié | [EV-005](JOURNAL.md#ev-005) ; périmètre Linux et explorer local, limites documentées. |
| QUA-02 | utile | QUA-01 | [Module](modules/03-qualite-tests.md) | Hooks utiles relançables et installation documentée, ou absence justifiée. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| QUA-03 | utile | REC-03 | [Module](modules/03-qualite-tests.md) | CI inspectée ; commandes, déclencheurs, permissions et effets externes décrits. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| QUA-04 | utile | QUA-03 | [Module](modules/03-qualite-tests.md) | Statut distant et règles obligatoires vérifiés si accessibles ; sinon limite explicite. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| TST-01 | essentiel | REC-02, REC-03 | [Module](modules/03-qualite-tests.md) | Contrats essentiels et commande de tests identifiés ; suite pertinente exécutée ou blocage déclaré. | Vérifié | [EV-005](JOURNAL.md#ev-005) ; périmètre Linux et explorer local, limites documentées. |
| TST-02 | optionnel | TST-01 | [Module](modules/03-qualite-tests.md) | Mutation ciblée évaluée : utilité, budget et suite concrète, ou non-applicabilité justifiée. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| DOC-01 | essentiel | ENV-01, QUA-01 | [Module](modules/04-decisions-documentation.md) | Point d’entrée documentaire donne les commandes réelles et liens utiles. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| DOC-02 | utile | REC-02 | [Module](modules/04-decisions-documentation.md) | Source unique des tâches/priorités désignée ; écarts utiles liés à des actions. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| DEC-01 | utile | REC-02 | [Module](modules/04-decisions-documentation.md) | Décisions et inconnues structurantes repérées ; ADR/spikes seulement si justifiés. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| CNV-01 | utile | REC-02 | [Module](modules/04-decisions-documentation.md) | Conventions techniques et graphiques existantes retrouvées et référencées. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| GOV-01 | utile | REC-02 | [Module](modules/04-decisions-documentation.md) | Licence, notices, contribution et canal sécurité inspectés ; décisions manquantes proposées. | À vérifier | Repères documentés, revue complète encore ouverte ; [EV-002](JOURNAL.md#ev-002). |
| GIT-01 | essentiel | REC-01 | [Module](modules/05-git-livraison.md) | Règles de commits/PR, autorisations et effets des pushs identifiés ; pas de publication implicite. | Vérifié | [EV-001](JOURNAL.md#ev-001) |
| GIT-02 | utile | GIT-01 | [Module](modules/05-git-livraison.md) | Droits/protections distants inspectés si accessibles ; modifications éventuelles autorisées séparément. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| REL-01 | optionnel | QUA-03, GIT-01 | [Module](modules/05-git-livraison.md) | Si livraison dans le périmètre : cible, validation et retour arrière documentés. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| COD-01 | essentiel | REC-02, INS-01 | [Conception](modules/06-conception-du-code.md) | Revue de conception référencée dans les instructions actives ; suivi par changement choisi, critères adaptés aux conventions. | Vérifié | [EV-001](JOURNAL.md#ev-001) |
| HYG-01 | essentiel | GIT-01, COD-01 | [Hygiène](modules/07-hygiene-apres-stabilisation.md) | Déclencheur après stabilisation, seuil applicable, garde-fous et suivi documentés ; chemin vers modèle et reprise vérifié. | Vérifié | [EV-001](JOURNAL.md#ev-001) |
| MEC-01 | utile | QUA-01, COD-01 | [Contrôles](modules/03-qualite-tests.md) | Règles classées en checks ou signaux/jugement ; contrôles utiles exécutés, bruit et limites consignés sans nouvel outil systématique. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| UX-01 | essentiel | REC-02 | [UX/UI](modules/08-ux-ui-design.md) | Pour une interface : utilisateurs, tâches, parcours essentiels et hypothèses identifiés ; sans objet justifié sinon. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| UI-01 | utile | UX-01, CNV-01 | [Référence design](templates/DESIGN.md) | Sources de design consultées, composants/tokens/textes retrouvés ; décisions et propositions distinguées sans charte concurrente. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| UI-02 | essentiel | UX-01, ENV-02, INS-01 | [UX/UI](modules/08-ux-ui-design.md) | Interface examinée et parcours prioritaire essayé sur l’état identifié, ou validation explicitement bloquée ; routine et suivi actifs. | Vérifié | [EV-005](JOURNAL.md#ev-005) ; périmètre Linux et explorer local, limites documentées. |
| UI-03 | utile | UI-01, UI-02 | [UX/UI](modules/08-ux-ui-design.md) | États utiles et tailles supportées recensés ; contrôles représentatifs réalisés et limites consignées. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| A11Y-01 | essentiel | UX-01, UI-02 | [UX/UI](modules/08-ux-ui-design.md) | Exigences connues ; contrôles applicables de clavier/focus/sémantique et lisibilité exécutés, limites et obstacles explicités sans fausse conformité. | À vérifier | [EV-003](JOURNAL.md#ev-003) ; validation restante détaillée dans la reprise. |
| MCP-01 | essentiel | REC-02, SEC-01 | [MCP](modules/09-mcp-integrations.md) | Intégrations configurées/exposées inventoriées, provenance/cibles/droits connus ; absence ou limites justifiées. | À vérifier | Repères documentés, revue complète encore ouverte ; [EV-002](JOURNAL.md#ev-002). |
| MCP-02 | utile | MCP-01 | [Registre MCP](templates/MCP.md) | Capacité utile testée sur cible autorisée, ou test non exécuté explicitement ; arguments et preuve expurgés. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| MCP-03 | essentiel | MCP-01, INS-01 | [MCP](modules/09-mcp-integrations.md) | Règles d’usage, données sortantes, effets, reprises et coûts référencés dans les instructions actives. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| CST-01 | essentiel | REC-02 | [Coûts](modules/10-couts-et-consommation.md) | Postes et comptes payeurs recensés, infra/dev/CI/IA/MCP inclus ; montants connus et inconnus distingués, source de suivi désignée. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| CST-02 | utile | CST-01 | [Registre coûts](templates/COUTS.md) | Sources de consommation et période rapprochées des coûts disponibles ; couverture, écarts et absence de mesures explicités. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| CST-03 | essentiel | CST-01, INS-01 | [Coûts](modules/10-couts-et-consommation.md) | Budgets/autorisations retrouvés ou inconnues déclarées ; limites et réaction définies pour opérations variables, alerte/plafond distingués. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| CST-04 | utile | CST-01, CST-02 | [Coûts](modules/10-couts-et-consommation.md) | Run et unité utile définis ; coût marginal/complet estimé ou mesuré avec hypothèses, retries, frais fixes et postes non alloués visibles. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| CST-05 | essentiel | CST-03 | [Demande de budget](templates/DEMANDE_BUDGET.md) | Décideur et chemin d’arbitrage identifiés ; demande chiffrée préparée si dépense non couverte, accord réel tracé avant lancement et règle d’extension connue. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| API-01 | essentiel | REC-02 | [Contrats](modules/11-api-et-contrats.md) | Frontières importantes et sources de contrat identifiées ; producteurs/consommateurs, garanties et inconnues consignés. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| API-02 | utile | API-01, TST-01 | [Registre](templates/CONTRATS.md) | Contrats prioritaires vérifiés sur comportements utiles et compatibilité ; limites et contrôles manquants explicites. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| API-03 | utile | API-01, INS-01 | [Contrats](modules/11-api-et-contrats.md) | Analyse d’impact, versionnement/dépréciation et revue par changement reliés aux instructions. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| ACC-01 | essentiel | REC-01, MCP-01 | [Accès](modules/12-acces-et-habilitations.md) | Droits agent/infra/produit attendus et effectifs recensés ; héritages et accès non vérifiables distingués. | À vérifier | Repères documentés, revue complète encore ouverte ; [EV-002](JOURNAL.md#ev-002). |
| ACC-02 | essentiel | ACC-01, TST-01 | [Registre droits](templates/DROITS.md) | Pour autorisations produit : cas permis/refusés prioritaires vérifiés côté serveur avec données de test, ou blocage explicite ; sans objet justifié sinon. | Vérifié | [EV-005](JOURNAL.md#ev-005) ; périmètre Linux et explorer local, limites documentées. |
| ACC-03 | utile | ACC-01 | [Accès](modules/12-acces-et-habilitations.md) | Attribution/révocation et revue périodique/événementielle définies, responsables et écarts suivis sans changement distant implicite. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| CYB-01 | essentiel | REC-02, ACC-01 | [Posture cyber](modules/13-posture-cyber.md) | Security by design activé : besoins, frontières, risques et contrôles étudiés avant implémentation, critères de validation reliés aux décisions. | À vérifier | Repères documentés, revue complète encore ouverte ; [EV-002](JOURNAL.md#ev-002). |
| CYB-02 | utile | CYB-01 | [Posture](templates/POSTURE_CYBER.md) | Détection, réponse et récupération ont responsables et preuves disponibles ; exercices manquants distingués des procédures présentes. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| LEG-01 | essentiel | REC-02 | [Lois/normes](modules/14-lois-normes-et-conformite.md) | Contexte et sujets d’applicabilité qualifiés ou questions ouvertes attribuées ; catégories loi/norme/contrat/guide distinguées. | Vérifié | [EV-002](JOURNAL.md#ev-002) |
| LEG-02 | utile | LEG-01, CYB-01 | [Applicabilité](templates/CONFORMITE.md) | Exigences retenues liées à sources actuelles, responsables et preuves ; écarts et blocages de publication visibles, aucune conformité inventée. | Différé | Revoir après les services locaux ; [EV-002](JOURNAL.md#ev-002). |
| CYB-03 | essentiel | REC-02, SEC-01 | [Données](templates/POSTURE_CYBER.md) | Catégories et sensibilité des données connues ou inconnues visibles ; règles de gestion par classe définies et application vérifiée sur périmètre déclaré. | À vérifier | Repères documentés, revue complète encore ouverte ; [EV-002](JOURNAL.md#ev-002). |
| CYB-04 | essentiel | CYB-01, CYB-03 | [Risques](templates/POSTURE_CYBER.md) | Analyse et traitement suivis par IDs/propriétaires ; initial/résiduel, preuves, décisions et réexamens distingués. | À vérifier | Repères documentés, revue complète encore ouverte ; [EV-002](JOURNAL.md#ev-002). |
| CYB-05 | essentiel | API-01, CYB-03 | [Cartographie](templates/ARCHITECTURE.md) | Cartographie composants/flux/données/frontières liée aux contrats et risques, actualité vérifiée ou limites visibles ; responsable et mise à jour par changement définis. | À vérifier | Repères documentés, revue complète encore ouverte ; [EV-002](JOURNAL.md#ev-002). |
| FIN-01 | essentiel | Toutes les essentielles | [Module](modules/00-cadre.md) | Diff revu, preuves actuelles, état de sauvegarde exact et reprise exploitable ; critères de clôture satisfaits. | À vérifier | [EV-003](JOURNAL.md#ev-003) ; validation restante détaillée dans la reprise. |

## Ajouter une action

Copie la structure d’une ligne avec un ID nouveau et stable. Lie la preuve à une ancre du journal, par exemple `[EV-001](JOURNAL.md#ev-001)` une fois cette entrée créée. Mets le détail du blocage dans le journal, pas dans une cellule interminable.

Ne remplace pas `Vérifié` par une simple case cochée : il faut distinguer travail fait, validation manquante, report et non-applicabilité.
