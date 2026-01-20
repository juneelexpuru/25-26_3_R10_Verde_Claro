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

El código se ha organizado de forma modular. **Nota Importante:** Los datasets y modelos entrenados no se incluyen en el repositorio por política de privacidad y tamaño, pero deben ubicarse en la carpeta local `/data` para la ejecución de los scripts.

```text
RETO-10-LOOKIERO/
│
├── datos/                   # CARPETA IGNORADA POR GIT (Colocar aquí los CSVs)
│   ├── originales/          # Datos originales (ej. productos.csv)
│   └── transformados/       # Datos limpios generados
│
├── modelos/                 # CARPETA IGNORADA POR GIT (Guardar aquí .pth / .pkl)
│
├── docs/                   # Documentación y entregables no-código
│   ├── ux_benchmarking/    # Informes de Benchmarking y Wireframes
│   └── images/             # Imágenes para el README o la Wiki
│
├── src/                    # Código Fuente Modular
│   ├── preprocessing/      # Scripts de limpieza y preparación
│   │   └── data_cleaner.py
│   │
│   ├── graphs/             # Lógica de Grafos y Generación de Looks
│   │   ├── graph_builder.py      # Construcción del grafo y cálculo de centralidad
│   │   └── look_generator.py     # Algoritmo de generación de outfits (reglas)
│   │
│   ├── mining/             # Machine Learning y Embeddings
│   │   ├── eda_look_like.py      # Análisis exploratorio Look&Like
│   │   └── node2vec_embed.py     # Generación de Graph Embeddings
│   │
│   ├── streaming/          # Arquitectura Big Data (Simulación)
│   │   ├── kafka_producer.py     # Simulación de entrada de nuevas prendas
│   │   └── kafka_consumer.py     # Ingesta y procesamiento en tiempo real
│   │
│   └── web/                # Visualización Frontend
│       ├── index.html
│       ├── css/
│       └── js/             # Scripts D3.js para visualización
│
├── requirements.txt        # Librerías necesarias (NetworkX, PyTorch, Kafka, etc.)
└── README.md               # Documentación del proyecto
