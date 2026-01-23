import json
import uuid
from flask import Flask, request, render_template
from kafka import KafkaProducer

app = Flask(__name__)

KAFKA_SERVER = 'localhost:9092'
TOPIC_NAME = 'input_garments'

MAPA_NIVEL = {
    'dress': 1, 'jumpsuit': 1,
    'bottoms': 2, 'skirt': 2,
    'top': 3,
    'scarf': 4, 'outerwear': 4, 'bag': 4
}

MAPA_SUBNIVEL = {
    'dress': 1.1, 'jumpsuit': 1.2,
    'skirt': 2.1, 'bottoms': 2.2,
    'top': 3.1,
    'outerwear': 4.1, 'scarf': 4.2, 'bag': 4.3
}

OPCIONES = {
    "colores": [
        '#000000', '#000081', '#153668', '#0053A5', '#00008B', '#640B22', 
        '#614051', '#3B6968', '#008000', '#666633', '#164A0A', '#EBD6A7', '#0000FF'
    ],
    "categorias": [
        'bottoms', 'top', 'outerwear', 'dress', 'skirt', 'scarf', 'bag', 'jumpsuit'
    ],
    "subcategorias": sorted([
        'cigarette', 'hoodies', 'tops', 't-shirts', 'bomber', 'biker', 'shirt', 
        'cardigan', 'sweaters', 'jegging', 'with_pleat', 'chino', 'pleated', 
        'mom_jeans', 'skinny', 'trench', 'straight', 'kimono', 'handkerchief', 
        'foulard', 'blouse', 'jacket', 'beachy', 'crossbag', 'bermuda', 
        'circle_skirt', 'paper_bag', 'flared_skirt', 'shorts', 'lady', 'knitted', 
        'jumpsuit', 'tube', 'structured_jacket', 'parka', 'puff', 'blazer', 
        'tunica', 'pencil', 'crossed', 'safari_jacket', 'baggie', 'over_shirt', 
        'culotte', 'flared', 'cowgirl', 'jogger', 'coat', 'other', 'raincoat', 
        'evase', 'babydoll', 'miniskirt', 'sweatshirt', 'palazzo', 'envelope', 
        'shopper', 'shoulder_bag', 'crossbody', 'tulip', 'cigarett', 'frill', 
        'skater', 'bell', 'a_line', 'collar', 'denim', 'bucket', 'chanel', 
        'hoodie', 'wide_leg', 'pant_skirt', 'scarf', 'wrapped', 'tight', 
        'leggings', 'beach_bag', 'feathers', 'lingerie', 'dungaree', 'wrap'
    ]),
    "adventurous": sorted([3, 2, 4, 1, 5]),
    "weather": ['warm_season', 'cold_season', 'warm', 'cold', 'mid_season'],
    "style": ['casual', 'boho', 'street', 'classic', 'night', 'minimal', 'smart'],
    "application": ['freetime', 'work', 'night', 'working_girl', 'special_occasion']
}

# Inicializar el producer
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    print("✅ Conexión con Kafka establecida.")
except Exception as e:
    print(f"❌ Error conectando con Kafka: {e}")
    producer = None

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje_exito = None
    
    if request.method == 'POST':
        try:
            cat_seleccionada = request.form.get('categoria')
            
            nivel_auto = MAPA_NIVEL.get(cat_seleccionada, 1) 
            subnivel_auto = MAPA_SUBNIVEL.get(cat_seleccionada, 1.1)

            nueva_prenda = {
                "categoria_prenda": cat_seleccionada,
                "subcategoria_prenda": request.form.get('subcategoria'),
                "hexadecimal": request.form.get('color'), 
                "adventurous": int(request.form.get('adventurous')),
                "weather": request.form.get('weather'),
                "style": request.form.get('style'),
                "application": request.form.get('application'),
                "nivel": int(nivel_auto),
                "subnivel": float(subnivel_auto),
                
                "print": "smooth",  
                "basic": False      
            }

            transaction_id = str(uuid.uuid4())
            mensaje_kafka = {
                "id_transaccion": transaction_id,
                "datos_prenda": nueva_prenda
            }

            if producer:
                producer.send(TOPIC_NAME, value=mensaje_kafka)
                producer.flush()
                print(f"Sent: {nueva_prenda['categoria_prenda']} (Nivel {nivel_auto})")
                mensaje_exito = f"¡Prenda enviada! ID: {transaction_id}"
            else:
                mensaje_exito = "Error: Kafka no está conectado."

        except Exception as e:
            mensaje_exito = f"Error procesando datos: {str(e)}"

    return render_template('index.html', mensaje=mensaje_exito, opciones=OPCIONES)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)