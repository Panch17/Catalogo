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
SCRIPT_DIR = r"C:\Users\Admin\Desktop\Proyecto\Catalogo"
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
OUTPUT_UPDATE_HTML = os.path.join(SCRIPT_DIR, "actualizar.html")
OUTPUT_CSS = os.path.join(STYLE_DIR, "style.css")
OUTPUT_JS = os.path.join(JS_DIR, "catalog.js")

# =============================================
# 1. LEER EL ARCHIVO EXCEL/CSV Y LIMPIAR DATOS
# =============================================
try:
    df = pd.read_excel(EXCEL_PATH)
    if 'Estatus' in df.columns:
        df['Estatus'] = pd.to_numeric(df['Estatus'], errors='coerce').fillna(1).astype(int)
    else:
        df['Estatus'] = 1

    # Solo mostrar registros activos (1)
    df = df[df['Estatus'] == 1].copy()
    if df.empty:
        print("⚠️ No hay productos activos (Estatus=1) para mostrar.")

    # Mezcla aleatoriamente solo los productos activos
    df = df.sample(frac=1).reset_index(drop=True)
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
    sys.exit(1)

# =============================================
# 2. DEFINIR CSS
# =============================================
css_content = """:root {
  --primary-color: #00d4ff;
  --secondary-color: #00ffa6;
  --accent-color: #ff6b00;
  --wa-color: #21c55d;
  --bg-light: #eef3ff;
  --bg-light-radial: radial-gradient(circle at 10% 20%, #ffffff 0%, #dce8ff 45%, #d0e7f8 100%);
  --bg-dark: #0a111f;
  --text-light: #12203a;
  --text-dark: #dce9ff;
  --card-light: rgba(255, 255, 255, 0.75);
  --card-dark: rgba(14, 23, 42, 0.8);
  --stroke-light: rgba(11, 29, 66, 0.08);
  --stroke-dark: rgba(255, 255, 255, 0.14);
}

* {
  box-sizing: border-box;
}

body {
  font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
  background: var(--bg-light-radial);
  color: var(--text-light);
  min-height: 100vh;
  padding: 18px 0 0;
  transition: background 0.35s ease, color 0.35s ease;
  overflow-x: hidden;
}

body::before,
body::after {
  content: '';
  position: fixed;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  filter: blur(60px);
  z-index: -1;
  opacity: 0.35;
}

body::before {
  top: -80px;
  left: -80px;
  background: #6be1ff;
}

body::after {
  right: -110px;
  bottom: 20%;
  background: #7dffcf;
}

body.dark-mode {
  background: radial-gradient(circle at 10% 0%, #0f1f3d 0%, var(--bg-dark) 40%, #050913 100%);
  color: var(--text-dark);
}

body.dark-mode::before {
  background: #0ea5e9;
  opacity: 0.22;
}

body.dark-mode::after {
  background: #22d3ee;
  opacity: 0.18;
}

.container {
  max-width: 1240px;
}

.theme-toggle,
.favorites-toggle {
  position: fixed;
  right: 20px;
  border-radius: 999px;
  border: 1px solid var(--stroke-light);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(14px);
  box-shadow: 0 10px 24px rgba(19, 38, 77, 0.15);
  cursor: pointer;
  z-index: 1100;
  font-weight: 700;
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
}

.theme-toggle {
  top: 20px;
  font-size: 18px;
  padding: 7px 14px;
}

.favorites-toggle {
  top: 70px;
  padding: 8px 14px;
  color: #1f2937;
  font-size: 15px;
}

body.dark-mode .theme-toggle,
body.dark-mode .favorites-toggle {
  background: rgba(10, 18, 34, 0.86);
  border-color: var(--stroke-dark);
  color: #d7e9ff;
}

.theme-toggle:hover,
.favorites-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 30px rgba(10, 30, 70, 0.2);
}

.hero {
  border: 1px solid var(--stroke-light);
  border-radius: 28px;
  padding: 32px 24px;
  margin: 12px 0 24px;
  background: linear-gradient(120deg, rgba(255, 255, 255, 0.92), rgba(223, 244, 255, 0.72));
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 35px rgba(11, 46, 88, 0.12);
  position: relative;
  overflow: hidden;
  animation: floatIn 0.7s ease-out;
}

.hero::after {
  content: '';
  position: absolute;
  right: -80px;
  top: -90px;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.34), rgba(0, 212, 255, 0));
}

body.dark-mode .hero {
  background: linear-gradient(130deg, rgba(10, 25, 49, 0.94), rgba(8, 18, 34, 0.82));
  border-color: var(--stroke-dark);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.42);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  background: rgba(0, 212, 255, 0.12);
  color: #075985;
  border: 1px solid rgba(0, 152, 209, 0.25);
}

body.dark-mode .hero-badge {
  color: #67e8f9;
  background: rgba(34, 211, 238, 0.12);
  border-color: rgba(103, 232, 249, 0.28);
}

h1 {
  margin-top: 12px;
  margin-bottom: 10px;
  font-family: 'Sora', 'Segoe UI', sans-serif;
  font-weight: 700;
  font-size: clamp(1.7rem, 2.6vw, 2.8rem);
  letter-spacing: -0.02em;
  line-height: 1.1;
  background: linear-gradient(130deg, #00c0ff, #00ffa6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

body.dark-mode h1 {
  background: linear-gradient(130deg, #67e8f9, #86efac);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  max-width: 760px;
  color: #2f4a77;
  margin-bottom: 0;
  font-size: 1rem;
}

body.dark-mode .hero-subtitle {
  color: #b5c9eb;
}

.controls-panel {
  position: static;
  z-index: 900;
  border-radius: 22px;
  border: 1px solid var(--stroke-light);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(14px);
  box-shadow: 0 12px 28px rgba(12, 39, 76, 0.12);
  padding: 14px;
  margin-bottom: 16px;
}

.mobile-filters-toggle {
  display: none;
  width: 100%;
  border: 1px solid rgba(20, 49, 90, 0.2);
  background: rgba(255, 255, 255, 0.86);
  color: #0f3a72;
  font-weight: 700;
  border-radius: 12px;
  padding: 9px 12px;
  margin-bottom: 10px;
}

body.dark-mode .mobile-filters-toggle {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.22);
  color: #d7ecff;
}

body.dark-mode .controls-panel {
  background: rgba(8, 15, 30, 0.85);
  border-color: var(--stroke-dark);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.42);
}

.form-control,
.form-select {
  border-radius: 12px;
  border: 1px solid rgba(14, 40, 78, 0.18);
  background-color: rgba(255, 255, 255, 0.9);
  color: #11294f;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s ease;
}

body.dark-mode .form-control,
body.dark-mode .form-select {
  background-color: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
  color: #deebff;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.16);
}

.results-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 8px 4px 0;
  font-size: 13px;
  color: #345382;
}

body.dark-mode .results-bar {
  color: #abc4ea;
}

.results-pill {
  border-radius: 999px;
  border: 1px solid rgba(0, 126, 174, 0.24);
  background: rgba(0, 212, 255, 0.1);
  color: #085577;
  font-weight: 700;
  padding: 5px 11px;
}

body.dark-mode .results-pill {
  color: #67e8f9;
  border-color: rgba(103, 232, 249, 0.3);
  background: rgba(103, 232, 249, 0.12);
}

.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.filter-chip {
  border: 1px solid rgba(14, 82, 131, 0.25);
  background: rgba(255, 255, 255, 0.8);
  color: #0d4878;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

body.dark-mode .filter-chip {
  border-color: rgba(130, 221, 251, 0.35);
  background: rgba(103, 232, 249, 0.12);
  color: #bff3ff;
}

.empty-state {
  margin: 10px 0 18px;
  border: 1px dashed rgba(14, 82, 131, 0.28);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.75);
  text-align: center;
  padding: 22px 18px;
}

body.dark-mode .empty-state {
  border-color: rgba(130, 221, 251, 0.25);
  background: rgba(255, 255, 255, 0.04);
}

.empty-title {
  font-weight: 700;
  color: #114378;
  margin-bottom: 6px;
}

body.dark-mode .empty-title {
  color: #c9eeff;
}

.empty-text {
  margin-bottom: 12px;
  color: #496b99;
}

body.dark-mode .empty-text {
  color: #adc8ea;
}

.card {
  transition: transform 0.35s ease, box-shadow 0.35s ease, border-color 0.35s ease;
  border: 1px solid rgba(13, 40, 75, 0.12);
  border-radius: 18px;
  background: var(--card-light);
  backdrop-filter: blur(8px);
  overflow: hidden;
  position: relative;
}

body.dark-mode .card {
  background: var(--card-dark);
  border-color: rgba(255, 255, 255, 0.14);
}

.card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(140deg, rgba(0, 212, 255, 0.12), rgba(0, 255, 166, 0));
  opacity: 0;
  transition: opacity 0.35s ease;
  pointer-events: none;
}

.card:hover {
  transform: translateY(-10px);
  border-color: rgba(0, 193, 255, 0.38);
  box-shadow: 0 24px 38px rgba(8, 35, 68, 0.2);
}

.card:hover::before {
  opacity: 1;
}

body.dark-mode .card:hover {
  box-shadow: 0 24px 44px rgba(0, 0, 0, 0.48);
}

.card-img-top {
  cursor: pointer;
  border-radius: 18px 18px 0 0;
  object-fit: contain;
  height: 250px;
  padding: 12px;
  transition: transform 0.3s ease, filter 0.3s ease;
  background: linear-gradient(135deg, rgba(238, 247, 255, 0.86), rgba(220, 255, 246, 0.85));
}

body.dark-mode .card-img-top {
  background: linear-gradient(130deg, rgba(15, 32, 60, 0.86), rgba(12, 24, 45, 0.9));
}

.card:hover .card-img-top {
  transform: scale(1.03);
  filter: saturate(1.05);
}

.card-title {
  font-weight: 700;
  color: #0f2b58;
}

.descripcion {
  color: #4a6288 !important;
}

body.dark-mode .card-title,
body.dark-mode .nombre {
  color: #f1f7ff !important;
}

body.dark-mode .descripcion,
body.dark-mode .text-decoration-line-through,
body.dark-mode .small {
  color: #b8cbeb !important;
}

.precio,
body.dark-mode .precio {
  color: #16a34a !important;
}

.card-footer {
  border-top: 1px solid rgba(18, 45, 84, 0.09);
  background: rgba(255, 255, 255, 0.65) !important;
}

body.dark-mode .card-footer,
body.dark-mode .card-footer.bg-white {
  border-top-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03) !important;
}

.whatsapp-btn {
  background-color: var(--wa-color) !important;
  border-color: var(--wa-color) !important;
  color: #f3fff8 !important;
  border-radius: 11px;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.whatsapp-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 20px rgba(33, 197, 93, 0.32);
}

.favoriteBtn {
  border-radius: 11px;
  font-weight: 700;
}

.btn-outline-danger {
  border-width: 1px;
}

.btn-danger {
  transform: scale(1.03);
  box-shadow: 0 8px 14px rgba(220, 53, 69, 0.24);
}

.admin-info {
  border-top: 1px dashed rgba(36, 66, 102, 0.28);
  margin-top: 8px;
  padding-top: 8px;
}

body.dark-mode .admin-info {
  border-top-color: rgba(255, 255, 255, 0.2);
}

body.dark-mode .admin-info a {
  color: #67e8f9;
}

.pagination {
  gap: 8px;
  margin-top: 10px;
}

.page-link {
  border-radius: 10px;
  border: 1px solid rgba(20, 49, 90, 0.18);
  color: #0b5cab;
  background-color: rgba(255, 255, 255, 0.75);
  transition: all 0.22s ease;
}

body.dark-mode .page-link {
  border-color: rgba(255, 255, 255, 0.2);
  color: #74dffc;
  background-color: rgba(255, 255, 255, 0.05);
}

.page-link:hover {
  background-color: #00b6ef;
  border-color: #00b6ef;
  color: #fff;
  transform: translateY(-1px);
}

.page-item.active .page-link {
  background-color: #00c7f6;
  border-color: #00c7f6;
  color: #032033;
}

.modal-content {
  border-radius: 16px;
  border: 1px solid rgba(20, 49, 90, 0.14);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(14px);
}

body.dark-mode .modal-content {
  background: rgba(8, 15, 30, 0.94);
  border-color: rgba(255, 255, 255, 0.15);
  color: #e5f1ff;
}

body.dark-mode .modal-header {
  border-bottom-color: rgba(255, 255, 255, 0.15);
}

body.dark-mode .modal-body,
body.dark-mode .modal-footer,
body.dark-mode .list-group-item {
  color: #d8e7fd;
  background-color: transparent;
  border-color: rgba(255, 255, 255, 0.12);
}

#modalImage {
  max-width: 100%;
  max-height: 80vh;
  width: auto;
  height: auto;
  display: block;
  margin: 0 auto;
  border-radius: 14px;
  object-fit: contain;
}

.back-to-top {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(140deg, #00d4ff, #00ffa6);
  color: #062230;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 12px 20px rgba(6, 42, 68, 0.25);
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

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(28px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes floatIn {
  from {
    opacity: 0;
    transform: translateY(18px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.producto {
  animation: fadeInUp 0.55s ease-out both;
}

.producto:nth-child(1) { animation-delay: 0.07s; }
.producto:nth-child(2) { animation-delay: 0.12s; }
.producto:nth-child(3) { animation-delay: 0.17s; }
.producto:nth-child(n+4) { animation-delay: 0.22s; }

html {
  scroll-behavior: smooth;
}

@media (max-width: 768px) {
  .hero {
    padding: 24px 16px;
    border-radius: 22px;
  }

  .controls-panel {
    border-radius: 16px;
    padding: 12px;
  }

  .mobile-filters-toggle {
    display: block;
  }

  .controls-panel .filters-content {
    display: block;
  }

  .controls-panel.collapsed .filters-content {
    display: none;
  }

  .results-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}

@media (max-width: 576px) {
  .theme-toggle {
    top: 12px;
    right: 12px;
    padding: 6px 10px;
    font-size: 16px;
  }

  .favorites-toggle {
    top: 52px;
    right: 12px;
    padding: 6px 10px;
    font-size: 13px;
  }

  .page-link {
    padding: 4px 8px;
    font-size: 12px;
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
  initMobileFilters();
  updateResultsInfo();
});

function initMobileFilters() {
  const controlsPanel = document.getElementById('controlsPanel');
  const mobileToggle = document.getElementById('mobileFiltersToggle');
  if (!controlsPanel || !mobileToggle) {
    return;
  }

  const isMobile = () => window.matchMedia('(max-width: 768px)').matches;
  const refreshState = () => {
    if (isMobile()) {
      const collapsed = controlsPanel.classList.contains('collapsed');
      mobileToggle.textContent = collapsed ? 'Mostrar filtros' : 'Ocultar filtros';
    } else {
      controlsPanel.classList.remove('collapsed');
      mobileToggle.textContent = 'Filtros';
    }
  };

  if (isMobile()) {
    controlsPanel.classList.add('collapsed');
  } else {
    controlsPanel.classList.remove('collapsed');
  }
  refreshState();

  mobileToggle.addEventListener('click', () => {
    controlsPanel.classList.toggle('collapsed');
    refreshState();
  });

  window.addEventListener('resize', refreshState);
}

function collapseMobileFilters() {
  const controlsPanel = document.getElementById('controlsPanel');
  const mobileToggle = document.getElementById('mobileFiltersToggle');
  if (!controlsPanel || !mobileToggle) {
    return;
  }
  if (window.matchMedia('(max-width: 768px)').matches) {
    controlsPanel.classList.add('collapsed');
    mobileToggle.textContent = 'Mostrar filtros';
  }
}

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
  
  // Actualizar estado visual de todos los botones
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

// Event delegation para favoritos (evita múltiples listeners)
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
      // Remover de favoritos
      favoritos = favoritos.filter((f) => f.nombre !== nombre);
      btn.classList.remove('btn-danger');
      btn.classList.add('btn-outline-danger');
    } else {
      // Agregar a favoritos
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
    modalBody.innerHTML = '<p class="text-center text-muted">No tienes productos favoritos aún.</p>';
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
  
  // Limpiar backdrops previos
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
  
  // Actualizar botones de favoritos en la página
  initFavoritos();
  
  const modalElement = document.getElementById('favoritosModal');
  
  if (favoritos.length === 0) {
    // Si no hay favoritos, cerrar el modal completamente
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) {
      // Usar el evento hidden de Bootstrap para saber cuándo terminó de cerrar
      const closeHandler = () => {
        // Limpiar backdrops y estilos después de que cierre
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
    // Si quedan favoritos, actualizar contenido del modal
    mostrarFavoritos();
  }
}

function enviarFavoritosWhatsApp() {
  const favoritos = JSON.parse(localStorage.getItem('favoritos')) || [];
  
  if (favoritos.length === 0) {
    alert('No tienes favoritos para enviar');
    return;
  }
  
  let mensaje = '¡Hola! Estoy interesado en los siguientes productos:%0A%0A';
  
  favoritos.forEach((fav, index) => {
    mensaje += `${index + 1}. ${encodeURIComponent(fav.nombre)}%0APrecio: $${parseFloat(fav.precio).toFixed(2)}%0AImagen: ${encodeURIComponent(fav.url)}%0A%0A`;
  });
  
  mensaje += '¡Gracias por tu atención!';
  
  const numeroWhatsApp = '526678191185';
  const urlWhatsApp = `https://wa.me/${numeroWhatsApp}?text=${mensaje}`;
  
  // Cerrar el modal
  const modalElement = document.getElementById('favoritosModal');
  const modal = bootstrap.Modal.getInstance(modalElement);
  if (modal) {
    modal.hide();
  }
  
  // Forzar eliminación del backdrop
  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
    document.body.classList.remove('modal-open');
  }, 100);
  
  // Abrir WhatsApp
  window.open(urlWhatsApp, '_blank');
}

// Variables para paginación, filtrado y orden
const allItems = Array.from(document.querySelectorAll('.producto'));
const originalOrder = new Map();
allItems.forEach((el, idx) => originalOrder.set(el, idx));
let filtered = [...allItems];
const pageSize = 18;
let currentPage = 1;
const sortSelect = document.getElementById('ordenar');
let currentSort = sortSelect ? sortSelect.value : 'reciente';
const productosContainer = document.getElementById('productos');

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

// Botón flotante "Ir arriba"
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

// Actualiza la lista principal
function update() {
  const sorted = applySort(filtered);
  reorderContainer(sorted);
  renderPage(sorted, currentPage);
  renderPagination(sorted);
  renderEmptyState();
  updateResultsInfo();
}

function renderActiveFilters() {
  const activeFilters = document.getElementById('activeFilters');
  if (!activeFilters) {
    return;
  }

  const chips = [];
  const term = (searchInput?.value || '').trim();
  const categoryValue = categorySelect?.value || '';
  const sortValue = sortSelect?.value || 'reciente';
  const sortLabel = sortSelect?.options[sortSelect.selectedIndex]?.text || 'Más recientes';

  if (term) {
    chips.push({ type: 'term', label: `Busqueda: ${term}` });
  }
  if (categoryValue) {
    chips.push({ type: 'category', label: `Categoria: ${categoryValue}` });
  }
  if (sortValue !== 'reciente') {
    chips.push({ type: 'sort', label: `Orden: ${sortLabel}` });
  }

  if (!chips.length) {
    activeFilters.innerHTML = '';
    return;
  }

  activeFilters.innerHTML = chips
    .map((chip) => `<button type="button" class="filter-chip" data-chip="${chip.type}">${chip.label} ×</button>`)
    .join('');
}

function renderEmptyState() {
  const emptyState = document.getElementById('emptyState');
  const pagination = document.getElementById('paginacion');
  const paginationNav = pagination ? pagination.closest('nav') : null;
  if (!emptyState) {
    return;
  }

  if (filtered.length === 0) {
    emptyState.classList.remove('d-none');
    if (paginationNav) {
      paginationNav.style.display = 'none';
    }
  } else {
    emptyState.classList.add('d-none');
    if (paginationNav) {
      paginationNav.style.display = '';
    }
  }
}

function updateResultsInfo() {
  const resultsCount = document.getElementById('resultsCount');
  const activeCategory = document.getElementById('activeCategory');
  if (resultsCount) {
    resultsCount.textContent = `${filtered.length} producto(s)`;
  }
  if (activeCategory) {
    const categoryText = categorySelect && categorySelect.value ? categorySelect.value : 'Todas';
    activeCategory.textContent = categoryText;
  }
  renderActiveFilters();
}

// Remueve acentos para filtro insensible
function removeAccents(str) {
  return str.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "");
}

// Evento filtro principal (texto + categoría)
const searchInput = document.getElementById('filtro');
const categorySelect = document.getElementById('filtroCategoria');

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
  categorySelect.addEventListener('change', () => {
    applyFilters();
    collapseMobileFilters();
  });
}

const activeFiltersContainer = document.getElementById('activeFilters');
if (activeFiltersContainer) {
  activeFiltersContainer.addEventListener('click', (e) => {
    const chip = e.target.closest('.filter-chip');
    if (!chip) {
      return;
    }

    const chipType = chip.getAttribute('data-chip');
    if (chipType === 'term' && searchInput) {
      searchInput.value = '';
    }
    if (chipType === 'category' && categorySelect) {
      categorySelect.value = '';
    }
    if (chipType === 'sort' && sortSelect) {
      sortSelect.value = 'reciente';
      currentSort = 'reciente';
    }

    applyFilters();
  });
}

const clearFiltersBtn = document.getElementById('clearFilters');
if (clearFiltersBtn) {
  clearFiltersBtn.addEventListener('click', () => {
    if (searchInput) {
      searchInput.value = '';
    }
    if (categorySelect) {
      categorySelect.value = '';
    }
    if (sortSelect) {
      sortSelect.value = 'reciente';
      currentSort = 'reciente';
    }
    applyFilters();
    collapseMobileFilters();
  });
}

const clearFiltersEmptyBtn = document.getElementById('clearFiltersEmpty');
if (clearFiltersEmptyBtn) {
  clearFiltersEmptyBtn.addEventListener('click', () => {
    if (searchInput) {
      searchInput.value = '';
    }
    if (categorySelect) {
      categorySelect.value = '';
    }
    if (sortSelect) {
      sortSelect.value = 'reciente';
      currentSort = 'reciente';
    }
    applyFilters();
  });
}

if (sortSelect) {
  sortSelect.addEventListener('change', (e) => {
    currentSort = e.target.value;
    currentPage = 1;
    update();
    scrollToTop();
    collapseMobileFilters();
  });
}

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
      toggleAdminMode(true);
    } else if (password === "Zombie2") {
      window.open('actualizar.html', '_blank');
    } else {
      alert("Contraseña incorrecta");
    }
  }
});

// Activa/desactiva la visibilidad de la info de admin en las cards
function toggleAdminMode(active) {
  document.querySelectorAll('.admin-info').forEach(el => {
    el.style.display = active ? 'block' : 'none';
  });
}

// Mostrar modal con 1% de probabilidad al cargar la página
window.addEventListener('DOMContentLoaded', () => {
  const probabilidad = 0.001; // 0.1%
  if (Math.random() < probabilidad) {
    setTimeout(() => {
      new bootstrap.Modal(document.getElementById('descuentoModal')).show();
    }, 2000); // Mostrar tras 2 segundos
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
  <title>Catálogo de Productos</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
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
    <section class="hero">
      <span class="hero-badge">CATALOGO DE PRODUCTOS</span>
      <!-- Título con botón oculto 🎁 -->
      <h1 class="text-start" id="hiddenTrigger" title="Haz clic 5 veces rápido aquí">
        🛍️ Explora nuestro catalogo
      </h1>
      <p class="hero-subtitle">
        Revisa productos por categoria, compara precios y encuentra opciones en segundos. Cuando te interese uno, contactanos facilmente por WhatsApp.
      </p>
    </section>

    <!-- Buscador principal -->
    <div class="controls-panel collapsed" id="controlsPanel">
      <button type="button" class="mobile-filters-toggle" id="mobileFiltersToggle">Mostrar filtros</button>
      <div class="filters-content" id="filtersContent">
      <div class="row g-2 align-items-center">
        <div class="col-12 col-lg-5">
          <input id="filtro" type="text" class="form-control" placeholder="Buscar por nombre, descripción o precio..." />
        </div>
        <div class="col-6 col-lg-3">
          <select id="filtroCategoria" class="form-select">
            <option value="" selected>Todas las categorías</option>
            {% for cat in categorias %}
            <option value="{{ cat }}">{{ cat }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="col-6 col-lg-3">
          <select id="ordenar" class="form-select">
            <option value="reciente" selected>Más recientes</option>
            <option value="precio-asc">Precio: menor a mayor</option>
            <option value="precio-desc">Precio: mayor a menor</option>
          </select>
        </div>
        <div class="col-12 col-lg-1 d-grid">
          <button id="clearFilters" class="btn btn-outline-secondary">Limpiar</button>
        </div>
      </div>
      <div class="results-bar">
        <span>Mostrando <strong id="resultsCount">0 producto(s)</strong></span>
        <span class="results-pill">Categoría: <span id="activeCategory">Todas</span></span>
      </div>
      <div class="active-filters" id="activeFilters"></div>
      </div>
    </div>

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

    <div class="empty-state d-none" id="emptyState">
      <p class="empty-title">No encontramos productos con esos filtros</p>
      <p class="empty-text">Prueba otra palabra, cambia la categoria o limpia los filtros.</p>
      <button type="button" class="btn btn-outline-secondary" id="clearFiltersEmpty">Limpiar filtros</button>
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

update_html_template = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Actualizar Catalogo</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body {
      background: linear-gradient(135deg, #f2f7ff 0%, #dbeafe 100%);
      min-height: 100vh;
      padding: 24px 0;
    }
    .panel {
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid rgba(30, 64, 175, 0.14);
      border-radius: 16px;
      box-shadow: 0 16px 30px rgba(30, 64, 175, 0.14);
    }
    .table-wrap {
      max-height: 65vh;
      overflow: auto;
    }
    .table th {
      position: sticky;
      top: 0;
      background: #f8fafc;
      z-index: 2;
      white-space: nowrap;
    }
    .table td {
      min-width: 140px;
    }
    .small-col {
      min-width: 90px;
    }
  </style>
</head>
<body>
  <div class="container-xl">
    <div class="panel p-4">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
        <div>
          <h2 class="h4 mb-1">Panel de administracion</h2>
          <p class="text-muted mb-0">Edita productos, desactiva con Estatus 0 y publica cambios.</p>
        </div>
        <a href="index.html" class="btn btn-outline-primary">Volver al catalogo</a>
      </div>

      <div class="row g-2 mb-3">
        <div class="col-12 col-md-4 d-flex gap-2">
          <input type="password" id="adminKey" class="form-control" placeholder="Clave admin" />
          <button id="connectBtn" class="btn btn-primary">Conectar</button>
        </div>
        <div class="col-12 col-md-4">
          <input type="url" id="apiBase" class="form-control" placeholder="URL del backend API" />
        </div>
        <div class="col-6 col-md-2 d-grid">
          <button id="addRow" class="btn btn-outline-secondary" disabled>Agregar</button>
        </div>
        <div class="col-6 col-md-2 d-grid">
          <button id="saveChanges" class="btn btn-success" disabled>Guardar cambios</button>
        </div>
        <div class="col-12 col-md-2 d-grid">
          <button id="generateBtn" class="btn btn-primary" disabled>Generar catálogo</button>
        </div>
        <div class="col-12 col-md-2 d-grid">
          <button id="implementBtn" class="btn btn-danger" disabled>Implementar</button>
        </div>
        <div class="col-12 col-md-2 d-grid">
          <button id="toggleActive" class="btn btn-outline-primary" disabled>Solo activos</button>
        </div>
      </div>

      <div id="statusBox" class="alert alert-secondary small mb-3">Conecta con tu clave para comenzar.</div>

      <div class="table-wrap border rounded">
        <table class="table table-sm table-striped align-middle mb-0" id="productsTable">
          <thead>
            <tr>
              <th class="small-col">Estatus</th>
              <th>Nombre</th>
              <th>Descripcion</th>
              <th class="small-col">Precio</th>
              <th class="small-col">PrecioRebaja</th>
              <th>Categoria</th>
              <th>ImagenURL</th>
              <th>LinkCompra</th>
              <th>Caja</th>
              <th class="small-col">Accion</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    let products = [];
    let showOnlyActive = false;
    let key = '';
    const columns = ['Estatus', 'Nombre', 'Descripcion', 'Precio', 'PrecioRebaja', 'Categoria', 'ImagenURL', 'LinkCompra', 'Caja'];

    const tbody = document.querySelector('#productsTable tbody');
    const statusBox = document.getElementById('statusBox');
    const connectBtn = document.getElementById('connectBtn');
    const apiBaseInput = document.getElementById('apiBase');
    const addRowBtn = document.getElementById('addRow');
    const saveBtn = document.getElementById('saveChanges');
    const generateBtn = document.getElementById('generateBtn');
    const implementBtn = document.getElementById('implementBtn');
    const toggleActiveBtn = document.getElementById('toggleActive');

    function loadApiBase() {
      const fromQuery = new URLSearchParams(window.location.search).get('apiBase');
      if (fromQuery) {
        return fromQuery;
      }
      return localStorage.getItem('catalogoApiBase') || window.location.origin;
    }

    function saveApiBase(value) {
      const normalized = value.trim();
      if (normalized) {
        localStorage.setItem('catalogoApiBase', normalized);
      } else {
        localStorage.removeItem('catalogoApiBase');
      }
    }

    function getApiBase() {
      const value = apiBaseInput.value.trim();
      return value || window.location.origin;
    }

    function showStatus(message, kind = 'secondary') {
      statusBox.className = `alert alert-${kind} small mb-3`;
      statusBox.textContent = message;
    }

    function api(path, options = {}) {
      const url = new URL(path, getApiBase());
      return fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': key,
          ...(options.headers || {})
        }
      });
    }

    function normalizeProduct(row) {
      return {
        Estatus: Number(row.Estatus) === 0 ? 0 : 1,
        Nombre: row.Nombre || '',
        Descripcion: row.Descripcion || '',
        Precio: row.Precio || '',
        PrecioRebaja: row.PrecioRebaja || '',
        Categoria: row.Categoria || 'Otros',
        ImagenURL: row.ImagenURL || '',
        LinkCompra: row.LinkCompra || '',
        Caja: row.Caja || ''
      };
    }

    function renderTable() {
      const data = showOnlyActive ? products.filter((item) => Number(item.Estatus) === 1) : products;
      tbody.innerHTML = data.map((item, viewIndex) => {
        const realIndex = products.indexOf(item);
        return `
          <tr data-index="${realIndex}">
            <td class="small-col">
              <select class="form-select form-select-sm" data-field="Estatus">
                <option value="1" ${Number(item.Estatus) === 1 ? 'selected' : ''}>1</option>
                <option value="0" ${Number(item.Estatus) === 0 ? 'selected' : ''}>0</option>
              </select>
            </td>
            ${columns.slice(1).map((field) => `<td><input class="form-control form-control-sm" data-field="${field}" value="${String(item[field] ?? '').replace(/"/g, '&quot;')}"></td>`).join('')}
            <td class="small-col"><button class="btn btn-sm btn-outline-danger" data-delete="${realIndex}">Borrar</button></td>
          </tr>
        `;
      }).join('');

      if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted py-3">No hay registros para mostrar</td></tr>';
      }
    }

    function syncInputsToModel() {
      document.querySelectorAll('#productsTable tbody tr[data-index]').forEach((tr) => {
        const index = Number(tr.getAttribute('data-index'));
        if (Number.isNaN(index) || !products[index]) return;
        tr.querySelectorAll('[data-field]').forEach((input) => {
          const field = input.getAttribute('data-field');
          if (field === 'Estatus') {
            products[index][field] = Number(input.value) === 0 ? 0 : 1;
          } else {
            products[index][field] = input.value;
          }
        });
      });
    }

    async function loadProducts() {
      const response = await api('/api/productos');
      if (!response.ok) {
        throw new Error('No se pudo leer el listado');
      }
      const payload = await response.json();
      products = (payload.items || []).map(normalizeProduct);
      renderTable();
    }

    function setControlsEnabled(enabled) {
      addRowBtn.disabled = !enabled;
      saveBtn.disabled = !enabled;
      generateBtn.disabled = !enabled;
      implementBtn.disabled = !enabled;
      toggleActiveBtn.disabled = !enabled;
    }

    apiBaseInput.value = loadApiBase();
    apiBaseInput.addEventListener('change', () => {
      saveApiBase(apiBaseInput.value);
    });

    connectBtn.addEventListener('click', async () => {
      key = document.getElementById('adminKey').value.trim();
      if (!key) {
        showStatus('Ingresa la clave admin.', 'warning');
        return;
      }
      saveApiBase(apiBaseInput.value);
      try {
        await loadProducts();
        setControlsEnabled(true);
        showStatus('Conectado correctamente.', 'success');
      } catch (err) {
        setControlsEnabled(false);
        showStatus('Clave incorrecta, servidor no disponible o URL del backend incorrecta.', 'danger');
      }
    });

    addRowBtn.addEventListener('click', () => {
      syncInputsToModel();
      products.push(normalizeProduct({}));
      renderTable();
    });

    tbody.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-delete]');
      if (!btn) return;
      const index = Number(btn.getAttribute('data-delete'));
      if (Number.isNaN(index) || !products[index]) return;
      products[index].Estatus = 0;
      renderTable();
      showStatus('Registro marcado como inactivo (Estatus 0). Recuerda guardar cambios.', 'warning');
    });

    tbody.addEventListener('input', syncInputsToModel);
    tbody.addEventListener('change', syncInputsToModel);

    saveBtn.addEventListener('click', async () => {
      syncInputsToModel();
      const response = await api('/api/productos', {
        method: 'PUT',
        body: JSON.stringify({ items: products })
      });
      if (!response.ok) {
        showStatus('No se pudo guardar el Excel.', 'danger');
        return;
      }
      showStatus('Excel actualizado correctamente en el servidor.', 'success');
    });

    generateBtn.addEventListener('click', async () => {
      syncInputsToModel();
      const response = await api('/api/generar', {
        method: 'POST',
        body: JSON.stringify({})
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        showStatus(`Error al generar catalogo: ${payload.error || 'desconocido'}`, 'danger');
        return;
      }
      showStatus(payload.message || 'Catalogo regenerado correctamente.', 'success');
    });

    implementBtn.addEventListener('click', async () => {
      const deploy = confirm('¿Tambien deseas hacer deploy a GitHub al implementar?');
      const response = await api('/api/implementar', {
        method: 'POST',
        body: JSON.stringify({ deploy })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        showStatus(`Error al implementar: ${payload.error || 'desconocido'}`, 'danger');
        return;
      }
      showStatus(payload.message || 'Catalogo regenerado correctamente.', 'success');
    });

    toggleActiveBtn.addEventListener('click', () => {
      showOnlyActive = !showOnlyActive;
      toggleActiveBtn.textContent = showOnlyActive ? 'Ver todos' : 'Solo activos';
      renderTable();
    });
  </script>
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

    # Generar HTML de actualizacion de productos
    with open(OUTPUT_UPDATE_HTML, "w", encoding="utf-8") as f:
        f.write(update_html_template)
    print(f"✅ Panel de actualización generado en: {OUTPUT_UPDATE_HTML}")

    print("📂 Abre el archivo en tu navegador para verlo.")
    if os.getenv("OPEN_BROWSER", "1") == "1":
      webbrowser.open(f"file://{OUTPUT_HTML}")
except Exception as e:
    print(f"❌ Error al generar los archivos: {e}")
    sys.exit(1)
