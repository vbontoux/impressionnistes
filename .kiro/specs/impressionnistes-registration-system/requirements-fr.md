# Document d'Exigences - Système d'Inscription Course des Impressionnistes

## Introduction

Le Système d'Inscription Course des Impressionnistes est une application web serverless qui permet aux responsables d'équipes de clubs d'aviron d'inscrire des équipages et des bateaux pour la compétition RCPM, tout en fournissant des outils administratifs pour la validation et la gestion. Le système prend en charge les interfaces multilingues, le traitement des paiements et la gestion complète des inscriptions tout au long du cycle de vie de la compétition.

## Glossaire

- **Système_Inscription** : L'application web complète pour gérer les inscriptions aux compétitions d'aviron
- **Responsable_Équipe** : Un utilisateur représentant un club d'aviron qui inscrit des bateaux et des équipages pour la compétition
- **Utilisateur_Admin** : Membre du personnel de l'organisation RCPM qui gère la configuration du système et valide les inscriptions
- **Utilisateur_DevOps** : Personnel technique responsable du déploiement et de la maintenance de l'infrastructure serverless
- **Membre_Équipage** : Un rameur ou barreur individuel inscrit pour participer dans un bateau
- **Inscription_Bateau** : Une entrée d'inscription complète contenant la configuration du bateau et les membres d'équipage assignés
- **Période_Inscription** : La fenêtre de temps pendant laquelle les responsables d'équipes peuvent créer et modifier les inscriptions
- **Attribution_Place** : L'association d'un membre d'équipage à une position spécifique (rameur ou barreur) dans un bateau
- **Passerelle_Paiement** : Intégration Stripe pour traiter les frais d'inscription
- **Processus_Validation** : Révision et approbation par l'admin des licences des membres d'équipage et des détails d'inscription

## 1. Exigences Fonctionnelles

Ces exigences définissent ce que fait le système du point de vue métier et utilisateur.

### EF-1 : Authentification des Responsables d'Équipe

**Histoire Utilisateur :** En tant que responsable d'équipe, je veux m'inscrire et m'authentifier de manière sécurisée, afin de pouvoir gérer les inscriptions de bateaux de mon club pour la compétition.

#### Critères d'Acceptation

1. QUAND un responsable d'équipe accède au portail d'inscription, LE Système_Inscription DOIT afficher les options d'authentification incluant email/mot de passe et fournisseurs de connexion sociale
2. QUAND un responsable d'équipe fournit des identifiants valides, LE Système_Inscription DOIT authentifier l'utilisateur et établir une session sécurisée
3. QUAND un responsable d'équipe reste inactif pendant 30 minutes, LE Système_Inscription DOIT automatiquement déconnecter l'utilisateur pour la sécurité
4. QUAND un responsable d'équipe demande une récupération de mot de passe, LE Système_Inscription DOIT envoyer un lien de réinitialisation sécurisé par email
5. LE Système_Inscription DOIT stocker les informations de profil du responsable d'équipe incluant nom, email, affiliation au club d'aviron, et numéro de mobile obligatoire

### EF-2 : Gestion des Membres d'Équipage

**Histoire Utilisateur :** En tant que responsable d'équipe, je veux gérer les informations des membres d'équipage, afin de maintenir des dossiers précis de tous les participants de mon club.

#### Critères d'Acceptation

1. QUAND un responsable d'équipe ajoute un membre d'équipage, LE Système_Inscription DOIT exiger nom, date de naissance, sexe, numéro de licence, et informations de catégorie
2. PENDANT que la période d'inscription est active, LE Système_Inscription DOIT permettre aux responsables d'équipes de modifier les informations des membres d'équipage
3. QUAND un responsable d'équipe saisit un numéro de licence, LE Système_Inscription DOIT valider le format alphanumérique
4. LE Système_Inscription DOIT persister les informations des membres d'équipage pendant toute la période d'inscription pour d'éventuels changements d'informations ou d'attribution de bateau
5. QUAND la période d'inscription se termine, LE Système_Inscription DOIT empêcher les responsables d'équipes de modifier les informations des membres d'équipage sauf exception accordée par l'admin

### EF-3 : Inscription de Bateau et Attribution de Places

