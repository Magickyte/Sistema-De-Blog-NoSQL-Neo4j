import customtkinter as ctk
from tkinter import messagebox
from database import DatabaseManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppBlog(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        
        self.title("Sistema de Blog - Publicaciones, Categorías y Etiquetas")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)

        self.current_user_id = None
        self.current_user_name = ""
        self.current_user_role = "USER"

        self.dict_categories = {}
        self.dict_tags = {}
        self.cat_filter_dict = {"Todas las categorías": None}

        self.minsize(720, 580)
        self.centrar_ventana(860, 700)
        self.pantalla_login()

    def centrar_ventana(self, ancho, alto):
        self.update_idletasks()
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()

        ancho = min(ancho, max(640, pantalla_ancho - 80))
        alto = min(alto, max(540, pantalla_alto - 100))

        pos_x = max(0, (pantalla_ancho - ancho) // 2)
        pos_y = max(0, (pantalla_alto - alto) // 2)

        self.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

    def al_cerrar(self):
        self.db.cerrar()
        self.destroy()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    # -------------------------------------------------------------
    # PANTALLA: LOGIN
    # -------------------------------------------------------------
    def pantalla_login(self):
        self.limpiar_pantalla()

        frame = ctk.CTkFrame(self, width=380, height=350, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(frame, text="Acceso al Blog", font=("Roboto", 22, "bold"))
        title.pack(pady=(35, 20))

        self.ent_email = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", width=280)
        self.ent_email.pack(pady=10)

        self.ent_password = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=280)
        self.ent_password.pack(pady=10)
        self.ent_password.bind("<Return>", lambda e: self.procesar_login())

        btn_ingresar = ctk.CTkButton(frame, text="Ingresar", width=280, command=self.procesar_login)
        btn_ingresar.pack(pady=(20, 10))

    def procesar_login(self):
        email = self.ent_email.get().strip()
        password = self.ent_password.get().strip()

        if not email or not password:
            messagebox.showwarning("Atención", "Ingresa correo y contraseña.")
            return

        try:
            record = self.db.obtener_usuario_por_email(email)
            if not record:
                messagebox.showerror("Acceso Denegado", "Usuario no registrado.")
                return

            if record["password"] != password:
                messagebox.showerror("Acceso Denegado", "Contraseña incorrecta.")
                return

            self.current_user_id = int(record["user_id"])
            self.current_user_name = str(record["name"])
            self.current_user_role = str(record["role"])
            self.pantalla_principal()

        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {e}")

    # -------------------------------------------------------------
    # PANTALLA PRINCIPAL
    # -------------------------------------------------------------
    def pantalla_principal(self):
        self.limpiar_pantalla()

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Barra Superior
        frame_top = ctk.CTkFrame(self, height=50, corner_radius=0)
        frame_top.grid(row=0, column=0, sticky="ew")

        badge_color = "#4CAF50" if self.current_user_role == "ADMIN" else "#2196F3"
        lbl_user = ctk.CTkLabel(
            frame_top,
            text=f"Usuario: {self.current_user_name} [{self.current_user_role}]",
            font=("Roboto", 14, "bold"),
            text_color=badge_color
        )
        lbl_user.pack(side="left", padx=20, pady=10)

        btn_logout = ctk.CTkButton(
            frame_top, text="Cerrar Sesión", fg_color="#E53935", hover_color="#C62828", width=130,
            command=self.cerrar_sesion
        )
        btn_logout.pack(side="right", padx=20, pady=10)

        # 2. Panel de Pestañas
        tabview = ctk.CTkTabview(self, height=235)
        tabview.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        tab_pub = tabview.add("Publicar Artículo")
        self.ent_titulo = ctk.CTkEntry(tab_pub, placeholder_text="Título de la publicación...")
        self.ent_titulo.pack(fill="x", padx=10, pady=4)

        self.txt_texto = ctk.CTkTextbox(tab_pub, height=50)
        self.txt_texto.pack(fill="x", padx=10, pady=4)

        frame_cat_tag = ctk.CTkFrame(tab_pub, fg_color="transparent", height=155)
        frame_cat_tag.pack(fill="x", padx=10, pady=2)
        frame_cat_tag.pack_propagate(False)

        frame_cat = ctk.CTkScrollableFrame(frame_cat_tag, height=100, label_text="Selecciona Categorías:")
        frame_cat.pack(side="left", fill="both", expand=True, padx=(0, 5))

        frame_tag = ctk.CTkScrollableFrame(frame_cat_tag, height=100, label_text="Selecciona Etiquetas / Tags:")
        frame_tag.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.cargar_opciones_cat_tag(frame_cat, frame_tag)

        btn_guardar = ctk.CTkButton(tab_pub, text="Publicar", command=self.guardar_articulo)
        btn_guardar.pack(pady=5)

        if self.current_user_role == "ADMIN":
            tab_user = tabview.add("Gestionar Usuarios")
            tab_categorias_admin = tabview.add("Categorías & Tags")

            for col in range(4):
                tab_user.grid_columnconfigure(col, weight=1)

            self.ent_new_name = ctk.CTkEntry(tab_user, placeholder_text="Nombre completo")
            self.ent_new_name.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

            self.ent_new_email = ctk.CTkEntry(tab_user, placeholder_text="Correo electrónico")
            self.ent_new_email.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            self.ent_new_pass = ctk.CTkEntry(tab_user, placeholder_text="Contraseña", show="*")
            self.ent_new_pass.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

            self.cmb_new_role = ctk.CTkOptionMenu(tab_user, values=["USER", "ADMIN"])
            self.cmb_new_role.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

            btn_crear_u = ctk.CTkButton(tab_user, text="Agregar Usuario", fg_color="#2E7D32", command=self.registrar_nuevo_usuario)
            btn_crear_u.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

            self.cmb_delete_user = ctk.CTkOptionMenu(tab_user, values=["Cargando..."])
            self.cmb_delete_user.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

            btn_del_u = ctk.CTkButton(tab_user, text="Eliminar", fg_color="#D32F2F", command=self.eliminar_usuario)
            btn_del_u.grid(row=2, column=3, padx=5, pady=10, sticky="ew")
            self.cargar_lista_usuarios()

            self.ent_new_cat = ctk.CTkEntry(tab_categorias_admin, placeholder_text="Nueva Categoría...", width=200)
            self.ent_new_cat.pack(pady=5)
            btn_cat = ctk.CTkButton(tab_categorias_admin, text="Agregar Categoría", command=self.agregar_categoria)
            btn_cat.pack(pady=2)

            self.ent_new_tag = ctk.CTkEntry(tab_categorias_admin, placeholder_text="Nuevo Tag...", width=200)
            self.ent_new_tag.pack(pady=5)
            btn_tag = ctk.CTkButton(tab_categorias_admin, text="Agregar Tag", command=self.agregar_tag)
            btn_tag.pack(pady=2)

        # 3. Filtro por Categorías
        frame_filtro = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtro.grid(row=2, column=0, padx=20, pady=(5, 0), sticky="ew")

        ctk.CTkLabel(frame_filtro, text="🔍 Filtrar por Categoría:", font=("Roboto", 12, "bold")).pack(side="left", padx=(0, 10))

        self.cmb_filtro_cat = ctk.CTkOptionMenu(
            frame_filtro,
            values=list(self.cat_filter_dict.keys()),
            command=lambda choice: self.cargar_articulos()
        )
        self.cmb_filtro_cat.pack(side="left")

        # 4. Feed de Publicaciones
        self.area_feed = ctk.CTkScrollableFrame(self)
        self.area_feed.grid(row=3, column=0, padx=20, pady=(10, 15), sticky="nsew")

        self.cargar_articulos()

    # -------------------------------------------------------------
    # MOSTRAR Y FILTRAR PUBLICACIONES
    # -------------------------------------------------------------
    def cargar_articulos(self):
        for widget in self.area_feed.winfo_children():
            widget.destroy()

        cat_seleccionada = self.cmb_filtro_cat.get() if hasattr(self, 'cmb_filtro_cat') else "Todas las categorías"
        cat_id_filtro = self.cat_filter_dict.get(cat_seleccionada, None)

        try:
            articles = self.db.obtener_articulos()
            comments_rows = self.db.obtener_comentarios()

            comments_by_article = {}
            for r in comments_rows:
                comments_by_article.setdefault(r["article_id"], []).append(
                    (r["comment_id"], r["text"], r["comment_date"], r["author"])
                )

            for r in articles:
                art_id = r["article_id"]
                cats = r["categories"]
                tags = r["tags"]

                if cat_id_filtro is not None and cat_seleccionada not in cats:
                    continue

                card = ctk.CTkFrame(self.area_feed, corner_radius=8)
                card.pack(fill="x", pady=8, padx=5)

                header = ctk.CTkLabel(
                    card, text=f"📌 {r['title']} | Por: {r['author']} ({r['art_date']})",
                    font=("Roboto", 13, "bold")
                )
                header.pack(anchor="w", padx=10, pady=(8, 2))

                body = ctk.CTkLabel(card, text=str(r["text"]), wraplength=650, justify="left", font=("Roboto", 11))
                body.pack(anchor="w", padx=10, pady=(2, 5))

                frame_etiquetas_post = ctk.CTkFrame(card, fg_color="transparent")
                frame_etiquetas_post.pack(anchor="w", padx=10, pady=(0, 5))

                str_cats = "📁 " + ", ".join(cats) if cats else "📁 Sin Categoría"
                lbl_categorias_post = ctk.CTkLabel(
                    frame_etiquetas_post, text=str_cats, font=("Roboto", 10, "italic"), text_color="#64B5F6"
                )
                lbl_categorias_post.pack(side="left", padx=(0, 15))

                str_tags = "🏷️ " + " ".join([f"#{t}" for t in tags]) if tags else "🏷️ Sin Tags"
                lbl_tags_post = ctk.CTkLabel(
                    frame_etiquetas_post, text=str_tags, font=("Roboto", 10, "bold"), text_color="#FFB74D"
                )
                lbl_tags_post.pack(side="left")

                if self.current_user_role == "ADMIN":
                    btn_borrar_art = ctk.CTkButton(
                        card, text="Eliminar Post", fg_color="#D32F2F", height=22, width=90,
                        command=lambda id_art=art_id: self.eliminar_articulo(id_art)
                    )
                    btn_borrar_art.pack(anchor="e", padx=10, pady=2)

                art_comments = comments_by_article.get(art_id, [])
                if art_comments:
                    frame_comentarios = ctk.CTkFrame(card, fg_color="#1E1E1E")
                    frame_comentarios.pack(fill="x", padx=10, pady=5)

                    for comm_id, c_text, c_date, c_author in art_comments:
                        c_box = ctk.CTkFrame(frame_comentarios, fg_color="transparent")
                        c_box.pack(fill="x", pady=2)

                        lbl_c = ctk.CTkLabel(
                            c_box, text=f"💬 {c_author} ({c_date}): {c_text}",
                            font=("Roboto", 10), wraplength=500, justify="left"
                        )
                        lbl_c.pack(side="left", padx=5)

                        if self.current_user_role == "ADMIN":
                            btn_del_c = ctk.CTkButton(
                                c_box, text="X", fg_color="#B71C1C", width=20, height=18,
                                command=lambda id_c=comm_id: self.eliminar_comentario(id_c)
                            )
                            btn_del_c.pack(side="right", padx=5)

                f_add_c = ctk.CTkFrame(card, fg_color="transparent")
                f_add_c.pack(fill="x", padx=10, pady=(0, 8))
                ent_c = ctk.CTkEntry(f_add_c, placeholder_text="Escribe un comentario...", height=25)
                ent_c.pack(side="left", fill="x", expand=True, padx=(0, 5))
                btn_c = ctk.CTkButton(
                    f_add_c, text="Comentar", height=25, width=80,
                    command=lambda id_a=art_id, txt=ent_c: self.agregar_comentario(id_a, txt)
                )
                btn_c.pack(side="right")

        except Exception as e:
            print(f"Error cargando artículos: {e}")

    # -------------------------------------------------------------
    # CONTROLADORES DE EVENTOS DE INTERFAZ
    # -------------------------------------------------------------
    def guardar_articulo(self):
        titulo = self.ent_titulo.get().strip()
        texto = self.txt_texto.get("1.0", "end-1c").strip()

        if not titulo or not texto:
            messagebox.showwarning("Atención", "Título y contenido son obligatorios.")
            return

        try:
            cat_ids = [cat_id for chk, cat_id in self.dict_categories.items() if chk.get() == 1]
            tag_ids = [tag_id for chk, tag_id in self.dict_tags.items() if chk.get() == 1]

            self.db.crear_articulo(self.current_user_id, titulo, texto, cat_ids, tag_ids)

            self.ent_titulo.delete(0, "end")
            self.txt_texto.delete("1.0", "end")
            for chk in self.dict_categories:
                chk.deselect()
            for chk in self.dict_tags:
                chk.deselect()

            self.cargar_articulos()
            messagebox.showinfo("Éxito", "Artículo publicado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo publicar: {e}")

    def agregar_comentario(self, article_id, entry_widget):
        texto = entry_widget.get().strip()
        if not texto:
            return
        try:
            self.db.agregar_comentario(self.current_user_id, article_id, texto)
            self.cargar_articulos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar comentario: {e}")

    def registrar_nuevo_usuario(self):
        nombre = self.ent_new_name.get().strip()
        email = self.ent_new_email.get().strip()
        password = self.ent_new_pass.get().strip()
        role = self.cmb_new_role.get()

        if not nombre or not email or not password:
            messagebox.showwarning("Atención", "Campos obligatorios.")
            return

        try:
            exito, msg = self.db.registrar_usuario(nombre, email, password, role)
            if not exito:
                messagebox.showerror("Error", msg)
                return

            self.ent_new_name.delete(0, "end")
            self.ent_new_email.delete(0, "end")
            self.ent_new_pass.delete(0, "end")
            messagebox.showinfo("Éxito", msg)
            self.cargar_lista_usuarios()
        except Exception as e:
            messagebox.showerror("Error", f"{e}")

    def cargar_lista_usuarios(self):
        try:
            res_u = self.db.obtener_todos_los_usuarios()
            self.lista_users_dict = {}
            opciones = []
            for r in res_u:
                u_id = r["user_id"]
                label = f"{u_id} - {r['name']} ({r['role']})"
                opciones.append(label)
                self.lista_users_dict[label] = u_id

            if opciones:
                self.cmb_delete_user.configure(values=opciones)
                self.cmb_delete_user.set(opciones[0])
        except Exception as e:
            print(f"Error cargando usuarios: {e}")

    def eliminar_usuario(self):
        seleccion = self.cmb_delete_user.get()
        if seleccion in self.lista_users_dict:
            u_id = self.lista_users_dict[seleccion]
            if u_id == self.current_user_id:
                messagebox.showwarning("Atención", "No puedes eliminar tu propia cuenta activa.")
                return
            try:
                self.db.eliminar_usuario(u_id)
                messagebox.showinfo("Éxito", "Usuario eliminado.")
                self.cargar_lista_usuarios()
            except Exception as e:
                messagebox.showerror("Error", f"{e}")

    def agregar_categoria(self):
        cat = self.ent_new_cat.get().strip()
        if cat:
            try:
                self.db.agregar_categoria(cat)
                self.pantalla_principal()
            except Exception as e:
                messagebox.showerror("Error", f"{e}")

    def agregar_tag(self):
        tag = self.ent_new_tag.get().strip()
        if tag:
            try:
                self.db.agregar_tag(tag)
                self.pantalla_principal()
            except Exception as e:
                messagebox.showerror("Error", f"{e}")

    def eliminar_articulo(self, article_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta publicación?"):
            try:
                self.db.eliminar_articulo(article_id)
                self.cargar_articulos()
            except Exception as e:
                messagebox.showerror("Error", f"{e}")

    def eliminar_comentario(self, comment_id):
        try:
            self.db.eliminar_comentario(comment_id)
            self.cargar_articulos()
        except Exception as e:
            messagebox.showerror("Error", f"{e}")

    def cargar_opciones_cat_tag(self, frame_cat, frame_tag):
        self.dict_categories.clear()
        self.dict_tags.clear()
        self.cat_filter_dict = {"Todas las categorías": None}

        try:
            for r in self.db.obtener_categorias():
                chk = ctk.CTkCheckBox(frame_cat, text=r["name"])
                chk.pack(anchor="w", padx=5, pady=2)
                self.dict_categories[chk] = r["id"]
                self.cat_filter_dict[r["name"]] = r["id"]

            for r in self.db.obtener_tags():
                chk = ctk.CTkCheckBox(frame_tag, text=r["name"])
                chk.pack(anchor="w", padx=5, pady=2)
                self.dict_tags[chk] = r["id"]
        except Exception as e:
            print(f"Error cargando opciones: {e}")

    def cerrar_sesion(self):
        self.current_user_id = None
        self.current_user_name = ""
        self.current_user_role = "USER"
        self.pantalla_login()


if __name__ == "__main__":
    app = AppBlog()
    app.mainloop()