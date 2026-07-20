import pandas as pd
from jinja2 import Template
import os
import webbrowser
import sys

# Configurar codificación UTF-8 para la consola
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# =============================================
# CONFIGURACIÓN DE RUTAS (¡AJUSTA ESTO!)
# =============================================
# SCRIPT_DIR = r"C:\Users\Lpz_p\Desktop\Mi Proyecto Gib\Catalogo"
# Usa la carpeta actual del script para evitar ajustes manuales de ruta.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Crear carpetas si no existen
DATOS_DIR = os.path.join(SCRIPT_DIR, "datos")
STYLE_DIR = os.path.join(SCRIPT_DIR, "style")
JS_DIR = os.path.join(SCRIPT_DIR, "js")

os.makedirs(DATOS_DIR, exist_ok=True)
os.makedirs(STYLE_DIR, exist_ok=True)
os.makedirs(JS_DIR, exist_ok=True)

# Rutas de archivos
EXCEL_PATH = os.path.join(DATOS_DIR, "productos.xlsx")
OUTPUT_HTML = os.path.join(SCRIPT_DIR, "index.html")
OUTPUT_CSS = os.path.join(STYLE_DIR, "style.css")
OUTPUT_JS = os.path.join(JS_DIR, "catalog.js")

# =============================================
# 1. LEER EL ARCHIVO EXCEL/CSV Y LIMPIAR DATOS
# =============================================
try:
    df = pd.read_excel(EXCEL_PATH)
    df = df.sample(frac=1).reset_index(drop=True)  # Mezcla aleatoriamente los productos
    df['Precio'] = df['Precio'].replace(r'[\$,]', '', regex=True).astype(float)
    df['PrecioRebaja'] = pd.to_numeric(df.get('PrecioRebaja'), errors='coerce')
    if 'ImagenURL' in df.columns:
      df['ImagenURL'] = df['ImagenURL'].fillna('').astype(str).replace('nan', '')
    if 'LinkCompra' in df.columns:
      df['LinkCompra'] = df['LinkCompra'].fillna('').astype(str).replace('nan', '')
    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].fillna('Otros').astype(str)
        df.loc[df['Categoria'].str.strip().str.lower() == 'seguridad', 'Categoria'] = 'Otros'
    else:
        df['Categoria'] = 'Otros'
    categorias = sorted(
        [c for c in df['Categoria'].dropna().unique().tolist() if str(c).strip() and str(c).strip().lower() != 'seguridad']
    )
    print("✅ Archivo Excel leído y procesado correctamente")
except Exception as e:
    print(f"❌ Error al leer el archivo: {e}")
    exit()

