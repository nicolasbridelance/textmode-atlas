Rapport d'Analyse Exhaustif sur l'Architecture, le Rendu et la Préservation de l'Art en Mode Texte Historique
Introduction et Fondements de l'Archéologie Numérique
La préservation de l'art numérique en mode texte et des protocoles de télécommunication des années 1970 à la fin des années 1990 représente un défi d'ingénierie inverse majeur. L'esthétique des œuvres encodées en ANSI, ASCII, PETSCII, ou Vidéotex n'est pas le fruit de choix stylistiques abstraits, mais la conséquence directe et intransigeante des architectures matérielles d'époque. L'élaboration de décodeurs et de moteurs de rendu logiciels modernes, dits "bit-perfect", exige une compréhension intime des limites des cartes vidéo (CGA, EGA, VGA), de la persistance des phosphores des écrans cathodiques (CRT), de l'adressage de la mémoire vidéo matérielle, et des débits asynchrones des modems analogiques1.
Ce rapport détaille les spécifications, les outils open-source contemporains, les divergences logicielles et les cadres matériels de quatorze familles de formats historiques, offrant ainsi un cahier des charges rigoureux pour le développement de moteurs de rendu fidèles.
Contexte Matériel : Écrans, Cartes Vidéo et Débits de Transmission
Pour appréhender la restitution de ces formats, il est indispensable de reconstruire le paradigme technologique dans lequel les artistes opéraient. L'expérience originelle de visualisation était conditionnée par le matériel terminal de l'utilisateur final, créant une fragmentation temporelle et géographique des scènes artistiques.
Les Débits de Modem : L'Animation par la Lenteur et la Contrainte Asynchrone
Durant l'âge d'or des Bulletin Board Systems (BBS) et des systèmes de télématique, les vitesses de connexion constituaient le goulot d'étranglement principal de la conception d'interfaces. La scène s'est structurée autour de trois grandes périodes :
L'Ère Fondatrice (300 à 2400 bauds, ~1980-1988) : À ces débits, l'affichage d'un plein écran texte prenait plusieurs secondes. Cette lenteur inhérente a été exploitée par les artistes pour créer un suspense visuel. L'apparition progressive des données ligne par ligne, ou la mise en page d'un écran RIPscrip élément par élément (vecteur par vecteur), constituait une animation de facto4.
L'Ère de l'Art ANSI et de l'Âge d'Or (9600 à 28 800 bauds, ~1989-1995) : L'augmentation de la bande passante a permis aux groupes (ACiD, iCE, Blocktronics) de distribuer des "Artpacks" de plus en plus volumineux. Les connexions à 14,4k ou 28,8k bauds offraient un affichage rapide mais encore perceptible du texte, permettant des macros d'animation ANSI sophistiquées en redessinant des parties de l'écran par déplacements rapides du curseur4.
L'Ère de la Transition (33 600 à 57 600 bauds, post-1995) : L'affichage textuel devenant presque instantané, l'accent s'est déplacé vers le transfert de fichiers (protocoles X/Y/Z Modem, ZModem batch)3.
Un moteur de rendu moderne qui injecte et affiche un fichier .ANS ou un script .RIP dans un tampon mémoire de manière asynchrone et instantanée dénature l'œuvre. Les terminaux modernes fidèles, comme IcyTerm ou SyncTERM, implémentent une "émulation de baud" (baud emulation) logicielle qui introduit des micro-délais entre l'interprétation des octets pour reproduire le flux d'un modem matériel6.
Architectures Vidéo, Phosphores et Rapports d'Aspect
L'autre composante cruciale est la traduction du signal numérique en un affichage physique sur tube cathodique (CRT). Les écrans CRT historiques présentaient presque universellement un ratio d'aspect physique de 4:3. Cependant, les cartes vidéo généraient des tampons d'affichage qui n'étaient pas homothétiques à ce ratio.
En mode texte VGA standard (mode 3), la résolution interne est de 720x400 pixels pour afficher 80 colonnes et 25 lignes. Lors de la projection de cette grille de 720x400 sur un écran 4:3, l'image est étirée verticalement. Les pixels historiques n'étaient donc pas carrés (non-square pixels), avec un ratio pixel d'environ 1:1.351. Les artistes ANSI dessinaient en intégrant visuellement cet étirement : un cercle parfait sur leur écran CRT apparaissait mathématiquement comme une ellipse dans le tampon mémoire. Rendre ces fichiers sur des moniteurs LCD modernes avec des pixels carrés stricts (1:1) écrase verticalement les œuvres. Un moteur de rendu rigoureux doit appliquer une correction d'aspect, généralement via une mise à l'échelle entière (integer scaling), en rendant chaque pixel d'origine sous la forme d'un bloc de 3 pixels de large sur 4 pixels de haut, couplé à un léger flou gaussien pour simuler le saignement (bleeding) des phosphores1.
Architecture des Familles de Formats et Moteurs de Rendu
L'analyse suivante décompose les quatorze formats cibles, encapsulant pour chacun la spécification de référence, les moteurs libres recommandés, les pièges d'implémentation et les polices de caractères requises.
1. ANSI / CP437 (ANSI.SYS, PCBoard, Avatar)
L'écosystème MS-DOS est le berceau de la scène textuelle dominante. Le rendu repose sur la page de code 437 (CP437) matérielle intégrée dans les ROM des cartes IBM PC, et sur l'interprétation des séquences d'échappement standardisées (ANSI X3.64) étendues par le pilote MS-DOS ANSI.SYS. Outre l'ANSI standard, des formats dérivés destinés aux BBS ont vu le jour, tels que les macros PCBoard (utilisant des séquences @X pour compresser la transmission de la couleur) et Avatar (qui emploie des codes binaires de contrôle rudimentaires au lieu de chaînes de texte)6.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Norme ANSI X3.64 et documentation Microsoft MS-DOS ANSI.SYS. Les spécifications PCBoard (.PCB) et Avatar (.AVT) sont documentées via ingénierie inverse dans les dépôts de libansilove8.
Décodeur Recommandé
libansilove / ansilove (C, licence BSD). Extrêmement actif, c'est l'étalon-or moderne pour la conversion vers PNG8. Alternative éditeur : Moebius / text0wnz (JavaScript/TypeScript, MIT/Apache)11.
Pièges et Divergences
1. Clignotement vs iCE Colors : Le bit 7 de l'octet d'attribut VGA bascule entre le texte clignotant et l'arrière-plan de haute intensité. Si non géré, les couleurs bavent. 2. Rendu de la 9e colonne : Le mode VGA 80x25 utilise des matrices de glyphes de 8x16 pixels projetées dans des cellules de 9x16 pixels pour espacer les lettres. Pour préserver les lignes continues (caractères 0xC0 à 0xDF), le matériel VGA duplique la 8e colonne de pixels dans la 9e. Ne pas émuler ce comportement matériel brise les dessins de blocs7.
Polices Fidèles
Ultimate Oldschool PC Font Pack v2.2 (par VileR). Contient des représentations bit-perfect (TrueType, WOFF) incluant les corrections de la 9e colonne14.
Licence des Polices
Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)16. L'usage des bitmaps extraits échappe souvent au droit d'auteur strict selon les juridictions, mais la licence CC prévaut sur l'assemblage vectoriel17.
Jeux de Fichiers de Test
Les archives ACiD et Blocktronics classiques. Un fichier critique pour évaluer les corruptions de palette est blocktronics_block_n_roll/nu-ninja_cat.ans19.

