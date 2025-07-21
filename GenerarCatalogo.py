import pandas as pd
from jinja2 import Template
import os
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
# 2. PLANTILLA HTML CON PAGINACIÓN, FILTRO, MODALES Y BOTÓN OCULTO CON CONTRASEÑA
# =============================================
html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Catálogo de Productos</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body { background-color: #f8f9fa; padding-top: 20px; }
    .card { transition: transform 0.3s; border: none; border-radius: 10px; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .card-img-top { cursor: pointer; border-radius: 10px 10px 0 0; object-fit: contain; height: 200px; padding: 10px; }
    .whatsapp-btn { background-color: #25D366 !important; border-color: #25D366 !important; }
    .text-decoration-line-through { text-decoration: line-through; }
    #hiddenTrigger { cursor: default; user-select: none; }
  </style>
</head>
<body>
  <div class="container" id="top">
    <!-- Título con botón oculto 🎁 -->
    <h1 class="text-center mb-4 text-primary" id="hiddenTrigger" title="Haz clic 5 veces rápido aquí">
      🎁 Catálogo de Ofertas 🔥
    </h1>

    <!-- Buscador principal -->
    <div class="mb-4 text-center">
      <input id="filtro" type="text" class="form-control w-50 d-inline" placeholder="🔍 Buscar productos..." />
    </div>

    <!-- Productos -->
    <div class="row" id="productos">
      {% for producto in productos %}
      <div class="col-md-4 mb-4 producto">
        <div class="card h-100 shadow">
{% set imagenes = producto.ImagenURL.split(';') %}
{% if imagenes|length > 1 %}
  <div id="carousel-{{ loop.index }}" class="carousel slide" data-bs-ride="carousel">
    <div class="carousel-inner">
      {% for img in imagenes %}
        <div class="carousel-item {% if loop.first %}active{% endif %}">
          <img src="{{ img.strip() }}" class="d-block w-100 card-img-top" alt="{{ producto.Nombre }}" loading="lazy" onerror="this.src='{{ producto.LinkCompra|urlencode }}'">
        </div>
      {% endfor %}
    </div>
    <button class="carousel-control-prev" type="button" data-bs-target="#carousel-{{ loop.index }}" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Anterior</span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target="#carousel-{{ loop.index }}" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Siguiente</span>
    </button>
  </div>
{% else %}
  <img src="{{ imagenes[0] }}" class="card-img-top" alt="{{ producto.Nombre }}" loading="lazy" onerror="this.src='{{ producto.LinkCompra|urlencode }}'">
{% endif %}
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

    <!-- Paginación principal -->
    <nav>
      <ul class="pagination justify-content-center" id="paginacion"></ul>
    </nav>
  </div>

  <!-- Modal Imagen Ampliada -->
  <div class="modal fade" id="imageModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content bg-transparent border-0">
        <img id="modalImage" src="" class="img-fluid rounded" alt="Imagen ampliada" />
      </div>
    </div>
  </div>

  <!-- Modal Lista con filtro -->
  <div class="modal fade" id="listaModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Lista de Productos</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body" id="modalListaBody" style="max-height: 70vh; overflow-y: auto;">
          <input type="text" id="filtroModal" class="form-control mb-3" placeholder="🔍 Buscar en la lista..." />
          <!-- La tabla se inyectará aquí -->
        </div>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9490673865072179"
     crossorigin="anonymous"></script>
  <script>
    // Variables para paginación y filtrado
    const allItems = Array.from(document.querySelectorAll('.producto'));
    let filtered = [...allItems];
    const pageSize = 18;
    let currentPage = 1;

    // Renderiza página principal
    function renderPage(items, page) {
      allItems.forEach(el => el.style.display = 'none');
      const start = (page - 1) * pageSize;
      items.slice(start, start + pageSize).forEach(el => el.style.display = 'block');
    }

    // Renderiza paginación principal
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

      container.appendChild(makeLi('«', currentPage - 1, currentPage === 1));

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

      container.appendChild(makeLi('»', currentPage + 1, currentPage === totalPages));
    }

    // Scroll suave al top
    function scrollToTop() {
      document.getElementById('top').scrollIntoView({ behavior: 'smooth' });
    }

    // Actualiza la lista principal
    function update() {
      renderPage(filtered, currentPage);
      renderPagination(filtered);
    }

    // Remueve acentos para filtro insensible
    function removeAccents(str) {
      return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }

    // Evento filtro principal
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

    // Inicializar lista principal
    update();

    // Modal imagen grande
    document.querySelectorAll('.card-img-top').forEach(img => {
      img.addEventListener('click', () => {
        const modalImage = document.getElementById('modalImage');
        modalImage.src = img.src;
        new bootstrap.Modal(document.getElementById('imageModal')).show();
      });
    });

    // BOTÓN OCULTO: Detectar 5 clics en 🎁 para pedir contraseña y mostrar lista
    const hiddenTrigger = document.getElementById('hiddenTrigger');
    let clickCount = 0;
    let clickTimeout;

    hiddenTrigger.addEventListener('click', () => {
      clickCount++;
      clearTimeout(clickTimeout);
      clickTimeout = setTimeout(() => {
        clickCount = 0;
      }, 2000); // Resetea contador después de 2 segundos sin clics

      if (clickCount === 5) {
        clickCount = 0;
        const password = prompt("Ingrese la contraseña:");
        if(password === "Zombie") {
          mostrarLista();
        } else {
          alert("Contraseña incorrecta");
        }
      }
    });

    // Función para generar y mostrar tabla completa en modal lista
    function mostrarLista() {
      const modalBody = document.getElementById('modalListaBody');
      // Limpiar antes
      modalBody.querySelector('table')?.remove();

      // Crear tabla con Bootstrap y scroll vertical limitado
      const table = document.createElement('table');
      table.className = 'table table-striped table-hover table-sm';
      table.style.width = '100%';

      // Encabezado tabla
      const thead = document.createElement('thead');
      thead.innerHTML = `
        <tr>
          <th>Nombre</th>
          <th>Precio</th>
          <th>Link Compra</th>
          <th>Caja</th>
        </tr>
      `;
      table.appendChild(thead);

      // Cuerpo tabla
      const tbody = document.createElement('tbody');

      // Los datos vienen de Jinja, vamos a usar la variable productos
      const productos = {{ productos|tojson|safe }};
      productos.forEach(p => {
        const tr = document.createElement('tr');

        // LinkCompra con etiqueta <a> que abre en nueva pestaña
        const linkCompraHTML = p.LinkCompra ? `<a href="${p.LinkCompra}" target="_blank" rel="noopener noreferrer">Abrir enlace</a>` : '';

        tr.innerHTML = `
          <td>${p.Nombre}</td>
          <td>$${p.Precio.toFixed(2)}</td>
          <td>${linkCompraHTML}</td>
          <td>${p.Caja || ''}</td>
        `;
        tbody.appendChild(tr);
      });

      table.appendChild(tbody);
      modalBody.appendChild(table);

      // Abrir modal lista
      new bootstrap.Modal(document.getElementById('listaModal')).show();
    }

    // FILTRO para tabla en modal lista
    document.addEventListener('input', (e) => {
      if(e.target && e.target.id === 'filtroModal') {
        const term = e.target.value.toLowerCase();
        const tabla = document.querySelector('#modalListaBody table tbody');
        if (!tabla) return;
        Array.from(tabla.rows).forEach(row => {
          const textoFila = row.innerText.toLowerCase();
          row.style.display = textoFila.includes(term) ? '' : 'none';
        });
      }
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