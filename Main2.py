"""
Frank Joyería Premium — Aplicación Móvil
Desarrollada con Flet (Python)
Versión refactorizada: correcciones de enums, API deprecada,
arquitectura de UI, eventos y manejo de errores.
"""

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            FRANK JOYERÍA PREMIUM — APLICACIÓN MÓVIL                        ║
║            Framework : Flet 0.84  |  Python 3.10+                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ARQUITECTURA                                                                ║
║  • Clase principal : FrankJoyeriaPremium                                    ║
║  • Patrón          : Componentes por método, estado centralizado            ║
║  • UI Root         : ft.Column estable — sin page.clean() destructivo       ║
║  • Actualización   : Parcial por índice, no rebuild total de página         ║
║                                                                              ║
║  API FLET 0.84 — REGLAS CLAVE                                               ║
║  • Dialogs/Drawers : Asignar a page.drawer / page.dialog y llamar           ║
║                      page.update() — NO usar page.open() (no existe)        ║
║  • BottomSheet     : Asignar a page.bottom_sheet, luego                     ║
║                      page.bottom_sheet.open = True + page.update()          ║
║  • SnackBar        : Asignar a page.snack_bar y llamar page.update()        ║
║  • Alignment       : ft.Alignment(x, y) — NO ft.alignment.center           ║
║  • Iconos          : ft.Icons.NOMBRE — NO strings                           ║
║  • ImageFit        : ft.ImageFit.COVER — NO strings                         ║
║  • Espaciado       : ft.Container(height=N) — NO ft.SizedBox                ║
║  • Ventana         : page.window.width/height — NO page.window_width        ║
║  • GridView.update : Solo llamar si el control ya está en la página         ║
║                      (verificar: control.page is not None)                  ║
║                                                                              ║
║  ESTRUCTURA DE ARCHIVOS ESPERADA                                             ║
║  proyecto/                                                                   ║
║  ├── main.py                                                                 ║
║  ├── Productos.py       ← Lista PRODUCTOS (opcional, hay fallback)          ║
║  └── Imagenes/          ← assets_dir, imágenes de productos                 ║
║      ├── Collar1.png                                                         ║
║      └── placeholder.png                                                    ║
║                                                                              ║
║  ÍNDICES DEL CONTENEDOR RAÍZ (contenido_root.controls)                      ║
║  [0] Header        — barra superior dorada                                  ║
║  [1] Banner        — imagen destacada con texto superpuesto                 ║
║  [2] Filtros       — fila de categorías scrolleable                         ║
║  [3] Título sección— categoría activa + conteo de productos                 ║
║  [4] Grid          — tarjetas de productos (GridView)                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import flet as ft


# ──────────────────────────────────────────────────────────────────────────────
#  IMPORTACIÓN SEGURA DE PRODUCTOS
#  Si no existe Productos.py se usan datos de ejemplo para desarrollo.
# ──────────────────────────────────────────────────────────────────────────────
try:
    from Productos import PRODUCTOS
except ImportError:
    PRODUCTOS = [
        {"name": "Anillo Aurora",    "price": "$250.000", "img": "anillo1.png",  "categoria": "Anillos"},
        {"name": "Collar Eternidad", "price": "$380.000", "img": "Collar1.png",  "categoria": "Collares"},
        {"name": "Aretes Luna",      "price": "$120.000", "img": "aretes1.png",  "categoria": "Aretes"},
        {"name": "Pulsera Oro",      "price": "$210.000", "img": "pulsera1.png", "categoria": "Pulseras"},
        {"name": "Anillo Diamante",  "price": "$520.000", "img": "anillo2.png",  "categoria": "Anillos"},
        {"name": "Collar Perla",     "price": "$290.000", "img": "collar2.png",  "categoria": "Collares"},
    ]


