 # Django Hackerz

Une plateforme e-commerce et blog sécurisée développée avec Django.

## 🚀 Fonctionnalités

### E-commerce
- Système de panier d'achat
- Gestion des produits par catégories
- Interface vendeur
- Système d'avis et de notation
- Processus de paiement sécurisé
- Gestion des commandes

### Blog
- Articles avec système de catégories et tags
- Commentaires et réponses
- Formatage riche du contenu
- Interface d'administration

### Sécurité
- Authentification utilisateur
- Gestion des rôles (admin, vendeur, client)
- Protection contre les attaques CSRF
- Validation des données

## 🛠️ Technologies

- Python 3.x
- Django
- SQLite (base de données)
- HTML/CSS/JavaScript
- Bootstrap Icons

## 📦 Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/keizenx/Django_Hackerz.git
cd Django_Hackerz
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Effectuez les migrations :
```bash
python manage.py migrate
```

5. Créez un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancez le serveur :
```bash
python manage.py runserver
```

## 🔐 Configuration

1. Créez un fichier `.env` à la racine du projet
2. Ajoutez les variables d'environnement nécessaires :
```env
SECRET_KEY=votre_clé_secrète
DEBUG=True
```

## 👥 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📧 Contact

- Auteur : keizenx
- GitHub : [@keizenx](https://github.com/keizenx)