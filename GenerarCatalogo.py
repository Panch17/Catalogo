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
    df['Precio'] = df['Precio'].replace(r'[\$,]', '', regex=True).astype(float)
    df['PrecioRebaja'] = pd.to_numeric(df.get('PrecioRebaja'), errors='coerce')
    print("✅ Archivo Excel leído y procesado correctamente")
except Exception as e:
    print(f"❌ Error al leer el archivo: {e}")
    exit()

# =============================================
# 2. PLANTILLA HTML CON PAGINACIÓN CON SOLO 5 BOTONES, FILTRO Y MODAL DE IMAGEN
# =============================================
html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catálogo de Productos</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background-color: #f8f9fa; padding-top: 20px; }
    .card { transition: transform 0.3s; border: none; border-radius: 10px; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .card-img-top { cursor: pointer; border-radius: 10px 10px 0 0; object-fit: contain; height: 200px; padding: 10px; }
    .whatsapp-btn { background-color: #25D366 !important; border-color: #25D366 !important; }
    .text-decoration-line-through { text-decoration: line-through; }
  </style>
</head>
<script src="https://cdn.counter.dev/script.js" data-id="a385688b-fca9-43be-90f6-bf9fff769d46" data-utcoffset="-7"></script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9490673865072179"
     crossorigin="anonymous"></script>
<body>
  <div class="container" id="top">
    <h1 class="text-center mb-4 text-primary">🎁 Catálogo de Ofertas 🔥</h1>

    <!-- Buscador -->
    <div class="mb-4 text-center">
      <input id="filtro" type="text" class="form-control w-50 d-inline" placeholder="🔍 Buscar productos...">
    </div>

    <div class="row" id="productos">
      {% for producto in productos %}
      <div class="col-md-4 mb-4 producto">
        <div class="card h-100 shadow">
          <img src="{{ producto.ImagenURL }}" class="card-img-top" alt="{{ producto.Nombre }}" loading="lazy" onerror="this.src='{{ producto.LinkCompra|urlencode }}'">
          <div class="card-body">
            <h5 class="card-title nombre">{{ producto.Nombre }}</h5>
            <p class="card-text text-muted descripcion">{{ producto.Descripción }}</p>
            {% if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 %}
              {% set desc = ((producto.Precio - producto.PrecioRebaja)/producto.Precio*100)|round(0,'floor') %}
              <p class="text-success fw-bold precio">${{ "%.2f"|format(producto.PrecioRebaja) }} <span class="badge bg-danger ms-2">-{{ desc }}%</span></p>
              <p class="text-muted text-decoration-line-through small mb-0">${{ "%.2f"|format(producto.Precio) }}</p>
            {% else %}
              <p class="text-success fw-bold precio">${{ "%.2f"|format(producto.Precio) }}</p>
            {% endif %}
          </div>
          <div class="card-footer bg-white">
            <a href="https://wa.me/526678191185?text=¡Estoy+interesado+en+{{ producto.Nombre|urlencode }}%0APrecio:+{{ (producto.PrecioRebaja if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 else producto.Precio)|urlencode }}%0AURL:+{{ producto.ImagenURL|urlencode }}" class="btn whatsapp-btn text-white w-100" target="_blank">📱 Contactar</a>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>

    <!-- Paginación -->
    <nav>
      <ul class="pagination justify-content-center" id="paginacion"></ul>
    </nav>
  </div>

  <!-- Modal Imagen -->
  <div class="modal fade" id="imageModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content bg-transparent border-0">
        <img id="modalImage" src="" class="img-fluid rounded" alt="Imagen ampliada">
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    const allItems = Array.from(document.querySelectorAll('.producto'));
    let filtered = [...allItems];
    const pageSize = 18;
    let currentPage = 1;

    function renderPage(items, page) {
      allItems.forEach(el => el.style.display = 'none');
      const start = (page - 1) * pageSize;
      items.slice(start, start + pageSize).forEach(el => el.style.display = 'block');
    }

    function renderPagination(items) {
      const totalPages = Math.ceil(items.length / pageSize) || 1;
      const container = document.getElementById('paginacion');
      container.innerHTML = '';
      const makeLi = (label, page, disabled=false, active=false) => {
        const li = document.createElement('li');
        li.className = `page-item${disabled?' disabled':''}${active?' active':''}`;
        const a = document.createElement('a'); a.className = 'page-link'; a.href = '#'; a.innerText = label;
        a.addEventListener('click', e => { e.preventDefault(); if(!disabled){ currentPage = page; update(); scrollToTop(); }});
        li.appendChild(a);
        return li;
      };

      // Flecha anterior
      container.appendChild(makeLi('«', currentPage - 1, currentPage === 1));

      // Ventana de 5 botones
      const maxButtons = 5;
      const half = Math.floor(maxButtons / 2);
      let startPage = Math.max(1, currentPage - half);
      let endPage = Math.min(totalPages, currentPage + half);
      if (endPage - startPage + 1 < maxButtons) {
        if (startPage === 1) endPage = Math.min(totalPages, startPage + maxButtons - 1);
        else if (endPage === totalPages) startPage = Math.max(1, endPage - maxButtons + 1);
      }

      if (startPage > 1) {
        container.appendChild(makeLi('1', 1, false, currentPage === 1));
        if (startPage > 2) {
          const dots = document.createElement('li'); dots.className = 'page-item disabled'; dots.innerHTML = '<span class="page-link">…</span>';
          container.appendChild(dots);
        }
      }

      for (let p = startPage; p <= endPage; p++) {
        container.appendChild(makeLi(p, p, false, currentPage === p));
      }

      if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
          const dots = document.createElement('li'); dots.className = 'page-item disabled'; dots.innerHTML = '<span class="page-link">…</span>';
          container.appendChild(dots);
        }
        container.appendChild(makeLi(totalPages, totalPages, false, currentPage === totalPages));
      }

      // Flecha siguiente
      container.appendChild(makeLi('»', currentPage + 1, currentPage === totalPages));
    }

    function scrollToTop() {
      document.getElementById('top').scrollIntoView({ behavior: 'smooth' });
    }

    function update() {
      renderPage(filtered, currentPage);
      renderPagination(filtered);
    }

    function removeAccents(str) {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

    document.getElementById('filtro').addEventListener('input', function() {
      const term = removeAccents(this.value.toLowerCase());

      filtered = allItems.filter(el => {
        const texto = [
          el.querySelector('.nombre').innerText,
          el.querySelector('.descripcion').innerText,
          el.querySelector('.precio').innerText
        ].join(' ').toLowerCase();

        return removeAccents(texto).includes(term);
      });

      currentPage = 1;
      update();
      scrollToTop();
    });


    // Inicializar
    update();
    // Modal
    document.querySelectorAll('.card-img-top').forEach(img => {
      img.addEventListener('click', () => {
        document.getElementById('modalImage').src = img.src;
        new bootstrap.Modal(document.getElementById('imageModal')).show();
      });
    });
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