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
from tkinter import ttk, messagebox, scrolledtext
import random
import threading
import time
import queue

class Proceso:
    def __init__(self, pid, tiempo_maximo, operacion, tiempo_llegada):
        self.pid = pid
        self.tiempo_maximo = tiempo_maximo
        self.tiempo_restante = tiempo_maximo
        self.operacion = operacion
        self.estado = "Nuevo"
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_finalizacion = None
        self.tiempo_respuesta = None
        self.tiempo_espera = 0
        self.tiempo_servicio = 0
        self.tiempo_ejecutado = 0
        self.tiempo_bloqueado = 0
        self.tiempo_restante_bloqueado = 0
        self.resultado = None
        self.error = False
        self.terminado_por = None  # "ERROR" o "NORMAL"
        
    def calcular_resultado(self):
        try:
            self.resultado = eval(self.operacion)
            if isinstance(self.resultado, float):
                self.resultado = round(self.resultado, 2)
        except:
            self.resultado = "ERROR"
            self.error = True

class SimuladorRoundRobin:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulador de Planificación Round-Robin - Actividad 10 SSO")
        self.root.geometry("1400x900")
        
        # Variables de control
        self.procesos = []
        self.proceso_actual = None
        self.reloj = 0
        self.pausado = False
        self.ejecutando = False
        self.contador_pid = 1
        self.max_procesos_memoria = 5
        self.detener = False
        self.tiempo_bloqueado_fijo = 9
        self.quantum = 4  # Valor por defecto
        self.quantum_actual = 0  # Contador de quantum para el proceso actual
        
        # Colas
        self.cola_nuevos = []
        self.cola_listos = []
        self.cola_bloqueados = []
        self.procesos_terminados = []
        
        # Cola de mensajes para comunicación segura entre hilos
        self.cola_mensajes = queue.Queue()
        
        # Ventana de BCP
        self.ventana_bcp = None
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Iniciar el procesamiento de mensajes
        self.procesar_mensajes()
        
    def procesar_mensajes(self):
        """Procesa mensajes de actualización de forma segura en el hilo principal"""
        try:
            while True:
                try:
                    mensaje = self.cola_mensajes.get_nowait()
                    if mensaje == "actualizar":
                        self.actualizar_interfaz()
                    elif mensaje == "resultados":
                        self.calcular_tiempos_finales()
                    elif mensaje == "finalizado":
                        messagebox.showinfo("Simulación Completada", 
                                          f"Todos los {len(self.procesos)} procesos han terminado.\n\n"
                                          f"Tiempo total: {self.reloj} unidades\n\n"
                                          f"Presione 'B' para ver la tabla completa de procesos (BCP)")
                except queue.Empty:
                    break
        except:
            pass
        
        # Programar siguiente verificación
        if not self.detener:
            self.root.after(100, self.procesar_mensajes)
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Simulador de Planificación Round-Robin (RR) - Actividad 10", 
                          font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Controles de entrada
        frame_controles = ttk.LabelFrame(main_frame, text="Configuración Inicial", padding="10")
        frame_controles.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Primera fila de controles
        ttk.Label(frame_controles, text="Número de Procesos:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entry_num_procesos = ttk.Entry(frame_controles, width=10)
        self.entry_num_procesos.grid(row=0, column=1, padx=5)
        self.entry_num_procesos.insert(0, "5")
        
        ttk.Label(frame_controles, text="Quantum:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.entry_quantum = ttk.Entry(frame_controles, width=10)
        self.entry_quantum.grid(row=0, column=3, padx=5)
        self.entry_quantum.insert(0, "4")
        
        ttk.Button(frame_controles, text="Iniciar Simulación", 
                  command=self.iniciar_simulacion).grid(row=0, column=4, padx=20)
        
        # Información de teclas - dividida en dos filas
        info_text1 = "E=Interrupción E/S (bloqueado 9 seg) | W=Error | P=Pausa | C=Continuar"
        ttk.Label(frame_controles, text=info_text1, 
                 font=("Arial", 9, "italic")).grid(row=1, column=0, columnspan=5, pady=(5, 0), sticky=tk.W)
        
        info_text2 = "N=Nuevo Proceso | B=Tabla de Procesos (BCP)"
        ttk.Label(frame_controles, text=info_text2, 
                 font=("Arial", 9, "italic")).grid(row=2, column=0, columnspan=5, pady=(2, 0), sticky=tk.W)
        
        # Frame para información de estado superior
        frame_estado_superior = ttk.Frame(main_frame)
        frame_estado_superior.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_estado_superior.columnconfigure(0, weight=1)
        frame_estado_superior.columnconfigure(1, weight=1)
        frame_estado_superior.columnconfigure(2, weight=1)
        
        # Procesos Nuevos
        frame_nuevos = ttk.LabelFrame(frame_estado_superior, text="Procesos Nuevos", padding="10")
        frame_nuevos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.label_nuevos = ttk.Label(frame_nuevos, text="0 procesos", font=("Arial", 11, "bold"))
        self.label_nuevos.pack()
        
        # Quantum Actual
        frame_quantum = ttk.LabelFrame(frame_estado_superior, text="Quantum Configurado", padding="10")
        frame_quantum.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.label_quantum = ttk.Label(frame_quantum, text="---", font=("Arial", 14, "bold"), foreground="green")
        self.label_quantum.pack()
        
        # Reloj
        frame_reloj = ttk.LabelFrame(frame_estado_superior, text="Reloj Global", padding="10")
        frame_reloj.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.label_reloj = ttk.Label(frame_reloj, text="0", font=("Arial", 18, "bold"), foreground="blue")
        self.label_reloj.pack()
        
        # Proceso en Ejecución (más grande)
        frame_ejecucion = ttk.LabelFrame(main_frame, text="Proceso en Ejecución", padding="10")
        frame_ejecucion.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.label_ejecucion = ttk.Label(frame_ejecucion, text="Ninguno", justify=tk.LEFT, font=("Arial", 10))
        self.label_ejecucion.pack()
        
        # Frame para colas
        frame_colas = ttk.Frame(main_frame)
        frame_colas.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        frame_colas.columnconfigure(0, weight=1)
        frame_colas.columnconfigure(1, weight=1)
        frame_colas.columnconfigure(2, weight=1)
        
        # Cola de Listos (con avance del carrusel)
        frame_listos = ttk.LabelFrame(frame_colas, text="Cola de Listos (Carrusel RR)", padding="5")
        frame_listos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.tree_listos = ttk.Treeview(frame_listos, columns=("PID", "TME", "TR"), show="headings", height=6)
        self.tree_listos.heading("PID", text="ID Proceso")
        self.tree_listos.heading("TME", text="TME")
        self.tree_listos.heading("TR", text="T. Restante")
        self.tree_listos.column("PID", width=80, anchor=tk.CENTER)
        self.tree_listos.column("TME", width=60, anchor=tk.CENTER)
        self.tree_listos.column("TR", width=80, anchor=tk.CENTER)
        self.tree_listos.pack(fill=tk.BOTH, expand=True)
        
        # Cola de Bloqueados
        frame_bloqueados = ttk.LabelFrame(frame_colas, text="Cola de Bloqueados", padding="5")
        frame_bloqueados.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.tree_bloqueados = ttk.Treeview(frame_bloqueados, columns=("PID", "TB"), show="headings", height=6)
        self.tree_bloqueados.heading("PID", text="ID Proceso")
        self.tree_bloqueados.heading("TB", text="Tiempo Transcurrido")
        self.tree_bloqueados.column("PID", width=80, anchor=tk.CENTER)
        self.tree_bloqueados.column("TB", width=120, anchor=tk.CENTER)
        self.tree_bloqueados.pack(fill=tk.BOTH, expand=True)
        
        # Procesos Terminados
        frame_terminados = ttk.LabelFrame(frame_colas, text="Procesos Terminados", padding="5")
        frame_terminados.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.tree_terminados = ttk.Treeview(frame_terminados, columns=("PID", "Op", "Res"), show="headings", height=6)
        self.tree_terminados.heading("PID", text="ID Proceso")
        self.tree_terminados.heading("Op", text="Operación")
        self.tree_terminados.heading("Res", text="Resultado")
        self.tree_terminados.column("PID", width=70, anchor=tk.CENTER)
        self.tree_terminados.column("Op", width=100, anchor=tk.CENTER)
        self.tree_terminados.column("Res", width=100, anchor=tk.CENTER)
        self.tree_terminados.pack(fill=tk.BOTH, expand=True)
        
        # Frame para resultados finales
        frame_resultados = ttk.LabelFrame(main_frame, text="Tabla de Tiempos - Resumen Final", padding="5")
        frame_resultados.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para resultados
        scrollbar_resultados = ttk.Scrollbar(frame_resultados, orient=tk.VERTICAL)
        
        # Treeview para resultados
        self.tree_resultados = ttk.Treeview(frame_resultados, 
                                          columns=("PID", "Llegada", "Finalizacion", "Retorno", 
                                                  "Respuesta", "Espera", "Servicio"), 
                                          show="headings", height=8,
                                          yscrollcommand=scrollbar_resultados.set)
        
        scrollbar_resultados.config(command=self.tree_resultados.yview)
        scrollbar_resultados.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_resultados.heading("PID", text="ID Proceso")
        self.tree_resultados.heading("Llegada", text="T. Llegada")
        self.tree_resultados.heading("Finalizacion", text="T. Finalización")
        self.tree_resultados.heading("Retorno", text="T. Retorno")
        self.tree_resultados.heading("Respuesta", text="T. Respuesta")
        self.tree_resultados.heading("Espera", text="T. Espera")
        self.tree_resultados.heading("Servicio", text="T. Servicio")
        
        self.tree_resultados.column("PID", width=80, anchor=tk.CENTER)
        self.tree_resultados.column("Llegada", width=80, anchor=tk.CENTER)
        self.tree_resultados.column("Finalizacion", width=100, anchor=tk.CENTER)
        self.tree_resultados.column("Retorno", width=80, anchor=tk.CENTER)
        self.tree_resultados.column("Respuesta", width=90, anchor=tk.CENTER)
        self.tree_resultados.column("Espera", width=80, anchor=tk.CENTER)
        self.tree_resultados.column("Servicio", width=80, anchor=tk.CENTER)
        
        self.tree_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar pesos para expansión
        main_frame.rowconfigure(4, weight=2)
        main_frame.rowconfigure(5, weight=1)
        
        # Vincular teclas según el PDF
        self.root.bind('e', lambda e: self.interrupcion_io())
        self.root.bind('E', lambda e: self.interrupcion_io())
        self.root.bind('w', lambda e: self.error_proceso())
        self.root.bind('W', lambda e: self.error_proceso())
        self.root.bind('p', lambda e: self.pausar_simulacion())
        self.root.bind('P', lambda e: self.pausar_simulacion())
        self.root.bind('c', lambda e: self.continuar_simulacion())
        self.root.bind('C', lambda e: self.continuar_simulacion())
        self.root.bind('n', lambda e: self.nuevo_proceso())
        self.root.bind('N', lambda e: self.nuevo_proceso())
        self.root.bind('b', lambda e: self.mostrar_bcp())
        self.root.bind('B', lambda e: self.mostrar_bcp())
        
    def generar_operacion(self):
        operadores = ['+', '-', '*', '/']
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        operador = random.choice(operadores)
        
        if operador == '/' and num2 == 0:
            num2 = 1
            
        return f"{num1} {operador} {num2}"
    
    def crear_procesos(self, num_procesos):
        for _ in range(num_procesos):
            tiempo_maximo = random.randint(7, 18)
            operacion = self.generar_operacion()
            proceso = Proceso(self.contador_pid, tiempo_maximo, operacion, None)
            self.procesos.append(proceso)
            self.cola_nuevos.append(proceso)
            self.contador_pid += 1
            print(f"Proceso {proceso.pid} creado y agregado a cola de nuevos")
    
    def nuevo_proceso(self):
        """Tecla N - Crear nuevo proceso"""
        if self.ejecutando:
            tiempo_maximo = random.randint(7, 18)
            operacion = self.generar_operacion()
            proceso = Proceso(self.contador_pid, tiempo_maximo, operacion, None)
            self.procesos.append(proceso)
            self.cola_nuevos.append(proceso)
            self.contador_pid += 1
            print(f"[T={self.reloj}] NUEVO PROCESO {proceso.pid} creado (Tecla N)")
            self.cola_mensajes.put("actualizar")
    
    def admitir_procesos(self):
        while len(self.cola_listos) < self.max_procesos_memoria and self.cola_nuevos:
            proceso = self.cola_nuevos.pop(0)
            proceso.estado = "Listo"
            proceso.tiempo_llegada = self.reloj
            self.cola_listos.append(proceso)
            print(f"[T={self.reloj}] Proceso {proceso.pid} admitido a cola de listos (Planificador Largo Plazo)")
    
    def siguiente_proceso(self):
        """Obtiene el siguiente proceso de la cola de listos (FIFO para RR)"""
        if self.cola_listos:
            proceso = self.cola_listos.pop(0)
            proceso.estado = "Ejecución"
            
            if proceso.tiempo_respuesta is None:
                proceso.tiempo_respuesta = self.reloj - proceso.tiempo_llegada
            
            # Reiniciar contador de quantum
            self.quantum_actual = 0
                
            return proceso
        return None
    
    def quantum_agotado(self):
        """Verifica si se agotó el quantum del proceso actual"""
        return self.quantum_actual >= self.quantum
    
    def cambio_contexto_quantum(self):
        """Realiza cambio de contexto por quantum agotado"""
        if self.proceso_actual:
            proceso = self.proceso_actual
            proceso.estado = "Listo"
            # Agregar al final de la cola (carrusel)
            self.cola_listos.append(proceso)
            self.proceso_actual = None
            self.quantum_actual = 0
            print(f"[T={self.reloj}] Proceso {proceso.pid} regresa al final de la cola (Quantum agotado - RR)")
    
    def actualizar_interfaz(self):
        try:
            # Actualizar procesos nuevos
            self.label_nuevos.config(text=f"{len(self.cola_nuevos)} procesos")
            
            # Actualizar quantum
            self.label_quantum.config(text=str(self.quantum))
            
            # Actualizar proceso en ejecución
            if self.proceso_actual:
                texto = f"ID: {self.proceso_actual.pid}  |  "
                texto += f"Operación: {self.proceso_actual.operacion}  |  "
                texto += f"TME: {self.proceso_actual.tiempo_maximo}\n"
                texto += f"Tiempo Ejecutado: {self.proceso_actual.tiempo_ejecutado}  |  "
                texto += f"Tiempo Restante: {self.proceso_actual.tiempo_restante}\n"
                texto += f"⏱ Quantum Transcurrido: {self.quantum_actual} / {self.quantum}"
                self.label_ejecucion.config(text=texto)
            else:
                self.label_ejecucion.config(text="Ninguno")
            
            # Actualizar reloj
            self.label_reloj.config(text=str(self.reloj))
            
            # Actualizar cola de listos (mostrar carrusel)
            self.tree_listos.delete(*self.tree_listos.get_children())
            for i, proceso in enumerate(self.cola_listos):
                # Marcar visualmente el orden del carrusel
                tag = "primero" if i == 0 else ""
                self.tree_listos.insert("", "end", values=(
                    f"→ {proceso.pid}" if i == 0 else proceso.pid, 
                    proceso.tiempo_maximo, 
                    proceso.tiempo_restante
                ), tags=(tag,))
            
            # Estilo para el primero en la cola
            self.tree_listos.tag_configure("primero", background="light green")
            
            # Actualizar cola de bloqueados
            self.tree_bloqueados.delete(*self.tree_bloqueados.get_children())
            for proceso in self.cola_bloqueados:
                self.tree_bloqueados.insert("", "end", values=(
                    proceso.pid, 
                    proceso.tiempo_bloqueado
                ))
            
            # Actualizar procesos terminados
            self.tree_terminados.delete(*self.tree_terminados.get_children())
            for proceso in self.procesos_terminados:
                resultado = str(proceso.resultado) if proceso.resultado is not None else "ERROR"
                self.tree_terminados.insert("", "end", values=(
                    proceso.pid, 
                    proceso.operacion, 
                    resultado
                ))
        except Exception as e:
            print(f"Error actualizando interfaz: {e}")
    
    def interrupcion_io(self):
        """Tecla E - Interrupción por E/S"""
        if self.proceso_actual and self.ejecutando:
            proceso = self.proceso_actual
            proceso.estado = "Bloqueado"
            proceso.tiempo_bloqueado = 0
            proceso.tiempo_restante_bloqueado = self.tiempo_bloqueado_fijo
            self.cola_bloqueados.append(proceso)
            self.proceso_actual = None
            self.quantum_actual = 0
            print(f"[T={self.reloj}] Proceso {proceso.pid} bloqueado por E/S (permanecerá {self.tiempo_bloqueado_fijo} unidades)")
            self.cola_mensajes.put("actualizar")
    
    def error_proceso(self):
        """Tecla W - Error en proceso"""
        if self.proceso_actual and self.ejecutando:
            proceso = self.proceso_actual
            proceso.estado = "Terminado"
            proceso.error = True
            proceso.terminado_por = "ERROR"
            proceso.tiempo_finalizacion = self.reloj
            proceso.resultado = "ERROR"
            if proceso.tiempo_respuesta is None:
                proceso.tiempo_respuesta = self.reloj - proceso.tiempo_llegada
            self.procesos_terminados.append(proceso)
            self.proceso_actual = None
            self.quantum_actual = 0
            print(f"[T={self.reloj}] Proceso {proceso.pid} terminado por ERROR (Tecla W)")
            self.admitir_procesos()
            self.cola_mensajes.put("actualizar")
    
    def pausar_simulacion(self):
        """Tecla P - Pausar simulación"""
        if self.ejecutando and not self.pausado:
            self.pausado = True
            print(f"[T={self.reloj}] ⏸ Simulación PAUSADA (Tecla P)")
    
    def continuar_simulacion(self):
        """Tecla C - Continuar simulación"""
        if self.ejecutando and self.pausado:
            self.pausado = False
            print(f"[T={self.reloj}] ▶ Simulación CONTINUADA (Tecla C)")
        # Si se presiona C y hay ventana BCP abierta, cerrarla
        if self.ventana_bcp:
            self.ventana_bcp.destroy()
            self.ventana_bcp = None
    
    def mostrar_bcp(self):
        """Tecla B - Mostrar tabla de procesos (BCP)"""
        # Pausar la simulación
        if self.ejecutando:
            self.pausado = True
            print(f"[T={self.reloj}] Mostrando BCP - Simulación pausada")
        
        # Si ya existe una ventana, cerrarla primero
        if self.ventana_bcp:
            self.ventana_bcp.destroy()
        
        # Crear ventana de BCP
        self.ventana_bcp = tk.Toplevel(self.root)
        self.ventana_bcp.title("Tabla de Procesos (BCP) - Bloque de Control de Procesos")
        self.ventana_bcp.geometry("1200x600")
        
        # Frame principal
        frame = ttk.Frame(self.ventana_bcp, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Bloque de Control de Procesos (BCP) - Round-Robin", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        ttk.Label(frame, text="Presione 'C' para continuar la simulación", 
                 font=("Arial", 10, "italic")).pack(pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        
        # Treeview para BCP
        columns = ("PID", "Estado", "Operacion", "Datos", "TLlegada", "TFin", 
                  "TRetorno", "TEspera", "TServicio", "TRestante", "TRespuesta")
        
        tree_bcp = ttk.Treeview(frame, columns=columns, show="headings", 
                               yscrollcommand=scrollbar.set, height=20)
        
        scrollbar.config(command=tree_bcp.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar columnas
        tree_bcp.heading("PID", text="ID")
        tree_bcp.heading("Estado", text="Estado")
        tree_bcp.heading("Operacion", text="Operación")
        tree_bcp.heading("Datos", text="Resultado")
        tree_bcp.heading("TLlegada", text="T. Llegada")
        tree_bcp.heading("TFin", text="T. Fin")
        tree_bcp.heading("TRetorno", text="T. Retorno")
        tree_bcp.heading("TEspera", text="T. Espera")
        tree_bcp.heading("TServicio", text="T. Servicio")
        tree_bcp.heading("TRestante", text="T. Restante CPU")
        tree_bcp.heading("TRespuesta", text="T. Respuesta")
        
        tree_bcp.column("PID", width=50, anchor=tk.CENTER)
        tree_bcp.column("Estado", width=120, anchor=tk.CENTER)
        tree_bcp.column("Operacion", width=100, anchor=tk.CENTER)
        tree_bcp.column("Datos", width=80, anchor=tk.CENTER)
        tree_bcp.column("TLlegada", width=80, anchor=tk.CENTER)
        tree_bcp.column("TFin", width=80, anchor=tk.CENTER)
        tree_bcp.column("TRetorno", width=80, anchor=tk.CENTER)
        tree_bcp.column("TEspera", width=80, anchor=tk.CENTER)
        tree_bcp.column("TServicio", width=80, anchor=tk.CENTER)
        tree_bcp.column("TRestante", width=100, anchor=tk.CENTER)
        tree_bcp.column("TRespuesta", width=90, anchor=tk.CENTER)
        
        # Llenar datos
        for proceso in self.procesos:
            # Determinar estado
            if proceso.estado == "Nuevo":
                estado = "Nuevo"
            elif proceso.estado == "Terminado":
                estado = f"Terminado ({proceso.terminado_por if proceso.terminado_por else 'NORMAL'})"
            elif proceso.estado == "Bloqueado":
                estado = f"Bloqueado (restante: {proceso.tiempo_restante_bloqueado})"
            else:
                estado = proceso.estado
            
            # Datos según estado
            resultado = "---" if proceso.estado == "Nuevo" else (
                str(proceso.resultado) if proceso.resultado is not None else "---"
            )
            
            llegada = "---" if proceso.tiempo_llegada is None else proceso.tiempo_llegada
            fin = "---" if proceso.tiempo_finalizacion is None else proceso.tiempo_finalizacion
            retorno = "---" if proceso.tiempo_finalizacion is None or proceso.tiempo_llegada is None else (
                proceso.tiempo_finalizacion - proceso.tiempo_llegada
            )
            espera = "---" if proceso.estado == "Nuevo" else proceso.tiempo_espera
            servicio = "---" if proceso.estado == "Nuevo" else proceso.tiempo_servicio
            restante = "---" if proceso.estado == "Terminado" else proceso.tiempo_restante
            respuesta = "---" if proceso.tiempo_respuesta is None else proceso.tiempo_respuesta
            
            tree_bcp.insert("", "end", values=(
                proceso.pid,
                estado,
                proceso.operacion,
                resultado,
                llegada,
                fin,
                retorno,
                espera,
                servicio,
                restante,
                respuesta
            ))
        
        tree_bcp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Botón para cerrar y continuar
        ttk.Button(frame, text="Cerrar y Continuar (C)", 
                  command=self.continuar_simulacion).pack(pady=10)
    
    def cerrar_aplicacion(self):
        self.detener = True
        self.ejecutando = False
        self.pausado = False
        time.sleep(0.2)
        try:
            if self.ventana_bcp:
                self.ventana_bcp.destroy()
        except:
            pass
        try:
            self.root.quit()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass
    
    def terminar_proceso(self, proceso):
        proceso.estado = "Terminado"
        proceso.terminado_por = "NORMAL"
        proceso.tiempo_finalizacion = self.reloj
        if proceso.tiempo_respuesta is None:
            proceso.tiempo_respuesta = self.reloj - proceso.tiempo_llegada
        proceso.calcular_resultado()
        self.procesos_terminados.append(proceso)
        print(f"[T={self.reloj}] Proceso {proceso.pid} terminado NORMALMENTE. Resultado: {proceso.resultado}")
    
    def actualizar_bloqueados(self):
        procesos_a_mover = []
        for proceso in self.cola_bloqueados:
            proceso.tiempo_bloqueado += 1
            proceso.tiempo_restante_bloqueado -= 1
            
            # Cuando llega a 9 unidades de tiempo transcurridas
            if proceso.tiempo_bloqueado >= self.tiempo_bloqueado_fijo:
                procesos_a_mover.append(proceso)
        
        for proceso in procesos_a_mover:
            self.cola_bloqueados.remove(proceso)
            proceso.estado = "Listo"
            proceso.tiempo_restante_bloqueado = 0
            # Agregar al final de la cola de listos
            self.cola_listos.append(proceso)
            print(f"[T={self.reloj}] Proceso {proceso.pid} desbloqueado y movido al final de cola de listos")
    
    def calcular_tiempos_finales(self):
        self.tree_resultados.delete(*self.tree_resultados.get_children())
        
        print(f"\n{'='*70}")
        print(f"TABLA DE RESULTADOS FINALES - Round-Robin")
        print(f"{'='*70}")
        
        for proceso in self.procesos:
            if proceso.tiempo_finalizacion is not None:
                tiempo_retorno = proceso.tiempo_finalizacion - proceso.tiempo_llegada
                tiempo_respuesta = proceso.tiempo_respuesta if proceso.tiempo_respuesta is not None else 0
                tiempo_espera = proceso.tiempo_espera
                tiempo_servicio = proceso.tiempo_servicio
                
                self.tree_resultados.insert("", "end", values=(
                    proceso.pid,
                    proceso.tiempo_llegada,
                    proceso.tiempo_finalizacion,
                    tiempo_retorno,
                    tiempo_respuesta,
                    tiempo_espera,
                    tiempo_servicio
                ))
                
                print(f"PID {proceso.pid}: Llegada={proceso.tiempo_llegada}, "
                      f"Fin={proceso.tiempo_finalizacion}, "
                      f"Retorno={tiempo_retorno}, "
                      f"Respuesta={tiempo_respuesta}, "
                      f"Espera={tiempo_espera}, "
                      f"Servicio={tiempo_servicio}")
        
        print(f"{'='*70}\n")
    
    def iniciar_simulacion(self):
        if self.ejecutando:
            messagebox.showwarning("Advertencia", "La simulación ya está en ejecución")
            return
            
        try:
            num_procesos = int(self.entry_num_procesos.get())
            if num_procesos <= 0:
                messagebox.showerror("Error", "El número de procesos debe ser mayor a 0")
                return
            if num_procesos > 50:
                respuesta = messagebox.askyesno("Advertencia", 
                                               f"Vas a crear {num_procesos} procesos.\n"
                                               "Se recomienda usar menos de 50.\n¿Continuar?")
                if not respuesta:
                    return
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un número válido de procesos")
            return
        
        try:
            quantum = int(self.entry_quantum.get())
            if quantum <= 0:
                messagebox.showerror("Error", "El quantum debe ser mayor a 0")
                return
            self.quantum = quantum
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un valor válido para el quantum")
            return
        
        # Reiniciar estado
        self.reloj = 0
        self.proceso_actual = None
        self.quantum_actual = 0
        self.cola_nuevos = []
        self.cola_listos = []
        self.cola_bloqueados = []
        self.procesos_terminados = []
        self.procesos = []
        self.pausado = False
        self.detener = False
        self.ejecutando = True
        self.contador_pid = 1
        
        # Limpiar cola de mensajes
        while not self.cola_mensajes.empty():
            try:
                self.cola_mensajes.get_nowait()
            except:
                break
        
        # Crear procesos iniciales
        self.crear_procesos(num_procesos)
        
        # Admitir procesos iniciales
        self.admitir_procesos()
        
        # Actualizar interfaz inicial
        self.actualizar_interfaz()
        
        # Iniciar hilo de simulación
        thread = threading.Thread(target=self.ejecutar_simulacion, daemon=True)
        thread.start()
        
        print(f"\n{'='*70}")
        print(f"SIMULACIÓN ROUND-ROBIN INICIADA")
        print(f"Número de procesos: {num_procesos}")
        print(f"Quantum configurado: {self.quantum} unidades")
        print(f"Máximo de procesos en memoria: {self.max_procesos_memoria}")
        print(f"Tiempo de bloqueo por E/S: {self.tiempo_bloqueado_fijo} unidades")
        print(f"{'='*70}\n")
    
    def ejecutar_simulacion(self):
        print("Hilo de simulación Round-Robin iniciado")
        
        while not self.detener and self.ejecutando:
            # Verificar si todos los procesos han terminado
            if len(self.procesos_terminados) >= len(self.procesos):
                break
            
            if self.pausado:
                time.sleep(0.1)
                continue
            
            try:
                # Actualizar procesos bloqueados
                self.actualizar_bloqueados()
                
                # Si no hay proceso en ejecución, tomar el siguiente
                if not self.proceso_actual:
                    self.proceso_actual = self.siguiente_proceso()
                    if self.proceso_actual:
                        print(f"[T={self.reloj}] >>> Proceso {self.proceso_actual.pid} entra al procesador (RR)")
                
                # Ejecutar proceso actual
                if self.proceso_actual:
                    self.proceso_actual.tiempo_ejecutado += 1
                    self.proceso_actual.tiempo_restante -= 1
                    self.proceso_actual.tiempo_servicio += 1
                    self.quantum_actual += 1
                    
                    # Verificar si el proceso ha terminado
                    if self.proceso_actual.tiempo_restante <= 0:
                        self.terminar_proceso(self.proceso_actual)
                        self.proceso_actual = None
                        self.quantum_actual = 0
                        self.admitir_procesos()
                    # Verificar si se agotó el quantum (sin terminar el proceso)
                    elif self.quantum_agotado():
                        print(f"[T={self.reloj}] Quantum agotado para proceso {self.proceso_actual.pid}")
                        self.cambio_contexto_quantum()
                
                # Incrementar tiempo de espera para procesos en cola de listos
                for proceso in self.cola_listos:
                    proceso.tiempo_espera += 1
                
                # Incrementar reloj
                self.reloj += 1
                
                # Enviar mensaje para actualizar interfaz
                if not self.detener:
                    self.cola_mensajes.put("actualizar")
                
                # Pausa para visualización
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error en simulación: {e}")
                import traceback
                traceback.print_exc()
                break
        
        # Simulación terminada
        if not self.detener and self.ejecutando:
            self.ejecutando = False
            self.cola_mensajes.put("resultados")
            self.cola_mensajes.put("finalizado")
            print(f"\n{'='*70}")
            print(f"SIMULACIÓN ROUND-ROBIN COMPLETADA")
            print(f"Tiempo total: {self.reloj} unidades")
            print(f"Total de procesos ejecutados: {len(self.procesos_terminados)}")
            print(f"Quantum utilizado: {self.quantum} unidades")
            print(f"{'='*70}\n")
    
    def run(self):
        self.root.mainloop()

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    try:
        simulador = SimuladorRoundRobin()
        simulador.run()
    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
