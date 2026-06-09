import psycopg2
from psycopg2 import Error
import sys
import os

# Configurações de conexão
DB_CONFIG = {
    "dbname": "linkedin",
    "user": "postgres",
    "password": "123",
    "host": "localhost",
    "port": "5432"
}

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def conectar_bd():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except Error as e:
        print(f"\n[ERRO CRÍTICO] Falha de conexão com o banco: {e}")
        return None

def tela_configuracao():
    print("\n=== Configuração do Banco de Dados ===")
    DB_CONFIG["host"] = prompt_input("Host", DB_CONFIG["host"])
    DB_CONFIG["port"] = prompt_input("Porta", DB_CONFIG["port"])
    DB_CONFIG["dbname"] = prompt_input("Banco de Dados", DB_CONFIG["dbname"])
    DB_CONFIG["user"] = prompt_input("Usuário", DB_CONFIG["user"])
    DB_CONFIG["password"] = prompt_input("Senha", DB_CONFIG["password"])
    
    conn = conectar_bd()
    if conn:
        print("\n✔ Conexão bem-sucedida!")
        conn.close()
    else:
        print("\n✘ Falha na conexão. Verifique os dados.")
    input("Pressione Enter para continuar...")

# ─────────────────────────── HELPERS CLI ───────────────────────────

def extrair_id(selecao):
    try:
        return int(str(selecao).split(" - ")[0])
    except (ValueError, IndexError, AttributeError):
        return None

def prompt_input(mensagem, default="", obrigatorio=True):
    while True:
        sufixo = f" [{default}]" if default else ""
        valor = input(f"{mensagem}{sufixo}: ").strip()
        if valor: return valor
        if default: return default
        if not obrigatorio: return None
        print("Erro: Este campo é obrigatório.")

def prompt_menu(mensagem, opcoes, extrair=True):
    if not opcoes:
        print(f"Nenhuma opção disponível para: {mensagem}")
        return None
    print(f"\n--- {mensagem} ---")
    for i, opt in enumerate(opcoes, 1):
        print(f"[{i}] {opt}")
    while True:
        try:
            esc = int(input("Escolha uma opção (número) ou 0 para cancelar: "))
            if esc == 0: return None
            if 1 <= esc <= len(opcoes):
                selecao = opcoes[esc-1]
                return extrair_id(selecao) if extrair else selecao
            print("Opção inválida.")
        except ValueError:
            print("Digite um número válido.")

def exibir_resultados(rows, formatador):
    if not rows:
        print("\nNenhum resultado encontrado.")
        return
    print("\n" + "="*50)
    for r in rows:
        print(formatador(r))
        print("-" * 50)

def executar_query(query, params=(), fetch=False, commit=False):
    conn = conectar_bd()
    if not conn: return None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if commit:
                conn.commit()
                print("\n✔ Operação realizada com sucesso!")
            if fetch:
                return cur.fetchall()
    except Error as e:
        if commit: conn.rollback()
        print(f"\n✘ Erro na operação: {e}")
    finally:
        if conn: conn.close()

def buscar_opcoes_dinamicas(tabela, id_col, expressao_label, clausula_extra=""):
    """
    Lista opções de forma paginada/limitada.
    Se o usuário não digitar nada, traz um Head e Tail (10 asc, 10 desc).
    Se digitar, faz um ILIKE filtrado (limitado a 20).
    """
    termo = prompt_input(f"Digite para filtrar {tabela.split()[0]} (ou Enter p/ Head e Tail)", obrigatorio=False)
    
    has_where = "WHERE " in clausula_extra.upper()
    where_and = "AND" if has_where else "WHERE"
    
    if termo:
        q = f"SELECT {id_col}, {expressao_label} FROM {tabela} {clausula_extra} {where_and} CAST({expressao_label} AS TEXT) ILIKE %s ORDER BY {id_col} LIMIT 20;"
        rows = executar_query(q, (f"%{termo}%",), fetch=True)
    else:
        q = f"""
            SELECT * FROM (
                (SELECT {id_col}, {expressao_label} FROM {tabela} {clausula_extra} ORDER BY {id_col} ASC LIMIT 10)
                UNION
                (SELECT {id_col}, {expressao_label} FROM {tabela} {clausula_extra} ORDER BY {id_col} DESC LIMIT 10)
            ) AS sub ORDER BY 1 ASC;
        """
        rows = executar_query(q, fetch=True)
        
    return [f"{r[0]} - {r[1]}" for r in rows] if rows else []

# ════════════════════════════════════════════════════════════════
#  MÓDULOS CRUD
# ════════════════════════════════════════════════════════════════

