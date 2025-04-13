import requests
import json
import os
from datetime import datetime
import uuid

# Configuration de l'API
BASE_URL = "http://127.0.0.1:8000/api/v1"
API_TOKEN = "2e5db3dfc70de80265cda1aad05cf7f0dad7fffd"  # Token de l'utilisateur

# Configuration SMTP
SMTP_CONFIG = {
    "EMAIL": "franckbcours99@gmail.com",
    "PASSWORD": "ialr jrtb slao urik",
    "HOST": "smtp.gmail.com",
    "PORT": 587
}

# En-têtes pour l'authentification
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

# Définition des endpoints à tester
ENDPOINTS = [
    # Documentation
    {"name": "Documentation Swagger", "method": "GET", "path": "/swagger/"},
    {"name": "Documentation ReDoc", "method": "GET", "path": "/redoc/"},
    
    # Auth
    {"name": "Auth Token", "method": "POST", "path": "/token/", "body": {"username": "franck", "password": "votre_mot_de_passe"}},
    
    # Shop
    {"name": "Liste des catégories", "method": "GET", "path": "/shop/categories/"},
    {"name": "Liste des produits", "method": "GET", "path": "/shop/products/"},
    {"name": "Détail d'un produit", "method": "GET", "path": "/shop/products/1/"},
    {"name": "Liste des avis", "method": "GET", "path": "/shop/reviews/"},
    {"name": "Avis par produit", "method": "GET", "path": "/shop/reviews/by_product/?product_id=1"},
    
    # Blog
    {"name": "Liste des catégories de blog", "method": "GET", "path": "/blog/categories/"},
    {"name": "Liste des articles", "method": "GET", "path": "/blog/posts/"},
    {"name": "Liste des commentaires", "method": "GET", "path": "/blog/comments/"},
    {"name": "Commentaires par article", "method": "GET", "path": "/blog/comments/by_post/?post_id=1"},
    
    # Projets
    {"name": "Liste des catégories de projets", "method": "GET", "path": "/projects/categories/"},
    {"name": "Liste des projets", "method": "GET", "path": "/projects/"},
    
    # Exemples d'opérations de création (POST)
    {"name": "Créer un produit", "method": "POST", "path": "/shop/products/", 
     "body": {
         "name": "Produit test via script",
         "category_id": 2,
         "price": 99.99,
         "stock": 10,
         "slug": "produit-test-script",
         "description": "Produit créé via script Python"
     }
    },
    {"name": "Créer un commentaire", "method": "POST", "path": "/blog/comments/", 
     "body": {
         "post": 1,
         "body": "Commentaire créé via script Python"
     }
    }
]

def test_endpoint(endpoint):
    url = f"{BASE_URL}{endpoint['path']}"
    print(f"Testing: {endpoint['method']} {url}")
    
    try:
        if endpoint['method'] == "GET":
            response = requests.get(url, headers=HEADERS)
        elif endpoint['method'] == "POST":
            response = requests.post(url, headers=HEADERS, json=endpoint.get('body'))
        elif endpoint['method'] == "PUT":
            response = requests.put(url, headers=HEADERS, json=endpoint.get('body'))
        elif endpoint['method'] == "PATCH":
            response = requests.patch(url, headers=HEADERS, json=endpoint.get('body'))
        elif endpoint['method'] == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        else:
            print(f"Méthode non supportée: {endpoint['method']}")
            return None
        
        # Vérifier si la requête a réussi
        if response.status_code < 400:
            print(f"SUCCESS: {response.status_code}")
            
            # Essayer de parser la réponse comme du JSON
            response_data = None
            if response.content:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    # Si ce n'est pas du JSON, stocker la réponse comme du texte
                    # mais seulement les 500 premiers caractères pour éviter les réponses trop longues
                    response_text = response.text[:500]
                    if len(response.text) > 500:
                        response_text += "... [truncated]"
                    response_data = {"text_response": response_text}
                    print(f"Response is not JSON, storing first 500 chars as text")
            
            return {
                "name": endpoint['name'],
                "method": endpoint['method'],
                "url": url,
                "status": response.status_code,
                "body": endpoint.get('body'),
                "response": response_data,
                "content_type": response.headers.get('Content-Type', '')
            }
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            return {
                "name": endpoint['name'],
                "method": endpoint['method'],
                "url": url,
                "status": response.status_code,
                "body": endpoint.get('body'),
                "error": response.text,
                "content_type": response.headers.get('Content-Type', '')
            }
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        return {
            "name": endpoint['name'],
            "method": endpoint['method'],
            "url": url,
            "body": endpoint.get('body'),
            "error": str(e)
        }

