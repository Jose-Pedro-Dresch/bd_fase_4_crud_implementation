import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from psycopg2 import Error
from datetime import date

# Configurações de conexão
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
        messagebox.showerror("Erro Crítico", f"Falha de conexão com o banco: {e}\n\nVerifique as configurações de conexão.")
        return None

def tela_configuracao(root):
    janela = tk.Toplevel(root)
    janela.title("Configuração do Banco de Dados")
    janela.geometry("350x280")
    janela.resizable(False, False)
    janela.grab_set()

    tk.Label(janela, text="Configuração de Conexão", font=("Arial", 11, "bold")).pack(pady=10)
    frame = tk.Frame(janela)
    frame.pack(pady=5)

    campos = [("Host:", "host"), ("Porta:", "port"), ("Banco de Dados:", "dbname"),
              ("Usuário:", "user"), ("Senha:", "password")]
    entradas = {}

    for i, (label, chave) in enumerate(campos):
        tk.Label(frame, text=label, anchor="e", width=15).grid(row=i, column=0, padx=5, pady=4, sticky="e")
        show = "*" if chave == "password" else ""
        ent = tk.Entry(frame, width=25, show=show)
        ent.insert(0, DB_CONFIG.get(chave, ""))
        ent.grid(row=i, column=1, pady=4)
        entradas[chave] = ent

    lbl_status = tk.Label(janela, text="", fg="gray")
    lbl_status.pack()

    def salvar_e_testar():
        for chave, ent in entradas.items():
            DB_CONFIG[chave] = ent.get()
        conn = conectar_bd()
        if conn:
            lbl_status.config(text="✔ Conexão bem-sucedida!", fg="green")
            conn.close()
        else:
            lbl_status.config(text="✘ Falha na conexão. Verifique os dados.", fg="red")

    frame_btn = tk.Frame(janela)
    frame_btn.pack(pady=10)
    tk.Button(frame_btn, text="Testar e Salvar", width=18, command=salvar_e_testar).pack(side="left", padx=5)
    tk.Button(frame_btn, text="Fechar", width=10, command=janela.destroy).pack(side="left", padx=5)


# ─────────────────────────── helpers ───────────────────────────

def extrair_id(selecao_combobox):
    try:
        return int(selecao_combobox.split(" - ")[0])
    except (ValueError, IndexError):
        return None

def buscar_combo(cur, query, params=()):
    cur.execute(query, params)
    return [f"{row[0]} - {row[1]}" for row in cur.fetchall()]

def label_entry(frame, texto, row, width=28, show=""):
    tk.Label(frame, text=texto).grid(row=row, column=0, sticky="e", padx=5, pady=2)
    ent = tk.Entry(frame, width=width, show=show)
    ent.grid(row=row, column=1, pady=2)
    return ent

def label_combo(frame, texto, row, width=26):
    tk.Label(frame, text=texto).grid(row=row, column=0, sticky="e", padx=5, pady=2)
    cb = ttk.Combobox(frame, width=width, state="readonly")
    cb.grid(row=row, column=1, pady=2)
    return cb

def label_text(frame, texto, row, width=22, height=3):
    tk.Label(frame, text=texto).grid(row=row, column=0, sticky="ne", padx=5, pady=2)
    txt = tk.Text(frame, width=width, height=height)
    txt.grid(row=row, column=1, pady=2)
    return txt

def salvar_btn(frame, row, cmd, texto="Salvar"):
    tk.Button(frame, text=texto, width=20, command=cmd).grid(row=row, column=0, columnspan=2, pady=10)

def scroll_frame(parent):
    """Retorna (container_externo, frame_interno_rolável)."""
    container = tk.Frame(parent)
    canvas = tk.Canvas(container)
    sb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return container, inner


# ════════════════════════════════════════════════════════════════
#  MÓDULOS CRUD por entidade
# ════════════════════════════════════════════════════════════════

# ── POST ────────────────────────────────────────────────────────