# =============================================
# 2. DEFINIR CSS
# =============================================
css_content = """@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700&family=Manrope:wght@400;500;700;800&display=swap');

:root {
  --primary-color: #ff5a36;
  --secondary-color: #00b894;
  --highlight-color: #f7c948;
  --bg-light: #f6f8ff;
  --bg-dark: #0f172a;
  --card-light: rgba(255, 255, 255, 0.92);
  --card-dark: rgba(15, 23, 42, 0.86);
  --title-font: 'Orbitron', sans-serif;
  --body-font: 'Manrope', sans-serif;
}

html {
  scroll-behavior: smooth;
}

body {
  background:
    radial-gradient(circle at 10% 10%, rgba(255, 90, 54, 0.12), transparent 35%),
    radial-gradient(circle at 90% 20%, rgba(0, 184, 148, 0.12), transparent 38%),
    var(--bg-light);
  padding-top: 20px;
  transition: background-color 0.3s ease, color 0.3s ease;
  color: #1f2937;
  font-family: var(--body-font);
}

body.dark-mode {
  background:
    radial-gradient(circle at 15% 10%, rgba(255, 90, 54, 0.2), transparent 35%),
    radial-gradient(circle at 85% 20%, rgba(0, 184, 148, 0.2), transparent 38%),
    linear-gradient(135deg, var(--bg-dark) 0%, #020617 100%);
  color: #e2e8f0;
}

.hero-panel {
  position: relative;
  margin-bottom: 18px;
  padding: 28px 24px;
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(255, 90, 54, 0.12), rgba(0, 184, 148, 0.12));
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 20px 35px rgba(0, 0, 0, 0.07);
  overflow: hidden;
}

.hero-panel::before {
  content: '';
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.28);
  top: -110px;
  right: -50px;
}

body.dark-mode .hero-panel {
  background: linear-gradient(145deg, rgba(255, 90, 54, 0.2), rgba(0, 184, 148, 0.18));
  border-color: rgba(148, 163, 184, 0.2);
}

.hero-kicker {
  font-size: 0.78rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  font-weight: 800;
  color: #fb5607;
  margin-bottom: 10px;
}

body.dark-mode .hero-kicker {
  color: #ffd166;
}

#hiddenTrigger.hero-title {
  font-family: var(--title-font);
  font-size: clamp(1.7rem, 4vw, 2.8rem);
  line-height: 1.15;
  margin: 0;
  user-select: none;
  cursor: default;
  text-shadow: 0 10px 22px rgba(255, 90, 54, 0.2);
  color: #0f172a;
}

body.dark-mode #hiddenTrigger.hero-title {
  color: #f8fafc;
  text-shadow: 0 12px 25px rgba(0, 0, 0, 0.4);
}

#hiddenTrigger.hero-title:hover {
  transform: translateY(-1px);
}

.hero-subtitle {
  margin: 12px 0 0;
  max-width: 820px;
  color: #334155;
  font-weight: 500;
}

body.dark-mode .hero-subtitle {
  color: #cbd5e1;
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 20px;
}

.stat-pill {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(148, 163, 184, 0.25);
  padding: 12px 14px;
}

body.dark-mode .stat-pill {
  background: rgba(15, 23, 42, 0.68);
  border-color: rgba(148, 163, 184, 0.24);
}

.stat-label {
  display: block;
  font-size: 0.78rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

body.dark-mode .stat-label {
  color: #94a3b8;
}

.stat-value {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
}

body.dark-mode .stat-value {
  color: #f8fafc;
}

.catalog-controls {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
}

body.dark-mode .catalog-controls {
  background: rgba(15, 23, 42, 0.74);
  border-color: rgba(148, 163, 184, 0.18);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
}

.filter-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-grid .form-control,
.filter-grid .form-select,
.filter-grid .btn {
  min-height: 46px;
  border-radius: 12px;
}

#filtro {
  flex: 1 1 320px;
}

#filtroCategoria,
#ordenar {
  flex: 1 1 210px;
}

#clearFilters {
  border: 0;
  background: linear-gradient(140deg, var(--primary-color), #ff8f3f);
  color: #fff;
  font-weight: 700;
  padding: 0 20px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

#clearFilters:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 18px rgba(255, 90, 54, 0.28);
}

.active-filter-note {
  margin-top: 10px;
  font-size: 0.9rem;
  color: #475569;
  font-weight: 600;
}

body.dark-mode .active-filter-note {
  color: #cbd5e1;
}

.theme-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  background: var(--card-light);
  border: 2px solid #e2e8f0;
  border-radius: 50px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.3s ease;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

body.dark-mode .theme-toggle {
  background: var(--card-dark);
  border-color: rgba(148, 163, 184, 0.45);
  color: #ffd700;
}

.theme-toggle:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.favorites-toggle {
  position: fixed;
  top: 70px;
  right: 20px;
  background: #f4b400;
  border: 2px solid #d97706;
  border-radius: 50px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s ease;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  font-weight: 700;
  color: #111827;
}

body.dark-mode .favorites-toggle {
  background: #ffd166;
  border-color: #f59e0b;
}

.favorites-toggle:hover {
  transform: scale(1.06);
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.45);
}

.card {
  transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
  border: none;
  border-radius: 20px;
  background: var(--card-light);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  position: relative;
}

body.dark-mode .card {
  background: var(--card-dark);
  border-color: rgba(148, 163, 184, 0.15);
}

.card:hover {
  transform: translateY(-10px) scale(1.012);
  box-shadow: 0 20px 40px rgba(255, 90, 54, 0.2);
  border-color: rgba(255, 90, 54, 0.3);
}

body.dark-mode .card:hover {
  box-shadow: 0 20px 40px rgba(255, 90, 54, 0.28);
}

.card-img-top {
  cursor: pointer;
  border-radius: 20px 20px 0 0;
  object-fit: contain;
  height: 250px;
  padding: 15px;
  transition: transform 0.3s ease, filter 0.3s ease;
  background: linear-gradient(135deg, #fff1eb 0%, #d3f5ee 100%);
}

body.dark-mode .card-img-top {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.card-img-top:hover {
  transform: scale(1.03);
  filter: brightness(1.08);
}

body.dark-mode .card-body .card-title,
body.dark-mode .card-body .nombre,
body.dark-mode .card-body .descripcion,
body.dark-mode .card-body .text-decoration-line-through,
body.dark-mode .card-body .small {
  color: #f8fafc !important;
}

body.dark-mode .card-body .text-success,
body.dark-mode .precio {
  color: #34d399 !important;
}

body.dark-mode .card-footer,
body.dark-mode .card-footer.bg-white {
  background: rgba(148, 163, 184, 0.03) !important;
}

.whatsapp-btn {
  background-color: #25D366 !important;
  border-color: #25D366 !important;
  transition: all 0.3s ease;
  font-weight: 700;
  border-radius: 12px;
}

.whatsapp-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(37, 211, 102, 0.35);
  background-color: #20ba5a !important;
}

.btn-outline-danger {
  border: 2px solid #dc3545;
  color: #dc3545;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.btn-outline-danger:hover {
  background-color: #ffebee;
  transform: scale(1.02);
}

.btn-danger {
  background-color: #dc3545 !important;
  border-color: #dc3545 !important;
  transform: scale(1.03);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.favoriteBtn {
  font-weight: 700;
}

.text-decoration-line-through {
  text-decoration: line-through;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.producto {
  animation: fadeInUp 0.6s ease-out forwards;
}

.producto:nth-child(1) { animation-delay: 0.1s; }
.producto:nth-child(2) { animation-delay: 0.2s; }
.producto:nth-child(3) { animation-delay: 0.3s; }
.producto:nth-child(n+4) { animation-delay: 0.4s; }

.form-control,
.form-select {
  border-radius: 12px;
  border: 2px solid #dbe3ef;
  transition: all 0.25s ease;
  font-size: 16px;
}

body.dark-mode .form-control,
body.dark-mode .form-select {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(148, 163, 184, 0.3);
  color: #e2e8f0;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(255, 90, 54, 0.16);
}

.empty-state {
  display: none;
  text-align: center;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 16px;
  border: 1px dashed #cbd5e1;
  padding: 28px;
  margin-bottom: 20px;
  color: #334155;
}

body.dark-mode .empty-state {
  background: rgba(15, 23, 42, 0.65);
  border-color: rgba(148, 163, 184, 0.35);
  color: #cbd5e1;
}

.back-to-top {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: var(--primary-color);
  color: #fff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  opacity: 0;
  pointer-events: none;
  transform: translateY(10px);
  transition: all 0.3s ease;
  z-index: 1000;
}

.back-to-top.show {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}

body.dark-mode .back-to-top {
  background: #fb5607;
}

.admin-info {
  border-top: 1px dashed #dee2e6;
  margin-top: 8px;
  padding-top: 8px;
}

body.dark-mode .admin-info {
  border-top-color: rgba(148, 163, 184, 0.35);
}

.admin-info small {
  line-height: 1.7;
}

body.dark-mode .admin-info small {
  color: #94a3b8 !important;
}

body.dark-mode .admin-info a {
  color: #7dd3fc;
}

.pagination {
  gap: 8px;
}

.page-link {
  border-radius: 8px;
  border: 1px solid #dbe3ef;
  transition: all 0.25s ease;
  color: #ea580c;
  font-weight: 600;
}

body.dark-mode .page-link {
  border-color: rgba(148, 163, 184, 0.3);
  color: #f8fafc;
  background-color: rgba(255, 255, 255, 0.05);
}

.page-link:hover {
  background-color: #ea580c;
  color: white;
  transform: translateY(-2px);
}

.page-item.active .page-link {
  background-color: #ea580c;
  border-color: #ea580c;
}

.modal-content {
  border-radius: 20px;
  border: none;
  background: var(--card-light);
  backdrop-filter: blur(10px);
}

body.dark-mode .modal-content {
  background: var(--card-dark);
  color: #e0e0e0;
}

body.dark-mode .modal-body,
body.dark-mode .modal-footer {
  background: transparent;
  color: #e0e0e0;
}

body.dark-mode .list-group-item {
  background-color: rgba(255, 255, 255, 0.04);
  color: #e0e0e0;
  border-color: rgba(148, 163, 184, 0.2);
}

.modal-header {
  border-bottom: 1px solid rgba(0,0,0,0.1);
  border-radius: 20px 20px 0 0;
}

body.dark-mode .modal-header {
  border-bottom-color: rgba(148, 163, 184, 0.2);
}

#modalImage {
  max-width: 100%;
  max-height: 80vh;
  width: auto;
  height: auto;
  display: block;
  margin: 0 auto;
  border-radius: 15px;
  object-fit: contain;
}

@media (max-width: 768px) {
  .stats-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .hero-panel {
    padding: 22px 16px;
  }

  .theme-toggle {
    top: 12px;
    right: 12px;
    padding: 6px 10px;
    font-size: 18px;
  }

  .favorites-toggle {
    top: 54px;
    right: 12px;
    padding: 6px 10px;
    font-size: 14px;
    border-radius: 40px;
  }

  .theme-toggle,
  .favorites-toggle {
    box-shadow: 0 6px 12px rgba(0,0,0,0.12);
  }

  .pagination {
    flex-wrap: wrap;
    gap: 4px;
    justify-content: center;
  }

  .page-link {
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 6px;
    min-width: 32px;
    text-align: center;
  }

  .back-to-top {
    right: 12px;
    bottom: 12px;
    width: 40px;
    height: 40px;
    font-size: 18px;
  }
}
"""

