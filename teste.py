import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from psycopg2 import Error

# ─────────────────────────── Configurações ───────────────────────────

DB_CONFIG = {
    "dbname": "linkedin",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def conectar_bd():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except Error as e:
        messagebox.showerror("Erro Crítico", f"Falha de conexão: {e}")
        return None

# ─────────────────────────── Helpers ───────────────────────────

def extrair_id(sel):
    try:
        return int(str(sel).split(" - ")[0])
    except (ValueError, IndexError):
        return None

def label_entry(frame, texto, row, width=28, show=""):
    tk.Label(frame, text=texto).grid(row=row, column=0, sticky="e", padx=5, pady=3)
    ent = tk.Entry(frame, width=width, show=show)
    ent.grid(row=row, column=1, pady=3)
    return ent

def label_combo(frame, texto, row, width=26):
    tk.Label(frame, text=texto).grid(row=row, column=0, sticky="e", padx=5, pady=3)
    cb = ttk.Combobox(frame, width=width, state="readonly")
    cb.grid(row=row, column=1, pady=3)
    return cb

def label_text(frame, texto, row, width=22, height=3):
    tk.Label(frame, text=texto).grid(row=row, column=0, sticky="ne", padx=5, pady=3)
    txt = tk.Text(frame, width=width, height=height)
    txt.grid(row=row, column=1, pady=3)
    return txt

def buscar_contas(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT IDConta,
                   COALESCE((SELECT NomPsso||' '||SobnomPsso FROM PESSOAL p WHERE p.IDConta=c.IDConta),
                            (SELECT NomComerc FROM CORPORATIVA cp WHERE cp.IDConta=c.IDConta),
                            c.EmailConta) AS nome
            FROM CONTA c ORDER BY nome;
        """)
        return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

def buscar_corporativas(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT IDConta, NomComerc FROM CORPORATIVA ORDER BY NomComerc;")
        return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

def buscar_competencias(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT IDComp, NomeComp FROM COMPETENCIA ORDER BY NomeComp;")
        return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

def buscar_idiomas(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT IDIdioma, NomeIdioma FROM IDIOMA ORDER BY NomeIdioma;")
        return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

# ════════════════════════════════════════════════════════════════
#  APLICAÇÃO PRINCIPAL — janela única com navegação por frames
# ════════════════════════════════════════════════════════════════

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn DB — Gerenciador")
        self.root.geometry("700x580")
        self.root.resizable(True, True)

        self._conta_crud = ContaCRUD(self)

        # ── Cabeçalho ──
        header = tk.Frame(root, bg="#0a66c2", pady=8)
        header.pack(fill="x")
        tk.Label(header, text="LinkedIn — Gerenciador de Dados",
                 font=("Arial", 14, "bold"), bg="#0a66c2", fg="white").pack(side="left", padx=16)
        tk.Button(header, text="⚙ Conexão", font=("Arial", 9),
                  command=self.tela_configuracao).pack(side="right", padx=12, pady=2)

        # ── Barra de navegação ──
        nav = tk.Frame(root, bg="#e8f0fe", pady=6)
        nav.pack(fill="x")

        self.btn_voltar = tk.Button(nav, text="◀ Voltar", state="disabled",
                                    command=self.voltar_menu, font=("Arial", 9))
        self.btn_voltar.pack(side="left", padx=10)

        self.lbl_caminho = tk.Label(nav, text="Menu Principal",
                                    font=("Arial", 9, "italic"), bg="#e8f0fe", fg="#444")
        self.lbl_caminho.pack(side="left", padx=4)

        # ── Área de conteúdo ──
        self.content = tk.Frame(root)
        self.content.pack(fill="both", expand=True, padx=10, pady=8)

        # Pilha de frames para navegação
        self._stack = []   # (frame, titulo)

        self.mostrar_menu_principal()

    # ── Gerenciamento de telas ──

    def _limpar_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _push(self, titulo, build_fn, *args, **kwargs):
        self._limpar_content()
        frame = tk.Frame(self.content)
        frame.pack(fill="both", expand=True)
        self._stack.append((build_fn, args, kwargs, titulo))
        self.lbl_caminho.config(text=" › ".join(t for _, _, _, t in self._stack))
        self.btn_voltar.config(state="normal" if len(self._stack) > 1 else "disabled")
        build_fn(frame, *args, **kwargs)

    def voltar_menu(self):
        if len(self._stack) > 1:
            self._stack.pop()
            build_fn, args, kwargs, titulo = self._stack[-1]
            self._limpar_content()
            frame = tk.Frame(self.content)
            frame.pack(fill="both", expand=True)
            self.lbl_caminho.config(text=" › ".join(t for _, _, _, t in self._stack))
            self.btn_voltar.config(state="normal" if len(self._stack) > 1 else "disabled")
            build_fn(frame, *args, **kwargs)

    def mostrar_menu_principal(self):
        self._stack = []
        self._push("Menu Principal", self._build_menu_principal)

    def _build_menu_principal(self, frame):
        tk.Label(frame, text="Selecione a entidade e a operação",
                 font=("Arial", 11, "bold")).pack(pady=(10, 6))

        MODULOS = {
            "Conta":                  (ContaCRUD,       ["Criar", "Buscar", "Atualizar", "Deletar"]),
            "Post":                   (PostCRUD,        ["Criar", "Buscar", "Atualizar", "Deletar"]),
            "Comentário":             (ComentarioCRUD,  ["Criar", "Buscar", "Deletar"]),
            "Reagir a Post":          (ReagePostCRUD,   ["Criar", "Buscar", "Deletar"]),
            "Vaga de Emprego":        (VagaCRUD,        ["Criar", "Buscar", "Deletar"]),
            "Aplicação a Vaga":       (AplicaVagaCRUD,  ["Criar", "Buscar"]),
            "Competência":            (CompetenciaCRUD, ["Criar", "Buscar", "Deletar"]),
            "Competência da Conta":   (PossCompCRUD,    ["Criar", "Buscar", "Deletar"]),
            "Comp. de Experiência":   (ExpPossCompCRUD, ["Criar", "Buscar"]),
            "Experiência Prof.":      (ExpProfCRUD,     ["Criar", "Buscar", "Deletar"]),
            "Formação Acadêmica":     (FormacaoCRUD,    ["Criar", "Buscar", "Deletar"]),
            "Comp. de Formação":      (FormPossCompCRUD,["Criar", "Buscar"]),
            "Idioma":                 (IdiomaCRUD,      ["Criar", "Buscar"]),
            "Idioma da Conta":        (FalaIdiomCRUD,   ["Criar", "Buscar", "Deletar"]),
            "Conexão":                (ConexaoCRUD,     ["Criar", "Buscar", "Atualizar", "Deletar"]),
            "Setor de Empresa":       (SetorEmpCRUD,    ["Criar", "Buscar", "Deletar"]),
        }

        CORES_OP = {
            "Criar":     "#2e7d32",
            "Buscar":    "#1565c0",
            "Atualizar": "#e65100",
            "Deletar":   "#b71c1c",
        }

        # Canvas com scrollbar
        canvas = tk.Canvas(frame, borderwidth=0)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def _scroll(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

        for nome, (cls, ops) in MODULOS.items():
            row_frame = tk.Frame(inner, pady=3)
            row_frame.pack(fill="x", padx=6)

            tk.Label(row_frame, text=nome, width=22, anchor="w",
                     font=("Arial", 10)).pack(side="left", padx=(4, 8))

            for op in ops:
                cor = CORES_OP.get(op, "#333")
                metodo = f"tela_{op.lower()}" if op != "Atualizar" else "tela_atualizar"
                metodo = "tela_" + {"Criar":"criar","Buscar":"buscar",
                                    "Atualizar":"atualizar","Deletar":"deletar"}[op]

                OP_LABELS = {"criar": "Criar", "buscar": "Buscar", "atualizar": "Atualizar", "deletar": "Deletar"}

                def make_cmd(n, c, m):
                    op_label = OP_LABELS.get(m.split("_")[1], m)
                    titulo = f"{n} › {op_label}"
                    def cmd():
                        inst = self._conta_crud if c is ContaCRUD else c
                        fn = getattr(inst, m)
                        self._push(titulo, fn)
                    return cmd

                tk.Button(row_frame, text=op, width=9, bg=cor, fg="white",
                          activebackground=cor, font=("Arial", 9),
                          command=make_cmd(nome, cls, metodo)).pack(side="left", padx=2)

            ttk.Separator(inner, orient="horizontal").pack(fill="x", padx=6, pady=1)

    # ── Tela de configuração (permanece como diálogo modal) ──

    def tela_configuracao(self):
        janela = tk.Toplevel(self.root)
        janela.title("Configuração do Banco de Dados")
        janela.geometry("350x280")
        janela.resizable(False, False)
        janela.grab_set()

        tk.Label(janela, text="Configuração de Conexão", font=("Arial", 11, "bold")).pack(pady=10)
        frame = tk.Frame(janela); frame.pack(pady=5)

        campos = [("Host:", "host"), ("Porta:", "port"), ("Banco:", "dbname"),
                  ("Usuário:", "user"), ("Senha:", "password")]
        entradas = {}

        for i, (label, chave) in enumerate(campos):
            tk.Label(frame, text=label, anchor="e", width=12).grid(row=i, column=0, padx=5, pady=3, sticky="e")
            ent = tk.Entry(frame, width=25, show="*" if chave == "password" else "")
            ent.insert(0, DB_CONFIG.get(chave, ""))
            ent.grid(row=i, column=1, pady=3)
            entradas[chave] = ent

        lbl_st = tk.Label(janela, text="", fg="gray"); lbl_st.pack()

        def salvar():
            for k, e in entradas.items():
                DB_CONFIG[k] = e.get()
            c = conectar_bd()
            if c:
                lbl_st.config(text="✔ Conexão bem-sucedida!", fg="green"); c.close()
            else:
                lbl_st.config(text="✘ Falha. Verifique os dados.", fg="red")

        fb = tk.Frame(janela); fb.pack(pady=8)
        tk.Button(fb, text="Testar e Salvar", width=16, command=salvar).pack(side="left", padx=5)
        tk.Button(fb, text="Fechar", width=10, command=janela.destroy).pack(side="left", padx=5)


# ════════════════════════════════════════════════════════════════
#  BASE MIXIN para construção de forms dentro do frame único
# ════════════════════════════════════════════════════════════════

class BaseCRUD:
    """Classe base; métodos recebem `frame` (ao invés de abrir Toplevel)."""

    def _resultado_text(self, frame, width=62, height=14):
        """Cria Text + Scrollbar dentro de frame."""
        cont = tk.Frame(frame)
        cont.pack(fill="both", expand=True, pady=6)
        sb = ttk.Scrollbar(cont)
        sb.pack(side="right", fill="y")
        txt = tk.Text(cont, width=width, height=height, state="disabled",
                      yscrollcommand=sb.set, wrap="word")
        txt.pack(side="left", fill="both", expand=True)
        sb.config(command=txt.yview)
        return txt

    def _exibir(self, txt, texto):
        txt.config(state="normal")
        txt.delete("1.0", "end")
        txt.insert("end", texto)
        txt.config(state="disabled")

    def _btn_salvar(self, frame, row, cmd, texto="Salvar"):
        tk.Button(frame, text=texto, width=20, command=cmd).grid(
            row=row, column=0, columnspan=2, pady=12)


# ════════════════════════════════════════════════════════════════
#  POST
# ════════════════════════════════════════════════════════════════

class PostCRUD(BaseCRUD):
    NIVEIS = ["Publico", "Conexoes", "Privado"]

    def tela_criar(self, frame):
        tk.Label(frame, text="Criar Post", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn)
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        tk.Label(f, text="Conteúdo:").grid(row=1, column=0, sticky="ne", padx=5, pady=3)
        txt = tk.Text(f, width=30, height=5); txt.grid(row=1, column=1, pady=3)
        tk.Label(f, text="Nível Visib.:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        cb_nv = ttk.Combobox(f, values=self.NIVEIS, state="readonly", width=28)
        cb_nv.current(0); cb_nv.grid(row=2, column=1, pady=3)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=4, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); cont = txt.get("1.0","end-1c").strip()
            if not id_c or not cont:
                messagebox.showerror("Erro","Preencha todos os campos."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO POST (DtPubliPost, ConteudoPost, NivelVisib, IDConta) VALUES (CURRENT_DATE,%s,%s,%s);",
                                (cont, cb_nv.get(), id_c))
                conn.commit()
                lbl_ok.config(text="✔ Post criado com sucesso!")
                txt.delete("1.0","end"); cb_conta.set("")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 3, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Posts", font=("Arial", 12, "bold")).pack(pady=8)
        f_top = tk.Frame(frame); f_top.pack(pady=4)

        tk.Label(f_top, text="ID do Post:").grid(row=0, column=0, sticky="e", padx=4)
        ent_id = tk.Entry(f_top, width=10); ent_id.grid(row=0, column=1, padx=4)
        tk.Label(f_top, text="ou ID Conta:").grid(row=0, column=2, sticky="e", padx=4)
        ent_c = tk.Entry(f_top, width=10); ent_c.grid(row=0, column=3, padx=4)
        tk.Button(f_top, text="Buscar", command=lambda: buscar()).grid(row=0, column=4, padx=6)

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    ip = ent_id.get().strip(); ic = ent_c.get().strip()
                    if ip:
                        cur.execute("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST WHERE IDPost=%s;", (ip,))
                    elif ic:
                        cur.execute("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST WHERE IDConta=%s ORDER BY DtPubliPost DESC;", (ic,))
                    else:
                        cur.execute("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST ORDER BY DtPubliPost DESC LIMIT 30;")
                    rows = cur.fetchall()
                    if not rows:
                        self._exibir(txt_res, "Nenhum resultado."); return
                    out = ""
                    for r in rows:
                        out += f"ID:{r[0]}  Data:{r[1]}  Nível:{r[2]}  Conta:{r[4]}\n{r[3]}\n{'─'*55}\n"
                    self._exibir(txt_res, out)
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_atualizar(self, frame):
        tk.Label(frame, text="Atualizar Post", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        ent_id = label_entry(f, "ID do Post:", 0, width=10)
        tk.Button(f, text="Carregar", command=lambda: carregar()).grid(row=0, column=2, padx=6)
        lbl_st = tk.Label(f, text=""); lbl_st.grid(row=1, column=0, columnspan=3)
        tk.Label(f, text="Conteúdo:").grid(row=2, column=0, sticky="ne", padx=5, pady=3)
        txt_novo = tk.Text(f, width=30, height=5); txt_novo.grid(row=2, column=1, pady=3)
        tk.Label(f, text="Nível:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        cb_nv = ttk.Combobox(f, values=PostCRUD.NIVEIS, state="readonly", width=28)
        cb_nv.current(0); cb_nv.grid(row=3, column=1, pady=3)

        def carregar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT ConteudoPost, NivelVisib FROM POST WHERE IDPost=%s;", (ent_id.get(),))
                    row = cur.fetchone()
                    if not row: lbl_st.config(text="Post não encontrado.", fg="red"); return
                    txt_novo.delete("1.0","end"); txt_novo.insert("1.0", row[0])
                    cb_nv.set(row[1]); lbl_st.config(text="✔ Carregado.", fg="green")
            finally:
                conn.close()

        def salvar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE POST SET ConteudoPost=%s, NivelVisib=%s WHERE IDPost=%s;",
                                (txt_novo.get("1.0","end-1c"), cb_nv.get(), ent_id.get()))
                conn.commit(); lbl_st.config(text="✔ Post atualizado!", fg="green")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 4, salvar)

    def tela_deletar(self, frame):
        tk.Label(frame, text="Deletar Post", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=10)
        ent_id = label_entry(f, "ID do Post:", 0, width=10)
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=2, column=0, columnspan=2)

        def deletar():
            if not messagebox.askyesno("Confirmar", "Deletar este post e seus comentários/reações?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM POST WHERE IDPost=%s;", (ent_id.get(),))
                conn.commit(); lbl_ok.config(text="✔ Post deletado!", fg="green")
                ent_id.delete(0, "end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, deletar, "Deletar")


# ════════════════════════════════════════════════════════════════
#  COMENTARIO
# ════════════════════════════════════════════════════════════════

class ComentarioCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Criar Comentário", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDPost, LEFT(ConteudoPost,40) FROM POST ORDER BY IDPost DESC;")
                posts = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_post  = label_combo(f, "Post:", 1);  cb_post["values"] = posts
        tk.Label(f, text="Conteúdo:").grid(row=2, column=0, sticky="ne", padx=5, pady=3)
        txt = tk.Text(f, width=28, height=4); txt.grid(row=2, column=1, pady=3)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=4, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); id_p = extrair_id(cb_post.get())
            cont = txt.get("1.0","end-1c").strip()
            if not id_c or not id_p or not cont:
                messagebox.showerror("Erro","Preencha todos os campos."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO COMENTARIO (ConteudoTxtCom, DtPubliCom, IDPost, IDConta) VALUES (%s, CURRENT_DATE, %s, %s);",
                                (cont, id_p, id_c))
                conn.commit(); lbl_ok.config(text="✔ Comentário criado!")
                txt.delete("1.0","end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 3, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Comentários", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID do Post:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDComentario, DtPubliCom, IDConta, ConteudoTxtCom FROM COMENTARIO WHERE IDPost=%s ORDER BY DtPubliCom;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: self._exibir(txt_res, "Nenhum comentário."); return
                    out = "".join(f"#{r[0]}  {r[1]}  Conta:{r[2]}\n{r[3]}\n{'─'*55}\n" for r in rows)
                    self._exibir(txt_res, out)
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Deletar Comentário", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=10)
        ent = label_entry(f, "ID do Comentário:", 0, width=10)
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=2, column=0, columnspan=2)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar este comentário?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM COMENTARIO WHERE IDComentario=%s;", (ent.get(),))
                conn.commit(); lbl_ok.config(text="✔ Comentário deletado!", fg="green")
                ent.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, deletar, "Deletar")


# ════════════════════════════════════════════════════════════════
#  REAGEPOST
# ════════════════════════════════════════════════════════════════

class ReagePostCRUD(BaseCRUD):
    TIPOS = ["Curtir", "Celebrar", "Apoiar", "Interessante", "Curioso"]

    def tela_criar(self, frame):
        tk.Label(frame, text="Reagir a Post", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDPost, LEFT(ConteudoPost,40) FROM POST ORDER BY IDPost DESC;")
                posts = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_post  = label_combo(f, "Post:", 1);  cb_post["values"] = posts
        tk.Label(f, text="Tipo Reação:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        cb_tipo = ttk.Combobox(f, values=self.TIPOS, state="readonly", width=28)
        cb_tipo.current(0); cb_tipo.grid(row=2, column=1, pady=3)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=4, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); id_p = extrair_id(cb_post.get())
            if not id_c or not id_p:
                messagebox.showerror("Erro","Selecione conta e post."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO REAGEPOST (IDConta, IDPost, DtReacao, TipoReacao) VALUES (%s,%s,CURRENT_DATE,%s) ON CONFLICT (IDConta,IDPost) DO UPDATE SET TipoReacao=%s, DtReacao=CURRENT_DATE;",
                                (id_c, id_p, cb_tipo.get(), cb_tipo.get()))
                conn.commit(); lbl_ok.config(text="✔ Reação registrada!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 3, salvar, "Reagir")

    def tela_buscar(self, frame):
        tk.Label(frame, text="Ver Reações de Post", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID do Post:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDConta, TipoReacao, DtReacao FROM REAGEPOST WHERE IDPost=%s ORDER BY DtReacao DESC;", (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: self._exibir(txt_res, "Nenhuma reação."); return
                    self._exibir(txt_res, "".join(f"Conta:{r[0]}  Tipo:{r[1]}  Data:{r[2]}\n" for r in rows))
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Remover Reação", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDPost, LEFT(ConteudoPost,40) FROM POST ORDER BY IDPost DESC;")
                posts = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_post  = label_combo(f, "Post:", 1);  cb_post["values"] = posts
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=3, column=0, columnspan=2)

        def deletar():
            id_c = extrair_id(cb_conta.get()); id_p = extrair_id(cb_post.get())
            if not id_c or not id_p: messagebox.showerror("Erro","Selecione conta e post."); return
            if not messagebox.askyesno("Confirmar","Remover reação?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM REAGEPOST WHERE IDConta=%s AND IDPost=%s;", (id_c, id_p))
                conn.commit(); lbl_ok.config(text="✔ Reação removida!", fg="green")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, deletar, "Remover")


# ════════════════════════════════════════════════════════════════
#  VAGAEMPREGO
# ════════════════════════════════════════════════════════════════

class VagaCRUD(BaseCRUD):
    FORMATOS = ["Presencial", "Remoto", "Hibrido"]

    def tela_criar(self, frame):
        tk.Label(frame, text="Criar Vaga de Emprego", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            corps = buscar_corporativas(conn)
        finally:
            conn.close()

        cb_emp    = label_combo(f, "Empresa:", 0);    cb_emp["values"] = corps
        ent_tit   = label_entry(f, "Título:", 1)
        tk.Label(f, text="Descrição:").grid(row=2, column=0, sticky="ne", padx=5, pady=3)
        txt_desc  = tk.Text(f, width=28, height=4); txt_desc.grid(row=2, column=1, pady=3)
        tk.Label(f, text="Formato:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        cb_fmt = ttk.Combobox(f, values=self.FORMATOS, state="readonly", width=28)
        cb_fmt.current(0); cb_fmt.grid(row=3, column=1, pady=3)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=5, column=0, columnspan=2)

        def salvar():
            id_e = extrair_id(cb_emp.get()); tit = ent_tit.get().strip()
            if not id_e or not tit:
                messagebox.showerror("Erro","Preencha empresa e título."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO VAGAEMPREGO (TtloVaga, DescriVaga, FormatoTrabVaga, DtCrcaoVaga, IDConta) VALUES (%s,%s,%s,CURRENT_DATE,%s);",
                                (tit, txt_desc.get("1.0","end-1c"), cb_fmt.get(), id_e))
                conn.commit(); lbl_ok.config(text="✔ Vaga criada!")
                ent_tit.delete(0,"end"); txt_desc.delete("1.0","end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 4, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Vagas", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="Título (parcial):").pack(side="left")
        ent = tk.Entry(f, width=22); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    t = ent.get().strip()
                    if t:
                        cur.execute("SELECT v.IDVagaEmo, v.TtloVaga, v.FormatoTrabVaga, v.DtCrcaoVaga, c.NomComerc FROM VAGAEMPREGO v JOIN CORPORATIVA c ON v.IDConta=c.IDConta WHERE v.TtloVaga ILIKE %s ORDER BY v.DtCrcaoVaga DESC;", (f"%{t}%",))
                    else:
                        cur.execute("SELECT v.IDVagaEmo, v.TtloVaga, v.FormatoTrabVaga, v.DtCrcaoVaga, c.NomComerc FROM VAGAEMPREGO v JOIN CORPORATIVA c ON v.IDConta=c.IDConta ORDER BY v.DtCrcaoVaga DESC LIMIT 30;")
                    rows = cur.fetchall()
                    if not rows: self._exibir(txt_res, "Nenhuma vaga."); return
                    out = "".join(f"ID:{r[0]}  {r[1]}  [{r[2]}]  {r[3]}\nEmpresa: {r[4]}\n{'─'*55}\n" for r in rows)
                    self._exibir(txt_res, out)
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Deletar Vaga", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=10)
        ent = label_entry(f, "ID da Vaga:", 0, width=10)
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=2, column=0, columnspan=2)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar esta vaga e suas aplicações?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM VAGAEMPREGO WHERE IDVagaEmo=%s;", (ent.get(),))
                conn.commit(); lbl_ok.config(text="✔ Vaga deletada!", fg="green")
                ent.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, deletar, "Deletar")


# ════════════════════════════════════════════════════════════════
#  APLICAVAGA
# ════════════════════════════════════════════════════════════════

class AplicaVagaCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Aplicar a Vaga", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDVagaEmo, TtloVaga FROM VAGAEMPREGO ORDER BY TtloVaga;")
                vagas = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Candidato (Conta):", 0); cb_conta["values"] = contas
        cb_vaga  = label_combo(f, "Vaga:", 1);              cb_vaga["values"] = vagas
        ent_site = label_entry(f, "Site/URL:", 2)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=4, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); id_v = extrair_id(cb_vaga.get())
            if not id_c or not id_v:
                messagebox.showerror("Erro","Selecione conta e vaga."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO APLICAAVAGA (IDVagaEmo, DtAplicao, SitusAplicao, IDConta) VALUES (%s, CURRENT_DATE, %s, %s);",
                                (id_v, ent_site.get() or None, id_c))
                conn.commit(); lbl_ok.config(text="✔ Aplicação registrada!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 3, salvar, "Aplicar")

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Aplicações", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID da Vaga:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    iv = ent.get().strip()
                    if iv:
                        cur.execute("SELECT IDVagaEmo, IDConta, DtAplicao, SitusAplicao FROM APLICAAVAGA WHERE IDVagaEmo=%s ORDER BY DtAplicao;", (iv,))
                    else:
                        cur.execute("SELECT IDVagaEmo, IDConta, DtAplicao, SitusAplicao FROM APLICAAVAGA ORDER BY DtAplicao DESC LIMIT 30;")
                    rows = cur.fetchall()
                    if not rows: self._exibir(txt_res, "Nenhuma aplicação."); return
                    self._exibir(txt_res, "".join(f"Vaga:{r[0]}  Conta:{r[1]}  Data:{r[2]}  Site:{r[3] or '-'}\n" for r in rows))
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()


# ════════════════════════════════════════════════════════════════
#  COMPETENCIA
# ════════════════════════════════════════════════════════════════

class CompetenciaCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Criar Competência", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=10)
        ent = label_entry(f, "Nome:", 0)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=2, column=0, columnspan=2)

        def salvar():
            nome = ent.get().strip()
            if not nome: messagebox.showerror("Erro","Preencha o nome."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO COMPETENCIA (NomeComp) VALUES (%s);", (nome,))
                conn.commit(); lbl_ok.config(text="✔ Competência criada!")
                ent.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Listar Competências", font=("Arial", 12, "bold")).pack(pady=8)
        txt_res = self._resultado_text(frame, height=16)
        tk.Button(frame, text="Atualizar Lista", command=lambda: listar()).pack(pady=4)

        def listar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDComp, NomeComp FROM COMPETENCIA ORDER BY NomeComp;")
                    rows = cur.fetchall()
                    self._exibir(txt_res, "".join(f"{r[0]} - {r[1]}\n" for r in rows) or "Nenhuma.")
            finally:
                conn.close()

        listar()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Deletar Competência", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            comps = buscar_competencias(conn)
        finally:
            conn.close()

        cb = label_combo(f, "Competência:", 0); cb["values"] = comps
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=2, column=0, columnspan=2)

        def deletar():
            id_c = extrair_id(cb.get())
            if not id_c: return
            if not messagebox.askyesno("Confirmar","Deletar competência?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM COMPETENCIA WHERE IDComp=%s;", (id_c,))
                conn.commit(); lbl_ok.config(text="✔ Competência deletada!", fg="green")
                cb.set("")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, deletar, "Deletar")


# ════════════════════════════════════════════════════════════════
#  POSSCOMP
# ════════════════════════════════════════════════════════════════

class PossCompCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Adicionar Competência à Conta", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn); comps = buscar_competencias(conn)
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_comp  = label_combo(f, "Competência:", 1); cb_comp["values"] = comps
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=3, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); id_k = extrair_id(cb_comp.get())
            if not id_c or not id_k: messagebox.showerror("Erro","Selecione conta e competência."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO POSSCOMP (IDComp, IDConta) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_k, id_c))
                conn.commit(); lbl_ok.config(text="✔ Competência vinculada!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, salvar, "Vincular")

    def tela_buscar(self, frame):
        tk.Label(frame, text="Competências da Conta", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT c.IDComp, c.NomeComp FROM POSSCOMP pc JOIN COMPETENCIA c ON pc.IDComp=c.IDComp WHERE pc.IDConta=%s ORDER BY c.NomeComp;", (ent.get(),))
                    rows = cur.fetchall()
                    self._exibir(txt_res, "".join(f"{r[0]} - {r[1]}\n" for r in rows) or "Nenhuma competência.")
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Remover Competência da Conta", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn); comps = buscar_competencias(conn)
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_comp  = label_combo(f, "Competência:", 1); cb_comp["values"] = comps
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=3, column=0, columnspan=2)

        def deletar():
            id_c = extrair_id(cb_conta.get()); id_k = extrair_id(cb_comp.get())
            if not id_c or not id_k: return
            if not messagebox.askyesno("Confirmar","Remover vínculo?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM POSSCOMP WHERE IDComp=%s AND IDConta=%s;", (id_k, id_c))
                conn.commit(); lbl_ok.config(text="✔ Vínculo removido!", fg="green")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, deletar, "Remover")


# ════════════════════════════════════════════════════════════════
#  EXPERIENCIAPROF
# ════════════════════════════════════════════════════════════════

class ExpProfCRUD(BaseCRUD):
    TIPOS_EMP = ["CLT", "PJ", "Freelancer", "Estagio", "Temporario"]

    def tela_criar(self, frame):
        tk.Label(frame, text="Criar Experiência Profissional", font=("Arial", 12, "bold")).pack(pady=8)

        canvas = tk.Canvas(frame, borderwidth=0)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        f = inner

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn); corps = buscar_corporativas(conn)
        finally:
            conn.close()

        cb_conta   = label_combo(f, "Conta:", 0);              cb_conta["values"] = contas
        ent_titulo = label_entry(f, "Título:", 1)
        tk.Label(f, text="Tipo Emprego:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        cb_tipo = ttk.Combobox(f, values=self.TIPOS_EMP, state="readonly", width=28)
        cb_tipo.current(0); cb_tipo.grid(row=2, column=1, pady=3)
        ent_ini    = label_entry(f, "Dt Início (AAAA-MM-DD):", 3)
        ent_fim    = label_entry(f, "Dt Fim (ou vazio):", 4)
        txt_desc   = label_text(f, "Descrição:", 5)
        cb_emp     = label_combo(f, "Empresa (opcional):", 6); cb_emp["values"] = [""] + corps
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=8, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); tit = ent_titulo.get().strip()
            if not id_c or not tit: messagebox.showerror("Erro","Preencha conta e título."); return
            id_emp = extrair_id(cb_emp.get()) if cb_emp.get() else None
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO EXPERIENCIAPROF (TituloExp, TipoEmpregoExp, DtInicioExp, DtFimExp, DescAtv, IDUsr, IDEmp) VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                (tit, cb_tipo.get(), ent_ini.get(), ent_fim.get() or None,
                                 txt_desc.get("1.0","end-1c"), id_c, id_emp))
                conn.commit(); lbl_ok.config(text="✔ Experiência criada!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 7, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Experiências", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT e.IDExp, e.TituloExp, e.TipoEmpregoExp, e.DtInicioExp, e.DtFimExp, COALESCE(c.NomComerc,'') FROM EXPERIENCIAPROF e LEFT JOIN CORPORATIVA c ON e.IDEmp=c.IDConta WHERE e.IDUsr=%s ORDER BY e.DtInicioExp DESC;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: self._exibir(txt_res, "Nenhuma experiência."); return
                    out = "".join(f"#{r[0]}  {r[1]}  [{r[2]}]\n  {r[3]} → {r[4] or 'atual'}  Empresa:{r[5]}\n{'─'*55}\n" for r in rows)
                    self._exibir(txt_res, out)
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Deletar Experiência", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=10)
        ent = label_entry(f, "ID Experiência:", 0, width=10)
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=2, column=0, columnspan=2)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar experiência?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM EXPERIENCIAPROF WHERE IDExp=%s;", (ent.get(),))
                conn.commit(); lbl_ok.config(text="✔ Experiência deletada!", fg="green")
                ent.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, deletar, "Deletar")


# ════════════════════════════════════════════════════════════════
#  EXPPOSSCOMP
# ════════════════════════════════════════════════════════════════

class ExpPossCompCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Vincular Competência a Experiência", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            comps = buscar_competencias(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDExp, TituloExp FROM EXPERIENCIAPROF ORDER BY TituloExp;")
                exps = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_exp  = label_combo(f, "Experiência:", 0); cb_exp["values"] = exps
        cb_comp = label_combo(f, "Competência:", 1); cb_comp["values"] = comps
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=3, column=0, columnspan=2)

        def salvar():
            id_e = extrair_id(cb_exp.get()); id_k = extrair_id(cb_comp.get())
            if not id_e or not id_k: messagebox.showerror("Erro","Selecione experiência e competência."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO EXPPOSSCOMP (IDComp, IDExp) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_k, id_e))
                conn.commit(); lbl_ok.config(text="✔ Vínculo criado!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, salvar, "Vincular")

    def tela_buscar(self, frame):
        tk.Label(frame, text="Competências por Experiência", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID Experiência:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT c.IDComp, c.NomeComp FROM EXPPOSSCOMP ec JOIN COMPETENCIA c ON ec.IDComp=c.IDComp WHERE ec.IDExp=%s;", (ent.get(),))
                    rows = cur.fetchall()
                    self._exibir(txt_res, "".join(f"{r[0]} - {r[1]}\n" for r in rows) or "Nenhuma.")
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()


# ════════════════════════════════════════════════════════════════
#  FORMACAOACAD
# ════════════════════════════════════════════════════════════════

class FormacaoCRUD(BaseCRUD):
    GRAUS = ["Fundamental", "Medio", "Tecnico", "Graduacao", "Pos-graduacao", "Mestrado", "Doutorado"]

    def tela_criar(self, frame):
        tk.Label(frame, text="Criar Formação Acadêmica", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn)
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        ent_inst = label_entry(f, "Instituição:", 1)
        tk.Label(f, text="Grau:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        cb_grau = ttk.Combobox(f, values=self.GRAUS, state="readonly", width=28)
        cb_grau.current(3); cb_grau.grid(row=2, column=1, pady=3)
        ent_area = label_entry(f, "Área:", 3)
        ent_ini  = label_entry(f, "Dt Início (AAAA-MM-DD):", 4)
        ent_fim  = label_entry(f, "Dt Fim (ou vazio):", 5)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=7, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); inst = ent_inst.get().strip()
            if not id_c or not inst: messagebox.showerror("Erro","Preencha conta e instituição."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO FORMACAOACAD (NomInstlForm, GrauForm, AreaForm, DtInicioForm, DtFimForm, IDConta) VALUES (%s,%s,%s,%s,%s,%s);",
                                (inst, cb_grau.get(), ent_area.get() or None,
                                 ent_ini.get() or None, ent_fim.get() or None, id_c))
                conn.commit(); lbl_ok.config(text="✔ Formação criada!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 6, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Formações", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDForm, NomInstlForm, GrauForm, AreaForm, DtInicioForm, DtFimForm FROM FORMACAOACAD WHERE IDConta=%s ORDER BY DtInicioForm DESC;", (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: self._exibir(txt_res, "Nenhuma formação."); return
                    out = "".join(f"#{r[0]}  {r[1]}  [{r[2]}]  Área:{r[3] or '-'}\n  {r[4]} → {r[5] or 'atual'}\n{'─'*55}\n" for r in rows)
                    self._exibir(txt_res, out)
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Deletar Formação", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=10)
        ent = label_entry(f, "ID Formação:", 0, width=10)
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=2, column=0, columnspan=2)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar formação?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM FORMACAOACAD WHERE IDForm=%s;", (ent.get(),))
                conn.commit(); lbl_ok.config(text="✔ Formação deletada!", fg="green")
                ent.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, deletar, "Deletar")


# ════════════════════════════════════════════════════════════════
#  FORMPOSSCOMP
# ════════════════════════════════════════════════════════════════

class FormPossCompCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Vincular Competência a Formação", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            comps = buscar_competencias(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDForm, NomInstlForm FROM FORMACAOACAD ORDER BY NomInstlForm;")
                forms = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_form = label_combo(f, "Formação:", 0); cb_form["values"] = forms
        cb_comp = label_combo(f, "Competência:", 1); cb_comp["values"] = comps
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=3, column=0, columnspan=2)

        def salvar():
            id_f = extrair_id(cb_form.get()); id_k = extrair_id(cb_comp.get())
            if not id_f or not id_k: messagebox.showerror("Erro","Selecione formação e competência."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO FORMPOSSCOMP (IDComp, IDForm) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_k, id_f))
                conn.commit(); lbl_ok.config(text="✔ Vínculo criado!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, salvar, "Vincular")

    def tela_buscar(self, frame):
        tk.Label(frame, text="Competências por Formação", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID Formação:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT c.IDComp, c.NomeComp FROM FORMPOSSCOMP fc JOIN COMPETENCIA c ON fc.IDComp=c.IDComp WHERE fc.IDForm=%s;", (ent.get(),))
                    rows = cur.fetchall()
                    self._exibir(txt_res, "".join(f"{r[0]} - {r[1]}\n" for r in rows) or "Nenhuma.")
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()


# ════════════════════════════════════════════════════════════════
#  IDIOMA
# ════════════════════════════════════════════════════════════════

class IdiomaCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Cadastrar Idioma", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=10)
        ent = label_entry(f, "Nome:", 0)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=2, column=0, columnspan=2)

        def salvar():
            nome = ent.get().strip()
            if not nome: messagebox.showerror("Erro","Preencha o nome."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO IDIOMA (NomeIdioma) VALUES (%s);", (nome,))
                conn.commit(); lbl_ok.config(text="✔ Idioma cadastrado!")
                ent.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 1, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Listar Idiomas", font=("Arial", 12, "bold")).pack(pady=8)
        txt_res = self._resultado_text(frame, height=16)
        tk.Button(frame, text="Atualizar Lista", command=lambda: listar()).pack(pady=4)

        def listar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDIdioma, NomeIdioma FROM IDIOMA ORDER BY NomeIdioma;")
                    rows = cur.fetchall()
                    self._exibir(txt_res, "".join(f"{r[0]} - {r[1]}\n" for r in rows) or "Nenhum.")
            finally:
                conn.close()

        listar()


# ════════════════════════════════════════════════════════════════
#  FALAIDIOM
# ════════════════════════════════════════════════════════════════

class FalaIdiomCRUD(BaseCRUD):
    NIVEIS = ["Basico", "Intermediario", "Avancado", "Fluente", "Nativo"]

    def tela_criar(self, frame):
        tk.Label(frame, text="Vincular Idioma à Conta", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn); idiomas = buscar_idiomas(conn)
        finally:
            conn.close()

        cb_conta  = label_combo(f, "Conta:", 0);  cb_conta["values"] = contas
        cb_idioma = label_combo(f, "Idioma:", 1); cb_idioma["values"] = idiomas
        tk.Label(f, text="Nível Profic.:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        cb_nv = ttk.Combobox(f, values=self.NIVEIS, state="readonly", width=28)
        cb_nv.current(0); cb_nv.grid(row=2, column=1, pady=3)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=4, column=0, columnspan=2)

        def salvar():
            id_c = extrair_id(cb_conta.get()); id_i = extrair_id(cb_idioma.get())
            if not id_c or not id_i: messagebox.showerror("Erro","Selecione conta e idioma."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO FALAIDIOM (IDIdioma, NvlProfic, IDConta) VALUES (%s,%s,%s) ON CONFLICT (IDIdioma, IDConta) DO UPDATE SET NvlProfic=%s;",
                                (id_i, cb_nv.get(), id_c, cb_nv.get()))
                conn.commit(); lbl_ok.config(text="✔ Idioma vinculado!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 3, salvar, "Vincular")

    def tela_buscar(self, frame):
        tk.Label(frame, text="Idiomas da Conta", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT i.IDIdioma, i.NomeIdioma, fi.NvlProfic FROM FALAIDIOM fi JOIN IDIOMA i ON fi.IDIdioma=i.IDIdioma WHERE fi.IDConta=%s ORDER BY i.NomeIdioma;", (ent.get(),))
                    rows = cur.fetchall()
                    self._exibir(txt_res, "".join(f"{r[0]} - {r[1]}  Nível: {r[2]}\n" for r in rows) or "Nenhum idioma vinculado.")
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Remover Idioma da Conta", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn); idiomas = buscar_idiomas(conn)
        finally:
            conn.close()

        cb_conta  = label_combo(f, "Conta:", 0);  cb_conta["values"] = contas
        cb_idioma = label_combo(f, "Idioma:", 1); cb_idioma["values"] = idiomas
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=3, column=0, columnspan=2)

        def deletar():
            id_c = extrair_id(cb_conta.get()); id_i = extrair_id(cb_idioma.get())
            if not id_c or not id_i: return
            if not messagebox.askyesno("Confirmar","Remover vínculo?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM FALAIDIOM WHERE IDIdioma=%s AND IDConta=%s;", (id_i, id_c))
                conn.commit(); lbl_ok.config(text="✔ Vínculo removido!", fg="green")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, deletar, "Remover")


# ════════════════════════════════════════════════════════════════
#  CONEXAO
# ════════════════════════════════════════════════════════════════

class ConexaoCRUD(BaseCRUD):
    STATUS = ["Pendente", "Aceita", "Recusada"]

    def tela_criar(self, frame):
        tk.Label(frame, text="Enviar Solicitação de Conexão", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = buscar_contas(conn)
        finally:
            conn.close()

        cb_de   = label_combo(f, "De (Conta):", 0);   cb_de["values"] = contas
        cb_para = label_combo(f, "Para (Conta):", 1); cb_para["values"] = contas
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=3, column=0, columnspan=2)

        def salvar():
            id_de = extrair_id(cb_de.get()); id_para = extrair_id(cb_para.get())
            if not id_de or not id_para or id_de == id_para:
                messagebox.showerror("Erro","Selecione duas contas distintas."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO CONEXAO (DtEnvConv, StatusConexao, IDConta_3, IDConta_2) VALUES (CURRENT_DATE, 'Pendente', %s, %s);",
                                (id_de, id_para))
                conn.commit(); lbl_ok.config(text="✔ Solicitação enviada!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, salvar, "Enviar")

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Conexões", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            id_c = ent.get().strip()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDConta_3, IDConta_2, DtEnvConv, DtAceitConv, StatusConexao FROM CONEXAO WHERE IDConta_3=%s OR IDConta_2=%s ORDER BY DtEnvConv DESC;",
                                (id_c, id_c))
                    rows = cur.fetchall()
                    if not rows: self._exibir(txt_res, "Nenhuma conexão."); return
                    self._exibir(txt_res, "".join(f"De:{r[0]} → Para:{r[1]}  Enviado:{r[2]}  Aceito:{r[3] or '-'}  Status:{r[4]}\n" for r in rows))
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_atualizar(self, frame):
        tk.Label(frame, text="Atualizar Status de Conexão", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)
        ent_de   = label_entry(f, "ID Conta Remetente:", 0, width=12)
        ent_para = label_entry(f, "ID Conta Destinatário:", 1, width=12)
        tk.Label(f, text="Novo Status:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        cb_st = ttk.Combobox(f, values=self.STATUS, state="readonly", width=16)
        cb_st.current(1); cb_st.grid(row=2, column=1, pady=3, sticky="w")
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=4, column=0, columnspan=2)

        def salvar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    dt = "CURRENT_DATE" if cb_st.get() == "Aceita" else "NULL"
                    cur.execute(f"UPDATE CONEXAO SET StatusConexao=%s, DtAceitConv={dt} WHERE IDConta_3=%s AND IDConta_2=%s;",
                                (cb_st.get(), ent_de.get(), ent_para.get()))
                conn.commit(); lbl_ok.config(text="✔ Status atualizado!")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 3, salvar)

    def tela_deletar(self, frame):
        tk.Label(frame, text="Remover Conexão", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)
        ent_de   = label_entry(f, "ID Conta Remetente:", 0, width=12)
        ent_para = label_entry(f, "ID Conta Destinatário:", 1, width=12)
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=3, column=0, columnspan=2)

        def deletar():
            if not messagebox.askyesno("Confirmar","Remover conexão?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM CONEXAO WHERE IDConta_3=%s AND IDConta_2=%s;", (ent_de.get(), ent_para.get()))
                conn.commit(); lbl_ok.config(text="✔ Conexão removida!", fg="green")
                ent_de.delete(0,"end"); ent_para.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, deletar, "Remover")


# ════════════════════════════════════════════════════════════════
#  CORPORATIVA_SETOREMP
# ════════════════════════════════════════════════════════════════

class SetorEmpCRUD(BaseCRUD):
    def tela_criar(self, frame):
        tk.Label(frame, text="Adicionar Setor a Empresa", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            corps = buscar_corporativas(conn)
        finally:
            conn.close()

        cb_emp  = label_combo(f, "Empresa:", 0); cb_emp["values"] = corps
        ent_set = label_entry(f, "Setor:", 1)
        lbl_ok = tk.Label(f, text="", fg="green"); lbl_ok.grid(row=3, column=0, columnspan=2)

        def salvar():
            id_e = extrair_id(cb_emp.get()); setor = ent_set.get().strip()
            if not id_e or not setor: messagebox.showerror("Erro","Preencha empresa e setor."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO CORPORATIVA_SETOREMP (SetorEmp, IDConta) VALUES (%s,%s);", (setor, id_e))
                conn.commit(); lbl_ok.config(text="✔ Setor adicionado!")
                ent_set.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, salvar)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Setores da Empresa", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=4)
        tk.Label(f, text="ID da Empresa:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        tk.Button(f, text="Buscar", command=lambda: buscar()).pack(side="left")

        txt_res = self._resultado_text(frame)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT SetorEmp FROM CORPORATIVA_SETOREMP WHERE IDConta=%s ORDER BY SetorEmp;", (ent.get(),))
                    rows = cur.fetchall()
                    self._exibir(txt_res, "".join(f"• {r[0]}\n" for r in rows) or "Nenhum setor.")
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

    def tela_deletar(self, frame):
        tk.Label(frame, text="Remover Setor", font=("Arial", 12, "bold")).pack(pady=8)
        f = tk.Frame(frame); f.pack(pady=6)

        conn = conectar_bd()
        if not conn: return
        try:
            corps = buscar_corporativas(conn)
        finally:
            conn.close()

        cb_emp  = label_combo(f, "Empresa:", 0); cb_emp["values"] = corps
        ent_set = label_entry(f, "Setor exato:", 1)
        lbl_ok = tk.Label(f, text=""); lbl_ok.grid(row=3, column=0, columnspan=2)

        def deletar():
            id_e = extrair_id(cb_emp.get()); setor = ent_set.get().strip()
            if not id_e or not setor: return
            if not messagebox.askyesno("Confirmar","Remover setor?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM CORPORATIVA_SETOREMP WHERE SetorEmp=%s AND IDConta=%s;", (setor, id_e))
                conn.commit(); lbl_ok.config(text="✔ Setor removido!", fg="green")
                ent_set.delete(0,"end")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        self._btn_salvar(f, 2, deletar, "Remover")


# ════════════════════════════════════════════════════════════════
#  CONTA  (stateful — mantido como instância)
# ════════════════════════════════════════════════════════════════

class ContaCRUD(BaseCRUD):
    def __init__(self, app):
        self.app = app
        self.ent_din1 = self.ent_din2 = self.ent_din3 = self.txt_din3 = None

    def _busca_dinamica(self, termo, tipo, cb):
        if len(termo) < 2: cb["values"] = []; return
        conn = conectar_bd()
        if not conn: return
        try:
            with conn.cursor() as cur:
                if tipo == "Pessoal":
                    cur.execute("SELECT IDConta, NomPsso||' '||SobnomPsso FROM PESSOAL WHERE NomPsso ILIKE %s OR SobnomPsso ILIKE %s;",
                                (f"%{termo}%", f"%{termo}%"))
                else:
                    cur.execute("SELECT IDConta, NomComerc FROM CORPORATIVA WHERE NomComerc ILIKE %s;", (f"%{termo}%",))
                cb["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        except Error as e:
            print(e)
        finally:
            conn.close()

    def _form_dinamico(self, frame_din, tipo):
        for w in frame_din.winfo_children(): w.destroy()
        if tipo == "Pessoal":
            tk.Label(frame_din, text="Nome:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
            self.ent_din1 = tk.Entry(frame_din, width=30); self.ent_din1.grid(row=0, column=1)
            tk.Label(frame_din, text="Sobrenome:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.ent_din2 = tk.Entry(frame_din, width=30); self.ent_din2.grid(row=1, column=1)
            tk.Label(frame_din, text="Título Prof.:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
            self.ent_din3 = tk.Entry(frame_din, width=30); self.ent_din3.grid(row=2, column=1)
        else:
            tk.Label(frame_din, text="Nome Empresa:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
            self.ent_din1 = tk.Entry(frame_din, width=30); self.ent_din1.grid(row=0, column=1)
            tk.Label(frame_din, text="Nº Funcionários:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.ent_din2 = tk.Entry(frame_din, width=30); self.ent_din2.grid(row=1, column=1)
            tk.Label(frame_din, text="Descrição:").grid(row=2, column=0, sticky="ne", padx=5, pady=2)
            self.txt_din3 = tk.Text(frame_din, width=23, height=4); self.txt_din3.grid(row=2, column=1)

    def tela_criar(self, frame):
        tk.Label(frame, text="Criar Nova Conta", font=("Arial", 12, "bold")).pack(pady=8)

        # Scrollable
        canvas = tk.Canvas(frame, borderwidth=0)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        tipo_var = tk.StringVar(value="Pessoal")
        frame_radios = tk.Frame(inner); frame_radios.pack(pady=5)

        frame_din = tk.Frame(inner)

        tk.Radiobutton(frame_radios, text="Pessoal", variable=tipo_var, value="Pessoal",
                       command=lambda: self._form_dinamico(frame_din, tipo_var.get())).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Corporativa", variable=tipo_var, value="Corporativa",
                       command=lambda: self._form_dinamico(frame_din, tipo_var.get())).pack(side="left", padx=10)

        frame_comum = tk.Frame(inner); frame_comum.pack(pady=6)
        tk.Label(frame_comum, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ent_email = tk.Entry(frame_comum, width=30); ent_email.grid(row=0, column=1)
        tk.Label(frame_comum, text="Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ent_senha = tk.Entry(frame_comum, width=30, show="*"); ent_senha.grid(row=1, column=1)
        tk.Label(frame_comum, text="País:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        cb_pais = ttk.Combobox(frame_comum, width=27, state="readonly"); cb_pais.grid(row=2, column=1)
        tk.Label(frame_comum, text="Estado:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        cb_est  = ttk.Combobox(frame_comum, width=27, state="readonly"); cb_est.grid(row=3, column=1)
        tk.Label(frame_comum, text="Cidade:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        cb_cid  = ttk.Combobox(frame_comum, width=27, state="readonly"); cb_cid.grid(row=4, column=1)

        conn = conectar_bd()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT IDPais, NomPais FROM PAIS;")
                cb_pais["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
            conn.close()

        def ao_pais(e):
            id_p = extrair_id(cb_pais.get())
            c = conectar_bd()
            if c and id_p:
                with c.cursor() as cur:
                    cur.execute("SELECT IDEstado, NomEstado FROM ESTADO WHERE IDPais=%s;", (id_p,))
                    cb_est["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
                    cb_est.set(""); cb_cid.set(""); cb_cid["values"] = []
                c.close()

        def ao_estado(e):
            id_e = extrair_id(cb_est.get())
            c = conectar_bd()
            if c and id_e:
                with c.cursor() as cur:
                    cur.execute("SELECT IDCidade, NomCidade FROM CIDADE WHERE IDEstado=%s;", (id_e,))
                    cb_cid["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
                    cb_cid.set("")
                c.close()

        cb_pais.bind("<<ComboboxSelected>>", ao_pais)
        cb_est.bind("<<ComboboxSelected>>", ao_estado)

        frame_din.pack(pady=6)
        self._form_dinamico(frame_din, "Pessoal")

        lbl_ok = tk.Label(inner, text="", fg="green"); lbl_ok.pack()

        def salvar():
            id_cid = extrair_id(cb_cid.get())
            if not id_cid: messagebox.showerror("Erro","Selecione uma cidade."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade) VALUES (%s,%s,CURRENT_DATE,%s) RETURNING IDConta;",
                                (ent_email.get(), ent_senha.get(), id_cid))
                    id_conta = cur.fetchone()[0]
                    if tipo_var.get() == "Pessoal":
                        cur.execute("INSERT INTO PESSOAL (IDConta, NomPsso, SobnomPsso, TtloProfPsso) VALUES (%s,%s,%s,%s);",
                                    (id_conta, self.ent_din1.get(), self.ent_din2.get(), self.ent_din3.get()))
                    else:
                        cur.execute("INSERT INTO CORPORATIVA (IDConta, NomComerc, NumFuncEmp, DescriEmp) VALUES (%s,%s,%s,%s);",
                                    (id_conta, self.ent_din1.get(), self.ent_din2.get(),
                                     self.txt_din3.get("1.0","end-1c") if self.txt_din3 else ""))
                conn.commit(); lbl_ok.config(text=f"✔ Conta criada! ID={id_conta}")
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        tk.Button(inner, text="Salvar", width=20, command=salvar).pack(pady=10)

    def tela_buscar(self, frame):
        tk.Label(frame, text="Buscar Conta", font=("Arial", 12, "bold")).pack(pady=8)
        tipo_var = tk.StringVar(value="Pessoal")
        frame_r = tk.Frame(frame); frame_r.pack(pady=4)

        def ao_trocar():
            cb.set(""); cb["values"] = []
            txt_res.config(state="normal"); txt_res.delete("1.0","end"); txt_res.config(state="disabled")

        tk.Radiobutton(frame_r, text="Pessoal", variable=tipo_var, value="Pessoal", command=ao_trocar).pack(side="left", padx=8)
        tk.Radiobutton(frame_r, text="Empresa", variable=tipo_var, value="Corporativa", command=ao_trocar).pack(side="left", padx=8)

        f_busca = tk.Frame(frame); f_busca.pack(pady=4)
        tk.Label(f_busca, text="Nome:").pack(side="left")
        cb = ttk.Combobox(f_busca, width=35); cb.pack(side="left", padx=5)

        txt_res = self._resultado_text(frame, height=8)

        def ao_digitar(e):
            self._busca_dinamica(cb.get(), tipo_var.get(), cb)

        def ao_selecionar(e):
            id_c = extrair_id(cb.get())
            if not id_c: return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    if tipo_var.get() == "Pessoal":
                        cur.execute("SELECT c.EmailConta, p.NomPsso, p.SobnomPsso, p.TtloProfPsso FROM CONTA c JOIN PESSOAL p ON c.IDConta=p.IDConta WHERE c.IDConta=%s;", (id_c,))
                        d = cur.fetchone()
                        info = f"ID: {id_c}\nNome: {d[1]} {d[2]}\nEmail: {d[0]}\nTítulo: {d[3] or 'N/A'}"
                    else:
                        cur.execute("SELECT c.EmailConta, cp.NomComerc, cp.NumFuncEmp, cp.DescriEmp FROM CONTA c JOIN CORPORATIVA cp ON c.IDConta=cp.IDConta WHERE c.IDConta=%s;", (id_c,))
                        d = cur.fetchone()
                        info = f"ID: {id_c}\nEmpresa: {d[1]}\nEmail: {d[0]}\nFuncionários: {d[2]}\nDescrição: {d[3]}"
                    self._exibir(txt_res, info)
            except Error as e:
                self._exibir(txt_res, str(e))
            finally:
                conn.close()

        cb.bind("<KeyRelease>", ao_digitar)
        cb.bind("<<ComboboxSelected>>", ao_selecionar)

    def tela_atualizar(self, frame):
        tk.Label(frame, text="Atualizar Conta", font=("Arial", 12, "bold")).pack(pady=8)
        tipo_var = tk.StringVar(value="Pessoal")
        frame_r = tk.Frame(frame); frame_r.pack(pady=4)

        def ao_trocar():
            cb.set(""); cb["values"] = []
            for w in frame_form.winfo_children(): w.destroy()

        tk.Radiobutton(frame_r, text="Pessoal", variable=tipo_var, value="Pessoal", command=ao_trocar).pack(side="left", padx=8)
        tk.Radiobutton(frame_r, text="Empresa", variable=tipo_var, value="Corporativa", command=ao_trocar).pack(side="left", padx=8)

        f_busca = tk.Frame(frame); f_busca.pack(pady=4)
        tk.Label(f_busca, text="Buscar:").pack(side="left")
        cb = ttk.Combobox(f_busca, width=35); cb.pack(side="left", padx=5)

        frame_form = tk.Frame(frame); frame_form.pack(pady=6, fill="x")

        def ao_digitar(e):
            self._busca_dinamica(cb.get(), tipo_var.get(), cb)

        def ao_selecionar(e):
            for w in frame_form.winfo_children(): w.destroy()
            id_c = extrair_id(cb.get())
            if not id_c: return
            conn = conectar_bd()
            if not conn: return
            ents = {}
            try:
                with conn.cursor() as cur:
                    if tipo_var.get() == "Pessoal":
                        cur.execute("SELECT c.EmailConta, p.NomPsso, p.SobnomPsso, p.TtloProfPsso FROM CONTA c JOIN PESSOAL p ON c.IDConta=p.IDConta WHERE c.IDConta=%s;", (id_c,))
                        d = cur.fetchone()
                        for i, (lbl, val) in enumerate([("Email:", d[0]), ("Nova Senha:", ""), ("Nome:", d[1]), ("Sobrenome:", d[2]), ("Título:", d[3] or "")]):
                            tk.Label(frame_form, text=lbl).grid(row=i, column=0, sticky="e", padx=5, pady=2)
                            e2 = tk.Entry(frame_form, width=30, show="*" if lbl == "Nova Senha:" else "")
                            e2.insert(0, val); e2.grid(row=i, column=1)
                            ents[lbl] = e2
                    else:
                        cur.execute("SELECT c.EmailConta, cp.NomComerc, cp.NumFuncEmp, cp.DescriEmp FROM CONTA c JOIN CORPORATIVA cp ON c.IDConta=cp.IDConta WHERE c.IDConta=%s;", (id_c,))
                        d = cur.fetchone()
                        for i, (lbl, val) in enumerate([("Email:", d[0]), ("Nova Senha:", ""), ("Nome Empresa:", d[1]), ("Nº Funcionários:", str(d[2] or ""))]):
                            tk.Label(frame_form, text=lbl).grid(row=i, column=0, sticky="e", padx=5, pady=2)
                            e2 = tk.Entry(frame_form, width=30, show="*" if lbl == "Nova Senha:" else "")
                            e2.insert(0, val); e2.grid(row=i, column=1)
                            ents[lbl] = e2
                        tk.Label(frame_form, text="Descrição:").grid(row=4, column=0, sticky="ne", padx=5, pady=2)
                        txt_desc = tk.Text(frame_form, width=23, height=4)
                        txt_desc.insert("1.0", d[3] or ""); txt_desc.grid(row=4, column=1)
                        ents["desc"] = txt_desc
            except Error as e:
                messagebox.showerror("Erro", str(e)); return
            finally:
                conn.close()

            lbl_ok = tk.Label(frame_form, text="", fg="green")
            lbl_ok.grid(row=6, column=0, columnspan=2)

            def salvar():
                conn = conectar_bd()
                if not conn: return
                try:
                    with conn.cursor() as cur:
                        cur.execute("UPDATE CONTA SET EmailConta=%s WHERE IDConta=%s;", (ents["Email:"].get(), id_c))
                        if ents["Nova Senha:"].get():
                            cur.execute("UPDATE CONTA SET SenhaConta=%s WHERE IDConta=%s;", (ents["Nova Senha:"].get(), id_c))
                        if tipo_var.get() == "Pessoal":
                            cur.execute("UPDATE PESSOAL SET NomPsso=%s, SobnomPsso=%s, TtloProfPsso=%s WHERE IDConta=%s;",
                                        (ents["Nome:"].get(), ents["Sobrenome:"].get(), ents["Título:"].get(), id_c))
                        else:
                            cur.execute("UPDATE CORPORATIVA SET NomComerc=%s, NumFuncEmp=%s, DescriEmp=%s WHERE IDConta=%s;",
                                        (ents["Nome Empresa:"].get(), ents["Nº Funcionários:"].get(),
                                         ents["desc"].get("1.0","end-1c"), id_c))
                    conn.commit(); lbl_ok.config(text="✔ Conta atualizada!")
                except Error as e:
                    conn.rollback(); messagebox.showerror("Erro", str(e))
                finally:
                    conn.close()

            tk.Button(frame_form, text="Salvar Alterações", width=20, command=salvar).grid(row=5, column=0, columnspan=2, pady=10)

        cb.bind("<KeyRelease>", ao_digitar)
        cb.bind("<<ComboboxSelected>>", ao_selecionar)

    def tela_deletar(self, frame):
        tk.Label(frame, text="Deletar Conta", font=("Arial", 12, "bold")).pack(pady=8)
        tipo_var = tk.StringVar(value="Pessoal")
        frame_r = tk.Frame(frame); frame_r.pack(pady=4)

        def ao_trocar():
            cb.set(""); cb["values"] = []
            frame_info.pack_forget()

        tk.Radiobutton(frame_r, text="Pessoal", variable=tipo_var, value="Pessoal", command=ao_trocar).pack(side="left", padx=8)
        tk.Radiobutton(frame_r, text="Empresa", variable=tipo_var, value="Corporativa", command=ao_trocar).pack(side="left", padx=8)

        f_busca = tk.Frame(frame); f_busca.pack(pady=4)
        tk.Label(f_busca, text="Buscar:").pack(side="left")
        cb = ttk.Combobox(f_busca, width=35); cb.pack(side="left", padx=5)

        frame_info = tk.Frame(frame)
        lbl_info = tk.Label(frame_info, text=""); lbl_info.pack(pady=6)

        def confirmar():
            id_c = extrair_id(cb.get())
            if not id_c: return
            if messagebox.askyesno("Aviso Crítico","Deletar permanentemente esta conta e todos os dados?"):
                conn = conectar_bd()
                if not conn: return
                try:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM CONTA WHERE IDConta=%s;", (id_c,))
                    conn.commit()
                    lbl_info.config(text="✔ Conta deletada!", fg="green")
                    btn_del.pack_forget(); cb.set("")
                except Error as e:
                    conn.rollback(); messagebox.showerror("Erro", str(e))
                finally:
                    conn.close()

        btn_del = tk.Button(frame_info, text="Deletar Conta", width=18, bg="red", fg="white", command=confirmar)

        def ao_digitar(e):
            self._busca_dinamica(cb.get(), tipo_var.get(), cb)

        def ao_selecionar(e):
            frame_info.pack(fill="x", pady=6)
            lbl_info.config(text=f"Pronto para deletar: {cb.get()}", fg="black")
            btn_del.pack(pady=4)

        cb.bind("<KeyRelease>", ao_digitar)
        cb.bind("<<ComboboxSelected>>", ao_selecionar)


# ════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()