// Fonction pour ajouter un commentaire via AJAX
function addComment(postSlug, commentBody) {
    fetch(`/blog/add-comment/${postSlug}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ body: commentBody })
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
                throw new Error(data.message || 'Erreur lors de l\'ajout du commentaire');
            });
        }
    })
    .then(data => {
        // Afficher un message de succès
        showToast('Succès', 'Votre commentaire a été ajouté avec succès.', 'success');
        
        // Ajouter le commentaire à la liste ou recharger la page
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
    // Gérer le formulaire de commentaire AJAX
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const postSlug = window.location.pathname.split('/').filter(Boolean).pop();
            const commentBody = document.getElementById('comment-body').value.trim();
            
            if (!commentBody) {
                showToast('Erreur', 'Le commentaire ne peut pas être vide.', 'danger');
                return;
            }
            
            addComment(postSlug, commentBody);
        });
    }
}); 