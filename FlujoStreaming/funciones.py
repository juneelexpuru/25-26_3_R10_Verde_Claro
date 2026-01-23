import pandas as pd
import numpy as np



COMPATIBILIDAD_ESTILOS = {
    'boho':    {'boho', 'casual', 'street', 'minimal'},
    'casual':  {'casual', 'boho', 'street', 'smart', 'minimal'},
    'street':  {'street', 'casual', 'boho', 'night', 'minimal'},
    'classic': {'classic', 'smart', 'night', 'minimal'},
    'smart':   {'smart', 'classic', 'casual', 'night', 'minimal'},
    'night':   {'night', 'street', 'classic', 'smart', 'minimal'},
    'minimal': {'minimal', 'boho', 'casual', 'classic', 'street', 'night', 'smart'}
}

COMPATIBILIDAD_APPLICATION = {
    'freetime':         {'freetime', 'working_girl', 'night','special_occasion'},
    'work':             {'work', 'working_girl', 'special_occasion'},
    'working_girl':     {'working_girl', 'work', 'freetime'},
    'night':            {'night', 'freetime', 'working_girl', 'special_occasion'},
    'special_occasion': {'special_occasion', 'night', 'work', 'freetime'}
}



def regla_nivel(nivel1, nivel2):
    try:
        n1, n2 = int(nivel1), int(nivel2)
    except:
        return False 

    if n1 == 1 and n2 == 4: return True
    if n1 == 2 and n2 in [3, 4]: return True
    if n1 == 3 and n2 in [2, 4]: return True
    if n1 == 4 and n2 in [1, 2, 3, 4]: return True
    

    if n1 == n2 and n1 == 4: return True 

    return False

def regla_categoria(categoria1, categoria2, nivel1, nivel2):
    if nivel1 == 4 and nivel2 == 4:
        if categoria1 == categoria2:
            return False
        return True
    

    if categoria1 == categoria2:
        return False
        
    return True

def regla_estilo(style1, style2):
    s1 = str(style1).strip().lower()
    compatibles = COMPATIBILIDAD_ESTILOS.get(s1, {s1})
    s2 = str(style2).strip().lower()
    return s2 in compatibles

def regla_adventurous(adv1, adv2):
    try:
        return abs(int(adv1) - int(adv2)) <= 1
    except:
        return True 

def regla_weather(weather1, weather2): 
    """Compatibilidad de clima"""
    w1 = str(weather1).strip()
    w2 = str(weather2).strip()
    
    compatibles = [
        ("warm", "warm_season"),
        ("cold", "cold_season"),
        ("all_weather", "cold"),
        ("all_weather", "warm"),
        ("all_weather", "warm_season"),
        ("all_weather", "cold_season")
    ]
    
    if w1 == w2: return True
    if (w1, w2) in compatibles: return True
    if (w2, w1) in compatibles: return True
    
    return False

def regla_application(app1, app2):
    a1 = str(app1).strip().lower()
    a2 = str(app2).strip().lower()
    
    compatibles = COMPATIBILIDAD_APPLICATION.get(a1, {a1})
    return a2 in compatibles

def regla_color(color1, color2):
    """
    Evalúa si dos colores combinan leyendo el CSV (si existe).
    Nota: Esta función requiere que el CSV esté cargado o accesible.
    Para el Consumer, usamos la lógica interna del script consumer, 
    pero la dejamos aquí por compatibilidad.
    """
    try:
        # Intentamos leer solo si es necesario, aunque es ineficiente hacerlo fila por fila.
        # Lo ideal es cargar el CSV fuera (en el consumer.py) y pasar el set de colores validos.
        # Esta función queda como placeholder.
        return True 
    except:
        return False