import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from psycopg2 import Error

# Configurações de conexão
DB_CONFIG = {
    "dbname": "linkedin",
    "user": "postgres",
    "password": "123",
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
    """Abre uma janela para configurar os parâmetros de conexão com o banco."""
    janela = tk.Toplevel(root)
    janela.title("Configuração do Banco de Dados")
    janela.geometry("350x280")
    janela.resizable(False, False)
    janela.grab_set()  # Bloqueia a janela principal

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

class LinkedinMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn - Menu Principal")
        self.root.geometry("300x290")

        tk.Label(root, text="Selecione a Operação", font=("Arial", 12, "bold")).pack(pady=20)

        tk.Button(root, text="Criar", width=20, command=self.tela_criar).pack(pady=5)
        tk.Button(root, text="Buscar", width=20, command=self.tela_buscar).pack(pady=5)
        tk.Button(root, text="Atualizar", width=20, command=self.tela_atualizar).pack(pady=5)
        tk.Button(root, text="Deletar", width=20, command=self.tela_deletar).pack(pady=5)
        tk.Button(root, text="Configurar Conexao", width=20,
                  command=lambda: tela_configuracao(self.root)).pack(pady=5)

    def extrair_id(self, selecao_combobox):
        try:
            return int(selecao_combobox.split(" - ")[0])
        except (ValueError, IndexError):
            return None

    def tela_criar(self):
        janela_criar = tk.Toplevel(self.root)
        janela_criar.title("Criar Nova Conta")
        janela_criar.geometry("400x550")

        tk.Label(janela_criar, text="Tipo de Conta:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_var = tk.StringVar(value="Pessoal")

        frame_radios = tk.Frame(janela_criar)
        frame_radios.pack(pady=5)
        
        tk.Radiobutton(frame_radios, text="Pessoal", variable=tipo_var, value="Pessoal", 
                       command=lambda: self.atualizar_formulario(frame_dinamico, tipo_var.get())).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Corporativa", variable=tipo_var, value="Corporativa", 
                       command=lambda: self.atualizar_formulario(frame_dinamico, tipo_var.get())).pack(side="left", padx=10)

        frame_comum = tk.Frame(janela_criar)
        frame_comum.pack(pady=10)
        
        tk.Label(frame_comum, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ent_email = tk.Entry(frame_comum, width=30)
        ent_email.grid(row=0, column=1, pady=2)
        
        tk.Label(frame_comum, text="Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ent_senha = tk.Entry(frame_comum, width=30, show="*")
        ent_senha.grid(row=1, column=1, pady=2)

        tk.Label(frame_comum, text="País:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        combo_pais = ttk.Combobox(frame_comum, width=27, state="readonly")
        combo_pais.grid(row=2, column=1, pady=2)

        tk.Label(frame_comum, text="Estado:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        combo_estado = ttk.Combobox(frame_comum, width=27, state="readonly")
        combo_estado.grid(row=3, column=1, pady=2)

        tk.Label(frame_comum, text="Cidade:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        combo_cidade = ttk.Combobox(frame_comum, width=27, state="readonly")
        combo_cidade.grid(row=4, column=1, pady=2)

        conn = conectar_bd()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT IDPais, NomPais FROM PAIS;")
                paises = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
                combo_pais["values"] = paises
            conn.close()

        def ao_selecionar_pais(event):
            id_pais = self.extrair_id(combo_pais.get())
            conn = conectar_bd()
            if conn and id_pais:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDEstado, NomEstado FROM ESTADO WHERE IDPais = %s;", (id_pais,))
                    combo_estado["values"] = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
                    combo_estado.set("")
                    combo_cidade.set("")
                    combo_cidade["values"] = []
                conn.close()

        def ao_selecionar_estado(event):
            id_estado = self.extrair_id(combo_estado.get())
            conn = conectar_bd()
            if conn and id_estado:
                with conn.cursor() as cur:
                    cur.execute("SELECT IDCidade, NomCidade FROM CIDADE WHERE IDEstado = %s;", (id_estado,))
                    combo_cidade["values"] = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
                    combo_cidade.set("")
                conn.close()

        combo_pais.bind("<<ComboboxSelected>>", ao_selecionar_pais)
        combo_estado.bind("<<ComboboxSelected>>", ao_selecionar_estado)

        frame_dinamico = tk.Frame(janela_criar)
        frame_dinamico.pack(pady=10)
        self.atualizar_formulario(frame_dinamico, "Pessoal")

        def salvar_novo():
            id_cidade = self.extrair_id(combo_cidade.get())
            if not id_cidade:
                messagebox.showerror("Erro", "Selecione uma cidade válida.")
                return

            conn = conectar_bd()
            if not conn: return

            try:
                with conn.cursor() as cur:
                    query_conta = "INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade) VALUES (%s, %s, CURRENT_DATE, %s) RETURNING IDConta;"
                    cur.execute(query_conta, (ent_email.get(), ent_senha.get(), id_cidade))
                    id_conta = cur.fetchone()[0]

                    if tipo_var.get() == "Pessoal":
                        query_psso = "INSERT INTO PESSOAL (IDConta, NomPsso, SobnomPsso, TtloProfPsso) VALUES (%s, %s, %s, %s);"
                        cur.execute(query_psso, (id_conta, self.ent_din1.get(), self.ent_din2.get(), self.ent_din3.get()))
                    else:
                        query_corp = "INSERT INTO CORPORATIVA (IDConta, NomComerc, NumFuncEmp, DescriEmp) VALUES (%s, %s, %s, %s);"
                        cur.execute(query_corp, (id_conta, self.ent_din1.get(), self.ent_din2.get(), self.txt_din3.get("1.0", "end-1c")))
                
                conn.commit()
                messagebox.showinfo("Sucesso", "Conta criada com sucesso!")
                janela_criar.destroy()
            except Error as e:
                conn.rollback()
                messagebox.showerror("Erro de Inserção", f"Ocorreu um erro: {e}")
            finally:
                conn.close()

        tk.Button(janela_criar, text="Salvar", width=20, command=salvar_novo).pack(pady=10)

    def atualizar_formulario(self, frame, tipo):
        for widget in frame.winfo_children():
            widget.destroy()

        if tipo == "Pessoal":
            tk.Label(frame, text="Nome:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
            self.ent_din1 = tk.Entry(frame, width=30)
            self.ent_din1.grid(row=0, column=1, pady=2)

            tk.Label(frame, text="Sobrenome:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.ent_din2 = tk.Entry(frame, width=30)
            self.ent_din2.grid(row=1, column=1, pady=2)

            tk.Label(frame, text="Título Profissional:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
            self.ent_din3 = tk.Entry(frame, width=30)
            self.ent_din3.grid(row=2, column=1, pady=2)

        elif tipo == "Corporativa":
            tk.Label(frame, text="Nome Empresa:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
            self.ent_din1 = tk.Entry(frame, width=30)
            self.ent_din1.grid(row=0, column=1, pady=2)

            tk.Label(frame, text="Nº Funcionários:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.ent_din2 = tk.Entry(frame, width=30)
            self.ent_din2.grid(row=1, column=1, pady=2)

            tk.Label(frame, text="Descrição:").grid(row=2, column=0, sticky="ne", padx=5, pady=2)
            self.txt_din3 = tk.Text(frame, width=23, height=4)
            self.txt_din3.grid(row=2, column=1, pady=2)

    def logica_busca_dinamica(self, termo, tipo, combobox):
        if len(termo) < 2:
            combobox["values"] = []
            return
        
        conn = conectar_bd()
        if not conn: return

        try:
            with conn.cursor() as cur:
                if tipo == "Pessoal":
                    query = "SELECT IDConta, NomPsso || ' ' || SobnomPsso FROM PESSOAL WHERE NomPsso ILIKE %s OR SobnomPsso ILIKE %s;"
                    cur.execute(query, (f"%{termo}%", f"%{termo}%"))
                else:
                    query = "SELECT IDConta, NomComerc FROM CORPORATIVA WHERE NomComerc ILIKE %s;"
                    cur.execute(query, (f"%{termo}%",))
                
                combobox["values"] = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
        except Error as e:
            print(f"Erro na busca: {e}")
        finally:
            conn.close()

    def tela_buscar(self):
        janela_buscar = tk.Toplevel(self.root)
        janela_buscar.title("Buscar Conta")
        janela_buscar.geometry("400x350")

        tk.Label(janela_buscar, text="Buscar por:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_busca_var = tk.StringVar(value="Pessoal")

        frame_radios = tk.Frame(janela_buscar)
        frame_radios.pack(pady=5)
        
        def ao_trocar_tipo():
            combo_busca.set("")
            combo_busca["values"] = []
            txt_resultado.config(state="normal")
            txt_resultado.delete("1.0", "end")
            txt_resultado.config(state="disabled")

        tk.Radiobutton(frame_radios, text="Conta Pessoal", variable=tipo_busca_var, value="Pessoal", command=ao_trocar_tipo).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Empresa", variable=tipo_busca_var, value="Corporativa", command=ao_trocar_tipo).pack(side="left", padx=10)

        frame_busca = tk.Frame(janela_buscar)
        frame_busca.pack(pady=10)

        tk.Label(frame_busca, text="Nome:").pack(side="left")
        combo_busca = ttk.Combobox(frame_busca, width=35)
        combo_busca.pack(side="left", padx=5)

        tk.Label(janela_buscar, text="Informações:", font=("Arial", 9, "bold")).pack(pady=(10, 0), anchor="w", padx=20)
        txt_resultado = tk.Text(janela_buscar, width=45, height=8)
        txt_resultado.pack(pady=5)
        txt_resultado.config(state="disabled")

        def ao_digitar(event):
            self.logica_busca_dinamica(combo_busca.get(), tipo_busca_var.get(), combo_busca)

        def ao_selecionar(event):
            id_conta = self.extrair_id(combo_busca.get())
            if not id_conta: return

            conn = conectar_bd()
            if not conn: return
            
            try:
                with conn.cursor() as cur:
                    if tipo_busca_var.get() == "Pessoal":
                        cur.execute("SELECT c.EmailConta, p.NomPsso, p.TtloProfPsso FROM CONTA c JOIN PESSOAL p ON c.IDConta = p.IDConta WHERE c.IDConta = %s;", (id_conta,))
                        dados = cur.fetchone()
                        info = f"Nome: {dados[1]}\nEmail: {dados[0]}\nTítulo: {dados[2] if dados[2] else 'N/A'}"
                    else:
                        cur.execute("SELECT c.EmailConta, cp.NomComerc, cp.NumFuncEmp, cp.DescriEmp FROM CONTA c JOIN CORPORATIVA cp ON c.IDConta = cp.IDConta WHERE c.IDConta = %s;", (id_conta,))
                        dados = cur.fetchone()
                        info = f"Empresa: {dados[1]}\nEmail: {dados[0]}\nFuncionários: {dados[2]}\nDescrição: {dados[3]}"
                
                txt_resultado.config(state="normal")
                txt_resultado.delete("1.0", "end")
                txt_resultado.insert("1.0", info)
                txt_resultado.config(state="disabled")
            except Error as e:
                print(e)
            finally:
                conn.close()

        combo_busca.bind("<KeyRelease>", ao_digitar)
        combo_busca.bind("<<ComboboxSelected>>", ao_selecionar)

    def tela_atualizar(self):
        janela_atualizar = tk.Toplevel(self.root)
        janela_atualizar.title("Atualizar Conta")
        janela_atualizar.geometry("400x450")

        tk.Label(janela_atualizar, text="Editar Perfil:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_var = tk.StringVar(value="Pessoal")

        frame_radios = tk.Frame(janela_atualizar)
        frame_radios.pack(pady=5)

        def ao_trocar_tipo():
            combo_busca.set("")
            combo_busca["values"] = []
            for widget in frame_form.winfo_children():
                widget.destroy()

        tk.Radiobutton(frame_radios, text="Conta Pessoal", variable=tipo_var, value="Pessoal", command=ao_trocar_tipo).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Empresa", variable=tipo_var, value="Corporativa", command=ao_trocar_tipo).pack(side="left", padx=10)

        frame_busca = tk.Frame(janela_atualizar)
        frame_busca.pack(pady=10)

        tk.Label(frame_busca, text="Buscar:").pack(side="left")
        combo_busca = ttk.Combobox(frame_busca, width=35)
        combo_busca.pack(side="left", padx=5)

        frame_form = tk.Frame(janela_atualizar)
        frame_form.pack(pady=10)

        def ao_digitar(event):
            self.logica_busca_dinamica(combo_busca.get(), tipo_var.get(), combo_busca)

        def salvar_alteracoes(id_conta, ent_email, ent_senha, ent_nome,
                              ent_sobrenome, ent_titulo, ent_func, txt_desc):
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE CONTA SET EmailConta = %s WHERE IDConta = %s;", (ent_email.get(), id_conta))
                    
                    nova_senha = ent_senha.get()
                    if nova_senha:
                        cur.execute("UPDATE CONTA SET SenhaConta = %s WHERE IDConta = %s;", (nova_senha, id_conta))
                    
                    if tipo_var.get() == "Pessoal":
                        cur.execute("UPDATE PESSOAL SET NomPsso = %s, SobnomPsso = %s, TtloProfPsso = %s WHERE IDConta = %s;",
                                    (ent_nome.get(), ent_sobrenome.get(), ent_titulo.get(), id_conta))
                    else:
                        cur.execute("UPDATE CORPORATIVA SET NomComerc = %s, NumFuncEmp = %s, DescriEmp = %s WHERE IDConta = %s;",
                                    (ent_nome.get(), ent_func.get(), txt_desc.get("1.0", "end-1c"), id_conta))
                conn.commit()
                messagebox.showinfo("Sucesso", "Conta atualizada com sucesso!")
                janela_atualizar.destroy()
            except Error as e:
                conn.rollback()
                messagebox.showerror("Erro", f"Falha ao atualizar: {e}")
            finally:
                conn.close()

        def ao_selecionar(event):
            for widget in frame_form.winfo_children():
                widget.destroy()

            id_conta = self.extrair_id(combo_busca.get())
            if not id_conta: return

            conn = conectar_bd()
            if not conn: return

            # Variáveis locais que serão capturadas pelo closure de salvar_alteracoes
            ent_email = ent_senha = ent_nome = ent_sobrenome = ent_titulo = None
            ent_func = txt_desc = None

            try:
                with conn.cursor() as cur:
                    if tipo_var.get() == "Pessoal":
                        cur.execute("SELECT c.EmailConta, p.NomPsso, p.SobnomPsso, p.TtloProfPsso FROM CONTA c JOIN PESSOAL p ON c.IDConta = p.IDConta WHERE c.IDConta = %s;", (id_conta,))
                        dados = cur.fetchone()

                        tk.Label(frame_form, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
                        ent_email = tk.Entry(frame_form, width=30)
                        ent_email.insert(0, dados[0])
                        ent_email.grid(row=0, column=1, pady=2)

                        tk.Label(frame_form, text="Nova Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
                        ent_senha = tk.Entry(frame_form, width=30, show="*")
                        ent_senha.grid(row=1, column=1, pady=2)

                        tk.Label(frame_form, text="Nome:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
                        ent_nome = tk.Entry(frame_form, width=30)
                        ent_nome.insert(0, dados[1])
                        ent_nome.grid(row=2, column=1, pady=2)

                        tk.Label(frame_form, text="Sobrenome:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
                        ent_sobrenome = tk.Entry(frame_form, width=30)
                        ent_sobrenome.insert(0, dados[2])
                        ent_sobrenome.grid(row=3, column=1, pady=2)

                        tk.Label(frame_form, text="Título:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
                        ent_titulo = tk.Entry(frame_form, width=30)
                        ent_titulo.insert(0, dados[3] if dados[3] else "")
                        ent_titulo.grid(row=4, column=1, pady=2)

                    else:
                        cur.execute("SELECT c.EmailConta, cp.NomComerc, cp.NumFuncEmp, cp.DescriEmp FROM CONTA c JOIN CORPORATIVA cp ON c.IDConta = cp.IDConta WHERE c.IDConta = %s;", (id_conta,))
                        dados = cur.fetchone()

                        tk.Label(frame_form, text="Email:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
                        ent_email = tk.Entry(frame_form, width=30)
                        ent_email.insert(0, dados[0])
                        ent_email.grid(row=0, column=1, pady=2)

                        tk.Label(frame_form, text="Nova Senha:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
                        ent_senha = tk.Entry(frame_form, width=30, show="*")
                        ent_senha.grid(row=1, column=1, pady=2)

                        tk.Label(frame_form, text="Nome Empresa:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
                        ent_nome = tk.Entry(frame_form, width=30)
                        ent_nome.insert(0, dados[1])
                        ent_nome.grid(row=2, column=1, pady=2)

                        tk.Label(frame_form, text="Nº Funcionários:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
                        ent_func = tk.Entry(frame_form, width=30)
                        ent_func.insert(0, dados[2] if dados[2] else "")
                        ent_func.grid(row=3, column=1, pady=2)

                        tk.Label(frame_form, text="Descrição:").grid(row=4, column=0, sticky="ne", padx=5, pady=2)
                        txt_desc = tk.Text(frame_form, width=23, height=4)
                        txt_desc.insert("1.0", dados[3] if dados[3] else "")
                        txt_desc.grid(row=4, column=1, pady=2)

            except Error as e:
                messagebox.showerror("Erro", f"Falha ao carregar dados: {e}")
                return
            finally:
                conn.close()

            # Passa as variáveis locais via closure para salvar_alteracoes
            def salvar_com_refs():
                salvar_alteracoes(id_conta, ent_email, ent_senha, ent_nome,
                                  ent_sobrenome, ent_titulo, ent_func, txt_desc)

            tk.Button(frame_form, text="Salvar Alterações", width=20,
                      command=salvar_com_refs).grid(row=5, column=0, columnspan=2, pady=15)

        combo_busca.bind("<KeyRelease>", ao_digitar)
        combo_busca.bind("<<ComboboxSelected>>", ao_selecionar)

    def tela_deletar(self):
        janela_deletar = tk.Toplevel(self.root)
        janela_deletar.title("Deletar Conta")
        janela_deletar.geometry("400x250")

        tk.Label(janela_deletar, text="Deletar Perfil:", font=("Arial", 10, "bold")).pack(pady=10)
        tipo_var = tk.StringVar(value="Pessoal")

        frame_radios = tk.Frame(janela_deletar)
        frame_radios.pack(pady=5)

        def ao_trocar_tipo():
            combo_busca.set("")
            combo_busca["values"] = []
            frame_info.pack_forget()

        tk.Radiobutton(frame_radios, text="Conta Pessoal", variable=tipo_var, value="Pessoal", command=ao_trocar_tipo).pack(side="left", padx=10)
        tk.Radiobutton(frame_radios, text="Empresa", variable=tipo_var, value="Corporativa", command=ao_trocar_tipo).pack(side="left", padx=10)

        frame_busca = tk.Frame(janela_deletar)
        frame_busca.pack(pady=10)

        tk.Label(frame_busca, text="Buscar:").pack(side="left")
        combo_busca = ttk.Combobox(frame_busca, width=35)
        combo_busca.pack(side="left", padx=5)

        frame_info = tk.Frame(janela_deletar)
        lbl_info = tk.Label(frame_info, text="")
        lbl_info.pack(pady=10)

        def confirmar_delecao():
            id_conta = self.extrair_id(combo_busca.get())
            if not id_conta: return

            resposta = messagebox.askyesno("Aviso Crítico", "Tem certeza que deseja deletar permanentemente esta conta e todos os dados associados (posts, aplicações, etc)?")
            if resposta:
                conn = conectar_bd()
                if not conn: return
                try:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM CONTA WHERE IDConta = %s;", (id_conta,))
                    conn.commit()
                    lbl_info.config(text="Conta deletada com sucesso!", fg="green")
                    btn_deletar.pack_forget()
                    combo_busca.set("")
                except Error as e:
                    conn.rollback()
                    messagebox.showerror("Erro", f"Falha na deleção: {e}")
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

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedinMenu(root)
    root.mainloop()