**Histoire Utilisateur :** En tant que responsable d'équipe, je veux configurer les inscriptions de bateaux avec attribution de places, afin de pouvoir inscrire des équipages complets pour des catégories de compétition spécifiques.

#### Critères d'Acceptation

1. QUAND un responsable d'équipe crée une inscription de bateau, LE Système_Inscription DOIT afficher les catégories disponibles de la liste prédéfinie de 28 catégories de compétition
2. QUAND un responsable d'équipe sélectionne un type de bateau, LE Système_Inscription DOIT configurer le nombre approprié de places de rameur et de places de barreur basé sur la configuration du bateau
3. PENDANT qu'une inscription de bateau est incomplète, LE Système_Inscription DOIT permettre aux responsables d'équipes de sauvegarder des configurations partielles et de revenir plus tard
4. QUAND toutes les places requises sont assignées à des membres d'équipage, LE Système_Inscription DOIT marquer l'inscription de bateau comme complète
5. QUAND un membre d'équipage est assigné à une place, LE Système_Inscription DOIT marquer le membre d'équipage comme assigné à un bateau
6. SI un membre d'équipage est déjà marqué comme assigné à une place, ALORS LE Système_Inscription NE DOIT PAS permettre au responsable d'équipe d'assigner le membre d'équipage à une autre place de bateau
7. SI un membre d'équipage est signalé avec des problèmes, ALORS LE Système_Inscription DOIT permettre au responsable d'équipe de marquer le problème comme résolu
8. LE Système_Inscription DOIT afficher les attributions de places avec les noms des membres d'équipage dans un format visuel clair avec des liens vers l'inscription de bateau ou les informations du membre d'équipage et avec des problèmes potentiellement signalés
9. LE Système_Inscription DOIT enregistrer tous les changements du responsable d'équipe avec horodatage et identification utilisateur

### EF-4 : Traitement des Paiements

**Histoire Utilisateur :** En tant que responsable d'équipe, je veux traiter les paiements pour mes inscriptions, afin de sécuriser la participation de mon club à la compétition.

#### Critères d'Acceptation

1. QUAND un responsable d'équipe initie un paiement, LE Système_Inscription DOIT calculer les frais totaux basés sur les prix configurés des places de rameur et de barreur
2. QUAND le traitement du paiement se produit, LE Système_Inscription DOIT s'intégrer avec la Passerelle_Paiement Stripe pour la gestion sécurisée des transactions
3. LE Système_Inscription DOIT suivre les paiements partiels et afficher le statut de paiement aux responsables d'équipes
4. QUAND le paiement est complété, LE Système_Inscription DOIT envoyer une confirmation par email et mettre à jour le statut d'inscription
5. SI le paiement n'est pas complété avant la fin de la période d'inscription, ALORS LE Système_Inscription DOIT notifier le responsable d'équipe de la date limite de la période de grâce
6. S'IL y a des problèmes signalés pour certains membres d'équipage, ALORS LE Système_Inscription DOIT quand même permettre le traitement du paiement

### EF-5 : Configuration Système Admin

**Histoire Utilisateur :** En tant qu'utilisateur admin, je veux configurer les paramètres système, afin de pouvoir gérer les périodes d'inscription, la tarification, et les catégories de compétition.

#### Critères d'Acceptation

1. QUAND un Utilisateur_Admin accède aux paramètres de configuration, LE Système_Inscription DOIT afficher les paramètres modifiables pour les dates de période d'inscription
2. QUAND un Utilisateur_Admin modifie la tarification des places, LE Système_Inscription DOIT mettre à jour les prix des places de rameur et de barreur pour toutes les nouvelles inscriptions
3. LE Système_Inscription DOIT fournir aux Utilisateurs_Admin l'accès à la liste prédéfinie de 28 catégories de compétition
4. QUAND un Utilisateur_Admin définit la durée de la période de grâce, LE Système_Inscription DOIT appliquer le délai configuré pour les notifications de paiement
5. LE Système_Inscription DOIT enregistrer tous les changements de configuration des Utilisateurs_Admin avec horodatage et identification utilisateur

### EF-6 : Validation et Gestion des Inscriptions

**Histoire Utilisateur :** En tant qu'utilisateur admin, je veux valider et gérer les inscriptions, afin d'assurer la conformité avec les règles de compétition et gérer les exceptions.

#### Critères d'Acceptation

