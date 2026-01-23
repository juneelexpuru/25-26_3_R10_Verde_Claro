# 25-26_3_R10_Verde_Claro

# Reto 10: Lookiero

Este repositorio contiene el desarrollo del **Reto 10**, centrado en la optimización del User Experience (UX) y la implementación de un sistema inteligente de generación de looks utilizando Teoría de Grafos, Machine Learning y Streaming.

## 👥 Equipo Verde Claro:
* **Libe Arana Carrascal**
* **Jon Ayala Lecea**
* **June Elexpuru Domínguez**
* **Markel Jorge Gomez**
* **Vega Lopez De Lapuente**
* **Martin Martinez Orive**

---

## 📂 Estructura del Proyecto
## 📂 Estructura del Proyecto

```text
RETO10_entrega/
│
├── datos/                  
│   ├── Originales/         
│   │   ├── Datos_look&like/
│   │   │   ├── customers_data_2.csv
│   │   │   ├── items_data.csv
│   │   │   └── look_and_like_data_2.csv 
│   │   ├── Datos_looks/
│   │   │   ├── brand.csv
│   │   │   ├── color.csv
│   │   │   ├── feature.csv
│   │   │   ├── feature_value.csv
│   │   │   ├── feature_value_family.csv
│   │   │   ├── product_2.csv
│   │   │   ├── product_feature_value.csv
│   │   │   ├── product_feature_value_qualifier.csv
│   │   │   ├── product_variant.csv
│   │   │   ├── season.csv
│   │   │   └── size.csv 
│   │   └── Datos_UX/
│   │       └── page_views_2.csv 
│   │
│   └── Transformados/        # Datos procesados listos para el modelo
│       ├── combinaciones_final.csv
│       ├── completo_combinaciones_colores.csv
│       ├── df_expandido.csv
│       ├── df_grafo_final.csv
│       ├── df_resultado.csv
│       └── resultados_looks_optimizado.csv 
│
├── Modelos/
│   ├── grap.gml         
│   └── Modelo_GAT.pth           
│
├── Scripts/                   # Orden de ejecución
│   ├── Preprocesamiento.ipynb # 1        
│   ├── Creacion_Grafo.ipynb   # 2
│   ├── Analisis_Grafo.ipynb   # 3
│   ├── Modelo.ipynb           # 4 
│   ├── funciones.py
│   ├── AnalisisUX.py
│   ├── looklikeanalisis.ipynb.py
│
├── Graficos/          
│
├── FlujoStreaming/
│   ├── templates/
│   │   └── index.html
│   ├── consumer_graph.py
│   ├── funciones.py
│   └── producer_app.py 
│
├── web/             
│   ├── dashboard.html
│   ├── index.html
│   ├── info.html
│   ├── looks.html
│   ├── look.png
│   ├── Look1.png
│   ├── Look2.png
│   ├── Look3.png
│   ├── Look4.png
│   ├── Look5.png
│   ├── Look6.png
│   ├── Look7.png
│   ├── Look8.png
│   ├── Look9.png
│   ├── Look10.png
│   ├── lookiero_logo.jpg
│   └── style.css      
│
├── environmentR10VerdeClaro.txt        
└── README.md 
