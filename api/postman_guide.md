# Guide d'utilisation de Postman pour l'API REST Hackerz

Ce guide vous explique comment configurer et utiliser Postman pour tester l'API REST de Hackerz.

## Solution rapide au problème "Error: getaddrinfo ENOTFOUND {{base_url}}"

1. Utilisez les fichiers générés par le script Python dans le dossier `postman_export_20250412_203959`:
   - Importez `hackerz_environment.json` pour définir les variables d'environnement
   - Importez `hackerz_collection.json` pour obtenir toutes les requêtes préconfigurées

2. **Important**: Vérifiez que:
   - L'environnement est sélectionné en haut à droite de l'interface Postman
   - Les valeurs des variables ne contiennent pas les accolades `{{ }}` elles-mêmes

## Procédure détaillée

### 1. Importez l'environnement

1. Dans Postman, cliquez sur l'icône "Environments" (engrenage) dans la barre latérale gauche
2. Cliquez sur "Import" 
3. Sélectionnez le fichier `api/postman_export_20250412_203959/hackerz_environment.json`
4. Après l'importation, vérifiez que les variables sont correctement définies:

| Variable | Valeur |
|----------|--------|
| base_url | http://127.0.0.1:8000/api/v1 |
| token | 2e5db3dfc70de80265cda1aad05cf7f0dad7fffd |

### 2. Importez la collection

1. Cliquez sur "Collections" dans la barre latérale gauche
2. Cliquez sur "Import"
3. Sélectionnez le fichier `api/postman_export_20250412_203959/hackerz_collection.json`

### 3. Activez l'environnement

1. En haut à droite de l'interface Postman, sélectionnez "Hackerz API Environment" dans le menu déroulant
2. Assurez-vous que l'environnement est bien actif (l'œil doit être ouvert)

### 4. Testez une requête simple

1. Dans la collection importée, ouvrez une requête simple comme `GET /blog/categories/`
2. Vérifiez que l'URL dans la requête est `{{base_url}}/blog/categories/` (avec les accolades)
3. Cliquez sur "Send"

## Prérequis

1. Téléchargez et installez [Postman](https://www.postman.com/downloads/)
2. Lancez votre serveur Django avec `python manage.py runserver`

## Configuration initiale

### Importer la collection

1. Ouvrez Postman
2. Cliquez sur "Import" dans le coin supérieur gauche
3. Sélectionnez le fichier `api/postman_export_20250412_203959/hackerz_collection.json`
4. Validez l'importation

### Créer un environnement

1. Cliquez sur l'icône "Environments" (engrenage) dans le coin supérieur droit
2. Cliquez sur "Import"
3. Sélectionnez le fichier `api/postman_export_20250412_203959/hackerz_environment.json`
4. Sélectionnez l'environnement "Hackerz API Environment" dans le menu déroulant en haut à droite

## Authentification

Le token est déjà configuré dans l'environnement importé avec la valeur:
```
2e5db3dfc70de80265cda1aad05cf7f0dad7fffd
```

## Utilisation des requêtes

La collection est organisée en plusieurs dossiers selon les types d'API:

- **Shop** : Requêtes liées aux produits, catégories, avis et commandes
- **Blog** : Requêtes liées aux articles, commentaires et catégories
- **Projects** : Requêtes liées aux projets

### Requêtes nécessitant une authentification

Toutes les requêtes dans la collection sont préconfigurées pour utiliser le token stocké dans votre environnement.

### Tests et scripts

La collection inclut des exemples de réponses qui vous aideront à comprendre le format des données attendues.

## Manipulation des données

### Création de ressources (POST)

Pour les requêtes POST, assurez-vous de :
1. Avoir un token valide (si nécessaire)
2. Vérifier que le corps de la requête respecte le format attendu par l'API
3. Vérifier que les headers incluent `Content-Type: application/json`

### Mise à jour de ressources (PUT/PATCH)

Pour mettre à jour une ressource :
1. Utilisez PUT pour remplacer complètement une ressource
2. Utilisez PATCH pour mettre à jour partiellement une ressource

### Suppression de ressources (DELETE)

Pour supprimer une ressource, assurez-vous d'avoir les droits nécessaires (authentification et permissions).

## Astuces

- **Variables d'environnement** : Utilisez-les pour stocker des valeurs réutilisables (token, IDs, etc.)
- **Tests automatisés** : Ajoutez des scripts de test pour vérifier les réponses
- **Collection Runner** : Exécutez plusieurs requêtes à la suite pour tester des scénarios complets
- **Documentation** : Consultez la documentation Swagger à l'URL `http://127.0.0.1:8000/api/v1/swagger/` pour des informations détaillées sur les endpoints

## Dépannage

- **Erreur 401 Unauthorized** : Vérifiez que votre token est valide et correctement utilisé
- **Erreur 400 Bad Request** : Vérifiez le format de vos données
- **Erreur 404 Not Found** : Vérifiez l'URL et les paramètres utilisés
- **Erreur 500 Server Error** : Consultez les logs du serveur Django pour identifier le problème

## Problème: "Error: getaddrinfo ENOTFOUND {{base_url}}"

Si vous rencontrez cette erreur, cela signifie que Postman ne peut pas résoudre la variable d'environnement `{{base_url}}`. Voici comment résoudre ce problème:

### Configuration correcte de l'environnement

1. Dans Postman, cliquez sur l'icône "Environments" dans la barre latérale gauche (icône d'engrenage)
2. Sélectionnez l'environnement "Hackerz API Environment" (ou créez-le s'il n'existe pas)
3. Assurez-vous que les variables suivantes sont correctement définies:

