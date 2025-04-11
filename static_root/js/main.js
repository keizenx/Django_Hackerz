// Toggle mobile menu
document.addEventListener('DOMContentLoaded', function() {
  const navbarToggle = document.querySelector('.navbar-toggle');
  const navbarMenu = document.querySelector('.navbar-menu');
  
  if (navbarToggle && navbarMenu) {
    navbarToggle.addEventListener('click', function() {
      navbarMenu.classList.toggle('show');
    });
  }
  
  // Toast notifications
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.classList.add(`toast-${type}`);
    toast.innerHTML = `
      <div class="toast-content">
        <span>${message}</span>
      </div>
    `;
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => {
      toast.classList.add('show');
    }, 100);
    
    // Hide toast after 3 seconds
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  }
  
  // Add to cart functionality
  const addToCartButtons = document.querySelectorAll('.add-to-cart-btn, .card-btn');
  addToCartButtons.forEach(button => {
    button.addEventListener('click', function() {
      showToast('Produit ajouté au panier!');
    });
  });
  
  // Quantity buttons
  const quantityBtns = document.querySelectorAll('.quantity-btn');
  quantityBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const input = this.parentElement.querySelector('.quantity-input');
      const currentValue = parseInt(input.value);
      
      if (this.textContent === '+') {
        input.value = currentValue + 1;
      } else if (this.textContent === '-' && currentValue > 1) {
        input.value = currentValue - 1;
      }
    });
  });
  
  // Form submissions
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Get form ID or class to determine what type of form was submitted
      if (form.id === 'login-form' || form.classList.contains('login-form')) {
        showToast('Connexion réussie!');
        // In a real app, you'd redirect here after successful login
        // window.location.href = 'profile.html';
      } else if (form.id === 'register-form' || form.classList.contains('register-form')) {
        showToast('Inscription réussie!');
        // In a real app, you'd redirect here after successful registration
        // window.location.href = 'login.html';
      } else if (form.id === 'contact-form' || form.classList.contains('contact-form')) {
        showToast('Message envoyé!');
        form.reset();
      }
    });
  });
  
  // Filter functionality
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      // Toggle filter options
      const targetId = this.getAttribute('data-target');
      if (targetId) {
        const filterOptions = document.getElementById(targetId);
        if (filterOptions) {
          filterOptions.classList.toggle('hidden');
        }
      }
      
      // Toggle active state for sort buttons
      if (this.classList.contains('sort-btn')) {
        document.querySelectorAll('.sort-btn').forEach(btn => {
          btn.classList.remove('active');
        });
        this.classList.add('active');
      }
    });
  });
  
  // Tag filtering
  const tags = document.querySelectorAll('.tag');
  tags.forEach(tag => {
    tag.addEventListener('click', function() {
      this.classList.toggle('active');
      
      // In a real app, you'd filter the displayed items here
      // For demo purposes, we'll just show a toast
      showToast('Filtres appliqués!');
    });
  });
  
  // Search functionality
  const searchInputs = document.querySelectorAll('.search-input');
  searchInputs.forEach(input => {
    input.addEventListener('keyup', function(e) {
      if (e.key === 'Enter') {
        showToast(`Recherche pour: ${this.value}`);
      }
    });
  });
  
  // Fermer le menu en cliquant ailleurs
  document.addEventListener('click', function(event) {
    if (navbarMenu && navbarMenu.classList.contains('active') && !event.target.closest('.navbar-container')) {
      navbarMenu.classList.remove('active');
    }
  });
  
  // Ajouter la gestion du lien de connexion pour afficher une modal AJAX
  const loginLink = document.getElementById('login-link');
  
  if (loginLink) {
    loginLink.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Vérifier si la modal existe déjà
      let loginModal = document.getElementById('login-modal');
      
      // Si la modal n'existe pas, la créer
      if (!loginModal) {
        loginModal = document.createElement('div');
        loginModal.id = 'login-modal';
        loginModal.className = 'modal';
        loginModal.style.display = 'none';
        loginModal.style.position = 'fixed';
        loginModal.style.top = '0';
        loginModal.style.left = '0';
        loginModal.style.width = '100%';
        loginModal.style.height = '100%';
        loginModal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        loginModal.style.zIndex = '1000';
        loginModal.style.justifyContent = 'center';
        loginModal.style.alignItems = 'center';
        
        // Contenu de la modal
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.backgroundColor = 'hsl(240, 3.7%, 10%)';
        modalContent.style.padding = '2rem';
        modalContent.style.borderRadius = '0.5rem';
        modalContent.style.width = '90%';
        modalContent.style.maxWidth = '400px';
        modalContent.style.position = 'relative';
        
        // Bouton de fermeture
        const closeButton = document.createElement('span');
        closeButton.className = 'close-modal';
        closeButton.innerHTML = '&times;';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '1rem';
        closeButton.style.right = '1rem';
        closeButton.style.fontSize = '1.5rem';
        closeButton.style.cursor = 'pointer';
        closeButton.style.color = 'hsl(240, 5%, 64.9%)';
        
        // Titre
        const title = document.createElement('div');
        title.style.textAlign = 'center';
        title.style.marginBottom = '2rem';
        title.innerHTML = '<h2 style="font-size: 2rem; margin-bottom: 0.5rem;"><span style="color: hsl(142, 100%, 50%);">C</span>onnexion</h2><p style="color: hsl(240, 5%, 64.9%);">Accédez à votre compte Hackerz</p>';
        
        // Formulaire (à charger via AJAX)
        const formContainer = document.createElement('div');
        formContainer.id = 'login-form-container';
        
        // Loader
        const loader = document.createElement('div');
        loader.className = 'loader';
        loader.style.textAlign = 'center';
        loader.style.padding = '2rem';
        loader.innerHTML = 'Chargement...';
        
        // Assembler la modal
        formContainer.appendChild(loader);
        modalContent.appendChild(closeButton);
        modalContent.appendChild(title);
        modalContent.appendChild(formContainer);
        loginModal.appendChild(modalContent);
        
        // Ajouter la modal au document
        document.body.appendChild(loginModal);
        
        // Gestion de la fermeture
        closeButton.addEventListener('click', function() {
          loginModal.style.display = 'none';
        });
        
        // Fermer en cliquant à l'extérieur
        loginModal.addEventListener('click', function(event) {
          if (event.target === loginModal) {
            loginModal.style.display = 'none';
          }
        });
        
        // Fermer avec Escape
        document.addEventListener('keydown', function(event) {
          if (event.key === 'Escape' && loginModal.style.display === 'flex') {
            loginModal.style.display = 'none';
          }
        });
      }
      
      // Afficher la modal
      loginModal.style.display = 'flex';
      
      // Charger le formulaire via AJAX
      const formContainer = document.getElementById('login-form-container');
      formContainer.innerHTML = '<div class="loader" style="text-align: center; padding: 2rem;">Chargement...</div>';
      
      // Requête AJAX pour récupérer le formulaire
      fetch('/login/', {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Erreur lors du chargement du formulaire');
        }
        return response.json();
      })
      .then(data => {
        if (data.html) {
          formContainer.innerHTML = '';
          
          // Créer le formulaire
          const form = document.createElement('form');
          form.id = 'ajax-login-form';
          form.method = 'post';
          form.action = '/login/';
          form.className = 'form';
          form.innerHTML = data.html;
          
          formContainer.appendChild(form);
          
          // Ajouter l'événement de soumission
          setupLoginFormSubmit(form);
        }
      })
      .catch(error => {
        console.error('Erreur:', error);
        formContainer.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement du formulaire. Veuillez réessayer.</div>';
      });
    });
  }
  
  // Fonction pour configurer la soumission du formulaire
  function setupLoginFormSubmit(form) {
    // Gérer le lien "mot de passe oublié"
    const forgotPasswordLink = form.querySelector('a[href*="password-reset"]');
    if (forgotPasswordLink) {
      forgotPasswordLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Fermer la modale de connexion
        const loginModal = document.getElementById('login-modal');
        if (loginModal) {
          loginModal.style.display = 'none';
        }
        
        // Créer la modale de réinitialisation de mot de passe
        let resetModal = document.getElementById('reset-password-modal');
        
        if (!resetModal) {
          resetModal = document.createElement('div');
          resetModal.id = 'reset-password-modal';
          resetModal.className = 'modal';
          resetModal.style.display = 'none';
          resetModal.style.position = 'fixed';
          resetModal.style.top = '0';
          resetModal.style.left = '0';
          resetModal.style.width = '100%';
          resetModal.style.height = '100%';
          resetModal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
          resetModal.style.zIndex = '1000';
          resetModal.style.justifyContent = 'center';
          resetModal.style.alignItems = 'center';
          
          // Contenu de la modal
          const modalContent = document.createElement('div');
          modalContent.className = 'modal-content';
          modalContent.style.backgroundColor = 'hsl(240, 3.7%, 10%)';
          modalContent.style.padding = '2rem';
          modalContent.style.borderRadius = '0.5rem';
          modalContent.style.width = '90%';
          modalContent.style.maxWidth = '400px';
          modalContent.style.position = 'relative';
          
          // Bouton de fermeture
          const closeButton = document.createElement('span');
          closeButton.className = 'close-modal';
          closeButton.innerHTML = '&times;';
          closeButton.style.position = 'absolute';
          closeButton.style.top = '1rem';
          closeButton.style.right = '1rem';
          closeButton.style.fontSize = '1.5rem';
          closeButton.style.cursor = 'pointer';
          closeButton.style.color = 'hsl(240, 5%, 64.9%)';
          
          // Titre
          const title = document.createElement('div');
          title.style.textAlign = 'center';
          title.style.marginBottom = '2rem';
          title.innerHTML = '<h2 style="font-size: 2rem; margin-bottom: 0.5rem;"><span style="color: hsl(142, 100%, 50%);">R</span>éinitialisation</h2><p style="color: hsl(240, 5%, 64.9%);">Saisissez votre email pour recevoir un lien</p>';
          
          // Formulaire (à créer)
          const formContainer = document.createElement('div');
          formContainer.id = 'reset-form-container';
          
          // Créer le formulaire de réinitialisation
          const resetForm = document.createElement('form');
          resetForm.id = 'reset-password-form';
          resetForm.method = 'post';
          resetForm.action = '/password-reset/';
          resetForm.className = 'form';
          
          // CSRF token
          const csrfInput = document.createElement('input');
          csrfInput.type = 'hidden';
          csrfInput.name = 'csrfmiddlewaretoken';
          csrfInput.value = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
          resetForm.appendChild(csrfInput);
          
          // Email field
          const formGroup = document.createElement('div');
          formGroup.className = 'form-group';
          
          const label = document.createElement('label');
          label.htmlFor = 'id_email';
          label.className = 'form-label';
          label.textContent = 'Email';
          formGroup.appendChild(label);
          
          const inputContainer = document.createElement('div');
          inputContainer.style.position = 'relative';
          
          const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
          svg.setAttribute('style', 'position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); color: hsl(240, 5%, 64.9%);');
          svg.setAttribute('width', '18');
          svg.setAttribute('height', '18');
          svg.setAttribute('viewBox', '0 0 24 24');
          svg.setAttribute('fill', 'none');
          svg.setAttribute('stroke', 'currentColor');
          svg.setAttribute('stroke-width', '2');
          svg.setAttribute('stroke-linecap', 'round');
          svg.setAttribute('stroke-linejoin', 'round');
          
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttribute('d', 'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z');
          svg.appendChild(path);
          
          const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
          polyline.setAttribute('points', '22,6 12,13 2,6');
          svg.appendChild(polyline);
          
          inputContainer.appendChild(svg);
          
          const input = document.createElement('input');
          input.type = 'email';
          input.name = 'email';
          input.id = 'id_email';
          input.className = 'form-input';
          input.style.paddingLeft = '2.5rem';
          input.placeholder = 'votre@email.com';
          input.required = true;
          inputContainer.appendChild(input);
          
          formGroup.appendChild(inputContainer);
          resetForm.appendChild(formGroup);
          
          // Submit button
          const button = document.createElement('button');
          button.type = 'submit';
          button.className = 'form-btn';
          button.style.width = '100%';
          button.style.display = 'flex';
          button.style.alignItems = 'center';
          button.style.justifyContent = 'center';
          button.style.gap = '0.5rem';
          button.style.marginTop = '1.5rem';
          button.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            <span>Envoyer le lien</span>
          `;
          resetForm.appendChild(button);
          
          // Lien de retour
          const linkContainer = document.createElement('div');
          linkContainer.style.textAlign = 'center';
          linkContainer.style.marginTop = '1.5rem';
          
          const linkText = document.createElement('p');
          linkText.style.fontSize = '0.875rem';
          linkText.style.color = 'hsl(240, 5%, 64.9%)';
          
          const backLink = document.createElement('a');
          backLink.href = '#';
          backLink.style.color = 'hsl(142, 100%, 50%)';
          backLink.style.textDecoration = 'none';
          backLink.textContent = 'Retour à la connexion';
          backLink.addEventListener('click', function(e) {
            e.preventDefault();
            resetModal.style.display = 'none';
            if (loginModal) {
              loginModal.style.display = 'flex';
            }
          });
          
          linkText.appendChild(backLink);
          linkContainer.appendChild(linkText);
          resetForm.appendChild(linkContainer);
          
          // Ajouter l'event listener pour soumettre le formulaire
          resetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupérer les valeurs du formulaire
            const formData = new FormData(this);
            
            // Changer le texte du bouton
            const submitButton = resetForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.innerHTML = '<span>Envoi en cours...</span>';
            submitButton.disabled = true;
            
            // Supprimer les alertes précédentes
            const previousAlert = resetForm.querySelector('.alert');
            if (previousAlert) {
              previousAlert.remove();
            }
            
            // Envoyer la requête AJAX
            fetch('/password-reset/', {
              method: 'POST',
              body: formData,
              headers: {
                'X-Requested-With': 'XMLHttpRequest'
              }
            })
            .then(response => {
              if (!response.ok) {
                return response.json().then(data => {
                  throw new Error(data.message || 'Une erreur est survenue');
                });
              }
              return response.json();
            })
            .then(data => {
              if (data.success) {
                // Vider le formulaire
                resetForm.querySelector('input[type="email"]').value = '';
                
                // Afficher un message de succès
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.textContent = data.message || 'Lien de réinitialisation envoyé! Vérifiez votre boîte mail.';
                resetForm.insertBefore(successAlert, resetForm.firstChild);
                
                // Fermer la modale après un délai
                setTimeout(() => {
                  resetModal.style.display = 'none';
                }, 3000);
              }
            })
            .catch(error => {
              console.error('Erreur:', error);
              
              // Afficher un message d'erreur
              const errorAlert = document.createElement('div');
              errorAlert.className = 'alert alert-danger';
              errorAlert.textContent = error.message || 'Une erreur est survenue. Veuillez réessayer.';
              resetForm.insertBefore(errorAlert, resetForm.firstChild);
            })
            .finally(() => {
              // Réinitialiser le bouton
              submitButton.innerHTML = originalButtonText;
              submitButton.disabled = false;
            });
          });
          
          formContainer.appendChild(resetForm);
          
          // Assembler la modal
          modalContent.appendChild(closeButton);
          modalContent.appendChild(title);
          modalContent.appendChild(formContainer);
          resetModal.appendChild(modalContent);
          
          // Ajouter la modal au document
          document.body.appendChild(resetModal);
          
          // Gestion de la fermeture
          closeButton.addEventListener('click', function() {
            resetModal.style.display = 'none';
          });
          
          // Fermer en cliquant à l'extérieur
          resetModal.addEventListener('click', function(event) {
            if (event.target === resetModal) {
              resetModal.style.display = 'none';
            }
          });
          
          // Fermer avec Escape
          document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && resetModal.style.display === 'flex') {
              resetModal.style.display = 'none';
            }
          });
        }
        
        // Afficher la modale
        resetModal.style.display = 'flex';
      });
    }

    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Récupérer les valeurs du formulaire
      const formData = new FormData(this);
      
      // Changer le texte du bouton
      const submitButton = form.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.innerHTML;
      submitButton.innerHTML = '<span>Connexion en cours...</span>';
      submitButton.disabled = true;
      
      // Supprimer les alertes précédentes
      const previousAlert = form.querySelector('.alert');
      if (previousAlert) {
        previousAlert.remove();
      }
      
      // Envoyer la requête AJAX
      fetch('/login/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (!response.ok) {
          return response.json().then(data => {
            throw new Error(data.message || 'Erreur lors de la connexion');
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Afficher un message de succès
          const successAlert = document.createElement('div');
          successAlert.className = 'alert alert-success';
          successAlert.textContent = data.message || 'Connexion réussie!';
          form.insertBefore(successAlert, form.firstChild);
          
          // Rediriger vers la page d'accueil après un délai
          setTimeout(() => {
            window.location.href = data.redirect_url || '/';
          }, 1000);
        }
      })
      .catch(error => {
        console.error('Erreur:', error);
        
        // Afficher un message d'erreur
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = error.message || 'Identifiants invalides. Veuillez réessayer.';
        form.insertBefore(errorAlert, form.firstChild);
        
        // Réinitialiser le bouton
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
      });
    });
  }

  // Ajouter la gestion du lien d'inscription pour afficher une modal AJAX
  const registerLink = document.querySelector('.navbar-cta');

  if (registerLink) {
    registerLink.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Vérifier si la modal existe déjà
      let registerModal = document.getElementById('register-modal');
      
      // Si la modal n'existe pas, la créer
      if (!registerModal) {
        registerModal = document.createElement('div');
        registerModal.id = 'register-modal';
        registerModal.className = 'modal';
        registerModal.style.display = 'none';
        registerModal.style.position = 'fixed';
        registerModal.style.top = '0';
        registerModal.style.left = '0';
        registerModal.style.width = '100%';
        registerModal.style.height = '100%';
        registerModal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        registerModal.style.zIndex = '1000';
        registerModal.style.justifyContent = 'center';
        registerModal.style.alignItems = 'center';
        
        // Contenu de la modal
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.backgroundColor = 'hsl(240, 3.7%, 10%)';
        modalContent.style.padding = '2rem';
        modalContent.style.borderRadius = '0.5rem';
        modalContent.style.width = '90%';
        modalContent.style.maxWidth = '500px';
        modalContent.style.position = 'relative';
        modalContent.style.maxHeight = '90vh';
        modalContent.style.overflowY = 'auto';
        
        // Bouton de fermeture
        const closeButton = document.createElement('span');
        closeButton.className = 'close-modal';
        closeButton.innerHTML = '&times;';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '1rem';
        closeButton.style.right = '1rem';
        closeButton.style.fontSize = '1.5rem';
        closeButton.style.cursor = 'pointer';
        closeButton.style.color = 'hsl(240, 5%, 64.9%)';
        
        // Titre
        const title = document.createElement('div');
        title.style.textAlign = 'center';
        title.style.marginBottom = '2rem';
        title.innerHTML = '<h2 style="font-size: 2rem; margin-bottom: 0.5rem;"><span style="color: hsl(142, 100%, 50%);">I</span>nscription</h2><p style="color: hsl(240, 5%, 64.9%);">Créez votre compte Hackerz</p>';
        
        // Formulaire (à charger via AJAX)
        const formContainer = document.createElement('div');
        formContainer.id = 'register-form-container';
        
        // Loader
        const loader = document.createElement('div');
        loader.className = 'loader';
        loader.style.textAlign = 'center';
        loader.style.padding = '2rem';
        loader.innerHTML = 'Chargement...';
        
        // Assembler la modal
        formContainer.appendChild(loader);
        modalContent.appendChild(closeButton);
        modalContent.appendChild(title);
        modalContent.appendChild(formContainer);
        registerModal.appendChild(modalContent);
        
        // Ajouter la modal au document
        document.body.appendChild(registerModal);
        
        // Gestion de la fermeture
        closeButton.addEventListener('click', function() {
          registerModal.style.display = 'none';
        });
        
        // Fermer en cliquant à l'extérieur
        registerModal.addEventListener('click', function(event) {
          if (event.target === registerModal) {
            registerModal.style.display = 'none';
          }
        });
        
        // Fermer avec Escape
        document.addEventListener('keydown', function(event) {
          if (event.key === 'Escape' && registerModal.style.display === 'flex') {
            registerModal.style.display = 'none';
          }
        });
      }
      
      // Afficher la modal
      registerModal.style.display = 'flex';
      
      // Charger le formulaire via AJAX
      const formContainer = document.getElementById('register-form-container');
      formContainer.innerHTML = '<div class="loader" style="text-align: center; padding: 2rem;">Chargement...</div>';
      
      // Requête AJAX pour récupérer le formulaire
      fetch('/register/', {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Erreur lors du chargement du formulaire');
        }
        return response.json();
      })
      .then(data => {
        if (data.html) {
          formContainer.innerHTML = '';
          
          // Créer le formulaire
          const form = document.createElement('form');
          form.id = 'ajax-register-form';
          form.method = 'post';
          form.action = '/register/';
          form.className = 'form';
          form.innerHTML = data.html;
          
          formContainer.appendChild(form);
          
          // Configurer les boutons de visibilité des mots de passe
          setupPasswordToggles(form);
          
          // Ajouter l'événement de soumission
          setupRegisterFormSubmit(form);
        }
      })
      .catch(error => {
        console.error('Erreur:', error);
        formContainer.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement du formulaire. Veuillez réessayer.</div>';
      });
    });
  }

  // Fonction pour configurer les toggles de mot de passe
  function setupPasswordToggles(form) {
    const togglePassword1 = form.querySelector('#toggle-password1');
    const togglePassword2 = form.querySelector('#toggle-password2');
    const password1 = form.querySelector('#password1');
    const password2 = form.querySelector('#password2');
    
    if (togglePassword1 && password1) {
      togglePassword1.addEventListener('click', function() {
        const type = password1.getAttribute('type') === 'password' ? 'text' : 'password';
        password1.setAttribute('type', type);
      });
    }
    
    if (togglePassword2 && password2) {
      togglePassword2.addEventListener('click', function() {
        const type = password2.getAttribute('type') === 'password' ? 'text' : 'password';
        password2.setAttribute('type', type);
      });
    }
  }

  // Fonction pour configurer la soumission du formulaire d'inscription
  function setupRegisterFormSubmit(form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Récupérer les valeurs du formulaire
      const formData = new FormData(this);
      
      // Changer le texte du bouton
      const submitButton = form.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.innerHTML;
      submitButton.innerHTML = '<span>Inscription en cours...</span>';
      submitButton.disabled = true;
      
      // Supprimer les alertes précédentes
      const previousAlert = form.querySelector('.alert');
      if (previousAlert) {
        previousAlert.remove();
      }
      
      // Envoyer la requête AJAX
      fetch('/register/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        if (!response.ok) {
          return response.json().then(data => {
            throw new Error(data.message || 'Erreur lors de l\'inscription');
          });
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Afficher un message de succès
          const successAlert = document.createElement('div');
          successAlert.className = 'alert alert-success';
          successAlert.textContent = data.message || 'Inscription réussie!';
          form.insertBefore(successAlert, form.firstChild);
          
          // Rediriger vers la page d'accueil après un délai
          setTimeout(() => {
            window.location.href = data.redirect_url || '/';
          }, 1000);
        }
      })
      .catch(error => {
        console.error('Erreur:', error);
        
        // Afficher un message d'erreur
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger';
        errorAlert.textContent = error.message || 'Une erreur s\'est produite lors de l\'inscription. Veuillez réessayer.';
        form.insertBefore(errorAlert, form.firstChild);
        
        // Réinitialiser le bouton
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
      });
    });
  }
});

// Add CSS to head for toast notifications
const toastStyles = document.createElement('style');
toastStyles.textContent = `
  .toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: hsl(0, 0%, 9%);
    color: hsl(0, 0%, 98%);
    padding: 12px 20px;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(100px);
    opacity: 0;
    transition: transform 0.3s, opacity 0.3s;
    z-index: 1000;
    border-left: 4px solid hsl(142, 100%, 50%);
  }
  
  .toast.show {
    transform: translateY(0);
    opacity: 1;
  }
  
  .toast-success {
    border-left-color: hsl(142, 100%, 50%);
  }
  
  .toast-error {
    border-left-color: hsl(0, 62.8%, 30.6%);
  }
  
  .toast-warning {
    border-left-color: hsl(39, 100%, 50%);
  }
  
  .hidden {
    display: none;
  }
`;
document.head.appendChild(toastStyles);

// Ajouter ici les styles CSS nécessaires
const styles = document.createElement('style');
styles.textContent = `
  .modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    justify-content: center;
    align-items: center;
  }
  
  .modal-content {
    background-color: hsl(240, 3.7%, 10%);
    padding: 2rem;
    border-radius: 0.5rem;
    width: 90%;
    max-width: 400px;
    position: relative;
  }
  
  .close-modal {
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 1.5rem;
    cursor: pointer;
    color: hsl(240, 5%, 64.9%);
  }
  
  .close-modal:hover {
    color: white;
  }
  
  .alert {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
    font-size: 0.875rem;
  }
  
  .alert-danger {
    background-color: rgba(255, 0, 0, 0.1);
    border: 1px solid rgba(255, 0, 0, 0.3);
    color: rgb(255, 80, 80);
  }
  
  .alert-success {
    background-color: rgba(0, 255, 0, 0.1);
    border: 1px solid rgba(0, 255, 0, 0.3);
    color: rgb(0, 255, 0);
  }
`;

document.head.appendChild(styles);
