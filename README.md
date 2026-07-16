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
├── GenerarCatalogo.py
└── DescargarImagenes.py
```

---

## 🛠️ Descarga de imágenes

```
python DescargarImagenes.py
```

El script `DescargarImagenes.py` lee la columna `ImagenURL` de `datos/productos.xlsx` y descarga las imágenes en `IMAGENES/Descargadas`.

## 🌐 Panel de actualizacion en servidor

Si quieres editar productos desde otra ubicacion (no solo local), usa el backend admin:

1. Instala dependencias en tu entorno Python:
	- `pip install flask openpyxl pandas jinja2`
2. Arranca el servidor:
	- `python ServidorActualizacion.py`
3. Abre en navegador:
	- `http://TU_SERVIDOR:8000/actualizar.html`
4. Clave admin por defecto:
	- `Zombie2`

Puedes cambiar la clave y puerto con variables de entorno:

- `ADMIN_KEY=TuClaveSegura`
- `ADMIN_PORT=8000`

Flujo recomendado:

1. Editar productos en `actualizar.html`.
2. Para "borrar" un producto, cambiar `Estatus` a `0` (no se elimina la fila).
3. Click en `Guardar cambios`.
4. Click en `Implementar` para regenerar catálogo.
5. Opcional: confirmar deploy para ejecutar guardado/push automático.

Nota:

- GitHub Pages por si solo no ejecuta Python; este panel requiere tu servidor con `ServidorActualizacion.py` corriendo.

## Subir a la rema

```
git status
git add .
git commit -m "Descripción de los cambios"
git push origin main
```
