# Campus Bourse – programme LinkedIn « construire la crédibilité » (lancé le 19 nov 2026)

Positionnement : **Campus Bourse – investir à la BRVM avec méthode, discipline et vision long terme.**
Éditeur : Campus des Bâtisseurs. Site : https://campusbourse.com. Publié sur la page LinkedIn Campus des Bâtisseurs.
Exception à la phase confiance (décision de l'utilisateur du 19 nov 2026) : sur LinkedIn, ces 3 posts peuvent présenter Campus Bourse et inviter à l'essai gratuit. Les autres réseaux restent en phase confiance.

## Rythme
3 posts par semaine : **lundi, mercredi, vendredi à 11h00** (Dakar). Ils remplacent le carrousel valeur LinkedIn de ces jours-là (le carrousel valeur reste sur LinkedIn mardi, jeudi, samedi à 11h ; le carrousel 16h reste à 13h du lundi au samedi).

## Les 5 thèmes, en rotation stricte (le suivant après le dernier noté dans journal.csv)
1. **ANALYSE** – une société cotée à la BRVM : activité, chiffres clés des derniers exercices publiés (chiffre d'affaires, résultat net, ROE, endettement, dividende), forces, risques, questions à se poser. Jamais de verdict « à acheter / à vendre / sous-évaluée ».
2. **ERREUR** – une erreur fréquente des investisseurs (acheter parce que le cours monte, rendement du dividende seul, rumeur, concentration, panique, absence de fonds d'urgence…) et la discipline qui l'évite.
3. **VALEUR** – valeur intrinsèque et cours de marché : définition, méthode (bénéfices, dividendes, marge de sécurité), exemple chiffré PÉDAGOGIQUE sur une « Société A » fictive, signalé « Exemple pédagogique ».
4. **LONG TERME** – investir à 5, 10 et 20 ans : intérêts composés, réinvestissement des dividendes, régularité ; calculs exacts (vérifiés en Python), hypothèses écrites, jamais de rendement promis.
5. **DÉMO** – une fonctionnalité réelle de Campus Bourse (liste ci-dessous), ce qu'elle permet de faire et pour qui, avec l'invitation à l'essai gratuit de 7 jours.

Ordre de départ : 1er post = DÉMO (lancement), puis ANALYSE, ERREUR, VALEUR, LONG TERME, DÉMO…
Sociétés déjà analysées : colonne `sujet` de journal.csv (ne pas répéter avant que les grandes capitalisations aient été couvertes).

## Fonctionnalités réelles (source : cahier des charges du projet, 15 nov 2026). N'en citer AUCUNE autre.
- 46 sociétés cotées à la BRVM analysées, comptes de 5 exercices issus des publications officielles.
- 4 piliers d'évaluation synthétisés sur 100 : Qualité, Valeur intrinsèque, Croissance, Risque (« Campus Scores », « Campus Wealth Score »).
- « Test des doyens de la Bourse ».
- Fiche entreprise en 8 sections, lisible en 3 niveaux : Débutant, Intermédiaire, Avancé.
- Comparer deux sociétés ; Top BRVM ; tableau de bord ; Master Liste.
- Projections à long terme (5 et 10 ans).
- Dividendes ; analyse technique (indicateurs expliqués) ; actualités ; assistant IA.
- Mon portefeuille, avec alerte personnelle sur la concentration sectorielle (plafond prudentiel de 35 %) ; liste de suivi ; simulation « et si le cours était… ».
- Contenus pédagogiques : Comprendre la bourse, Fondamentaux (action, obligations, FCP, cours, dividende).
- Offres : Découverte gratuite ; essai Premium 7 jours sans carte bancaire (activation après confirmation de l'e-mail, un essai par personne) ; Premium 5 000 FCFA / mois ou 50 000 FCFA / an (paiement unique, sans renouvellement automatique).

## Interdits (bloquants)
- Ne JAMAIS publier les décisions de la plateforme (ACHETER, CONSERVER, RÉDUIRE…), un score ou un « prix maximum » pour une société nommée : ce serait un conseil en investissement.
- Jamais « v8 », « classeur », date d'extraction ou de cours des données de la plateforme.
- Jamais de rendement garanti, de « titre sous-évalué » affirmé, de faux témoignage, de faux nombre d'utilisateurs, de capture d'écran inventée.
- Chiffres d'une société : uniquement depuis des sources publiques ouvertes (rapport annuel, BRVM, communiqués), datés, source en une ligne.
- Mention finale obligatoire : « Outil d'aide à l'analyse. Ceci n'est pas un conseil en investissement. »

## Format
- Texte LinkedIn : accroche forte en 1re ligne (≤ 120 caractères), 900 à 1 300 caractères, phrases courtes, une ligne vide entre les blocs, 1 question aux lecteurs, 3 à 5 hashtags (#BRVM #Investissement #CampusBourse + 1 ou 2 selon le sujet). Pas de lien dans le texte : le lien https://campusbourse.com va dans le PREMIER COMMENTAIRE.
- Carrousel PDF (5 à 7 diapos) avec outils/carousel.py, clé racine "territoire": "bourse" ; dernière diapo : big = « campusbourse.com ».
- DÉMO : si des captures réelles sont dans campus-bourse/captures/ (PNG/JPG fournis par l'utilisateur), les utiliser en priorité comme images ; sinon carrousel explicatif, sans fausse capture.

## Mesure
journal.csv : date, thème, sujet, post Metricool. Le rapport du lundi suit les impressions, réactions, commentaires, partages et clics de ces posts, comparés aux autres posts LinkedIn.
