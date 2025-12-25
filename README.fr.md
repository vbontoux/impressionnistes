# Système d'Inscription Course des Impressionnistes

Une application web serverless pour gérer les inscriptions aux compétitions d'aviron, construite sur AWS avec un frontend Vue.js et un backend Python.

## 🚀 Démarrage Rapide

Nouveau sur le projet ? Commencez ici :

1. **[Guide de Démarrage Rapide](docs/guides/setup/quick-start.md)** - Démarrez en quelques minutes
2. **[Guide d'Installation](docs/guides/setup/setup.md)** - Instructions d'installation détaillées
3. **[Guide de Déploiement](docs/guides/setup/deployment.md)** - Déployer sur AWS

## 📖 Aperçu

Le Système d'Inscription Course des Impressionnistes permet aux responsables d'équipe des clubs d'aviron d'inscrire des équipages et des bateaux pour la Compétition RCPM.

### Fonctionnalités Principales

**Pour les Responsables d'Équipe :**
- Inscrire et gérer les membres d'équipage
- Créer des inscriptions de bateaux avec attribution des places
- Demander la location de bateaux au RCPM
- Traiter les paiements de manière sécurisée via Stripe
- Recevoir des notifications sur l'état des inscriptions

**Pour les Administrateurs :**
- Valider et gérer toutes les inscriptions
- Configurer les paramètres système (dates, tarifs, courses)
- Signaler des problèmes et accorder des exceptions de modification
- Exporter les données pour la gestion de la compétition (CSV, Excel/CrewTimer)
- Consulter les statistiques du tableau de bord en temps réel

**Points Techniques Forts :**
- Architecture serverless avec mise à l'échelle automatique
- Conception DynamoDB à table unique pour l'efficacité
- Support multilingue (Français/Anglais)
- Domaines personnalisés avec certificats SSL
- Gestion des données conforme au RGPD
- Surveillance et journalisation complètes

## 🏗️ Architecture

- **Frontend** : Vue.js 3 avec Vite, servi via S3/CloudFront
- **Backend** : Fonctions Lambda Python
- **Base de données** : Amazon DynamoDB (conception à table unique)
- **API** : AWS API Gateway (REST)
- **Authentification** : Amazon Cognito
- **Paiements** : Intégration Stripe
- **Infrastructure** : AWS CDK (Python)
- **Surveillance** : Journaux et alarmes CloudWatch

**[→ Structure Détaillée du Projet](docs/reference/project-structure.md)**

## 📚 Documentation

### Installation & Déploiement

- **[Démarrage Rapide](docs/guides/setup/quick-start.md)** - Démarrez rapidement
- **[Guide d'Installation](docs/guides/setup/setup.md)** - Instructions d'installation complètes
- **[Guide de Déploiement](docs/guides/setup/deployment.md)** - Déployer sur les environnements AWS
- **[Domaines Personnalisés](docs/guides/setup/custom-domains.md)** - Configurer les domaines personnalisés et SSL
- **[Configuration Stripe](docs/guides/setup/stripe-setup.md)** - Configurer le traitement des paiements
- **[Gestion des Secrets](docs/guides/setup/secrets-management.md)** - Gérer la configuration sensible

### Développement

- **[Flux de Développement](docs/guides/development/dev-workflow.md)** - Processus de développement quotidien
- **[Guide de Test](docs/guides/development/testing-guide.md)** - Stratégie et pratiques de test
- **[Test Lambda](docs/guides/development/lambda-testing.md)** - Tester les fonctions Lambda localement
- **[Test Frontend](docs/guides/development/frontend-testing.md)** - Guide de test frontend
- **[Configuration Frontend](docs/guides/development/frontend-setup.md)** - Configuration du développement frontend
- **[Guide de Réactivité Mobile](docs/guides/development/mobile-responsiveness-guide.md)** - Modèles et meilleures pratiques de réactivité mobile
- **[Liste de Vérification Mobile](docs/guides/development/mobile-testing-checklist.md)** - Liste de vérification pour tester la réactivité mobile
- **[Design Réactif](docs/guides/development/responsive-design.md)** - Guide de conception réactive mobile-first
- **[Modèles de Tableaux Réactifs](docs/guides/development/responsive-table-patterns.md)** - Stratégies de réactivité des tableaux

### Opérations

- **[Démarrage Rapide Infrastructure](docs/guides/operations/infrastructure-quickstart.md)** - Commandes d'infrastructure rapides
- **[Export Base de Données](docs/guides/operations/database-export.md)** - Exporter et sauvegarder la base de données
- **[Surveillance](docs/guides/operations/monitoring.md)** - Surveiller la santé du système
- **[Enregistrements DNS](docs/guides/operations/dns-records.md)** - Référence de configuration DNS

### Référence

- **[Points de Terminaison API](docs/reference/api-endpoints.md)** - Référence API complète
- **[API d'Authentification](docs/reference/auth-api.md)** - Points de terminaison d'authentification
- **[Commandes](docs/reference/commands.md)** - Référence des commandes CLI
- **[Structure du Projet](docs/reference/project-structure.md)** - Organisation du code

### Documentation Spécifique aux Composants

- **[Fichiers d'Environnement Frontend](frontend/ENV_FILES_GUIDE.md)** - Configuration .env du frontend
- **[Test des Paiements](frontend/PAYMENT_TESTING.md)** - Tester l'intégration Stripe
- **[README Infrastructure](infrastructure/README.md)** - Aperçu du module d'infrastructure
- **[Événements de Test Auth](functions/auth/TEST_EVENTS.md)** - Charges utiles de test Lambda
- **[Guide des Migrations](functions/migrations/README.md)** - Instructions de migration de base de données
- **[README Tests](tests/README.md)** - Documentation de la suite de tests

## 🛠️ Prérequis

- Node.js 18+ et npm
- Python 3.11+
- AWS CLI configuré avec les identifiants
- AWS CDK CLI (`npm install -g aws-cdk`)
- Compte Stripe (mode test pour le développement)

## ⚡ Démarrage

### 1. Cloner et Installer

```bash
# Cloner le dépôt
git clone <repository-url>
cd impressionnistes

# Configurer les environnements virtuels Python (automatisé)
./setup-venv.sh  # macOS/Linux
# ou
.\setup-venv.ps1  # Windows PowerShell

# Installer les dépendances frontend
cd frontend
npm install
```

### 2. Configurer l'Environnement

Voir le **[Guide d'Installation](docs/guides/setup/setup.md)** pour les instructions de configuration détaillées.

### 3. Déployer l'Infrastructure

```bash
cd infrastructure
make deploy-dev
```

Voir le **[Guide de Déploiement](docs/guides/setup/deployment.md)** pour les instructions de déploiement complètes.

### 4. Exécuter le Frontend Localement

```bash
cd frontend
npm run dev
```

## 🔧 Commandes Courantes

### Infrastructure (utiliser le Makefile)

```bash
cd infrastructure

# Déploiement
make deploy-dev          # Déployer sur l'environnement de dev
make deploy-prod         # Déployer en production
make describe-infra      # Afficher les URLs API et la config

# Base de données
make db-view             # Voir le contenu de la base de données
make db-export           # Exporter la base de données en CSV
make db-migrate          # Exécuter les migrations de base de données

# Tests
make test                # Exécuter les tests d'intégration
make test-coverage       # Exécuter les tests avec couverture

# Surveillance
make costs               # Afficher les coûts AWS
make list                # Lister toutes les piles
```

**[→ Référence Complète des Commandes](docs/reference/commands.md)**

### Développement Frontend

```bash
cd frontend
npm run dev              # Démarrer le serveur de dev
npm run build            # Construire pour la production
npm run lint             # Linter le code
```

### Test Backend

```bash
cd infrastructure
make test                # Exécuter tous les tests d'intégration
make test ARGS="tests/integration/test_crew_member_api.py"  # Exécuter un test spécifique
```

## 🌐 Environnements

### Développement
- **Domaine** : `impressionnistes-dev.aviron-rcpm.fr`
- **Objectif** : Tests et développement

### Production
- **Domaine** : `impressionnistes.aviron-rcpm.fr`
- **Objectif** : Inscription en direct pour la compétition

**[→ Configuration des Domaines Personnalisés](docs/guides/setup/custom-domains.md)**

## 🔐 Sécurité

- Toutes les données chiffrées au repos (DynamoDB)
- HTTPS/TLS pour toutes les communications
- Authentification Cognito avec support MFA
- Contrôle d'accès basé sur les rôles (Responsables d'Équipe, Administrateurs)
- Assainissement et validation des entrées
- Fonctionnalités de conformité RGPD

## 📊 Surveillance

- **Journaux CloudWatch** : Tous les journaux des fonctions Lambda
- **Alarmes CloudWatch** : Taux d'erreur, limitation
- **Notifications Slack** : Alertes en temps réel pour les administrateurs et DevOps
- **Notifications Email** : Notifications utilisateur via SES

**[→ Guide de Surveillance](docs/guides/operations/monitoring.md)**

## 🤝 Contribution

### Flux de Développement

1. Créer une branche de fonctionnalité
2. Apporter des modifications en suivant les normes de codage
3. Exécuter les tests : `cd infrastructure && make test`
4. Déployer en dev : `make deploy-dev`
5. Tester vos modifications
6. Créer une pull request

**[→ Guide du Flux de Développement](docs/guides/development/dev-workflow.md)**

### Tests

- **Tests d'Intégration** : 24 tests couvrant tous les points de terminaison API
- **Tests Frontend** : Tests de composants et E2E
- **Tests Lambda** : Tests locaux avec moto

**[→ Guide de Test](docs/guides/development/testing-guide.md)**

## 📞 Support

Pour toute question ou problème, contactez l'organisation RCPM :
- **Email** : contact@impressionnistes.rcpm.fr
- **Site Web** : [Course des Impressionnistes](https://impressionnistes.aviron-rcpm.fr)

## 📄 Licence

Copyright © 2025 RCPM - Rowing Club de Port Marly

---

## 📁 Structure de la Documentation

```
docs/
├── guides/
│   ├── setup/              # Guides d'installation et de déploiement
│   ├── development/        # Guides de développement
│   └── operations/         # Opérations et maintenance
├── reference/              # Documentation de référence technique
└── archived/               # Documentation historique

La documentation spécifique aux composants reste avec leurs composants :
├── frontend/               # Guides spécifiques au frontend
├── infrastructure/         # Guides spécifiques à l'infrastructure
├── functions/              # Documentation des fonctions Lambda
└── tests/                  # Documentation des tests
```

**[→ Index Complet de la Documentation](docs/)**

