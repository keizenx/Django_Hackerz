# Guide d'utilisation du générateur de collections Postman

Ce script Python permet de générer des collections Postman adaptables à différents environnements pour l'API Hackerz. Contrairement au script précédent, ce générateur est beaucoup plus flexible et permet de personnaliser facilement l'URL de base, le token, et d'autres paramètres.

## Utilisation basique

Pour générer une collection avec les paramètres par défaut :

```bash
python api/postman_generator.py
```

Cela va créer un dossier `postman_export_YYYYMMDD_HHMMSS` contenant deux fichiers :
- `collection.json` : La collection Postman avec toutes les requêtes
- `environment.json` : L'environnement Postman avec les variables configurables

## Options disponibles

Le script accepte plusieurs options pour personnaliser la génération :

```bash
python api/postman_generator.py --base-url "https://api.example.com" --token "votre_token" --output-dir "mon_dossier" --collection-name "Ma Collection API"
```

### Options détaillées

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `--base-url` | URL de base de l'API | http://127.0.0.1:8000/api/v1 |
| `--token` | Token d'authentification | (vide) |
| `--output-dir` | Dossier de sortie | postman_export_YYYYMMDD_HHMMSS |
| `--collection-name` | Nom de la collection | Hackerz API |

## Exemples d'utilisation

### Exemple 1 : Générer pour un environnement local

```bash
python api/postman_generator.py --token "2e5db3dfc70de80265cda1aad05cf7f0dad7fffd"
```

### Exemple 2 : Générer pour un environnement de développement distant

```bash
python api/postman_generator.py --base-url "https://dev-api.hackerz.com/api/v1" --token "votre_token_dev" --collection-name "Hackerz API (Dev)"
```

### Exemple 3 : Générer pour un environnement de production

```bash
python api/postman_generator.py --base-url "https://api.hackerz.com/api/v1" --token "votre_token_prod" --collection-name "Hackerz API (Production)" --output-dir "postman_prod"
```

## Importer dans Postman

1. Ouvrez Postman
2. Cliquez sur "Import" dans le coin supérieur gauche
3. Sélectionnez les fichiers générés (collection.json et environment.json)
4. Après l'importation, assurez-vous de sélectionner l'environnement dans le menu déroulant en haut à droite

## Personnalisation avancée

Si vous souhaitez personnaliser les endpoints ou ajouter de nouveaux endpoints, vous pouvez modifier la fonction `define_default_api_structure()` dans le script Python. Cette fonction définit tous les endpoints disponibles dans la collection.

### Structure d'un endpoint

```python
{
    "name": "Nom de la requête",
    "method": "GET",  # ou POST, PUT, DELETE, etc.
    "path": "/chemin/de/endpoint/",
    "description": "Description de l'endpoint",
    "auth_required": True,  # True si l'authentification est nécessaire
    "params": {
        "param1": "Description du paramètre 1",
        "param2": "Description du paramètre 2"
    },
    "body": {
        "field1": "value1",
        "field2": "value2"
    },
    "tests": [
        "pm.test(\"Test name\", function() {",
        "    pm.response.to.have.status(200);",
        "});"
    ]
}
```

## Fonctionnalités

Le générateur offre plusieurs fonctionnalités avancées :

1. **Organisation par catégories** : Les endpoints sont automatiquement organisés en dossiers selon leur chemin
2. **Authentification automatique** : Les requêtes sont préconfigurées avec le token
3. **Exemples de réponses** : Des exemples de réponses peuvent être inclus pour chaque requête
4. **Tests automatisés** : Des scripts de test peuvent être ajoutés pour valider les réponses
5. **Paramètres de requête** : Les paramètres sont documentés et préconfigurés
6. **Descriptions détaillées** : Chaque requête inclut une description claire de son utilité

## Dépannage

Si vous rencontrez des problèmes lors de l'utilisation des collections générées :

1. **Variables non résolues** : Assurez-vous que l'environnement est bien sélectionné dans Postman
2. **Erreur d'authentification** : Vérifiez que le token est valide et correctement configuré
3. **URL inaccessible** : Vérifiez que l'URL de base est correcte et que le serveur est accessible

## Personnalisation des variables d'environnement

Si vous avez besoin d'ajouter des variables d'environnement supplémentaires, vous pouvez modifier la fonction `define_environment_variables()` dans le script.

## Conclusion

Ce générateur facilite grandement la création et la maintenance de collections Postman pour différents environnements. En utilisant ce script, vous pourrez rapidement générer des collections adaptées à vos besoins spécifiques. 