1. QUAND un Utilisateur_Admin révise les inscriptions, LE Système_Inscription DOIT afficher les informations des membres d'équipage avec des indicateurs de statut de validation
2. QUAND un Utilisateur_Admin identifie des problèmes d'inscription, LE Système_Inscription DOIT permettre le signalement de problèmes visibles au responsable d'équipe correspondant
3. SI un responsable d'équipe a résolu un problème signalé, LE Système_Inscription DOIT afficher le problème signalé comme résolu par le responsable d'équipe
4. PENDANT que la période d'inscription est active, LE Système_Inscription DOIT permettre aux responsables d'équipes de corriger les problèmes signalés de manière autonome
5. QUAND la période d'inscription se termine, LE Système_Inscription DOIT permettre aux Utilisateurs_Admin de modifier manuellement les informations d'inscription ou d'accorder un accès d'édition temporaire à des responsables d'équipes spécifiques
6. QUAND un Utilisateur_Admin accorde des exceptions d'édition, LE Système_Inscription DOIT appliquer une limite de temps configurable avec expiration automatique

### EF-7 : Rapports et Analyses

**Histoire Utilisateur :** En tant qu'utilisateur admin, je veux accéder à des rapports et analyses complets, afin de pouvoir surveiller le progrès des inscriptions et exporter des données pour la gestion de la compétition.

#### Critères d'Acceptation

1. QUAND un Utilisateur_Admin accède au tableau de bord, LE Système_Inscription DOIT afficher des statistiques en temps réel incluant le nombre de participants et de bateaux par catégorie
2. QUAND un Utilisateur_Admin demande une exportation de données, LE Système_Inscription DOIT générer des fichiers CSV ou Excel contenant tous les détails des bateaux et membres d'équipage
3. LE Système_Inscription DOIT fournir aux Utilisateurs_Admin des rapports financiers montrant le ratio de places payées aux places inscrites
4. LE Système_Inscription DOIT suivre et afficher les métriques d'inscription incluant le total des participants et la distribution par catégorie
5. LE Système_Inscription DOIT maintenir des journaux d'audit de toutes les actions des Utilisateurs_Admin avec étiquetage basé sur les rôles

### EF-8 : Gestion de Configuration Dynamique

**Histoire Utilisateur :** En tant qu'utilisateur admin, je veux pouvoir changer la configuration du Système_Inscription, afin de pouvoir modifier la liste des catégories de compétition, les dates de période d'inscription, et d'autres paramètres système de manière dynamique.

#### Critères d'Acceptation

1. QUAND un Utilisateur_Admin accède à l'interface de configuration système, LE Système_Inscription DOIT afficher tous les paramètres configurables dans un format organisé et modifiable
2. QUAND un Utilisateur_Admin modifie la liste des catégories de compétition, LE Système_Inscription DOIT valider les changements et mettre à jour les catégories disponibles pour les nouvelles inscriptions de bateaux
3. QUAND un Utilisateur_Admin change les dates de début et fin de période d'inscription, LE Système_Inscription DOIT valider que la date de début est antérieure à la date de fin et appliquer les changements immédiatement
4. QUAND un Utilisateur_Admin met à jour la configuration de tarification des places, LE Système_Inscription DOIT appliquer les nouveaux prix à toutes les inscriptions futures tout en préservant la tarification des inscriptions existantes
5. QUAND un Utilisateur_Admin modifie les paramètres de période de grâce, LE Système_Inscription DOIT mettre à jour la chronologie de notification de paiement pour toutes les inscriptions affectées
6. LE Système_Inscription DOIT exiger une confirmation de l'Utilisateur_Admin avant d'appliquer les changements de configuration qui pourraient affecter les inscriptions existantes
7. QUAND les changements de configuration sont appliqués, LE Système_Inscription DOIT enregistrer toutes les modifications avec horodatage, valeurs précédentes, nouvelles valeurs, et identification de l'Utilisateur_Admin
8. SI les changements de configuration échouent à la validation, ALORS LE Système_Inscription DOIT afficher des messages d'erreur clairs et empêcher les changements invalides d'être sauvegardés

### EF-9 : Affichage d'Informations Page d'Accueil

**Histoire Utilisateur :** En tant qu'utilisateur quelconque, je veux voir les informations générales et les détails du processus d'inscription sur la page d'accueil, afin de pouvoir comprendre la compétition et les procédures d'inscription avant de créer un compte.