# =============================================
# 3. DEFINIR JAVASCRIPT
# =============================================
js_content = """// Inicializar Dark Mode al cargar
document.addEventListener('DOMContentLoaded', function() {
  initDarkMode();
  initFavoritos();
  updateStats(allItems);
});

function initDarkMode() {
  const darkMode = localStorage.getItem('darkMode') === 'true';
  if (darkMode) {
    document.body.classList.add('dark-mode');
  }
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon && darkMode) {
      themeIcon.textContent = '☀️';
    }
    themeToggle.addEventListener('click', toggleDarkMode);
  }
}

function toggleDarkMode() {
  const isDark = document.body.classList.toggle('dark-mode');
  const themeIcon = document.getElementById('themeIcon');
  if (themeIcon) {
    themeIcon.textContent = isDark ? '☀️' : '🌙';
  }
  localStorage.setItem('darkMode', isDark);
}

function initFavoritos() {
  const favoritos = JSON.parse(localStorage.getItem('favoritos')) || [];
  actualizarContadorFavoritos(favoritos.length);

  document.querySelectorAll('.favoriteBtn').forEach((btn) => {
    const nombre = btn.getAttribute('data-nombre');
    const esFavorito = favoritos.some((f) => f.nombre === nombre);

    if (esFavorito) {
      btn.classList.remove('btn-outline-danger');
      btn.classList.add('btn-danger');
    } else {
      btn.classList.remove('btn-danger');
      btn.classList.add('btn-outline-danger');
    }
  });
}

document.addEventListener('click', function(e) {
  if (e.target.closest('.favoriteBtn')) {
    e.preventDefault();
    const btn = e.target.closest('.favoriteBtn');
    const nombre = btn.getAttribute('data-nombre');
    const precio = btn.getAttribute('data-precio');
    const url = btn.getAttribute('data-url');

    let favoritos = JSON.parse(localStorage.getItem('favoritos')) || [];
    const existe = favoritos.some((f) => f.nombre === nombre);

    if (existe) {
      favoritos = favoritos.filter((f) => f.nombre !== nombre);
      btn.classList.remove('btn-danger');
      btn.classList.add('btn-outline-danger');
    } else {
      favoritos.push({ nombre, precio, url });
      btn.classList.remove('btn-outline-danger');
      btn.classList.add('btn-danger');
    }

    localStorage.setItem('favoritos', JSON.stringify(favoritos));
    actualizarContadorFavoritos(favoritos.length);
  }
});

function actualizarContadorFavoritos(cantidad) {
  const contador = document.getElementById('favCount');
  if (contador) {
    contador.textContent = cantidad;
  }
}

function mostrarFavoritos() {
  const favoritos = JSON.parse(localStorage.getItem('favoritos')) || [];
  const modalBody = document.getElementById('modalFavoritosBody');

  if (favoritos.length === 0) {
    modalBody.innerHTML = '<p class="text-center text-muted">No tienes productos favoritos aun.</p>';
  } else {
    let html = '<div class="list-group">';
    favoritos.forEach((fav, index) => {
      html += `
        <div class="list-group-item">
          <div class="d-flex gap-3">
            <div style="min-width: 100px;">
              <img src="${fav.url}" alt="${fav.nombre}" style="width: 100px; height: 100px; object-fit: contain; border-radius: 8px;" onerror="this.src='https://via.placeholder.com/100'">
            </div>
            <div class="flex-grow-1">
              <h6 class="mb-1">${fav.nombre}</h6>
              <p class="mb-2 text-success fw-bold">$${parseFloat(fav.precio).toFixed(2)}</p>
              <button class="btn btn-sm btn-danger" onclick="eliminarFavorito(${index})">Eliminar</button>
            </div>
          </div>
        </div>
      `;
    });
    html += '</div>';
    modalBody.innerHTML = html;
  }

  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
  document.body.classList.remove('modal-open');

  const modalElement = document.getElementById('favoritosModal');
  let modal = bootstrap.Modal.getInstance(modalElement);
  if (!modal) {
    modal = new bootstrap.Modal(modalElement);
  }
  modal.show();
}

function eliminarFavorito(index) {
  const favoritos = JSON.parse(localStorage.getItem('favoritos')) || [];
  favoritos.splice(index, 1);
  localStorage.setItem('favoritos', JSON.stringify(favoritos));
  actualizarContadorFavoritos(favoritos.length);
  initFavoritos();

  const modalElement = document.getElementById('favoritosModal');

  if (favoritos.length === 0) {
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) {
      const closeHandler = () => {
        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        modalElement.removeEventListener('hidden.bs.modal', closeHandler);
      };
      modalElement.addEventListener('hidden.bs.modal', closeHandler, { once: true });
      modal.hide();
    }
  } else {
    mostrarFavoritos();
  }
}

function enviarFavoritosWhatsApp() {
  const favoritos = JSON.parse(localStorage.getItem('favoritos')) || [];

  if (favoritos.length === 0) {
    alert('No tienes favoritos para enviar');
    return;
  }

  let mensaje = 'Hola. Estoy interesado en los siguientes productos:%0A%0A';

  favoritos.forEach((fav, index) => {
    mensaje += `${index + 1}. ${encodeURIComponent(fav.nombre)}%0APrecio: $${parseFloat(fav.precio).toFixed(2)}%0AImagen: ${encodeURIComponent(fav.url)}%0A%0A`;
  });

  mensaje += 'Gracias por tu atencion.';

  const numeroWhatsApp = '526678191185';
  const urlWhatsApp = `https://wa.me/${numeroWhatsApp}?text=${mensaje}`;

  const modalElement = document.getElementById('favoritosModal');
  const modal = bootstrap.Modal.getInstance(modalElement);
  if (modal) {
    modal.hide();
  }

  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.body.classList.remove('modal-open');
  }, 100);

  window.open(urlWhatsApp, '_blank');
}

const allItems = Array.from(document.querySelectorAll('.producto'));
const originalOrder = new Map();
allItems.forEach((el, idx) => originalOrder.set(el, idx));
let filtered = [...allItems];
const pageSize = 18;
let currentPage = 1;
const sortSelect = document.getElementById('ordenar');
let currentSort = sortSelect ? sortSelect.value : 'reciente';
const productosContainer = document.getElementById('productos');
const searchInput = document.getElementById('filtro');
const categorySelect = document.getElementById('filtroCategoria');
const clearFiltersBtn = document.getElementById('clearFilters');
const totalProductsEl = document.getElementById('totalProducts');
const visibleProductsEl = document.getElementById('visibleProducts');
const activeCategoryEl = document.getElementById('activeCategory');
const activeFilterNote = document.getElementById('activeFilterNote');
const emptyState = document.getElementById('emptyState');

function getItemPrice(el) {
  const raw = el.dataset.price || el.querySelector('.precio')?.innerText || '0';
  return parseFloat(String(raw).replace(/[^0-9.]/g, '')) || 0;
}

function applySort(items) {
  const sorted = [...items];
  if (currentSort === 'precio-asc') {
    sorted.sort((a, b) => getItemPrice(a) - getItemPrice(b));
  } else if (currentSort === 'precio-desc') {
    sorted.sort((a, b) => getItemPrice(b) - getItemPrice(a));
  } else {
    sorted.sort((a, b) => (originalOrder.get(a) ?? 0) - (originalOrder.get(b) ?? 0));
  }
  return sorted;
}

function reorderContainer(items) {
  if (!productosContainer || items.length === 0) return;
  const fragment = document.createDocumentFragment();
  items.forEach(el => fragment.appendChild(el));
  productosContainer.appendChild(fragment);
}

function renderPage(items, page) {
  allItems.forEach(el => el.style.display = 'none');
  const start = (page - 1) * pageSize;
  items.slice(start, start + pageSize).forEach(el => el.style.display = 'block');
}

function renderPagination(items) {
  const totalPages = Math.ceil(items.length / pageSize) || 1;
  const container = document.getElementById('paginacion');
  if (!container) return;
  container.innerHTML = '';
  const nav = container.closest('nav');
  if (nav) {
    nav.style.display = items.length > pageSize ? '' : 'none';
  }

  if (items.length === 0) return;

  const makeLi = (label, page, disabled=false, active=false) => {
    const li = document.createElement('li');
    li.className = `page-item${disabled ? ' disabled' : ''}${active ? ' active' : ''}`;
    const a = document.createElement('a');
    a.className = 'page-link';
    a.href = '#';
    a.innerText = label;
    a.addEventListener('click', e => {
      e.preventDefault();
      if (!disabled) {
        currentPage = page;
        update();
        scrollToTop();
      }
    });
    li.appendChild(a);
    return li;
  };

  container.appendChild(makeLi('«', currentPage - 1, currentPage === 1));

  const maxButtons = window.matchMedia('(max-width: 576px)').matches ? 3 : 5;
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
      const dots = document.createElement('li');
      dots.className = 'page-item disabled';
      dots.innerHTML = '<span class="page-link">...</span>';
      container.appendChild(dots);
    }
  }

  for (let p = startPage; p <= endPage; p++) {
    container.appendChild(makeLi(p, p, false, currentPage === p));
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      const dots = document.createElement('li');
      dots.className = 'page-item disabled';
      dots.innerHTML = '<span class="page-link">...</span>';
      container.appendChild(dots);
    }
    container.appendChild(makeLi(totalPages, totalPages, false, currentPage === totalPages));
  }

  container.appendChild(makeLi('»', currentPage + 1, currentPage === totalPages));
}

function scrollToTop() {
  document.getElementById('top').scrollIntoView({ behavior: 'smooth' });
}

const backToTopBtn = document.getElementById('backToTop');
if (backToTopBtn) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      backToTopBtn.classList.add('show');
    } else {
      backToTopBtn.classList.remove('show');
    }
  });

  backToTopBtn.addEventListener('click', () => {
    scrollToTop();
  });
}

function updateStats(items) {
  if (totalProductsEl) totalProductsEl.textContent = allItems.length;
  if (visibleProductsEl) visibleProductsEl.textContent = items.length;

  const activeCategory = categorySelect?.value ? categorySelect.value : 'Todas';
  if (activeCategoryEl) activeCategoryEl.textContent = activeCategory;

  const query = (searchInput?.value || '').trim();
  if (activeFilterNote) {
    const textTag = query ? `"${query}"` : 'sin texto';
    activeFilterNote.textContent = `Mostrando ${items.length} de ${allItems.length} productos | Categoria: ${activeCategory} | Busqueda: ${textTag}`;
  }
}

function update() {
  const sorted = applySort(filtered);
  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  if (currentPage > totalPages) {
    currentPage = totalPages;
  }

  reorderContainer(sorted);
  renderPage(sorted, currentPage);
  renderPagination(sorted);
  updateStats(sorted);

  if (emptyState) {
    emptyState.style.display = sorted.length === 0 ? 'block' : 'none';
  }
}

function removeAccents(str) {
  return str.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
}

function applyFilters() {
  const term = removeAccents((searchInput?.value || '').toLowerCase());
  const category = removeAccents((categorySelect?.value || '').toLowerCase());

  filtered = allItems.filter(el => {
    const texto = [
      el.querySelector('.nombre').innerText,
      el.querySelector('.descripcion').innerText,
      el.querySelector('.precio').innerText
    ].join(' ').toLowerCase();

    const matchesText = removeAccents(texto).includes(term);
    const itemCategory = removeAccents((el.dataset.category || '').toLowerCase());
    const matchesCategory = !category || itemCategory === category;

    return matchesText && matchesCategory;
  });

  currentPage = 1;
  update();
  scrollToTop();
}

if (searchInput) {
  searchInput.addEventListener('input', applyFilters);
}

if (categorySelect) {
  categorySelect.addEventListener('change', applyFilters);
}

if (sortSelect) {
  sortSelect.addEventListener('change', (e) => {
    currentSort = e.target.value;
    currentPage = 1;
    update();
    scrollToTop();
  });
}

if (clearFiltersBtn) {
  clearFiltersBtn.addEventListener('click', () => {
    if (searchInput) searchInput.value = '';
    if (categorySelect) categorySelect.value = '';
    if (sortSelect) {
      sortSelect.value = 'reciente';
      currentSort = 'reciente';
    }
    filtered = [...allItems];
    currentPage = 1;
    update();
    scrollToTop();
  });
}

update();

document.querySelectorAll('.card-img-top').forEach(img => {
  img.addEventListener('click', () => {
    const modalImage = document.getElementById('modalImage');
    modalImage.src = img.src;
    new bootstrap.Modal(document.getElementById('imageModal')).show();
  });
});

const hiddenTrigger = document.getElementById('hiddenTrigger');
let clickCount = 0;
let clickTimeout;

if (hiddenTrigger) {
  hiddenTrigger.addEventListener('click', () => {
    clickCount++;
    clearTimeout(clickTimeout);
    clickTimeout = setTimeout(() => {
      clickCount = 0;
    }, 2000);

    if (clickCount === 5) {
      clickCount = 0;
      const password = prompt('Ingrese la contrasena:');
      if (password === 'Zombie') {
        toggleAdminMode(true);
      } else {
        alert('Contrasena incorrecta');
      }
    }
  });
}

function toggleAdminMode(active) {
  document.querySelectorAll('.admin-info').forEach(el => {
    el.style.display = active ? 'block' : 'none';
  });
}

window.addEventListener('DOMContentLoaded', () => {
  const probabilidad = 0.001;
  if (Math.random() < probabilidad) {
    setTimeout(() => {
      new bootstrap.Modal(document.getElementById('descuentoModal')).show();
    }, 2000);
  }
});
"""

