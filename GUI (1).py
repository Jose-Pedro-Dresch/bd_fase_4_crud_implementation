import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

def conectar():
    return psycopg2.connect(dbname="linkedin", user="postgres", password="123", host="localhost", port="5432")

# 1. Definição das Tabelas e Colunas
SCHEMAS = {
    "CONTA": (["idconta"], ["emailconta", "senhaconta", "dtcrcaoconta", "idcidade"]),
    "PESSOAL": (["idconta"], ["idconta", "nompsso", "sobnompsso", "ttloprofpsso"]),
    "CORPORATIVA": (["idconta"], ["idconta", "nomcomerc", "numfuncemp", "descriemp"]),
    "PAIS": (["idpais"], ["nompais"]),
    "CONEXAO": (["idconta_1", "idconta_2"], ["idconta_1", "idconta_2", "dtenvconv", "dtaceitconv", "statusconexao"]),
    "IDIOMA": (["ididioma"], ["nomeidioma"]),
    "FALAIDIOM": (["idconta", "ididioma"], ["idconta", "ididioma", "nvlprofic"])
}

# 2. Constraints da Interface (Dropdowns)
OPCOES_RESTRITAS = {
    "nvlprofic": ["Básico", "Intermediário", "Avançado", "Fluente", "Nativo"],
    "statusconexao": ["PENDENTE", "ACEITO"]
}

class BancoCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn - SGBD Dinâmico")
        self.root.geometry("400x300")

        tk.Label(root, text="Selecione a Tabela:", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.combo_tabela = ttk.Combobox(root, values=list(SCHEMAS.keys()), state="readonly", width=30)
        self.combo_tabela.set("FALAIDIOM")
        self.combo_tabela.pack(pady=10)

        frame_botoes = tk.Frame(root)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="Criar (Insert)", width=15, command=self.tela_criar).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_botoes, text="Buscar (Select)", width=15, command=self.tela_buscar).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame_botoes, text="Atualizar (Update)", width=15, command=self.tela_atualizar).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame_botoes, text="Deletar (Delete)", width=15, command=self.tela_deletar).grid(row=1, column=1, padx=5, pady=5)

    def get_info_tabela(self):
        tabela = self.combo_tabela.get()
        pks, colunas = SCHEMAS[tabela]
        return tabela, pks, colunas

    # Função que cria o input correto (Entry normal ou Combobox para restritos)
    def criar_input(self, janela, col, row_idx):
        tk.Label(janela, text=f"{col}:").grid(row=row_idx, column=0, pady=5, padx=10, sticky="e")
        
        if col in OPCOES_RESTRITAS:
            ent = ttk.Combobox(janela, values=OPCOES_RESTRITAS[col], state="readonly", width=27)
            ent.set(OPCOES_RESTRITAS[col][0])
        else:
            ent = tk.Entry(janela, width=30)
            
        ent.grid(row=row_idx, column=1, pady=5, padx=10)
        return ent

    def tela_criar(self):
        tabela, _, colunas = self.get_info_tabela()
        janela = tk.Toplevel(self.root)
        janela.title(f"Insert - {tabela}")
        
        entries = {}
        for idx, col in enumerate(colunas):
            entries[col] = self.criar_input(janela, col, idx)

        def executar_insert():
            valores = [entries[col].get() for col in colunas]
            placeholders = ", ".join(["%s"] * len(colunas))
            cols_str = ", ".join(colunas)
            query = f"INSERT INTO {tabela} ({cols_str}) VALUES ({placeholders});"
            
            try:
                with conectar() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, valores)
                        conn.commit()
                messagebox.showinfo("Sucesso", f"Registro inserido em {tabela}.")
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(janela, text="Inserir", command=executar_insert, bg="lightgreen").grid(row=len(colunas), columnspan=2, pady=15)

    def tela_buscar(self):
        tabela = self.combo_tabela.get()
        janela = tk.Toplevel(self.root)
        janela.title(f"Select - {tabela}")
        janela.geometry("600x300")

        tree = ttk.Treeview(janela, show="headings")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            with conectar() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT * FROM {tabela};")
                    col_names = [desc[0] for desc in cur.description]
                    tree["columns"] = col_names
                    
                    for col in col_names:
                        tree.heading(col, text=col)
                        tree.column(col, width=100)
                        
                    for row in cur.fetchall():
                        tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def tela_atualizar(self):
        tabela, pks, colunas = self.get_info_tabela()
        janela = tk.Toplevel(self.root)
        janela.title(f"Update - {tabela}")

        entries_pk = {}
        for idx, pk in enumerate(pks):
            tk.Label(janela, text=f"{pk} (Alvo):").grid(row=idx, column=0, pady=5, padx=10, sticky="e")
            ent = tk.Entry(janela, width=30)
            ent.grid(row=idx, column=1, pady=5, padx=10)
            entries_pk[pk] = ent

        offset = len(pks)
        entries_col = {}
        for idx, col in enumerate(colunas):
            entries_col[col] = self.criar_input(janela, col, offset + idx)

        def executar_update():
            set_clause = ", ".join([f"{col}=%s" for col in colunas])
            where_clause = " AND ".join([f"{pk}=%s" for pk in pks])
            
            valores_set = [entries_col[col].get() for col in colunas]
            valores_where = [entries_pk[pk].get() for pk in pks]
            valores = valores_set + valores_where
            
            query = f"UPDATE {tabela} SET {set_clause} WHERE {where_clause};"
            
            try:
                with conectar() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, valores)
                        conn.commit()
                        if cur.rowcount == 0:
                            messagebox.showwarning("Aviso", "Registro não encontrado.")
                        else:
                            messagebox.showinfo("Sucesso", "Registro atualizado.")
                            janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(janela, text="Atualizar", command=executar_update, bg="lightblue").grid(row=offset+len(colunas), columnspan=2, pady=15)

    def tela_deletar(self):
        tabela, pks, _ = self.get_info_tabela()
        janela = tk.Toplevel(self.root)
        janela.title(f"Delete - {tabela}")

        entries_pk = {}
        for idx, pk in enumerate(pks):
            tk.Label(janela, text=f"{pk}:").grid(row=idx, column=0, pady=10, padx=10, sticky="e")
            ent = tk.Entry(janela, width=20)
            ent.grid(row=idx, column=1, pady=10, padx=10)
            entries_pk[pk] = ent

        def executar_delete():
            where_clause = " AND ".join([f"{pk}=%s" for pk in pks])
            valores_where = [entries_pk[pk].get() for pk in pks]
            
            try:
                with conectar() as conn:
                    with conn.cursor() as cur:
                        cur.execute(f"DELETE FROM {tabela} WHERE {where_clause};", valores_where)
                        conn.commit()
                        if cur.rowcount == 0:
                            messagebox.showwarning("Aviso", "Registro não encontrado.")
                        else:
                            messagebox.showinfo("Sucesso", "Registro deletado.")
                            janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(janela, text="Deletar", command=executar_delete, bg="lightcoral").grid(row=len(pks), columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = BancoCRUDApp(root)
    root.mainloop()