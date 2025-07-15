import pandas as pd
from jinja2 import Template
import os
import webbrowser

# =============================================
# CONFIGURACIÓN DE RUTAS
# =============================================
SCRIPT_DIR = r"C:\Users\Lpz_p\Desktop\Mi Proyecto Gib\Catalogo"
EXCEL_PATH = os.path.join(SCRIPT_DIR, "productos.xlsx")
OUTPUT_HTML = os.path.join(SCRIPT_DIR, "index.html")

# =============================================
# 1. LEER EXCEL
# =============================================
try:
    df = pd.read_excel(EXCEL_PATH)
    df = df.sample(frac=1).reset_index(drop=True)
    df['Precio'] = df['Precio'].replace(r'[\$,]', '', regex=True).astype(float)
    df['PrecioRebaja'] = pd.to_numeric(df.get('PrecioRebaja'), errors='coerce')
    print("✅ Archivo Excel procesado")
except Exception as e:
    print(f"❌ Error al leer el archivo: {e}")
    exit()

# =============================================
# 2. PLANTILLA HTML CON TOQUE DRAGON BALL
# =============================================
html_template = """
<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Catálogo Z</title>
  <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\" />
  <style>
    body {
      background: url('https://wallpapercave.com/wp/wp1890471.jpg') no-repeat center center fixed;
      background-size: cover;
      padding-top: 30px;
      color: white;
    }
    .container {
      background: rgba(0,0,0,0.75);
      padding: 30px;
      border-radius: 15px;
    }
    h1 {
      font-family: 'Impact', sans-serif;
      font-size: 3rem;
      color: #FFD700;
      text-shadow: 2px 2px #000;
    }
    .card {
      transition: transform 0.3s;
      border-radius: 15px;
      background-color: #fff;
    }
    .card:hover {
      transform: scale(1.03);
      box-shadow: 0 10px 25px rgba(255,255,255,0.2);
    }
    .card-title {
      color: #e67e22;
      font-weight: bold;
    }
    .whatsapp-btn {
      background-color: #25D366 !important;
    }
  </style>
</head>
<body>
  <div class=\"container\">
    <h1 class=\"text-center mb-4\">🔥 Catálogo Saiyajin 🔥</h1>
    <div class=\"text-center mb-3\">
      <input type=\"text\" id=\"filtro\" class=\"form-control w-50 d-inline\" placeholder=\"🔍 Buscar...\">
    </div>
    <div class=\"row\" id=\"productos\">
      {% for producto in productos %}
      <div class=\"col-md-4 mb-4 producto\">
        <div class=\"card\">
          <img src=\"{{ producto.ImagenURL }}\" class=\"card-img-top p-3\" alt=\"{{ producto.Nombre }}\">
          <div class=\"card-body\">
            <h5 class=\"card-title nombre\">{{ producto.Nombre }}</h5>
            <p class=\"descripcion text-muted\">{{ producto.Descripción }}</p>
            {% if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 %}
              <p class=\"fw-bold text-success precio\">${{ "%.2f"|format(producto.PrecioRebaja) }} <span class=\"badge bg-danger\">-{{ ((producto.Precio - producto.PrecioRebaja)/producto.Precio*100)|round(0,'floor') }}%</span></p>
              <p class=\"text-decoration-line-through text-muted\">${{ "%.2f"|format(producto.Precio) }}</p>
            {% else %}
              <p class=\"fw-bold text-success precio\">${{ "%.2f"|format(producto.Precio) }}</p>
            {% endif %}
          </div>
          <div class=\"card-footer bg-white\">
            <a href=\"https://wa.me/526678191185?text=Estoy+interesado+en+{{ producto.Nombre|urlencode }}\" class=\"btn whatsapp-btn w-100 text-white\">📱 Contactar</a>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
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

    function update() {
      renderPage(filtered, currentPage);
    }

    function removeAccents(str) {
      return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }

    document.getElementById('filtro').addEventListener('input', function() {
      const term = removeAccents(this.value.toLowerCase());
      filtered = allItems.filter(el => {
        const texto = el.innerText.toLowerCase();
        return removeAccents(texto).includes(term);
      });
      currentPage = 1;
      update();
    });

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
    webbrowser.open(f"file://{OUTPUT_HTML}")
except Exception as e:
    print(f"❌ Error al generar el HTML: {e}")
