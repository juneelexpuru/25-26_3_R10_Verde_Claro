import json
import os
import pandas as pd
import numpy as np
import networkx as nx
import torch
import torch.nn.functional as F
from kafka import KafkaConsumer
from torch_geometric.nn import GATConv
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings("ignore")


TOPIC_INPUT = 'input_garments'
KAFKA_SERVER = 'localhost:9092'
CARPETA_SALIDA = 'resultados_looks_gat'

PATH_GRAPH = "../Modelos/graph.gml" 
PATH_MODEL_PTH = "../Modelos/Modelo_GAT.pth"  
PATH_COLORS = "../Datos/Transformados/combinaciones_final.csv"

if not os.path.exists(CARPETA_SALIDA): os.makedirs(CARPETA_SALIDA)


class GAT(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, num_layers, heads=2):
        super().__init__()
        self.convs = torch.nn.ModuleList()
        self.convs.append(GATConv(in_channels, hidden_channels[0], heads=heads, concat=True))
        for i in range(num_layers - 2):
            self.convs.append(GATConv(hidden_channels[i] * heads, hidden_channels[i+1], heads=heads, concat=True))
        self.convs.append(GATConv(hidden_channels[-1] * heads, out_channels, heads=1, concat=False))

    def encode(self, x, edge_index):
        for conv in self.convs[:-1]:
            x = conv(x, edge_index)
            x = F.elu(x)
        return self.convs[-1](x, edge_index)

    def project_new_node(self, x):
        for i, conv in enumerate(self.convs):
            if hasattr(conv, 'lin'): x = conv.lin(x)
            elif hasattr(conv, 'lin_src'): x = conv.lin_src(x)
            
            if i < len(self.convs) - 1:
                x = F.elu(x)
        return x


VALID_COLOR_PAIRS = set()
if os.path.exists(PATH_COLORS):
    try:
        df_c = pd.read_csv(PATH_COLORS)
        df_c['color1'] = df_c['color1'].astype(str).str.strip().str.replace('#','').str.upper()
        df_c['color2'] = df_c['color2'].astype(str).str.strip().str.replace('#','').str.upper()
        for _, row in df_c[df_c['score'] > 0.7].iterrows():
            VALID_COLOR_PAIRS.add((row['color1'], row['color2']))
            VALID_COLOR_PAIRS.add((row['color2'], row['color1']))
    except: pass

def validar_par(a, b):
    if a.get('categoria_prenda') == b.get('categoria_prenda'): return False
    
    n1, n2 = int(a.get('nivel', 0)), int(b.get('nivel', 0))
    pairs = sorted([n1, n2])
    valid = (pairs == [1, 4]) or (pairs == [2, 3]) or (pairs == [3, 4]) or (pairs == [2, 4]) or (n1==4 and n2==4)
    if not valid: return False
    
    s1 = str(a.get('style', '')).split(',')[0].strip().lower()
    s2 = str(b.get('style', '')).split(',')[0].strip().lower()
    if s1 != s2 and 'casual' not in [s1, s2]: return False 

    c1 = str(a.get('hexadecimal', '')).replace('#','').upper().strip()
    c2 = str(b.get('hexadecimal', '')).replace('#','').upper().strip()
    if VALID_COLOR_PAIRS:
        if (c1, c2) not in VALID_COLOR_PAIRS and c1 != c2: 
             if c1 not in ['000000', 'FFFFFF'] and c2 not in ['000000', 'FFFFFF']: return False
    return True

def safe_transform(encoder, value):
    val_str = str(value)
    if val_str in encoder.classes_: return encoder.transform([val_str])[0]
    if 'unknown' in encoder.classes_: return encoder.transform(['unknown'])[0]
    return 0

def vectorize_node(d, encoders):
    return [
        safe_transform(encoders['hexadecimal'], d.get('hexadecimal', '000000')),
        safe_transform(encoders['categoria_prenda'], d.get('categoria_prenda', 'unknown')),
        safe_transform(encoders['weather'], d.get('weather', 'unknown')),
        safe_transform(encoders['style'], d.get('style', 'unknown'))
    ]


