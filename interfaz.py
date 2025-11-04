
import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial
import json
import os
from datetime import datetime

try:
    import ttkbootstrap as tb
    from ttkbootstrap.style import Style
    TB_AVAILABLE = True
except Exception:
    TB_AVAILABLE = False


from logica import Concesionario, Moto, Cliente


AZUL_OSCURO = "#0A1931"
DORADO = "#F4C430"
BLANCO = "#FFFFFF"
FONDO = "#F7F9FB"


ARCHIVO_RESERVAS = "reservas.json"
ARCHIVO_COMPRAS = "compras.json"
ARCHIVO_COMPARACIONES = "comparaciones.json"
CARPETA_RECIBOS = "recibos"


def cargar_json_si_existe(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_json_lista(path, entry):
    data = cargar_json_si_existe(path)
    data.append(entry)
    guardar_json(path, data)


class InterfazConcesionario:
    def __init__(self, root):
        self.root = root
        self.root.title("Concesionario UDEM")
        self.root.geometry("1150x720")
        self.root.minsize(1000, 660)

        # style
        if TB_AVAILABLE:
            self.style = Style(theme="flatly")
        else:
            self.style = ttk.Style()
            try:
                self.style.theme_use("clam")
            except Exception:
                pass

        self.concesionario = Concesionario("base_datos.json")

        self._cargar_reservas_desde_archivo()
        self._cargar_compras_desde_archivo()

        self.container = tk.Frame(self.root, bg=FONDO)
        self.container.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.container, bg=AZUL_OSCURO, width=240)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = tk.Frame(self.container, bg=FONDO)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.header = tk.Frame(self.main_area, bg=BLANCO, height=100)
        self.header.pack(fill="x", side="top")
        self._build_header()
        self.sep = tk.Frame(self.main_area, bg=DORADO, height=4)
        self.sep.pack(fill="x")

        # content
        self.content = tk.Frame(self.main_area, bg=FONDO)
        self.content.pack(fill="both", expand=True, padx=14, pady=12)

        self._build_sidebar()

        self.pages = {}
        self.current_page = None
        self._create_pages()

        self.show_page("inventario")

    def _cargar_reservas_desde_archivo(self):
        raw = cargar_json_si_existe(ARCHIVO_RESERVAS)
        for r in raw:
            try:
                cli = r.get("cliente", {})
                cliente = Cliente(cli.get("nombre",""), cli.get("cedula",""), cli.get("telefono",""), cli.get("correo",""))
                moto = self.concesionario.repo.get_by_id(int(r.get("moto_id")))
                dia = r.get("dia","")
                if not any((c.cedula==cliente.cedula and m.id==moto.id and d==dia) for c,m,d in self.concesionario.pruebas.reservas):
                    self.concesionario.pruebas.reservas.append((cliente, moto, dia))
                    if dia.capitalize() in self.concesionario.pruebas.disponibilidad:
                        self.concesionario.pruebas.disponibilidad[dia.capitalize()] = False
            except Exception:
                continue

    def _cargar_compras_desde_archivo(self):
        raw = cargar_json_si_existe(ARCHIVO_COMPRAS)
        for c in raw:
            try:
                cli = c.get("cliente", {})
                cliente = Cliente(cli.get("nombre",""), cli.get("cedula",""), cli.get("telefono",""), cli.get("correo",""))
                moto = self.concesionario.repo.get_by_id(int(c.get("moto_id")))
                metodo = c.get("metodo","")
                if not any((cl.cedula==cliente.cedula and m.id==moto.id and me==metodo) for cl,m,me in self.concesionario.compras.compras):
                    self.concesionario.compras.compras.append((cliente, moto, metodo))
            except Exception:
                continue

    def _build_header(self):
        frame = tk.Frame(self.header, bg=BLANCO)
        frame.pack(fill="both", expand=True, padx=16)
        emoji = tk.Label(frame, text="🏍️", font=("Segoe UI Emoji", 34), bg=BLANCO)
        emoji.pack(side="left", padx=(6,10), pady=12)
        title = tk.Label(frame, text="Concesionario UDEM", font=("Segoe UI", 24, "bold"),
                         fg=AZUL_OSCURO, bg=BLANCO)
        title.pack(side="left", pady=12)
        subtitle = tk.Label(frame, text="Gestión de inventario, reservas y ventas", font=("Segoe UI", 10),
                            fg="#333333", bg=BLANCO)
        subtitle.pack(side="left", padx=(12,0), pady=36)

    def _build_sidebar(self):
        top_logo = tk.Label(self.sidebar, text="UDEM", font=("Segoe UI", 20, "bold"),
                            fg=BLANCO, bg=AZUL_OSCURO)
        top_logo.pack(pady=(18, 4))

        botones = [
            ("Ver todas las motos", partial(self.show_page, "inventario")),
            ("Agregar moto", partial(self.show_page, "agregar_moto")),
            ("Reservar test drive", partial(self.show_page, "reservar_prueba")),
            ("Ver reservas", partial(self.show_page, "ver_reservas")),
            ("Comprar moto", partial(self.show_page, "comprar_moto")),
            ("Ver compras", partial(self.show_page, "ver_compras")),  # <-- nuevo botón
            ("Comparar motos", partial(self.show_page, "comparar_motos")),
        ]
        for texto, cmd in botones:
            b = tk.Button(self.sidebar, text=texto, command=cmd,
                          font=("Segoe UI", 11, "bold"),
                          fg=AZUL_OSCURO, bg=BLANCO, activebackground=DORADO,
                          relief="flat", bd=0, padx=12, pady=10)
            b.pack(fill="x", padx=14, pady=8)

        spacer = tk.Frame(self.sidebar, bg=AZUL_OSCURO)
        spacer.pack(expand=True, fill="both")

        footer = tk.Label(self.sidebar, text="v1.0 • Concesionario UDEM", bg=AZUL_OSCURO, fg="#C7D2E0",
                          font=("Segoe UI", 9))
        footer.pack(pady=12)

    def _create_pages(self):

        frame_inv = tk.Frame(self.content, bg=FONDO)
        hdr = tk.Label(frame_inv, text="Inventario de motos", font=("Segoe UI", 16, "bold"), bg=FONDO)
        hdr.pack(pady=8)

        cols = ("id","nombre","marca","motor","potencia","precio","peso","tipo")
        self.tree_inv = ttk.Treeview(frame_inv, columns=cols, show="headings", height=18, selectmode="extended")
        for c in cols:
            self.tree_inv.heading(c, text=c.capitalize())
            self.tree_inv.column(c, anchor="center", width=110)
        self.tree_inv.column("nombre", width=180)
        self.tree_inv.pack(fill="both", expand=True, padx=12, pady=8)

        btns = tk.Frame(frame_inv, bg=FONDO)
        btns.pack(fill="x", padx=12, pady=6)
        ttk.Button(btns, text="Recargar inventario", command=self._load_motos).pack(side="left", padx=6)
        ttk.Button(btns, text="Comparar selección (2)", command=self._compare_selection).pack(side="left", padx=6)
        ttk.Button(btns, text="Eliminar seleccionada", command=self._delete_selected).pack(side="left", padx=6)

        self.pages["inventario"] = frame_inv

        frame_add = tk.Frame(self.content, bg=FONDO)
        lbl = tk.Label(frame_add, text="Agregar nueva moto", font=("Segoe UI", 14, "bold"), bg=FONDO)
        lbl.pack(pady=8)
        form = tk.Frame(frame_add, bg=FONDO)
        form.pack(pady=6, padx=6, fill="x")

        self.add_entries = {}
        fields = [("id","ID (opcional)"),("nombre","Nombre"),("marca","Marca"),("motor","Motor"),
                  ("potencia","Potencia"),("precio","Precio"),("peso","Peso (kg)"),("tipo","Tipo")]
        for key, label in fields:
            row = tk.Frame(form, bg=FONDO)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=FONDO, font=("Segoe UI", 10)).pack(side="left", padx=6)
            ent = ttk.Entry(row)
            ent.pack(side="left", fill="x", expand=True, padx=6)
            self.add_entries[key] = ent

        def guardar_moto():
            try:
                data = {k: self.add_entries[k].get().strip() for k,_ in fields}
                data["id"] = int(data["id"]) if data["id"] else None
                data["precio"] = int(data["precio"]) if data["precio"] else 0
                data["peso"] = int(data["peso"]) if data["peso"] else 0
                nueva = Moto(
                    id=data["id"] or 0,
                    nombre=data["nombre"],
                    marca=data["marca"],
                    precio=data["precio"],
                    motor=data["motor"],
                    potencia=data["potencia"],
                    peso=data["peso"],
                    tipo=data["tipo"] or "Urbana"
                )
                self.concesionario.repo.add(nueva)
                messagebox.showinfo("Éxito", "Moto agregada correctamente.")
                self._clear_add_form()
                self._load_motos()
                self.show_page("inventario")
            except Exception as e:
                messagebox.showerror("Error al agregar", str(e))

        ttk.Button(frame_add, text="Guardar moto", command=guardar_moto).pack(pady=10)
        self.pages["agregar_moto"] = frame_add

        frame_res = tk.Frame(self.content, bg=FONDO)
        tk.Label(frame_res, text="Reservar Test Drive", font=("Segoe UI", 14, "bold"), bg=FONDO).pack(pady=8)
        formr = tk.Frame(frame_res, bg=FONDO)
        formr.pack(pady=6, padx=6, fill="x")

        tk.Label(formr, text="ID de la moto:", bg=FONDO).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.id_m_entry = ttk.Entry(formr); self.id_m_entry.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formr, text="Día (Lunes-Viernes):", bg=FONDO).grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.dia_entry = ttk.Entry(formr); self.dia_entry.grid(row=1, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formr, text="Nombre cliente:", bg=FONDO).grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.nom_entry = ttk.Entry(formr); self.nom_entry.grid(row=2, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formr, text="Cédula:", bg=FONDO).grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.ced_entry = ttk.Entry(formr); self.ced_entry.grid(row=3, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formr, text="Teléfono:", bg=FONDO).grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.tel_entry = ttk.Entry(formr); self.tel_entry.grid(row=4, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formr, text="Correo:", bg=FONDO).grid(row=5, column=0, sticky="w", padx=6, pady=4)
        self.correo_entry = ttk.Entry(formr); self.correo_entry.grid(row=5, column=1, padx=6, pady=4, sticky="ew")

        formr.columnconfigure(1, weight=1)

        def reservar_prueba_gui():
            try:
                moto_id = int(self.id_m_entry.get())
                moto = self.concesionario.repo.get_by_id(moto_id)
                cliente = Cliente(self.nom_entry.get().strip(), self.ced_entry.get().strip(), self.tel_entry.get().strip(), self.correo_entry.get().strip())
                dia = self.dia_entry.get().strip()
                self.concesionario.pruebas.reservar_prueba(dia, cliente, moto)
                reserva_entry = {"cliente": {"nombre": cliente.nombre, "cedula": cliente.cedula, "telefono": cliente.telefono, "correo": cliente.correo},
                                 "moto_id": moto.id, "dia": dia}
                append_json_lista(ARCHIVO_RESERVAS, reserva_entry)
                messagebox.showinfo("Reservado", f"Prueba reservada para {cliente.nombre} el {dia}.")
                self._clear_reserva_form()
                self.show_page("ver_reservas")
            except Exception as e:
                messagebox.showerror("Error reserva", str(e))

        ttk.Button(frame_res, text="Reservar", command=reservar_prueba_gui).pack(pady=8)
        self.pages["reservar_prueba"] = frame_res

        frame_vr = tk.Frame(self.content, bg=FONDO)
        tk.Label(frame_vr, text="Reservas de Test Drive", font=("Segoe UI", 14, "bold"), bg=FONDO).pack(pady=8)
        self.list_reservas = tk.Listbox(frame_vr, height=14)
        self.list_reservas.pack(fill="both", expand=True, padx=12, pady=8)
        ttk.Button(frame_vr, text="Actualizar reservas", command=self._load_reservas).pack(pady=6)
        self.pages["ver_reservas"] = frame_vr

        frame_compra = tk.Frame(self.content, bg=FONDO)
        tk.Label(frame_compra, text="Comprar Moto", font=("Segoe UI", 14, "bold"), bg=FONDO).pack(pady=8)
        formc = tk.Frame(frame_compra, bg=FONDO)
        formc.pack(pady=6, padx=6, fill="x")

        tk.Label(formc, text="ID de la moto:", bg=FONDO).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.id_comp = ttk.Entry(formc); self.id_comp.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formc, text="Nombre comprador:", bg=FONDO).grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.nom_comp = ttk.Entry(formc); self.nom_comp.grid(row=1, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formc, text="Cédula:", bg=FONDO).grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.ced_comp = ttk.Entry(formc); self.ced_comp.grid(row=2, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formc, text="Teléfono:", bg=FONDO).grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.tel_comp = ttk.Entry(formc); self.tel_comp.grid(row=3, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formc, text="Correo:", bg=FONDO).grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.correo_comp = ttk.Entry(formc); self.correo_comp.grid(row=4, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(formc, text="Método de pago (efectivo/tarjeta/transferencia):", bg=FONDO).grid(row=5, column=0, sticky="w", padx=6, pady=4)
        self.metodo_comp = ttk.Entry(formc); self.metodo_comp.grid(row=5, column=1, padx=6, pady=4, sticky="ew")

        formc.columnconfigure(1, weight=1)

        def comprar_moto_gui():
            try:
                moto_id = int(self.id_comp.get())
                moto = self.concesionario.repo.get_by_id(moto_id)
                cliente = Cliente(self.nom_comp.get().strip(), self.ced_comp.get().strip(), self.tel_comp.get().strip(), self.correo_comp.get().strip())
                metodo = self.metodo_comp.get().strip()
                # registra la compra en la lógica (lista en memoria)
                self.concesionario.compras.realizar_pago(cliente, moto, metodo)

                # registro genérico en compras.json
                compra_entry = {"cliente": {"nombre": cliente.nombre, "cedula": cliente.cedula, "telefono": cliente.telefono, "correo": cliente.correo},
                                "moto_id": moto.id, "metodo": metodo}
                append_json_lista(ARCHIVO_COMPRAS, compra_entry)

                # --- generar recibo individual ---
                try:
                    os.makedirs(CARPETA_RECIBOS, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    recibo = {
                        "fecha": timestamp,
                        "cliente": {"nombre": cliente.nombre, "cedula": cliente.cedula, "telefono": cliente.telefono, "correo": cliente.correo},
                        "moto": {"id": moto.id, "nombre": moto.nombre, "marca": moto.marca, "precio": moto.precio, "motor": moto.motor, "potencia": moto.potencia},
                        "metodo": metodo
                    }
                    recibo_nombre = f"recibo_{cliente.cedula}_{moto.id}_{timestamp}.json"
                    recibo_path = os.path.join(CARPETA_RECIBOS, recibo_nombre)
                    with open(recibo_path, "w", encoding="utf-8") as f:
                        json.dump(recibo, f, ensure_ascii=False, indent=2)
                except Exception as e_rec:
                    # no bloqueamos la compra por un fallo en guardar recibo; mostramos aviso
                    messagebox.showwarning("Aviso recibo", f"La compra se registró pero no se pudo guardar el recibo: {e_rec}")
                # --- fin recibo ---

                messagebox.showinfo("Compra", "Compra registrada correctamente.")
                self._clear_compra_form()
                self.show_page("inventario")
                self._load_motos()
            except Exception as e:
                messagebox.showerror("Error compra", str(e))

        ttk.Button(frame_compra, text="Pagar / Registrar compra", command=comprar_moto_gui).pack(pady=8)
        self.pages["comprar_moto"] = frame_compra

        # COMPARAR MOTOS
        frame_cmp = tk.Frame(self.content, bg=FONDO)
        tk.Label(frame_cmp, text="Comparar motos (selecciona 2 desde Inventario)", font=("Segoe UI", 14, "bold"), bg=FONDO).pack(pady=8)
        self.compare_box = tk.Text(frame_cmp, height=20, wrap="word", state="disabled", font=("Consolas", 10))
        self.compare_box.pack(fill="both", expand=True, padx=12, pady=8)
        ttk.Button(frame_cmp, text="Usar selección en Inventario", command=self._compare_selection).pack(pady=6)
        self.pages["comparar_motos"] = frame_cmp

        # VER COMPRAS (nueva página)
        frame_vc = tk.Frame(self.content, bg=FONDO)
        tk.Label(frame_vc, text="Historial de Compras", font=("Segoe UI", 14, "bold"), bg=FONDO).pack(pady=8)
        self.list_compras = tk.Listbox(frame_vc, height=14)
        self.list_compras.pack(fill="both", expand=True, padx=12, pady=8)
        ttk.Button(frame_vc, text="Actualizar compras", command=self._load_compras).pack(pady=6)
        # botón para abrir carpeta de recibos (opcional, sólo si el sistema lo permite)
        def abrir_carpeta_recibos():
            try:
                path = os.path.abspath(CARPETA_RECIBOS)
                if not os.path.exists(path):
                    messagebox.showinfo("Recibos", "Aún no hay recibos guardados.")
                    return
                # intenta abrir el explorador de archivos (funciona en Windows/Mac/Linux en la mayoría de setups)
                if os.name == 'nt':
                    os.startfile(path)
                elif os.uname().sysname == 'Darwin':
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
            except Exception:
                messagebox.showinfo("Recibos", f"Los recibos están en la carpeta: {os.path.abspath(CARPETA_RECIBOS)}")

        ttk.Button(frame_vc, text="Abrir carpeta de recibos", command=abrir_carpeta_recibos).pack(pady=4)
        self.pages["ver_compras"] = frame_vc

    # ---------------- mostrar página ---



    def show_page(self, name: str):
        if self.current_page:
            self.current_page.pack_forget()
        page = self.pages.get(name)
        if page:
            page.pack(fill="both", expand=True)
            self.current_page = page
            if name == "inventario":
                self._load_motos()
            elif name == "ver_reservas":
                self._load_reservas()
            elif name == "comparar_motos":
                self.compare_box.configure(state="normal")
                self.compare_box.delete("1.0", tk.END)
                self.compare_box.insert(tk.END, "Selecciona 2 motos en Inventario y presiona 'Usar selección en Inventario' o usa el botón 'Comparar selección (2)'.")
                self.compare_box.configure(state="disabled")
            elif name == "ver_compras":
                self._load_compras()

    # ---------------- helpers ----------------
    def _clear_add_form(self):
        for e in self.add_entries.values():
            e.delete(0, tk.END)

    def _clear_reserva_form(self):
        self.id_m_entry.delete(0, tk.END)
        self.dia_entry.delete(0, tk.END)
        self.nom_entry.delete(0, tk.END)
        self.ced_entry.delete(0, tk.END)
        self.tel_entry.delete(0, tk.END)
        self.correo_entry.delete(0, tk.END)

    def _clear_compra_form(self):
        self.id_comp.delete(0, tk.END)
        self.nom_comp.delete(0, tk.END)
        self.ced_comp.delete(0, tk.END)
        self.tel_comp.delete(0, tk.END)
        self.correo_comp.delete(0, tk.END)
        self.metodo_comp.delete(0, tk.END)

    # ---------------- cargas / acciones ----------------
    def _load_motos(self):
        try:
            self.concesionario.repo.load()
            for r in self.tree_inv.get_children():
                self.tree_inv.delete(r)
            for m in self.concesionario.repo.list_all():
                self.tree_inv.insert("", "end", iid=str(m.id), values=(m.id, m.nombre, m.marca, m.motor, m.potencia, f"{m.precio:,}", m.peso, m.tipo))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_reservas(self):
        try:
            self.list_reservas.delete(0, tk.END)
            reservas = self.concesionario.pruebas.reservas
            if not reservas:
                self.list_reservas.insert(tk.END, "No hay reservas.")
            else:
                for cliente, moto, dia in reservas:
                    self.list_reservas.insert(tk.END, f"{cliente.nombre} -> {moto.nombre} el {dia}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_compras(self):
        try:
            self.list_compras.delete(0, tk.END)
            compras = self.concesionario.compras.compras
            if not compras:
                self.list_compras.insert(tk.END, "No hay compras registradas.")
            else:
                for cliente, moto, metodo in compras:
                    self.list_compras.insert(tk.END, f"{cliente.nombre} compró {moto.nombre} ({moto.marca}) con {metodo}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_selected(self):
        try:
            sel = self.tree_inv.selection()
            if not sel:
                messagebox.showwarning("Selecciona", "Selecciona una moto a eliminar.")
                return
            moto_id = int(sel[0])
            confirm = messagebox.askyesno("Confirmar", "¿Eliminar la moto seleccionada?")
            if not confirm:
                return
            self.concesionario.repo.delete(moto_id)
            self._load_motos()
            messagebox.showinfo("Eliminado", "Moto eliminada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _compare_selection(self):
        """
        Función corregida: no depende de compare_motos_structured.
        Abre un popup que muestra las especificaciones de cada moto lado a lado
        (sin ID). También guarda un registro sencillo en comparaciones.json.
        """
        try:
            sel = self.tree_inv.selection()
            if len(sel) != 2:
                messagebox.showwarning("Selecciona 2", "Selecciona exactamente 2 motos en Inventario para comparar.")
                return
            id1, id2 = int(sel[0]), int(sel[1])
            m1 = self.concesionario.repo.get_by_id(id1)
            m2 = self.concesionario.repo.get_by_id(id2)

            # Crear reporte simple para guardar
            report = {
                "m1": {"id": m1.id, "nombre": m1.nombre},
                "m2": {"id": m2.id, "nombre": m2.nombre},
                "attributes": {
                    "nombre": {"m1": m1.nombre, "m2": m2.nombre},
                    "marca": {"m1": m1.marca, "m2": m2.marca},
                    "precio": {"m1": m1.precio, "m2": m2.precio},
                    "motor": {"m1": m1.motor, "m2": m2.motor},
                    "potencia": {"m1": m1.potencia, "m2": m2.potencia},
                    "peso": {"m1": m1.peso, "m2": m2.peso},
                    "tipo": {"m1": m1.tipo, "m2": m2.tipo},
                }
            }
            try:
                append_json_lista(ARCHIVO_COMPARACIONES, report)
            except Exception:
                # no crítico; seguir sin bloquear la UI
                pass

            # Popup con la comparación lado a lado
            popup = tk.Toplevel(self.root)
            popup.title(f"Comparación: {m1.nombre}  VS  {m2.nombre}")
            popup.configure(bg=BLANCO)
            popup.geometry("900x420")
            popup.minsize(760, 380)

            # Header del popup
            header = tk.Frame(popup, bg=AZUL_OSCURO, height=60)
            header.pack(fill="x")
            tk.Label(header, text="Comparativa de motos", font=("Segoe UI", 14, "bold"), bg=AZUL_OSCURO, fg=BLANCO).pack(side="left", padx=12, pady=10)
            tk.Label(header, text=f"{m1.nombre}  🆚  {m2.nombre}", font=("Segoe UI", 11), bg=AZUL_OSCURO, fg=BLANCO).pack(side="right", padx=12)

            body = tk.Frame(popup, bg=BLANCO)
            body.pack(fill="both", expand=True, padx=12, pady=12)

            # Columnas: etiquetas centrales, luego m1 y m2
            left = tk.Frame(body, bg=BLANCO)
            left.grid(row=0, column=0, sticky="nsew", padx=(0,8))
            center = tk.Frame(body, bg=BLANCO)
            center.grid(row=0, column=1, sticky="nsew", padx=8)
            right = tk.Frame(body, bg=BLANCO)
            right.grid(row=0, column=2, sticky="nsew", padx=(8,0))

            body.columnconfigure(0, weight=1)
            body.columnconfigure(1, weight=1)
            body.columnconfigure(2, weight=1)

            # Encabezados de columnas
            tk.Label(left, text=m1.nombre, font=("Segoe UI", 12, "bold"), bg=BLANCO, fg=AZUL_OSCURO).pack(pady=6)
            tk.Label(center, text="ESPECIFICACIÓN", font=("Segoe UI", 11, "bold"), bg=BLANCO, fg="#333333").pack(pady=6)
            tk.Label(right, text=m2.nombre, font=("Segoe UI", 12, "bold"), bg=BLANCO, fg=AZUL_OSCURO).pack(pady=6)

            specs = [
                ("Marca", m1.marca, m2.marca),
                ("Precio", f"${m1.precio:,}", f"${m2.precio:,}"),
                ("Motor", m1.motor, m2.motor),
                ("Potencia", m1.potencia, m2.potencia),
                ("Peso (kg)", str(m1.peso), str(m2.peso)),
                ("Tipo", m1.tipo, m2.tipo),
            ]

            # Mostrar cada fila
            for spec_label, left_val, right_val in specs:
                row_frame_left = tk.Frame(left, bg=BLANCO)
                row_frame_left.pack(fill="x", pady=6)
                tk.Label(row_frame_left, text=left_val, font=("Segoe UI", 10), bg=BLANCO, fg="#111827").pack(anchor="center")

                row_frame_center = tk.Frame(center, bg=BLANCO)
                row_frame_center.pack(fill="x", pady=6)
                tk.Label(row_frame_center, text=spec_label, font=("Segoe UI", 10, "bold"), bg=BLANCO, fg="#374151").pack()

                row_frame_right = tk.Frame(right, bg=BLANCO)
                row_frame_right.pack(fill="x", pady=6)
                tk.Label(row_frame_right, text=right_val, font=("Segoe UI", 10), bg=BLANCO, fg="#111827").pack(anchor="center")

            # Footer con botón cerrar
            footer = tk.Frame(popup, bg=BLANCO)
            footer.pack(fill="x", pady=(8,12))
            tk.Button(footer, text="Cerrar", command=popup.destroy, bg=AZUL_OSCURO, fg=BLANCO, padx=12, pady=6).pack(side="right", padx=12)

            # Llevar foco al popup
            popup.transient(self.root)
            popup.grab_set()
            self.root.wait_window(popup)

        except Exception as e:
            messagebox.showerror("Error al comparar", str(e))

# ---------------- ejecución ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazConcesionario(root)
    root.mainloop()