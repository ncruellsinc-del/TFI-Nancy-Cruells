import sqlite3

from colorama import Fore, Style, init
init(autoreset=True)  # Restablece automáticamente los colores al final de cada print

COLOR_TITULO = Fore.CYAN + Style.BRIGHT
COLOR_EXITO = Fore.GREEN + Style.BRIGHT
COLOR_ERROR = Fore.RED + Style.BRIGHT
COLOR_ALERTA = Fore.YELLOW + Style.BRIGHT
COLOR_MENU = Fore.BLUE + Style.BRIGHT
RESET_ESTILO = Style.RESET_ALL

DB_NAME = "inventario.db"

# FUNCIONES DE BASE DE DATOS
def conectar_db():
    """Establece y devuelve la conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    """
    Crea la tabla 'productos' en inventario.db si no existe previamente.
    Estructura: id, nombre, descripcion, cantidad, precio, categoria.
    """
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    cantidad INTEGER NOT NULL,
                    precio REAL NOT NULL,
                    categoria TEXT
                )
            ''')
            conexion.commit()
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] No se pudo inicializar la base de datos: {e}{RESET_ESTILO}")

def registrar_producto(nombre, descripcion, cantidad, precio, categoria):
    """Inserta un nuevo registro utilizando consultas parametrizadas."""
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, descripcion, cantidad, precio, categoria))
            conexion.commit()
            return True
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] Error al registrar el producto: {e}{RESET_ESTILO}")
        return False

def obtener_todos_los_productos():
    """Recupera todos los productos ordenados por ID."""
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre, descripcion, cantidad, precio, categoria FROM productos ORDER BY id ASC")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] Error al consultar la base de datos: {e}{RESET_ESTILO}")
        return []

def obtener_producto_por_id(producto_id):
    """Busca y retorna un único producto mediante su ID."""
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre, descripcion, cantidad, precio, categoria FROM productos WHERE id = ?", (producto_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] Error al buscar por ID: {e}{RESET_ESTILO}")
        return None

def buscar_productos_por_texto(criterio):
    """Busca coincidencias parciales por nombre o categoría."""
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            patron = f"%{criterio}%"
            cursor.execute('''
                SELECT id, nombre, descripcion, cantidad, precio, categoria 
                FROM productos 
                WHERE nombre LIKE ? OR categoria LIKE ?
                ORDER BY id ASC
            ''', (patron, patron))
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] Error en la búsqueda de texto: {e}{RESET_ESTILO}")
        return []

def actualizar_producto_db(producto_id, nombre, descripcion, cantidad, precio, categoria):
    """Actualiza la información de un producto existente dado su ID."""
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                UPDATE productos 
                SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?
                WHERE id = ?
            ''', (nombre, descripcion, cantidad, precio, categoria, producto_id))
            conexion.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] Error al actualizar el producto: {e}{RESET_ESTILO}")
        return False

def eliminar_producto_db(producto_id):
    """Elimina permanentemente un producto de la base de datos por su ID."""
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conexion.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] Error al eliminar el producto: {e}{RESET_ESTILO}")
        return False

def obtener_reporte_bajo_stock(limite):
    """Retorna productos con cantidad igual o inferior al límite establecido."""
    try:
        with conectar_db() as conexion:
            cursor = conexion.cursor()
            cursor.execute('''
                SELECT id, nombre, descripcion, cantidad, precio, categoria 
                FROM productos 
                WHERE cantidad <= ?
                ORDER BY cantidad ASC
            ''', (limite,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"{COLOR_ERROR}[ERROR] Error al generar el reporte: {e}{RESET_ESTILO}")
        return []


# FUNCIONES AUXILIARES DE VALIDACIÓN Y TABLA
def mostrar_tabla_productos(lista_productos):
    """Muestra una lista de productos formateada en tabla con ancho de columnas fijo."""
    if not lista_productos:
        print(f"{COLOR_ALERTA}No se encontraron productos registrados.{RESET_ESTILO}")
        return

    print(f"\n{COLOR_TITULO}{'ID':<5} | {'Nombre':<20} | {'Categoría':<15} | {'Cant.':<7} | {'Precio':<10} | {'Descripción'}{RESET_ESTILO}")
    print("-" * 85)
    for p in lista_productos:
        p_id, nom, desc, cant, prec, cat = p
        cat_txt = cat if cat else "Sin Cat."
        desc_corta = (desc[:20] + '..') if desc and len(desc) > 22 else (desc or "Sin desc.")
        print(f"{p_id:<5} | {nom:<20} | {cat_txt:<15} | {cant:<7} | ${prec:<9.2f} | {desc_corta}")
    print("-" * 85)

def pedir_entero(mensaje, es_obligatorio=True):
    """Solicita y valida un número entero positivo."""
    while True:
        entrada = input(mensaje).strip()
        if not es_obligatorio and entrada == "":
            return None
        if entrada.isdigit():
            return int(entrada)
        print(f"{COLOR_ERROR}¡Error! Debe ingresar un número entero válido.{RESET_ESTILO}")

def pedir_flotante(mensaje, es_obligatorio=True):
    """Solicita y valida un número decimal positivo (precio)."""
    while True:
        entrada = input(mensaje).strip()
        if not es_obligatorio and entrada == "":
            return None
        try:
            val = float(entrada)
            if val >= 0:
                return val
            print(f"{COLOR_ERROR}¡Error! El valor no puede ser negativo.{RESET_ESTILO}")
        except ValueError:
            print(f"{COLOR_ERROR}¡Error! Debe ingresar un valor numérico (ej: 150 o 99.50).{RESET_ESTILO}")


# VISTAS DE NAVEGACIÓN
def vista_registrar():
    """Flujo para el registro de nuevos productos con opción de repetir (S/N)."""
    while True:
        print(f"\n{COLOR_TITULO}=== REGISTRAR NUEVO PRODUCTO ==={RESET_ESTILO}")
        
        while True:
            nombre = input("Nombre del producto (obligatorio): ").strip().title()
            if nombre:
                break
            print(f"{COLOR_ERROR}El nombre del producto no puede estar vacío.{RESET_ESTILO}")

        descripcion = input("Descripción breve (opcional): ").strip()
        cantidad = pedir_entero("Cantidad en stock (entero): ")
        precio = pedir_flotante("Precio ($): ")
        categoria = input("Categoría (opcional): ").strip().title()

        if registrar_producto(nombre, descripcion, cantidad, precio, categoria):
            print(f"\n{COLOR_EXITO}¡Producto '{nombre}' registrado correctamente en inventario.db!{RESET_ESTILO}")

        # Confirmación para agregar otro producto consecutivamente
        continuar = input(f"\n{COLOR_ALERTA}¿Desea agregar otro producto? (S/N): {RESET_ESTILO}").strip().upper()
        if continuar != "S":
            break

def vista_visualizar():
    """Flujo para consultar todos los productos."""
    print(f"\n{COLOR_TITULO}=== INVENTARIO COMPLETO DE PRODUCTOS ==={RESET_ESTILO}")
    productos = obtener_todos_los_productos()
    mostrar_tabla_productos(productos)

def vista_actualizar():
    """Flujo para modificar un producto mediante su ID."""
    print(f"\n{COLOR_TITULO}=== ACTUALIZAR PRODUCTO POR ID ==={RESET_ESTILO}")
    p_id = pedir_entero("Ingrese el ID del producto que desea actualizar: ")
    producto = obtener_producto_por_id(p_id)

    if not producto:
        print(f"{COLOR_ERROR}No se encontró ningún producto con el ID {p_id}.{RESET_ESTILO}")
        return

    print(f"\n{COLOR_ALERTA}Producto seleccionado actualmente:{RESET_ESTILO}")
    mostrar_tabla_productos([producto])
    print(f"{COLOR_MENU}(Presione ENTER sin escribir nada para conservar el valor actual){RESET_ESTILO}\n")

    p_id, nom_act, desc_act, cant_act, prec_act, cat_act = producto

    nuevo_nombre = input(f"Nuevo nombre [{nom_act}]: ").strip().title() or nom_act
    nueva_desc = input(f"Nueva descripción [{desc_act or 'Sin desc.'}]: ").strip()
    if nueva_desc == "":
        nueva_desc = desc_act

    nueva_cant = pedir_entero(f"Nueva cantidad [{cant_act}]: ", es_obligatorio=False)
    if nueva_cant is None:
        nueva_cant = cant_act

    nuevo_precio = pedir_flotante(f"Nuevo precio [${prec_act:.2f}]: ", es_obligatorio=False)
    if nuevo_precio is None:
        nuevo_precio = prec_act

    nueva_cat = input(f"Nueva categoría [{cat_act or 'Sin Cat.'}]: ").strip().title() or cat_act

    if actualizar_producto_db(p_id, nuevo_nombre, nueva_desc, nueva_cant, nuevo_precio, nueva_cat):
        print(f"\n{COLOR_EXITO}¡Producto ID {p_id} actualizado con éxito!{RESET_ESTILO}")

def vista_eliminar():
    """Flujo para eliminar productos con opción de repetir (S/N)."""
    while True:
        print(f"\n{COLOR_TITULO}=== ELIMINAR PRODUCTO POR ID ==={RESET_ESTILO}")
        productos = obtener_todos_los_productos()
        if not productos:
            print(f"{COLOR_ALERTA}No quedan productos registrados para eliminar.{RESET_ESTILO}")
            break

        mostrar_tabla_productos(productos)
        p_id = pedir_entero("Ingrese el ID del producto a eliminar: ")
        producto = obtener_producto_por_id(p_id)

        if not producto:
            print(f"{COLOR_ERROR}No existe ningún producto con el ID {p_id}.{RESET_ESTILO}")
        else:
            mostrar_tabla_productos([producto])
            confirmacion = input(f"{COLOR_ALERTA}¿Está seguro de que desea eliminar este producto? (S/N): {RESET_ESTILO}").strip().upper()
            
            if confirmacion == "S":
                if eliminar_producto_db(p_id):
                    print(f"\n{COLOR_EXITO}¡Producto ID {p_id} eliminado exitosamente.{RESET_ESTILO}")
            else:
                print(f"\n{COLOR_MENU}Operación cancelada.{RESET_ESTILO}")

        # Confirmación para eliminar otro producto consecutivamente
        respuesta = input(f"\n{COLOR_ALERTA}¿Desea eliminar otro producto? (S/N): {RESET_ESTILO}").strip().upper()
        if respuesta != "S":
            break

def vista_buscar():
    """Flujo para buscar por ID o coincidencia en Nombre / Categoría."""
    print(f"\n{COLOR_TITULO}=== BÚSQUEDA DE PRODUCTOS ==={RESET_ESTILO}")
    print("1. Buscar por ID único")
    print("2. Buscar por Nombre o Categoría")
    
    opcion = input("Seleccione tipo de búsqueda (1-2): ").strip()
    
    if opcion == "1":
        p_id = pedir_entero("Ingrese el ID a buscar: ")
        prod = obtener_producto_por_id(p_id)
        mostrar_tabla_productos([prod] if prod else [])
    elif opcion == "2":
        criterio = input("Ingrese el texto a buscar (Nombre o Categoría): ").strip()
        if criterio:
            resultados = buscar_productos_por_texto(criterio)
            mostrar_tabla_productos(resultados)
        else:
            print(f"{COLOR_ERROR}El criterio de búsqueda no puede estar vacío.{RESET_ESTILO}")
    else:
        print(f"{COLOR_ERROR}Opción no válida.{RESET_ESTILO}")

def vista_reporte_stock():
    """Flujo para filtrar productos con stock bajo o igual al límite estipulado."""
    print(f"\n{COLOR_TITULO}=== REPORTE DE PRODUCTOS BAJO STOCK ==={RESET_ESTILO}")
    limite = pedir_entero("Ingrese la cantidad máxima de stock límite: ")
    reporte = obtener_reporte_bajo_stock(limite)
    
    print(f"\n{COLOR_ALERTA}Productos con stock igual o inferior a {limite} unidades:{RESET_ESTILO}")
    mostrar_tabla_productos(reporte)

# MENÚ PRINCIPAL DEL SISTEMA
def menu_principal():
    """Punto de entrada de la aplicación."""
    inicializar_db()

    while True:
        print(f"\n{COLOR_MENU}{'='*55}{RESET_ESTILO}")
        print(f"{COLOR_TITULO}{'SISTEMA DE GESTIÓN DE INVENTARIO':^55}{RESET_ESTILO}")
        print(f"{COLOR_MENU}{'='*55}{RESET_ESTILO}")
        print(f"  {COLOR_TITULO}1.{RESET_ESTILO} Registrar nuevo producto")
        print(f"  {COLOR_TITULO}2.{RESET_ESTILO} Visualizar todos los productos")
        print(f"  {COLOR_TITULO}3.{RESET_ESTILO} Actualizar datos de un producto por ID")
        print(f"  {COLOR_TITULO}4.{RESET_ESTILO} Eliminar producto por ID")
        print(f"  {COLOR_TITULO}5.{RESET_ESTILO} Buscar producto (por ID / Nombre / Categoría)")
        print(f"  {COLOR_TITULO}6.{RESET_ESTILO} Reporte de productos bajo stock")
        print(f"  {COLOR_TITULO}7.{RESET_ESTILO} Salir del sistema")
        print(f"{COLOR_MENU}{'='*55}{RESET_ESTILO}")

        opcion = input("Seleccione una opción (1-7): ").strip()

        match opcion:
            case "1": vista_registrar()
            case "2": vista_visualizar()
            case "3": vista_actualizar()
            case "4": vista_eliminar()
            case "5": vista_buscar()
            case "6": vista_reporte_stock()
            case "7":
                print(f"\n{COLOR_EXITO}¡Gracias por utilizar el Sistema de Inventario! Hasta pronto.{RESET_ESTILO}")
                break
            case _:
                print(f"{COLOR_ERROR}¡Opción inválida! Ingrese un número entre el 1 y el 7.{RESET_ESTILO}")

if __name__ == "__main__":
    menu_principal()