class PostCRUD:
    NIVEIS = ["Publico", "Conexoes", "Privado"]

    @staticmethod
    def _buscar_contas():
        return buscar_opcoes_dinamicas(
            tabela="CONTA c",
            id_col="c.IDConta",
            expressao_label="COALESCE((SELECT NomPsso||' '||SobnomPsso FROM PESSOAL p WHERE p.IDConta=c.IDConta), (SELECT NomComerc FROM CORPORATIVA cp WHERE cp.IDConta=c.IDConta), c.EmailConta)"
        )

    @staticmethod
    def tela_criar():
        print("\n--- Criar Post ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        if not id_conta: return
        conteudo = prompt_input("Conteúdo")
        nivel = prompt_menu("Nível Visib.", PostCRUD.NIVEIS, extrair=False)
        if not nivel: return
        executar_query("INSERT INTO POST (DtPubliPost, ConteudoPost, NivelVisib, IDConta) VALUES (CURRENT_TIMESTAMP,%s,%s,%s);", 
                       (conteudo, nivel, id_conta), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Buscar Post ---")
        id_post = prompt_input("ID do Post (ou deixe vazio)", obrigatorio=False)
        if id_post:
            rows = executar_query("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST WHERE IDPost=%s;", (id_post,), fetch=True)
        else:
            id_conta = prompt_input("Listar por Conta (ID) (ou vazio p/ todos)", obrigatorio=False)
            if id_conta:
                rows = executar_query("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST WHERE IDConta=%s ORDER BY DtPubliPost DESC;", (id_conta,), fetch=True)
            else:
                rows = executar_query("SELECT IDPost, DtPubliPost, NivelVisib, ConteudoPost, IDConta FROM POST ORDER BY DtPubliPost DESC LIMIT 20;", fetch=True)
        exibir_resultados(rows, lambda r: f"ID:{r[0]}  Data:{r[1]}  Nível:{r[2]}  Conta:{r[4]}\n{r[3]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Post ---")
        id_post = prompt_input("ID do Post")
        rows = executar_query("SELECT ConteudoPost, NivelVisib FROM POST WHERE IDPost=%s;", (id_post,), fetch=True)
        if not rows:
            print("Post não encontrado.")
            return
        print(f"\nConteúdo Atual: {rows[0][0]}\nNível Atual: {rows[0][1]}")
        novo_conteudo = prompt_input("Novo Conteúdo")
        novo_nivel = prompt_menu("Novo Nível", PostCRUD.NIVEIS, extrair=False)
        if novo_nivel:
            executar_query("UPDATE POST SET ConteudoPost=%s, NivelVisib=%s WHERE IDPost=%s;", (novo_conteudo, novo_nivel, id_post), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Post ---")
        id_post = prompt_input("ID do Post")
        if prompt_input("Deletar post e comentários? (S/N)").upper() == 'S':
            executar_query("DELETE FROM POST WHERE IDPost=%s;", (id_post,), commit=True)


class ComentarioCRUD:
    @staticmethod
    def _buscar_posts():
        return buscar_opcoes_dinamicas("POST", "IDPost", "LEFT(ConteudoPost, 40)")

    @staticmethod
    def tela_criar():
        print("\n--- Criar Comentário ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        id_post = prompt_menu("Post", ComentarioCRUD._buscar_posts())
        if not id_conta or not id_post: return
        conteudo = prompt_input("Conteúdo")
        executar_query("INSERT INTO COMENTARIO (ConteudoTxtCom, DtPubliCom, IDPost, IDConta) VALUES (%s, CURRENT_TIMESTAMP, %s, %s);",
                       (conteudo, id_post, id_conta), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Buscar Comentários ---")
        id_post = prompt_input("ID do Post")
        rows = executar_query("SELECT IDComentario, DtPubliCom, IDConta, ConteudoTxtCom FROM COMENTARIO WHERE IDPost=%s ORDER BY DtPubliCom;", (id_post,), fetch=True)
        exibir_resultados(rows, lambda r: f"#{r[0]}  {r[1]}  Conta:{r[2]}\n{r[3]}")

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Comentário ---")
        id_com = prompt_input("ID do Comentário")
        if prompt_input("Confirmar deleção? (S/N)").upper() == 'S':
            executar_query("DELETE FROM COMENTARIO WHERE IDComentario=%s;", (id_com,), commit=True)

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Comentário ---")
        id_com = prompt_input("ID do Comentário")
        rows = executar_query("SELECT ConteudoTxtCom FROM COMENTARIO WHERE IDComentario=%s;", (id_com,), fetch=True)
        if not rows:
            print("Comentário não encontrado.")
            return
        print(f"\nConteúdo Atual: {rows[0][0]}")
        novo_conteudo = prompt_input("Novo Conteúdo")
        executar_query("UPDATE COMENTARIO SET ConteudoTxtCom=%s WHERE IDComentario=%s;", (novo_conteudo, id_com), commit=True)


class ReagePostCRUD:
    TIPOS = ["Curtir", "Celebrar", "Apoiar", "Interessante", "Curioso"]

    @staticmethod
    def tela_criar():
        print("\n--- Reagir a Post ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        id_post = prompt_menu("Post", ComentarioCRUD._buscar_posts())
        tipo = prompt_menu("Tipo Reação", ReagePostCRUD.TIPOS, extrair=False)
        if not all([id_conta, id_post, tipo]): return
        executar_query("INSERT INTO REAGEPOST (IDConta, IDPost, DtReacao, TipoReacao) VALUES (%s,%s,CURRENT_TIMESTAMP,%s) ON CONFLICT (IDConta,IDPost) DO UPDATE SET TipoReacao=%s, DtReacao=CURRENT_TIMESTAMP;",
                       (id_conta, id_post, tipo, tipo), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Ver Reações ---")
        id_post = prompt_input("ID do Post")
        rows = executar_query("SELECT IDConta, TipoReacao, DtReacao FROM REAGEPOST WHERE IDPost=%s ORDER BY DtReacao DESC;", (id_post,), fetch=True)
        exibir_resultados(rows, lambda r: f"Conta:{r[0]}  Tipo:{r[1]}  Data:{r[2]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Reação ---")
        id_conta = prompt_input("ID Conta")
        id_post = prompt_input("ID Post")
        novo_tipo = prompt_menu("Novo Tipo", ReagePostCRUD.TIPOS, extrair=False)
        if novo_tipo:
            executar_query("UPDATE REAGEPOST SET TipoReacao=%s, DtReacao=CURRENT_TIMESTAMP WHERE IDConta=%s AND IDPost=%s;", (novo_tipo, id_conta, id_post), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Remover Reação ---")
        id_conta = prompt_input("ID Conta")
        id_post = prompt_input("ID Post")
        if prompt_input("Confirmar remoção? (S/N)").upper() == 'S':
            executar_query("DELETE FROM REAGEPOST WHERE IDConta=%s AND IDPost=%s;", (id_conta, id_post), commit=True)


class VagaCRUD:
    FORMATOS = ["Presencial", "Remoto", "Hibrido"]

    @staticmethod
    def _buscar_corporativas():
        return buscar_opcoes_dinamicas("CORPORATIVA", "IDConta", "NomComerc")

    @staticmethod
    def tela_criar():
        print("\n--- Criar Vaga ---")
        id_emp = prompt_menu("Empresa", VagaCRUD._buscar_corporativas())
        if not id_emp: return
        titulo = prompt_input("Título")
        desc = prompt_input("Descrição")
        fmt = prompt_menu("Formato", VagaCRUD.FORMATOS, extrair=False)
        if fmt:
            executar_query("INSERT INTO VAGAEMPREGO (TtloVaga, DescriVaga, FormatoTrabVaga, DtCrcaoVaga, IDConta) VALUES (%s,%s,%s,CURRENT_DATE,%s);",
                           (titulo, desc, fmt, id_emp), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Buscar Vagas ---")
        termo = prompt_input("Título (parcial ou vazio)", obrigatorio=False)
        q = "SELECT v.IDVagaEmp, v.TtloVaga, v.FormatoTrabVaga, v.DtCrcaoVaga, c.NomComerc FROM VAGAEMPREGO v JOIN CORPORATIVA c ON v.IDConta=c.IDConta "
        if termo:
            rows = executar_query(q + "WHERE v.TtloVaga ILIKE %s ORDER BY v.DtCrcaoVaga DESC;", (f"%{termo}%",), fetch=True)
        else:
            rows = executar_query(q + "ORDER BY v.DtCrcaoVaga DESC LIMIT 20;", fetch=True)
        exibir_resultados(rows, lambda r: f"ID:{r[0]}  {r[1]}  [{r[2]}]  {r[3]}\nEmpresa: {r[4]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Vaga ---")
        id_vaga = prompt_input("ID da Vaga")
        rows = executar_query("SELECT TtloVaga, DescriVaga, FormatoTrabVaga FROM VAGAEMPREGO WHERE IDVagaEmp=%s;", (id_vaga,), fetch=True)
        if not rows:
            print("Vaga não encontrada.")
            return
        ntit = prompt_input("Título", default=rows[0][0])
        ndesc = prompt_input("Descrição", default=rows[0][1])
        nfmt = prompt_menu(f"Formato (Atual: {rows[0][2]})", VagaCRUD.FORMATOS, extrair=False) or rows[0][2]
        executar_query("UPDATE VAGAEMPREGO SET TtloVaga=%s, DescriVaga=%s, FormatoTrabVaga=%s WHERE IDVagaEmp=%s;", (ntit, ndesc, nfmt, id_vaga), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Vaga ---")
        id_vaga = prompt_input("ID da Vaga")
        if prompt_input("Deletar vaga e aplicações? (S/N)").upper() == 'S':
            executar_query("DELETE FROM VAGAEMPREGO WHERE IDVagaEmp=%s;", (id_vaga,), commit=True)


class AplicaVagaCRUD:
    @staticmethod
    def _buscar_vagas():
        return buscar_opcoes_dinamicas("VAGAEMPREGO", "IDVagaEmp", "TtloVaga")

    STATUS = ["Enviada", "Em Analise", "Aprovada", "Recusada"]

    @staticmethod
    def tela_criar():
        print("\n--- Aplicar a Vaga ---")
        id_conta = prompt_menu("Candidato (Conta)", PostCRUD._buscar_contas())
        id_vaga = prompt_menu("Vaga", AplicaVagaCRUD._buscar_vagas())
        if not id_conta or not id_vaga: return
        status = prompt_menu("Status da Aplicação", AplicaVagaCRUD.STATUS, extrair=False) or "Enviada"
        executar_query("INSERT INTO APLICAAVAGA (IDVagaEmp, DtAplccao, SttusAplccao, IDConta) VALUES (%s, CURRENT_TIMESTAMP, %s, %s);",
                       (id_vaga, status, id_conta), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Buscar Aplicações ---")
        id_vaga = prompt_input("ID da Vaga (ou deixe vazio para todas)", obrigatorio=False)
        if id_vaga:
            rows = executar_query("SELECT IDVagaEmp, IDConta, DtAplccao, SttusAplccao FROM APLICAAVAGA WHERE IDVagaEmp=%s ORDER BY DtAplccao;", (id_vaga,), fetch=True)
        else:
            rows = executar_query("SELECT IDVagaEmp, IDConta, DtAplccao, SttusAplccao FROM APLICAAVAGA ORDER BY DtAplccao DESC LIMIT 30;", fetch=True)
        exibir_resultados(rows, lambda r: f"Vaga:{r[0]}  Conta:{r[1]}  Data:{r[2]}  Status:{r[3] or '-'}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Aplicação ---")
        id_vaga = prompt_input("ID da Vaga")
        id_conta = prompt_input("ID da Conta")
        rows = executar_query("SELECT SttusAplccao FROM APLICAAVAGA WHERE IDVagaEmp=%s AND IDConta=%s;", (id_vaga, id_conta), fetch=True)
        if not rows:
            print("Aplicação não encontrada.")
            return
        novo_status = prompt_menu(f"Novo Status (Atual: {rows[0][0]})", AplicaVagaCRUD.STATUS, extrair=False)
        if novo_status:
            executar_query("UPDATE APLICAAVAGA SET SttusAplccao=%s WHERE IDVagaEmp=%s AND IDConta=%s;", (novo_status, id_vaga, id_conta), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Aplicação ---")
        id_vaga = prompt_input("ID da Vaga")
        id_conta = prompt_input("ID da Conta")
        if prompt_input("Deletar aplicação? (S/N)").upper() == 'S':
            executar_query("DELETE FROM APLICAAVAGA WHERE IDVagaEmp=%s AND IDConta=%s;", (id_vaga, id_conta), commit=True)


class CompetenciaCRUD:
    @staticmethod
    def _todas():
        return buscar_opcoes_dinamicas("COMPETENCIA", "IDComp", "NomeComp")

    @staticmethod
    def tela_criar():
        print("\n--- Criar Competência ---")
        nome = prompt_input("Nome da Competência")
        executar_query("INSERT INTO COMPETENCIA (NomeComp) VALUES (%s);", (nome,), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Listar Competências ---")
        rows = executar_query("SELECT IDComp, NomeComp FROM COMPETENCIA ORDER BY NomeComp;", fetch=True)
        exibir_resultados(rows, lambda r: f"ID: {r[0]} - {r[1]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Competência ---")
        id_comp = prompt_menu("Competência", CompetenciaCRUD._todas())
        if not id_comp: return
        rows = executar_query("SELECT NomeComp FROM COMPETENCIA WHERE IDComp=%s;", (id_comp,), fetch=True)
        novo_nome = prompt_input("Novo Nome", default=rows[0][0])
        executar_query("UPDATE COMPETENCIA SET NomeComp=%s WHERE IDComp=%s;", (novo_nome, id_comp), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Competência ---")
        id_comp = prompt_menu("Competência", CompetenciaCRUD._todas())
        if not id_comp: return
        if prompt_input("Deletar competência? (S/N)").upper() == 'S':
            executar_query("DELETE FROM COMPETENCIA WHERE IDComp=%s;", (id_comp,), commit=True)


class PossCompCRUD:
    @staticmethod
    def tela_criar():
        print("\n--- Adicionar Competência à Conta ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        id_comp = prompt_menu("Competência", CompetenciaCRUD._todas())
        if not id_conta or not id_comp: return
        executar_query("INSERT INTO POSSCOMP (IDComp, IDConta) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_comp, id_conta), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Competências da Conta ---")
        id_conta = prompt_input("ID da Conta")
        rows = executar_query("SELECT c.IDComp, c.NomeComp FROM POSSCOMP pc JOIN COMPETENCIA c ON pc.IDComp=c.IDComp WHERE pc.IDConta=%s ORDER BY c.NomeComp;", (id_conta,), fetch=True)
        exibir_resultados(rows, lambda r: f"ID: {r[0]} - {r[1]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Competência da Conta ---")
        id_conta = prompt_input("ID da Conta")
        id_comp_antiga = prompt_input("ID da Competência Atual")
        print("Escolha a nova competência:")
        id_comp_nova = prompt_menu("Nova Competência", CompetenciaCRUD._todas())
        if id_comp_nova:
            executar_query("UPDATE POSSCOMP SET IDComp=%s WHERE IDConta=%s AND IDComp=%s;", (id_comp_nova, id_conta, id_comp_antiga), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Remover Competência da Conta ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        id_comp = prompt_menu("Competência", CompetenciaCRUD._todas())
        if not id_conta or not id_comp: return
        if prompt_input("Remover vínculo? (S/N)").upper() == 'S':
            executar_query("DELETE FROM POSSCOMP WHERE IDComp=%s AND IDConta=%s;", (id_comp, id_conta), commit=True)


class ExpProfCRUD:
    TIPOS_EMP = ["CLT", "PJ", "Freelancer", "Estagio", "Temporario"]

    @staticmethod
    def tela_criar():
        print("\n--- Criar Experiência Profissional ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        if not id_conta: return
        titulo = prompt_input("Título")
        tipo = prompt_menu("Tipo Emprego", ExpProfCRUD.TIPOS_EMP, extrair=False)
        inicio = prompt_input("Dt Início (AAAA-MM-DD)")
        fim = prompt_input("Dt Fim (ou deixe vazio p/ atual)", obrigatorio=False)
        desc = prompt_input("Descrição", obrigatorio=False)
        id_emp = prompt_menu("Empresa (opcional, digite 0 p/ pular)", VagaCRUD._buscar_corporativas())
        
        executar_query("INSERT INTO EXPERIENCIAPROF (TituloExp, TipoEmpregoExp, DtInicioExp, DtFimExp, DescAtv, IDConta, IDEmp) VALUES (%s,%s,%s,%s,%s,%s,%s);",
                       (titulo, tipo, inicio, fim if fim else None, desc, id_conta, id_emp), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Buscar Experiências ---")
        id_conta = prompt_input("ID da Conta")
        rows = executar_query("SELECT e.IDExp, e.TituloExp, e.TipoEmpregoExp, e.DtInicioExp, e.DtFimExp, COALESCE(c.NomComerc,'') FROM EXPERIENCIAPROF e LEFT JOIN CORPORATIVA c ON e.IDEmp=c.IDConta WHERE e.IDConta=%s ORDER BY e.DtInicioExp DESC;", (id_conta,), fetch=True)
        exibir_resultados(rows, lambda r: f"#{r[0]}  {r[1]}  [{r[2]}]\n  {r[3]} → {r[4] or 'atual'}  Empresa:{r[5]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Experiência ---")
        id_exp = prompt_input("ID da Experiência")
        rows = executar_query("SELECT TituloExp, TipoEmpregoExp, DtInicioExp, DtFimExp, DescAtv FROM EXPERIENCIAPROF WHERE IDExp=%s;", (id_exp,), fetch=True)
        if not rows:
            print("Experiência não encontrada.")
            return
        r = rows[0]
        ntit = prompt_input("Título", default=r[0])
        ntipo = prompt_menu(f"Tipo Emprego (Atual: {r[1]})", ExpProfCRUD.TIPOS_EMP, extrair=False) or r[1]
        nini = prompt_input("Dt Início", default=str(r[2]))
        nfim = prompt_input("Dt Fim (vazio p/ atual)", default=str(r[3] if r[3] else ""), obrigatorio=False)
        ndesc = prompt_input("Descrição", default=r[4] or "", obrigatorio=False)
        executar_query("UPDATE EXPERIENCIAPROF SET TituloExp=%s, TipoEmpregoExp=%s, DtInicioExp=%s, DtFimExp=%s, DescAtv=%s WHERE IDExp=%s;",
                       (ntit, ntipo, nini, nfim if nfim else None, ndesc, id_exp), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Experiência ---")
        id_exp = prompt_input("ID Experiência")
        if prompt_input("Deletar experiência? (S/N)").upper() == 'S':
            executar_query("DELETE FROM EXPERIENCIAPROF WHERE IDExp=%s;", (id_exp,), commit=True)


class ExpPossCompCRUD:
    @staticmethod
    def _buscar_exps():
        return buscar_opcoes_dinamicas("EXPERIENCIAPROF", "IDExp", "TituloExp")

    @staticmethod
    def tela_criar():
        print("\n--- Vincular Competência a Experiência ---")
        id_exp = prompt_menu("Experiência", ExpPossCompCRUD._buscar_exps())
        id_comp = prompt_menu("Competência", CompetenciaCRUD._todas())
        if not id_exp or not id_comp: return
        executar_query("INSERT INTO EXPPOSSCOMP (IDComp, IDExp) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_comp, id_exp), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Competências por Experiência ---")
        id_exp = prompt_input("ID Experiência")
        rows = executar_query("SELECT c.IDComp, c.NomeComp FROM EXPPOSSCOMP ec JOIN COMPETENCIA c ON ec.IDComp=c.IDComp WHERE ec.IDExp=%s;", (id_exp,), fetch=True)
        exibir_resultados(rows, lambda r: f"ID: {r[0]} - {r[1]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Competência de Experiência ---")
        id_exp = prompt_input("ID da Experiência")
        id_comp_antiga = prompt_input("ID da Competência Atual")
        id_comp_nova = prompt_menu("Nova Competência", CompetenciaCRUD._todas())
        if id_comp_nova:
            executar_query("UPDATE EXPPOSSCOMP SET IDComp=%s WHERE IDExp=%s AND IDComp=%s;", (id_comp_nova, id_exp, id_comp_antiga), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Remover Competência de Experiência ---")
        id_exp = prompt_input("ID da Experiência")
        id_comp = prompt_input("ID da Competência")
        if prompt_input("Remover vínculo? (S/N)").upper() == 'S':
            executar_query("DELETE FROM EXPPOSSCOMP WHERE IDExp=%s AND IDComp=%s;", (id_exp, id_comp), commit=True)


class FormacaoCRUD:
    GRAUS = ["Fundamental", "Medio", "Tecnico", "Graduacao", "Pos-graduacao", "Mestrado", "Doutorado"]

    @staticmethod
    def tela_criar():
        print("\n--- Criar Formação Acadêmica ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        if not id_conta: return
        inst = prompt_input("Instituição")
        grau = prompt_menu("Grau", FormacaoCRUD.GRAUS, extrair=False)
        area = prompt_input("Área (opcional)", obrigatorio=False)
        ini = prompt_input("Dt Início (AAAA-MM-DD)", obrigatorio=False)
        fim = prompt_input("Dt Fim (ou vazio)", obrigatorio=False)
        
        executar_query("INSERT INTO FORMACAOACAD (NomInstitForm, GrauForm, AreaForm, DtInicioForm, DtFimForm, IDConta) VALUES (%s,%s,%s,%s,%s,%s);",
                       (inst, grau, area if area else None, ini if ini else None, fim if fim else None, id_conta), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Buscar Formações ---")
        id_conta = prompt_input("ID da Conta")
        rows = executar_query("SELECT IDForm, NomInstitForm, GrauForm, AreaForm, DtInicioForm, DtFimForm FROM FORMACAOACAD WHERE IDConta=%s ORDER BY DtInicioForm DESC;", (id_conta,), fetch=True)
        exibir_resultados(rows, lambda r: f"#{r[0]}  {r[1]}  [{r[2]}]  Área:{r[3] or '-'}\n  {r[4]} → {r[5] or 'atual'}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Formação ---")
        id_form = prompt_input("ID da Formação")
        rows = executar_query("SELECT NomInstitForm, GrauForm, AreaForm, DtInicioForm, DtFimForm FROM FORMACAOACAD WHERE IDForm=%s;", (id_form,), fetch=True)
        if not rows: return
        r = rows[0]
        ninst = prompt_input("Instituição", default=r[0])
        ngrau = prompt_menu(f"Grau (Atual: {r[1]})", FormacaoCRUD.GRAUS, extrair=False) or r[1]
        narea = prompt_input("Área", default=r[2] or "", obrigatorio=False)
        nini = prompt_input("Dt Início", default=str(r[3] if r[3] else ""), obrigatorio=False)
        nfim = prompt_input("Dt Fim", default=str(r[4] if r[4] else ""), obrigatorio=False)
        executar_query("UPDATE FORMACAOACAD SET NomInstitForm=%s, GrauForm=%s, AreaForm=%s, DtInicioForm=%s, DtFimForm=%s WHERE IDForm=%s;",
                       (ninst, ngrau, narea if narea else None, nini if nini else None, nfim if nfim else None, id_form), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Formação ---")
        id_form = prompt_input("ID Formação")
        if prompt_input("Deletar formação? (S/N)").upper() == 'S':
            executar_query("DELETE FROM FORMACAOACAD WHERE IDForm=%s;", (id_form,), commit=True)


class FormPossCompCRUD:
    @staticmethod
    def _buscar_forms():
        return buscar_opcoes_dinamicas("FORMACAOACAD", "IDForm", "NomInstitForm")

    @staticmethod
    def tela_criar():
        print("\n--- Vincular Competência a Formação ---")
        id_form = prompt_menu("Formação", FormPossCompCRUD._buscar_forms())
        id_comp = prompt_menu("Competência", CompetenciaCRUD._todas())
        if not id_form or not id_comp: return
        executar_query("INSERT INTO FORMPOSSCOMP (IDComp, IDForm) VALUES (%s,%s) ON CONFLICT DO NOTHING;", (id_comp, id_form), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Competências por Formação ---")
        id_form = prompt_input("ID Formação")
        rows = executar_query("SELECT c.IDComp, c.NomeComp FROM FORMPOSSCOMP fc JOIN COMPETENCIA c ON fc.IDComp=c.IDComp WHERE fc.IDForm=%s;", (id_form,), fetch=True)
        exibir_resultados(rows, lambda r: f"ID: {r[0]} - {r[1]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Competência de Formação ---")
        id_form = prompt_input("ID da Formação")
        id_comp_antiga = prompt_input("ID da Competência Atual")
        id_comp_nova = prompt_menu("Nova Competência", CompetenciaCRUD._todas())
        if id_comp_nova:
            executar_query("UPDATE FORMPOSSCOMP SET IDComp=%s WHERE IDForm=%s AND IDComp=%s;", (id_comp_nova, id_form, id_comp_antiga), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Remover Competência de Formação ---")
        id_form = prompt_input("ID da Formação")
        id_comp = prompt_input("ID da Competência")
        if prompt_input("Remover vínculo? (S/N)").upper() == 'S':
            executar_query("DELETE FROM FORMPOSSCOMP WHERE IDForm=%s AND IDComp=%s;", (id_form, id_comp), commit=True)


class IdiomaCRUD:
    @staticmethod
    def _todos():
        return buscar_opcoes_dinamicas("IDIOMA", "IDIdioma", "NomeIdioma")

    @staticmethod
    def tela_criar():
        print("\n--- Cadastrar Idioma ---")
        nome = prompt_input("Nome do Idioma")
        executar_query("INSERT INTO IDIOMA (NomeIdioma) VALUES (%s);", (nome,), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Listar Idiomas ---")
        rows = executar_query("SELECT IDIdioma, NomeIdioma FROM IDIOMA ORDER BY NomeIdioma;", fetch=True)
        exibir_resultados(rows, lambda r: f"ID: {r[0]} - {r[1]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Idioma ---")
        id_idioma = prompt_menu("Idioma", IdiomaCRUD._todos())
        if not id_idioma: return
        rows = executar_query("SELECT NomeIdioma FROM IDIOMA WHERE IDIdioma=%s;", (id_idioma,), fetch=True)
        novo_nome = prompt_input("Novo Nome", default=rows[0][0])
        executar_query("UPDATE IDIOMA SET NomeIdioma=%s WHERE IDIdioma=%s;", (novo_nome, id_idioma), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Deletar Idioma ---")
        id_idioma = prompt_menu("Idioma", IdiomaCRUD._todos())
        if not id_idioma: return
        if prompt_input("Deletar idioma? (S/N)").upper() == 'S':
            executar_query("DELETE FROM IDIOMA WHERE IDIdioma=%s;", (id_idioma,), commit=True)


class FalaIdiomCRUD:
    NIVEIS = ["Basico", "Intermediario", "Avancado", "Fluente", "Nativo"]

    @staticmethod
    def tela_criar():
        print("\n--- Vincular Idioma à Conta ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        id_idioma = prompt_menu("Idioma", IdiomaCRUD._todos())
        nivel = prompt_menu("Nível", FalaIdiomCRUD.NIVEIS, extrair=False)
        if not all([id_conta, id_idioma, nivel]): return
        executar_query("INSERT INTO FALAIDIOM (IDIdioma, NvlProfic, IDConta) VALUES (%s,%s,%s) ON CONFLICT (IDIdioma, IDConta) DO UPDATE SET NvlProfic=%s;",
                       (id_idioma, nivel, id_conta, nivel), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Idiomas da Conta ---")
        id_conta = prompt_input("ID da Conta")
        rows = executar_query("SELECT i.IDIdioma, i.NomeIdioma, fi.NvlProfic FROM FALAIDIOM fi JOIN IDIOMA i ON fi.IDIdioma=i.IDIdioma WHERE fi.IDConta=%s ORDER BY i.NomeIdioma;", (id_conta,), fetch=True)
        exibir_resultados(rows, lambda r: f"ID: {r[0]} - {r[1]}  Nível: {r[2]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Idioma da Conta ---")
        id_conta = prompt_input("ID da Conta")
        id_idioma = prompt_input("ID do Idioma")
        rows = executar_query("SELECT NvlProfic FROM FALAIDIOM WHERE IDConta=%s AND IDIdioma=%s;", (id_conta, id_idioma), fetch=True)
        if not rows: return
        novo_nivel = prompt_menu(f"Novo Nível (Atual: {rows[0][0]})", FalaIdiomCRUD.NIVEIS, extrair=False)
        if novo_nivel:
            executar_query("UPDATE FALAIDIOM SET NvlProfic=%s WHERE IDConta=%s AND IDIdioma=%s;", (novo_nivel, id_conta, id_idioma), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Remover Idioma da Conta ---")
        id_conta = prompt_menu("Conta", PostCRUD._buscar_contas())
        id_idioma = prompt_menu("Idioma", IdiomaCRUD._todos())
        if not id_conta or not id_idioma: return
        if prompt_input("Remover vínculo? (S/N)").upper() == 'S':
            executar_query("DELETE FROM FALAIDIOM WHERE IDIdioma=%s AND IDConta=%s;", (id_idioma, id_conta), commit=True)


class ConexaoCRUD:
    STATUS = ["Pendente", "Aceita", "Recusada"]

    @staticmethod
    def tela_criar():
        print("\n--- Enviar Solicitação de Conexão ---")
        contas = PostCRUD._buscar_contas()
        id_de = prompt_menu("De (Conta Remetente)", contas)
        id_para = prompt_menu("Para (Conta Destinatário)", contas)
        if not id_de or not id_para or id_de == id_para:
            print("Erro: Selecione duas contas distintas.")
            return
        executar_query("INSERT INTO CONEXAO (DtEnvConv, StatusConexao, IDConta_1, IDConta_2) VALUES (CURRENT_TIMESTAMP, 'Pendente', %s, %s);", (id_de, id_para), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Buscar Conexões ---")
        id_conta = prompt_input("ID da Conta")
        rows = executar_query("SELECT IDConta_1, IDConta_2, DtEnvConv, DtAceitConv, StatusConexao FROM CONEXAO WHERE IDConta_1=%s OR IDConta_2=%s ORDER BY DtEnvConv DESC;", (id_conta, id_conta), fetch=True)
        exibir_resultados(rows, lambda r: f"De:{r[0]} → Para:{r[1]}  Enviado:{r[2]}  Aceito:{r[3] or '-'}  Status:{r[4]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Status de Conexão ---")
        id_de = prompt_input("ID Conta Remetente")
        id_para = prompt_input("ID Conta Destinatário")
        status = prompt_menu("Novo Status", ConexaoCRUD.STATUS, extrair=False)
        if not status: return
        query = f"UPDATE CONEXAO SET StatusConexao=%s, DtAceitConv={'CURRENT_TIMESTAMP' if status=='Aceita' else 'NULL'} WHERE IDConta_1=%s AND IDConta_2=%s;"
        executar_query(query, (status, id_de, id_para), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Remover Conexão ---")
        id_de = prompt_input("ID Conta Remetente")
        id_para = prompt_input("ID Conta Destinatário")
        if prompt_input("Remover conexão? (S/N)").upper() == 'S':
            executar_query("DELETE FROM CONEXAO WHERE IDConta_1=%s AND IDConta_2=%s;", (id_de, id_para), commit=True)


class SetorEmpCRUD:
    @staticmethod
    def tela_criar():
        print("\n--- Adicionar Setor a Empresa ---")
        id_emp = prompt_menu("Empresa", VagaCRUD._buscar_corporativas())
        if not id_emp: return
        setor = prompt_input("Nome do Setor")
        executar_query("INSERT INTO CORPORATIVA_SETOREMP (SetorEmp, IDConta) VALUES (%s,%s);", (setor, id_emp), commit=True)

    @staticmethod
    def tela_buscar():
        print("\n--- Setores da Empresa ---")
        id_emp = prompt_input("ID da Empresa")
        rows = executar_query("SELECT SetorEmp FROM CORPORATIVA_SETOREMP WHERE IDConta=%s ORDER BY SetorEmp;", (id_emp,), fetch=True)
        exibir_resultados(rows, lambda r: f"• {r[0]}")

    @staticmethod
    def tela_atualizar():
        print("\n--- Atualizar Setor ---")
        id_emp = prompt_input("ID da Empresa")
        setor_antigo = prompt_input("Nome do Setor Atual")
        setor_novo = prompt_input("Novo Nome do Setor")
        executar_query("UPDATE CORPORATIVA_SETOREMP SET SetorEmp=%s WHERE IDConta=%s AND SetorEmp=%s;", (setor_novo, id_emp, setor_antigo), commit=True)

    @staticmethod
    def tela_deletar():
        print("\n--- Remover Setor ---")
        id_emp = prompt_menu("Empresa", VagaCRUD._buscar_corporativas())
        if not id_emp: return
        setor = prompt_input("Nome exato do Setor")
        if prompt_input("Remover setor? (S/N)").upper() == 'S':
            executar_query("DELETE FROM CORPORATIVA_SETOREMP WHERE SetorEmp=%s AND IDConta=%s;", (setor, id_emp), commit=True)

class ContaCRUD:
    def tela_criar(self):
        print("\n--- Criar Nova Conta ---")
        tipo = prompt_menu("Tipo de Conta", ["Pessoal", "Corporativa"], extrair=False)
        if not tipo: return
        
        email = prompt_input("Email")
        senha = prompt_input("Senha")
        
        id_pais = prompt_menu("País", buscar_opcoes_dinamicas("PAIS", "IDPais", "NomPais"))
        if not id_pais: return
        
        id_estado = prompt_menu("Estado", buscar_opcoes_dinamicas("ESTADO", "IDEstado", "NomEstado", f"WHERE IDPais={id_pais}"))
        if not id_estado: return

        id_cidade = prompt_menu("Cidade", buscar_opcoes_dinamicas("CIDADE", "IDCidade", "NomCidade", f"WHERE IDEstado={id_estado}"))
        if not id_cidade: return

        if tipo == "Pessoal":
            nome = prompt_input("Nome")
            sobrenome = prompt_input("Sobrenome")
            titulo = prompt_input("Título Profissional", obrigatorio=False)
            
            conn = conectar_bd()
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade) VALUES (%s,%s,CURRENT_DATE,%s) RETURNING IDConta;", (email, senha, id_cidade))
                        id_c = cur.fetchone()[0]
                        cur.execute("INSERT INTO PESSOAL (IDConta, NomPsso, SobnomPsso, TtloProfPsso) VALUES (%s,%s,%s,%s);", (id_c, nome, sobrenome, titulo))
                    conn.commit()
                    print("\n✔ Conta Pessoal criada!")
                except Error as e:
                    conn.rollback(); print(f"Erro: {e}")
                finally:
                    conn.close()
        else:
            nome_emp = prompt_input("Nome Empresa")
            num_func = prompt_input("Nº Funcionários", obrigatorio=False)
            desc = prompt_input("Descrição", obrigatorio=False)
            
            conn = conectar_bd()
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade) VALUES (%s,%s,CURRENT_DATE,%s) RETURNING IDConta;", (email, senha, id_cidade))
                        id_c = cur.fetchone()[0]
                        cur.execute("INSERT INTO CORPORATIVA (IDConta, NomComerc, NumFuncEmp, DescriEmp) VALUES (%s,%s,%s,%s);", (id_c, nome_emp, num_func, desc))
                    conn.commit()
                    print("\n✔ Conta Corporativa criada!")
                except Error as e:
                    conn.rollback(); print(f"Erro: {e}")
                finally:
                    conn.close()

    def tela_buscar(self):
        print("\n--- Buscar Conta ---")
        termo = prompt_input("Buscar por Nome/Empresa")
        
        q_p = "SELECT c.IDConta, c.EmailConta, p.NomPsso, p.TtloProfPsso FROM CONTA c JOIN PESSOAL p ON c.IDConta=p.IDConta WHERE p.NomPsso ILIKE %s;"
        q_c = "SELECT c.IDConta, c.EmailConta, cp.NomComerc, cp.NumFuncEmp FROM CONTA c JOIN CORPORATIVA cp ON c.IDConta=cp.IDConta WHERE cp.NomComerc ILIKE %s;"
        
        rows_p = executar_query(q_p, (f"%{termo}%",), fetch=True)
        rows_c = executar_query(q_c, (f"%{termo}%",), fetch=True)
        
        print("\n--- Pessoais ---")
        exibir_resultados(rows_p, lambda r: f"ID:{r[0]} | {r[2]} | {r[1]} | {r[3]}")
        print("\n--- Corporativas ---")
        exibir_resultados(rows_c, lambda r: f"ID:{r[0]} | {r[2]} | {r[1]} | Funcs: {r[3]}")

    def tela_atualizar(self):
        print("\n--- Atualizar Conta ---")
        id_conta = prompt_input("ID da Conta")

        rows = executar_query("SELECT EmailConta FROM CONTA WHERE IDConta=%s;", (id_conta,), fetch=True)
        if not rows:
            print("Conta não encontrada.")
            return

        novo_email = prompt_input("Novo Email", default=rows[0][0])

        rows_p = executar_query("SELECT NomPsso, SobnomPsso, TtloProfPsso FROM PESSOAL WHERE IDConta=%s;", (id_conta,), fetch=True)
        rows_c = executar_query("SELECT NomComerc, NumFuncEmp, DescriEmp FROM CORPORATIVA WHERE IDConta=%s;", (id_conta,), fetch=True)

        conn = conectar_bd()
        if not conn: return
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE CONTA SET EmailConta=%s WHERE IDConta=%s;", (novo_email, id_conta))
                if rows_p:
                    r = rows_p[0]
                    novo_nom = prompt_input("Nome", default=r[0])
                    novo_sob = prompt_input("Sobrenome", default=r[1])
                    novo_ttl = prompt_input("Título Profissional", default=r[2] or "", obrigatorio=False)
                    cur.execute("UPDATE PESSOAL SET NomPsso=%s, SobnomPsso=%s, TtloProfPsso=%s WHERE IDConta=%s;",
                                (novo_nom, novo_sob, novo_ttl if novo_ttl else None, id_conta))
                elif rows_c:
                    r = rows_c[0]
                    novo_nome_emp = prompt_input("Nome Empresa", default=r[0])
                    novo_num_func = prompt_input("Nº Funcionários", default=str(r[1]) if r[1] else "", obrigatorio=False)
                    novo_desc = prompt_input("Descrição", default=r[2] or "", obrigatorio=False)
                    cur.execute("UPDATE CORPORATIVA SET NomComerc=%s, NumFuncEmp=%s, DescriEmp=%s WHERE IDConta=%s;",
                                (novo_nome_emp, novo_num_func if novo_num_func else None, novo_desc if novo_desc else None, id_conta))
            conn.commit()
            print("\n✔ Conta atualizada com sucesso!")
        except Error as e:
            conn.rollback(); print(f"Erro: {e}")
        finally:
            conn.close()

    def tela_deletar(self):
        print("\n--- Deletar Conta ---")
        id_conta = prompt_input("ID da Conta")
        if prompt_input("Aviso Critico: Deletar permanentemente? (S/N)").upper() == 'S':
            conn = conectar_bd()
            if not conn: return
            try:
                with conn.cursor() as cur:
                    # EXPERIENCIAPROF tem FK sem CASCADE para CORPORATIVA (IDEmp).
                    # Nullifica o vinculo antes de deletar para evitar violacao de FK.
                    cur.execute("UPDATE EXPERIENCIAPROF SET IDEmp=NULL WHERE IDEmp=%s;", (id_conta,))
                    cur.execute("DELETE FROM CONTA WHERE IDConta=%s;", (id_conta,))
                conn.commit()
                print("\n✔ Operacao realizada com sucesso!")
            except Error as e:
                conn.rollback()
                print(f"\n✘ Erro na operacao: {e}")
            finally:
                conn.close()


# ════════════════════════════════════════════════════════════════
#  MENU PRINCIPAL ITERATIVO
# ════════════════════════════════════════════════════════════════

MODULOS = {
    "Conta": ContaCRUD(),
    "Post": PostCRUD,
    "Comentário": ComentarioCRUD,
    "Reagir a Post": ReagePostCRUD,
    "Vaga de Emprego": VagaCRUD,
    "Aplicação a Vaga": AplicaVagaCRUD,
    "Competência": CompetenciaCRUD,
    "Competência da Conta": PossCompCRUD,
    "Comp. de Experiência": ExpPossCompCRUD,
    "Experiência Prof.": ExpProfCRUD,
    "Formação Acadêmica": FormacaoCRUD,
    "Comp. de Formação": FormPossCompCRUD,
    "Idioma": IdiomaCRUD,
    "Idioma da Conta": FalaIdiomCRUD,
    "Conexão": ConexaoCRUD,
    "Setor de Empresa": SetorEmpCRUD,
}

OPERACOES = ["Criar", "Buscar", "Atualizar", "Deletar"]

def main():
    while True:
        limpar_tela()
        print("=== LinkedIn DB - Menu Principal CLI ===")
        print("[0] Sair")
        print("[C] Configurar Conexão DB")
        print("-" * 40)
        
        opcoes_modulos = list(MODULOS.keys())
        for i, mod in enumerate(opcoes_modulos, 1):
            print(f"[{i}] {mod}")
            
        esc = input("\nEscolha um módulo: ").strip().upper()
        
        if esc == '0':
            print("Saindo...")
            sys.exit(0)
        elif esc == 'C':
            tela_configuracao()
            continue
            
        try:
            idx = int(esc) - 1
            if 0 <= idx < len(opcoes_modulos):
                mod_nome = opcoes_modulos[idx]
                mod_obj = MODULOS[mod_nome]
                
                while True:
                    limpar_tela()
                    print(f"=== Operações: {mod_nome} ===")
                    print("[0] Voltar")
                    
                    # Filtra apenas os métodos que existem na classe selecionada
                    op_disponiveis = []
                    for op in OPERACOES:
                        if hasattr(mod_obj, f"tela_{op.lower()}"):
                            op_disponiveis.append(op)
                            
                    for j, op in enumerate(op_disponiveis, 1):
                        print(f"[{j}] {op}")
                            
                    op_esc = input("\nEscolha a operação: ").strip()
                    if op_esc == '0': break
                    
                    try:
                        op_idx = int(op_esc) - 1
                        if 0 <= op_idx < len(op_disponiveis):
                            nome_metodo = f"tela_{op_disponiveis[op_idx].lower()}"
                            getattr(mod_obj, nome_metodo)()
                            input("\nPressione Enter para continuar...")
                        else:
                            print("Opção inválida.")
                            input()
                    except ValueError:
                        pass
        except ValueError:
            pass

if __name__ == "__main__":
    main()