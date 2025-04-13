from io import BytesIO
from decimal import Decimal
import os
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings

def generate_invoice_pdf(order):
    """
    Génère une facture PDF pour une commande donnée
    
    Args:
        order: L'instance de la commande Order
        
    Returns:
        HttpResponse avec le PDF ou None en cas d'erreur
    """
    # Calcul du sous-total
    total = sum(item.get_cost() for item in order.items.all())
    
    # Calcul de la TVA (20%)
    tax = total * Decimal('0.2')
    
    # Total avec TVA
    total_with_tax = total * Decimal('1.2')
    
    # Contexte pour le template
    context = {
        'order': order,
        'order_items': order.items.all(),
        'total': total,
        'tax': tax,
        'total_with_tax': total_with_tax,
        'company_name': 'Hackerz',
        'company_address': '123 Rue de la Tech, 75000 Paris',
        'company_phone': '+33 1 23 45 67 89',
        'company_email': 'contact@hackerz.fr',
        'company_website': 'www.hackerz.fr',
    }
    
    # Charger le template HTML
    template = get_template('shop/invoice_pdf.html')
    html = template.render(context)
    
    # Créer un buffer pour le PDF
    result = BytesIO()
    
    # Générer le PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        # Si la génération du PDF a réussi, retourner la réponse HTTP
        filename = f"facture_{order.id}.pdf"
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return None

def save_invoice_pdf(order):
    """
    Sauvegarde une facture PDF pour une commande dans le système de fichiers
    
    Args:
        order: L'instance de la commande Order
        
    Returns:
        Le chemin du fichier PDF ou None en cas d'erreur
    """
    # Calcul du sous-total
    total = sum(item.get_cost() for item in order.items.all())
    
    # Calcul de la TVA (20%)
    tax = total * Decimal('0.2')
    
    # Total avec TVA
    total_with_tax = total * Decimal('1.2')
    
    # Contexte pour le template
    context = {
        'order': order,
        'order_items': order.items.all(),
        'total': total,
        'tax': tax,
        'total_with_tax': total_with_tax,
        'company_name': 'Hackerz',
        'company_address': '123 Rue de la Tech, 75000 Paris',
        'company_phone': '+33 1 23 45 67 89',
        'company_email': 'contact@hackerz.fr',
        'company_website': 'www.hackerz.fr',
    }
    
    # Charger le template HTML
    template = get_template('shop/invoice_pdf.html')
    html = template.render(context)
    
    # Créer un buffer pour le PDF
    result = BytesIO()
    
    # Générer le PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        # Si la génération du PDF a réussi, sauvegarder dans le dossier media
        invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
        
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(invoices_dir):
            os.makedirs(invoices_dir)
        
        filename = f"facture_{order.id}.pdf"
        filepath = os.path.join(invoices_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(result.getvalue())
        
        # Retourner le chemin relatif pour accès via URL
        return os.path.join('invoices', filename)
    
    return None 