2. SAUCE (Standard Architecture for Universal Comment Extensions)
Introduit par ACiD Productions en 1994, SAUCE n'est pas un protocole de rendu graphique, mais un bloc de métadonnées binaire de 128 octets systématiquement greffé à la fin (EOF) des fichiers textes de l'époque. Il dicte au moteur de rendu comment interpréter les octets qui le précèdent7.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Spécification SAUCE v00.5. Accessible sous la forme du document sauce.txt dans l'archive originale ou via la documentation du package icy_sauce7.
Décodeur Recommandé
icy_sauce (Rust, Licence MIT) pour un parsing typé sûr de la mémoire. Intégré nativement dans IcyTerm et libansilove7.
Pièges et Divergences
Omettre la lecture du bloc SAUCE condamne le décodeur à l'approximation heuristique. Les drapeaux critiques (Flags) incluent ice_colors (forçant l'interprétation du bit 7 comme couleur d'arrière-plan), letter_spacing (forçant le rendu 8 pixels ou 9 pixels), et aspect_ratio (pixel carré, legacy étiré, ou ratio matériel)7. Le bloc SAUCE définit également la police précise à charger (par ex. IBM VGA 80x50, Amiga Topaz)8.
Polices Fidèles
Sans objet (Métadonnées).
Licence des Polices
Sans objet.
Jeux de Fichiers de Test
Les tests d'intégration automatisés du dépôt GitHub icy_sauce ou les suites de tests unitaires de text0wnz valident la lecture des 255 lignes de commentaires optionnelles (COMNT)7.

3. XBIN (eXtended BINary)
Face aux limitations sémantiques et matérielles du standard ANSI (limité historiquement à 80 colonnes, aux 16 couleurs par défaut de la palette VGA, et à la police CP437 matérielle), le format XBIN a été conçu en 1996. Ce format binaire est une image complète de l'état de la carte vidéo : il encapsule non seulement les données texte et attributs compressées (via un algorithme RLE personnalisé), mais intègre directement la palette de couleurs modifiée et le dump binaire de la police de caractères utilisée (jusqu'à 32 pixels de hauteur)7.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Document XBIN.TXT (issu de l'archive acdu0896.zip d'ACiD) détaillant l'en-tête, la structure RLE et le stockage des polices21.
Décodeur Recommandé
MoebiusXBIN (Fork par hlotvonen, JavaScript/Electron, Licence Apache-2.0). C'est l'éditeur moderne le plus puissant dédié au XBIN22. libansilove supporte très bien l'export XBIN vers PNG9.
Pièges et Divergences
Les dimensions de la grille XBIN peuvent excéder largement le matériel d'époque (jusqu'à 65 535 colonnes). Par définition, XBIN ignore les drapeaux SAUCE liés au ratio ou aux couleurs iCE, car le format impose ses propres règles explicites. Le rendu de la police doit strictement suivre le tableau binaire encapsulé, et la taille de la police doit être forcée à 16 pixels si le champ est ambigu ou corrompu dans de vieux fichiers7.
Polices Fidèles
Les polices sont encapsulées dans le fichier .XB lui-même. Cependant, pour l'édition, la bibliothèque de MoebiusXBIN inclut 661 polices extraites et le pack de VileR22.
Licence des Polices
Héritée du créateur de l'œuvre .XB.
Jeux de Fichiers de Test
Archive historique blocktronics_block_to_the_future.zip contenant des fichiers .xb de référence exploitant la compression et les palettes personnalisées21.

