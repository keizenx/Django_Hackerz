#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import uuid
import argparse
from datetime import datetime

def create_collection(name, description, base_url, endpoints):
    """
    Crée une collection Postman complète
    
    Args:
        name: Nom de la collection
        description: Description de la collection
        base_url: URL de base de l'API (sans variables)
        endpoints: Liste des endpoints à inclure
        
    Returns:
        Un dictionnaire représentant la collection Postman
    """
    collection = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    # Organiser par dossiers
    categories = {}
    
    for endpoint in endpoints:
        # Extraire la catégorie du chemin
        path_parts = endpoint["path"].split("/")
        if len(path_parts) > 1 and path_parts[0] == "":
            category = path_parts[1]
        else:
            category = "Général"
            
        if category not in categories:
            categories[category] = []
            
        # Construire l'URL complète
        if endpoint["path"].startswith("/"):
            url = f"{{{{base_url}}}}{endpoint['path']}"
        else:
            url = f"{{{{base_url}}}}/{endpoint['path']}"
            
        # Créer la requête Postman
        request = {
            "name": endpoint["name"],
            "request": {
                "method": endpoint["method"],
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "url": {
                    "raw": url,
                    "host": ["{{base_url}}"],
                    "path": [p for p in endpoint["path"].split("/") if p]
                },
                "description": endpoint.get("description", "")
            },
            "response": []
        }
        
        # Ajouter l'authentification si nécessaire
        if endpoint.get("auth_required", False):
            request["request"]["header"].append({
                "key": "Authorization",
                "value": "{{auth_prefix}} {{token}}",
                "type": "text"
            })
            
        # Ajouter les paramètres de requête si nécessaire
        if endpoint.get("params"):
            request["request"]["url"]["query"] = []
            for param_name, param_desc in endpoint["params"].items():
                request["request"]["url"]["query"].append({
                    "key": param_name,
                    "value": "",
                    "description": param_desc,
                    "disabled": True
                })
                
        # Ajouter le body si nécessaire
        if endpoint.get("body"):
            request["request"]["body"] = {
                "mode": "raw",
                "raw": json.dumps(endpoint["body"], indent=2),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }
            
        # Ajouter des exemples de réponse si disponibles
        if endpoint.get("response_examples"):
            for example in endpoint["response_examples"]:
                response_example = {
                    "name": example.get("name", "Example Response"),
                    "originalRequest": {
                        "method": endpoint["method"],
                        "header": request["request"]["header"],
                        "url": {
                            "raw": url,
                            "host": ["{{base_url}}"],
                            "path": [p for p in endpoint["path"].split("/") if p]
                        }
                    },
                    "status": example.get("status", "OK"),
                    "code": example.get("code", 200),
                    "_postman_previewlanguage": "json",
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        }
                    ],
                    "cookie": [],
                    "body": json.dumps(example.get("body", {}), indent=2)
                }
                
                # Ajouter le body à la requête originale si nécessaire
                if endpoint.get("body"):
                    response_example["originalRequest"]["body"] = request["request"]["body"]
                    
                request["response"].append(response_example)
                
        # Ajouter des tests si nécessaire
        if endpoint.get("tests"):
            request["event"] = [
                {
                    "listen": "test",
                    "script": {
                        "exec": endpoint["tests"],
                        "type": "text/javascript"
                    }
                }
            ]
            
        categories[category].append(request)
        
    # Ajouter les dossiers de catégories à la collection
    for category, requests in categories.items():
        folder = {
            "name": category.capitalize(),
            "item": requests,
            "description": f"Endpoints relatifs à {category}"
        }
        collection["item"].append(folder)
        
    return collection

def create_environment(env_name, variables):
    """
    Crée un environnement Postman
    
    Args:
        env_name: Nom de l'environnement
        variables: Dictionnaire des variables d'environnement
        
    Returns:
        Un dictionnaire représentant l'environnement Postman
    """
    environment = {
        "id": str(uuid.uuid4()),
        "name": env_name,
        "values": [],
        "_postman_variable_scope": "environment"
    }
    
    for key, var_config in variables.items():
        env_var = {
            "key": key,
            "value": var_config.get("value", ""),
            "type": var_config.get("type", "default"),
            "enabled": var_config.get("enabled", True)
        }
        
        if var_config.get("description"):
            env_var["description"] = var_config["description"]
            
        environment["values"].append(env_var)
        
    return environment

