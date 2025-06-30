import pandas as pd
from jinja2 import Template
import os
from urllib.parse import quote  # Para codificar el texto en URLs
import webbrowser
# =============================================
# CONFIGURACIÓN DE RUTAS (¡AJUSTA ESTO!)
# =============================================
SCRIPT_DIR = r"C:\Users\Lpz_p\Desktop\Mi Proyecto Gib\Catalogo"
EXCEL_PATH = os.path.join(SCRIPT_DIR, "productos.xlsx")
OUTPUT_HTML = os.path.join(SCRIPT_DIR, "index.html")

# =============================================
# 1. LEER EL ARCHIVO EXCEL/CSV Y LIMPIAR DATOS
# =============================================
try:
    df = pd.read_excel(EXCEL_PATH)
    df = df.sample(frac=1).reset_index(drop=True)  # Mezcla aleatoriamente los productos
    
    # Limpiar símbolo $ del precio
    df['Precio'] = df['Precio'].replace(r'[\$,]', '', regex=True).astype(float)
    df['PrecioRebaja'] = pd.to_numeric(df.get('PrecioRebaja'), errors='coerce')

    print("✅ Archivo Excel leído y procesado correctamente")
except Exception as e:
    print(f"❌ Error al leer el archivo: {e}")
    exit()

# =============================================
# 2. PLANTILLA HTML CON PAGINACIÓN Y FILTRO DINÁMICO CORREGIDO
# =============================================
html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <title>Catálogo de Productos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .card { transition: transform 0.3s; border: none; border-radius: 10px; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        .card-img-top { border-radius: 10px 10px 0 0; object-fit: contain; height: 200px; padding: 10px; }
        body { background-color: #f8f9fa; padding-top: 20px; }
        .whatsapp-btn { background-color: #25D366 !important; border-color: #25D366 !important; }
        .text-decoration-line-through { text-decoration: line-through; }
        .pagination { justify-content: center; }
        .page-item.disabled .page-link { pointer-events: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4 text-primary">🎁 Catálogo de Ofertas 🔥</h1>

        <!-- Buscador -->
        <div class="mb-4 text-center">
            <input id="filtro" type="text" class="form-control w-50 d-inline" placeholder="🔍 Buscar productos...">
        </div>

        <div class="row" id="productos">
            {% for producto in productos %}
            <div class="col-md-4 mb-4 producto">
                <div class="card h-100 shadow">
                    <img 
                        src="{{ producto.ImagenURL }}" 
                        class="card-img-top" 
                        alt="{{ producto.Nombre }}"
                        loading="lazy"
                        onerror="this.src='{{ producto.LinkCompra|urlencode }}'"
                    >
                    <div class="card-body">
                        <h5 class="card-title nombre">{{ producto.Nombre }}</h5>
                        <p class="card-text text-muted descripcion">{{ producto.Descripción }}</p>
                        {% if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 %}
                            {% set descuento = ((producto.Precio - producto.PrecioRebaja) / producto.Precio * 100) | round(0, 'floor') %}
                            <p class="text-success fw-bold precio">
                                ${{ "%.2f"|format(producto.PrecioRebaja) }} <span class="badge bg-danger ms-2">-{{ descuento }}%</span>
                            </p>
                            <p class="text-muted text-decoration-line-through small mb-0">${{ "%.2f"|format(producto.Precio) }}</p>
                        {% else %}
                            <p class="text-success fw-bold precio">${{ "%.2f"|format(producto.Precio) }}</p>
                        {% endif %}
                    </div>
                    <div class="card-footer bg-white">
                        <a href="https://wa.me/526678191185?text=¡Estoy+interesado+en+{{ producto.Nombre|urlencode }}%0APrecio:+{{ (producto.PrecioRebaja or producto.Precio)|urlencode }}%0AURL:+{{ producto.ImagenURL|urlencode }}" class="btn whatsapp-btn text-white w-100" target="_blank">📱 Contactar</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Controles de paginación -->
        <nav>
            <ul class="pagination" id="paginacion"></ul>
        </nav>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const allItems = Array.from(document.querySelectorAll('.producto'));
        let filtered = [...allItems];
        const pageSize = 12;
        let currentPage = 1;

        function renderPage(items, page) {
            // Primero ocultar todos
            allItems.forEach(el => el.style.display = 'none');
            // Luego mostrar solo los de la página actual
            const start = (page - 1) * pageSize;
            items.slice(start, start + pageSize).forEach(el => el.style.display = 'block');
        }

        function renderPagination(items) {
            const totalPages = Math.ceil(items.length / pageSize) || 1;
            const container = document.getElementById('paginacion');
            container.innerHTML = '';
            const createLi = (label, page, disabled=false, active=false) => {
                const li = document.createElement('li');
                li.className = `page-item${disabled?' disabled':''}${active?' active':''}`;
                const a = document.createElement('a');
                a.className = 'page-link'; a.href='#'; a.innerText = label;
                a.addEventListener('click', e => { e.preventDefault(); if(!disabled){ currentPage=page; update(); }});
                li.appendChild(a);
                return li;
            };
            container.appendChild(createLi('«', currentPage-1, currentPage===1));
            for(let p=1; p<=totalPages; p++){
                container.appendChild(createLi(p, p, false, currentPage===p));
            }
            container.appendChild(createLi('»', currentPage+1, currentPage===totalPages));
        }

        function update() {
            renderPage(filtered, currentPage);
            renderPagination(filtered);
        }

        document.getElementById('filtro').addEventListener('input', function(){
            const term = this.value.toLowerCase();
            filtered = allItems.filter(el => {
                const txt = [
                    el.querySelector('.nombre').innerText,
                    el.querySelector('.descripcion').innerText,
                    el.querySelector('.precio').innerText
                ].join(' ').toLowerCase();
                return txt.includes(term);
            });
            currentPage = 1;
            update();
        });

        // Inicialización
        update();
    </script>
</body>
</html>
"""

# =============================================
# 3. GENERAR HTML
# =============================================
try:
    template = Template(html_template)
    html_output = template.render(productos=df.to_dict("records"))

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"✅ Catálogo generado en: {OUTPUT_HTML}")
    print("📂 Abre el archivo en tu navegador para verlo.")
    webbrowser.open(f"file://{OUTPUT_HTML}")
except Exception as e:
    print(f"❌ Error al generar el HTML: {e}")