# ──────────────────────────────────────────────────────────────────────────────
#  TOKENS DE DISEÑO
#  Centralizar colores aquí evita magic strings dispersos en el código.
# ──────────────────────────────────────────────────────────────────────────────
NEGRO        = "#050505"   # Fondo principal
NEGRO_CARD   = "#111111"   # Fondo de tarjetas
NEGRO_BANNER = "#1A1A1A"   # Fondo del banner
NEGRO_DRAWER = "#111111"   # Fondo del menú lateral
DORADO       = "#D4AF37"   # Color de acento principal
BLANCO       = "#FFFFFF"   # Texto primario
GRIS_TEXTO   = "#AAAAAA"   # Texto secundario / inactivo
GRIS_DIV     = "#333333"   # Color de divisores

CATEGORIAS   = ["Todo", "Anillos", "Collares", "Aretes", "Pulseras"]


# ──────────────────────────────────────────────────────────────────────────────
#  HELPERS DE COMPATIBILIDAD
#
#  _e(enum_class_name, attr, fallback)
#  Resuelve ft.<Clase>.<ATRIBUTO> de forma segura.
#  Si la clase o el atributo no existen en la versión instalada,
#  retorna `fallback` (generalmente el string equivalente).
#
#  Todos los valores se resuelven UNA SOLA VEZ al importar el módulo,
#  no en cada llamada al constructor — esto es más eficiente.
# ──────────────────────────────────────────────────────────────────────────────
def _e(enum_class_name: str, attr: str, fallback):
    cls = getattr(ft, enum_class_name, None)
    if cls is not None:
        return getattr(cls, attr, fallback)
    return fallback


# Enums resueltos al inicio del módulo
IMAGE_FIT_CONTAIN = _e("ImageFit",     "CONTAIN",             "contain")
IMAGE_FIT_COVER   = _e("ImageFit",     "COVER",               "cover")
FONT_WEIGHT_BOLD  = _e("FontWeight",   "BOLD",                "bold")
TEXT_ALIGN_CENTER = _e("TextAlign",    "CENTER",              "center")
TEXT_OVF_ELLIPSIS = _e("TextOverflow", "ELLIPSIS",            "ellipsis")
ICON_MENU         = _e("Icons",        "MENU",                "menu")
ICON_BAG          = _e("Icons",        "SHOPPING_BAG",        "shopping_bag")
ICON_IMG_OFF      = _e("Icons",        "IMAGE_NOT_SUPPORTED", "image_not_supported")
ICON_INFO         = _e("Icons",        "INFO_OUTLINE",        "info_outline")
ICON_CLOSE        = _e("Icons",        "CLOSE",               "close")
ICON_STAR         = _e("Icons",        "STAR",                "star")


