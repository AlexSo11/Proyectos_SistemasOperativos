"""
⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣿⡿⠗⠀⠠⠄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⡜⠁⠀⠀⠀⠀⠀⠈⠑⢶⣶⡄
⢀⣶⣦⣸⠀⢼⣟⡇⠀⠀⢀⣀⠀⠘⡿⠃
⠀⢿⣿⣿⣄⠒⠀⠠⢶⡂⢫⣿⢇⢀⠃⠀
⠀⠈⠻⣿⣿⣿⣶⣤⣀⣀⣀⣂⡠⠊⠀⠀
⠀⠀⠀⠃⠀⠀⠉⠙⠛⠿⣿⣿⣧⠀⠀⠀
⠀⠀⠘⡀⠀⠀⠀⠀⠀⠀⠘⣿⣿⡇⠀⠀
⠀⠀⠀⣷⣄⡀⠀⠀⠀⢀⣴⡟⠿⠃⠀⠀
⠀⠀⠀⢻⣿⣿⠉⠉⢹⣿⣿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠁⠀⠀⠀⠉⠁

Desarrollo AlexWhite USER GIT AlexSo11
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import threading
import random

class Proceso:
    def __init__(self, id_proceso, operacion, dato1, dato2, tiempo_max):
        self.id = id_proceso
        self.operacion = operacion
        self.dato1 = dato1
        self.dato2 = dato2
        self.tiempo_max = tiempo_max
        self.tiempo_restante = tiempo_max
        self.tiempo_transcurrido = 0
        self.resultado = None
        self.estado = "Listo" 

    def calcular_resultado(self):
        try:
            if self.operacion == '+':
                return self.dato1 + self.dato2
            elif self.operacion == '-':
                return self.dato1 - self.dato2
            elif self.operacion == '*':
                return self.dato1 * self.dato2
            elif self.operacion == '/':
                if self.dato2 == 0:
                    return "Error: División por cero"
                return round(self.dato1 / self.dato2, 2)
            elif self.operacion == '%':
                if self.dato2 == 0:
                    return "Error: Módulo por cero"
                return self.dato1 % self.dato2
        except Exception as e:
            return f"Error: {str(e)}"

class SimuladorLotes:
    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ Simulador de Procesos por Lotes")
        self.root.geometry("1100x700")
        self.root.configure(bg="#252526")
        
        # Colores del tema
        self.colors = {
            'bg_dark': "#2d2d2f",
            'bg_medium': "#303136",
            'bg_light': "#56595c",
            'accent_blue': '#53a8e2',
            'accent_green': "#57af92",
            'accent_red': '#ee6055',
            'accent_orange': '#ffa372',
            'text_white': '#eaeaea',
            'text_gray': '#94a3b8'
        }

        self.lotes = []
        self.procesos_terminados = []
        self.contador_global = 0
        self.simulacion_activa = False
        self.pausado = False
        self.error_actual = False
        self.interrumpido = False

        self.configurar_estilos()
        self.crear_interfaz()
        self.generar_procesos()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styles
        style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        style.configure('Card.TFrame', background=self.colors['bg_medium'], 
                       relief='flat', borderwidth=0)
        
        # LabelFrame styles
        style.configure('Card.TLabelframe', background=self.colors['bg_medium'],
                       foreground=self.colors['text_white'], borderwidth=2,
                       relief='solid', bordercolor=self.colors['bg_light'])
        style.configure('Card.TLabelframe.Label', background=self.colors['bg_medium'],
                       foreground=self.colors['accent_blue'], font=('Segoe UI', 11, 'bold'))
        
        # Label styles
        style.configure('Title.TLabel', background=self.colors['bg_medium'],
                       foreground=self.colors['text_white'], font=('Segoe UI', 10))
        style.configure('Info.TLabel', background=self.colors['bg_medium'],
                       foreground=self.colors['text_gray'], font=('Segoe UI', 9))
        style.configure('Stat.TLabel', background=self.colors['bg_dark'],
                       foreground=self.colors['accent_green'], font=('Segoe UI', 12, 'bold'))
        
        # Button styles
        style.configure('Action.TButton', font=('Segoe UI', 9, 'bold'),
                       background=self.colors['accent_blue'], foreground='white',
                       borderwidth=0, focuscolor='none', padding=8)
        style.map('Action.TButton',
                 background=[('active', self.colors['accent_green'])],
                 foreground=[('active', 'white')])
        
        # Treeview style
        style.configure('Custom.Treeview', background=self.colors['bg_light'],
                       foreground=self.colors['text_white'], fieldbackground=self.colors['bg_light'],
                       borderwidth=0, font=('Segoe UI', 9))
        style.configure('Custom.Treeview.Heading', background=self.colors['bg_medium'],
                       foreground=self.colors['accent_blue'], font=('Segoe UI', 10, 'bold'),
                       borderwidth=0)
        style.map('Custom.Treeview', background=[('selected', self.colors['accent_blue'])])

    def crear_interfaz(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors['bg_medium'], height=80)
        header.pack(fill='x', padx=0, pady=0)
        
        title_label = tk.Label(header, text="🖥️ SIMULADOR DE PROCESOS POR LOTES",
                              bg=self.colors['bg_medium'], fg=self.colors['accent_blue'],
                              font=('Segoe UI', 18, 'bold'))
        title_label.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Top section - Lote y Proceso actual
        top_frame = tk.Frame(main_container, bg=self.colors['bg_dark'])
        top_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Lote en ejecución
        lote_container = tk.Frame(top_frame, bg=self.colors['bg_medium'], 
                                 highlightbackground=self.colors['accent_blue'],
                                 highlightthickness=2)
        lote_container.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        lote_title = tk.Label(lote_container, text="📦 LOTE EN EJECUCIÓN",
                            bg=self.colors['bg_medium'], fg=self.colors['accent_blue'],
                            font=('Segoe UI', 12, 'bold'), pady=10)
        lote_title.pack()
        
        self.lote_frame = tk.Frame(lote_container, bg=self.colors['bg_medium'])
        self.lote_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Proceso en ejecución
        proceso_container = tk.Frame(top_frame, bg=self.colors['bg_medium'],
                                    highlightbackground=self.colors['accent_green'],
                                    highlightthickness=2)
        proceso_container.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        proceso_title = tk.Label(proceso_container, text="⚙️ PROCESO EN EJECUCIÓN",
                               bg=self.colors['bg_medium'], fg=self.colors['accent_green'],
                               font=('Segoe UI', 12, 'bold'), pady=10)
        proceso_title.pack()
        
        self.proceso_frame = tk.Frame(proceso_container, bg=self.colors['bg_medium'])
        self.proceso_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Bottom section - Terminados
        terminados_container = tk.Frame(main_container, bg=self.colors['bg_medium'],
                                       highlightbackground=self.colors['accent_orange'],
                                       highlightthickness=2)
        terminados_container.pack(fill='both', expand=True)
        
        terminados_title = tk.Label(terminados_container, text="✅ PROCESOS TERMINADOS",
                                   bg=self.colors['bg_medium'], fg=self.colors['accent_orange'],
                                   font=('Segoe UI', 12, 'bold'), pady=10)
        terminados_title.pack()
        
        tree_frame = tk.Frame(terminados_container, bg=self.colors['bg_medium'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columns = ("ID", "Operación", "Datos", "Resultado")
        self.tree_terminados = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                          height=8, style='Custom.Treeview')
        
        for col in columns:
            self.tree_terminados.heading(col, text=col)
            self.tree_terminados.column(col, width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_terminados.yview)
        self.tree_terminados.configure(yscrollcommand=scrollbar.set)
        
        self.tree_terminados.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Footer - Stats y controles
        footer = tk.Frame(self.root, bg=self.colors['bg_medium'], height=100)
        footer.pack(fill='x', padx=0, pady=0)
        
        # Stats
        stats_frame = tk.Frame(footer, bg=self.colors['bg_medium'])
        stats_frame.pack(pady=15)
        
        # Contador Global
        contador_card = tk.Frame(stats_frame, bg=self.colors['bg_light'], 
                                highlightbackground=self.colors['accent_green'],
                                highlightthickness=2)
        contador_card.pack(side='left', padx=10)
        
        tk.Label(contador_card, text="⏱️ Contador Global",
                bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                font=('Segoe UI', 9)).pack(padx=20, pady=(8, 2))
        self.lbl_contador_global = tk.Label(contador_card, text="0",
                                           bg=self.colors['bg_light'],
                                           fg=self.colors['accent_green'],
                                           font=('Segoe UI', 20, 'bold'))
        self.lbl_contador_global.pack(padx=20, pady=(0, 8))
        
        # Lotes Pendientes
        lotes_card = tk.Frame(stats_frame, bg=self.colors['bg_light'],
                             highlightbackground=self.colors['accent_blue'],
                             highlightthickness=2)
        lotes_card.pack(side='left', padx=10)
        
        tk.Label(lotes_card, text="📊 Lotes Pendientes",
                bg=self.colors['bg_light'], fg=self.colors['text_gray'],
                font=('Segoe UI', 9)).pack(padx=20, pady=(8, 2))
        self.lbl_lotes_pendientes = tk.Label(lotes_card, text="0",
                                            bg=self.colors['bg_light'],
                                            fg=self.colors['accent_blue'],
                                            font=('Segoe UI', 20, 'bold'))
        self.lbl_lotes_pendientes.pack(padx=20, pady=(0, 8))
        
        # Botones
        buttons_frame = tk.Frame(stats_frame, bg=self.colors['bg_medium'])
        buttons_frame.pack(side='left', padx=20)
        
        btn_config = [
            ("▶️ Iniciar", self.iniciar_simulacion, self.colors['accent_green']),
            ("🔄 Interrumpir", self.interrumpir_actual, self.colors['accent_orange']),
            ("❌ Error", self.error_en_actual, self.colors['accent_red']),
            ("⏸️ Pausar", self.pausar_simulacion, self.colors['accent_blue']),
            ("▶️ Continuar", self.continuar_simulacion, self.colors['accent_green']),
            ("🚪 Salir", self.root.quit, '#64748b')
        ]
        
        for i, (text, cmd, color) in enumerate(btn_config):
            btn = tk.Button(buttons_frame, text=text, command=cmd,
                          bg=color, fg='white', font=('Segoe UI', 9, 'bold'),
                          relief='flat', cursor='hand2', padx=15, pady=8,
                          borderwidth=0)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            
            # Efecto hover
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.configure(bg=self._darken_color(c)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
        
        # Binding de tecla 'C' para continuar
        self.root.bind('c', lambda e: self.continuar_simulacion())
        self.root.bind('C', lambda e: self.continuar_simulacion())

    def _darken_color(self, color):
        """Oscurece un color hex para el efecto hover"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f'#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}'

    def generar_procesos(self):
        num_trabajos = simpledialog.askinteger("Número de trabajos", 
                                              "Ingrese el número de trabajos a simular:",
                                              minvalue=1)
        if num_trabajos is None:
            self.root.quit()
            return
        
        operaciones = ['+', '-', '*', '/', '%']
        procesos = []
        for i in range(1, num_trabajos + 1):
            tiempo = random.randint(7, 18)
            oper = random.choice(operaciones)
            d1, d2 = random.randint(1, 20), random.randint(1, 20)
            procesos.append(Proceso(i, oper, d1, d2, tiempo))
        procesos.sort(key=lambda p: p.id)
        self.lotes = self.dividir_en_lotes(procesos, 3)
        self.actualizar_lotes_pendientes()

    def dividir_en_lotes(self, lista_procesos, tamaño_lote=3):
        return [lista_procesos[i:i + tamaño_lote] for i in range(0, len(lista_procesos), tamaño_lote)]

    def iniciar_simulacion(self):
        if self.simulacion_activa:
            return
        self.simulacion_activa = True
        threading.Thread(target=self.simular_lotes, daemon=True).start()

    def simular_lotes(self):
        self.contador_global = 0
        self.procesos_terminados.clear()
        for lote in list(self.lotes):
            self.root.after(0, lambda l=lote: self.mostrar_lote_actual(l))
            self.lotes.remove(lote)
            self.actualizar_lotes_pendientes()
            
            for proceso in lote:
                while proceso.tiempo_restante > 0:
                    if self.error_actual:
                        proceso.resultado = "ERROR"
                        proceso.estado = "Error"
                        self.error_actual = False
                        self.root.after(0, lambda p=proceso: self.agregar_proceso_terminado(p))
                        break
                    
                    if self.interrumpido:
                        proceso.estado = "Interrumpido"
                        self.interrumpido = False
                        proceso.tiempo_restante = proceso.tiempo_max
                        proceso.tiempo_transcurrido = 0
                        lote.append(proceso)
                        break
                    
                    if self.pausado:
                        while self.pausado:
                            time.sleep(0.5)
                    
                    proceso.estado = "Ejecutando"
                    self.root.after(0, lambda p=proceso: self.mostrar_proceso_ejecucion(p))
                    time.sleep(1)
                    proceso.tiempo_restante -= 1
                    proceso.tiempo_transcurrido += 1
                    self.contador_global += 1
                    self.root.after(0, self.actualizar_contador_global)
                
                if proceso.tiempo_restante == 0 and proceso.estado not in ("Error", "Interrumpido"):
                    proceso.resultado = proceso.calcular_resultado()
                    proceso.estado = "Terminado"
                    self.root.after(0, lambda p=proceso: self.agregar_proceso_terminado(p))
            
            lote[:] = [p for p in lote if p.estado not in ("Terminado", "Error")]
            if lote:
                self.lotes.insert(0, lote)
                self.actualizar_lotes_pendientes()
        
        self.root.after(0, self.simulacion_completada)

    def interrumpir_actual(self):
        self.interrumpido = True

    def error_en_actual(self):
        self.error_actual = True

    def pausar_simulacion(self):
        self.pausado = True

    def continuar_simulacion(self):
        self.pausado = False

    def mostrar_lote_actual(self, lote):
        for w in self.lote_frame.winfo_children():
            w.destroy()
        
        header = tk.Label(self.lote_frame, text="ID | TME | Restante",
                         bg=self.colors['bg_light'], fg=self.colors['accent_blue'],
                         font=('Segoe UI', 10, 'bold'), pady=8)
        header.pack(fill='x', pady=(0, 5))
        
        for p in lote:
            proceso_card = tk.Frame(self.lote_frame, bg=self.colors['bg_light'],
                                   highlightbackground=self.colors['accent_blue'],
                                   highlightthickness=1)
            proceso_card.pack(fill='x', pady=3)
            
            texto = f"  🔹 ID: {p.id}  •  TME: {p.tiempo_max}s  •  Restante: {p.tiempo_restante}s"
            tk.Label(proceso_card, text=texto, bg=self.colors['bg_light'],
                    fg=self.colors['text_white'], font=('Consolas', 9),
                    anchor='w').pack(fill='x', padx=10, pady=8)

    def mostrar_proceso_ejecucion(self, proceso):
        for w in self.proceso_frame.winfo_children():
            w.destroy()
        
        datos = [
            (f"ID: {proceso.id}", "💼"),
            (f"Operación: {proceso.dato1} {proceso.operacion} {proceso.dato2}", "🔢"),
            (f"Tiempo Transcurrido: {proceso.tiempo_transcurrido}s", "⏱️"),
            (f"Tiempo Restante: {proceso.tiempo_restante}s", "⏳"),
            (f"Tiempo Máximo: {proceso.tiempo_max}s", "⏰"),
            (f"Estado: {proceso.estado}", "🔄")
        ]
        
        for texto, emoji in datos:
            info_frame = tk.Frame(self.proceso_frame, bg=self.colors['bg_light'])
            info_frame.pack(fill='x', pady=3)
            
            tk.Label(info_frame, text=f"{emoji} {texto}",
                    bg=self.colors['bg_light'], fg=self.colors['text_white'],
                    font=('Segoe UI', 10), anchor='w').pack(padx=10, pady=5)

    def agregar_proceso_terminado(self, proceso):
        # Colores según resultado
        if proceso.resultado == "ERROR":
            tag = 'error'
        else:
            tag = 'success'
        
        self.tree_terminados.insert("", "end",
            values=(proceso.id, proceso.operacion,
                    f"{proceso.dato1} {proceso.operacion} {proceso.dato2}",
                    proceso.resultado), tags=(tag,))
        
        self.tree_terminados.tag_configure('error',
                                          background=self.colors['accent_red'],
                                          foreground='white')
        self.tree_terminados.tag_configure('success',
                                          background=self.colors['bg_light'],
                                          foreground=self.colors['text_white'])

    def actualizar_contador_global(self):
        self.lbl_contador_global.config(text=str(self.contador_global))

    def actualizar_lotes_pendientes(self):
        self.lbl_lotes_pendientes.config(text=str(len(self.lotes)))

    def simulacion_completada(self):
        self.simulacion_activa = False
        messagebox.showinfo("✅ Simulación Completada", 
                          "Todos los lotes han terminado su ejecución.")
        self.actualizar_lotes_pendientes()

def main():
    root = tk.Tk()
    app = SimuladorLotes(root)
    root.mainloop()

if __name__ == "__main__":
    main()
