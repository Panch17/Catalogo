# Catálogo de Productos

Generador de catálogo con favoritos, modo noche y envío por WhatsApp.

---

## ✅ Favoritos y Modo Noche - Guía

### ❤️ Botón de Favoritos

- Cada producto tiene botón **❤️ Favorito**.
- Al hacer clic, se marca en rojo y se guarda en **localStorage**.
- El contador **❤️** en la esquina superior izquierda se actualiza automáticamente.

### 🌙 Modo Noche

- Botón 🌙 en la esquina superior derecha.
- Cambia a **☀️** cuando el modo noche está activo.
- Se guarda la preferencia en **localStorage**.

### 📱 Envío por WhatsApp

- Botón **❤️ Favoritos** abre el modal con productos guardados.
- Botón **"📱 Enviar por WhatsApp"** envía todos los favoritos en un solo mensaje.

---

## 🎮 Cómo Usar

### Agregar a Favoritos

1. Ve el producto que te interesa.
2. Haz clic en **❤️ Favorito**.
3. El contador aumenta.

### Ver tus Favoritos

1. Haz clic en **❤️ Favoritos**.
2. Se abre un modal con tus productos.
3. Puedes eliminar favoritos desde ahí.

### Enviar por WhatsApp

1. Agrega productos a favoritos.
2. Abre **❤️ Favoritos**.
3. Pulsa **"📱 Enviar por WhatsApp"**.

### Cambiar Modo Noche

1. Haz clic en **🌙**.
2. Cambia a oscuro (☀️).
3. Vuelve a hacer clic para regresar.

---

## 🖼️ Mejoras v2.0 (Favoritos)

### Imagen en el modal de favoritos

- Se muestra la imagen del producto (100x100px, bordes redondeados).
- Incluye nombre, precio y botón eliminar.
- Si no carga la imagen, se ve un placeholder gris.

### Pantalla oscura después de eliminar

- Se cierra correctamente el modal.
- Se elimina el backdrop y la clase `modal-open`.
- Funciona igual al enviar por WhatsApp.

---

## 📂 Estructura de Archivos

```
Catalogo/
├── index.html
├── style/
│   └── style.css
├── js/
│   └── catalog.js
├── datos/
│   └── productos.xlsx
└── GenerarCatalogo.py
```

---

## 🛠️ Compilación

```
pyinstaller --onefile GenerarCatalogo.py
```

## Subir a la rema

```
git status
git add .
git commit -m "Descripción de los cambios"
git push origin main
```