4. ADF (ArtWorx Data Format)
Le format ADF est une réponse précoce aux limitations de l'ANSI, propriétaire à l'éditeur ArtWorx. À l'instar de XBIN, il visait à capturer la mémoire vidéo brute, la palette modifiée et le jeu de caractères personnalisé9.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Spécifications peu standardisées, reconstruites principalement via ingénierie inverse dans les dépôts de libansilove et le projet Just Solve the File Format Problem9.
Décodeur Recommandé
libansilove (C, BSD). Le code source expose clairement le mappage couleur spécifique à Artworx dans les routines de configuration9.
Pièges et Divergences
L'organisation de la table des couleurs (color mapping array) diverge de la norme VGA standard de Microsoft. De plus, les anciennes implémentations souffraient de fuites de mémoire ou d'allocations redondantes (appels gdImageColorAllocate) qui corrompaient la palette 24-bits ; ce bogue a été résolu dans ansilove depuis 202010.
Polices Fidèles
Les polices sont encapsulées dans le fichier, de façon similaire au XBIN.
Licence des Polices
Dépend de l'encapsulation de l'artiste.
Jeux de Fichiers de Test
Les dépôts de ansilove maintiennent des fichiers .adf de test pour valider l'intégrité de la palette après des refontes de code9.

5. IDF (iCE Draw Format)
Format concurrent d'ArtWorx, créé pour l'éditeur iCE Draw. Sa particularité réside dans son intégration pionnière de l'astuce matérielle remplaçant le bit de clignotement matériel par les 8 couleurs de fond supplémentaires (d'où l'origine du terme technique "iCE Colors")8.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Identifiable par un en-tête de métadonnées lisible (;FFMETADATA1 ou chaînes spécifiques à iCE Draw) et analysé par rétro-ingénierie dans la communauté libavcodec et libansilove8.
Décodeur Recommandé
libansilove (C, BSD). L'outil en ligne de commande associé est hautement recommandé pour générer des PNG optimisés en 4 bits8. FFmpeg inclut également un parseur rudimentaire d'en-tête IDF25.
Pièges et Divergences
La structure de l'en-tête peut parfois être confondue avec d'autres formats IFF (Interchange File Format). L'émulateur doit forcer la désactivation de toute logique de clignotement pour les fichiers IDF, l'arrière-plan haute intensité étant la pierre angulaire du format7.
Polices Fidèles
Polices personnalisées encapsulées dans le fichier8.
Licence des Polices
Héritée de l'œuvre.
Jeux de Fichiers de Test
Suites de tests de la bibliothèque FFmpeg et jeux de tests unitaires de libansilove8.