class PostCRUD:
    NIVEIS = ["Publico", "Conexoes", "Privado"]

    @staticmethod
    def _buscar_contas(conn):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT IDConta,
                       COALESCE((SELECT NomPsso||' '||SobnomPsso FROM PESSOAL p WHERE p.IDConta=c.IDConta),
                                (SELECT NomComerc FROM CORPORATIVA cp WHERE cp.IDConta=c.IDConta),
                                c.EmailConta) AS nome
                FROM CONTA c ORDER BY nome;
            """)
            return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Criar Post")
        jan.geometry("440x320")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0)
        cb_conta["values"] = contas

        tk.Label(f, text="Conteúdo:").grid(row=1, column=0, sticky="ne", padx=5, pady=2)
        txt_conteudo = tk.Text(f, width=28, height=5)
        txt_conteudo.grid(row=1, column=1, pady=2)

        tk.Label(f, text="Nível Visib.:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        cb_nivel = ttk.Combobox(f, values=PostCRUD.NIVEIS, state="readonly", width=26)
        cb_nivel.current(0)
        cb_nivel.grid(row=2, column=1, pady=2)

        def salvar():
            id_conta = extrair_id(cb_conta.get())
            conteudo = txt_conteudo.get("1.0", "end-1c").strip()
            nivel = cb_nivel.get()
            if not id_conta or not conteudo:
                messagebox.showerror("Erro", "Preencha todos os campos."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO POST (DtPubliPost, ConteudoPost, NivelVisib, IDConta) VALUES (CURRENT_DATE,%s,%s,%s);",
                                (conteudo, nivel, id_conta))
                conn.commit()
                messagebox.showinfo("Sucesso", "Post criado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 3, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Buscar Post")
        jan.geometry("460x400")
        f_top = tk.Frame(jan); f_top.pack(pady=8)

        tk.Label(f_top, text="ID do Post:").pack(side="left")
        ent_id = tk.Entry(f_top, width=10); ent_id.pack(side="left", padx=5)

        txt_res = tk.Text(jan, width=55, height=12, state="disabled")
        txt_res.pack(pady=5)

        tk.Label(jan, text="Ou listar por Conta (ID):").pack()
        f_bot = tk.Frame(jan); f_bot.pack(pady=4)
        ent_conta = tk.Entry(f_bot, width=10); ent_conta.pack(side="left", padx=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    id_post = ent_id.get().strip()
                    id_conta = ent_conta.get().strip()
                    if id_post:
                        cur.execute("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST WHERE IDPost=%s;", (id_post,))
                    elif id_conta:
                        cur.execute("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST WHERE IDConta=%s ORDER BY DtPubliPost DESC;", (id_conta,))
                    else:
                        cur.execute("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST ORDER BY DtPubliPost DESC LIMIT 20;")
                    rows = cur.fetchall()
                    if not rows:
                        txt_res.insert("end", "Nenhum resultado."); return
                    for r in rows:
                        txt_res.insert("end", f"ID:{r[0]}  Data:{r[1]}  Nível:{r[2]}  Conta:{r[4]}\n{r[3]}\n{'─'*50}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close()
                txt_res.config(state="disabled")

        tk.Button(f_top, text="Buscar", command=buscar).pack(side="left")
        tk.Button(f_bot, text="Listar", command=buscar).pack(side="left")

    @staticmethod
    def tela_atualizar(root):
        jan = tk.Toplevel(root)
        jan.title("Atualizar Post")
        jan.geometry("440x260")
        f = tk.Frame(jan); f.pack(pady=10)

        ent_id = label_entry(f, "ID do Post:", 0, width=10)
        lbl_atual = tk.Label(f, text=""); lbl_atual.grid(row=1, column=0, columnspan=2)
        tk.Label(f, text="Novo Conteúdo:").grid(row=2, column=0, sticky="ne", padx=5, pady=2)
        txt_novo = tk.Text(f, width=28, height=4); txt_novo.grid(row=2, column=1, pady=2)
        tk.Label(f, text="Novo Nível:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        cb_nivel = ttk.Combobox(f, values=PostCRUD.NIVEIS, state="readonly", width=26)
        cb_nivel.current(0); cb_nivel.grid(row=3, column=1, pady=2)

        def carregar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT ConteudoPost, NivelVisib FROM POST WHERE IDPost=%s;", (ent_id.get(),))
                    row = cur.fetchone()
                    if not row: lbl_atual.config(text="Post não encontrado."); return
                    txt_novo.delete("1.0","end"); txt_novo.insert("1.0", row[0])
                    cb_nivel.set(row[1]); lbl_atual.config(text="Post carregado.")
            finally:
                conn.close()

        def salvar():
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE POST SET ConteudoPost=%s, NivelVisib=%s WHERE IDPost=%s;",
                                (txt_novo.get("1.0","end-1c"), cb_nivel.get(), ent_id.get()))
                conn.commit(); messagebox.showinfo("Sucesso","Post atualizado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        tk.Button(f, text="Carregar", command=carregar).grid(row=0, column=2, padx=5)
        salvar_btn(f, 4, salvar)

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Deletar Post")
        jan.geometry("350x150")
        f = tk.Frame(jan); f.pack(pady=15)
        ent_id = label_entry(f, "ID do Post:", 0, width=10)

        def deletar():
            if not messagebox.askyesno("Confirmar", "Deletar este post e seus comentários/reações?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM POST WHERE IDPost=%s;", (ent_id.get(),))
                conn.commit(); messagebox.showinfo("Sucesso","Post deletado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, deletar, "Deletar")


# ── COMENTARIO ──────────────────────────────────────────────────

class ComentarioCRUD:
    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Criar Comentário")
        jan.geometry("420x260")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDPost, LEFT(ConteudoPost,40) FROM POST ORDER BY IDPost DESC;")
                posts = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_post  = label_combo(f, "Post:", 1);  cb_post["values"] = posts
        tk.Label(f, text="Conteúdo:").grid(row=2, column=0, sticky="ne", padx=5, pady=2)
        txt = tk.Text(f, width=26, height=4); txt.grid(row=2, column=1, pady=2)

        def salvar():
            id_conta = extrair_id(cb_conta.get())
            id_post  = extrair_id(cb_post.get())
            conteudo = txt.get("1.0","end-1c").strip()
            if not id_conta or not id_post or not conteudo:
                messagebox.showerror("Erro","Preencha todos os campos."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO COMENTARIO (ConteudoTxtCom, DtPubliCom, IDPost, IDConta) VALUES (%s, CURRENT_DATE, %s, %s);",
                                (conteudo, id_post, id_conta))
                conn.commit(); messagebox.showinfo("Sucesso","Comentário criado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 3, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Buscar Comentários")
        jan.geometry("460x360")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID do Post:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=55, height=12, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDComentario, DtPubliCom, IDConta, ConteudoTxtCom FROM COMENTARIO WHERE IDPost=%s ORDER BY DtPubliCom;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhum comentário."); return
                    for r in rows:
                        txt_res.insert("end", f"#{r[0]}  {r[1]}  Conta:{r[2]}\n{r[3]}\n{'─'*50}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Deletar Comentário")
        jan.geometry("350x150")
        f = tk.Frame(jan); f.pack(pady=15)
        ent = label_entry(f, "ID do Comentário:", 0, width=10)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar este comentário?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM COMENTARIO WHERE IDComentario=%s;", (ent.get(),))
                conn.commit(); messagebox.showinfo("Sucesso","Comentário deletado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, deletar, "Deletar")


# ── REAGEPOST ───────────────────────────────────────────────────

class ReagePostCRUD:
    TIPOS = ["Curtir", "Celebrar", "Apoiar", "Interessante", "Curioso"]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Reagir a Post")
        jan.geometry("420x220")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDPost, LEFT(ConteudoPost,40) FROM POST ORDER BY IDPost DESC;")
                posts = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_post  = label_combo(f, "Post:", 1);  cb_post["values"] = posts
        tk.Label(f, text="Tipo Reação:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        cb_tipo = ttk.Combobox(f, values=ReagePostCRUD.TIPOS, state="readonly", width=26)
        cb_tipo.current(0); cb_tipo.grid(row=2, column=1, pady=2)

        def salvar():
            id_conta = extrair_id(cb_conta.get())
            id_post  = extrair_id(cb_post.get())
            tipo     = cb_tipo.get()
            if not id_conta or not id_post:
                messagebox.showerror("Erro","Selecione conta e post."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO REAGEPOST (IDConta, IDPost, DtReacao, TipoReacao) VALUES (%s,%s,CURRENT_DATE,%s) ON CONFLICT (IDConta,IDPost) DO UPDATE SET TipoReacao=%s, DtReacao=CURRENT_DATE;",
                                (id_conta, id_post, tipo, tipo))
                conn.commit(); messagebox.showinfo("Sucesso","Reação registrada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 3, salvar, "Reagir")

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Ver Reações")
        jan.geometry("460x340")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID do Post:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=55, height=10, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDConta, TipoReacao, DtReacao FROM REAGEPOST WHERE IDPost=%s ORDER BY DtReacao DESC;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma reação."); return
                    for r in rows:
                        txt_res.insert("end", f"Conta:{r[0]}  Tipo:{r[1]}  Data:{r[2]}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Remover Reação")
        jan.geometry("380x180")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDPost, LEFT(ConteudoPost,40) FROM POST ORDER BY IDPost DESC;")
                posts = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_post  = label_combo(f, "Post:", 1);  cb_post["values"] = posts

        def deletar():
            id_conta = extrair_id(cb_conta.get()); id_post = extrair_id(cb_post.get())
            if not id_conta or not id_post: messagebox.showerror("Erro","Selecione conta e post."); return
            if not messagebox.askyesno("Confirmar","Remover reação?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM REAGEPOST WHERE IDConta=%s AND IDPost=%s;", (id_conta, id_post))
                conn.commit(); messagebox.showinfo("Sucesso","Reação removida!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, deletar, "Remover")


# ── VAGAEMPREGO ─────────────────────────────────────────────────

class VagaCRUD:
    FORMATOS = ["Presencial", "Remoto", "Hibrido"]

    @staticmethod
    def _buscar_corporativas(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT IDConta, NomComerc FROM CORPORATIVA ORDER BY NomComerc;")
            return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Criar Vaga de Emprego")
        jan.geometry("440x360")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            corps = VagaCRUD._buscar_corporativas(conn)
        finally:
            conn.close()

        cb_emp = label_combo(f, "Empresa:", 0); cb_emp["values"] = corps
        ent_titulo = label_entry(f, "Título:", 1)
        tk.Label(f, text="Descrição:").grid(row=2, column=0, sticky="ne", padx=5, pady=2)
        txt_desc = tk.Text(f, width=26, height=4); txt_desc.grid(row=2, column=1, pady=2)
        tk.Label(f, text="Formato:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        cb_fmt = ttk.Combobox(f, values=VagaCRUD.FORMATOS, state="readonly", width=26)
        cb_fmt.current(0); cb_fmt.grid(row=3, column=1, pady=2)

        def salvar():
            id_emp = extrair_id(cb_emp.get())
            titulo = ent_titulo.get().strip()
            if not id_emp or not titulo:
                messagebox.showerror("Erro","Preencha empresa e título."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO VAGAEMPREGO (TtloVaga, DescriVaga, FormatoTrabVaga, DtCrcaoVaga, IDConta) VALUES (%s,%s,%s,CURRENT_DATE,%s);",
                                (titulo, txt_desc.get("1.0","end-1c"), cb_fmt.get(), id_emp))
                conn.commit(); messagebox.showinfo("Sucesso","Vaga criada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 4, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Buscar Vagas")
        jan.geometry("480x420")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="Título (parcial):").pack(side="left")
        ent = tk.Entry(f, width=20); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=58, height=14, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    termo = ent.get().strip()
                    if termo:
                        cur.execute("SELECT v.IDVagaEmo, v.TtloVaga, v.FormatoTrabVaga, v.DtCrcaoVaga, c.NomComerc FROM VAGAEMPREGO v JOIN CORPORATIVA c ON v.IDConta=c.IDConta WHERE v.TtloVaga ILIKE %s ORDER BY v.DtCrcaoVaga DESC;",
                                    (f"%{termo}%",))
                    else:
                        cur.execute("SELECT v.IDVagaEmo, v.TtloVaga, v.FormatoTrabVaga, v.DtCrcaoVaga, c.NomComerc FROM VAGAEMPREGO v JOIN CORPORATIVA c ON v.IDConta=c.IDConta ORDER BY v.DtCrcaoVaga DESC LIMIT 20;")
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma vaga encontrada."); return
                    for r in rows:
                        txt_res.insert("end", f"ID:{r[0]}  {r[1]}  [{r[2]}]  {r[3]}\nEmpresa: {r[4]}\n{'─'*50}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Deletar Vaga")
        jan.geometry("350x150")
        f = tk.Frame(jan); f.pack(pady=15)
        ent = label_entry(f, "ID da Vaga:", 0, width=10)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar esta vaga e suas aplicações?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM VAGAEMPREGO WHERE IDVagaEmo=%s;", (ent.get(),))
                conn.commit(); messagebox.showinfo("Sucesso","Vaga deletada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, deletar, "Deletar")


# ── APLICAVAGA ──────────────────────────────────────────────────

class AplicaVagaCRUD:
    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Aplicar a Vaga")
        jan.geometry("440x240")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDVagaEmo, TtloVaga FROM VAGAEMPREGO ORDER BY TtloVaga;")
                vagas = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_conta = label_combo(f, "Candidato (Conta):", 0); cb_conta["values"] = contas
        cb_vaga  = label_combo(f, "Vaga:", 1);              cb_vaga["values"] = vagas
        tk.Label(f, text="Site/URL:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ent_site = tk.Entry(f, width=28); ent_site.grid(row=2, column=1, pady=2)

        def salvar():
            id_conta = extrair_id(cb_conta.get()); id_vaga = extrair_id(cb_vaga.get())
            if not id_conta or not id_vaga:
                messagebox.showerror("Erro","Selecione conta e vaga."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO APLICAAVAGA (IDVagaEmo, DtAplicao, SitusAplicao, IDConta) VALUES (%s, CURRENT_DATE, %s, %s);",
                                (id_vaga, ent_site.get() or None, id_conta))
                conn.commit(); messagebox.showinfo("Sucesso","Aplicação registrada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 3, salvar, "Aplicar")

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Buscar Aplicações")
        jan.geometry("480x380")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID da Vaga:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=58, height=12, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    id_vaga = ent.get().strip()
                    if id_vaga:
                        cur.execute("SELECT a.IDVagaEmo, a.IDConta, a.DtAplicao, a.SitusAplicao FROM APLICAAVAGA a WHERE a.IDVagaEmo=%s ORDER BY a.DtAplicao;",
                                    (id_vaga,))
                    else:
                        cur.execute("SELECT a.IDVagaEmo, a.IDConta, a.DtAplicao, a.SitusAplicao FROM APLICAAVAGA a ORDER BY a.DtAplicao DESC LIMIT 30;")
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma aplicação."); return
                    for r in rows:
                        txt_res.insert("end", f"Vaga:{r[0]}  Conta:{r[1]}  Data:{r[2]}  Site:{r[3] or '-'}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")


# ── COMPETENCIA ─────────────────────────────────────────────────

class CompetenciaCRUD:
    @staticmethod
    def _todas(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT IDComp, NomeComp FROM COMPETENCIA ORDER BY NomeComp;")
            return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Criar Competência")
        jan.geometry("380x150")
        f = tk.Frame(jan); f.pack(pady=15)
        ent = label_entry(f, "Nome:", 0)

        def salvar():
            nome = ent.get().strip()
            if not nome: messagebox.showerror("Erro","Preencha o nome."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO COMPETENCIA (NomeComp) VALUES (%s);", (nome,))
                conn.commit(); messagebox.showinfo("Sucesso","Competência criada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Listar Competências")
        jan.geometry("400x340")
        txt_res = tk.Text(jan, width=50, height=14, state="disabled"); txt_res.pack(pady=10)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDComp, NomeComp FROM COMPETENCIA ORDER BY NomeComp;")
                    for r in cur.fetchall():
                        txt_res.insert("end", f"{r[0]} - {r[1]}\n")
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(jan, text="Atualizar Lista", command=buscar).pack()
        buscar()

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Deletar Competência")
        jan.geometry("380x160")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            comps = CompetenciaCRUD._todas(conn)
        finally:
            conn.close()

        cb = label_combo(f, "Competência:", 0); cb["values"] = comps

        def deletar():
            id_comp = extrair_id(cb.get())
            if not id_comp: return
            if not messagebox.askyesno("Confirmar","Deletar competência?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM COMPETENCIA WHERE IDComp=%s;", (id_comp,))
                conn.commit(); messagebox.showinfo("Sucesso","Competência deletada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, deletar, "Deletar")


# ── POSSCOMP (Competências da Conta) ────────────────────────────

class PossCompCRUD:
    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Adicionar Competência à Conta")
        jan.geometry("420x200")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
            comps  = CompetenciaCRUD._todas(conn)
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_comp  = label_combo(f, "Competência:", 1); cb_comp["values"] = comps

        def salvar():
            id_conta = extrair_id(cb_conta.get()); id_comp = extrair_id(cb_comp.get())
            if not id_conta or not id_comp:
                messagebox.showerror("Erro","Selecione conta e competência."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO POSSCOMP (IDComp, IDConta) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_comp, id_conta))
                conn.commit(); messagebox.showinfo("Sucesso","Competência vinculada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, salvar, "Vincular")

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Competências da Conta")
        jan.geometry("460x360")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=55, height=12, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT c.IDComp, c.NomeComp FROM POSSCOMP pc JOIN COMPETENCIA c ON pc.IDComp=c.IDComp WHERE pc.IDConta=%s ORDER BY c.NomeComp;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma competência."); return
                    for r in rows:
                        txt_res.insert("end", f"{r[0]} - {r[1]}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Remover Competência da Conta")
        jan.geometry("420x200")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
            comps  = CompetenciaCRUD._todas(conn)
        finally:
            conn.close()

        cb_conta = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        cb_comp  = label_combo(f, "Competência:", 1); cb_comp["values"] = comps

        def deletar():
            id_conta = extrair_id(cb_conta.get()); id_comp = extrair_id(cb_comp.get())
            if not id_conta or not id_comp: return
            if not messagebox.askyesno("Confirmar","Remover vínculo?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM POSSCOMP WHERE IDComp=%s AND IDConta=%s;", (id_comp, id_conta))
                conn.commit(); messagebox.showinfo("Sucesso","Vínculo removido!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, deletar, "Remover")


# ── EXPERIENCIAPROF ─────────────────────────────────────────────

class ExpProfCRUD:
    TIPOS_EMP = ["CLT", "PJ", "Freelancer", "Estagio", "Temporario"]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Criar Experiência Profissional")
        jan.geometry("460x400")
        cont, inner = scroll_frame(jan)
        cont.pack(fill="both", expand=True)
        f = inner

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
            corps  = VagaCRUD._buscar_corporativas(conn)
        finally:
            conn.close()

        cb_conta  = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        ent_titulo= label_entry(f, "Título:", 1)
        tk.Label(f, text="Tipo Emprego:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        cb_tipo = ttk.Combobox(f, values=ExpProfCRUD.TIPOS_EMP, state="readonly", width=26)
        cb_tipo.current(0); cb_tipo.grid(row=2, column=1, pady=2)
        ent_inicio = label_entry(f, "Dt Início (AAAA-MM-DD):", 3)
        ent_fim    = label_entry(f, "Dt Fim (ou vazio):", 4)
        txt_desc   = label_text(f, "Descrição:", 5)
        cb_emp     = label_combo(f, "Empresa (opcional):", 6); cb_emp["values"] = [""] + corps

        def salvar():
            id_conta = extrair_id(cb_conta.get()); titulo = ent_titulo.get().strip()
            if not id_conta or not titulo:
                messagebox.showerror("Erro","Preencha conta e título."); return
            id_emp = extrair_id(cb_emp.get()) if cb_emp.get() else None
            fim = ent_fim.get().strip() or None
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO EXPERIENCIAPROF (TituloExp, TipoEmpregoExp, DtInicioExp, DtFimExp, DescAtv, IDUsr, IDEmp) VALUES (%s,%s,%s,%s,%s,%s,%s);",
                                (titulo, cb_tipo.get(), ent_inicio.get(), fim,
                                 txt_desc.get("1.0","end-1c"), id_conta, id_emp))
                conn.commit(); messagebox.showinfo("Sucesso","Experiência criada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 7, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Buscar Experiências")
        jan.geometry("480x400")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=58, height=14, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT e.IDExp, e.TituloExp, e.TipoEmpregoExp, e.DtInicioExp, e.DtFimExp, COALESCE(c.NomComerc,'') FROM EXPERIENCIAPROF e LEFT JOIN CORPORATIVA c ON e.IDEmp=c.IDConta WHERE e.IDUsr=%s ORDER BY e.DtInicioExp DESC;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma experiência."); return
                    for r in rows:
                        txt_res.insert("end", f"#{r[0]}  {r[1]}  [{r[2]}]\n  {r[3]} → {r[4] or 'atual'}  Empresa:{r[5]}\n{'─'*50}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Deletar Experiência")
        jan.geometry("350x150")
        f = tk.Frame(jan); f.pack(pady=15)
        ent = label_entry(f, "ID Experiência:", 0, width=10)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar experiência?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM EXPERIENCIAPROF WHERE IDExp=%s;", (ent.get(),))
                conn.commit(); messagebox.showinfo("Sucesso","Experiência deletada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, deletar, "Deletar")


# ── EXPPOSSCOMP (Competências de Experiência) ───────────────────

class ExpPossCompCRUD:
    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Vincular Competência a Experiência")
        jan.geometry("420x200")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            comps = CompetenciaCRUD._todas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDExp, TituloExp FROM EXPERIENCIAPROF ORDER BY TituloExp;")
                exps = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_exp  = label_combo(f, "Experiência:", 0); cb_exp["values"] = exps
        cb_comp = label_combo(f, "Competência:", 1); cb_comp["values"] = comps

        def salvar():
            id_exp = extrair_id(cb_exp.get()); id_comp = extrair_id(cb_comp.get())
            if not id_exp or not id_comp:
                messagebox.showerror("Erro","Selecione experiência e competência."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO EXPPOSSCOMP (IDComp, IDExp) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_comp, id_exp))
                conn.commit(); messagebox.showinfo("Sucesso","Vínculo criado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, salvar, "Vincular")

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Competências por Experiência")
        jan.geometry("460x340")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID Experiência:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=55, height=10, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT c.IDComp, c.NomeComp FROM EXPPOSSCOMP ec JOIN COMPETENCIA c ON ec.IDComp=c.IDComp WHERE ec.IDExp=%s;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma."); return
                    for r in rows: txt_res.insert("end", f"{r[0]} - {r[1]}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")


# ── FORMACAOACAD ─────────────────────────────────────────────────

class FormacaoCRUD:
    GRAUS = ["Fundamental", "Medio", "Tecnico", "Graduacao", "Pos-graduacao", "Mestrado", "Doutorado"]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Criar Formação Acadêmica")
        jan.geometry("460x340")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
        finally:
            conn.close()

        cb_conta  = label_combo(f, "Conta:", 0); cb_conta["values"] = contas
        ent_inst  = label_entry(f, "Instituição:", 1)
        tk.Label(f, text="Grau:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        cb_grau = ttk.Combobox(f, values=FormacaoCRUD.GRAUS, state="readonly", width=26)
        cb_grau.current(3); cb_grau.grid(row=2, column=1, pady=2)
        ent_area  = label_entry(f, "Área:", 3)
        ent_ini   = label_entry(f, "Dt Início (AAAA-MM-DD):", 4)
        ent_fim   = label_entry(f, "Dt Fim (ou vazio):", 5)

        def salvar():
            id_conta = extrair_id(cb_conta.get()); inst = ent_inst.get().strip()
            if not id_conta or not inst:
                messagebox.showerror("Erro","Preencha conta e instituição."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO FORMACAOACAD (NomInstlForm, GrauForm, AreaForm, DtInicioForm, DtFimForm, IDConta) VALUES (%s,%s,%s,%s,%s,%s);",
                                (inst, cb_grau.get(), ent_area.get() or None,
                                 ent_ini.get() or None, ent_fim.get() or None, id_conta))
                conn.commit(); messagebox.showinfo("Sucesso","Formação criada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 6, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Buscar Formações")
        jan.geometry("480x380")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=58, height=12, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDForm, NomInstlForm, GrauForm, AreaForm, DtInicioForm, DtFimForm FROM FORMACAOACAD WHERE IDConta=%s ORDER BY DtInicioForm DESC;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma formação."); return
                    for r in rows:
                        txt_res.insert("end", f"#{r[0]}  {r[1]}  [{r[2]}]  Área:{r[3] or '-'}\n  {r[4]} → {r[5] or 'atual'}\n{'─'*50}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Deletar Formação")
        jan.geometry("350x150")
        f = tk.Frame(jan); f.pack(pady=15)
        ent = label_entry(f, "ID Formação:", 0, width=10)

        def deletar():
            if not messagebox.askyesno("Confirmar","Deletar formação?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM FORMACAOACAD WHERE IDForm=%s;", (ent.get(),))
                conn.commit(); messagebox.showinfo("Sucesso","Formação deletada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, deletar, "Deletar")


# ── FORMPOSSCOMP (Competências de Formação) ─────────────────────

class FormPossCompCRUD:
    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Vincular Competência a Formação")
        jan.geometry("420x200")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            comps = CompetenciaCRUD._todas(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT IDForm, NomInstlForm FROM FORMACAOACAD ORDER BY NomInstlForm;")
                forms = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        finally:
            conn.close()

        cb_form = label_combo(f, "Formação:", 0); cb_form["values"] = forms
        cb_comp = label_combo(f, "Competência:", 1); cb_comp["values"] = comps

        def salvar():
            id_form = extrair_id(cb_form.get()); id_comp = extrair_id(cb_comp.get())
            if not id_form or not id_comp:
                messagebox.showerror("Erro","Selecione formação e competência."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO FORMPOSSCOMP (IDComp, IDForm) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_comp, id_form))
                conn.commit(); messagebox.showinfo("Sucesso","Vínculo criado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, salvar, "Vincular")

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Competências por Formação")
        jan.geometry("460x320")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID Formação:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=55, height=10, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT c.IDComp, c.NomeComp FROM FORMPOSSCOMP fc JOIN COMPETENCIA c ON fc.IDComp=c.IDComp WHERE fc.IDForm=%s;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma."); return
                    for r in rows: txt_res.insert("end", f"{r[0]} - {r[1]}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")


# ── IDIOMA ───────────────────────────────────────────────────────

class IdiomaCRUD:
    @staticmethod
    def _todos(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT IDIdioma, NomeIdioma FROM IDIOMA ORDER BY NomeIdioma;")
            return [f"{r[0]} - {r[1]}" for r in cur.fetchall()]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Cadastrar Idioma")
        jan.geometry("380x150")
        f = tk.Frame(jan); f.pack(pady=15)
        ent = label_entry(f, "Nome:", 0)

        def salvar():
            nome = ent.get().strip()
            if not nome: messagebox.showerror("Erro","Preencha o nome."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO IDIOMA (NomeIdioma) VALUES (%s);", (nome,))
                conn.commit(); messagebox.showinfo("Sucesso","Idioma cadastrado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 1, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Listar Idiomas")
        jan.geometry("380x300")
        txt_res = tk.Text(jan, width=45, height=12, state="disabled"); txt_res.pack(pady=10)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDIdioma, NomeIdioma FROM IDIOMA ORDER BY NomeIdioma;")
                    for r in cur.fetchall():
                        txt_res.insert("end", f"{r[0]} - {r[1]}\n")
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(jan, text="Atualizar Lista", command=buscar).pack()
        buscar()


# ── FALAIDIOM ────────────────────────────────────────────────────

class FalaIdiomCRUD:
    NIVEIS = ["Basico", "Intermediario", "Avancado", "Fluente", "Nativo"]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Vincular Idioma à Conta")
        jan.geometry("420x220")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas  = PostCRUD._buscar_contas(conn)
            idiomas = IdiomaCRUD._todos(conn)
        finally:
            conn.close()

        cb_conta  = label_combo(f, "Conta:", 0);  cb_conta["values"] = contas
        cb_idioma = label_combo(f, "Idioma:", 1); cb_idioma["values"] = idiomas
        tk.Label(f, text="Nível Profic.:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        cb_nivel = ttk.Combobox(f, values=FalaIdiomCRUD.NIVEIS, state="readonly", width=26)
        cb_nivel.current(0); cb_nivel.grid(row=2, column=1, pady=2)

        def salvar():
            id_conta  = extrair_id(cb_conta.get()); id_idioma = extrair_id(cb_idioma.get())
            if not id_conta or not id_idioma:
                messagebox.showerror("Erro","Selecione conta e idioma."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO FALAIDIOM (IDIdioma, NvlProfic, IDConta) VALUES (%s,%s,%s) ON CONFLICT (IDIdioma, IDConta) DO UPDATE SET NvlProfic=%s;",
                                (id_idioma, cb_nivel.get(), id_conta, cb_nivel.get()))
                conn.commit(); messagebox.showinfo("Sucesso","Idioma vinculado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 3, salvar, "Vincular")

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Idiomas da Conta")
        jan.geometry("460x320")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=55, height=10, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT i.IDIdioma, i.NomeIdioma, fi.NvlProfic FROM FALAIDIOM fi JOIN IDIOMA i ON fi.IDIdioma=i.IDIdioma WHERE fi.IDConta=%s ORDER BY i.NomeIdioma;",
                                (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhum idioma vinculado."); return
                    for r in rows: txt_res.insert("end", f"{r[0]} - {r[1]}  Nível: {r[2]}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Remover Idioma da Conta")
        jan.geometry("420x200")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas  = PostCRUD._buscar_contas(conn)
            idiomas = IdiomaCRUD._todos(conn)
        finally:
            conn.close()

        cb_conta  = label_combo(f, "Conta:", 0);  cb_conta["values"] = contas
        cb_idioma = label_combo(f, "Idioma:", 1); cb_idioma["values"] = idiomas

        def deletar():
            id_conta = extrair_id(cb_conta.get()); id_idioma = extrair_id(cb_idioma.get())
            if not id_conta or not id_idioma: return
            if not messagebox.askyesno("Confirmar","Remover vínculo?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM FALAIDIOM WHERE IDIdioma=%s AND IDConta=%s;", (id_idioma, id_conta))
                conn.commit(); messagebox.showinfo("Sucesso","Vínculo removido!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, deletar, "Remover")


# ── CONEXAO ──────────────────────────────────────────────────────

class ConexaoCRUD:
    STATUS = ["Pendente", "Aceita", "Recusada"]

    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Enviar Solicitação de Conexão")
        jan.geometry("420x200")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            contas = PostCRUD._buscar_contas(conn)
        finally:
            conn.close()

        cb_de  = label_combo(f, "De (Conta):", 0); cb_de["values"] = contas
        cb_para = label_combo(f, "Para (Conta):", 1); cb_para["values"] = contas

        def salvar():
            id_de   = extrair_id(cb_de.get()); id_para = extrair_id(cb_para.get())
            if not id_de or not id_para or id_de == id_para:
                messagebox.showerror("Erro","Selecione duas contas distintas."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO CONEXAO (DtEnvConv, StatusConexao, IDConta_3, IDConta_2) VALUES (CURRENT_DATE, 'Pendente', %s, %s);",
                                (id_de, id_para))
                conn.commit(); messagebox.showinfo("Sucesso","Solicitação enviada!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, salvar, "Enviar")

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Buscar Conexões")
        jan.geometry("500x380")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID da Conta:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=60, height=12, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            id_conta = ent.get().strip()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDConta_3, IDConta_2, DtEnvConv, DtAceitConv, StatusConexao FROM CONEXAO WHERE IDConta_3=%s OR IDConta_2=%s ORDER BY DtEnvConv DESC;",
                                (id_conta, id_conta))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhuma conexão encontrada."); return
                    for r in rows:
                        txt_res.insert("end", f"De:{r[0]} → Para:{r[1]}  Enviado:{r[2]}  Aceito:{r[3] or '-'}  Status:{r[4]}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_atualizar(root):
        jan = tk.Toplevel(root)
        jan.title("Atualizar Status de Conexão")
        jan.geometry("420x240")
        f = tk.Frame(jan); f.pack(pady=10)
        tk.Label(f, text="ID Conta Remetente:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ent_de = tk.Entry(f, width=10); ent_de.grid(row=0, column=1, pady=2, sticky="w")
        tk.Label(f, text="ID Conta Destinatário:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ent_para = tk.Entry(f, width=10); ent_para.grid(row=1, column=1, pady=2, sticky="w")
        tk.Label(f, text="Novo Status:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        cb_status = ttk.Combobox(f, values=ConexaoCRUD.STATUS, state="readonly", width=14)
        cb_status.current(1); cb_status.grid(row=2, column=1, pady=2, sticky="w")

        def salvar():
            conn = conectar_bd()
            if not conn: return
            aceito = "CURRENT_DATE" if cb_status.get() == "Aceita" else "NULL"
            try:
                with conn.cursor() as cur:
                    cur.execute(f"UPDATE CONEXAO SET StatusConexao=%s, DtAceitConv={'CURRENT_DATE' if cb_status.get()=='Aceita' else 'NULL'} WHERE IDConta_3=%s AND IDConta_2=%s;",
                                (cb_status.get(), ent_de.get(), ent_para.get()))
                conn.commit(); messagebox.showinfo("Sucesso","Status atualizado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 3, salvar)

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Remover Conexão")
        jan.geometry("420x180")
        f = tk.Frame(jan); f.pack(pady=10)
        tk.Label(f, text="ID Conta Remetente:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ent_de = tk.Entry(f, width=10); ent_de.grid(row=0, column=1, sticky="w")
        tk.Label(f, text="ID Conta Destinatário:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ent_para = tk.Entry(f, width=10); ent_para.grid(row=1, column=1, sticky="w")

        def deletar():
            if not messagebox.askyesno("Confirmar","Remover conexão?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM CONEXAO WHERE IDConta_3=%s AND IDConta_2=%s;", (ent_de.get(), ent_para.get()))
                conn.commit(); messagebox.showinfo("Sucesso","Conexão removida!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, deletar, "Remover")


# ── CORPORATIVA_SETOREMP ─────────────────────────────────────────

class SetorEmpCRUD:
    @staticmethod
    def tela_criar(root):
        jan = tk.Toplevel(root)
        jan.title("Adicionar Setor a Empresa")
        jan.geometry("420x180")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            corps = VagaCRUD._buscar_corporativas(conn)
        finally:
            conn.close()

        cb_emp  = label_combo(f, "Empresa:", 0); cb_emp["values"] = corps
        ent_set = label_entry(f, "Setor:", 1)

        def salvar():
            id_emp = extrair_id(cb_emp.get()); setor = ent_set.get().strip()
            if not id_emp or not setor:
                messagebox.showerror("Erro","Preencha empresa e setor."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO CORPORATIVA_SETOREMP (SetorEmp, IDConta) VALUES (%s,%s);", (setor, id_emp))
                conn.commit(); messagebox.showinfo("Sucesso","Setor adicionado!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, salvar)

    @staticmethod
    def tela_buscar(root):
        jan = tk.Toplevel(root)
        jan.title("Setores da Empresa")
        jan.geometry("460x320")
        f = tk.Frame(jan); f.pack(pady=8)
        tk.Label(f, text="ID da Empresa:").pack(side="left")
        ent = tk.Entry(f, width=10); ent.pack(side="left", padx=5)
        txt_res = tk.Text(jan, width=55, height=10, state="disabled"); txt_res.pack(pady=5)

        def buscar():
            conn = conectar_bd()
            if not conn: return
            txt_res.config(state="normal"); txt_res.delete("1.0","end")
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT SetorEmp FROM CORPORATIVA_SETOREMP WHERE IDConta=%s ORDER BY SetorEmp;", (ent.get(),))
                    rows = cur.fetchall()
                    if not rows: txt_res.insert("end","Nenhum setor."); return
                    for r in rows: txt_res.insert("end", f"• {r[0]}\n")
            except Error as e:
                txt_res.insert("end", str(e))
            finally:
                conn.close(); txt_res.config(state="disabled")

        tk.Button(f, text="Buscar", command=buscar).pack(side="left")

    @staticmethod
    def tela_deletar(root):
        jan = tk.Toplevel(root)
        jan.title("Remover Setor")
        jan.geometry("420x180")
        f = tk.Frame(jan); f.pack(pady=10)

        conn = conectar_bd()
        if not conn: return
        try:
            corps = VagaCRUD._buscar_corporativas(conn)
        finally:
            conn.close()

        cb_emp  = label_combo(f, "Empresa:", 0); cb_emp["values"] = corps
        ent_set = label_entry(f, "Setor exato:", 1)

        def deletar():
            id_emp = extrair_id(cb_emp.get()); setor = ent_set.get().strip()
            if not id_emp or not setor: return
            if not messagebox.askyesno("Confirmar","Remover setor?"): return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM CORPORATIVA_SETOREMP WHERE SetorEmp=%s AND IDConta=%s;", (setor, id_emp))
                conn.commit(); messagebox.showinfo("Sucesso","Setor removido!"); jan.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", str(e))
            finally:
                conn.close()

        salvar_btn(f, 2, deletar, "Remover")


# ════════════════════════════════════════════════════════════════
#  CRUD ORIGINAL — CONTA  (mantido do código original)
# ════════════════════════════════════════════════════════════════

class ContaCRUD:
    def __init__(self):
        self.ent_din1 = self.ent_din2 = self.ent_din3 = self.txt_din3 = None

    def extrair_id(self, sel):
        return extrair_id(sel)

    def atualizar_formulario(self, frame, tipo):
        for widget in frame.winfo_children():
            widget.destroy()
        if tipo == "Pessoal":
            tk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
            self.ent_din1 = tk.Entry(frame, width=30); self.ent_din1.grid(row=0, column=1, pady=2)
            tk.Label(frame, text="Sobrenome:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.ent_din2 = tk.Entry(frame, width=30); self.ent_din2.grid(row=1, column=1, pady=2)
            tk.Label(frame, text="Título Profissional:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
            self.ent_din3 = tk.Entry(frame, width=30); self.ent_din3.grid(row=2, column=1, pady=2)
        else:
            tk.Label(frame, text="Nome Empresa:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
            self.ent_din1 = tk.Entry(frame, width=30); self.ent_din1.grid(row=0, column=1, pady=2)
            tk.Label(frame, text="Nº Funcionários:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.ent_din2 = tk.Entry(frame, width=30); self.ent_din2.grid(row=1, column=1, pady=2)
            tk.Label(frame, text="Descrição:").grid(row=2, column=0, sticky="ne", padx=5, pady=2)
            self.txt_din3 = tk.Text(frame, width=23, height=4); self.txt_din3.grid(row=2, column=1, pady=2)

    def logica_busca_dinamica(self, termo, tipo, combobox):
        if len(termo) < 2:
            combobox["values"] = []; return
        conn = conectar_bd()
        if not conn: return
        try:
            with conn.cursor() as cur:
                if tipo == "Pessoal":
                    cur.execute("SELECT IDConta, NomPsso || ' ' || SobnomPsso FROM PESSOAL WHERE NomPsso ILIKE %s OR SobnomPsso ILIKE %s;",
                                (f"%{termo}%", f"%{termo}%"))
                else:
                    cur.execute("SELECT IDConta, NomComerc FROM CORPORATIVA WHERE NomComerc ILIKE %s;", (f"%{termo}%",))
                combobox["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
        except Error as e:
            print(f"Erro na busca: {e}")
        finally:
            conn.close()

    def tela_criar(self, root):
        janela = tk.Toplevel(root); janela.title("Criar Nova Conta"); janela.geometry("400x550")
        tk.Label(janela, text="Tipo de Conta:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_var = tk.StringVar(value="Pessoal")
        frame_radios = tk.Frame(janela); frame_radios.pack(pady=5)
        frame_dinamico = tk.Frame(janela)

        tk.Radiobutton(frame_radios, text="Pessoal", variable=tipo_var, value="Pessoal",
                       command=lambda: self.atualizar_formulario(frame_dinamico, tipo_var.get())).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Corporativa", variable=tipo_var, value="Corporativa",
                       command=lambda: self.atualizar_formulario(frame_dinamico, tipo_var.get())).pack(side="left", padx=10)

        frame_comum = tk.Frame(janela); frame_comum.pack(pady=10)
        tk.Label(frame_comum, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ent_email = tk.Entry(frame_comum, width=30); ent_email.grid(row=0, column=1, pady=2)
        tk.Label(frame_comum, text="Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ent_senha = tk.Entry(frame_comum, width=30, show="*"); ent_senha.grid(row=1, column=1, pady=2)
        tk.Label(frame_comum, text="País:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        combo_pais = ttk.Combobox(frame_comum, width=27, state="readonly"); combo_pais.grid(row=2, column=1, pady=2)
        tk.Label(frame_comum, text="Estado:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        combo_estado = ttk.Combobox(frame_comum, width=27, state="readonly"); combo_estado.grid(row=3, column=1, pady=2)
        tk.Label(frame_comum, text="Cidade:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        combo_cidade = ttk.Combobox(frame_comum, width=27, state="readonly"); combo_cidade.grid(row=4, column=1, pady=2)

        conn = conectar_bd()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT IDPais, NomPais FROM PAIS;")
                combo_pais["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
            conn.close()

        def ao_selecionar_pais(event):
            id_pais = extrair_id(combo_pais.get())
            conn = conectar_bd()
            if conn and id_pais:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDEstado, NomEstado FROM ESTADO WHERE IDPais=%s;", (id_pais,))
                    combo_estado["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
                    combo_estado.set(""); combo_cidade.set(""); combo_cidade["values"] = []
                conn.close()

        def ao_selecionar_estado(event):
            id_estado = extrair_id(combo_estado.get())
            conn = conectar_bd()
            if conn and id_estado:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDCidade, NomCidade FROM CIDADE WHERE IDEstado=%s;", (id_estado,))
                    combo_cidade["values"] = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
                    combo_cidade.set("")
                conn.close()

        combo_pais.bind("<<ComboboxSelected>>", ao_selecionar_pais)
        combo_estado.bind("<<ComboboxSelected>>", ao_selecionar_estado)
        frame_dinamico.pack(pady=10)
        self.atualizar_formulario(frame_dinamico, "Pessoal")

        def salvar_novo():
            id_cidade = extrair_id(combo_cidade.get())
            if not id_cidade:
                messagebox.showerror("Erro","Selecione uma cidade válida."); return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade) VALUES (%s,%s,CURRENT_DATE,%s) RETURNING IDConta;",
                                (ent_email.get(), ent_senha.get(), id_cidade))
                    id_conta = cur.fetchone()[0]
                    if tipo_var.get() == "Pessoal":
                        cur.execute("INSERT INTO PESSOAL (IDConta, NomPsso, SobnomPsso, TtloProfPsso) VALUES (%s,%s,%s,%s);",
                                    (id_conta, self.ent_din1.get(), self.ent_din2.get(), self.ent_din3.get()))
                    else:
                        cur.execute("INSERT INTO CORPORATIVA (IDConta, NomComerc, NumFuncEmp, DescriEmp) VALUES (%s,%s,%s,%s);",
                                    (id_conta, self.ent_din1.get(), self.ent_din2.get(), self.txt_din3.get("1.0","end-1c")))
                conn.commit(); messagebox.showinfo("Sucesso","Conta criada com sucesso!"); janela.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro de Inserção", f"Ocorreu um erro: {e}")
            finally:
                conn.close()

        tk.Button(janela, text="Salvar", width=20, command=salvar_novo).pack(pady=10)

    def tela_buscar(self, root):
        janela = tk.Toplevel(root); janela.title("Buscar Conta"); janela.geometry("400x350")
        tk.Label(janela, text="Buscar por:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_busca_var = tk.StringVar(value="Pessoal")
        frame_radios = tk.Frame(janela); frame_radios.pack(pady=5)

        def ao_trocar_tipo():
            combo_busca.set(""); combo_busca["values"] = []
            txt_resultado.config(state="normal"); txt_resultado.delete("1.0","end"); txt_resultado.config(state="disabled")

        tk.Radiobutton(frame_radios, text="Conta Pessoal", variable=tipo_busca_var, value="Pessoal", command=ao_trocar_tipo).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Empresa", variable=tipo_busca_var, value="Corporativa", command=ao_trocar_tipo).pack(side="left", padx=10)
        frame_busca = tk.Frame(janela); frame_busca.pack(pady=10)
        tk.Label(frame_busca, text="Nome:").pack(side="left")
        combo_busca = ttk.Combobox(frame_busca, width=35); combo_busca.pack(side="left", padx=5)
        tk.Label(janela, text="Informações:", font=("Arial", 9, "bold")).pack(pady=(10,0), anchor="w", padx=20)
        txt_resultado = tk.Text(janela, width=45, height=8); txt_resultado.pack(pady=5)
        txt_resultado.config(state="disabled")

        def ao_digitar(event):
            self.logica_busca_dinamica(combo_busca.get(), tipo_busca_var.get(), combo_busca)

        def ao_selecionar(event):
            id_conta = extrair_id(combo_busca.get())
            if not id_conta: return
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    if tipo_busca_var.get() == "Pessoal":
                        cur.execute("SELECT c.EmailConta, p.NomPsso, p.TtloProfPsso FROM CONTA c JOIN PESSOAL p ON c.IDConta=p.IDConta WHERE c.IDConta=%s;", (id_conta,))
                        d = cur.fetchone()
                        info = f"Nome: {d[1]}\nEmail: {d[0]}\nTítulo: {d[2] if d[2] else 'N/A'}"
                    else:
                        cur.execute("SELECT c.EmailConta, cp.NomComerc, cp.NumFuncEmp, cp.DescriEmp FROM CONTA c JOIN CORPORATIVA cp ON c.IDConta=cp.IDConta WHERE c.IDConta=%s;", (id_conta,))
                        d = cur.fetchone()
                        info = f"Empresa: {d[1]}\nEmail: {d[0]}\nFuncionários: {d[2]}\nDescrição: {d[3]}"
                txt_resultado.config(state="normal"); txt_resultado.delete("1.0","end")
                txt_resultado.insert("1.0", info); txt_resultado.config(state="disabled")
            except Error as e:
                print(e)
            finally:
                conn.close()

        combo_busca.bind("<KeyRelease>", ao_digitar)
        combo_busca.bind("<<ComboboxSelected>>", ao_selecionar)

    def tela_atualizar(self, root):
        janela = tk.Toplevel(root); janela.title("Atualizar Conta"); janela.geometry("400x450")
        tk.Label(janela, text="Editar Perfil:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_var = tk.StringVar(value="Pessoal")
        frame_radios = tk.Frame(janela); frame_radios.pack(pady=5)

        def ao_trocar_tipo():
            combo_busca.set(""); combo_busca["values"] = []
            for w in frame_form.winfo_children(): w.destroy()

        tk.Radiobutton(frame_radios, text="Conta Pessoal", variable=tipo_var, value="Pessoal", command=ao_trocar_tipo).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Empresa", variable=tipo_var, value="Corporativa", command=ao_trocar_tipo).pack(side="left", padx=10)
        frame_busca = tk.Frame(janela); frame_busca.pack(pady=10)
        tk.Label(frame_busca, text="Buscar:").pack(side="left")
        combo_busca = ttk.Combobox(frame_busca, width=35); combo_busca.pack(side="left", padx=5)
        frame_form = tk.Frame(janela); frame_form.pack(pady=10)

        def ao_digitar(event):
            self.logica_busca_dinamica(combo_busca.get(), tipo_var.get(), combo_busca)

        def salvar_alteracoes(id_conta, ent_email, ent_senha, ent_nome, ent_sobrenome, ent_titulo, ent_func, txt_desc):
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE CONTA SET EmailConta=%s WHERE IDConta=%s;", (ent_email.get(), id_conta))
                    nova_senha = ent_senha.get()
                    if nova_senha:
                        cur.execute("UPDATE CONTA SET SenhaConta=%s WHERE IDConta=%s;", (nova_senha, id_conta))
                    if tipo_var.get() == "Pessoal":
                        cur.execute("UPDATE PESSOAL SET NomPsso=%s, SobnomPsso=%s, TtloProfPsso=%s WHERE IDConta=%s;",
                                    (ent_nome.get(), ent_sobrenome.get(), ent_titulo.get(), id_conta))
                    else:
                        cur.execute("UPDATE CORPORATIVA SET NomComerc=%s, NumFuncEmp=%s, DescriEmp=%s WHERE IDConta=%s;",
                                    (ent_nome.get(), ent_func.get(), txt_desc.get("1.0","end-1c"), id_conta))
                conn.commit(); messagebox.showinfo("Sucesso","Conta atualizada!"); janela.destroy()
            except Error as e:
                conn.rollback(); messagebox.showerror("Erro", f"Falha ao atualizar: {e}")
            finally:
                conn.close()

        def ao_selecionar(event):
            for w in frame_form.winfo_children(): w.destroy()
            id_conta = extrair_id(combo_busca.get())
            if not id_conta: return
            conn = conectar_bd()
            if not conn: return
            ent_email = ent_senha = ent_nome = ent_sobrenome = ent_titulo = ent_func = txt_desc = None
            try:
                with conn.cursor() as cur:
                    if tipo_var.get() == "Pessoal":
                        cur.execute("SELECT c.EmailConta, p.NomPsso, p.SobnomPsso, p.TtloProfPsso FROM CONTA c JOIN PESSOAL p ON c.IDConta=p.IDConta WHERE c.IDConta=%s;", (id_conta,))
                        d = cur.fetchone()
                        tk.Label(frame_form, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
                        ent_email = tk.Entry(frame_form, width=30); ent_email.insert(0, d[0]); ent_email.grid(row=0, column=1)
                        tk.Label(frame_form, text="Nova Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
                        ent_senha = tk.Entry(frame_form, width=30, show="*"); ent_senha.grid(row=1, column=1)
                        tk.Label(frame_form, text="Nome:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
                        ent_nome = tk.Entry(frame_form, width=30); ent_nome.insert(0, d[1]); ent_nome.grid(row=2, column=1)
                        tk.Label(frame_form, text="Sobrenome:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
                        ent_sobrenome = tk.Entry(frame_form, width=30); ent_sobrenome.insert(0, d[2]); ent_sobrenome.grid(row=3, column=1)
                        tk.Label(frame_form, text="Título:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
                        ent_titulo = tk.Entry(frame_form, width=30); ent_titulo.insert(0, d[3] or ""); ent_titulo.grid(row=4, column=1)
                    else:
                        cur.execute("SELECT c.EmailConta, cp.NomComerc, cp.NumFuncEmp, cp.DescriEmp FROM CONTA c JOIN CORPORATIVA cp ON c.IDConta=cp.IDConta WHERE c.IDConta=%s;", (id_conta,))
                        d = cur.fetchone()
                        tk.Label(frame_form, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
                        ent_email = tk.Entry(frame_form, width=30); ent_email.insert(0, d[0]); ent_email.grid(row=0, column=1)
                        tk.Label(frame_form, text="Nova Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
                        ent_senha = tk.Entry(frame_form, width=30, show="*"); ent_senha.grid(row=1, column=1)
                        tk.Label(frame_form, text="Nome Empresa:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
                        ent_nome = tk.Entry(frame_form, width=30); ent_nome.insert(0, d[1]); ent_nome.grid(row=2, column=1)
                        tk.Label(frame_form, text="Nº Funcionários:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
                        ent_func = tk.Entry(frame_form, width=30); ent_func.insert(0, d[2] or ""); ent_func.grid(row=3, column=1)
                        tk.Label(frame_form, text="Descrição:").grid(row=4, column=0, sticky="ne", padx=5, pady=2)
                        txt_desc = tk.Text(frame_form, width=23, height=4); txt_desc.insert("1.0", d[3] or ""); txt_desc.grid(row=4, column=1)
            except Error as e:
                messagebox.showerror("Erro", f"Falha ao carregar: {e}"); return
            finally:
                conn.close()

            def salvar_com_refs():
                salvar_alteracoes(id_conta, ent_email, ent_senha, ent_nome, ent_sobrenome, ent_titulo, ent_func, txt_desc)

            tk.Button(frame_form, text="Salvar Alterações", width=20, command=salvar_com_refs).grid(row=5, column=0, columnspan=2, pady=15)

        combo_busca.bind("<KeyRelease>", ao_digitar)
        combo_busca.bind("<<ComboboxSelected>>", ao_selecionar)

    def tela_deletar(self, root):
        janela = tk.Toplevel(root); janela.title("Deletar Conta"); janela.geometry("400x250")
        tk.Label(janela, text="Deletar Perfil:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_var = tk.StringVar(value="Pessoal")
        frame_radios = tk.Frame(janela); frame_radios.pack(pady=5)

        def ao_trocar_tipo():
            combo_busca.set(""); combo_busca["values"] = []; frame_info.pack_forget()

        tk.Radiobutton(frame_radios, text="Conta Pessoal", variable=tipo_var, value="Pessoal", command=ao_trocar_tipo).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Empresa", variable=tipo_var, value="Corporativa", command=ao_trocar_tipo).pack(side="left", padx=10)
        frame_busca = tk.Frame(janela); frame_busca.pack(pady=10)
        tk.Label(frame_busca, text="Buscar:").pack(side="left")
        combo_busca = ttk.Combobox(frame_busca, width=35); combo_busca.pack(side="left", padx=5)
        frame_info = tk.Frame(janela)
        lbl_info = tk.Label(frame_info, text=""); lbl_info.pack(pady=10)

        def confirmar_delecao():
            id_conta = extrair_id(combo_busca.get())
            if not id_conta: return
            if messagebox.askyesno("Aviso Crítico","Deletar permanentemente esta conta e todos os dados associados?"):
                conn = conectar_bd()
                if not conn: return
                try:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM CONTA WHERE IDConta=%s;", (id_conta,))
                    conn.commit(); lbl_info.config(text="Conta deletada com sucesso!", fg="green")
                    btn_deletar.pack_forget(); combo_busca.set("")
                except Error as e:
                    conn.rollback(); messagebox.showerror("Erro", f"Falha na deleção: {e}")
                finally:
                    conn.close()

        btn_deletar = tk.Button(frame_info, text="Deletar Conta", width=20, bg="red", fg="white", command=confirmar_delecao)

        def ao_digitar(event):
            self.logica_busca_dinamica(combo_busca.get(), tipo_var.get(), combo_busca)

        def ao_selecionar(event):
            frame_info.pack(fill="x", pady=10)
            lbl_info.config(text=f"Pronto para deletar: {combo_busca.get()}", fg="black")
            btn_deletar.pack(pady=5)

        combo_busca.bind("<KeyRelease>", ao_digitar)
        combo_busca.bind("<<ComboboxSelected>>", ao_selecionar)


# ════════════════════════════════════════════════════════════════
#  MENU PRINCIPAL
# ════════════════════════════════════════════════════════════════

# Mapeamento: nome exibido → classe CRUD
MODULOS = {
    "Conta":                  ContaCRUD,
    "Post":                   PostCRUD,
    "Comentário":             ComentarioCRUD,
    "Reagir a Post":          ReagePostCRUD,
    "Vaga de Emprego":        VagaCRUD,
    "Aplicação a Vaga":       AplicaVagaCRUD,
    "Competência":            CompetenciaCRUD,
    "Competência da Conta":   PossCompCRUD,
    "Comp. de Experiência":   ExpPossCompCRUD,
    "Experiência Prof.":      ExpProfCRUD,
    "Formação Acadêmica":     FormacaoCRUD,
    "Comp. de Formação":      FormPossCompCRUD,
    "Idioma":                 IdiomaCRUD,
    "Idioma da Conta":        FalaIdiomCRUD,
    "Conexão":                ConexaoCRUD,
    "Setor de Empresa":       SetorEmpCRUD,
}

# Operações disponíveis por módulo (alguns não têm atualizar)
OPERACOES = {
    "Conta":                {"Criar": "tela_criar", "Buscar": "tela_buscar", "Atualizar": "tela_atualizar", "Deletar": "tela_deletar"},
    "Post":                 {"Criar": "tela_criar", "Buscar": "tela_buscar", "Atualizar": "tela_atualizar", "Deletar": "tela_deletar"},
    "Comentário":           {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Reagir a Post":        {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Vaga de Emprego":      {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Aplicação a Vaga":     {"Criar": "tela_criar", "Buscar": "tela_buscar"},
    "Competência":          {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Competência da Conta": {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Comp. de Experiência": {"Criar": "tela_criar", "Buscar": "tela_buscar"},
    "Experiência Prof.":    {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Formação Acadêmica":   {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Comp. de Formação":    {"Criar": "tela_criar", "Buscar": "tela_buscar"},
    "Idioma":               {"Criar": "tela_criar", "Buscar": "tela_buscar"},
    "Idioma da Conta":      {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
    "Conexão":              {"Criar": "tela_criar", "Buscar": "tela_buscar", "Atualizar": "tela_atualizar", "Deletar": "tela_deletar"},
    "Setor de Empresa":     {"Criar": "tela_criar", "Buscar": "tela_buscar", "Deletar": "tela_deletar"},
}


class LinkedinMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn DB - Menu Principal")
        self.root.geometry("420x620")
        self.root.resizable(False, False)

        # Instância do CRUD de conta (tem estado interno para formulários dinâmicos)
        self._conta_crud = ContaCRUD()

        tk.Label(root, text="LinkedIn — Gerenciador de Dados",
                 font=("Arial", 13, "bold")).pack(pady=14)

        # Combobox de módulo
        frame_mod = tk.Frame(root); frame_mod.pack(pady=4)
        tk.Label(frame_mod, text="Entidade:", width=10, anchor="e").pack(side="left")
        self.combo_modulo = ttk.Combobox(frame_mod, values=list(MODULOS.keys()), state="readonly", width=24)
        self.combo_modulo.current(0); self.combo_modulo.pack(side="left", padx=6)
        self.combo_modulo.bind("<<ComboboxSelected>>", self._atualizar_botoes)

        # Frame de botões de operação
        self.frame_ops = tk.Frame(root); self.frame_ops.pack(pady=10)
        self._atualizar_botoes()

        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=8)
        tk.Button(root, text="⚙  Configurar Conexão", width=26,
                  command=lambda: tela_configuracao(self.root)).pack(pady=4)

    def _atualizar_botoes(self, event=None):
        for w in self.frame_ops.winfo_children():
            w.destroy()

        modulo = self.combo_modulo.get()
        ops = OPERACOES.get(modulo, {})
        cores = {"Criar": "#2e7d32", "Buscar": "#1565c0", "Atualizar": "#e65100", "Deletar": "#b71c1c"}

        for op, metodo in ops.items():
            cor = cores.get(op, "#333")
            tk.Button(
                self.frame_ops, text=op, width=16, bg=cor, fg="white",
                activebackground=cor,
                command=lambda m=modulo, meth=metodo: self._abrir(m, meth)
            ).pack(pady=4)

    def _abrir(self, modulo, metodo):
        cls = MODULOS[modulo]

        # Captura janelas filhas existentes antes de abrir nova
        filhas_antes = set(self.root.winfo_children())

        # ContaCRUD é stateful, usamos a instância existente
        if cls is ContaCRUD:
            getattr(self._conta_crud, metodo)(self.root)
        else:
            getattr(cls, metodo)(self.root)

        # Detecta a nova janela filha e restaura o estado ao fechá-la
        def _vincular_restauracao():
            filhas_depois = set(self.root.winfo_children())
            novas = filhas_depois - filhas_antes
            if novas:
                nova_jan = novas.pop()
                nova_jan.bind("<Destroy>", lambda e: self.root.after(50, self._restaurar_foco))
            else:
                # Nenhuma janela nova detectada (ex: erro de conexão), restaura mesmo assim
                self.root.after(50, self._restaurar_foco)

        self.root.after(10, _vincular_restauracao)

    def _restaurar_foco(self):
        """Restaura foco e estado do combo após fechar janela filha."""
        self.root.focus_force()
        self.combo_modulo.config(state="readonly")
        self._atualizar_botoes()


if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedinMenu(root)
    root.mainloop()