# Fonctionnalité de Téléchargement de l'Avant-Programme

## Vue d'ensemble

Cette fonctionnalité permet à tous les visiteurs du site (authentifiés ou non) de télécharger l'avant-programme de la Course des Impressionnistes directement depuis la bannière d'accueil.

## Implémentation

### 1. Fichier PDF

**Emplacement:** `frontend/public/avant-programme-fr.pdf`

Le fichier PDF est placé dans le dossier `public` du frontend, ce qui le rend accessible directement via l'URL `/avant-programme-fr.pdf`.

**Nom du fichier:**
- Format : `avant-programme-fr.pdf`
- Sans espaces (meilleure compatibilité URL)
- Sans année (pas besoin de renommer chaque année)
- Suffixe `-fr` pour la version française (permet d'ajouter `-en` pour l'anglais)

### 2. Bouton de Téléchargement

**Emplacement:** `frontend/src/views/Home.vue` (section hero)

Un bouton de téléchargement a été ajouté dans la bannière hero de la page d'accueil, à côté du bouton "Site de l'événement".

**Caractéristiques:**
- Icône de téléchargement (flèche vers le bas) + texte
- Texte "Avant-programme" (FR) / "Program" (EN)
- Style cohérent avec le bouton "Site de l'événement" (btn-outline)
- Accessible à tous les visiteurs (authentifiés ou non)
- Visible dans les deux états : non connecté et connecté
- Responsive : s'adapte automatiquement sur mobile

**Position:**
- Pour les utilisateurs non connectés : 
  - Gauche : "Site de l'événement" et "Avant-programme"
  - Droite : "Se connecter" et "S'inscrire"
- Pour les utilisateurs connectés : 
  - Gauche : "Site de l'événement" et "Avant-programme"
  - Droite : "Tableau de bord"

### 3. Traductions

**Fichiers modifiés:**
- `frontend/src/locales/fr.json` : `"downloadProgram": "Avant-programme"`
- `frontend/src/locales/en.json` : `"downloadProgram": "Program"`

### 4. Styles CSS

Le bouton utilise les design tokens existants et suit les conventions de style du site :
- Bordure verte (#4CAF50)
- Fond transparent avec hover vert clair
- Icône SVG intégrée
- Hauteur minimale de 44px (touch target)
- Gap entre l'icône et le texte

## Utilisation

### Pour les Visiteurs

1. Accéder au site Course des Impressionnistes
2. Cliquer sur le bouton "Avant-programme" dans la bannière hero
3. Le PDF s'ouvre dans un nouvel onglet du navigateur
4. L'utilisateur peut le consulter en ligne ou le télécharger via le navigateur

**Comportement:**
- Le PDF s'affiche dans le navigateur (pas de téléchargement automatique)
- Ouverture dans un nouvel onglet (`target="_blank"`)
- L'utilisateur garde le contrôle : consultation en ligne ou téléchargement manuel
- Comportement cohérent sur tous les navigateurs

### Pour les Administrateurs

#### Mettre à Jour l'Avant-Programme

1. Remplacer le fichier dans `frontend/public/avant-programme-fr.pdf`
2. Rebuild le frontend : `cd frontend && npm run build`
3. Déployer : `cd infrastructure && make deploy-frontend-dev` (ou `-prod`)

**Important :** Gardez le même nom de fichier (`avant-programme-fr.pdf`) pour ne pas avoir à modifier le code chaque année.

#### Ajouter une Version Anglaise

Pour ajouter une version anglaise de l'avant-programme :

1. Placer le fichier dans `frontend/public/avant-programme-en.pdf`
2. Modifier `frontend/src/views/Home.vue` pour détecter la langue :

```vue
<a 
  :href="$i18n.locale === 'fr' ? '/avant-programme-fr.pdf' : '/avant-programme-en.pdf'"
  target="_blank" 
  rel="noopener noreferrer"
  class="btn btn-outline"
>
```

## Responsive Design

### Desktop (≥768px)
- Icône + texte visible
- Padding normal

### Mobile (<768px)
- Icône uniquement (texte masqué)
- Padding réduit
- Taille minimale de 44px maintenue

## Accessibilité

- Attribut `title` pour le tooltip
- Icône SVG avec `stroke` pour la visibilité
- Contraste suffisant (vert sur blanc)
- Touch target de 44px minimum

## Notes Techniques

- Le fichier PDF est servi statiquement depuis le dossier `public`
- Aucune authentification requise
- Pas d'appel API nécessaire
- Le PDF s'ouvre dans un nouvel onglet (`target="_blank"`)
- Attribut `rel="noopener noreferrer"` pour la sécurité
- Pas d'attribut `download` : le navigateur affiche le PDF au lieu de le télécharger automatiquement
- L'utilisateur peut télécharger le PDF via les contrôles du navigateur s'il le souhaite

## Évolutions Futures

- [ ] Ajouter une version anglaise de l'avant-programme
- [ ] Permettre le téléchargement de plusieurs documents (règlement, parcours, etc.)
- [ ] Ajouter un menu déroulant pour plusieurs documents
- [ ] Tracker les téléchargements (analytics)
