// Inicializar Dark Mode al cargar
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
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
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