#### Critères d'Acceptation

1. QUAND un utilisateur quelconque accède à la page d'accueil du Système_Inscription, LE Système_Inscription DOIT afficher les informations générales sur la compétition Course des Impressionnistes
2. LE Système_Inscription DOIT afficher le processus d'inscription et les procédures d'inscription telles que définies dans l'Annexe B
3. LE Système_Inscription DOIT fournir des options de navigation claires pour que les utilisateurs puissent soit se connecter à un compte existant soit créer un nouveau compte
4. LE Système_Inscription DOIT afficher les dates de période d'inscription actuelles et les dates limites de manière proéminente sur la page d'accueil
5. LE Système_Inscription DOIT montrer tout le contenu de la page d'accueil dans la langue sélectionnée par l'utilisateur (français ou anglais)
6. LE Système_Inscription DOIT fournir les informations de contact de l'organisation RCPM pour les utilisateurs qui ont besoin d'assistance

## 2. Exigences Non-Fonctionnelles

Ces exigences définissent comment le système performe et les attributs de qualité.

### ENF-1 : Exigences de Performance

#### Critères d'Acceptation

1. LE Système_Inscription DOIT charger les pages en moins de 3 secondes dans des conditions réseau normales
2. LE Système_Inscription DOIT répondre aux interactions utilisateur en moins de 1 seconde pour les opérations standard
3. LE Système_Inscription DOIT gérer le traitement concurrent des paiements sans dégradation de performance
4. LE Système_Inscription DOIT maintenir une performance réactive pendant les périodes de pointe d'inscription

### ENF-2 : Exigences de Scalabilité

#### Critères d'Acceptation

1. LE Système_Inscription DOIT automatiquement s'adapter pour gérer jusqu'à 1000 utilisateurs concurrents sans intervention manuelle
2. LE Système_Inscription DOIT supporter l'inscription de jusqu'à 10 000 membres d'équipage et 2 000 bateaux par compétition
3. LE Système_Inscription DOIT maintenir les niveaux de performance à mesure que le volume de données augmente pendant la période d'inscription
4. LE Système_Inscription DOIT réduire à zéro quand possible en dehors de la période d'inscription

### ENF-3 : Exigences de Sécurité

#### Critères d'Acceptation

1. LE Système_Inscription DOIT chiffrer toutes les données au repos en utilisant des algorithmes de chiffrement standard de l'industrie
2. LE Système_Inscription DOIT chiffrer toutes les données en transit en utilisant les protocoles HTTPS/TLS
3. LE Système_Inscription DOIT implémenter une authentification sécurisée avec des options d'authentification multi-facteurs
4. LE Système_Inscription DOIT se conformer aux exigences RGPD pour la protection et la confidentialité des données utilisateur
5. LE Système_Inscription DOIT implémenter un contrôle d'accès basé sur les rôles pour restreindre les fonctionnalités selon les rôles utilisateur

### ENF-4 : Exigences d'Utilisabilité

#### Critères d'Acceptation

1. LE Système_Inscription DOIT fournir un support multilingue pour les langues française et anglaise
2. LE Système_Inscription DOIT détecter la langue du navigateur et par défaut au français ou anglais en conséquence
3. LE Système_Inscription DOIT fournir un changement manuel de langue entre français et anglais à tout moment pendant les sessions utilisateur
4. LE Système_Inscription DOIT s'afficher de manière responsive sur les tailles d'écran mobile, tablette et bureau
5. LE Système_Inscription DOIT maintenir une fonctionnalité cohérente et une expérience utilisateur sur les navigateurs supportés incluant Chrome, Firefox, Safari, et Edge

### ENF-5 : Exigences de Fiabilité

#### Critères d'Acceptation

1. LE Système_Inscription DOIT maintenir 99,5% de disponibilité pendant la période d'inscription
2. LE Système_Inscription DOIT implémenter une gestion d'erreur gracieuse avec des messages d'erreur conviviaux
3. LE Système_Inscription DOIT fournir une récupération automatique des pannes transitoires
4. LE Système_Inscription DOIT maintenir la cohérence des données pendant les pannes système

### ENF-6 : Exigences de Notification

#### Critères d'Acceptation

