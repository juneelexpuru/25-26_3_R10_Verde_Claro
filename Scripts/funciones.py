import pandas as pd
import numpy as np
import os
from IPython.display import display
import torch
from sklearn.metrics import roc_auc_score, precision_score, recall_score

# =============================================================================
# 1. LOGICA DE COLORES (Usado en validar_par)
# =============================================================================
VALID_COLOR_PAIRS = set()
if os.path.exists("combinaciones_final.csv"):
    df_c = pd.read_csv("combinaciones_final.csv")
    df_c['color1'] = df_c['color1'].astype(str).str.strip().str.lstrip('#').upper()
    df_c['color2'] = df_c['color2'].astype(str).str.strip().str.lstrip('#').upper()
    for _, row in df_c[df_c['score'] > 0.5].iterrows():
        VALID_COLOR_PAIRS.add((row['color1'], row['color2']))
        VALID_COLOR_PAIRS.add((row['color2'], row['color1']))

# =============================================================================
# 2. REGLAS BÁSICAS (Dependencias internas de validar_par)
# =============================================================================
def regla_nivel(n1, n2):
    n1, n2 = int(n1), int(n2)
    pairs = sorted([n1, n2])
    if pairs == [1, 4]: return True
    if pairs == [2, 3]: return True
    if pairs == [3, 4]: return True
    if pairs == [2, 4]: return True 
    return False

def regla_estilo(s1, s2):
    compat = {
        'boho': {'boho', 'casual', 'street', 'minimal', 'warm_season', 'cold_season'}, 
        'casual': {'casual', 'boho', 'street', 'smart', 'minimal'}, 
        'street': {'street', 'casual', 'boho', 'night', 'minimal'}, 
        'classic': {'classic', 'smart', 'night', 'minimal'}, 
        'smart': {'smart', 'classic', 'casual', 'night', 'minimal'}, 
        'night': {'night', 'street', 'classic', 'smart', 'minimal'}, 
        'minimal': {'minimal', 'boho', 'casual', 'classic', 'street', 'night', 'smart'}
    }
    s1 = str(s1).split(',')[0].strip().lower()
    s2 = str(s2).split(',')[0].strip().lower()
    return s2 in compat.get(s1, {s1}) or s1 in compat.get(s2, {s2})

# =============================================================================
# 3. FUNCIONES UTILIZADAS EN MODELO.IPYNB
# =============================================================================
def validar_par(a, b):
    if a.get('categoria_prenda') == b.get('categoria_prenda'): return False
    if not regla_nivel(a['nivel'], b['nivel']): return False
    if not regla_estilo(a['style'], b['style']): return False
    
    c1 = str(a.get('hexadecimal', '')).lstrip('#').upper()
    c2 = str(b.get('hexadecimal', '')).lstrip('#').upper()
    
    if VALID_COLOR_PAIRS:
        if (c1, c2) not in VALID_COLOR_PAIRS and c1 != c2: 
            return False
    else:
        neutros = ['000000', 'FFFFFF', '808080', '000080']
        if c1 not in neutros and c2 not in neutros and c1 != c2:
            return False
    return True

def safe_transform(encoder, value):
    val_str = str(value)
    if val_str in encoder.classes_:
        return encoder.transform([val_str])[0]
    else:
        if 'unknown' not in encoder.classes_:
            return 0
        return encoder.transform(['unknown'])[0]

def vectorize_node(d, encoders):
    return [
        safe_transform(encoders['hexadecimal'], d.get('hexadecimal', '000000')),
        safe_transform(encoders['categoria_prenda'], d.get('categoria_prenda', 'unknown')),
        safe_transform(encoders['weather'], d.get('weather', 'unknown')),
        safe_transform(encoders['style'], str(d.get('style', 'unknown')).split(',')[0])
    ]

@torch.no_grad()
def eval_link_predictor(model, data):
    model.eval()
    z = model.encode(data.x, data.edge_index)
    out = model.decode(z, data.edge_label_index).view(-1).sigmoid()
    y_true = data.edge_label.cpu().numpy()
    y_pred = out.cpu().numpy()
    auc = roc_auc_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred.round())
    recall = recall_score(y_true, y_pred.round())
    return auc, precision, recall

# =============================================================================
# 4. FUNCIONES UTILIZADAS EN PREPROCESAMIENTO.IPYNB
# =============================================================================
def asignar_subnivel_por_categoria(row):
    """Asigna un código decimal (ej. 1.1, 2.2) basándose en el nivel jerárquico y el nombre de la categoría."""
    cat = str(row["categoria_prenda"]).lower().strip()
    nivel = int(row["nivel"]) if not np.isnan(row["nivel"]) else None

    if nivel == 1:
        if cat in ["dress"]: return 1.1
        if cat in ["jumpsuit"]: return 1.2
        return np.nan
    if nivel == 2:
        if cat in ["skirt"]: return 2.1
        if cat in ["bottoms"]: return 2.2
        return np.nan
    if nivel == 3:
        if cat in ["top"]: return 3.1
        return np.nan
    if nivel == 4:
        if cat in ["outerwear"]: return 4.1
        if cat in ["scarf"]: return 4.2
        if cat in ["bag"]: return 4.3
        return np.nan
    return np.nan

