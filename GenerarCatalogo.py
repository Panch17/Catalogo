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
SCRIPT_DIR = r"C:\Users\Lpz_p\Desktop\Mi Proyecto Gib\Catalogo"

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
    print("✅ Archivo Excel leído y procesado correctamente")
except Exception as e:
    print(f"❌ Error al leer el archivo: {e}")
    exit()

# =============================================
# 2. DEFINIR CSS
# =============================================
css_content = """:root {
  --primary-color: #6366f1;
  --secondary-color: #25D366;
  --bg-light: #f8f9fa;
  --bg-dark: #1a1a2e;
  --card-light: rgba(255, 255, 255, 0.95);
  --card-dark: rgba(30, 41, 59, 0.8);
}

body { 
  background-color: var(--bg-light);
  padding-top: 20px;
  transition: background-color 0.3s ease, color 0.3s ease;
  color: #333;
}

body.dark-mode {
  background: linear-gradient(135deg, var(--bg-dark) 0%, #0f1419 100%);
  color: #e0e0e0;
}

.theme-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  background: var(--card-light);
  border: 2px solid #e0e0e0;
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
  border-color: #444;
  color: #ffd700;
}

.theme-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.favorites-toggle {
  position: fixed;
  top: 70px; /* debajo del toggle de tema */
  right: 20px; /* alinear con el toggle */
  background: #ffc107;
  border: 2px solid #ff9800;
  border-radius: 50px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s ease;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  font-weight: 600;
  color: #000;
}

body.dark-mode .favorites-toggle {
  background: #ffb700;
  border-color: #ff8c00;
}

.favorites-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(255, 152, 0, 0.4);
  background: #ffb300;
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
  border-color: rgba(255, 255, 255, 0.1);
}

/* Dark mode: mejorar contraste de texto en las tarjetas */
body.dark-mode .card-body .card-title,
body.dark-mode .card-body .nombre,
body.dark-mode .card-body .descripcion,
body.dark-mode .card-body .text-decoration-line-through,
body.dark-mode .card-body .small {
  color: #ffffff !important;
}

/* Precio con descuento: verde más brillante en modo oscuro para mayor visibilidad */
body.dark-mode .card-body .text-success,
body.dark-mode .precio {
  color: #4ade80 !important; /* verde brillante */
}

/* Footer de la tarjeta en modo oscuro menos brillante */
body.dark-mode .card-footer {
  background: rgba(255,255,255,0.02);
}

body.dark-mode .card-footer.bg-white {
  background: rgba(255,255,255,0.02) !important;
}

.card:hover {
  transform: translateY(-12px) scale(1.02);
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.3);
}

body.dark-mode .card:hover {
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
}

.card-img-top {
  cursor: pointer;
  border-radius: 20px 20px 0 0;
  object-fit: contain;
  height: 250px;
  padding: 15px;
  transition: transform 0.3s ease, filter 0.3s ease;
  background: linear-gradient(135deg, #f0f9ff 0%, #f3e8ff 100%);
}

body.dark-mode .card-img-top {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.card-img-top:hover {
  transform: scale(1.05);
  filter: brightness(1.1);
}

.whatsapp-btn {
  background-color: #25D366 !important;
  border-color: #25D366 !important;
  transition: all 0.3s ease;
  font-weight: 600;
  border-radius: 12px;
}

.whatsapp-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(37, 211, 102, 0.4);
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
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.favoriteBtn {
  font-weight: 600;
}

.text-decoration-line-through {
  text-decoration: line-through;
}

#hiddenTrigger {
  cursor: default;
  user-select: none;
  transition: transform 0.3s ease;
}

#hiddenTrigger:hover {
  transform: scale(1.05);
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

h1 {
  animation: fadeInUp 0.8s ease-out;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

body.dark-mode h1 {
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.form-control {
  border-radius: 12px;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
  font-size: 16px;
}

.form-select {
  border-radius: 12px;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
  font-size: 16px;
}

body.dark-mode .form-control {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #e0e0e0;
}

body.dark-mode .form-select {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #e0e0e0;
}

.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  transform: scale(1.02);
}

.form-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
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
  background: #60a5fa;
}

.pagination {
  gap: 8px;
}

.page-link {
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
  color: var(--primary-color);
}

body.dark-mode .page-link {
  border-color: rgba(255, 255, 255, 0.2);
  color: #60a5fa;
  background-color: rgba(255, 255, 255, 0.05);
}

.page-link:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-2px);
}

.page-item.active .page-link {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
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
  border-color: rgba(255, 255, 255, 0.08);
}

body.dark-mode .table {
  color: #e0e0e0;
}

body.dark-mode .table thead th,
body.dark-mode .table tbody td {
  color: #e0e0e0;
  background-color: transparent;
}

body.dark-mode .table thead th {
  background-color: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

body.dark-mode .table > :not(caption) > * > * {
  background-color: transparent;
  border-color: rgba(255, 255, 255, 0.1);
}

body.dark-mode #modalListaBody .form-control {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: #e0e0e0;
}

body.dark-mode .table-striped > tbody > tr:nth-of-type(odd) {
  background-color: rgba(255, 255, 255, 0.03);
}

body.dark-mode .table-hover > tbody > tr:hover {
  background-color: rgba(255, 255, 255, 0.06);
}

.modal-header {
  border-bottom: 1px solid rgba(0,0,0,0.1);
  border-radius: 20px 20px 0 0;
}

body.dark-mode .modal-header {
  border-bottom-color: rgba(255,255,255,0.1);
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

html {
  scroll-behavior: smooth;
}

/* Ajustes responsive: botones más pequeños en móviles */
@media (max-width: 576px) {
  .theme-toggle {
    top: 12px;
    right: 12px;
    padding: 6px 10px;
    font-size: 18px;
  }

  .favorites-toggle {
    top: 54px; /* ligeramente debajo del toggle reducido */
    right: 12px;
    padding: 6px 10px;
    font-size: 14px;
    border-radius: 40px;
  }

  .theme-toggle, .favorites-toggle {
    box-shadow: 0 6px 12px rgba(0,0,0,0.12);
  }

  /* Paginación más compacta en móviles */
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
}

// Remueve acentos para filtro insensible
function removeAccents(str) {
  return str.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "");
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

if (sortSelect) {
  sortSelect.addEventListener('change', (e) => {
    currentSort = e.target.value;
    currentPage = 1;
    update();
    scrollToTop();
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
      <th>Almacenamiento</th>
      <th>Fuente</th>
    </tr>
  `;
  table.appendChild(thead);

  // Cuerpo tabla
  const tbody = document.createElement('tbody');

  // Los datos vienen de Jinja, vamos a usar la variable productos
  const productos = {{ productos|tojson|safe }};
  productos.forEach(p => {
    const tr = document.createElement('tr');
    const precioFinal = (p.PrecioRebaja !== null && p.PrecioRebaja > 0) ? p.PrecioRebaja : p.Precio;
    // LinkCompra con icono que abre en nueva pestaña
    const linkCompraHTML = p.LinkCompra ? `<a href="${p.LinkCompra}" target="_blank" rel="noopener noreferrer" title="Abrir enlace" aria-label="Abrir enlace">🔗</a>` : '';
    //<td>$${p.Precio.toFixed(2)}</td>
    tr.innerHTML = `
      <td>${p.Nombre}</td>
      <td>$${precioFinal.toFixed(2)}</td>
      <td>${p.Caja || ''}</td>
      <td>${linkCompraHTML}</td>
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
    const term = removeAccents(e.target.value.toLowerCase());
    const tabla = document.querySelector('#modalListaBody table tbody');
    if (!tabla) return;
    Array.from(tabla.rows).forEach(row => {
      const textoFila = removeAccents(row.innerText.toLowerCase());
      row.style.display = textoFila.includes(term) ? '' : 'none';
    });
  }
});

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
    <!-- Título con botón oculto 🎁 -->
    <h1 class="text-center mb-4 text-primary" id="hiddenTrigger" title="Haz clic 5 veces rápido aquí">
      🎁 Catálogo de Ofertas 🔥
    </h1>

    <!-- Buscador principal -->
    <div class="mb-4 text-center d-flex justify-content-center gap-2 flex-wrap">
      <input id="filtro" type="text" class="form-control w-50" placeholder="🔍 Buscar productos..." />
      <select id="ordenar" class="form-select w-auto">
        <option value="reciente" selected>Más recientes</option>
        <option value="precio-asc">Precio: menor a mayor</option>
        <option value="precio-desc">Precio: mayor a menor</option>
      </select>
    </div>

    <!-- Productos -->
    <div class="row" id="productos">
      {% for producto in productos %}
      <div class="col-md-4 mb-4 producto" data-price="{{ (producto.PrecioRebaja if producto.PrecioRebaja is not none and producto.PrecioRebaja > 0 else producto.Precio) }}" data-index="{{ loop.index0 }}">
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
    html_output = template.render(productos=df.to_dict("records"))
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"✅ Catálogo generado en: {OUTPUT_HTML}")
    print("📂 Abre el archivo en tu navegador para verlo.")
    webbrowser.open(f"file://{OUTPUT_HTML}")
except Exception as e:
    print(f"❌ Error al generar los archivos: {e}")