# =============================================
# 4. PLANTILLA HTML
# =============================================
html_template = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Catalogo de Productos | Ofertas</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
  <link rel="stylesheet" href="style/style.css">
</head>
<body>
  <!-- Toggle Dark Mode y Favoritos -->
  <button id="themeToggle" class="theme-toggle" title="Cambiar tema">
    <span id="themeIcon">🌙</span>
  </button>
  <button id="favoritosBtn" class="favorites-toggle" onclick="mostrarFavoritos()" title="Ver favoritos">
    ❤️ (<span id="favCount">0</span>)
  </button>

  <div class="container" id="top">
    <section class="hero-panel">
      <p class="hero-kicker">Seleccion premium</p>
      <!-- Título con botón oculto 🎁 -->
      <h1 class="hero-title" id="hiddenTrigger" title="Haz clic 5 veces rapido aqui">
        Catalogo de Ofertas Imbatibles
      </h1>
      <p class="hero-subtitle">
        Descubre productos seleccionados con precios competitivos, descuentos reales y contacto rapido por WhatsApp.
      </p>

      <div class="stats-strip" aria-label="Estadisticas del catalogo">
        <div class="stat-pill">
          <span class="stat-label">Total productos</span>
          <span class="stat-value" id="totalProducts">0</span>
        </div>
        <div class="stat-pill">
          <span class="stat-label">Mostrando</span>
          <span class="stat-value" id="visibleProducts">0</span>
        </div>
        <div class="stat-pill">
          <span class="stat-label">Categoria activa</span>
          <span class="stat-value" id="activeCategory">Todas</span>
        </div>
      </div>
    </section>

    <section class="catalog-controls" aria-label="Filtros y orden">
      <div class="filter-grid">
        <input id="filtro" type="text" class="form-control" placeholder="Buscar por nombre, descripcion o precio" />
        <select id="filtroCategoria" class="form-select">
          <option value="" selected>Todas las categorias</option>
          {% for cat in categorias %}
          <option value="{{ cat }}">{{ cat }}</option>
          {% endfor %}
        </select>
        <select id="ordenar" class="form-select">
          <option value="reciente" selected>Mas recientes</option>
          <option value="precio-asc">Precio: menor a mayor</option>
          <option value="precio-desc">Precio: mayor a menor</option>
        </select>
        <button id="clearFilters" type="button" class="btn">Limpiar</button>
      </div>
      <div class="active-filter-note" id="activeFilterNote">Mostrando todos los productos</div>
    </section>

    <!-- Productos -->
    <div class="row" id="productos">
      {% for producto in productos %}
      <div class="col-md-4 mb-4 producto" data-price="{{ (producto.PrecioRebaja if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 else producto.Precio) }}" data-index="{{ loop.index0 }}" data-category="{{ (producto.Categoria if producto.Categoria is not none else 'Otros') }}">
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

    <div id="emptyState" class="empty-state">
      <h5 class="mb-2">No encontramos productos con esos filtros</h5>
      <p class="mb-0">Prueba quitando categoria o cambiando el texto de busqueda.</p>
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
            <div class="admin-info" style="display:none;">
              <small class="d-block text-secondary mt-2">📦 {{ producto.Caja or '—' }}</small>
              {% if producto.LinkCompra %}
              <small class="d-block text-secondary">🔗 <a href="{{ producto.LinkCompra }}" target="_blank" rel="noopener noreferrer">Ver enlace</a></small>
              {% else %}
              <small class="d-block text-secondary">🔗 —</small>
              {% endif %}
            </div>
          </div>
          <div class="card-footer bg-white">
            <div class="d-flex gap-2">
              <button class="btn btn-outline-danger flex-grow-1 favoriteBtn" data-nombre="{{ producto.Nombre }}" data-precio="{{ (producto.PrecioRebaja if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 else producto.Precio) }}" data-url="{{ producto.ImagenURL }}">❤️ Favorito</button>
              <a href="https://wa.me/526678191185?text=¡Estoy+interesado+en+{{ producto.Nombre|urlencode }}%0APrecio:+{{ (producto.PrecioRebaja if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 else producto.Precio)|urlencode }}%0AURL:+{{ producto.ImagenURL|urlencode }}" class="btn whatsapp-btn text-white flex-grow-1" target="_blank">📱 Contactar</a>
            </div>
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

  <!-- Modal de Descuento Aleatorio -->
  <div class="modal fade" id="descuentoModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content text-center">
        <div class="modal-header bg-success text-white">
          <h5 class="modal-title">🎉 ¡Felicidades!</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <p class="fs-5">¡Has obtenido un <strong>5% de descuento</strong> exclusivo! 😱</p>
          <p class="text-muted">Para hacerlo válido, <strong>envíanos mensaje por WhatsApp</strong>. Si no lo haces, el descuento <strong>no aplica</strong>.</p>
          <p class="text-danger small">* Tope máximo del descuento: <strong>$150 MXN</strong>.</p>
          <a href="https://wa.me/526678191185?text=¡Hola!+Tengo+un+descuento+del+5%+y+quiero+aplicarlo+en+mi+compra" target="_blank" class="btn btn-success mt-2">📱 Enviar Mensaje</a>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Modal Imagen Ampliada -->
  <div class="modal fade" id="imageModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content bg-transparent border-0">
        <img id="modalImage" src="" class="img-fluid rounded" alt="Imagen ampliada" />
      </div>
    </div>
  </div>

  <!-- Modal Favoritos -->
  <div class="modal fade" id="favoritosModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-scrollable modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Mis Favoritos ❤️</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body" id="modalFavoritosBody" style="max-height: 70vh; overflow-y: auto;">
          <!-- Los favoritos se inyectarán aquí -->
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
          <button type="button" class="btn btn-success" id="enviarFavWhatsApp" onclick="enviarFavoritosWhatsApp()">📱 Enviar por WhatsApp</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Botón Ir Arriba -->
  <button id="backToTop" class="back-to-top" title="Ir arriba" aria-label="Ir arriba">↑</button>

  <script src="https://cdn.counter.dev/script.js" data-id="a385688b-fca9-43be-90f6-bf9fff769d46" data-utcoffset="-7"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <script src="js/catalog.js"></script>
</body>
</html>
"""

# =============================================
# 5. GENERAR ARCHIVOS (CSS, JS, HTML)
# =============================================
try:
    # Generar CSS
    with open(OUTPUT_CSS, "w", encoding="utf-8") as f:
        f.write(css_content)
    print(f"✅ CSS generado en: {OUTPUT_CSS}")
    
    # Generar JS (reemplazar variables de Jinja)
    template_js = Template(js_content)
    js_output = template_js.render(productos=df.to_dict("records"))
    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(js_output)
    print(f"✅ JavaScript generado en: {OUTPUT_JS}")
    
    # Generar HTML
    template = Template(html_template)
    html_output = template.render(productos=df.to_dict("records"), categorias=categorias)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"✅ Catálogo generado en: {OUTPUT_HTML}")
    print("📂 Abre el archivo en tu navegador para verlo.")
    webbrowser.open(f"file://{OUTPUT_HTML}")
except Exception as e:
    print(f"❌ Error al generar los archivos: {e}")