6. RIPscrip (Remote Imaging Protocol)
Le RIPscrip, conçu en 1993 par TeleGrafix Communications, s'écarte radicalement de l'art par blocs CP437. Il s'agit d'un langage de script graphique vectoriel (lignes, cercles, splines, polygones remplis) conçu pour doter les environnements BBS textuels d'une véritable interface utilisateur graphique (GUI) interactive cliquable à la souris, tout en transitant sur de très faibles bandes passantes (typiquement 2400 à 9600 bauds)4.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Spécification officielle RIPscrip v1.54 de TeleGrafix. Des restaurations documentaires communautaires sont hébergées sur le GitHub de bbs-land (remote-imaging-protocol) ou via riplib27.
Décodeur Recommandé
PabloDraw (C#, Licence MIT, mais projet largement inactif)29. Le projet émergent RIPtermJS (JavaScript/Canvas) et le terminal IcyTerm (Rust) sont les moteurs modernes les plus prometteurs pour le Web et le bureau6. L'authentique client MS-DOS RIPterm 1.54 reste la référence de vérité matérielle4.
Pièges et Divergences
1. Émulation EGA 640x350 : Les coordonnées vectorielles RIPscrip assument historiquement la grille matérielle EGA. Sur un affichage moderne, cela crée des distorsions si l'échelle asymétrique n'est pas corrigée. Pour corriger l'écrasement, l'heuristique recommandée est de rendre chaque pixel EGA avec une largeur triple et une hauteur quadruple sur des écrans HD1. 2. Rendu synchrone vs progressif : Dessiner instantanément les vecteurs ruine l'effet artistique. Un décodeur doit simuler le délai du baud1.
Polices Fidèles
RIPscrip gère ses propres fontes vectorielles internes, redimensionnables et rotatives27.
Licence des Polices
Intégrées aux décodeurs via l'implémentation algorithmique de la spécification.
Jeux de Fichiers de Test
Les écrans de test du Realm of Serion BBS, qui utilise nativement des graphismes RIP sur toutes ses interfaces, et les tests de régression de riplib27.

7. ASCII Amiga
La scène artistique de l'Amiga a divergé du monde PC en raison de l'absence de page de code matérielle CP437. L'Amiga (via l'OS Workbench) s'appuie sur la norme ISO-8859-1 (Latin-1) et ne possède pas de caractères spécifiques de "dessin de bloc". Les artistes ont donc inventé un style de rendu textuel basé sur les ombrages et l'anti-aliasing visuel en utilisant des caractères alphanumériques standards (M, W, :, ., _)31.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Le rendu dépend d'un couplage strict entre l'encodage Latin-1 et la police système de l'Amiga.
Décodeur Recommandé
Éditeurs supportant l'import ASCII pur : text0wnz (PWA JavaScript) et MoebiusXBIN12.
Pièges et Divergences
Les pixels sur les moniteurs PAL de l'Amiga en mode Hi-Res (typiquement 640x256 ou 640x512) étaient très différents des pixels PC. Un visualiseur d'art Amiga doit forcer l'espacement et interdire formellement tout anti-aliasing logiciel moderne, qui détruirait l'illusion de l'ombrage au niveau du sous-pixel simulé par les artistes12.
Polices Fidèles
La célèbre police bitmap Topaz. Des reconstructions modernes pixel-perfect existent, comme Topaz New ou la variante Topaz-a500 (doublée en hauteur pour recréer l'expérience matérielle Hi-Res originelle)31. Le pack amigafonts de dMG/t!s^dS! est incontournable32.
Licence des Polices
SIL Open Font License ou "Gratuit pour usage personnel"31. Les droits originaux appartenant à Commodore International sont aujourd'hui une zone de tolérance tacite (abandonware)11.
Jeux de Fichiers de Test
Les vastes archives du site asciiart.eu dédiées à la section "Amiga Style"32.

8. PETSCII (Commodore 64, PET, VIC-20)
Le Commodore 64 possède l'architecture mémoire la plus distincte de cette ère. L'encodage PETSCII (PET Standard Code of Information Interchange) diffère fondamentalement de l'ASCII. Les artistes exploitaient la grille de 40x25 caractères et la palette inaltérable de 16 couleurs matérielles spécifiques3.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Tables matérielles du C64 (Commodore ROM character sets)3.
Décodeur Recommandé
PyCGMS (Terminal écrit en Python, Licence Open Source non spécifiée, très actif) pour le transfert et le rendu Telnet3. rgc-basic avec basic-gfx (Moteur Raylib/C) est excellent pour l'émulation fenêtrée locale des flux .seq34.
Pièges et Divergences
L'architecture matérielle sépare les "Control Codes" (utilisés pour les chaînes BASIC ou de transmission) et les "Screen Codes" (utilisés par la puce VIC-II dans la RAM vidéo à partir de l'adresse 1024). L'index d'un caractère stocké en mémoire écran n'est pas son code PETSCII. De plus, le mode vidéo inversé (Reverse video state) n'est pas géré par l'octet de couleur, mais en basculant le bit 7 du code d'écran3. Le décodeur doit pré-rendre et cacher les matrices via une table de correspondance complexe. L'implémentation stricte de la palette C64 (sans lissage RGB) est obligatoire3.
Polices Fidèles
Dumps directs et extractions des puces ROM d'origine (upper.bmp pour le mode majuscule/graphique, et lower.bmp pour le mode minuscule)3. Le projet Playscii contient également d'excellentes extractions35.
Licence des Polices
L'extraction littérale des ROM du C64 opère dans un flou légal (domaine public de facto / abandonware technique)3.
Jeux de Fichiers de Test
Des modules de tests sont intégrés dans les exemples de rgc-basic (ex. basic examples/trek.bas et tests de codes de contrôle via .bas)34. La restitution d'images via le projet GitHub petsciirender fournit également des tampons mémoires .pet pré-générés pour comparaison binaire35.

9. ATASCII (Atari 8-bit)
Variante de l'encodage ASCII conçue pour la gamme d'ordinateurs Atari 8-bit (400, 800, XL, XE). L'ATASCII exploite la puce vidéo ANTIC. Sa principale originalité est le remplacement pur et simple de tous les codes de contrôle ASCII classiques (plage 0 à 31, qui servent normalement au formatage invisible) par des glyphes graphiques visibles (lignes, blocs, symboles de cartes à jouer)36.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Spécifications des registres ANTIC et cartographie des tables matérielles ATASCII Atari36.
Décodeur Recommandé
IcyTerm (Terminal multi-plateforme Rust, hautement performant)6. Les moteurs Node.js comme ascii-art intègrent également le support ATASCII40.
Pièges et Divergences
1. Mappage matériel ANTIC : L'ordre des glyphes dans la ROM (utilisé par ANTIC pour le rendu) ne correspond pas du tout à l'ordre binaire de la table ATASCII. 2. Curseur inversé : Contrairement au clignotement PC, l'éditeur matériel Atari indique le curseur texte par une inversion vidéo mathématique (application d'un opérateur logique binaire XOR 0x80 sur l'octet du caractère)36.
Polices Fidèles
Dumps ROM Atari (intégrés nativement dans l'architecture matérielle simulée d'IcyTerm).
Licence des Polices
Identique au PETSCII ; tolérance d'usage pour émulation de ROM historique.
Jeux de Fichiers de Test
Scripts et captures d'écran testés par les interpréteurs comme FastBasic41. Les captures et séquences d'animations textuelles historiques (ATASCII animations enregistrant les frappes de touches)37.

