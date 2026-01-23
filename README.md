RETO-10-LOOKIERO/
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
│   │   │   ├── desktop.ini
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
├── Scripts/                   # orden de ejecución
│   ├── Preprocesamiento.ipynb # 1        
│   └── Creacion_Grafo.ipynb   # 2
│   └── Analisis_Grafo.ipynb   # 3
│   └── Modelo.ipynb           # 4 
│   └── funciones.py
│   │
│   ├── Graficos/            
│   │
├── FlujoStreaming/
│   ├── templates/
│   │     │ index.html
│   consumer_graph.py
│   funciones.py
│   producer_app.py
│   │
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