1. QUAND des événements d'inscription se produisent, LE Système_Inscription DOIT envoyer des notifications email pour les confirmations, problèmes, et rappels de dates limites
2. LE Système_Inscription DOIT répéter les notifications par email de manière régulière (par défaut hebdomadaire) s'il y a des problèmes en cours
3. LE Système_Inscription DOIT afficher des notifications dans l'application via des bannières ou popups pour l'attention immédiate de l'utilisateur
4. QUAND on approche des dates limites d'inscription, LE Système_Inscription DOIT notifier les responsables d'équipes via email et notifications dans l'application
5. LE Système_Inscription DOIT fournir un centre de notifications dans l'application pour que les utilisateurs puissent réviser l'historique des messages
6. LE Système_Inscription DOIT s'assurer que toutes les notifications sont livrées dans la préférence de langue sélectionnée par l'utilisateur

## 3. Contraintes Techniques

Ces exigences définissent l'architecture technique obligatoire et les contraintes d'implémentation.

### CT-1 : Contrainte d'Architecture Serverless

**Contrainte :** Le système doit être implémenté en utilisant une architecture serverless sur AWS.

#### Critères d'Acceptation

1. LE Système_Inscription DOIT utiliser les fonctions AWS Lambda écrites en Python pour tout le traitement backend
2. LE Système_Inscription DOIT stocker toutes les données dans Amazon DynamoDB avec chiffrement au repos activé
3. QUAND le trafic augmente, LE Système_Inscription DOIT automatiquement adapter les fonctions Lambda et la capacité DynamoDB sans intervention manuelle
4. LE Système_Inscription DOIT servir l'application frontend via Amazon S3 et CloudFront pour une performance optimale

### CT-2 : Contrainte d'Infrastructure as Code

**Contrainte :** Toute l'infrastructure doit être définie et déployée en utilisant les pratiques Infrastructure as Code.

#### Critères d'Acceptation

1. LE Système_Inscription DOIT implémenter Infrastructure as Code en utilisant AWS CDK en langage Python pour des déploiements reproductibles
2. LE Système_Inscription DOIT sauvegarder les données vers Amazon S3 de manière régulière (par défaut quotidienne) avec un préfixe de l'année courante et un nom d'objet avec date/heure complète
3. QUAND un Utilisateur_DevOps déploie l'infrastructure, LE Système_Inscription DOIT permettre soit la spécification d'une base de données existante soit la restauration de données de sauvegarde précédentes soit la création d'une nouvelle base de données
4. LE Système_Inscription DOIT maintenir le versioning de configuration pour permettre aux Utilisateurs_DevOps de suivre les changements et de revenir en arrière si nécessaire

### CT-3 : Contrainte de Surveillance et Journalisation

**Contrainte :** Le système doit fournir des capacités complètes de surveillance et journalisation.

#### Critères d'Acceptation

1. LE Système_Inscription DOIT envoyer tous les journaux d'application vers Amazon CloudWatch avec formatage JSON structuré
2. QUAND des erreurs système se produisent, LE Système_Inscription DOIT déclencher des alarmes CloudWatch et envoyer des notifications email aux Utilisateurs_DevOps
3. LE Système_Inscription DOIT implémenter des vérifications de santé pour tous les composants système critiques incluant les fonctions Lambda et DynamoDB
4. QUAND les seuils de performance sont dépassés, LE Système_Inscription DOIT automatiquement alerter les Utilisateurs_DevOps via les canaux de notification configurés
5. LE Système_Inscription DOIT maintenir des capacités de sauvegarde et récupération avec sauvegardes DynamoDB quotidiennes et récupération point-dans-le-temps de 35 jours

### CT-4 : Contrainte de Configuration Centralisée

**Contrainte :** Toute la configuration système doit être gérée de manière centralisée et accessible aux utilisateurs DevOps.

#### Critères d'Acceptation