10. Télétexte (Niveaux 1 à 2.5)
Les protocoles de télédiffusion utilisaient l'intervalle de suppression trame (Vertical Blanking Interval - VBI) du signal de télévision analogique pour transmettre des pages de texte et de mosaïque numérique. Le standard européen a défini des niveaux de complexité progressifs.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
La norme standardisée ETS 300 706 (Enhanced Teletext specification) maintenue par l'ETSI42.
Décodeur Recommandé
libzvbi (Bibliothèque C sous licence GPL). Développée initialement pour le projet Zapping, c'est la seule bibliothèque de classe mondiale capable de démoduler le VBI logiciel et de décoder la norme. Elle est le moteur sous-jacent de FFmpeg et mpv pour le sous-titrage45.
Pièges et Divergences
L'architecture de rendu s'éloigne drastiquement d'une matrice PC. Le Télétexte utilise des "attributs de contrôle en série" (serial attributes). Le simple changement d'une couleur de texte au milieu d'une ligne d'affichage consomme physiquement une cellule de caractère vide sur l'écran. L'implémentation du Niveau 2.5 augmente dramatiquement la complexité en permettant l'appel d'objets distincts hors de la grille centrale (les side panels) et des palettes de couleurs modifiables (CLUT), pouvant causer des dépassements de mémoire ou des crashs si le décodeur n'avertit pas explicitement la version ciblée (par défaut, libzvbi bloque le niveau 2.5 sauf forçage)44.
Polices Fidèles
Implémentations modernes émulant le générateur matériel de caractères Philips SAA505051.
Licence des Polices
Les reconstructions modernes du SAA5050 (comme le projet teletext de TheMarco) sont licenciées sous CC BY 4.051.
Jeux de Fichiers de Test
L'outil zvbi-chains et les binaires de tests de libzvbi contiennent de nombreux cas limites capturés directement depuis les flux VBI en direct46.

11. Prestel, Minitel et Antiope
Le monde du Vidéotex interactif européen a été codifié dans la norme CEPT (Conférence européenne des administrations des postes et télécommunications). Le Minitel (standard Teletel, dérivé de la recherche sur Antiope) et le Prestel britannique partagent des bases communes.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Recommandation CEPT T/TE 06-01. Normes d'affichage Vidéotex françaises (Teletel) et britanniques52.
Décodeur Recommandé
Des projets spécifiques d'ingénierie inverse française (souvent liés au Raspberry Pi ou au projet Minitel de PyMinitel). Le support terminal multi-protocole IcyTerm propose une émulation expérimentale "Viewdata"6.
Pièges et Divergences
À l'instar du Télétexte, le système repose sur des attributs séries (les espaces de contrôle). Les alphabets mosaïques contigus et séparés exigent des calculs de masquage de bits stricts pour dessiner des graphiques sans jointures.
Polices Fidèles
Grilles matricielles 2x3 pixels intégrées dans les décodeurs de mosaïque CEPT.
Licence des Polices
Libre (reconstruction algorithmique, pas de fichier bitmap strict).
Jeux de Fichiers de Test
Les sauvegardes historiques de pages Vidéotex et les émulateurs de serveurs Minitel (Micro-Serveurs RTC modernes).