def rellenar_categorias_faltantes(row):
    """Infiere la categoría y subcategoría buscando palabras clave en el nombre del producto si los campos están vacíos."""
    cat_actual = row.get('categoria_prenda', np.nan)
    sub_actual = row.get('subcategoria_prenda', np.nan)
    
    if pd.notna(cat_actual) and str(cat_actual).strip() != "":
        return pd.Series([cat_actual, sub_actual])

    nombre = str(row['nombre_producto']).lower()
    categoria = np.nan
    subcategoria = np.nan
    
    if any(x in nombre for x in ['scarf', 'foulard', 'bufanda']):
        categoria, subcategoria = 'scarf', 'scarf'
    elif any(x in nombre for x in ['bag', 'shopper', 'tote', 'bolso']):
        categoria, subcategoria = 'bag', 'shopper'
    elif 'shirt' in nombre and 't-shirt' not in nombre and 't-shit' not in nombre:
        categoria, subcategoria = 'top', 'shirt'
    elif any(x in nombre for x in ['blouse', 'blusa']):
        categoria, subcategoria = 'top', 'blouse'
    elif any(x in nombre for x in ['sweater', 'knit', 'jersey', 'pull']):
        categoria, subcategoria = 'top', 'sweaters'
    elif 'cardigan' in nombre:
        categoria, subcategoria = 'top', 'cardigan'
    elif any(x in nombre for x in ['top', 't-shirt', 'tee', 't-shit', 'camisa', 'camiseta']):
        categoria, subcategoria = 'top', 'top'
    elif any(x in nombre for x in ['short', 'bermuda']):
        categoria, subcategoria = 'bottoms', 'shorts'
    elif any(x in nombre for x in ['trousers', 'pant', 'culotte']):
        categoria, subcategoria = 'bottoms', 'trousers'
    elif any(x in nombre for x in ['jean', 'denim']): 
        categoria, subcategoria = 'bottoms', 'jeans'
    elif any(x in nombre for x in ['skirt', 'falda']):
        categoria, subcategoria = 'skirt', 'skirt'
    elif any(x in nombre for x in ['dress', 'vestido']):
        categoria, subcategoria = 'dress', 'dress'
    elif any(x in nombre for x in ['jumpsuit', 'dungaree', 'playsuit', 'mono', 'peto']):
        categoria, subcategoria = 'jumpsuit', 'jumpsuit'
    elif 'trench' in nombre:
        categoria, subcategoria = 'outerwear', 'trench'
    elif any(x in nombre for x in ['coat', 'parka', 'abrigo']):
        categoria, subcategoria = 'outerwear', 'coat'
    elif 'kimono' in nombre:
        categoria, subcategoria = 'outerwear', 'kimono'
    elif any(x in nombre for x in ['jacket', 'blazer', 'jakect', 'jackect', 'cazadora', 'chaqueta']):
        categoria, subcategoria = 'outerwear', 'jacket'
        
    return pd.Series([categoria, subcategoria])

def consolidar_categoria(row):
    """Escanea las columnas '_type'. Si encuentra valor, asigna categoría y usa el valor como subcategoría."""
    cat, sub = np.nan, np.nan
    type_map = {
        "top_type": "top", 
        "jump_suit_type": "jumpsuit", 
        "skirt_type": "skirt", 
        "dress_type": "dress", 
        "bag_type": "bag", 
        "outside_type": "outerwear", 
        "foulard_type": "scarf", 
        "down_part_type": "bottoms" 
    }
    
    for col_type, cat_name in type_map.items():
        if col_type in row.index and pd.notna(row[col_type]):
            cat = cat_name
            sub = row[col_type] 
            break
            
    if pd.isna(cat) and pd.notna(row.get("nombre_producto")):
        name_low = str(row["nombre_producto"]).lower()
        if "jeans" in name_low or "pant" in name_low: cat, sub = "bottoms", "trousers"
        elif "dress" in name_low: cat, sub = "dress", "dress"
        elif "top" in name_low or "shirt" in name_low: cat = "top"
        
    return pd.Series([cat, sub])

def recalcular_nivel(categoria):
    """Recalcula el nivel numérico (1, 2, 3, 4) basándose en la categoría de la prenda ya rellenada."""
    if pd.isna(categoria): return np.nan
    cat = str(categoria).lower().strip()
    if cat in ["dress", "jumpsuit"]: return 1
    elif cat in ["bottoms", "skirt"]: return 2
    elif cat == "top": return 3
    elif cat in ["outerwear", "bag", "scarf"]: return 4
    return np.nan

def get_level(cat):
    if cat in ["dress", "jumpsuit"]: return 1
    elif cat in ["bottoms", "skirt"]: return 2
    elif cat == "top": return 3
    elif cat in ["outerwear", "bag", "scarf"]: return 4
    return np.nan

# =============================================================================
# 5. FUNCIONES UTILIZADAS EN ANALISIS_GRAFO.IPYNB
# =============================================================================
def filtrar_triangulos(triangulos, nivel_dict):
    """Filtra los triángulos en base a las condiciones de niveles de los nodos."""
    def cumple_condiciones(triangle):
        niveles = [nivel_dict[nodo] for nodo in triangle]
        if 1 in niveles:
            nivel_1_index = niveles.index(1)
            restantes = [niveles[i] for i in range(3) if i != nivel_1_index]
            return restantes.count(4) == 2
        if 2 in niveles:
            nivel_2_index = niveles.index(2)
            restantes = [niveles[i] for i in range(3) if i != nivel_2_index]
            return restantes.count(3) == 1 and restantes.count(4) == 1
        return False
    return list(filter(cumple_condiciones, triangulos))

def mostrar_look(triangulo, df, triangulos_filtrados):
    """Muestra un look filtrado según los triángulos seleccionados."""
    df_triangulo = df.iloc[list(triangulos_filtrados[triangulo])]      
    columnas_sin_nulos = df_triangulo.columns[~df_triangulo.isna().any()]
    display(df_triangulo[columnas_sin_nulos])