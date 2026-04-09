#!/usr/bin/env python3
"""
Stripe Checkout Server per VisualCode AI
Server per gestire i pagamenti in tempo reale
"""

import os
import json
import stripe
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

app = Flask(__name__)

# Carica configurazione Stripe
env_path = '/home/node/.openclaw/workspace/.env'
stripe_key = None

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('STRIPE_SECRET_KEY='):
                stripe_key = line.strip().split('=', 1)[1].strip('\"\'')
                break

if stripe_key:
    stripe.api_key = stripe_key
    print('✅ Stripe LIVE密钥已加载')
else:
    print('❌ Stripe密钥未找到')

# Prezzi (aggiornati con i prezzi reali)
PRICES = {
    'monthly': 'price_1TI3s9DRLWt3rKvb4zRx9Ui7',  # €99/mese
    'yearly': 'price_1TI3s9DRLWt3rKvbly6ZsDyj'   # €999/anno
}

# Configurazione email
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'notifiche@visualcodeai.it',
    'sender_password': os.getenv('EMAIL_PASSWORD', ''),
    'admin_email': 'admin@visualcodeai.it'
}

# Database semplice (in memoria)
customers_db = {}
orders_db = {}

def send_welcome_email(customer_email, customer_name, plan_type):
    """Invia email di benvenuto"""
    try:
        plan_name = "Mensile (€99/mese)" if plan_type == 'monthly' else "Annuale (€999/anno)"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Benvenuto in VisualCode AI - {customer_name}'
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = customer_email
        
        # Testo dell'email
        text = f"""Ciao {customer_name},

Grazie per esserti iscritto a VisualCode AI!

Il tuo abbonamento: {plan_name}
Data di iscrizione: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Per accedere alla piattaforma:
1. Visita https://app.visualcodeai.it
2. Usa questa email per il login
3. Ti invieremo la password di accesso entro 24 ore

Hai domande? Rispondi a questa email o contattaci su WhatsApp: +39 123 456 7890

Benvenuto nella rivoluzione dello sviluppo AI italiano!

Il team di VisualCode AI
"""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4f46e5; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ padding: 30px; background: #f9fafb; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #4f46e5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Benvenuto in VisualCode AI!</h1>
        </div>
        <div class="content">
            <p>Ciao <strong>{customer_name}</strong>,</p>
            
            <p>Grazie per esserti iscritto a VisualCode AI, il primo platform italiano di generazione codice AI!</p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #4f46e5; margin: 20px 0;">
                <h3 style="margin-top: 0;">📋 Dettagli del tuo abbonamento:</h3>
                <p><strong>Piano:</strong> {plan_name}</p>
                <p><strong>Data di iscrizione:</strong> {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
                <p><strong>Email di accesso:</strong> {customer_email}</p>
            </div>
            
            <h3>🚀 Come accedere:</h3>
            <ol>
                <li>Visita <a href="https://app.visualcodeai.it">app.visualcodeai.it</a></li>
                <li>Usa questa email per il login</li>
                <li>Ti invieremo la password di accesso entro 24 ore</li>
            </ol>
            
            <a href="https://app.visualcodeai.it" class="button">Accedi alla Piattaforma</a>
            
            <h3>📞 Supporto</h3>
            <p>Hai domande? Siamo qui per aiutarti:</p>
            <ul>
                <li>Email: supporto@visualcodeai.it</li>
                <li>WhatsApp: +39 123 456 7890</li>
                <li>Telefono: +39 02 1234 5678 (Lun-Ven, 9-18)</li>
            </ul>
            
            <p>Benvenuto nella rivoluzione dello sviluppo AI italiano! 🚀</p>
        </div>
        <div class="footer">
            <p>© 2026 VisualCode AI - Innovazione Italiana SRL</p>
            <p>Via Roma 123, 20121 Milano, Italia</p>
            <p>P.IVA: IT12345678901 | <a href="https://visualcodeai.it/termini">Termini di servizio</a> | <a href="https://visualcodeai.it/privacy">Privacy Policy</a></p>
        </div>
    </div>
</body>
</html>"""
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Invia email (solo se configurata)
        if EMAIL_CONFIG['sender_password']:
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
            server.quit()
            print(f'✅ Email inviata a {customer_email}')
        else:
            print(f'ℹ️  Email simulata per {customer_email}')
            
        return True
        
    except Exception as e:
        print(f'❌ Errore invio email: {str(e)}')
        return False

def send_admin_notification(customer_email, customer_name, plan_type, amount):
    """Invia notifica all'amministratore"""
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f'🔥 NUOVO CLIENTE: {customer_name} - {plan_type}'
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['admin_email']
        
        text = f"""NUOVO CLIENTE ACQUISTATO!

Nome: {customer_name}
Email: {customer_email}
Piano: {plan_type}
Importo: €{amount}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Totale clienti oggi: {len(customers_db)}
Totale ordini oggi: {len(orders_db)}

🚀 INIZIA SUBTO IL SUPPORTO!"""
        
        part = MIMEText(text, 'plain')
        msg.attach(part)
        
        if EMAIL_CONFIG['sender_password']:
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
            server.quit()
            
        return True
        
    except Exception as e:
        print(f'❌ Errore notifica admin: {str(e)}')
        return False

@app.route('/')
def home():
    """Pagina principale"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>VisualCode AI - Checkout Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { background: #4f46e5; color: white; padding: 30px; border-radius: 10px; text-align: center; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
            .stat-number { font-size: 2.5rem; font-weight: bold; color: #4f46e5; }
            .stat-label { color: #6b7280; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 VisualCode AI Checkout Server</h1>
            <p>Sistema di pagamento in tempo reale</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ customers|length }}</div>
                <div class="stat-label">Clienti Registrati</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ orders|length }}</div>
                <div class="stat-label">Ordini Oggi</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">€{{ revenue }}</div>
                <div class="stat-label">Fatturato Oggi</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ active }}</div>
                <div class="stat-label">Server Attivo</div>
            </div>
        </div>
        
        <h2>Clienti Recenti</h2>
        <ul>
            {% for customer in recent_customers %}
            <li>{{ customer.name }} - {{ customer.email }} ({{ customer.plan }})</li>
            {% endfor %}
        </ul>
        
        <div style="margin-top: 40px; padding: 20px; background: #f0fdf4; border-radius: 10px; border: 2px solid #bbf7d0;">
            <h3>✅ Sistema Operativo</h3>
            <p>Stripe: {{ 'CONNESSO' if stripe_key else 'NON CONNESSO' }}</p>
            <p>Ultimo aggiornamento: {{ now }}</p>
        </div>
    </body>
    </html>
    """, 
    customers=customers_db,
    orders=orders_db,
    revenue=sum(order.get('amount', 0) for order in orders_db.values()),
    active="✅",
    recent_customers=list(customers_db.values())[-5:],
    now=datetime.now().strftime('%H:%M:%S')
    )

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Crea una sessione di checkout Stripe"""
    try:
        data = request.json
        price_id = data.get('priceId')
        customer_email = data.get('customerEmail')
        customer_name = data.get('customerName')
        plan_type = data.get('planType', 'monthly')
        
        if not all([price_id, customer_email, customer_name]):
            return jsonify({'error': 'Dati mancanti'}), 400
        
        # Determina l'importo
        amount = 9900 if plan_type == 'monthly' else 99900  # in centesimi
        
        # Crea la sessione di checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://visualcodeai.it/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://visualcodeai.it/cancel',
            customer_email=customer_email,
            metadata={
                'customer_name': customer_name,
                'plan_type': plan_type,
                'amount': amount
            }
        )
        
        # Salva il cliente temporaneamente
        customer_id = f"cust_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        customers_db[customer_id] = {
            'id': customer_id,
            'name': customer_name,
            'email': customer_email,
            'plan': plan_type,
            'amount': amount / 100,
            'registered_at': datetime.now().isoformat(),
            'status': 'pending_payment'
        }
        
        # Salva l'ordine
        order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        orders_db[order_id] = {
            'order_id': order_id,
            'customer_id': customer_id,
            'session_id': session.id,
            'amount': amount / 100,
            'plan_type': plan_type,
            'status': 'created',
            'created_at': datetime.now().isoformat()
        }
        
        print(f'✅ Sessione checkout creata per {customer_name} ({customer_email}) - €{amount/100}')
        
        return jsonify({
            'id': session.id,
            'customer_id': customer_id,
            'order_id': order_id
        })
        
    except Exception as e:
        print(f'❌ Errore creazione checkout: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Webhook per eventi Stripe"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        # Verifica la firma del webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET', '')
        )
        
        # Gestisci l'evento
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_email = session.get('customer_email')
            customer_name = session.get('metadata', {}).get('customer_name', '')
            plan_type = session.get('metadata', {}).get('plan_type', 'monthly')
            amount = session.get('amount_total', 0) / 100
            
            # Trova il cliente
            customer_id = None
            for cid, customer in customers_db.items():
                if customer['email'] == customer_email:
                    customer_id = cid
                    break
            
            if customer_id:
                # Aggiorna stato cliente
                customers_db[customer_id]['status'] = 'active'
                customers_db[customer_id]['payment_date'] = datetime.now().isoformat()
                customers_db[customer_id]['stripe_customer_id'] = session.get('customer')
                
                # Aggiorna ordine
                for oid, order in orders_db.items():
                    if order.get('customer_id') == customer_id:
                        orders_db[oid]['status'] = 'paid'
                        orders_db[oid]['paid_at'] = datetime.now().isoformat()
                        orders_db[oid]['stripe_session_id'] = session.get('id')
                        break
                
                # Invia email di benvenuto
                threading.Thread(
                    target=send_welcome_email,
                    args=(customer_email, customer_name, plan_type)
                ).start()
                
                # Invia notifica admin
                threading.Thread(
                    target=send_admin_notification,
                    args=(customer_email, customer_name, plan_type, amount)
                ).start()
                
                print(f'🎉 PAGAMENTO COMPLETATO: {customer_name} - €{amount}')
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f'❌ Errore webhook: {str(e)}')
        return jsonify({'error': str(e)}), 400

@app.route('/customers')
def list_customers():
    """Lista clienti"""
    return jsonify({
        'total': len(customers_db),
        'customers': list(customers_db.values()),
        'revenue_today': sum(order.get('amount', 0) for order in orders_db.values())
    })

@app.route('/orders')
def list_orders():
    """Lista ordini"""
    return jsonify({
        'total': len(orders_db),
        'orders': list(orders_db.values())
    })

if __name__ == '__main__':
    print('🚀 Avvio server Checkout Stripe...')
    print(f'✅ Stripe LIVE: {stripe_key[:20]}...')
    print('🌐 Server in ascolto su http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)