| Variable | Valeur initiale | Valeur actuelle |
|----------|----------------|-----------------|
| base_url | http://127.0.0.1:8000/api/v1 | http://127.0.0.1:8000/api/v1 |
| token | 2e5db3dfc70de80265cda1aad05cf7f0dad7fffd | 2e5db3dfc70de80265cda1aad05cf7f0dad7fffd |

4. **Important**: Supprimez les accolades `{{ }}` dans les valeurs elles-mêmes - elles ne doivent apparaître que lorsque vous référencez les variables dans les requêtes

5. Cliquez sur "Save" pour enregistrer ces modifications

### Vérifier l'environnement actif

Assurez-vous que votre environnement est bien sélectionné:

1. En haut à droite de l'interface Postman, vérifiez que "Hackerz API Environment" est sélectionné dans le menu déroulant des environnements
2. Si ce n'est pas le cas, sélectionnez-le dans la liste

### Tester avec une URL directe

Si le problème persiste, essayez temporairement de remplacer `{{base_url}}` par l'URL complète:

```
http://127.0.0.1:8000/api/v1/blog/posts/
```

### Autres vérifications

1. **Serveur en cours d'exécution**: Assurez-vous que votre serveur Django est bien en cours d'exécution sur le port 8000
2. **Format des variables**: Vérifiez qu'il n'y a pas d'espaces ou de caractères indésirables dans vos variables d'environnement
3. **Version de Postman**: Assurez-vous d'utiliser une version récente de Postman

### Importer la collection et l'environnement

Si vous utilisez les fichiers générés par le script Python:

1. Dans Postman, cliquez sur "Import" (en haut à gauche)
2. Sélectionnez les fichiers suivants:
   - `api/postman_export_20250412_203959/hackerz_collection.json`
   - `api/postman_export_20250412_203959/hackerz_environment.json`
3. Cliquez sur "Import" pour finaliser

### Vérifier que l'authentification fonctionne

Assurez-vous que votre token est valide en testant d'abord un endpoint simple comme:

```
GET http://127.0.0.1:8000/api/v1/blog/categories/
```

Si vous obtenez une erreur d'authentification, vérifiez la validité de votre token 