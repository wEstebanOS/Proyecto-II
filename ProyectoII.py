import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import json
import os

# ============== CONFIGURACIÓN ================
ANCHO = 20
ALTO = 20
TAM = 28

# Tipos de casilla
CAMINO = 0
MURO = 1
TUNEL = 2
LIANA = 3

# Archivo para puntajes
ARCHIVO_PUNTAJES = "puntajes.json"


if not os.path.exists(ARCHIVO_PUNTAJES):
    with open(ARCHIVO_PUNTAJES, "w", encoding="utf-8") as f:
        json.dump({"escapa": [], "cazador": []}, f)

with open(ARCHIVO_PUNTAJES, "r", encoding="utf-8") as f:
    puntajes = json.load(f)

# =============== CLASES Y UTILIDADES =================

class Casilla:
    def __init__(self, tipo):
        self.tipo = tipo

    def permite_jugador(self, modo):

        if modo == "Escapa":
            if self.tipo == CAMINO: return True
            if self.tipo == TUNEL: return True
            if self.tipo == LIANA: return False
            if self.tipo == MURO: return False

        if modo == "Cazador":
            if self.tipo == CAMINO: return True
            if self.tipo == LIANA: return True
            if self.tipo == TUNEL: return False
            if self.tipo == MURO: return False
        return False

    def permite_enemigo(self, modo):

        if modo == "Escapa":
            if self.tipo == CAMINO: return True
            if self.tipo == LIANA: return True
            if self.tipo == TUNEL: return False
            if self.tipo == MURO: return False

        if modo == "Cazador":
            if self.tipo == CAMINO: return True
            if self.tipo == TUNEL: return True
            if self.tipo == LIANA: return False
            if self.tipo == MURO: return False
        return False

class Enemigo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vivo = True
        self.respawn_time = 0.0

class Jugador:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.energia = 100
        self.max_energia = 100
        self.correr = False

def clave_puntaje(e):
    return e["puntos"]

# ===================== GENERACIÓN DE MAPA ====================