def define_default_api_structure():
    """
    Définit une structure par défaut pour l'API Hackerz
    
    Returns:
        Tuple contenant (name, description, base_url, endpoints)
    """
    name = "Hackerz API"
    description = "Collection pour tester l'API Hackerz"
    base_url = "http://127.0.0.1:8000/api/v1"
    
    endpoints = [
        # Documentation
        {
            "name": "Documentation Swagger",
            "method": "GET",
            "path": "/swagger/",
            "description": "Documentation interactive de l'API avec Swagger UI"
        },
        {
            "name": "Documentation ReDoc",
            "method": "GET",
            "path": "/redoc/",
            "description": "Documentation de l'API avec ReDoc"
        },
        
        # Auth
        {
            "name": "Obtenir un token",
            "method": "POST",
            "path": "/token/",
            "description": "Obtenir un token d'authentification",
            "body": {
                "username": "admin",
                "password": "password123"
            },
            "response_examples": [
                {
                    "name": "Token Success",
                    "code": 200,
                    "body": {
                        "token": "votre_token_ici"
                    }
                }
            ],
            "tests": [
                "pm.test(\"Status code is 200\", function() {",
                "    pm.response.to.have.status(200);",
                "});",
                "",
                "pm.test(\"Token is present\", function() {",
                "    var jsonData = pm.response.json();",
                "    pm.expect(jsonData.token).to.exist;",
                "    pm.environment.set(\"token\", jsonData.token);",
                "});"
            ]
        },
        
        # Shop
        {
            "name": "Liste des catégories",
            "method": "GET",
            "path": "/shop/categories/",
            "description": "Récupérer la liste des catégories de produits",
            "auth_required": True,
            "params": {
                "page": "Numéro de page pour la pagination",
                "search": "Terme de recherche"
            }
        },
        {
            "name": "Détail d'une catégorie",
            "method": "GET",
            "path": "/shop/categories/1/",
            "description": "Récupérer les détails d'une catégorie spécifique",
            "auth_required": True
        },
        {
            "name": "Liste des produits",
            "method": "GET",
            "path": "/shop/products/",
            "description": "Récupérer la liste des produits",
            "auth_required": True,
            "params": {
                "page": "Numéro de page pour la pagination",
                "search": "Terme de recherche",
                "category": "ID de la catégorie pour filtrer",
                "min_price": "Prix minimum",
                "max_price": "Prix maximum"
            }
        },
        {
            "name": "Détail d'un produit",
            "method": "GET",
            "path": "/shop/products/1/",
            "description": "Récupérer les détails d'un produit spécifique",
            "auth_required": True
        },
        {
            "name": "Créer un produit",
            "method": "POST",
            "path": "/shop/products/",
            "description": "Créer un nouveau produit",
            "auth_required": True,
            "body": {
                "name": "Nouveau produit",
                "category_id": 1,
                "price": 99.99,
                "stock": 10,
                "slug": "nouveau-produit",
                "description": "Description du nouveau produit"
            }
        },
        {
            "name": "Mettre à jour un produit",
            "method": "PUT",
            "path": "/shop/products/1/",
            "description": "Mettre à jour un produit existant",
            "auth_required": True,
            "body": {
                "name": "Produit mis à jour",
                "category_id": 1,
                "price": 129.99,
                "stock": 15,
                "slug": "produit-mis-a-jour",
                "description": "Description mise à jour"
            }
        },
        {
            "name": "Supprimer un produit",
            "method": "DELETE",
            "path": "/shop/products/1/",
            "description": "Supprimer un produit",
            "auth_required": True
        },
        {
            "name": "Liste des avis",
            "method": "GET",
            "path": "/shop/reviews/",
            "description": "Récupérer la liste des avis",
            "auth_required": True
        },
        {
            "name": "Avis par produit",
            "method": "GET",
            "path": "/shop/reviews/by_product/",
            "description": "Récupérer les avis pour un produit spécifique",
            "auth_required": True,
            "params": {
                "product_id": "ID du produit"
            }
        },
        
        # Blog
        {
            "name": "Liste des catégories de blog",
            "method": "GET",
            "path": "/blog/categories/",
            "description": "Récupérer la liste des catégories d'articles",
            "auth_required": True
        },
        {
            "name": "Liste des articles",
            "method": "GET",
            "path": "/blog/posts/",
            "description": "Récupérer la liste des articles",
            "auth_required": True,
            "params": {
                "page": "Numéro de page pour la pagination",
                "search": "Terme de recherche",
                "category": "ID de la catégorie pour filtrer"
            }
        },
        {
            "name": "Détail d'un article",
            "method": "GET",
            "path": "/blog/posts/1/",
            "description": "Récupérer les détails d'un article spécifique",
            "auth_required": True
        },
        {
            "name": "Liste des commentaires",
            "method": "GET",
            "path": "/blog/comments/",
            "description": "Récupérer la liste des commentaires",
            "auth_required": True
        },
        {
            "name": "Commentaires par article",
            "method": "GET",
            "path": "/blog/comments/by_post/",
            "description": "Récupérer les commentaires pour un article spécifique",
            "auth_required": True,
            "params": {
                "post_id": "ID de l'article"
            }
        },
        {
            "name": "Créer un commentaire",
            "method": "POST",
            "path": "/blog/comments/",
            "description": "Créer un nouveau commentaire",
            "auth_required": True,
            "body": {
                "post": 1,
                "body": "Contenu du commentaire"
            }
        },
        
        # Projects
        {
            "name": "Liste des catégories de projets",
            "method": "GET",
            "path": "/projects/categories/",
            "description": "Récupérer la liste des catégories de projets",
            "auth_required": True
        },
        {
            "name": "Liste des projets",
            "method": "GET",
            "path": "/projects/",
            "description": "Récupérer la liste des projets",
            "auth_required": True,
            "params": {
                "page": "Numéro de page pour la pagination",
                "search": "Terme de recherche",
                "category": "ID de la catégorie pour filtrer"
            }
        },
        {
            "name": "Détail d'un projet",
            "method": "GET",
            "path": "/projects/1/",
            "description": "Récupérer les détails d'un projet spécifique",
            "auth_required": True
        }
    ]
    
    return name, description, base_url, endpoints