# ──────────────────────────────────────────────────────────────────────────────
#  CLASE PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────
class FrankJoyeriaPremium:
    """
    Controlador principal de la aplicación Frank Joyería.

    Responsabilidades:
    - Configurar la ventana/página de Flet.
    - Construir y ensamblar todos los componentes de UI.
    - Gestionar el estado de filtrado por categoría.
    - Manejar eventos de usuario (menú, filtros, carrito, etc.).

    Estado interno:
    - categoria_activa (str): Categoría seleccionada actualmente.
    - contenido_root (ft.Column): Contenedor raíz estable de la UI.
    - grid_productos (ft.GridView): Grid de tarjetas de productos.
    """

    def __init__(self, page: ft.Page):
        self.page             = page
        self.productos        = PRODUCTOS
        self.categoria_activa = "Todo"

        # Contenedor raíz — se construye una vez y se actualiza por índice.
        # Esto evita el anti-patrón page.clean() que causa parpadeos.
        self.contenido_root = ft.Column(spacing=0, expand=True)

        # GridView declarado aquí para poder referenciarlo en _actualizar_grid()
        # sin tener que buscarlo dentro del árbol de controles.
        self.grid_productos = ft.GridView(
            runs_count=2,
            spacing=15,
            run_spacing=15,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            child_aspect_ratio=0.72,
            expand=True,
        )

        self._setup_page()
        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    #  CONFIGURACIÓN DE VENTANA
    # ─────────────────────────────────────────────────────────────────────────

    def _setup_page(self):
        """
        Configura propiedades globales de la página.
        Nota: page.window.* es la API correcta desde Flet 0.21+.
        La API antigua page.window_width está deprecada.
        """
        self.page.title      = "Frank Joyería | Luxury Experience"
        self.page.bgcolor    = NEGRO
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding    = 0
        self.page.window.width     = 450
        self.page.window.height    = 850
        self.page.window.resizable = True

    # ─────────────────────────────────────────────────────────────────────────
    #  COMPONENTES DE UI — MÉTODOS DE CONSTRUCCIÓN
    #  Cada método retorna un ft.Control listo para ser insertado en el árbol.
    #  No tienen efectos secundarios sobre self.page.
    # ─────────────────────────────────────────────────────────────────────────

    def _build_header(self) -> ft.Container:
        """
        Barra superior de la app.
        Contiene: botón de menú (izquierda), nombre de marca (centro),
        botón de carrito (derecha).
        Usa ft.Stack para superponer el fondo dorado y el contenido.
        """
        return ft.Container(
            content=ft.Stack([
                # Capa 1: fondo dorado
                ft.Container(bgcolor=DORADO, height=45, border_radius=12),
                # Capa 2: controles superpuestos
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ICON_MENU,
                            icon_color=NEGRO,
                            icon_size=20,
                            on_click=self._on_menu_click,
                            tooltip="Menú",
                        ),
                        ft.Text(
                            "FRANK JOYERÍA",
                            color=NEGRO,
                            size=16,
                            weight=FONT_WEIGHT_BOLD,
                            font_family="Serif",
                        ),
                        ft.IconButton(
                            icon=ICON_BAG,
                            icon_color=NEGRO,
                            icon_size=20,
                            on_click=self._on_carrito_click,
                            tooltip="Carrito",
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=5),
                    height=45,
                    alignment=ft.Alignment(0, 0),
                ),
            ]),
            # top=60 deja espacio para el safe area / notch del teléfono
            padding=ft.padding.only(top=60, left=25, right=25, bottom=10),
            height=115,
        )

    def _build_banner(self) -> ft.Container:
        """
        Banner principal con imagen de fondo semitransparente y texto superpuesto.
        Usa ClipBehavior.ANTI_ALIAS para respetar el border_radius en la imagen.
        """
        return ft.Container(
            content=ft.Container(
                width=400,
                height=180,
                border_radius=20,
                bgcolor=NEGRO_BANNER,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                content=ft.Stack([
                    # Imagen de fondo con opacidad reducida
                    ft.Image(
                        src="Collar1.png",
                        width=400,
                        height=180,
                        fit=IMAGE_FIT_COVER,
                        opacity=0.5,
                    ),
                    # Texto superpuesto centrado
                    ft.Container(
                        content=ft.Column([
                            ft.Text("DISEÑOS DE AUTOR", size=20, color=DORADO, weight=FONT_WEIGHT_BOLD),
                            ft.Text("Joyería artesanal única", size=12, color=BLANCO, opacity=0.8),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                        ),
                        alignment=ft.Alignment(0, 0),
                        width=400,
                        height=180,
                    ),
                ]),
            ),
            padding=ft.padding.symmetric(horizontal=25),
            alignment=ft.Alignment(0, 0),
        )

    def _build_filtros(self) -> ft.Container:
        """
        Fila horizontal scrolleable de botones de categoría.
        El botón activo se renderiza con fondo dorado y texto negro.
        Los inactivos tienen borde dorado y fondo oscuro.
        Se reconstruye completamente al cambiar categoria_activa.
        """
        controles = []
        for cat in CATEGORIAS:
            activo = cat == self.categoria_activa
            controles.append(
                ft.Container(
                    content=ft.Text(
                        cat,
                        color=NEGRO if activo else DORADO,
                        weight=FONT_WEIGHT_BOLD,
                        size=10,
                    ),
                    bgcolor=DORADO if activo else "#222222",
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    border_radius=15,
                    border=None if activo else ft.border.all(1, DORADO),
                    # lambda con argumento por defecto c=cat captura el valor
                    # correcto de cat en cada iteración (evita closure bug)
                    on_click=lambda e, c=cat: self._filtrar_categoria(c),
                    ink=True,
                )
            )
        return ft.Container(
            content=ft.Row(
                controls=controles,
                scroll=ft.ScrollMode.HIDDEN,
                spacing=10,
            ),
            padding=ft.padding.symmetric(horizontal=25, vertical=15),
        )

    def _build_seccion_titulo(self) -> ft.Container:
        """
        Fila con el nombre de la categoría activa y el conteo de productos.
        Se reconstruye junto con los filtros al cambiar categoria_activa.
        """
        label = self.categoria_activa if self.categoria_activa != "Todo" else "Colección"
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=14, weight=FONT_WEIGHT_BOLD, color=BLANCO),
                ft.Text(
                    f"{len(self._productos_filtrados())} productos",
                    size=12,
                    color=GRIS_TEXTO,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=25, vertical=5),
        )

    def _crear_card(self, item: dict) -> ft.Container:
        """
        Tarjeta individual de producto.

        Args:
            item: Diccionario con claves 'name', 'price', 'img', 'categoria'.

        Contiene:
        - Imagen del producto con fallback en caso de error de carga.
        - Nombre en mayúsculas, truncado a 2 líneas.
        - Precio en dorado.
        - Botón 'Agregar' con evento propio.
        - on_click en el contenedor para ir al detalle.

        Nota sobre lambdas: se usa p=item como argumento por defecto
        para capturar el valor correcto en el loop (evita closure bug).
        """
        src = item.get("img") or "placeholder.png"

        return ft.Container(
            content=ft.Column([
                # Imagen
                ft.Container(
                    content=ft.Image(
                        src=src,
                        width=120,
                        height=120,
                        fit=IMAGE_FIT_CONTAIN,
                        error_content=ft.Icon(ICON_IMG_OFF, color=GRIS_TEXTO, size=40),
                    ),
                    alignment=ft.Alignment(0, 0),
                    width=150,
                    height=130,
                ),
                # Nombre
                ft.Text(
                    item.get("name", "Sin nombre").upper(),
                    size=10,
                    weight=FONT_WEIGHT_BOLD,
                    color=BLANCO,
                    text_align=TEXT_ALIGN_CENTER,
                    max_lines=2,
                    overflow=TEXT_OVF_ELLIPSIS,
                ),
                # Precio
                ft.Text(
                    item.get("price", ""),
                    size=11,
                    color=DORADO,
                    weight=FONT_WEIGHT_BOLD,
                ),
                # Botón agregar
                ft.Container(
                    content=ft.Text("Agregar", size=9, color=NEGRO, weight=FONT_WEIGHT_BOLD),
                    bgcolor=DORADO,
                    padding=ft.padding.symmetric(horizontal=12, vertical=5),
                    border_radius=10,
                    on_click=lambda e, p=item: self._agregar_carrito(p),
                    ink=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            ),
            padding=10,
            bgcolor=NEGRO_CARD,
            border_radius=15,
            on_click=lambda e, p=item: self._ver_detalle(p),
            ink=True,
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  LÓGICA DE FILTRADO Y ACTUALIZACIÓN DE UI
    # ─────────────────────────────────────────────────────────────────────────

    def _productos_filtrados(self) -> list:
        """Retorna la lista de productos según la categoría activa."""
        if self.categoria_activa == "Todo":
            return self.productos
        return [p for p in self.productos if p.get("categoria") == self.categoria_activa]

    def _actualizar_grid(self):
        """
        Recarga las tarjetas del GridView según el filtro activo.
        IMPORTANTE: solo llama .update() si el control ya está montado
        en la página (grid_productos.page is not None).
        Llamar .update() antes de que el control esté en la página
        lanza: 'Control must be added to the page first'.
        """
        self.grid_productos.controls.clear()
        for p in self._productos_filtrados():
            self.grid_productos.controls.append(self._crear_card(p))
        if self.grid_productos.page is not None:
            self.grid_productos.update()

    def _actualizar_filtros(self):
        """
        Reemplaza los nodos de filtros y título en el contenedor raíz.
        Opera por índice directo para evitar un rebuild completo de la UI.
        Índice [2] = fila de filtros, Índice [3] = título de sección.
        """
        self.contenido_root.controls[2] = self._build_filtros()
        self.contenido_root.controls[3] = self._build_seccion_titulo()
        self.contenido_root.update()

    # ─────────────────────────────────────────────────────────────────────────
    #  ENSAMBLAJE PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        """
        Construye y monta la UI completa en la página.

        Orden crítico:
        1. Poblar grid_productos.controls SIN llamar .update()
           (el control aún no está en la página).
        2. Asignar controles al contenido_root.
        3. Llamar page.add() para montar el árbol.
        4. Llamar page.update() para renderizar.

        Invertir el orden 1 y 3 causa el error:
        'Control must be added to the page first'.
        """
        # Paso 1 — poblar sin .update()
        self.grid_productos.controls.clear()
        for p in self._productos_filtrados():
            self.grid_productos.controls.append(self._crear_card(p))

        # Paso 2 — armar árbol de controles
        self.contenido_root.controls = [
            self._build_header(),                                     # [0]
            self._build_banner(),                                     # [1]
            self._build_filtros(),                                    # [2]
            self._build_seccion_titulo(),                             # [3]
            ft.Container(content=self.grid_productos, expand=True),  # [4]
        ]

        # Pasos 3 y 4 — montar y renderizar
        self.page.add(self.contenido_root)
        self.page.update()

    # ─────────────────────────────────────────────────────────────────────────
    #  MANEJADORES DE EVENTOS
    # ─────────────────────────────────────────────────────────────────────────

    def _filtrar_categoria(self, categoria: str):
        """
        Cambia la categoría activa y actualiza filtros + grid.
        El guard evita un re-render innecesario si se toca la categoría activa.
        """
        if self.categoria_activa == categoria:
            return
        self.categoria_activa = categoria
        self._actualizar_filtros()
        self._actualizar_grid()

    def _on_menu_click(self, _e):
        """
        Abre el menú lateral (NavigationDrawer).

        API Flet 0.84:
        - Asignar el drawer a page.drawer.
        - Abrir con page.drawer.open = True + page.update().
        - Cerrar con page.drawer.open = False + page.update().

        El drawer contiene dos opciones:
        - Productos: resetea el filtro a "Todo" y cierra el drawer.
        - Quiénes somos: cierra el drawer y abre el BottomSheet informativo.
        """
        def cerrar(_e=None):
            self.page.drawer.open = False
            self.page.update()

        def ir_productos(_e):
            cerrar()
            self.categoria_activa = "Todo"
            self._actualizar_filtros()
            self._actualizar_grid()

        def ir_quienes_somos(_e):
            cerrar()
            self._mostrar_quienes_somos()

        self.page.drawer = ft.NavigationDrawer(
            bgcolor=NEGRO_DRAWER,
            controls=[
                # Cabecera con logo y nombre
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("FJ", size=28, weight=FONT_WEIGHT_BOLD, color=NEGRO),
                            bgcolor=DORADO,
                            width=60,
                            height=60,
                            border_radius=30,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text("FRANK JOYERÍA", size=14, weight=FONT_WEIGHT_BOLD, color=DORADO),
                        ft.Text("Luxury Experience", size=11, color=GRIS_TEXTO),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    ),
                    padding=ft.padding.symmetric(vertical=35, horizontal=20),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Divider(color=GRIS_DIV, height=1),
                ft.Container(height=8),
                # Opción: Productos
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ICON_BAG, color=DORADO, size=22),
                        ft.Text("Productos", color=BLANCO, size=14, weight=FONT_WEIGHT_BOLD),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    border_radius=12,
                    ink=True,
                    on_click=ir_productos,
                ),
                # Opción: Quiénes somos
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ICON_INFO, color=DORADO, size=22),
                        ft.Text("Quiénes somos", color=BLANCO, size=14, weight=FONT_WEIGHT_BOLD),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    border_radius=12,
                    ink=True,
                    on_click=ir_quienes_somos,
                ),
                ft.Divider(color=GRIS_DIV, height=1),
                # Cerrar
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ICON_CLOSE, color=GRIS_TEXTO, size=20),
                        ft.Text("Cerrar menú", color=GRIS_TEXTO, size=13),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    border_radius=12,
                    ink=True,
                    on_click=cerrar,
                ),
            ],
        )
        self.page.drawer.open = True
        self.page.update()

    def _mostrar_quienes_somos(self):
        """
        Muestra información de la marca en un BottomSheet.

        API Flet 0.84:
        - Asignar a page.bottom_sheet.
        - Abrir con page.bottom_sheet.open = True + page.update().
        - Cerrar con page.bottom_sheet.open = False + page.update().
        """
        def cerrar(_e=None):
            self.page.bottom_sheet.open = False
            self.page.update()

        self.page.bottom_sheet = ft.BottomSheet(
            bgcolor=NEGRO_CARD,
            open=True,
            content=ft.Container(
                content=ft.Column([
                    # Indicador visual de arrastre
                    ft.Container(bgcolor="#444444", width=40, height=4, border_radius=2),
                    ft.Container(height=8),
                    ft.Text("QUIÉNES SOMOS", size=18, weight=FONT_WEIGHT_BOLD, color=DORADO),
                    ft.Divider(color=GRIS_DIV),
                    ft.Text(
                        "Frank Joyería nació de la pasión por el arte y el lujo. "
                        "Cada pieza es creada a mano por artesanos con más de 20 años "
                        "de experiencia, usando materiales de la más alta calidad.",
                        size=13,
                        color=BLANCO,
                        opacity=0.9,
                    ),
                    ft.Container(height=8),
                    ft.Row([ft.Icon(ICON_STAR, color=DORADO, size=16),
                            ft.Text("Diseños exclusivos y únicos", size=12, color=GRIS_TEXTO)],
                           spacing=8),
                    ft.Row([ft.Icon(ICON_STAR, color=DORADO, size=16),
                            ft.Text("Materiales certificados", size=12, color=GRIS_TEXTO)],
                           spacing=8),
                    ft.Row([ft.Icon(ICON_STAR, color=DORADO, size=16),
                            ft.Text("Garantía de por vida", size=12, color=GRIS_TEXTO)],
                           spacing=8),
                    ft.Container(height=15),
                    ft.Container(
                        content=ft.Text(
                            "Cerrar",
                            color=NEGRO,
                            weight=FONT_WEIGHT_BOLD,
                            size=13,
                            text_align=TEXT_ALIGN_CENTER,
                        ),
                        bgcolor=DORADO,
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=12),
                        on_click=cerrar,
                        ink=True,
                        expand=True,
                    ),
                    ft.Container(height=10),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=25, vertical=20),
            ),
        )
        self.page.update()

    def _ver_detalle(self, producto: dict):
        """Placeholder para la vista de detalle de producto."""
        self._snack(f"🔍 {producto.get('name')} — Detalle próximamente", BLANCO, "#222222")

    def _agregar_carrito(self, producto: dict):
        """Agrega un producto al carrito. TODO: implementar estado de carrito."""
        self._snack(f"✅ {producto.get('name')} agregado al carrito", NEGRO, DORADO)

    def _on_carrito_click(self, _e):
        """Placeholder para la vista del carrito."""
        self._snack("🛍️ Carrito próximamente", BLANCO, "#222222")

    def _snack(self, msg: str, text_color: str, bg: str):
        """
        Muestra un SnackBar con mensaje.

        API Flet 0.84:
        - Asignar a page.snack_bar.
        - Activar con page.snack_bar.open = True + page.update().
        - page.show_snack_bar() y page.open() no existen en esta versión.
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color=text_color),
            bgcolor=bg,
            duration=2000,
            open=True,
        )
        self.page.update()


# ──────────────────────────────────────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    """Entry point requerido por ft.app(). Instancia el controlador principal."""
    FrankJoyeriaPremium(page)


if __name__ == "__main__":
    ft.app(
        target=main,
        assets_dir="Imagenes",
    )