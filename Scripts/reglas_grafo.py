import pandas as pd
import numpy as np

# ==========================================
# 1. DICCIONARIOS DE COMPATIBILIDAD (RELAJADOS)
# ==========================================

COMPATIBILIDAD_ESTILOS = {
    'boho': {'boho', 'casual', 'street', 'minimal', 'warm_season'},
    'casual': {'casual', 'boho', 'street', 'smart', 'minimal', 'classic', 'sport'},
    'street': {'street', 'casual', 'boho', 'night', 'minimal', 'modern'},
    'classic': {'classic', 'smart', 'night', 'minimal', 'casual'},
    'smart': {'smart', 'classic', 'casual', 'night', 'minimal'},
    'night': {'night', 'street', 'classic', 'smart', 'minimal', 'party'},
    'minimal': {'minimal', 'boho', 'casual', 'classic', 'street', 'night', 'smart'}
}

COMPATIBILIDAD_APPLICATION = {
    'freetime': {'freetime', 'working_girl', 'night', 'special_occasion', 'work'},
    'work': {'work', 'working_girl', 'special_occasion', 'classic'},
    'working_girl': {'working_girl', 'work', 'freetime', 'smart'},
    'night': {'night', 'freetime', 'working_girl', 'special_occasion', 'party'},
    'special_occasion': {'special_occasion', 'night', 'work', 'freetime'}
}

# ==========================================
# 2. FUNCIONES DE LIMPIEZA Y REGLAS
# ==========================================

def clean_str(val):
    """Limpia strings y maneja valores nulos/unknown."""
    if pd.isna(val) or str(val).lower() in ['nan', 'unknown', 'none', '']:
        return None
    return str(val).split(',')[0].strip().lower()

def regla_nivel(nivel1, nivel2):
    """
    Regla Estructural: Qué prendas pueden ir juntas físicamente.
    Esta es la única regla estricta que mantenemos.
    """
    try:
        n1, n2 = int(nivel1), int(nivel2)
    except:
        return False 
        
    if n1 == 1 and n2 == 4: return True # Cuerpo entero + Exterior/Accesorios
    if n1 == 2 and n2 in [3, 4]: return True # Abajo + Arriba o Exterior
    if n1 == 3 and n2 in [2, 4]: return True # Arriba + Abajo o Exterior
    if n1 == 4 and n2 in [1, 2, 3, 4]: return True # Exterior con todo
    return False

def regla_categoria(c1, c2, n1, n2):
    """Evita duplicar categorías en accesorios (ej. dos bolsos)."""
    if n1 == 4 and n2 == 4:
        return c1 != c2
    return True

def regla_estilo(style1, style2):
    """
    Regla de Estilo (Flexible):
    - Si falta el dato (None) -> True (Ante la duda, conecta).
    - Si es un estilo básico/casual -> True (Comodín).
    """
    s1 = clean_str(style1)
    s2 = clean_str(style2)
    
    # Comodín 1: Si no hay dato, permitimos la conexión
    if s1 is None or s2 is None: return True
    
    # Comodín 2: Estilos universales que pegan con todo
    universales = {'casual', 'minimal', 'basic', 'neutral', 'sport', 'modern'}
    if s1 in universales or s2 in universales: return True

    compatibles = COMPATIBILIDAD_ESTILOS.get(s1, {s1})
    return s2 in compatibles or s1 in COMPATIBILIDAD_ESTILOS.get(s2, {s2})

def regla_adventurous(adv1, adv2):
    """
    Regla de Atrevimiento (Flexible):
    - Permite diferencia de hasta 2 puntos.
    """
    try:
        return abs(int(adv1) - int(adv2)) <= 2
    except:
        return True # Si es nulo, conecta

def regla_weather(w1, w2): 
    """
    Regla de Clima (Flexible):
    - 'all_weather' conecta con todo.
    """
    w1 = clean_str(w1)
    w2 = clean_str(w2)
    
    if w1 is None or w2 is None: return True
    if 'all' in w1 or 'all' in w2: return True # all_weather comodín
    
    compatibles = [("warm", "warm_season"), ("cold", "cold_season")]
    return w1 == w2 or (w1, w2) in compatibles or (w2, w1) in compatibles

def regla_application(a1, a2):
    """Regla de Ocasión (Flexible)."""
    a1 = clean_str(a1)
    a2 = clean_str(a2)
    if a1 is None or a2 is None: return True
    compatibles = COMPATIBILIDAD_APPLICATION.get(a1, {a1})
    return a2 in compatibles