def generar_mapa():
    mapa = []
    for fila in range(ALTO):
        fila_nueva = []
        for col in range(ANCHO):
            r = random.random()
            if r < 0.70:
                fila_nueva.append(CAMINO)
            elif r < 0.82:
                fila_nueva.append(MURO)
            elif r < 0.92:
                fila_nueva.append(TUNEL)
            else:
                fila_nueva.append(LIANA)
        mapa.append(fila_nueva)

    # Garantizar inicio y salida de caminos
    mapa[0][0] = CAMINO
    salida_pos = (ALTO - 1, ANCHO // 2)
    mapa[salida_pos[0]][salida_pos[1]] = CAMINO
    return mapa, salida_pos

# ===================== PUNTAJES ====================

def guardar_puntaje(modo, nombre, puntos):
    global puntajes
    clave = modo.lower()
    if clave not in puntajes:
        puntajes[clave] = []
    puntajes[clave].append({"nombre": nombre, "puntos": puntos, "fecha": time.strftime("%Y-%m-%d %H:%M:%S")})
    puntajes[clave].sort(key=clave_puntaje, reverse=True)
    puntajes[clave] = puntajes[clave][:5]
    with open(ARCHIVO_PUNTAJES, "w", encoding="utf-8") as f:
        json.dump(puntajes, f, ensure_ascii=False, indent=2)

def borrar_puntajes():
    global puntajes
    puntajes = {"escapa": [], "cazador": []}
    with open(ARCHIVO_PUNTAJES, "w", encoding="utf-8") as f:
        json.dump(puntajes, f, ensure_ascii=False, indent=2)
    messagebox.showinfo("Puntajes", "Puntajes reiniciados.")

# =================== TOP5 ===================

def mostrar_top5(parent):
    ventana = tk.Toplevel(parent)
    ventana.title("Top 5 - Puntajes")
    ventana.geometry("360x340")
    tk.Label(ventana, text="Top 5 - Modo Escapa", font=("Arial", 12, "bold")).pack(pady=(8,4))
    lista_escapa = puntajes.get("escapa", [])
    if not lista_escapa:
        tk.Label(ventana, text="(Sin puntajes)", font=("Arial", 11)).pack()
    else:
        for i, e in enumerate(lista_escapa, start=1):
            tk.Label(ventana, text=f"{i}. {e['nombre']} — {e['puntos']}", font=("Arial", 11)).pack(anchor="w", padx=12)

    tk.Label(ventana, text=" ", font=("Arial", 6)).pack()
    tk.Label(ventana, text="Top 5 - Modo Cazador", font=("Arial", 12, "bold")).pack(pady=(6,4))
    lista_cazador = puntajes.get("cazador", [])
    if not lista_cazador:
        tk.Label(ventana, text="(Sin puntajes)", font=("Arial", 11)).pack()
    else:
        for i, e in enumerate(lista_cazador, start=1):
            tk.Label(ventana, text=f"{i}. {e['nombre']} — {e['puntos']}", font=("Arial", 11)).pack(anchor="w", padx=12)

    # Botón para cerrar
    def cerrar_top():
        ventana.destroy()
    tk.Button(ventana, text="Cerrar", command=cerrar_top).pack(pady=12)

# ======================== VENTANA DE REGISTRO =============================

def ventana_registro(root):
    reg = tk.Toplevel(root)
    reg.title("Registro de Jugador")
    reg.geometry("420x300")
    reg.resizable(False, False)

    tk.Label(reg, text="Registro", font=("Arial", 16, "bold")).pack(pady=(10,6))

    tk.Label(reg, text="Ingrese su nombre:", font=("Arial", 11)).pack(pady=(6,2))
    entrada_nombre = tk.Entry(reg, font=("Arial", 12), width=28)
    entrada_nombre.pack(pady=(0,8))

    tk.Label(reg, text="Seleccione modo de juego:", font=("Arial", 11)).pack(pady=(4,2))
    cb_modo = ttk.Combobox(reg, values=["Escapa", "Cazador"], state="readonly", width=20)
    cb_modo.pack(pady=(0,8))
    cb_modo.current(0)

    tk.Label(reg, text="Seleccione dificultad:", font=("Arial", 11)).pack(pady=(4,2))
    cb_dif = ttk.Combobox(reg, values=["Fácil", "Medio", "Difícil"], state="readonly", width=20)
    cb_dif.pack(pady=(0,8))
    cb_dif.current(0)


    def continuar_registro():
        nombre = entrada_nombre.get().strip()
        modo = cb_modo.get()
        dif = cb_dif.get()
        if nombre == "":
            messagebox.showerror("Registro", "Por favor ingrese un nombre.")
            return
        reg.destroy()
        iniciar_juego(root, nombre, modo, dif)

    def cancelar_registro():
        reg.destroy()

    btn_frame = tk.Frame(reg)
    btn_frame.pack(pady=12)
    btn_ok = tk.Button(btn_frame, text="Iniciar", width=12, command=continuar_registro)
    btn_ok.grid(row=0, column=0, padx=8)
    btn_cancel = tk.Button(btn_frame, text="Cancelar", width=12, command=cancelar_registro)
    btn_cancel.grid(row=0, column=1, padx=8)

# =========================================================================

def iniciar_juego(root, nombre, modo, dificultad):
    # Ventana de juego
    ventana = tk.Toplevel(root)
    ventana.title(f"Juego - {modo} - {nombre}")
    ventana.resizable(False, False)

    canvas = tk.Canvas(ventana, width=ANCHO * TAM, height=ALTO * TAM, bg="#111111")
    canvas.grid(row=0, column=0, padx=6, pady=6)

    panel = tk.Frame(ventana, width=220)
    panel.grid(row=0, column=1, sticky="n", padx=(8,12), pady=6)

    tk.Label(panel, text=f"Jugador: {nombre}", font=("Arial", 12)).pack(pady=(6,2))
    lbl_puntos = tk.Label(panel, text="Puntos: 0", font=("Arial", 12))
    lbl_puntos.pack(pady=(4,4))
    lbl_energia = tk.Label(panel, text="Energía: 100", font=("Arial", 12))
    lbl_energia.pack(pady=(2,8))

    # Velocidad enemigos
    if dificultad == "Fácil":
        intervalo_enemigo = 420
    elif dificultad == "Medio":
        intervalo_enemigo = 280
    else:
        intervalo_enemigo = 160

    # Número de enemigos segun dificultad
    if dificultad == "Fácil":
        num_enemigos = 3
    elif dificultad == "Medio":
        num_enemigos = 5
    else:
        num_enemigos = 7

    # Crear mapa y salida
    mapa_nums, salida_pos = generar_mapa()
    # hacer objetos a las casillas
    mapa = [[Casilla(mapa_nums[r][c]) for c in range(ANCHO)] for r in range(ALTO)]

    jugador = Jugador()
    jugador.x, jugador.y = 0, 0

    # Crear enemigos en posiciones válidas para enemigos
    enemigos = []
    intentos_spawn = 0
    while len(enemigos) < num_enemigos and intentos_spawn < 2000:
        intentos_spawn += 1
        ex = random.randint(0, ANCHO - 1)
        ey = random.randint(0, ALTO - 1)
        if (ex, ey) == (jugador.x, jugador.y): continue
        if (ey, ex) == salida_pos or (ey, ex) == salida_pos: pass
        # spawn solo si tile permite enemigo en este modo
        if mapa[ey][ex].permite_enemigo(modo):
            enemigos.append(Enemigo(ex, ey))

    puntos = 0
    trampas = []
    trampa_cooldown_until = 0.0

    # tiempos para puntaje en cazador y regeneracion energia
    tiempo_inicio = time.time()
    ultimo_bonus_cazador = tiempo_inicio
    ultimo_regen = time.time()


    def dibujar():
        canvas.delete("all")
        # mapa
        for r in range(ALTO):
            for c in range(ANCHO):
                t = mapa[r][c].tipo
                x0 = c * TAM
                y0 = r * TAM
                x1 = x0 + TAM
                y1 = y0 + TAM
                color = "#ecebe7"
                if t == CAMINO:
                    color = "#ecebe7"
                elif t == MURO:
                    color = "#0c344e"
                elif t == TUNEL:
                    color = "#6ecae6"
                elif t == LIANA:
                    color = "#2f9a2f"
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#0c344e")

        # salida
        sr, sc = salida_pos
        sx0 = sc * TAM
        sy0 = sr * TAM
        sx1 = sx0 + TAM
        sy1 = sy0 + TAM
        canvas.create_rectangle(sx0+2, sy0+2, sx1-2, sy1-2, fill="#d4412d", outline="#b27f00")
        canvas.create_text(sx0 + TAM/2, sy0 + TAM/2, text="SAL", font=("Arial", 8, "bold"))

        # trampas
        for (tx, ty) in trampas:
            canvas.create_oval(tx*TAM+6, ty*TAM+6, tx*TAM+TAM-6, ty*TAM+TAM-6, fill="#000000")

        # enemigos
        for e in enemigos:
            if e.vivo:
                ex0 = e.x * TAM + 6
                ey0 = e.y * TAM + 6
                canvas.create_rectangle(ex0, ey0, ex0+TAM-12, ey0+TAM-12, fill="#2a7078")

        # circulillo
        jx0 = jugador.x * TAM + 4
        jy0 = jugador.y * TAM + 4
        canvas.create_oval(jx0, jy0, jx0+TAM-8, jy0+TAM-8, fill="#d4412d")

        # actualizar hud
        ventana.update_idletasks()

    # mover circulillo
    def intentar_mover_un_paso(dy, dx):
        """Intenta mover un paso; devuelve True si se movió."""
        ny = jugador.y + dy
        nx = jugador.x + dx
        if nx < 0 or nx >= ANCHO or ny < 0 or ny >= ALTO:
            return False
        if mapa[ny][nx].permite_jugador(modo):
            jugador.x = nx
            jugador.y = ny
            return True
        return False

    #movimiento circulillo caminar y correr
    def mover_con_tecla(dy, dx):
        nonlocal tiempo_inicio, ultimo_regen
        pasos_a_intentar = 1
        if jugador.correr:
            pasos_a_intentar = 2  # opción A: dos casillas por tecla
        pasos_logrados = 0
        for i in range(pasos_a_intentar):
            # Comprobar energia suficiente
            if jugador.correr:
                if jugador.energia <= 0:
                    # Parar si no hay energia
                    jugador.correr = False
                    break
                # 2 energia por paso
                jugador.energia -= 2
                if jugador.energia < 0:
                    jugador.energia = 0
            moved = intentar_mover_un_paso(dy, dx)
            if not moved:
                break
            pasos_logrados += 1
        # Si no energia, no correr
        if jugador.energia <= 0:
            jugador.correr = False
        # actualizar regeneracion
        ultimo_regen = time.time()

    def tecla_presionada(event):
        key = event.keysym
        if key == "Up":
            mover_con_tecla(-1, 0)
        elif key == "Down":
            mover_con_tecla(1, 0)
        elif key == "Left":
            mover_con_tecla(0, -1)
        elif key == "Right":
            mover_con_tecla(0, 1)
        elif key == "space":
            colocar_trampa()
        elif key == "r" or key == "R":
            # alternar correr si hay energia
            if jugador.correr:
                jugador.correr = False
            else:
                if jugador.energia > 0:
                    jugador.correr = True
        comprobar_post_movimiento()

    ventana.bind("<Key>", tecla_presionada)
    ventana.focus_set()

    # tramps
    def colocar_trampa():
        nonlocal trampa_cooldown_until
        if modo != "Escapa":
            return
        ahora = time.time()
        if ahora < trampa_cooldown_until:
            return
        if len(trampas) >= 3:
            return
        pos = (jugador.x, jugador.y)
        if pos in trampas:
            return
        trampas.append(pos)
        trampa_cooldown_until = ahora + 5.0

    # logica de los malos grrr
    ultimo_movimiento_enemigos = 0.0
    def mover_enemigos():
        nonlocal puntos, ultimo_movimiento_enemigos
        ahora = time.time()
        # controlar tiempo entre pasos
        if (ahora - ultimo_movimiento_enemigos) * 1000.0 < intervalo_enemigo:
            return
        ultimo_movimiento_enemigos = ahora

        for e in enemigos:
            # respawn si muerto y tiempo cumplido
            if not e.vivo:
                if ahora >= e.respawn_time:
                    # buscar posición válida para respawnear
                    intent = 0
                    while intent < 500:
                        intent += 1
                        nx = random.randint(0, ANCHO - 1)
                        ny = random.randint(0, ALTO - 1)
                        if (nx, ny) == (jugador.x, jugador.y): continue
                        if (ny, nx) == salida_pos: pass
                        if mapa[ny][nx].permite_enemigo(modo):
                            e.x = nx
                            e.y = ny
                            e.vivo = True
                            break
                continue

            # Si enemigo está en la misma casilla que jugador
            if e.x == jugador.x and e.y == jugador.y:
                if modo == "Escapa":
                    terminar_partida(derrota=True)
                    return
                else:
                    # circulillo atrapa a los malos
                    puntos += 50
                    e.vivo = False
                    e.respawn_time = ahora + 10.0
                    continue

            # Movimiento simple: un paso en x o en y según perseguir o huir
            dx = 0
            dy = 0
            if modo == "Escapa":
                # perseguir circulillo
                if jugador.x < e.x:
                    dx = -1
                elif jugador.x > e.x:
                    dx = 1
                if jugador.y < e.y:
                    dy = -1
                elif jugador.y > e.y:
                    dy = 1
            else:
                # huir del circulillo
                if jugador.x < e.x:
                    dx = 1
                elif jugador.x > e.x:
                    dx = -1
                if jugador.y < e.y:
                    dy = 1
                elif jugador.y > e.y:
                    dy = -1

            # probar mover en x primero, luego en y; si no posible, intentar otras opciones
            opciones = []
            if dx != 0:
                opciones.append((e.x + dx, e.y))
            if dy != 0:
                opciones.append((e.x, e.y + dy))
            # también agregar movimientos ortogonales como alternativas
            opciones.append((e.x + 1, e.y))
            opciones.append((e.x - 1, e.y))
            opciones.append((e.x, e.y + 1))
            opciones.append((e.x, e.y - 1))

            movido = False
            for nx, ny in opciones:
                if 0 <= nx < ANCHO and 0 <= ny < ALTO:
                    if mapa[ny][nx].permite_enemigo(modo):
                        # no mover encima de otro enemigo vivo
                        ocupado = False
                        for otro in enemigos:
                            if otro is not e and otro.vivo and otro.x == nx and otro.y == ny:
                                ocupado = True
                                break
                        if ocupado:
                            continue
                        e.x = nx
                        e.y = ny
                        movido = True
                        break
            # comprobar si llegó a la salida (modo cazador penaliza si enemigo llega)
            if (e.y, e.x) == salida_pos and e.vivo:
                if modo == "Cazador":
                    # enemigo escapó por la salida: penalizar
                    puntos -= 30
                    e.vivo = False
                    e.respawn_time = ahora + 10.0

            # comprobar trampas (si pisa trampa, muere)
            if (e.x, e.y) in trampas and e.vivo:
                try:
                    trampas.remove((e.x, e.y))
                except ValueError:
                    pass
                e.vivo = False
                e.respawn_time = ahora + 10.0
                puntos += 10

        if modo == "Cazador":
            todos_muertos = True
            for ene in enemigos:
                 if ene.vivo:
                    todos_muertos = False
                    break
            if todos_muertos:
                puntos += 200  # recompensa opcional
                terminar_partida_interna()
                messagebox.showinfo("Partida", f"Los has matado a todos grrr. Puntaje: {puntos}")
                guardar_puntaje(modo, nombre, puntos)
                return

    # Comprobaciones después del movimiento del jugador
    def comprobar_post_movimiento():
        nonlocal puntos
        # si jugador llegó a la salida en modo Escapa -> gana
        if modo == "Escapa":
            if (jugador.y, jugador.x) == salida_pos:
                terminar_partida_interna()
                # calcular puntos por tiempo exacta: puntos_final = puntos + max(0, 200 - segundos_transcurridos)
                tiempo_total = int(time.time() - tiempo_inicio)
                bono = max(0, 200 - tiempo_total)
                puntos_final = puntos + bono
                # asignamos puntos_final antes de terminar
                messagebox.showinfo("Partida", f"¡Has escapado! Tiempo: {tiempo_total}s. Puntaje: {bono}")
                guardar_puntaje(modo, nombre, puntos_final)

                return
        # en modo Cazador la colisión se gestiona en mover_enemigos

    # FIN DE PARTIDA (cerrar ventana)
    def terminar_partida(derrota=False):
        if derrota:
            messagebox.showinfo("Partida", "¡Has sido atrapado! Fin de la partida.")
            guardar_puntaje(modo, nombre, puntos)
        else:
            # en otros casos usamos guardar antes
            guardar_puntaje(modo, nombre, puntos)
        terminar_partida_interna()

    def terminar_partida_interna():
        try:
            ventana.destroy()
        except Exception:
            pass

    # BUCLE PRINCIPAL de actualización
    def actualizar():
        nonlocal puntos, ultimo_bonus_cazador, ultimo_regen
        ahora = time.time()
        # puntos por tiempo para modo Cazador: +2 puntos por segundo jugado
        if modo == "Cazador":
            segundos_trans = int(ahora - ultimo_bonus_cazador)
            if segundos_trans >= 1:
                # añadir 2 puntos por cada segundo transcurrido y avanzar el marcador
                puntos += segundos_trans * 2
                ultimo_bonus_cazador += segundos_trans

        # regeneración de energía: +1 por segundo si NO está corriendo
        if not jugador.correr:
            segundos_regen = int(ahora - ultimo_regen)
            if segundos_regen >= 1:
                jugador.energia = min(jugador.max_energia, jugador.energia + segundos_regen * 1)
                ultimo_regen += segundos_regen

        mover_enemigos()
        dibujar()
        lbl_puntos.config(text=f"Puntos: {puntos}")
        lbl_energia.config(text=f"Energía: {jugador.energia}/{jugador.max_energia}")
        ventana.after(80, actualizar)   # refresco gráfico; enemigos usan su propio intervalo



    
    def cerrar_ventana():
        if messagebox.askyesno("Salir", "¿Deseas salir de la partida?"):
            terminar_partida_interna()
    btn_salir = tk.Button(panel, text="Salir", width=18, command=cerrar_ventana)
    btn_salir.pack(pady=(0,6))

    # Iniciar dibujar y bucle
    dibujar()
    actualizar()

# ------------------ MENÚ PRINCIPAL ------------------

def menu_principal():
    root = tk.Tk()
    root.title("Proyecto II")
    root.geometry("420x520")
    root.resizable(False, False)


    lbl_titulo = tk.Label(root, text="Yumpinelson", font=("Georgia", 30), fg="#d4412d")
    lbl_titulo.pack(pady=(10,8))


    txt_info = ("Una metáfora para el consumismo")
    lbl_info = tk.Label(root, text=txt_info, font=("Arial", 10), justify="left")
    lbl_info.pack(pady=(6,4))


    spacer = tk.Label(root, text="", height=6)
    spacer.pack()

    # Funciones del menu
    def abrir_registro():
        ventana_registro(root)

    def abrir_top5():
        mostrar_top5(root)

    def reiniciar_scores():
        if messagebox.askyesno("Confirmar", "¿Reiniciar todos los puntajes?"):
            borrar_puntajes()

    def salir_app():
        root.destroy()

    btn_jugar = tk.Button(root, text="Jugar", width=24, height=2, font=("Arial", 12), command=abrir_registro)
    btn_jugar.pack(pady=(6,6))

    btn_top5 = tk.Button(root, text="Ver Top 5", width=24, height=2, font=("Arial", 12), command=abrir_top5)
    btn_top5.pack(pady=(6,6))

    btn_reset = tk.Button(root, text="Reiniciar puntajes", width=24, height=2, font=("Arial", 12), command=reiniciar_scores)
    btn_reset.pack(pady=(6,6))

    btn_salir = tk.Button(root, text="Salir", width=24, height=2, font=("Arial", 12), command=salir_app)
    btn_salir.pack(pady=(6,10))

    root.mainloop()

# ================== EJECUCIÓN PRINCIPAL =================

if __name__ == "__main__":
    menu_principal()