def generate_postman_collection(results):
    collection = {
        "info": {
            "name": "Hackerz API",
            "_postman_id": str(uuid.uuid4()),
            "description": "Collection pour tester l'API Hackerz",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    # Organiser les résultats par catégorie
    categories = {}
    for result in results:
        if not result:
            continue
            
        # Extraire la catégorie du chemin
        path_parts = result['url'].replace(BASE_URL, '').split('/')
        if len(path_parts) > 1:
            category = path_parts[1]
        else:
            category = "Autre"
        
        if category not in categories:
            categories[category] = []
        
        # Créer une copie du résultat sans inclure la réponse
        # pour éviter les références circulaires
        request_copy = {k: v for k, v in result.items() if k != 'response' and k != 'error'}
        
        # Créer la requête Postman
        postman_request = {
            "name": result['name'],
            "request": {
                "method": result['method'],
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    },
                    {
                        "key": "Authorization",
                        "value": "{{token}}"
                    }
                ],
                "url": {
                    "raw": result['url'],
                    "host": ["{{base_url}}"],
                    "path": result['url'].replace(BASE_URL, '').split('/')[1:]
                }
            },
            "response": []
        }
        
        # Ajouter le body si nécessaire
        if result.get('body'):
            postman_request["request"]["body"] = {
                "mode": "raw",
                "raw": json.dumps(result['body'], indent=2),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }
        
        # Ajouter une réponse d'exemple si disponible
        if result.get('response') or result.get('error'):
            response_example = {
                "name": f"Example Response {result.get('status', 'Error')}",
                "originalRequest": {
                    "method": result['method'],
                    "header": postman_request["request"]["header"],
                    "url": postman_request["request"]["url"].copy(),
                }
            }
            
            # Ajouter le body à la requête originale si nécessaire
            if result.get('body'):
                response_example["originalRequest"]["body"] = postman_request["request"]["body"].copy()
            
            # Ajouter les détails de la réponse
            if result.get('status'):
                response_example["status"] = "OK"
                response_example["code"] = result['status']
                
                # Déterminer le type de contenu
                content_type = result.get('content_type', 'application/json')
                response_example["header"] = [
                    {
                        "key": "Content-Type",
                        "value": content_type
                    }
                ]
                
                # Ajouter le corps de la réponse
                if result.get('response'):
                    response_example["body"] = json.dumps(result['response'], indent=2)
                elif result.get('error'):
                    response_example["body"] = result['error']
            
            postman_request["response"].append(response_example)
        
        categories[category].append(postman_request)
    
    # Ajouter les dossiers de catégories à la collection
    for category, requests in categories.items():
        folder = {
            "name": category.capitalize(),
            "item": requests
        }
        collection["item"].append(folder)
    
    return collection

def create_environment():
    return {
        "name": "Hackerz API Environment",
        "values": [
            {
                "key": "base_url",
                "value": BASE_URL,
                "type": "default",
                "enabled": True
            },
            {
                "key": "token",
                "value": API_TOKEN,
                "type": "secret",
                "enabled": True
            }
        ]
    }

if __name__ == "__main__":
    # Créer un dossier pour les exports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = f"postman_export_{timestamp}"
    os.makedirs(export_dir, exist_ok=True)
    
    # Tester les endpoints
    results = []
    for endpoint in ENDPOINTS:
        result = test_endpoint(endpoint)
        if result:
            results.append(result)
    
    # Générer la collection Postman
    collection = generate_postman_collection(results)
    
    # Générer l'environnement Postman
    environment = create_environment()
    
    # Sauvegarder les fichiers
    with open(f"{export_dir}/hackerz_collection.json", "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)
    
    with open(f"{export_dir}/hackerz_environment.json", "w", encoding="utf-8") as f:
        json.dump(environment, f, indent=2)
    
    # Sauvegarder les résultats bruts pour référence
    with open(f"{export_dir}/api_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nExportation terminée ! Fichiers sauvegardés dans le dossier '{export_dir}'")
    print(f"Pour importer dans Postman:")
    print(f"1. Collection: {export_dir}/hackerz_collection.json")
    print(f"2. Environnement: {export_dir}/hackerz_environment.json") 