12. NAPLPS (North American Presentation Level Protocol Syntax)
Protocole de présentation vectorielle d'une sophistication extrême, conçu pour les services télématiques nord-américains (comme Telidon au Canada ou Prodigy aux États-Unis). Il se base sur des "Picture Description Instructions" (PDI) indépendantes de la résolution matérielle53.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Standard ANSI X3.110-1983 / CSA T500-19832. Des descriptions techniques magistrales ont été publiées dans le magazine BYTE en 198353.
Décodeur Recommandé
Telidraw (.NET 10, C#). Une boîte à outils moderne de A à Z : parseur, moteur de rendu, et éditeur web. Licence présumée open-source / MIT53.
Pièges et Divergences
Le NAPLPS est un cauchemar algorithmique : il autorise un système de coordonnées géométriques infini, la gestion de macros complexes, et le remplacement dynamique à la volée du jeu de caractères matériel par téléchargement (DRCS - Dynamically Redefinable Character Sets). Le concepteur du décodeur doit préserver mathématiquement tous les octets non définis par la norme pour permettre des conversions "round-trip" sans perte53.
Polices Fidèles
Le rendu est purement géométrique. Les glyphes sont générés vectoriellement ou via l'envoi du DRCS par le serveur hôte53.
Licence des Polices
Intégrée nativement au moteur vectoriel.
Jeux de Fichiers de Test
Le dépôt Telidraw contient le nec plus ultra de la validation technique : un corpus historique de plus de 375 fichiers originaux .nap, associés à une suite de tests de régression visuelle qui compare le rendu au pixel près contre des références APNG validées53.

13. Art Japonais : Shift_JIS
Contrairement aux arts occidentaux limités aux blocs de CP437, l'art asiatique sur les forums tels que 2channel (2ch) utilise l'encodage de caractères Shift_JIS. L'essence de cet art réside dans l'exploitation millimétrée des largeurs inégales de la typographie japonaise proportionnelle pour créer des ombrages et des contours.

Paramètre
Spécifications et Directives d'Ingénierie
Spécification
Encodage de caractères standardisé JIS X 020819.
Décodeur Recommandé
Les navigateurs web modernes avec des balises d'encodage forcées, ou l'extension dédiée RetroTxt qui détecte et bascule intelligemment la police lorsque Shift_JIS est rencontré19.
Pièges et Divergences
Le danger mortel de l'art Shift_JIS est l'affichage via une police monospace classique ou une police proportionnelle moderne occidentale (comme Arial). Le design des œuvres (par exemple les fameux "Shift_JIS art" de personnages d'anime) s'effondre totalement en une bouillie illisible si les espaces demi-chasse (half-width) et pleine-chasse (full-width) spécifiques au japonais ne sont pas respectés par le moteur de rendu texte du système d'exploitation19.
Polices Fidèles
Historiquement la police Windows MS PGothic. Pour le libre, la police de contournement de référence est Mona Font (spécifiquement conçue pour le rendu sous Linux)19.
Licence des Polices
MS PGothic (Propriétaire Microsoft). Mona Font (Domaine public).
Jeux de Fichiers de Test
Toute sauvegarde d'archive historique (threads) du forum 2channel.

Synthèse Analytique : Divergences Moteur et Cas Ambigus d'Interprétation
Dans l'écriture d'un moteur unifié, l'ingénieur va inévitablement affronter des contradictions inhérentes aux documents spécifiant ces formats et aux tolérances matérielles. La robustesse d'un logiciel se mesure à la gestion des ambiguïtés suivantes, qui exigent des heuristiques strictes.
Le Glitch du Retour à la Ligne (The 80-Column Wrap Glitch)
C'est la cause la plus fréquente d'échec du rendu dans les terminaux écrits hâtivement. Dans l'environnement original du pilote ANSI.SYS de MS-DOS, le comportement du curseur atteignant la limite droite de l'écran (colonne 80) contredisait le bon sens moderne. Le curseur ne revenait pas automatiquement à la colonne 1 de la ligne suivante. Il restait virtuellement bloqué à la position 80. Ce n'est qu'à la réception du 81ème caractère que le saut de ligne matériel s'opérait. Des milliers d'œuvres ANSI reposent sur ce comportement de "Lazy Wrap"19. Un émulateur moderne qui effectue un passage à la ligne forcé à la colonne 80 brisera tous les alignements verticaux de l'œuvre. Le moteur de rendu doit conserver l'état du curseur en attente.
Le Conflit du Bit 7 : Clignotement contre Haute Intensité (iCE Colors)
Sur la carte graphique matérielle VGA, la mémoire d'attribut pour chaque caractère attribue 4 bits pour la couleur du texte (avant-plan) et 3 bits pour la couleur du fond, laissant le 8ème bit (bit 7) libre. Historiquement, le VGA utilisait ce bit pour faire clignoter le texte matériellement. Cependant, la scène BBS (notamment via le logiciel iCE) a découvert qu'en reprogrammant les registres VGA, ce bit pouvait être utilisé pour désactiver le clignotement et doubler la palette de fond (passant de 8 couleurs sombres à 16 couleurs incluant des tons vifs)7. Interprétation heuristique : Si un bloc SAUCE est présent, la variable binaire ice_colors fait force de loi7. Sans SAUCE, un fichier .XB ou .IDF impose techniquement la désactivation du clignotement. Pour un vieux fichier .ANS sans métadonnées, le moteur doit fournir une bascule manuelle à l'utilisateur, l'interprétation algorithmique étant mathématiquement impossible.
L'Épineuse Question des 8 ou 9 Pixels de Largeur
L'affichage matériel VGA standard du texte en 80 colonnes se fait non pas avec 640 pixels horizontaux, mais avec 720 pixels de large. Les caractères CP437, conçus sur des matrices de 8x16, étaient projetés sur des grilles matérielles de 9x16. La carte VGA insérait une 9e colonne vide pour aérer les lettres. Or, pour les caractères continus d'interface (lignes de tableaux et blocs graphiques, plage 0xC0 à 0xDF), cette colonne vide détruisait l'illusion de continuité continue de la ligne. Le matériel VGA embarquait donc un algorithme silicium qui détectait ces caractères précis et recopiait la 8e colonne de pixels dans la 9e7. Interprétation du moteur : Le moteur de rendu logiciel doit implémenter exactement ce même correctif conditionnel lors du rendu des chaînes de texte, sous peine de voir toutes les boîtes ANSI fracturées visuellement par des bandes noires verticales d'un pixel. Les polices bit-perfect de VileR fournissent l'infrastructure de base pour ce comportement13. Le flag SAUCE letter_spacing doit cependant permettre de désactiver ce comportement pour forcer un rendu brut 8 pixels (Legacy) si l'artiste l'a exigé7.
Anomalies de Séquences SGR Non Standards (Le Cas PabloDraw)
Certains éditeurs modernes ont tenté de moderniser les formats au mépris des spécifications DOS. PabloDraw, par exemple, a implémenté des séquences d'échappement SGR (Select Graphic Rendition) totalement non-standards permettant d'injecter des valeurs couleurs RGB 24-bits arbitraires directement dans un fichier .ANS classique8. Ces séquences polluent les vieux terminaux. Les moteurs modernes robustes (comme les révisions récentes de libansilove) ont dû intégrer un parseur dérogatoire capable de détecter ces injections spécifiques à PabloDraw, d'appliquer la couleur RGB au rendu PNG, tout en neutralisant l'arrière-plan avec soin si un attribut de clignotement (qui corrompt souvent l'affichage 24-bits) est rencontré simultanément9.
Les Formats Orphelins (Sans Décodeur ou Implémentation Fiable)
Bien que la majorité des défis d'ingénierie inverse aient été relevés par des communautés dédiées (ACiD, Blocktronics), notre analyse révèle l'existence de "terres en friche" techniques, des protocoles pour lesquels aucune implémentation de rendu bit-perfect moderne, sous forme de bibliothèque libre et standardisée, n'existe à ce jour :
RIPscrip Versions 2.0 et Supérieures : Si le client et la spécification v1.54 ont été sauvés par rétro-ingénierie (PabloDraw, RIPtermJS), l'adoption massive d'Internet par le grand public à partir de 1995 a anéanti la trajectoire des versions suivantes de TeleGrafix. La spécification RIPscrip 2.00a4 n'existe qu'à l'état de brouillon inachevé, et aucune implémentation moderne ne peut afficher de manière cohérente les fichiers expérimentaux (WIP) basés sur ces normes mort-nées27.
Télétexte Niveau 3.5 (Enhanced Geometrics) : Les formidables efforts du projet C libzvbi (utilisé par FFmpeg) permettent un rendu immaculé des niveaux de 1.0 à 2.5 (incluant les couleurs haute résolution et les panneaux latéraux). Toutefois, les fonctionnalités extrêmes de géométrie vectorielle prévues par la norme ETS 300 706 au Niveau 3.5 ne bénéficient pas d'un décodage visuel de qualité production, créant un angle mort logiciel44.
Protocoles de BBS Privés et Encapsulations Expérimentales : Des tentatives isolées de formats très haut débit et d'interface graphique (comme les extensions spécifiques associées à des clients MS-DOS rares comme Terminate, ou le protocole générique mentionné sous le nom de WIP graphics protocol) sont documentées dans des magazines d'époque mais n'ont jamais été compilées en C/Rust27.
Conclusion
Le rendu de l'art en mode texte est fondamentalement l'art de l'émulation asynchrone des défauts du matériel d'antan. Développer des décodeurs fiables transcende le simple passage d'un code ASCII à une fonction de rendu de texte système. Les algorithmes doivent ingérer les métadonnées de contextualisation temporelle (SAUCE), mapper mathématiquement les ratios de pixels d'une carte VGA face à un moniteur CRT, simuler le timing d'un port série baud, et compenser les erreurs d'une page de code gravée dans le silicium1. C'est à ce niveau de granularité, exemplifié par les travaux de l'interface libansilove en C et de la robustesse de IcyTerm en Rust, que s'établit la validité de la préservation du patrimoine de la téléinformatique.
Sources des citations
r/bbs - Found my copy of RIPterm, which let you add simple raster, https://www.reddit.com/r/bbs/comments/1t02ysx/found_my_copy_of_ripterm_which_let_you_add_simple/
Traditional User-Interface Graphics, https://peteroupc.github.io/classic-wallpaper/docs/uielements.html
lastylegp/PyCGMS: PETSCII BBS Terminal - GitHub, https://github.com/lastylegp/PyCGMS
The Montreal Greek Times Unicorn, https://greektimes.ca/retro/
The Major BBS, http://software.bbsdocumentary.com/IBM/DOS/MAJORBBS/gcommdoc001.pdf
GitHub - mkrueger/icy_term: Old school ANSI/AVT terminal program, https://github.com/mkrueger/icy_term
icy_sauce - crates.io: Rust Package Registry, https://crates.io/crates/icy_sauce
GitHub - ansilove/ansilove: ANSI and ASCII art to PNG converter in C, https://github.com/ansilove/ansilove
GitHub - ansilove/libansilove: Library for converting ANSI, ASCII, https://github.com/ansilove/libansilove
Ansilove - ANSi to PNG converter, https://www.ansilove.org/
Moebius - Modern ANSI & ASCII Art Editor - GitHub, https://github.com/blocktronics/moebius
GitHub - xero/text0wnz: 𝙔𝙤𝙪𝙧 𝙗𝙧𝙤𝙬𝙨𝙚𝙧 𝙞𝙨 𝙩𝙝𝙚, https://github.com/xero/text0wnz
The Ultimate Oldschool PC Font Pack - Adafruit Blog, https://blog.adafruit.com/2024/10/01/the-ultimate-oldschool-pc-font-pack/
Oldschool PC Font - eCSoft/2, https://ecsoft2.org/oldschool-pc-font
The Ultimate Oldschool PC Font Pack: Download - INT10h.org, https://int10h.org/oldschool-pc-fonts/download/
fntgrpoldschoolpcfonts · olikraus/u8g2 Wiki - GitHub, https://github.com/olikraus/u8g2/wiki/fntgrpoldschoolpcfonts
The Ultimate Oldschool PC Font Pack - Hacker News, https://news.ycombinator.com/item?id=41692922
The Ultimate Oldschool PC Font Pack : r/linux - Reddit, https://www.reddit.com/r/linux/comments/7tj4e5/this_might_interest_linux_users_as_well_the/
Changes and improvements - RetroTxt, https://docs.retrotxt.com/changes/
tpt-async/spec.txt at master · tpt-solutions/tpt-async · GitHub, https://github.com/tpt-solutions/tpt-async/blob/master/spec.txt
XBIN - Just Solve the File Format Problem, http://justsolve.archiveteam.org/wiki/XBIN
Moebius XBIN - Modern ASCII & text-mode art editor - GitHub, https://github.com/hlotvonen/moebiusXBIN
File Formats Wiki - DigiPres.org, https://www.digipres.org/formats/sources/ffw/formats/
Format List - Multimedia Xpert, https://www.atlas-informatik.ch/multimediaXpert/FormatList.en.html
FFmpeg Basics, https://wangwei1237.github.io/shares/FFmpegBasics.pdf
Quick Start Guide FFmpeg 2023 | PDF | Codec - Scribd, https://www.scribd.com/document/633402781/Quick-Start-Guide-FFmpeg-2023
Here is a RIPScrip 1.54 in JavaScript https://github.com ... - Facebook, https://www.facebook.com/groups/RIPscrip/posts/2830044693849500/
riplib/docs/spec/14-divergence-register.md at main · BradHawthorne, https://github.com/BradHawthorne/riplib/blob/main/docs/spec/14-divergence-register.md
PabloDraw is an Ansi/Ascii text and RIPscrip vector graphic ... - GitHub, https://github.com/cwensley/pablodraw
1.54/2.0/3/4+ full implementation. · Issue #134 · cwensley ... - GitHub, https://github.com/cwensley/pablodraw/issues/134
Topaz New Font Download - Fonts4Free, https://www.fonts4free.net/topaz-new-font.html
Acknowledgments - ASCII Art Archive, https://www.asciiart.eu/acknowledgments
Topaz-a500 - OS4Depot - Your one stop for AmigaOS4 files, https://os4depot.net/index.php?function=showfile&file=graphics/misc/topaz-a500.lha
GitHub - omiq/rgc-basic: Modern cross-platform BASIC Interpreter, https://github.com/omiq/rgc-basic
PETSCII Art Renderer - C64 OS, https://c64os.com/post/petsciiartrenderer
ATASCII - Wikipedia, https://en.wikipedia.org/wiki/ATASCII
ATASCII "international character set" - Atari 8-Bit Computers, https://forums.atariage.com/topic/323262-atascii-international-character-set/
Atari 8-bit Display List Interrupts: A Complete(ish) Tutorial, https://playermissile.com/dli_tutorial/
Altirra Hardware Reference Manual | Virtual Dub, https://www.virtualdub.org/downloads/Altirra%20Hardware%20Reference%20Manual.pdf
GitHub - khrome/ascii-art: A Node.js library for ansi codes, figlet fonts, https://github.com/khrome/ascii-art
fastbasic/manual.md at master - GitHub, https://github.com/dmsc/fastbasic/blob/master/manual.md
gkthemac/QTeletextMaker: An open source Level 2.5 ... - GitHub, https://github.com/gkthemac/QTeletextMaker
Analog TV Simulator: Old TV & VHS Simulator, CRT & Broadcast TV, https://analogtv.net/
ETS 300 706 - Enhanced Teletext specification - ETSI, https://www.etsi.org/deliver/etsi_i_ets/300700_300799/300706/01_60/ets_300706e01p.pdf
ffmpeg-codecs(1) - Arch Linux manual pages, https://man.archlinux.org/man/ffmpeg-codecs.1.en
GitHub - zapping-vbi/zvbi: Vertical Blanking Interval (VBI) utilities, https://github.com/zapping-vbi/zvbi
mpv(1) - Arch Linux manual pages, https://man.archlinux.org/man/mpv.1.en
ffplay Documentation - Index of /docs, https://gensoft.pasteur.fr/docs/ffmpeg/4.3.1/ffplay-all.html
xbmc-rbp/xbmc/video/Teletext.cpp at master - GitHub, https://github.com/xbmc/xbmc-rbp/blob/master/xbmc/video/Teletext.cpp
ETS 300 706 - Enhanced Teletext specification - ETSI, https://www.etsi.org/deliver/etsi_i_ets/300700_300799/300706/01_40_57/ets_300706e01o.pdf
GitHub - TheMarco/teletext, https://github.com/TheMarco/teletext
Teletext Around The World, Still | Hackaday, https://hackaday.com/2025/08/15/teletext-around-the-world-still/
Telidraw, a NAPLPS toolkit and editor, https://telidraw.com/
NAPLPS - Wikipedia, https://en.wikipedia.org/wiki/NAPLPS
draft-mavrakis-videotex-url-spec-00, https://datatracker.ietf.org/doc/html/draft-mavrakis-videotex-url-spec-00
Ultimate Oldschool PC Font Pack: v2.0 released - Pouet.net, https://www.pouet.net/topic.php?which=11961
May 1995 - The Vintage Technology Digital Archive, https://vtda.org/pubs/BBS/BBS_VOL_06_05_1995_May.pdf