def generar_10_looks(seed, model, full_emb, G, encoders, look_id_base):
    feat_vec = vectorize_node(seed, encoders)
    feat_tensor = torch.tensor([feat_vec], dtype=torch.float)
    
    model.eval()
    with torch.no_grad():
        seed_emb = model.project_new_node(feat_tensor)
        scores = torch.matmul(full_emb, seed_emb.t()).sigmoid().view(-1)
    
    top_k = 2000
    top_scores, top_idxs = torch.topk(scores, min(top_k, len(G.nodes)))
    
    pool = {1: [], 2: [], 3: [], 4: []}
    for i in top_idxs.numpy():
        node_id = list(G.nodes)[i]
        node_data = G.nodes[node_id]
        if validar_par(seed, node_data):
            lvl = int(node_data.get('nivel', 0))
            if lvl in pool: pool[lvl].append({'data': node_data})

    seed_lvl = int(seed.get('nivel', 3))
    seed_name = seed.get('nombre_producto', seed.get('Tipo de prenda', 'Input'))
    datos_csv = []
    
    for n in range(10):
        fila = {
            'Semilla_Producto': seed_name, 'Semilla_Nivel': seed_lvl, 'Look_ID': f"{look_id_base}_{n+1}",
            'Nivel_1_Jumpsuit': '', 'Nivel_2_Bottom': '', 'Nivel_3_Top': '', 'Nivel_4_Outerwear': ''
        }
        
        if seed_lvl == 1: fila['Nivel_1_Jumpsuit'] = seed_name
        elif seed_lvl == 2: fila['Nivel_2_Bottom'] = seed_name
        elif seed_lvl == 3: fila['Nivel_3_Top'] = seed_name
        elif seed_lvl == 4: fila['Nivel_4_Outerwear'] = seed_name

        if seed_lvl == 3: 
            if pool[2]:
                bot = pool[2][n % len(pool[2])]['data']
                fila['Nivel_2_Bottom'] = bot['nombre_producto']
                if pool[4]:
                     for k in range(len(pool[4])):
                         out = pool[4][(n + k) % len(pool[4])]['data']
                         if validar_par(out, bot):
                             fila['Nivel_4_Outerwear'] = out['nombre_producto']; break
        elif seed_lvl == 2: 
            if pool[3]:
                top = pool[3][n % len(pool[3])]['data']
                fila['Nivel_3_Top'] = top['nombre_producto']
                if pool[4]:
                     for k in range(len(pool[4])):
                         out = pool[4][(n + k) % len(pool[4])]['data']
                         if validar_par(out, top):
                             fila['Nivel_4_Outerwear'] = out['nombre_producto']; break
        elif seed_lvl == 4: 
             if (n % 2 != 0) and pool[1]: 
                fila['Nivel_1_Jumpsuit'] = pool[1][n % len(pool[1])]['data']['nombre_producto']
             elif pool[3] and pool[2]:
                top = pool[3][n % len(pool[3])]['data']
                fila['Nivel_3_Top'] = top['nombre_producto']
                for k in range(len(pool[2])):
                    bot = pool[2][(n + k) % len(pool[2])]['data']
                    if validar_par(bot, top):
                        fila['Nivel_2_Bottom'] = bot['nombre_producto']; break
        elif seed_lvl == 1: 
            if pool[4]: fila['Nivel_4_Outerwear'] = pool[4][n % len(pool[4])]['data']['nombre_producto']

        datos_csv.append(fila)

    return pd.DataFrame(datos_csv)


def main():
    if not os.path.exists(PATH_GRAPH) or not os.path.exists(PATH_MODEL_PTH):
        print("❌ Faltan archivos (.gml o .pth)."); return

    print("⏳ Cargando Checkpoint (.pth)...")
    try:
        checkpoint = torch.load(PATH_MODEL_PTH)
        
        encoders = checkpoint['encoders']
        print("✅ Encoders recuperados.")
        
        config = checkpoint['model_config'] 
        input_dim = checkpoint['input_dim']
        

        h_dim = config['hidden_channels']
        hidden_list = [h_dim, h_dim // 2]
        
        print(f"Config recuperada: Heads={config['heads']}, Hidden={hidden_list}")
        
    except KeyError as e:
        print(f"El archivo .pth no tiene el formato esperado (falta {e}).")
        return

    print("⏳ Cargando Grafo...")
    G = nx.read_gml(PATH_GRAPH)
    
    from torch_geometric.utils import from_networkx
    for n in G.nodes(): G.nodes[n]['x'] = vectorize_node(G.nodes[n], encoders)
    data = from_networkx(G)
    data.x = data.x.float()

    model = GAT(
        in_channels=input_dim,
        hidden_channels=hidden_list,
        out_channels=32, 
        num_layers=3,    
        heads=config['heads']
    )
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print("⏳ Generando Embeddings Base...")
    with torch.no_grad():
        full_emb = model.encode(data.x, data.edge_index)

    consumer = KafkaConsumer(
        TOPIC_INPUT,
        bootstrap_servers=[KAFKA_SERVER],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print(f"\n📡 Consumer GAT listo en '{TOPIC_INPUT}'")

    for message in consumer:
        try:
            payload = message.value
            tid = payload.get('id_transaccion', 'unknown')
            prenda_in = payload.get('datos_prenda')
            
            print(f"\n⚡ Prenda: {prenda_in.get('categoria_prenda')}")
            
            df = generar_10_looks(prenda_in, model, full_emb, G, encoders, tid)
            
            f_out = os.path.join(CARPETA_SALIDA, f"looks_{tid}.csv")
            cols = ['Semilla_Producto', 'Semilla_Nivel', 'Look_ID', 'Nivel_1_Jumpsuit', 'Nivel_2_Bottom', 'Nivel_3_Top', 'Nivel_4_Outerwear']
            df[cols].to_csv(f_out, index=False)
            print(f"   ✅ Generado: {f_out}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()