def define_environment_variables(base_url, token=None):
    """
    Définit les variables d'environnement par défaut
    
    Args:
        base_url: URL de base
        token: Token d'authentification (optionnel)
        
    Returns:
        Un dictionnaire des variables d'environnement
    """
    variables = {
        "base_url": {
            "value": base_url,
            "type": "default",
            "description": "URL de base de l'API"
        },
        "auth_prefix": {
            "value": "Token",
            "type": "default",
            "description": "Préfixe d'authentification (Token, Bearer, etc.)"
        }
    }
    
    if token:
        variables["token"] = {
            "value": token,
            "type": "secret",
            "description": "Token d'authentification"
        }
    else:
        variables["token"] = {
            "value": "",
            "type": "secret",
            "description": "Token d'authentification (à remplir)"
        }
        
    return variables

def save_to_file(data, filename):
    """
    Sauvegarde des données au format JSON dans un fichier
    
    Args:
        data: Données à sauvegarder
        filename: Nom du fichier
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Fichier sauvegardé: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Générateur de collection Postman pour l'API Hackerz")
    parser.add_argument("--base-url", dest="base_url", default="http://127.0.0.1:8000/api/v1",
                        help="URL de base de l'API (par défaut: http://127.0.0.1:8000/api/v1)")
    parser.add_argument("--token", dest="token", default=None,
                        help="Token d'authentification (optionnel)")
    parser.add_argument("--output-dir", dest="output_dir", default=None,
                        help="Dossier de sortie (par défaut: postman_export_DATE)")
    parser.add_argument("--collection-name", dest="collection_name", default=None,
                        help="Nom de la collection (par défaut: Hackerz API)")
    
    args = parser.parse_args()
    
    # Définir la structure de l'API
    name, description, default_base_url, endpoints = define_default_api_structure()
    
    # Utiliser les valeurs fournies ou les valeurs par défaut
    base_url = args.base_url or default_base_url
    collection_name = args.collection_name or name
    
    # Créer la collection
    collection = create_collection(collection_name, description, base_url, endpoints)
    
    # Créer l'environnement
    environment = create_environment(
        f"{collection_name} Environment",
        define_environment_variables(base_url, args.token)
    )
    
    # Créer le dossier de sortie
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = args.output_dir or f"postman_export_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder les fichiers
    save_to_file(collection, f"{output_dir}/collection.json")
    save_to_file(environment, f"{output_dir}/environment.json")
    
    print(f"\nFichiers générés dans: {output_dir}")
    print("\nComment utiliser ces fichiers:")
    print("1. Ouvrez Postman")
    print("2. Importez l'environnement depuis: " + f"{output_dir}/environment.json")
    print("3. Importez la collection depuis: " + f"{output_dir}/collection.json")
    print("4. Sélectionnez l'environnement dans le menu déroulant en haut à droite")
    print("5. Utilisez les requêtes préconfigurées dans la collection")
    
    if not args.token:
        print("\nNote: Aucun token n'a été fourni. Vous devrez obtenir un token en utilisant la requête 'Obtenir un token'.")

if __name__ == "__main__":
    main() 