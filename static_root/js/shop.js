// Fonction pour ajouter un produit au panier via AJAX
function addToCart(productId, quantity = 1) {
    fetch(`/shop/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else if (response.status === 401) {
            // Utilisateur non connecté, rediriger vers la page de connexion
            return response.json().then(data => {
                showToast('Attention', data.message, 'warning');
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 2000);
                throw new Error('Redirection vers connexion');
            });
        } else {
            throw new Error('Erreur lors de l\'ajout au panier');
        }
    })
    .then(data => {
        // Mettre à jour le nombre d'articles dans le panier
        updateCartCount(data.cart_count);
        
        // Afficher un message de succès
        showToast('Succès', data.message, 'success');
    })
    .catch(error => {
        if (error.message !== 'Redirection vers connexion') {
            showToast('Erreur', 'Une erreur est survenue lors de l\'ajout au panier.', 'danger');
            console.error('Erreur:', error);
        }
    });
}

// Fonction pour récupérer un cookie (pour le CSRF token)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fonction pour mettre à jour le compteur de panier
function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
        
        // Animation pour attirer l'attention
        element.classList.add('cart-count-updated');
        setTimeout(() => {
            element.classList.remove('cart-count-updated');
        }, 1000);
    });
}

// Fonction pour afficher un toast (notification)
function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast show toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Ajouter le toast à la fin du body
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
        toastContainer.appendChild(toast);
    } else {
        const newContainer = document.createElement('div');
        newContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        newContainer.style.zIndex = '5';
        newContainer.appendChild(toast);
        document.body.appendChild(newContainer);
    }
    
    // Fermer automatiquement après 5 secondes
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, 5000);
    
    // Gestion du bouton de fermeture
    const closeButton = toast.querySelector('.btn-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 500);
        });
    }
}

// Gestionnaire d'événement au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Gérer les boutons "Ajouter au panier"
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const quantityInput = document.querySelector(`#quantity-${productId}`);
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
            
            addToCart(productId, quantity);
        });
    });
    
    // Gérer le bouton "Acheter maintenant"
    const buyNowButtons = document.querySelectorAll('.buy-now-btn');
    buyNowButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const quantityInput = document.querySelector(`#quantity-${productId}`);
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
            
            // Ajouter au panier puis rediriger vers la page de paiement
            fetch(`/shop/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else if (response.status === 401) {
                    // Utilisateur non connecté, rediriger vers la page de connexion
                    return response.json().then(data => {
                        showToast('Attention', data.message, 'warning');
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 2000);
                        throw new Error('Redirection vers connexion');
                    });
                } else {
                    throw new Error('Erreur lors de l\'ajout au panier');
                }
            })
            .then(data => {
                // Rediriger vers la page de paiement
                window.location.href = '/shop/checkout/';
            })
            .catch(error => {
                if (error.message !== 'Redirection vers connexion') {
                    showToast('Erreur', 'Une erreur est survenue.', 'danger');
                    console.error('Erreur:', error);
                }
            });
        });
    });
    
    // Gérer le formulaire d'avis sur la page de détail du produit
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        // Gestion des étoiles pour la notation
        const stars = document.querySelectorAll('.rating-stars .fa-star');
        const ratingInput = document.getElementById('rating');
        
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = this.getAttribute('data-rating');
                ratingInput.value = rating;
                
                // Mettre à jour l'apparence des étoiles
                stars.forEach(s => {
                    if (s.getAttribute('data-rating') <= rating) {
                        s.classList.add('text-warning');
                    } else {
                        s.classList.remove('text-warning');
                    }
                });
            });
        });
        
        // Soumission du formulaire d'avis
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const productId = this.action.split('/').filter(Boolean).pop();
            const rating = document.getElementById('rating').value;
            const title = document.getElementById('title').value;
            const comment = document.getElementById('comment').value;
            
            if (!rating || rating < 1) {
                showToast('Erreur', 'Veuillez sélectionner une note.', 'danger');
                return;
            }
            
            if (!title.trim()) {
                showToast('Erreur', 'Veuillez entrer un titre.', 'danger');
                return;
            }
            
            if (!comment.trim()) {
                showToast('Erreur', 'Veuillez entrer un commentaire.', 'danger');
                return;
            }
            
            fetch(`/shop/add-review/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    rating: rating,
                    title: title,
                    comment: comment
                })
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else if (response.status === 401) {
                    // Utilisateur non connecté, rediriger vers la page de connexion
                    return response.json().then(data => {
                        showToast('Attention', data.message, 'warning');
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 2000);
                        throw new Error('Redirection vers connexion');
                    });
                } else {
                    return response.json().then(data => {
                        throw new Error(data.message || 'Erreur lors de l\'ajout de l\'avis');
                    });
                }
            })
            .then(data => {
                showToast('Succès', data.message, 'success');
                
                // Réinitialiser le formulaire
                reviewForm.reset();
                stars.forEach(s => s.classList.remove('text-warning'));
                
                // Recharger la page pour afficher le nouvel avis
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            })
            .catch(error => {
                if (error.message !== 'Redirection vers connexion') {
                    showToast('Erreur', error.message, 'danger');
                    console.error('Erreur:', error);
                }
            });
        });
    }
}); 