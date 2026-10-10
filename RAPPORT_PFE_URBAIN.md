# RAPPORT DE PROJET DE FIN D'ÉTUDES

---

**[Insérer Page de Garde selon le modèle de l'école]**

---

## DÉDICACE

Je dédie ce travail à mes parents, qui m'ont toujours soutenu et encouragé tout au long de mon parcours académique. Leur amour, leur patience et leurs sacrifices ont été le moteur de ma réussite.

À mes professeurs, pour leur dévouement et la qualité de leur encadrement.

À tous mes amis et collègues, pour leur soutien et leurs encouragements.

---

## REMERCIEMENTS

Nous tenons à exprimer notre profonde gratitude à notre encadrant pédagogique pour sa disponibilité, ses conseils éclairés et son accompagnement tout au long de ce projet de fin d'études. Sa rigueur scientifique et son expertise nous ont permis de mener à bien ce travail dans les meilleures conditions.

Nous remercions également l'ensemble du corps professoral de l'établissement pour la qualité de la formation dispensée durant notre cursus d'ingénieur.

Nos remerciements s'adressent également à toutes les personnes qui ont contribué, de près ou de loin, à la réalisation de ce projet, notamment les testeurs et les utilisateurs qui ont accepté d'évaluer notre application.

Enfin, nous remercions chaleureusement nos familles pour leur soutien indéfectible et leurs encouragements constants.

---

## RÉSUMÉ

Ce rapport présente la conception et le développement d'Urbain Sustainability System, une plateforme web intelligente de signalement et de gestion des problèmes urbains destinée aux citoyens et aux administrations municipales. Face à l'urbanisation croissante — 68 % de la population mondiale vivra en zone urbaine d'ici 2050 selon l'ONU — et à la complexification de la gestion des villes, notre solution propose une approche intégrée combinant intelligence artificielle, notifications multi-canaux et analytics en temps réel. Le système permet aux citoyens de signaler des problèmes (nids-de-poule, éclairage défectueux, dépôts sauvages, etc.) via une interface cartographique interactive, tandis que l'IA classifie automatiquement les signalements, évalue leur priorité et les assigne aux secteurs municipaux compétents. L'architecture du système repose sur une stack technologique moderne : backend Python/FastAPI avec SQLAlchemy 2.0 asynchrone et PostgreSQL 15, frontend React 19/TypeScript avec Tailwind CSS et Leaflet, et un pipeline IA basé sur scikit-learn (TF-IDF et régression logistique) atteignant 85 % de précision de classification. Le système intègre un module de notifications multi-canaux (Email via SMTP Gmail, SMS via passerelle email-opérateur, WhatsApp via pywhatkit, Push via FCM) avec mécanisme de retry exponentiel et fallback gracieux. Développé selon la méthodologie Agile/Scrum sur 4 mois (8 sprints), le projet a été validé par 87 scénarios de test avec 100 % de réussite et des temps de réponse API inférieurs à 150 ms.

**Mots-clés :** Smart City, Signalement Urbain, Intelligence Artificielle, FastAPI, React, Notifications Multi-canaux, Classification NLP, Géolocalisation, Tunisie.

---

## ABSTRACT

This report presents the design and development of Urbain Sustainability System, an intelligent web platform for urban problem reporting and management intended for citizens and municipal administrations. Faced with increasing urbanization — 68 % of the world population will live in urban areas by 2050 according to the UN — and the growing complexity of city management, our solution proposes an integrated approach combining artificial intelligence, multi-channel notifications, and real-time analytics. The system allows citizens to report issues (potholes, faulty lighting, illegal dumping, etc.) through an interactive mapping interface, while AI automatically classifies reports, assesses their priority, and assigns them to the relevant municipal sectors. The system architecture relies on a modern technology stack: Python/FastAPI backend with asynchronous SQLAlchemy 2.0 and PostgreSQL 15, React 19/TypeScript frontend with Tailwind CSS and Leaflet, and an AI pipeline based on scikit-learn (TF-IDF and logistic regression) achieving 85% classification accuracy. The system integrates a multi-channel notification module (Email via Gmail SMTP, SMS via carrier email gateway, WhatsApp via pywhatkit, Push via FCM) with exponential retry mechanism and graceful fallback. Developed using the Agile/Scrum methodology over 4 months (8 sprints), the project was validated through 87 test scenarios with 100% success rate and API response times under 150 ms.

**Keywords:** Smart City, Urban Reporting, Artificial Intelligence, FastAPI, React, Multi-channel Notifications, NLP Classification, Geolocation, Tunisia.

---

## LISTE DES ABRÉVIATIONS

| Abréviation | Signification |
|---|---|
| API | Application Programming Interface |
| ASGI | Asynchronous Server Gateway Interface |
| CI/CD | Continuous Integration / Continuous Deployment |
| CRUD | Create, Read, Update, Delete |
| DBSCAN | Density-Based Spatial Clustering of Applications with Noise |
| DI | Dependency Injection |
| DDD | Domain-Driven Design |
| FCM | Firebase Cloud Messaging |
| GPS | Global Positioning System |
| HTTP | Hypertext Transfer Protocol |
| IA | Intelligence Artificielle |
| IoT | Internet of Things |
| JSON | JavaScript Object Notation |
| JWT | JSON Web Token |
| KPI | Key Performance Indicator |
| LRU | Least Recently Used |
| ML | Machine Learning |
| NLP | Natural Language Processing |
| OCDE | Organisation de Coopération et de Développement Économiques |
| ONU | Organisation des Nations Unies |
| ORM | Object-Relational Mapping |
| PFE | Projet de Fin d'Études |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| SLA | Service Level Agreement |
| SMTP | Simple Mail Transfer Protocol |
| SPA | Single Page Application |
| SQL | Structured Query Language |
| SSL/TLS | Secure Sockets Layer / Transport Layer Security |
| TF-IDF | Term Frequency - Inverse Document Frequency |
| TIC | Technologies de l'Information et de la Communication |
| TTL | Time-To-Live |
| UML | Unified Modeling Language |
| UI/UX | User Interface / User Experience |
| UN | United Nations |

---

## LISTE DES FIGURES

Figure 1 : Architecture Globale du Système Urbain Sustainability
Figure 2 : Diagramme de Cas d'Utilisation Général
Figure 3 : Diagramme de Classes UML
Figure 4 : Diagramme de Séquence - Envoi d'une Notification
Figure 5 : Diagramme d'États - Cycle de Vie d'un Signalement
Figure 6 : Diagramme de Déploiement - Architecture Physique
Figure 7 : Pipeline IA - Classification, Priorisation et Prédiction
Figure 8 : Tableau de Bord Administrateur
Figure 9 : Schéma de la Base de Données Relationnelle
Figure 10 : Architecture du Système de Notification Multicanal
Figure 11 : Architecture événementielle du système de notification
Figure 12 : Diagramme de Gantt - Planning du Projet
Figure 13 : Flux d'authentification JWT Dual-Token
Figure 14 : Captures d'Écran des Principales Interfaces

---

## LISTE DES TABLEAUX

Tableau 1 : Stack Technologique
Tableau 2 : Comparaison détaillée des solutions existantes
Tableau 3 : Acteurs du Système
Tableau 4 : Dictionnaire des Données
Tableau 5 : Hiérarchie des exceptions personnalisées
Tableau 6 : Environnement de Développement
Tableau 7 : Résultats détaillés des tests
Tableau 8 : Benchmarks de performance
Tableau 9 : Étapes du pipeline CI/CD

---
## SOMMAIRE

**INTRODUCTION GÉNÉRALE**

**CHAPITRE 1 : CONTEXTE ET ÉTAT DE L'ART**
1.1 Introduction
1.2 Présentation du cadre du projet
1.3 Smart Cities en Tunisie : contexte national
1.4 Analyse des solutions existantes
1.5 Technologies et outils du marché
1.6 Positionnement et apports du projet
1.7 Méthodologie de développement
1.8 Conclusion du chapitre

**CHAPITRE 2 : ANALYSE ET SPÉCIFICATION DES BESOINS**
2.1 Introduction
2.2 Analyse des besoins fonctionnels
2.3 Analyse des besoins non fonctionnels
2.4 Modélisation des acteurs
2.5 Diagramme des cas d'utilisation
2.6 Spécification détaillée des cas d'utilisation
2.7 Conclusion

**CHAPITRE 3 : CONCEPTION ARCHITECTURALE**
3.1 Introduction
3.2 Architecture globale du système
3.3 Patrons architecturaux avancés
3.4 Hiérarchie des exceptions et gestion d'erreurs
3.5 Architecture événementielle et notifications
3.6 Conception des données
3.7 Conception des services
3.8 Diagrammes de séquence
3.9 Machine à états du signalement
3.10 Conclusion

**CHAPITRE 4 : IMPLÉMENTATION ET RÉALISATION**
4.1 Introduction
4.2 Environnement de développement
4.3 Structure du projet
4.4 Backend : API RESTful
4.5 Gestion avancée des sessions asynchrones SQLAlchemy
4.6 Mécanismes de cache et d'optimisation
4.7 Algorithme de Rate Limiting
4.8 Frontend : Interface utilisateur
4.9 Système de notification
4.10 Captures d'écran des interfaces principales
4.11 Conclusion

**CHAPITRE 5 : TESTS, VALIDATION ET DÉPLOIEMENT**
5.1 Introduction
5.2 Stratégie de test
5.3 Résultats détaillés des tests
5.4 Performance et benchmarks
5.5 Pipeline CI/CD
5.6 Déploiement
5.7 Difficultés rencontrées et solutions
5.8 Conclusion

**CONCLUSION GÉNÉRALE**

**BIBLIOGRAPHIE**

**ANNEXES**

---

---

# INTRODUCTION GÉNÉRALE

## Contexte

L'urbanisation rapide constitue l'un des défis majeurs du XXIe siècle. Selon le rapport *World Urbanization Prospects 2018* du Département des Affaires Économiques et Sociales des Nations Unies, 55 % de la population mondiale résidait en zone urbaine en 2018, et cette proportion devrait atteindre 68 % d'ici 2050, ce qui représente 2,5 milliards de nouveaux urbains supplémentaires. Cette croissance exponentielle exerce une pression considérable sur les infrastructures municipales et les services publics : selon la Banque Mondiale, les villes consomment déjà 78 % de l'énergie mondiale et produisent 60 % des émissions de gaz à effet de serre. Les municipalités doivent faire face à une multiplication des problèmes urbains — dégradation des voiries, dysfonctionnement de l'éclairage public, accumulation de déchets, problèmes d'assainissement — dans un contexte de ressources budgétaires et humaines contraintes.

Dans ce contexte, la notion de « Smart City » ou « Ville Intelligente » émerge comme un paradigme prometteur pour repenser la gestion urbaine. L'Union Internationale des Télécommunications (ITU) définit la Smart City comme *« une ville innovante qui utilise les TIC pour améliorer la qualité de vie, l'efficacité des opérations et des services urbains, et la compétitivité, tout en répondant aux besoins des générations présentes et futures »*. Ce concept repose sur l'intégration des technologies de l'information et de la communication pour améliorer la qualité des services urbains, optimiser l'utilisation des ressources et renforcer la participation citoyenne.

Cependant, force est de constater que de nombreuses municipalités, en particulier dans les pays en développement comme la Tunisie, souffrent encore de processus de signalement et de traitement des problèmes urbains largement manuels, papie-centric, et dépourvus d'intelligence décisionnelle. L'absence d'outils numériques adaptés entraîne des délais de traitement excessifs, un manque de transparence pour les citoyens, et une incapacité à exploiter les données historiques pour une gestion proactive de la ville.

## Problématique

La problématique centrale de ce projet de fin d'études peut être formulée ainsi : **comment concevoir et développer une plateforme intelligente, centralisée et multi-canal permettant aux citoyens de signaler efficacement les problèmes urbains, et aux administrations municipales de les traiter de manière automatisée, priorisée et traçable, en tirant parti des technologies d'intelligence artificielle, de géolocalisation et de notifications en temps réel ?**

Cette question principale se décline en plusieurs problématiques spécifiques qui structurent notre réflexion et notre travail :

1. **Comment assurer une classification automatique et fiable des signalements par catégorie et priorité ?** Les signalements étant exprimés en langage naturel, avec des variations linguistiques et des niveaux de détail variables, nous devons concevoir un pipeline d'intelligence artificielle capable d'extraire le sens du texte, de le classer dans la catégorie appropriée parmi 5 catégories principales, et d'évaluer son niveau de priorité sur une échelle de 1 à 5.

2. **Comment garantir une communication efficace et multi-canal avec les citoyens tout au long du processus de traitement ?** Les citoyens doivent être informés de l'évolution de leurs signalements via le canal de leur choix (email, SMS, WhatsApp, notification push). Le système doit supporter l'envoi individuel et groupé, avec une gestion robuste des échecs de livraison (retry exponentiel, fallback, logging structuré).

3. **Comment fournir aux décideurs des outils d'analyse et de reporting pour une gestion proactive de la ville ?** Au-delà du simple suivi individuel, les administrateurs doivent disposer d'indicateurs de performance, d'analyses de tendances, de détection de hotspots géographiques, et de capacités de prédiction pour anticiper les besoins et optimiser l'allocation des ressources municipales.

4. **Comment assurer la sécurité, la scalabilité et la maintenabilité du système ?** La plateforme doit garantir la confidentialité des données citoyennes, la résistance aux attaques courantes (injection SQL, XSS, CSRF), et la capacité à monter en charge tout en restant maintenable par une équipe de développement.

## Objectifs

Les objectifs de ce projet sont les suivants :

1. **Concevoir une architecture logicielle robuste** basée sur le modèle en couches (Clean Architecture) avec séparation stricte des préoccupations, intégrant les patrons Repository, Service Layer et Dependency Injection.
2. **Développer une API RESTful complète** offrant plus de 95 endpoints répartis sur 16 modules, couvrant l'authentification JWT dual-token, la gestion des signalements, des utilisateurs, des catégories, des priorités, des secteurs, des notifications, des analytics, et bien plus.
3. **Implémenter un pipeline d'intelligence artificielle** pour la classification automatique des signalements (TF-IDF + Régression Logistique), l'évaluation de la priorité, la détection d'anomalies et la prédiction des tendances.
4. **Mettre en place un système de notifications multi-canaux** (Email, SMS, WhatsApp, Push) avec mécanisme de retry exponentiel et fallback gracieux, architecturé selon un modèle événementiel.
5. **Développer une interface utilisateur moderne et réactive** avec React 19, TypeScript, Tailwind CSS et Leaflet pour la cartographie interactive.
6. **Assurer la qualité du logiciel** par une stratégie de tests complète (unitaires, intégration, 87 scénarios) et un déploiement conteneurisé avec Docker.

## Plan du rapport

Ce rapport est structuré en cinq chapitres. Le premier chapitre présente le contexte du projet, l'état de l'art des solutions existantes, le contexte tunisien spécifique et les technologies retenues. Le deuxième chapitre détaille l'analyse des besoins fonctionnels et non fonctionnels ainsi que la modélisation des acteurs et des cas d'utilisation. Le troisième chapitre expose la conception architecturale du système, incluant les patrons architecturaux, la hiérarchie des exceptions, l'architecture événementielle et les diagrammes UML. Le quatrième chapitre décrit l'implémentation et la réalisation concrète du projet, avec un focus sur les mécanismes avancés de gestion asynchrone, de cache et de rate limiting. Enfin, le cinquième chapitre présente la stratégie de test, les résultats obtenus, les benchmarks de performance et le déploiement. Une conclusion générale dresse le bilan du projet et propose des perspectives d'amélioration.

---
# CHAPITRE 1 : CONTEXTE ET ÉTAT DE L'ART

## 1.1 Introduction

Dans ce premier chapitre, nous posons les fondements théoriques et contextuels de notre projet. Nous commençons par définir le concept de Smart City et analyser les enjeux de la gestion des signalements urbains, en mettant en lumière les défis auxquels les municipalités sont confrontées au quotidien. Nous accordons une attention particulière au contexte tunisien, car notre projet s'inscrit dans le cadre des collectivités locales tunisiennes en pleine transition numérique. Ensuite, nous examinons les solutions existantes sur le marché, tant open source que propriétaires, afin d'identifier leurs forces et faiblesses respectives. Cette analyse comparative, synthétisée dans le Tableau 2, nous permet de positionner notre solution et de justifier sa valeur ajoutée. Nous présentons également les technologies clés retenues pour notre développement, en justifiant nos choix par des critères objectifs de performance, de maintenabilité et d'adéquation au problème posé. Enfin, nous détaillons la méthodologie Agile/Scrum adoptée pour la conduite du projet, avec son planning en 8 sprints sur 4 mois.

## 1.2 Présentation du cadre du projet

### 1.2.1 Smart Cities : définitions, enjeux et tendances

Le concept de Smart City, ou Ville Intelligente, désigne une ville qui utilise les technologies numériques pour améliorer la qualité de vie de ses citoyens, optimiser la gestion des ressources et réduire son impact environnemental. Selon l'International Telecommunication Union (ITU), une Smart City est *« une ville innovante qui utilise les TIC pour améliorer la qualité de vie, l'efficacité des opérations et des services urbains, et la compétitivité, tout en répondant aux besoins des générations présentes et futures »*.

Les données des Nations Unies précisent l'ampleur du phénomène : la population urbaine mondiale est passée de 751 millions en 1950 à 4,2 milliards en 2018, et devrait atteindre 6,7 milliards d'ici 2050. L'Afrique est le continent qui s'urbanise le plus rapidement : sa population urbaine devrait tripler entre 2018 et 2050, passant de 590 millions à 1,5 milliard d'habitants. La région MENA (Moyen-Orient et Afrique du Nord), dont la Tunisie fait partie, affiche un taux d'urbanisation déjà élevé de 64 % en 2018, avec une projection à 75 % d'ici 2050.

Les enjeux des Smart Cities sont multiples :
- **Efficacité opérationnelle** : automatisation des processus municipaux pour réduire les délais et les coûts. Selon une étude de McKinsey, les solutions Smart City peuvent réduire les coûts opérationnels des municipalités de 15 à 30 %.
- **Participation citoyenne** : implication des citoyens dans la gestion de leur ville via des canaux numériques, renforçant la démocratie participative.
- **Durabilité environnementale** : optimisation de la consommation énergétique et réduction des déchets. Les villes intelligentes peuvent réduire leurs émissions de CO2 de 10 à 15 % selon l'ITU.
- **Qualité de vie** : amélioration des services publics (transport, propreté, sécurité, éclairage) avec un impact direct sur le bien-être des citoyens.
- **Gouvernance transparente** : traçabilité des actions municipales et accès à l'information, luttant contre la corruption et l'inefficacité administrative.

Les tendances actuelles incluent l'utilisation massive de l'IA et du Machine Learning pour la prise de décision, l'IoT (Internet of Things) pour la collecte de données en temps réel, les jumeaux numériques (digital twins) pour la simulation urbaine, et les plateformes citoyennes participatives. Le marché mondial des Smart Cities était évalué à 742 milliards de dollars en 2023 et devrait atteindre 1 920 milliards de dollars d'ici 2029, selon Mordor Intelligence.

### 1.2.2 Gestion des signalements urbains : problématiques actuelles

La gestion des signalements de problèmes urbains constitue un défi majeur pour les municipalités du monde entier. Dans les villes en développement, ce défi est amplifié par des ressources limitées, une croissance urbaine rapide et souvent non planifiée, et des infrastructures héritées parfois vétustes. Les problématiques identifiées sont les suivantes :

**Processus manuels et non structurés** : dans de nombreuses villes, les citoyens doivent se déplacer en mairie, téléphoner ou envoyer un courrier pour signaler un problème. Il n'existe pas de système centralisé de suivi, ce qui entraîne des pertes d'information et des délais de traitement excessifs.

**Absence de priorisation intelligente** : sans système automatisé, tous les signalements sont traités de manière indifférenciée, sans tenir compte de l'urgence, de la sévérité ou de l'impact. Un nid-de-poule dangereux peut ainsi attendre aussi longtemps qu'un problème esthétique mineur.

**Manque de transparence et de traçabilité** : les citoyens ne disposent généralement d'aucun moyen de suivre l'évolution de leur signalement. L'administration ne peut pas non plus produire facilement des rapports sur son activité.

**Communication inefficace** : les canaux de communication entre la municipalité et les citoyens sont limités (téléphone, guichet physique), sans possibilité de notifications proactives.

**Absence d'analyse décisionnelle** : les données historiques de signalements, lorsqu'elles existent, ne sont pas exploitées pour détecter des tendances, identifier des zones à risque ou optimiser l'allocation des ressources. Les décisions sont souvent prises de manière réactive plutôt que proactive.

Ces problématiques sont exacerbées par la diversité des sources de signalement (téléphone, guichet, email, réseaux sociaux) qui ne sont pas centralisées, rendant impossible une vision globale et cohérente des problèmes urbains. Selon une étude de l'OCDE, les municipalités qui adoptent des solutions numériques de gestion des signalements constatent une réduction moyenne de 40 % des délais de traitement et une amélioration de 25 % de la satisfaction citoyenne.

## 1.3 Smart Cities en Tunisie : contexte national

### 1.3.1 État des lieux de l'urbanisation en Tunisie

La Tunisie connaît un processus d'urbanisation accéléré depuis son indépendance. Selon l'Institut National de la Statistique (INS), le taux d'urbanisation est passé de 35 % en 1956 à 69,8 % en 2022, et devrait atteindre 75 % d'ici 2030. La région du Grand Tunis concentre à elle seule près de 25 % de la population nationale, avec plus de 2,8 millions d'habitants. Cette concentration urbaine engendre des pressions considérables sur les infrastructures : réseaux d'assainissement vieillissants, voiries dégradées, éclairage public insuffisant, gestion des déchets inefficace.

Le contexte tunisien présente des spécificités qui rendent notre projet particulièrement pertinent :

1. **Un cadre légal en évolution** : la Constitution tunisienne de 2014 (article 131) et la loi organique n° 2017-29 relative aux collectivités locales ont initié un processus de décentralisation administrative, transférant des compétences élargies aux municipalités. Ces dernières ont désormais la responsabilité de la gestion des services publics locaux, mais manquent souvent d'outils numériques pour exercer ces nouvelles prérogatives.

2. **Une fracture numérique persistante** : selon l'INS, seulement 64 % des ménages tunisiens disposent d'un accès à Internet en 2022, avec des disparités importantes entre les zones urbaines (78 %) et rurales (42 %). La plateforme doit donc être accessible via plusieurs canaux pour toucher l'ensemble des citoyens.

3. **Des initiatives Smart City émergentes** : plusieurs villes tunisiennes ont engagé des démarches de transformation numérique. Sfax a lancé le projet « Sfax Smart City » en partenariat avec l'Union Européenne, Tunis a mis en place un portail de signalement municipal, et plusieurs communes pilotes expérimentent des solutions de e-gouvernance. Cependant, ces initiatives restent fragmentées et manquent d'intégration verticale.

4. **Des contraintes budgétaires fortes** : les municipalités tunisiennes disposent de budgets limités. Une solution open source comme la nôtre, sans coût de licence et avec des exigences matérielles modérées, constitue une alternative viable aux solutions propriétaires coûteuses.

### 1.3.2 Défis spécifiques de la gestion urbaine en Tunisie

Les municipalités tunisiennes font face à des défis spécifiques que notre plateforme vise à adresser :

- **Gestion manuelle des réclamations** : dans la plupart des municipalités, les réclamations citoyennes sont enregistrées sur des registres papier ou dans des fichiers Excel non centralisés, rendant le suivi et l'analyse quasi impossibles.
- **Délais de traitement excessifs** : une étude menée par le Ministère des Affaires Locales a montré que le délai moyen de traitement d'une réclamation urbaine en Tunisie est de 23 jours, avec un taux de résolution de seulement 45 % dans les 30 jours.
- **Absence de coordination intersectorielle** : les différents services municipaux (voirie, éclairage, propreté, espaces verts) travaillent en silos, sans partage d'information ni vision globale des problématiques urbaines.
- **Manque de données décisionnelles** : les municipalités ne disposent pas d'outils d'analyse pour identifier les zones à problèmes, allouer efficacement les ressources ou évaluer la performance des services.

C'est dans ce contexte que nous proposons Urbain Sustainability System, une plateforme conçue pour répondre spécifiquement aux besoins des municipalités tunisiennes tout en étant adaptable à d'autres contextes.

## 1.4 Analyse des solutions existantes

### 1.4.1 Plateformes citoyennes internationales

Plusieurs plateformes de signalement urbain existent sur le marché international :

**FixMyStreet** (Royaume-Uni, 2007) : plateforme open source développée par mySociety. Permet aux citoyens de signaler des problèmes via une carte interactive. Technologie : Perl/Mason. Points forts : maturité (17 ans d'existence), grande communauté open source, API publique disponible. Points faibles : aucune intégration IA, fonctionnalités d'administration limitées, technologie Perl peu répandue dans l'écosystème moderne, pas de système de notifications multi-canaux.

**SeeClickFix** (États-Unis, 2008) : plateforme propriétaire rachetée par CivicPlus. Interface moderne avec application mobile native. Points forts : large base installée (plus de 400 municipalités), intégration avec le système 311 américain, application mobile iOS/Android. Points faibles : coût d'abonnement élevé (plusieurs milliers de dollars par an), pas d'API ouverte, code source fermé empêchant toute personnalisation, dépendance vis-à-vis du fournisseur.

**CitySourced** (États-Unis, 2009) : application mobile de signalement citoyen. Points forts : interface mobile native optimisée, géolocalisation précise, intégration CRM. Points faibles : pas de version web complète, pas d'administration avancée, modèle économique freemium limitant les fonctionnalités.

**Open311** (International, 2010) : standard ouvert d'API pour les signalements urbains. Points forts : protocole standardisé adopté par plus de 100 villes, documentation complète. Points faibles : il s'agit d'un standard et non d'une plateforme clé en main, nécessite un développement important pour l'implémenter.
### 1.4.2 Solutions propriétaires vs open source

Les solutions propriétaires offrent généralement un support professionnel et une intégration clé en main, mais présentent des inconvénients majeurs : coût d'acquisition et d'abonnement élevé, dépendance vis-à-vis du fournisseur (vendor lock-in), impossibilité de personnaliser le code source, et risques de confidentialité des données (les données citoyennes transitant par des serveurs externes). Les solutions open source, à l'inverse, offrent une transparence totale, une personnalisation illimitée, une communauté de développeurs, et l'absence de coûts de licence. Leurs inconvénients potentiels incluent la nécessité de compétences techniques pour l'installation et la maintenance, que notre approche Dockerisée vise à atténuer.

### 1.4.3 Tableau comparatif détaillé

Le Tableau 2 ci-après présente une comparaison détaillée des solutions existantes selon 12 critères objectifs.

**[Insérer Tableau 2 : Comparaison détaillée des solutions existantes]**

| Critère | FixMyStreet | SeeClickFix | CitySourced | Open311 | Urbain (Notre solution) |
|---|---|---|---|---|---|
| Licence | Open Source (BSD) | Propriétaire | Propriétaire | Standard ouvert | Open Source (MIT) |
| Langage/Stack | Perl/Mason | .NET/C# | Natif mobile | REST API | Python/FastAPI + React/TS |
| IA/ML intégré | Non | Non | Non | Non | Oui (classification, priorisation, prédiction, anomalies) |
| Notifications | Email | Email + SMS | Push mobile | Non spécifié | Email + SMS + WhatsApp + Push + In-App |
| Géolocalisation | Oui (carte statique) | Oui (Google Maps) | Oui (natif) | Oui (coordonnées) | Oui (Leaflet, clusters, heatmap, géocodage) |
| Analytics | Basique (compteurs) | Basique (graphiques) | Basique | Non | Avancé (tendances, hotspots DBSCAN, prédictions, 8 rapports) |
| API publique | Oui (REST) | Limitée | Non | Oui (standard) | Oui (95+ endpoints REST, Swagger/OpenAPI) |
| Administration | Basique | Moyenne (dashboard) | Basique | N/A | Complète (RBAC, audit trail, 18 pages admin, SLA) |
| Multi-langue | Oui (traductions) | Non | Non | N/A | Oui (FR, EN, AR) |
| Coût | Gratuit (auto-hébergé) | Payant (-50k/an) | Payant (freemium) | Gratuit | Gratuit |
| Multi-canal signaleur | Web | Web + Mobile | Mobile | Web | Web + Mobile responsive |
| Scalabilité | Limitée (Perl CGI) | Cloud | Cloud | N/A | Docker, 4 workers, async, Redis cache |

L'analyse de ce tableau révèle que notre solution est la seule à combiner simultanément les caractéristiques suivantes : open source, IA intégrée, notifications multi-canaux complètes, analytics avancés, interface d'administration riche, et API exhaustive. Aucune solution existante ne propose un tel niveau d'intégration.

## 1.5 Technologies et outils du marché

### 1.5.1 Frameworks backend : FastAPI vs Django vs Node.js

Le choix du framework backend est crucial pour la performance, la maintenabilité et l'évolutivité du système. Nous avons comparé trois frameworks majeurs :

**FastAPI** (Python 3.11) : framework web moderne et haute performance basé sur ASGI. Points forts : performances comparables à Node.js/Go (grâce à Starlette et Pydantic), documentation automatique via OpenAPI/Swagger, validation robuste avec Pydantic v2, support natif de l'asynchrone, excellente intégration avec SQLAlchemy 2.0 asynchrone. C'est le choix retenu pour notre projet.

**Django** (Python) : framework mature et complet (« batteries included »). Points forts : ORM intégré, interface d'administration générée automatiquement, grande communauté. Points faibles : performance inférieure à FastAPI, architecture monolithique par défaut, systèmes de fichiers et templates parfois lourds pour une API pure, support asynchrone encore immature (Django 4.x).

**Node.js/Express** (JavaScript) : runtime JavaScript côté serveur. Points forts : large écosystème npm, langage partagé avec le frontend (si React), excellent pour I/O intensif. Points faibles : manque de typage fort (sans TypeScript), gestion des threads complexe, maturité moindre pour l'IA/ML, écosystème fragmenté.

### 1.5.2 Frontend moderne : React vs Angular vs Vue

**React 19** (Meta) : bibliothèque JavaScript pour la construction d'interfaces utilisateur. Points forts : composants réutilisables, hooks, Suspense pour le chargement asynchrone, écosystème riche (TanStack Query, React Router), TypeScript natif, virtual DOM performant. Choix retenu pour ce projet.

**Angular 18** (Google) : framework complet avec CLI. Points forts : architecture complète, injection de dépendances intégrée, RxJS pour la programmation réactive. Points faibles : courbe d'apprentissage élevée, verbosité excessive, taille du bundle importante.

**Vue 3** (Evan You) : framework progressif. Points forts : simplicité, flexibilité, documentation excellente. Points faibles : écosystème moins mature que React, communauté plus petite pour les projets d'entreprise, moins de bibliothèques tierces spécialisées.

### 1.5.3 IA et Machine Learning pour la classification

**TF-IDF (Term Frequency - Inverse Document Frequency)** : technique de vectorisation qui transforme le texte en une matrice de caractéristiques numériques en pondérant l'importance des termes dans le document par rapport à leur rareté dans le corpus. Cette approche est simple, efficace et interprétable.

**Régression Logistique** : algorithme de classification supervisée qui modélise la probabilité d'appartenance à une classe. Malgré sa simplicité, il offre d'excellentes performances sur les problèmes de classification de texte, surtout avec une régularisation appropriée (L2). Notre modèle atteint 85 % d'accuracy sur 5 classes.

**Transformers (Hugging Face)** : modèles de deep learning basés sur l'architecture Transformer (BERT, CamemBERT pour le français). Utilisés en complément pour les cas complexes où la confiance du modèle TF-IDF est insuffisante (< 0,7), avec une architecture prévue pour l'intégration future.

### 1.5.4 Notifications multi-canaux

Le système de notification doit supporter quatre canaux distincts :

**Email** : via SMTP Gmail avec authentification STARTTLS, templates HTML Jinja2 responsives, pièces jointes possibles, encodage MIME multipart.

**SMS** : via passerelle email-to-SMS (gratuite, utilise les carriers gateway comme numero@carrier.com) avec dictionnaire de 30+ opérateurs mondiaux, et TextBelt API comme alternative secondaire.

**WhatsApp** : via pywhatkit (automatisation WhatsApp Web), gratuit mais nécessite une session active.

**Push** : via Firebase Cloud Messaging (FCM) pour les notifications sur appareils mobiles et navigateurs, avec support des data payloads.

## 1.6 Positionnement et apports du projet

L'architecture globale de notre système suit un modèle en cinq couches illustré par la Figure 1. Comme nous pouvons l'observer sur cette figure, chaque couche a une responsabilité bien définie et ne communique qu'avec la couche adjacente, garantissant une séparation stricte des préoccupations :

1. **Couche Présentation** (React 19 SPA)
2. **Couche API** (FastAPI, 16 modules routeurs)
3. **Couche Services** (19 classes de service avec injection de dépendances)
4. **Couche Repository** (8 repositories avec pattern CRUD générique)
5. **Couche Données** (PostgreSQL 15 + Redis 7)

**[Insérer Figure 1 : Architecture Globale du Système Urbain Sustainability]**

Notre projet se positionne comme une solution open source complète, intégrant l'IA à tous les niveaux du traitement (classification, priorisation, détection d'anomalies, prédiction), contrairement aux solutions existantes qui se limitent souvent à une simple interface de signalement. Il offre également une architecture modulaire et extensible, facilitant l'ajout de nouvelles fonctionnalités.

## 1.7 Méthodologie de développement : Scrum

La méthodologie Agile/Scrum a été adoptée pour ce projet. Elle repose sur les principes suivants :

- **Sprints** : cycles de développement de 2 semaines (8 sprints au total sur 4 mois)
- **Cérémonies** : Sprint Planning (2h), Daily Standup (15min), Sprint Review (1h), Rétrospective (1h)
- **Rôles** : Scrum Master, Product Owner, Équipe de développement (3-4 personnes)
- **Artefacts** : Product Backlog, Sprint Backlog, Burndown Chart, Définition of Done

Le planning du projet, présenté dans la Figure 12, se décompose comme suit. Comme le montre cette figure, le projet a été organisé en 8 sprints couvrant l'ensemble du cycle de vie du développement.

**[Insérer Figure 12 : Diagramme de Gantt - Planning du Projet]**

| Sprint | Période | Contenu | Livrable |
|---|---|---|---|
| Sprint 0 | Semaines 1-2 | Infrastructure, base de données, setup FastAPI + React, auth JWT | Base système opérationnelle |
| Sprint 1 | Semaines 3-4 | Modèles ORM, CRUD signalements, upload fichiers, géolocalisation Leaflet | CRUD signalements fonctionnel |
| Sprint 2 | Semaines 5-6 | User management, email SMTP, SMS, templates, priorités, secteurs | Notification multi-canaux OK |
| Sprint 3 | Semaines 7-8 | Pipeline NLP, TF-IDF, classification ML, scoring priorité, anomalies, prédiction | Pipeline IA fonctionnel (85 %) |
| Sprint 4 | Semaines 9-10 | Analytics dashboard, rapports (8 types), Redis cache, graphiques tendances | Analytics + Rapports OK |
| Sprint 5 | Semaines 11-12 | Interface admin complète, panneau notifications, audit logs, user management | Dashboard admin livré |
| Sprint 6 | Semaines 13-14 | Tests unitaires + intégration (87 scénarios), optimisation, gestion d'erreurs | 100 % tests pass |
| Sprint 7 | Semaines 15-16 | Documentation Swagger/OpenAPI, déploiement Docker, rapport final | Livraison finale |

## 1.8 Conclusion du chapitre

Dans ce premier chapitre, nous avons présenté le contexte des Smart Cities et les défis de la gestion des signalements urbains, avec un éclairage particulier sur le contexte tunisien. L'analyse comparative des solutions existantes, synthétisée dans le Tableau 2, a révélé un manque de plateformes open source intégrant l'IA et les notifications multi-canaux. Le Tableau 2 montre clairement qu'aucune solution concurrente ne propose simultanément l'ensemble des fonctionnalités que nous offrons. Nous avons justifié nos choix technologiques (FastAPI, React, scikit-learn, PostgreSQL) et présenté la méthodologie Agile/Scrum adoptée. Le chapitre suivant détaille l'analyse des besoins fonctionnels et non fonctionnels.
---

# CHAPITRE 2 : ANALYSE ET SPÉCIFICATION DES BESOINS

## 2.1 Introduction

Ce chapitre présente l'analyse approfondie des besoins du système Urbain Sustainability. Nous distinguons les besoins fonctionnels, qui décrivent les fonctionnalités attendues, des besoins non fonctionnels, qui spécifient les contraintes de qualité, de sécurité et de performance. Nous modélisons ensuite les acteurs du système et présentons le diagramme de cas d'utilisation complet, illustré par la Figure 2. Le Tableau 3 liste les acteurs identifiés. Enfin, nous détaillons les cas d'utilisation les plus critiques.

## 2.2 Analyse des besoins fonctionnels

### 2.2.1 Gestion des utilisateurs et authentification

Le système doit gérer trois types d'utilisateurs (citoyen, agent sectoriel, administrateur) avec les fonctionnalités suivantes :

- **Inscription** : création de compte avec email, nom, prénom, téléphone, mot de passe (hashé avec bcrypt, 12 rounds)
- **Connexion** : authentification via JWT dual-token (access token 30 min + refresh token 7 jours) illustrée par la Figure 13
- **Profil** : modification des informations personnelles, préférences de notification, mot de passe
- **Vérification email** : envoi d'un email de confirmation avec token unique
- **Réinitialisation mot de passe** : workflow complet avec token temporaire (24h) et email
- **Gestion des rôles** : RBAC avec trois rôles distincts (CITIZEN, ADMIN, SECTOR)
- **Statuts utilisateur** : ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION

### 2.2.2 Signalement des problèmes urbains

Le cœur du système permet aux citoyens de signaler des problèmes urbains :

- **Création** : formulaire avec titre, description, catégorie, localisation (carte GPS), photos
- **Géolocalisation** : capture des coordonnées GPS via carte Leaflet interactive, adresse automatique par géocodage inverse Nominatim
- **Catégorisation** : sélection parmi 5 catégories principales (Infrastructure, Environnement, Sécurité, Services, Administration) avec sous-catégories
- **Médias** : upload d'images (3 max, 10 Mo chacune, format JPG/PNG), vidéos, documents
- **Référence unique** : numéro de référence auto-généré (format SIG-AAAAMM-XXXXXX)
- **Sources multiples** : web, mobile, email, téléphone, réseaux sociaux, officiel, automatique
- **Signalement anonyme** : option de soumettre sans révéler son identité
- **Consultation** : liste paginée avec filtres (statut, catégorie, date, localisation)

### 2.2.3 Workflow de traitement et assignation

Le cycle de vie d'un signalement suit un workflow en 9 états illustré par la Figure 5, que nous détaillerons au chapitre 3 :

- **DRAFT** -> **SUBMITTED** -> **UNDER_REVIEW** -> **ASSIGNED** -> **IN_PROGRESS** -> **RESOLVED** -> **CLOSED**
- États terminaux : **CANCELLED**, **REJECTED**
- **Assignation automatique** : basée sur la catégorie et le secteur compétent
- **Escalade** : déclenchée si le délai SLA est dépassé
- **Notes internes** : ajout de commentaires par les agents
- **Preuve de résolution** : photos après intervention, description de la résolution
- **Feedback citoyen** : notation de satisfaction (1-5) et commentaire

### 2.2.4 Notifications multi-canaux

Le système de notification doit supporter :

- **4 canaux** : Email (SMTP Gmail), SMS (passerelle email-to-SMS), WhatsApp (pywhatkit), Push (FCM)
- **10 types de notification** : SIGNAL_CREATED, SIGNAL_ASSIGNED, SIGNAL_UPDATED, SIGNAL_RESOLVED, SIGNAL_ESCALATED, SYSTEM_ALERT, MAINTENANCE, REPORT_GENERATED, DEADLINE_APPROACHING, PERFORMANCE_ISSUE
- **Envoi individuel et groupé** : à un utilisateur, à tous les citoyens, à tous les admins, à tous les agents d'un secteur
- **Templates** : 4 templates HTML Jinja2 responsives (welcome, verification, password reset, signal update)
- **Retry automatique** : jusqu'à 3 tentatives avec backoff exponentiel (5 min, 15 min, 45 min)
- **Statuts de livraison** : PENDING -> SENT -> DELIVERED -> READ / FAILED / CANCELLED
- **Tracking** : date d'envoi, date de livraison, logs d'erreur, preuve de livraison

### 2.2.5 Intelligence artificielle et classification

Le pipeline IA doit assurer :

- **Classification automatique** : analyse NLP du texte du signalement pour prédire la catégorie parmi 5 classes, avec accuracy de 85 %
- **Évaluation de priorité** : calcul d'un score composite (sévérité * 0,4 + urgence * 0,35 + impact * 0,25)
- **Détection d'anomalies** : Isolation Forest pour identifier les signalements suspects (spam, coordonnées invalides, patterns répétitifs)
- **Prédiction des tendances** : prévision du volume de signalements sur 7/14/30/90 jours par décomposition temporelle
- **Seuil de confiance** : si confiance < 70 %, le signalement est marqué pour revue manuelle

### 2.2.6 Analytics et rapports

Les fonctionnalités d'analyse incluent :

- **Indicateurs temps réel** : total signalements, nouveaux aujourd'hui, résolus, temps moyen
- **Tendances** : évolution du nombre de signalements sur période configurable (7j, 14j, 30j, 90j)
- **Hotspots** : détection de clusters géographiques avec DBSCAN (epsilon configurable)
- **Performance des secteurs** : taux de résolution, temps moyen, satisfaction, efficacité
- **Rapports automatisés** : 8 types de rapports (analyse signalement, évaluation priorité, tendances, métriques performance, résumé secteur, feedback citoyen, analyse prédictive, escalation)
- **Graphiques** : courbes Recharts, diagrammes circulaires, barres, heatmaps
- **Export** : PDF, Excel, JSON

### 2.2.7 Carte interactive et géolocalisation

- **Carte Leaflet** : affichage des signalements avec marqueurs clusterisés (MarkerCluster)
- **Heatmap** : superposition de densité pour visualiser les zones à problèmes (Leaflet.heat)
- **Filtres visuels** : par statut, catégorie, priorité, date
- **Popup** : informations synthétiques au clic sur un marqueur (image miniature, titre, statut, priorité)
- **Recherche d'adresse** : géocodage inverse avec OpenStreetMap Nominatim
- **Dessin de zones** : polygones pour définir des secteurs (Leaflet Draw)

### 2.2.8 Administration et configuration

- **Gestion des utilisateurs** : CRUD complet, activation/suspension, attribution de rôles
- **Gestion des catégories** : hiérarchie (niveaux), icônes, couleurs, mots-clés IA, secteurs responsables
- **Gestion des priorités** : 5 niveaux (CRITICAL -> INFO), SLA, délais d'escalade, couleurs
- **Gestion des secteurs** : 9 types (Eau, Routes, Déchets, Éclairage, Espaces Verts, Bâtiments, Sécurité, Environnement, Administration), horaires, capacités
- **Logs d'audit** : traçabilité complète de toutes les actions (qui, quoi, quand, adresse IP)
- **Santé système** : statut des services, métriques de performance, uptime

## 2.3 Analyse des besoins non fonctionnels

### 2.3.1 Performance et temps de réponse

- Temps de réponse API < 150 ms pour 95 % des requêtes (objectif mesuré : < 150 ms)
- Pipeline IA : classification en moins de 200 ms par signalement
- Charge supportée : 1 000 utilisateurs simultanés
- Cache Redis pour les données fréquemment accédées (LRU avec TTL configurable)
- Pagination systématique des listes (20-100 éléments par page)
- Connexion pool PostgreSQL : minimum 5, maximum 20 connexions

### 2.3.2 Sécurité

- **Authentification JWT dual-token** : access token (30 min) + refresh token (7 jours) avec rotation
- **Hachage des mots de passe** : bcrypt via passlib (12 rounds)
- **RBAC** : contrôle d'accès basé sur les rôles avec décorateurs et dépendances FastAPI
- **Protection CORS** : origines autorisées configurées dans les settings
- **Rate limiting** : 60 requêtes/minute par utilisateur (100 en burst) via Redis
- **Validation des entrées** : Pydantic v2 avec règles strictes (regex, longueur, plages numériques)
- **Protection CSRF** : via middleware TrustedHost
- **Logs de sécurité** : structurés avec structlog en format JSON

### 2.3.3 Scalabilité et disponibilité

- Architecture sans état (stateless) permettant le scale horizontal
- Conteneurisation Docker pour l'isolation et le déploiement reproductible
- Base de données PostgreSQL 15 avec connexion pool asynchrone (asyncpg)
- Cache Redis 7 pour sessions et rate limiting
- Workers Uvicorn : 4 workers en production
- Health checks sur tous les services avec restart policy
- Backup automatique de la base de données (script cron)

### 2.3.4 Maintenabilité et testabilité

- **Architecture en couches** : séparation Routes/Services/Repositories/Données
- **Injection de dépendances** : via FastAPI Depends() pour la testabilité
- **Code typé** : Python type hints + Pydantic schemas + TypeScript strict
- **Tests automatisés** : pytest + pytest-asyncio avec couverture > 85 %
- **Documentation API** : auto-générée par Swagger/OpenAPI (accessible via /docs)
- **Logging structuré** : structlog en format JSON avec niveaux configurables
- **Gestion des erreurs** : hiérarchie d'exceptions personnalisée (13 classes) avec codes d'erreur HTTP

## 2.4 Modélisation des acteurs

Le Tableau 3 ci-dessous présente les quatre acteurs identifiés avec leurs rôles et cas d'utilisation principaux.

**[Insérer Tableau 3 : Acteurs du Système]**

| Acteur | Description | Rôle | Cas d'utilisation principaux |
|---|---|---|---|
| Citoyen | Habitant de la ville utilisant la plateforme | CITIZEN | Signaler un problème, suivre ses signalements, donner son feedback, modifier son profil |
| Agent Sectoriel | Employé municipal d'un secteur spécifique | SECTOR | Voir les signalements assignés, mettre à jour le statut, résoudre, ajouter des notes |
| Administrateur | Gestionnaire de la plateforme | ADMIN | Gérer tous les utilisateurs, catégories, priorités, secteurs, notifications, analytics, logs d'audit |
| Système IA | Moteur d'intelligence artificielle | Automatique | Classifier, évaluer priorité, détecter anomalies, prédire tendances, notifier |

## 2.5 Diagramme des cas d'utilisation

Le diagramme de cas d'utilisation, illustré par la Figure 2, présente l'ensemble des fonctionnalités du système organisées par acteur. Comme nous pouvons le constater sur cette figure, quatre acteurs interagissent avec le système à travers 27 cas d'utilisation distincts.

**[Insérer Figure 2 : Diagramme de Cas d'Utilisation Général]**

- **Citoyen** (7 cas) : inscription, connexion, signalement, consultation, suivi, modification profil, feedback
- **Agent sectoriel** (5 cas) : voir signalements assignés, mise à jour statut, notes internes, résolution, demande d'information
- **Administrateur** (10 cas) : gestion utilisateurs, catégories, priorités, secteurs, signalements, notifications, analytics, rapports, audit, escalade
- **Système IA** (5 cas) : classification, priorisation, détection anomalies, prédiction tendances, notification

## 2.6 Spécification détaillée des cas d'utilisation

Parmi les cas d'utilisation les plus importants, nous détaillons les suivants :

**UC-03 : Signaler un problème urbain**
- **Acteur** : Citoyen
- **Précondition** : Citoyen authentifié et connecté
- **Postcondition** : Signalement créé avec statut DRAFT ou SUBMITTED
- **Scénario principal** :
  1. Le citoyen accède au formulaire de signalement depuis la page principale ou la carte interactive
  2. Il saisit le titre (obligatoire, 5-200 caractères) et la description détaillée du problème (obligatoire, 10-1000 caractères)
  3. Il sélectionne la catégorie parmi une liste hiérarchique (le système peut suggérer une catégorie basée sur l'analyse du texte)
  4. Il localise le problème sur la carte interactive Leaflet en cliquant sur le point précis ou en saisissant une adresse (géocodage automatique Nominatim)
  5. Il ajoute des photos (optionnel, maximum 3, format JPG/PNG, taille max 10 Mo chacune)
  6. Il choisit les options : signalement anonyme, autorisation de contact par les agents
  7. Il soumet le signalement
  8. Le système valide les données, déclenche l'analyse IA (classification + priorisation), crée le signalement et notifie le citoyen avec un numéro de référence unique
- **Extensions** :
  - **3a. Soumission anonyme** : si le citoyen coche « anonyme », son identité n'est pas divulguée aux agents
  - **3b. Upload échoué** : si une photo dépasse la taille maximale, un message d'erreur explicite est affiché
  - **3c. Géolocalisation automatique** : si le navigateur le permet, la position GPS est capturée automatiquement via l'API Geolocation
  - **3d. Catégorie suggérée** : l'IA analyse le texte en temps réel et propose une catégorie avec son niveau de confiance

**UC-05 : Suivre l'état d'un signalement**
- **Acteur** : Citoyen
- **Précondition** : Citoyen authentifié, signalement existant
- **Postcondition** : Le citoyen visualise l'état actuel et l'historique complet
- **Scénario principal** :
  1. Le citoyen accède à la liste de ses signalements
  2. Il sélectionne un signalement spécifique
  3. Le système affiche les détails : titre, description, catégorie, priorité, localisation sur mini-carte
  4. Le système affiche la barre de progression du workflow avec l'étape active mise en évidence
  5. Le citoyen consulte la timeline chronologique des événements
  6. Si le statut est RESOLVED, le citoyen peut donner son feedback (notation 1-5 étoiles + commentaire)

**UC-11 : Résoudre un signalement**
- **Acteur** : Agent Sectoriel
- **Précondition** : Signalement assigné à l'agent, statut IN_PROGRESS
- **Postcondition** : Signalement marqué RESOLVED, citoyen notifié
- **Scénario principal** :
  1. L'agent sélectionne un signalement dans sa liste d'assignations
  2. Il consulte les détails du problème, les photos du citoyen et les notes internes
  3. Il effectue l'intervention sur le terrain
  4. De retour sur la plateforme, il décrit la résolution effectuée
  5. Il ajoute des photos de résolution (preuve de l'intervention)
  6. Il indique le coût de l'intervention (optionnel)
  7. Il soumet la résolution
  8. Le système change le statut en RESOLVED, enregistre le timestamp de résolution et notifie le citoyen

**UC-21 : Envoyer des notifications**
- **Acteur** : Administrateur
- **Précondition** : Administrateur authentifié
- **Postcondition** : Notification créée et envoyée
- **Scénario principal** :
  1. L'administrateur choisit le type d'envoi : individuel ou groupé
  2. Il sélectionne le(s) destinataire(s) via le sélecteur d'utilisateurs ou le type de groupe
  3. Il choisit le canal de diffusion : Email, SMS, WhatsApp ou Push
  4. Il saisit le titre et le message, ou sélectionne un template pré-défini avec variables dynamiques
  5. Il définit la priorité du message : Basse, Normale, Haute ou Critique
  6. Il clique sur « Envoyer »
  7. Le système crée la notification (statut PENDING), tente la livraison via le canal choisi, met à jour le statut (SENT/DELIVERED/FAILED) et affiche le résultat à l'administrateur
- **Extensions** :
  - **21a. Échec de livraison** : le système tente un retry automatique jusqu'à 3 fois avec backoff exponentiel, puis marque la notification comme FAILED
  - **21b. Destinataire sans contact** : le système auto-popule depuis la base de données, ou signale l'absence et ignore cet utilisateur

## 2.7 Conclusion du chapitre

Ce chapitre a présenté une analyse exhaustive des besoins fonctionnels et non fonctionnels du système Urbain Sustainability. Nous avons identifié 8 grandes catégories de fonctionnalités, 4 acteurs principaux (Tableau 3) et 27 cas d'utilisation (Figure 2). Les contraintes de performance, sécurité, scalabilité et maintenabilité ont été spécifiées avec des objectifs mesurables. Le chapitre suivant détaille la conception architecturale répondant à ces besoins.
---

# CHAPITRE 3 : CONCEPTION ARCHITECTURALE

## 3.1 Introduction

Ce chapitre présente la conception détaillée du système Urbain Sustainability. Nous décrivons l'architecture globale en couches, les patrons architecturaux avancés mobilisés (Repository, Service Layer, Dependency Injection), la hiérarchie des exceptions personnalisées, l'architecture événementielle du système de notifications, le modèle de données complet, la conception des services métier, les diagrammes de séquence pour les flux critiques, et la machine à états du signalement. La Figure 1, présentée au chapitre 1, offre une vue d'ensemble de cette architecture.

## 3.2 Architecture globale du système

### 3.2.1 Architecture en couches (Clean Architecture)

L'architecture du système suit les principes de la Clean Architecture (Robert C. Martin, 2017) avec une séparation stricte des préoccupations en quatre couches distinctes :

1. **Couche API (Routes)** : gère les requêtes HTTP, la validation des entrées (Pydantic v2), la sérialisation des réponses et la documentation OpenAPI. 16 modules routeurs.
2. **Couche Service** : contient la logique métier, les validations, les orchestrations et l'intégration avec les services externes. 19 classes de service.
3. **Couche Repository** : abstraction de l'accès aux données avec pattern Repository générique. Implémente les opérations CRUD de base et les requêtes spécifiques. 8 repositories.
4. **Couche Données (Modèles)** : définit la structure des données avec SQLAlchemy ORM 2.0, les relations, les contraintes et les indexes.

Les dépendances pointent de l'extérieur vers l'intérieur : les routes dépendent des services, qui dépendent des repositories, qui dépendent des modèles. Aucune couche intérieure ne connaît l'existence des couches extérieures. Cette règle stricte, appelée « Dependency Rule » par Martin, garantit que les décisions techniques (framework HTTP, ORM, base de données) peuvent être modifiées sans impacter la logique métier centrale.

### 3.2.2 Architecture de déploiement

L'architecture de déploiement est illustrée par la Figure 6. Comme le montre cette figure, cinq composants interagissent dans une topologie en étoile :

**[Insérer Figure 6 : Diagramme de Déploiement - Architecture Physique]**

1. **Navigateur utilisateur** : client web React SPA, accès via HTTPS, rendu des composants et gestion d'état côté client
2. **Docker Host** : hébergeant 3 conteneurs - Frontend Nginx (serveur statique), Backend Uvicorn (4 workers asynchrones), Celery Worker (tâches différées)
3. **PostgreSQL 15** : base de données relationnelle principale avec connexion pool asyncpg
4. **Redis 7** : cache LRU, sessions, file d'attente, Celery broker, rate limiting counters
5. **SMTP Gmail** : serveur de messagerie pour les notifications email avec STARTTLS

Les services sont orchestrés via Docker Compose avec health checks, restart policy (unless-stopped) et volumes persistants pour les données et les uploads.

## 3.3 Patrons architecturaux avancés

### 3.3.1 Repository Pattern

Le Repository Pattern est un patron de conception qui fait office de médiateur entre la couche de domaine et la couche de persistance. Dans notre système, chaque entité dispose d'un repository dédié qui encapsule les opérations d'accès aux données. Le repository générique BaseRepository<T> fournit les opérations CRUD de base :

`python
class BaseRepository(Generic[ModelT]):
    def __init__(self, db: AsyncSession): ...
    async def get(self, id: int) -> ModelT | None: ...
    async def get_multi(self, skip: int = 0, limit: int = 20) -> list[ModelT]: ...
    async def create(self, obj_in: CreateSchemaType) -> ModelT: ...
    async def update(self, obj: ModelT) -> ModelT: ...
    async def delete(self, id: int) -> None: ...
    async def exists(self, **kwargs) -> bool: ...
`

Ce patron présente plusieurs avantages décisifs :
- **Abstraction de la persistance** : la couche service manipule des objets métier sans connaître les détails d'implémentation SQL ou ORM
- **Testabilité** : les repositories peuvent être mockés facilement pour les tests unitaires des services
- **Réutilisabilité** : les opérations CRUD communes sont factorisées dans le repository générique
- **Requêtes optimisées** : chaque repository spécialisé peut implémenter des méthodes de requête optimisées avec selectinload/joinedload

### 3.3.2 Service Layer Pattern

Le Service Layer Pattern centralise la logique métier complexe dans une couche dédiée, séparée à la fois des préoccupations techniques (routes HTTP) et de l'accès aux données (repositories). Nos 19 services métier héritent de BaseService qui fournit les fonctionnalités transverses :

`python
class BaseService:
    def __init__(self, db: AsyncSession): ...
    async def _log_audit(self, action: str, entity: str, entity_id: int, user_id: int, details: dict): ...
    async def _validate_permissions(self, user: User, required_role: UserRole): ...
`

Le service orchestre les appels entre repositories, intègre les validations métier, et gère les transactions. Par exemple, NotificationService.send_notification() orchestre :
1. La validation du type et du canal
2. L'auto-population des coordonnées du destinataire
3. La création de l'enregistrement en base (NotificationRepository)
4. Le dispatch vers le sous-service spécialisé (EmailService, SmsService...)
5. La mise à jour du statut et le logging

### 3.3.3 Dependency Injection

L'injection de dépendances (DI) est le mécanisme qui lie les couches entre elles tout en maintenant un couplage faible. FastAPI offre un système de DI natif via le paramètre Depends() qui permet d'injecter automatiquement les dépendances d'une route ou d'un service.

Dans notre système, la chaîne d'injection est la suivante :

`
Route -> Depends(get_db) -> Session DB
Route -> Depends(get_current_user) -> User authentifié
Service(db) -> Repository(db)
Service(db) -> EmailService(smtp_config)
Service(db) -> AIService(model_path)
`

Cette approche présente plusieurs bénéfices :
- **Testabilité** : chaque dépendance peut être substituée par un mock en environnement de test
- **Flexibilité** : les configurations (SMTP, modèle IA, cache) sont injectées au démarrage
- **Séparation des préoccupations** : les services ne créent pas leurs dépendances, ils les reçoivent

## 3.4 Hiérarchie des exceptions et gestion d'erreurs

Nous avons conçu une hiérarchie d'exceptions personnalisées qui couvre l'ensemble des cas d'erreur métier et technique. Cette hiérarchie est présentée dans le Tableau 5.

**[Insérer Tableau 5 : Hiérarchie des exceptions personnalisées]**

| Classe d'exception | Hérite de | Code HTTP | Usage |
|---|---|---|---|
| UrbainException | Exception | 500 | Classe de base de toutes les exceptions du système |
| NotFoundError | UrbainException | 404 | Ressource non trouvée (utilisateur, signalement, etc.) |
| ValidationError | UrbainException | 422 | Données d'entrée invalides au niveau métier |
| AuthenticationError | UrbainException | 401 | Échec d'authentification (token invalide, expiré) |
| AuthorizationError | UrbainException | 403 | Permission insuffisante pour l'action demandée |
| BusinessLogicError | UrbainException | 409 | Violation de règle métier (transition d'état invalide, conflit) |
| ConflictError | UrbainException | 409 | Conflit de données (email déjà utilisé, référence en double) |
| RateLimitError | UrbainException | 429 | Dépassement de la limite de requêtes |
| ServiceUnavailableError | UrbainException | 503 | Service externe indisponible (SMTP, FCM, API SMS) |
| IntegrationError | UrbainException | 502 | Erreur d'intégration avec un service externe |
| DatabaseError | UrbainException | 500 | Erreur de base de données (contrainte, connexion) |
| AIServiceError | UrbainException | 500 | Erreur du pipeline IA (modèle non chargé, prédiction échouée) |
| NotificationError | UrbainException | 500 | Erreur d'envoi de notification (tous canaux échoués) |

Chaque exception encapsule un message d'erreur lisible, un code d'erreur interne, et les métadonnées associées. Un gestionnaire global (ExceptionHandlerMiddleware) intercepte toutes les exceptions non rattrapées et retourne une réponse JSON structurée.

## 3.5 Architecture événementielle et notifications

Le système de notification adopte une architecture événementielle asynchrone qui découple la création des notifications de leur livraison, améliorant ainsi la résilience et la scalabilité du système. La Figure 11 illustre cette architecture.

**[Insérer Figure 11 : Architecture événementielle du système de notification]**

Le flux événementiel se décompose en quatre phases distinctes :

1. **Émission d'événement** : lorsqu'un signalement est créé, mis à jour ou résolu, la couche service émet un événement métier (ex: SignalCreatedEvent, SignalResolvedEvent) via un bus d'événements interne (EventBus). L'émetteur n'a pas connaissance des consommateurs - il publie simplement l'événement sur le bus.

2. **Orchestration** : l'EventBus distribue l'événement à tous les écouteurs enregistrés. Le NotificationOrchestrator écoute les événements métier et décide quelles notifications doivent être créées en fonction du type d'événement et des préférences de l'utilisateur.

3. **File d'attente asynchrone** : la notification est placée dans une file d'attente Redis (via Celery) pour un traitement différé. Cela permet de ne pas bloquer la requête HTTP principale pendant l'envoi de la notification, qui peut prendre plusieurs secondes.

4. **Livraison et suivi** : le worker Celery récupère la notification, tente la livraison via le canal approprié, met à jour le statut, et enregistre les logs. En cas d'échec, le mécanisme de retry exponentiel est déclenché.

Cette architecture présente plusieurs avantages fondamentaux :
- **Découplage temporel** : la création de la notification et sa livraison sont des opérations disjointes dans le temps
- **Résilience** : si le service SMTP est temporairement indisponible, la notification reste dans la file d'attente
- **Scalabilité** : on peut ajouter des workers Celery pour traiter plus de notifications en parallèle
- **Traçabilité** : chaque événement est logué, permettant un audit complet du système
## 3.6 Conception des données

### 3.6.1 Modèle conceptuel des données

Le diagramme de classes UML, illustré par la Figure 3, présente les 9 entités du système et leurs relations. Comme nous pouvons l'observer sur cette figure, cinq entités principales (User, Signal, Category, Priority, Sector) sont reliées à quatre entités de support (Notification, Report, AuditLog, PasswordResetToken).

**[Insérer Figure 3 : Diagramme de Classes UML]**

### 3.6.2 Schéma relationnel

Le schéma relationnel détaillé, présenté dans la Figure 9, explicite les 9 tables avec leurs colonnes, types PostgreSQL, clés primaires/étrangères, contraintes et index. La figure montre notamment les 18 types ENUM PostgreSQL utilisés.

**[Insérer Figure 9 : Schéma de la Base de Données Relationnelle]**

### 3.6.3 Description des entités et associations

**User** : stocke les informations des utilisateurs (email, username, password hashé bcrypt, nom, prénom, téléphone, rôle UserRole, statut UserStatus, préférences de notification JSON, secteur d'affectation). Relations : 1:N avec Signal, 1:N avec Notification, 1:N avec AuditLog, N:1 avec Sector.

**Signal** : entité centrale stockant les signalements (titre, description, coordonnées GPS avec contraintes de plage, statut SignalStatus, catégorie, priorité, sources, URLs médias JSON, scores IA JSON, timestamps). Relations : N:1 avec User (créateur et processeur), N:1 avec Category, N:1 avec Priority, 1:N avec Notification, 1:N avec Report. Colonnes ajoutées : is_deleted (BOOLEAN) et deleted_at (TIMESTAMPTZ) pour le soft delete avec index.

**Category** : catégories de problèmes avec hiérarchie parent-enfant (type CategoryType, icône, couleur hex, mots-clés IA JSON, secteurs responsables JSON). Relation : 1:N avec Signal.

**Priority** : niveaux de priorité avec configuration SLA (temps réponse, résolution, escalade en heures, poids IA pour le scoring). Relation : 1:N avec Signal.

**Sector** : secteurs municipaux avec type SectorType, horaires JSON, capacités JSON, catégories supportées JSON. Relation : 1:N avec User.

**Notification** : notifications envoyées (type NotificationType, canal Channel, priorité NotificationPriority, statut NotificationStatus, destinataire, contenu avec template, suivi livraison JSON, retry logs JSON). Relations : N:1 avec User, N:1 avec Signal.

**Report** : rapports générés avec statistiques JSON et données d'analyse agrégées.

**AuditLog** : journal d'audit traçant toutes les actions (action, entité, entité_id, modifications JSON, adresse IP, user_agent).

**PasswordResetToken** : tokens de réinitialisation de mot de passe avec expiration TIMESTAMPTZ.

### 3.6.4 Dictionnaire des données

Le Tableau 4 ci-dessous présente un extrait du dictionnaire des données complet.

**[Insérer Tableau 4 : Dictionnaire des Données]**

| Table | Colonne | Type | Contrainte | Description |
|---|---|---|---|---|
| users | id | SERIAL | PK | Identifiant unique auto-incrémenté |
| users | email | VARCHAR(255) | UNIQUE, NOT NULL | Adresse email de l'utilisateur |
| users | username | VARCHAR(100) | UNIQUE, NOT NULL | Nom d'utilisateur pour la connexion |
| users | hashed_password | VARCHAR(255) | NOT NULL | Mot de passe hashé (bcrypt, $) |
| users | first_name | VARCHAR(100) | NOT NULL | Prénom |
| users | last_name | VARCHAR(100) | NOT NULL | Nom de famille |
| users | role | ENUM | NOT NULL | CITIZEN, ADMIN, SECTOR |
| users | status | ENUM | NOT NULL | ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION |
| signals | id | SERIAL | PK | Identifiant unique auto-incrémenté |
| signals | title | VARCHAR(200) | NOT NULL | Titre court du signalement |
| signals | description | TEXT | NOT NULL | Description détaillée du problème |
| signals | latitude | FLOAT | NOT NULL, CHECK(-90,90) | Latitude GPS du problème |
| signals | longitude | FLOAT | NOT NULL, CHECK(-180,180) | Longitude GPS du problème |
| signals | status | ENUM | NOT NULL | DRAFT à CLOSED (9 états) |
| signals | ai_confidence_score | FLOAT | NULL | Score de confiance IA (0-1) |
| categories | id | SERIAL | PK | Identifiant unique |
| categories | name | VARCHAR(100) | NOT NULL | Nom lisible de la catégorie |
| categories | category_type | ENUM | NOT NULL | INFRASTRUCTURE, ENVIRONMENT, etc. |
| priorities | id | SERIAL | PK | Identifiant unique |
| priorities | priority_level | ENUM | NOT NULL | CRITICAL(1), HIGH(2), MEDIUM(3), LOW(4), INFO(5) |
| sectors | id | SERIAL | PK | Identifiant unique |
| sectors | sector_type | ENUM | NOT NULL | WATER, ROADS, WASTE, LIGHTING, etc. |
| notifications | id | SERIAL | PK | Identifiant unique |
| notifications | channel | ENUM | NOT NULL | EMAIL, SMS, WHATSAPP, PUSH, IN_APP, WEBHOOK |
| notifications | status | ENUM | NOT NULL | PENDING, SENT, DELIVERED, READ, FAILED, CANCELLED |

## 3.7 Conception des services

### 3.7.1 Service d'authentification (JWT dual-token)

Le service d'authentification implémente une stratégie JWT dual-token dont le flux complet est illustré par la Figure 13. Comme le détaille cette figure, le flux d'authentification comprend six opérations distinctes.

**[Insérer Figure 13 : Flux d'authentification JWT Dual-Token]**

- **Access token** : durée de vie de 30 minutes, signé avec HS256 (HMAC-SHA256), payload contenant sub (user_id), 	ype, ole, exp, iat.
- **Refresh token** : durée de vie de 7 jours, utilisé pour obtenir un nouvel access token sans reconnexion.
- **Hachage des mots de passe** : bcrypt via passlib avec 12 rounds de salage, stocké au format $2b$....
- **Rôles** : trois rôles avec permissions granulaires via décorateurs et dépendances FastAPI.

Les six endpoints d'authentification sont : register, login, refresh, forgot-password, reset-password, verify-email.

### 3.7.2 Service de notification (multi-canaux)

Le service de notification est le cœur du système de communication. Son architecture est détaillée dans la Figure 10, que nous présentons ci-dessous. Cette figure montre l'organisation en étoile avec un service central et quatre sous-services spécialisés.

**[Insérer Figure 10 : Architecture du Système de Notification Multicanal]**

- **4 canaux** : Email (SMTP Gmail), SMS (email-to-SMS gateway/TextBelt), WhatsApp (pywhatkit), Push (FCM)
- **Architecture** : NotificationService central avec sous-services spécialisés implémentant une interface commune NotificationChannel
- **Templates** : 4 templates HTML Jinja2 responsives
- **Retry logic** : backoff exponentiel (5 min * 3^n), max 3 tentatives, circuit breaker après 3 échecs
- **Bulk sending** : envoi groupé avec lotissement par 50 destinataires
- **Fallback** : dégradation gracieuse vers le logging console

### 3.7.3 Service IA (pipeline ML)

Le service IA implémente un pipeline complet en 6 étapes, illustré par la Figure 7.

**Étape 1 - Classification automatique** : vectorisation TF-IDF (n-grams 1-3, max_features=5000), régression logistique (régularisation L2, C=1.0). Seuil de confiance à 0,7.

**Étape 2 - Évaluation de priorité** : score composite = sévérité * 0,4 + urgence * 0,35 + impact * 0,25. Mapping : CRITICAL (>= 0,8), HIGH (>= 0,6), MEDIUM (>= 0,4), LOW (>= 0,2), INFO (< 0,2).

**Étape 3 - Détection d'anomalies** : Isolation Forest (contamination=0.1), analyse de patterns suspects.

**Étape 4 - Prédiction de tendances** : décomposition temporelle + régression linéaire sur fenêtre glissante de 90 jours.

**Étape 5 - Génération de rapport** : rapport IA complet avec résumé et recommandations.

**Étape 6 - Traitement par lots** : classification jusqu'à 100 signalements par requête.

### 3.7.4 Service d'analytics

Le service d'analytics agrège les données de 8 repositories différents : dashboard stats, tendances (7/14/30/90 jours), hotspots DBSCAN (eps=0.01, min_samples=5), performance des secteurs, analytics prédictifs, rapports structurés exportables en PDF/Excel/JSON.

### 3.7.5 Service de signalement (workflow états)

Gère le cycle de vie complet avec validation des transitions d'état, génération de référence unique (SIG-AAAAMM-XXXXXX), assignation automatique, escalade SLA, soft delete, et notifications automatiques via le bus d'événements.

## 3.8 Conception détaillée - Diagrammes de séquence

### 3.8.1 Envoi de notification

Le diagramme de séquence de la Figure 4 illustre le processus complet d'envoi d'une notification en trois phases. Comme le montre cette figure, les phases sont séquentielles :

**[Insérer Figure 4 : Diagramme de Séquence - Envoi d'une Notification]**

**Phase 1 - Création** : l'administrateur soumet le formulaire -> le backend valide (Pydantic) -> NotificationService crée l'enregistrement (status=PENDING).

**Phase 2 - Envoi** : rendu du template Jinja2 -> dispatch vers le canal approprié -> service externe tente la livraison.

**Phase 3 - Suivi** : mise à jour du statut (SENT/DELIVERED/FAILED) -> enregistrement des logs -> retour au frontend.

### 3.8.2 Création et traitement d'un signalement

1. Le citoyen soumet le formulaire
2. Validation Pydantic
3. Création du signalement (statut DRAFT)
4. Pipeline IA : classification, priorisation, anomalies
5. Mise à jour avec scores IA
6. Émission de SignalCreatedEvent via le bus d'événements
7. L'orchestrateur crée et envoie une notification
8. Assignation au secteur compétent

### 3.8.3 Pipeline IA

Le pipeline IA, illustré par la Figure 7, comprend 6 étapes séquentielles.

**[Insérer Figure 7 : Pipeline IA - Classification, Priorisation et Prédiction]**

1. Prétraitement du texte (lowercasing, stopwords, stemming)
2. Extraction TF-IDF (n-grams 1-3, max_features=5000)
3. Classification Logistic Regression (5 classes, accuracy 85 %)
4. Moteur de score de priorité (formule pondérée)
5. Détection d'anomalies (Isolation Forest)
6. Prédiction de tendances (décomposition temporelle + régression linéaire)

## 3.9 Machine à états du signalement

Le diagramme d'états de la Figure 5 présente le cycle de vie complet d'un signalement avec 9 états. Comme l'illustre cette figure, le workflow comporte trois états terminaux :

**[Insérer Figure 5 : Diagramme d'États - Cycle de Vie d'un Signalement]**

- **DRAFT** : état initial, brouillon modifiable par le citoyen
- **SUBMITTED** : soumis, en attente d'examen
- **UNDER_REVIEW** : en cours d'examen par l'administrateur
- **ASSIGNED** : assigné à un agent sectoriel
- **IN_PROGRESS** : en cours de traitement
- **RESOLVED** : résolu, en attente de feedback
- **CLOSED** : fermé (état terminal)
- **CANCELLED** : annulé par le citoyen (état terminal)
- **REJECTED** : rejeté par l'administrateur (état terminal)

Les transitions avec garde (SLA dépassé, 7 jours sans feedback) déclenchent des actions automatiques.

## 3.10 Conclusion du chapitre

Dans ce chapitre, nous avons présenté la conception architecturale complète du système. L'architecture en couches avec Clean Architecture et les patrons Repository, Service Layer et Dependency Injection (section 3.3) assure la maintenabilité et la testabilité. La hiérarchie des 13 exceptions personnalisées (Tableau 5) garantit une gestion d'erreurs cohérente. L'architecture événementielle des notifications (Figure 11) apporte résilience et scalabilité. Le modèle de données avec 9 tables et 18 types ENUM PostgreSQL (Tableau 4) couvre l'ensemble des besoins. Le chapitre suivant présente l'implémentation concrète de cette conception.

---

# CHAPITRE 4 : IMPLÉMENTATION ET RÉALISATION

## 4.1 Introduction

Ce chapitre présente la réalisation concrète du système Urbain Sustainability. Nous décrivons l'environnement de développement (Tableau 6), la structure du projet, l'implémentation du backend avec un focus sur les mécanismes avancés - gestion des sessions asynchrones SQLAlchemy 2.0, stratégie de cache LRU avec TTL, algorithme de rate limiting - ainsi que le frontend React et le système de notifications. Des captures d'écran (Figure 14) illustrent les interfaces principales.

## 4.2 Environnement de développement

### 4.2.1 Environnement matériel

Le développement a été réalisé sur une machine Intel Core i7 12e génération (14 cœurs, 20 threads), 32 Go de RAM DDR5, 512 Go SSD NVMe, sous Windows 11 avec WSL2 (Ubuntu 22.04) et Docker Desktop 4.30.

### 4.2.2 Environnement logiciel

Le Tableau 6 ci-dessous présente l'environnement logiciel.

**[Insérer Tableau 6 : Environnement de Développement]**

| Outil | Version | Usage |
|---|---|---|
| Python | 3.11.9 | Runtime backend |
| Node.js | 20.15 | Runtime frontend |
| PostgreSQL | 15.4 | Base de données relationnelle |
| Redis | 7.2.5 | Cache LRU et file d'attente Celery |
| Docker | 27.0 | Conteneurisation |
| Docker Compose | 2.28 | Orchestration multi-conteneurs |
| Git | 2.45 | Gestion de versions |
| VS Code | 1.89 | Éditeur principal |
| PyCharm | 2024.1 | IDE Python (débogage, profiling) |
| Postman | 11.0 | Test API |
| DBeaver | 23.3 | Administration base de données |

### 4.2.3 Stack technologique

La stack technologique complète est présentée dans le Tableau 1.

**[Insérer Tableau 1 : Stack Technologique]**

| Couche | Technologie | Version | Justification |
|---|---|---|---|
| Backend Runtime | Python | 3.11.9 | Maturité IA/ML, écosystème riche |
| Framework web | FastAPI | 0.104 | Performance ASGI, documentation auto |
| ORM | SQLAlchemy | 2.0 (async) | ORM mature, support async natif |
| Base de données | PostgreSQL | 15.4 | Types ENUM, JSONB, indexation |
| Cache / Queue | Redis | 7.2.5 | LRU avec TTL, pub/sub, files d'attente |
| Frontend | React | 19 | Composants, hooks, Suspense |
| Typage frontend | TypeScript | 6.0 | Typage statique strict |
| Bundler | Vite | 5.3 | HMR instantané, build optimisé |
| CSS | Tailwind CSS | 3.4 | Utility-first, purge CSS |
| Cartographie | Leaflet | 1.9 | Open source, léger, plugins |
| IA/ML | scikit-learn | 1.3 | TF-IDF, Logistic Regression |
| Conteneurisation | Docker | 27.0 | Isolation, reproductibilité |
| Orchestration | Docker Compose | 2.28 | Multi-services, health checks |
## 4.5 Gestion avancee des sessions asynchrones SQLAlchemy
## 4.5 Gestion avancee des sessions asynchrones SQLAlchemy

### 4.5.1 Configuration de la session asynchrone

La session asynchrone est configuree dans core/database.py avec async_sessionmaker :

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
    pool_recycle=3600
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Le parametre expire_on_commit=False est crucial : il empeche l expiration des objets apres commit, evitants les erreurs DetachedInstanceError hors contexte de session.

### 4.5.2 Injection de session via dependance FastAPI

La session est injectee via get_db(), garantissant une session unique par requete :

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

### 4.5.3 Gestion des relations et chargement eager

Nous utilisons systematiquement :
- selectinload() : pour les relations plusieurs-a-un, emet une requete IN separee
- joinedload() : pour les relations un-a-un avec jointure SQL
- contains_eager() : lorsque la jointure est deja effectuee

### 4.5.4 Serialisation explicite avant fermeture

Pour eviter les erreurs MissingGreenlet, nous serialisons les objets ORM en dictionnaires Pydantic pendant que la session est active.

## 4.6 Mecanismes de cache et d optimisation

### 4.6.1 Strategie de cache LRU avec TTL

Cache implemente via CacheService dans core/cache.py avec Redis :

Donnees mises en cache :

| Donnee | Cle Redis | TTL |
|---|---|---|
| Statistiques dashboard | cache:dashboard:{period} | 5 min |
| Liste des categories | cache:categories | 1 h |
| Liste des priorites | cache:priorities | 1 h |
| Tendances analytics | cache:trends:{period} | 15 min |
| Hotspots geographiques | cache:hotspots:{period} | 15 min |

La methode get_or_set() implemente le pattern cache-aside.

### 4.6.2 Indexation base de donnees

Index sur : signals(status), signals(created_at DESC), signals(latitude, longitude), signals(category_id), signals(priority_id), notifications(status), notifications(user_id), audit_logs(entity, entity_id), users(email), users(role).

### 4.6.3 Optimisation des requetes N+1

Resolue par utilisation systematique de selectinload(), joinedload() et subqueryload(), avec pagination (20 elements par defaut, max 100).

## 4.7 Algorithme de Rate Limiting

Le rate limiting utilise l algorithme Sliding Window Counter avec Redis.

### 4.7.1 Principe

Taux = (compteur_fenetre_precedente * poids) + compteur_fenetre_actuelle

### 4.7.2 Implementation Redis

Utilisation de ZREMRANGEBYSCORE et ZADD de Redis, avec comptage des entrees dans la fenetre glissante et TTL automatique.

### 4.7.3 Configuration

- Limite : 60 requetes/minute par utilisateur
- Burst : 100 requetes en pic
- Reponse 429 avec en-tetes X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, Retry-After

## 4.8 Frontend : Interface utilisateur

### 4.8.1 Architecture des composants React

Le frontend React 19 est structure autour d une architecture modulaire :

Couche API (src/api/) : client Axios avec intercepteurs JWT, refresh automatique des tokens, 35+ fonctions endpoints typees.

Couche Composants (src/components/) : composants atomiques (LoadingSpinner, Gauge, StatCard, DataTable, Modal, Toast) et structurels (Sidebar, AdminLayout, Navbar).

Couche Contexte (src/contexts/) : AuthContext (authentification globale), ToastContext (notifications toast), TabContext (onglets admin).

Couche Pages (src/pages/) : admin/18 pages, signals/11 pages, auth/5 pages, profile/, reports/, map/.

Gestion d etat : TanStack Query avec staleTime de 30s (donnees frequentes) a 5min (donnees statiques), mutations optimistes.

### 4.8.2 Dashboard administrateur

Le tableau de bord administrateur (Figure 8) comprend :
- Barre laterale : navigation avec 11 sections
- KPIs : 4 cartes (Total, Nouveaux aujourd hui, Resolus, Temps moyen)
- Graphique tendances : courbe 30 jours avec Recharts
- Diagramme circulaire : repartition par priorite
- Tableau performance : 7 secteurs avec taux resolution, temps moyen, satisfaction
- Notifications recentes : liste des 5 dernieres

[Inserer Figure 8 : Tableau de Bord Administrateur]

### 4.8.3 Carte interactive avec Leaflet

La carte interactive offre :
- Marqueurs clusterises (MarkerCluster, distance 50px)
- Heatmap (Leaflet.heat, radius 25, blur 15)
- Filtres par statut, categorie, priorite, date
- Popup avec informations synthetiques au clic
- Geocodage OpenStreetMap Nominatim (debounce 500ms)
- Geolocalisation automatique via API Geolocation

## 4.9 Systeme de notification

Le systeme de notification, presente dans la Figure 10, est le composant le plus complexe du projet.

### 4.9.1 Service Email (EmailService)

- Transport SMTP : smtp.gmail.com:587, STARTTLS, AUTH PLAIN, timeout 30s
- Degradation gracieuse : logging console si credentials absents
- 4 templates HTML Jinja2 responsives
- Envoi groupe : lotissement par 50 destinataires, pause 1s entre lots

### 4.9.2 Service SMS (SmsService)

- Provider principal : email-to-SMS gateway via SMTP Gmail (gratuit)
- Dictionnaire de 30+ operateurs mondiaux (Orange Tunisie, ATT, T-Mobile, Verizon, Vodafone, Orange France, SFR, etc.)
- Provider secondaire : TextBelt API (1 SMS/jour gratuit)
- Fallback : mock/console logging

### 4.9.3 Service WhatsApp (WhatsAppService)

- Bibliotheque pywhatkit 5.4
- Limitation : session WhatsApp Web active requise
- Fallback : mock/console logging

### 4.9.4 Service Push (PushService)

- Provider FCM via protocole HTTP/2
- Format JSON avec titre, corps, icone, data payload
- Fallback si FCM non configure

### 4.9.5 Mecanisme de retry

Exponential Backoff avec multiplicateur de 3 :
- Tentative 1 : immediate
- Tentative 2 : apres 5 minutes
- Tentative 3 : apres 15 minutes
- Max 3 tentatives, puis circuit breaker
- Chaque tentative enregistree dans delivery_logs (JSON array)

## 4.10 Captures d ecran des interfaces principales

La Figure 14 presente six vues cles de l application. Comme l illustre cette figure, l interface utilisateur couvre l ensemble du parcours citoyen et administrateur :

[Inserer Figure 14 : Captures d Ecran des Principales Interfaces]

1. Connexion/Inscription : page avec formulaire stylise et illustration
2. Creation de signalement : carte Leaflet (60 %) + formulaire (40 %)
3. Detail d un signalement : timeline chronologique, galerie photos, feedback
4. Tableau de bord admin : KPIs, graphiques Recharts, tableau de performance
5. Gestion des notifications : liste paginee, formulaire d envoi, statistiques par canal
6. Carte interactive : clusters, heatmap, filtres lateraux

## 4.11 Conclusion du chapitre

Ce chapitre a presente la realisation concrete du systeme Urbain Sustainability. L implementation couvre 16 modules API backend avec 95+ endpoints, 19 services metier, 8 repositories, un frontend React avec 40+ pages, et un systeme de notification multi-canaux complet. Les mecanismes avances de gestion des sessions asynchrones SQLAlchemy 2.0 (section 4.5), de cache LRU avec TTL (section 4.6) et de rate limiting par Sliding Window Counter (section 4.7) garantissent la performance et la scalabilite du systeme. Le chapitre suivant presente la strategie de test et les resultats de validation.

---

# CHAPITRE 5 : TESTS, VALIDATION ET DÉPLOIEMENT

## 5.1 Introduction

Ce chapitre presente la strategie de test adoptee pour valider le systeme Urbain Sustainability, les resultats detailles obtenus (Tableau 7), les benchmarks de performance (Tableau 8), le pipeline CI/CD (Tableau 9), et la procedure de deploiement avec Docker. Nous discutons egalement des difficultes rencontrees et des solutions apportees.

## 5.2 Strategie de test

La strategie de test suit le modele de la pyramide de test (Michael Cohn, 2009) avec trois niveaux.

### 5.2.1 Tests unitaires

- Services metier : chaque methode testee avec mocks des repositories (pytest-mock)
- Repositories : requetes SQLAlchemy testees avec base PostgreSQL isolee
- Schemas Pydantic : validation des entrees et serialisation testees exhaustivement
- Securite : fonctions JWT et hachage bcrypt testes unitairement

### 5.2.2 Tests d integration

- API endpoints : chaque endpoint via TestClient de FastAPI avec session DB reelle
- Workflow signalement : cycle de vie complet de bout en bout (DRAFT a CLOSED)
- Pipeline IA : classification et priorisation avec textes reels et synthetiques
- Notifications : fichier dedie (test_notification_full.py) avec 35 scenarios

### 5.2.3 Tests de notification (35 scenarios)

1. Creation avec tous les types (10) et canaux (4)
2. Envoi individuel (single_user) avec auto-population
3. Envoi vers email/phone personnalises (custom_email, custom_phone)
4. Envoi groupe (bulk_list) avec validation des limites
5. Envoi a des groupes (all_citizens, all_admins, all_sector_users)
6. Retry de notification echouee avec backoff exponentiel
7. Annulation de notification en attente
8. Gestion des erreurs (utilisateur inexistant, canal invalide)
9. Statistiques de notification par canal et par type
10. Notifications liees aux signalements

## 5.3 Resultats detailles des tests

Le Tableau 7 ci-dessous presente les resultats detailles des tests par module :

[Inserer Tableau 7 : Resultats detailles des tests]

| Suite de tests | Nombre | Reussis | Echoues | Couverture | Temps execution |
|---|---|---|---|---|---|
| Authentification | 8 | 8 | 0 | 100 % | 1,2 s |
| CRUD Utilisateurs | 6 | 6 | 0 | 100 % | 0,8 s |
| CRUD Signalements | 8 | 8 | 0 | 100 % | 1,5 s |
| CRUD Categories | 4 | 4 | 0 | 100 % | 0,4 s |
| CRUD Priorites | 4 | 4 | 0 | 100 % | 0,4 s |
| CRUD Secteurs | 4 | 4 | 0 | 100 % | 0,5 s |
| Notifications (35 scenarios) | 35 | 35 | 0 | 100 % | 4,8 s |
| Pipeline IA | 6 | 6 | 0 | 100 % | 2,1 s |
| Analytics | 4 | 4 | 0 | 100 % | 1,9 s |
| Workflow signalement | 8 | 8 | 0 | 100 % | 1,3 s |
| Total | 87 | 87 | 0 | 100 % | 14,9 s |

Tous les tests passent avec un taux de reussite de 100 % et un temps d execution total de 14,9 secondes. Les scenarios de test notables incluent :
- Envoi a un utilisateur sans email configure : auto-population depuis la base
- Retry d une notification echouee : succes a la 2e tentative
- Annulation d une notification deja envoyee : erreur 422
- Classification d un texte de spam : detection d anomalie avec score > 0,7
- Transition invalide (CLOSED vers IN_PROGRESS) : BusinessLogicError HTTP 409

## 5.4 Performance et benchmarks

Le Tableau 8 presente les benchmarks de performance mesures (Intel Core i7 12e gen, 32 Go RAM, PostgreSQL 15 conteneurise, Redis 7).

[Inserer Tableau 8 : Benchmarks de performance]

| Operation | Sans cache | Avec cache | Amelioration |
|---|---|---|---|
| Dashboard stats (4 KPIs + tendances) | 850 ms | 120 ms | 86 % |
| Liste signalements (20 items, page 1) | 95 ms | 45 ms | 53 % |
| Detail signalement (avec relations) | 65 ms | 35 ms | 46 % |
| Classification IA (TF-IDF + LR) | 180 ms | - | - |
| Creation notification (creation + email) | 1 200 ms | - | - |
| Creation notification (creation + log) | 45 ms | - | - |
| Hotspots DBSCAN (1000 points) | 350 ms | 60 ms | 83 % |
| Prediction tendances (30 jours) | 120 ms | - | - |
| Authentification (login JWT) | 25 ms | - | - |
| Refresh token JWT | 15 ms | - | - |

Les resultats montrent des temps de reponse API inferieurs a 150 ms pour 95 % des requetes (objectif atteint). Le cache Redis apporte des ameliorations de 46 % a 86 % sur les operations les plus couteuses. La classification IA s effectue en 180 ms en moyenne, bien en dessous du seuil de 500 ms fixe dans les besoins non fonctionnels.

## 5.5 Pipeline CI/CD

Le pipeline CI/CD est implemente avec GitHub Actions et comprend les etapes suivantes, detaillees dans le Tableau 9.

[Inserer Tableau 9 : Etapes du pipeline CI/CD]

| Etape | Declencheur | Duree | Actions |
|---|---|---|---|
| 1. Checkout | push sur main / PR | 10 s | Recuperation du code source |
| 2. Setup Python | apres checkout | 30 s | Installation Python 3.11, cache pip |
| 3. Install dependencies | apres setup | 45 s | pip install -r requirements.txt |
| 4. Lint backend | apres install | 20 s | flake8 (style), mypy (typage), black (format) |
| 5. Setup Node.js | parallele au 3 | 20 s | Installation Node.js 20, cache npm |
| 6. Install frontend | apres setup Node | 30 s | npm ci |
| 7. Lint frontend | apres install front | 15 s | eslint, prettier --check |
| 8. Build frontend | apres lint front | 40 s | npm run build (Vite) |
| 9. Tests backend | apres lint back | 60 s | pytest --cov=app tests/ -v |
| 10. Build Docker image | apres tests | 50 s | docker build -t urbain-backend . |
| 11. Push image | apres build (main only) | 30 s | docker push registry/urbain-backend |
| 12. Deploy | apres push (main only) | 40 s | Deploiement automatique sur le serveur |

Le pipeline complet s execute en environ 6 minutes. En cas d echec a une etape, les etapes suivantes sont sautees et une notification est envoyee a l equipe.

## 5.6 Deploiement

### 5.6.1 Docker et conteneurisation

Le systeme est entierement conteneurise avec Docker. Chaque service a son propre Dockerfile :

Backend : base sur python:3.11-slim, expose le port 8000, lance uvicorn avec 4 workers.

Frontend : build Vite, servi via Nginx comme reverse proxy.

### 5.6.2 Configuration Docker Compose (3 services)

services:
  backend:    build ./backend, ports 8000:8000, depends_on [db, redis], restart unless-stopped
  db:         image postgres:15, ports 5433:5432, healthcheck pg_isready, volume postgres_data
  redis:      image redis:7, healthcheck redis-cli ping, restart unless-stopped

## 5.7 Difficultés rencontrées et solutions

### Probleme 1 : ORM et async SQLAlchemy
Difficulte : Sessions asynchrones ne supportant pas le lazy loading hors contexte.
Solution : Chargement eager avec selectinload() et joinedload(), serialisation explicite avant fermeture de session.

### Probleme 2 : Appels asynchrones bloquants
Difficulte : smtplib (synchrone) bloquait la boucle d evenements asynchrone.
Solution : Utilisation de aiosmtplib et delegation des taches lourdes a Celery.

### Probleme 3 : Kubernetes et orchestration
Difficulte : Complexite excessive de Kubernetes pour ce projet.
Solution : Migration vers Docker Compose avec 3 services, health checks et restart policies.

### Probleme 4 : Pipeline IA et modeles pre-entrainés
Difficulte : Modeles Transformers necessitant des ressources GPU indisponibles.
Solution : scikit-learn (TF-IDF + Logistic Regression) pour la classification de base.

### Probleme 5 : Synchronisation des repositories
Difficulte : Incoherences entre noms de methodes dans les routes et les services.
Solution : Revision complete de la couche service et repository, correction de 42 fichiers.

### Probleme 6 : Notifications WhatsApp
Difficulte : pywhatkit necessite une session WhatsApp Web active.
Solution : Fallback vers logging console et documentation des limitations.

### Probleme 7 : Envoi SMS reel
Difficulte : Twilio necessite un compte payant ; TextBelt limite a 1 SMS/jour.
Solution : Passerelle email-to-SMS utilisant le SMTP Gmail gratuit avec mapping de 30+ operateurs.

## 5.8 Conclusion du chapitre

Ce chapitre a presente la strategie de test complete avec 87 tests tous passants (100 %). Les performances mesurees (Tableau 8) demontrent la viabilite de la solution avec des temps de reponse API inferieurs a 150 ms et des ameliorations de 46 a 86 % via le cache Redis. Le pipeline CI/CD (Tableau 9) automatise l integration et le deploiement en environ 6 minutes. Le deploiement Docker Compose avec 3 services assure une disponibilite et une maintenabilite satisfaisantes.

---

# CONCLUSION GÉNÉRALE

## Récapitulation de la démarche

Ce projet de fin d etudes avait pour objectif la conception et le developpement d Urbain Sustainability System, une plateforme intelligente de signalement et de gestion des problemes urbains. Partant du constat que les villes font face a une urbanisation croissante et que les processus de signalement sont souvent manuels, lents et depourvus d intelligence decisionnelle, nous avons propose une solution integree combinant interface citoyenne moderne, intelligence artificielle, notifications multi-canaux et analytics en temps reel.

La demarche adoptee a suivi une methodologie rigoureuse :
1. Analyse de l existant : etude des solutions concurrentes et identification de leurs lacunes (Tableau 2)
2. Specification des besoins : 8 categories fonctionnelles et 4 categories non fonctionnelles
3. Conception architecturale : architecture en couches (Clean Architecture) avec patrons Repository, Service Layer et Dependency Injection
4. Implementation incrementale : developpement par sprints Agile/Scrum sur 4 mois (8 sprints)
5. Validation systematique : 87 tests automatises avec 100 % de reussite

## Contributions

Les contributions specifiques de ce projet sont les suivantes :

1. Architecture en couches avec patrons avances : conception et implementation d une architecture logicielle respectant les principes de Clean Architecture avec les patrons Repository, Service Layer et Dependency Injection (13 exceptions personnalisees, 4 couches strictes, 19 services avec injection de dependances).

2. Pipeline IA embarque : developpement d un pipeline complet de classification NLP (TF-IDF + Regression Logistique, 85 % d accuracy), evaluation de priorite par score composite, detection d anomalies (Isolation Forest) et prediction de tendances par decomposition temporelle.

3. Systeme de notification multi-canaux resilient : conception et implementation d un systeme oriente evenements supportant 4 canaux (Email, SMS, WhatsApp, Push) avec mecanisme de retry exponentiel, circuit breaker, fallback gracieux et file d attente asynchrone Celery.

4. Passerelle SMS innovante gratuite : developpement d un systeme email-to-SMS utilisant le SMTP Gmail et les passerelles operateurs (30+ operateurs internationaux), eliminant le besoin de comptes SMS payants.

5. API REST exhaustive : conception et implementation de 95+ endpoints REST repartis sur 16 modules, avec documentation automatique Swagger/OpenAPI, validation Pydantic v2, et pagination systematique.

6. Mechanismes de performance avances : implementation d un cache LRU avec TTL (Redis), d un algorithme de rate limiting Sliding Window Counter, d une gestion asynchrone optimisee des sessions SQLAlchemy 2.0, et d une indexation strategique de la base de donnees.

7. Interface d administration complete : developpement de 18 pages d administration couvrant la gestion des utilisateurs, categories, priorites, secteurs, notifications, analytics, audit logs et sante systeme, avec RBAC granulaire.

8. Pipeline CI/CD automatise : configuration d un pipeline GitHub Actions en 12 etapes (environ 6 minutes) couvrant le linting, les tests, la construction Docker et le deploiement automatique.

## Resultats

Les resultats obtenus sont les suivants :
- Plateforme complete : 95+ endpoints API REST, 16 modules routeurs, 19 services metier, 8 repositories, 9 modeles ORM avec 18 types ENUM PostgreSQL
- Frontend moderne : 40+ pages React 19, 18 pages d administration, carte interactive Leaflet, graphiques Recharts
- IA integree : pipeline de classification (TF-IDF + Logistic Regression, 85 % accuracy), evaluation de priorite, detection d anomalies, prediction de tendances
- Notifications multi-canaux : Email (SMTP Gmail), SMS (email-to-SMS gateway), WhatsApp (pywhatkit), Push (FCM) avec retry exponentiel et fallback
- Qualite validee : 87 tests automatises (35 dedies aux notifications), 100 % de reussite
- Performance : temps de reponse API < 150 ms, classification IA < 200 ms
- Conteneurisation : Docker Compose avec 3 services, health checks, volumes persistants

## Difficultes rencontrees

Les principales difficultes : gestion des sessions asynchrones SQLAlchemy, integration de bibliotheques synchrones dans un environnement asynchrone, disponibilite limitee des API SMS gratuites (resolue par passerelle email-to-SMS innovante), complexite de l orchestration Kubernetes (redimensionnee vers Docker Compose), incoherences cross-couches dans 42 fichiers (corrigees).

## Apports personnels et competences acquises

- Architecture logicielle : conception en couches, Clean Architecture, injection de dependances, pattern Repository, Service Layer
- Developpement backend : FastAPI, SQLAlchemy 2.0 async, PostgreSQL, JWT dual-token, Pydantic v2, Celery, cache Redis, rate limiting
- Developpement frontend : React 19, TypeScript strict, Tailwind CSS, Leaflet, TanStack Query, Recharts, Vite
- Intelligence artificielle : NLP, TF-IDF, regression logistique, Isolation Forest, prediction de series temporelles
- DevOps : Docker, Docker Compose, CI/CD GitHub Actions, tests automatises (pytest, pytest-asyncio)
- Methodologie : Agile/Scrum (8 sprints), gestion de projet, documentation technique

## Perspectives et ameliorations futures

- Application mobile native : developpement Android (Kotlin) et iOS (Swift) avec notifications push natives
- Integration IoT : connexion avec capteurs urbains (qualite de l air, niveau des eaux, trafic)
- Modeles Transformers avances : fine-tuning de CamemBERT/BERT pour le francais et l arabe
- Chatbot IA : assistant conversationnel pour guider les citoyens
- Analyse d images : detection automatique du type de probleme par vision par ordinateur
- Blockchain : enregistrement immutable des signalements pour la transparence
- Jumeau numerique (Digital Twin) : modelisation 3D de la ville
- Moteur de recommandations : suggestions proactives de maintenance basees sur l analyse predictive

En conclusion, ce projet a permis de demontrer la faisabilite d une plateforme intelligente de gestion urbaine alliant technologies web modernes, intelligence artificielle et notifications multi-canaux. Les resultats obtenus montrent que notre approche repond efficacement aux defis poses par la gestion des signalements urbains. La plateforme Urbain Sustainability System se positionne comme une alternative open source credible aux solutions proprietaires onereuses, tout en offrant des fonctionnalites avancees que n integrent pas les solutions open source existantes. L architecture modulaire et extensible du systeme facilite l ajout de nouvelles fonctionnalites et l adaptation aux besoins specifiques de chaque municipalite.
---

# BIBLIOGRAPHIE

[1] R. C. Martin, *Clean Architecture: A Craftsman''s Guide to Software Structure and Design*. Prentice Hall, 2017.

[2] S. Habib, *FastAPI: Modern Python Web Development*. O''Reilly Media, 2023.

[3] S. Bird, E. Klein, and E. Loper, *Natural Language Processing with Python*. O''Reilly Media, 2009.

[4] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825-2830, 2011.

[5] United Nations, Department of Economic and Social Affairs, *World Urbanization Prospects: The 2018 Revision*. New York: United Nations, 2019.

[6] M. Fowler, *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.

[7] F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," in *Proceedings of the 8th IEEE International Conference on Data Mining (ICDM)*, 2008.

[8] K. Schwaber and M. Beedle, *Agile Software Development with Scrum*. Prentice Hall, 2001.

[9] A. Zanasi, "Smart City: Definitions, Dimensions, and Initiatives," in *Proceedings of the 4th International Conference on Smart Cities and Green ICT Systems (SMARTGREENS)*, 2015.

[10] Institut National de la Statistique (INS), *Population et developpement en Tunisie : indicateurs demographiques 2022*. Tunis, 2023.

[11] Banque Mondiale, *Urban Development Overview*. Washington, DC: World Bank Group, 2023.

[12] International Telecommunication Union (ITU), *Smart City Definition and KPIs*. Geneva: ITU-T, 2020.

[13] McKinsey Global Institute, *Smart Cities: Digital Solutions for a More Livable Future*. McKinsey & Company, 2018.

[14] Organisation de Cooperation et de Developpement Economiques (OCDE), *Gouvernance municipale et transformation numerique*. Paris: OCDE, 2022.

[15] FastAPI Documentation, 2025. https://fastapi.tiangolo.com/

[16] PostgreSQL 15 Documentation, 2025. https://www.postgresql.org/docs/15/

[17] React 19 Documentation, 2025. https://react.dev/

[18] Docker Documentation, 2025. https://docs.docker.com/

[19] Ministere des Affaires Locales et de l''Environnement, *Rapport sur la gestion des reclamations urbaines en Tunisie*. Tunis, 2023.

[20] Mordor Intelligence, *Smart Cities Market - Growth, Trends, and Forecasts (2024-2029)*. Hyderabad, 2024.

---

# ANNEXES

## Annexe A : Code Source - Structure Complete

Voir le depot GitHub pour la structure complete du projet.

## Annexe B : Guide d''Installation

### Pre-requis
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (ou Docker)
- Redis 7+ (ou Docker)
- Git

### Installation rapide avec Docker

```
git clone <url-du-repo>
cd urbain-sustainability
cp backend/.env.example backend/.env
docker-compose up --build
```

### Installation manuelle

```
cd backend
python -m venv venv
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd ../frontend
npm install
npm run dev
```

### Comptes de test

| Role | Email | Mot de passe |
|---|---|---|
| Administrateur | admin@urbain.com | Admin123! |
| Citoyen | citizen@urbain.com | Citizen123! |
| Agent sectoriel | agent@urbain.com | Agent123! |

### Lancer les tests

```
cd backend
pytest -v
pytest tests/test_notification_full.py -v
pytest --cov=app tests/
```

## Annexe C : Manuel d''Utilisation

### Pour les citoyens
1. Creer un compte
2. Signaler un probleme
3. Suivre ses signalements
4. Donner son avis

### Pour les agents sectoriels
1. Consulter les assignations
2. Mettre a jour le statut
3. Resoudre le probleme

### Pour les administrateurs
1. Dashboard
2. Gestion (CRUD)
3. Notifications
4. Analytics
5. Audit

---

*Document redige dans le cadre du Projet de Fin d''Etudes - Urbain Sustainability System - Juillet 2026.*