1. LE Système_Inscription DOIT stocker tous les paramètres de configuration dans un service de configuration centralisé accessible aux Utilisateurs_DevOps
2. QUAND un Utilisateur_DevOps accède au magasin de configuration, LE Système_Inscription DOIT afficher tous les paramètres système incluant les périodes d'inscription, tarification, catégories, et paramètres de notification
3. LE Système_Inscription DOIT fournir aux Utilisateurs_DevOps un accès en lecture seule aux valeurs de configuration via AWS Systems Manager Parameter Store ou service équivalent
4. QUAND des changements de configuration sont faits via l'interface admin, LE Système_Inscription DOIT automatiquement mettre à jour le magasin de configuration centralisé
5. QUAND un Utilisateur_DevOps a besoin de modifier manuellement la configuration pour des urgences, LE Système_Inscription DOIT fournir un accès CLI ou API sécurisé avec authentification appropriée
6. LE Système_Inscription DOIT valider tous les changements de configuration pour assurer l'intégrité système avant de les appliquer
7. LE Système_Inscription DOIT notifier les Utilisateurs_Admin pertinents quand les Utilisateurs_DevOps font des changements de configuration manuels

## Annexe A : Données de Référence

### A.1 Catégories de Compétition

Le système doit supporter les 28 catégories de compétition prédéfinies suivantes :

| Numéro Catégorie | Nom Catégorie (Français) |
| ---------------- | ------------------------------------------------------------ |
| 1                | FEMME-CADET-QUATRE DE POINTE OU COUPLE AVEC BARREUR          |
| 2                | HOMME-CADET-QUATRE DE POINTE OU COUPLE AVEC BARREUR          |
| 3                | MIXTE-CADET-QUATRE DE POINTE OU COUPLE AVEC BARREUR          |
| 4                | FEMME-CADET-HUIT DE POINTE AVEC BARREUR                      |
| 5                | HOMME-CADET-HUIT DE POINTE AVEC BARREUR                      |
| 6                | FEMME-JUNIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 7                | HOMME-JUNIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 8                | MIXTE-JUNIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 9                | HOMME-JUNIOR-QUATRE DE POINTE AVEC BARREUR                   |
| 10               | FEMME-JUNIOR-HUIT DE POINTE AVEC BARREUR                     |
| 11               | HOMME-JUNIOR-HUIT DE POINTE AVEC BARREUR                     |
| 12               | FEMME-SENIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 13               | HOMME-SENIOR-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 14               | HOMME SENIOR-QUATRE DE POINTE AVEC BARREUR                   |
| 15               | FEMME-SENIOR-HUIT DE POINTE AVEC BARREUR                     |
| 16               | HOMME-SENIOR-HUIT DE POINTE AVEC BARREUR                     |
| 17               | FEMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR YOLETTE |
| 18               | HOMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR YOLETTE |
| 19               | MIXTE-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR YOLETTE |
| 20               | FEMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR         |
| 21               | HOMME-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR         |
| 22               | MIXTE-MASTER-QUATRE DE POINTE OU COUPLE AVEC BARREUR         |
| 23               | FEMME-MASTER-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 24               | HOMME-MASTER-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 25               | MIXTE-MASTER-QUATRE DE POINTE OU COUPLE SANS BARREUR         |
| 26               | FEMME-MASTER-HUIT DE POINTE OU COUPLE AVEC BARREUR           |
| 27               | HOMME-MASTER-HUIT DE POINTE OU COUPLE AVEC BARREUR           |
| 28               | MIXTE-MASTER-HUIT DE POINTE OU COUPLE AVEC BARREUR           |

### A.2 Configurations de Types de Bateaux

Le système doit supporter les types de bateaux suivants avec leurs configurations de places :

| Type de Bateau | Places Rameur | Places Barreur | Total Places |
| -------------- | ------------- | -------------- | ------------ |
| SKIFF (1x) | 1 | 0 | 1 |
| QUATRE AVEC BARREUR | 4 | 1 | 5 |
| QUATRE SANS BARREUR | 4 | 0 | 4 |
| HUIT | 8 | 1 | 9 |

## Annexe B : Contenu Page d'Accueil

### B.1 Informations Générales et Processus d'Inscription

*Contenu à extraire de /raw-requirements/procedure-inscription-A1.docx*

**Note :** Cette section devrait contenir le texte complet du document français "procedure-inscription-A1.docx" qui inclut :
- Informations générales sur la compétition Course des Impressionnistes
- Processus et procédures d'inscription détaillés
- Directives et exigences d'inscription
- Informations de contact et dates importantes

Le contenu devrait être fourni en versions française (originale) et anglaise (traduite) pour supporter les exigences multilingues du système.
