
<div align="center">

```
 ██╗     ██╗███╗   ██╗██╗  ██╗███████╗██████╗ ██╗███╗   ██╗
 ██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██║████╗  ██║
 ██║     ██║██╔██╗ ██║█████╔╝ █████╗  ██║  ██║██║██╔██╗ ██║
 ██║     ██║██║╚██╗██║██╔═██╗ ██╔══╝  ██║  ██║██║██║╚██╗██║
 ███████╗██║██║ ╚████║██║  ██╗███████╗██████╔╝██║██║ ╚████║
 ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝
```

**Interface CLI para interação com banco de dados relacional inspirado no LinkedIn**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-336791?style=flat-square&logo=postgresql)
![psycopg2](https://img.shields.io/badge/psycopg2-2.9%2B-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

---

## Sobre o Projeto

Este projeto implementa uma **interface de linha de comando (CLI)** completa para gerenciar um banco de dados relacional modelado com base nas entidades do LinkedIn. A aplicação permite realizar operações **CRUD** (Create, Read, Update, Delete) sobre todas as 20 tabelas do schema.

O banco de dados cobre entidades como contas pessoais e corporativas, posts, comentários, vagas de emprego, competências, formações acadêmicas, experiências profissionais, idiomas e conexões entre usuários — totalizando suporte a **mais de 100.000 registros**.

---

## Autores

| Nome | GitHub |
|------|--------|
| José Pedro Dresch | [@josepedrodresch](https://github.com/Jose-Pedro-Dresch) |
| Phelipe Gabriel Lima da Silva | [@phelipegabriel](https://github.com/PhelipeGL17) |
| Murilo Granemann de Souza | [@murilogranemann](https://github.com/Granemann21) |
| Luis Eduardo Weigert Weiss | [@luiseduardo](https://github.com/LW-Weiss) 

---

## Estrutura do Repositório

```
linkedin-db/
├── app.py                 # Aplicação CLI principal
├── sql/
│   ├── schema.sql         # DDL: criação das tabelas e constraints
│   ├── inserts.sql        # DML: dados iniciais + carga massiva (100k+ registros)
│   └── indices.sql        # Demonstração de análise de índices com EXPLAIN ANALYZE
├── Dockerfile             # Imagem da aplicação Python
├── docker-compose.yml     # Orquestração: app + PostgreSQL
├── entrypoint.sh          # Script de inicialização do container
├── relational_schema.png  # Diagrama do esquema relacional
├── README.md
└── LICENSE
```

---

## Esquema Relacional

O banco é composto por **20 tabelas** organizadas em torno da entidade central `CONTA`:

![Esquema Relacional](relational_schema.png)

<details>
<summary>Ver lista completa de tabelas</summary>

| Tabela | Descrição |
|--------|-----------|
| `PAIS`, `ESTADO`, `CIDADE` | Localização geográfica |
| `CONTA` | Entidade central — toda conta tem email e senha |
| `PESSOAL` | Perfil pessoal (nome, sobrenome, título profissional) |
| `CORPORATIVA` | Perfil de empresa (nome comercial, setor, nº de funcionários) |
| `CORPORATIVA_SETOREMP` | Setores de atuação da empresa |
| `COMPETENCIA`, `POSSCOMP` | Competências e vínculo com contas pessoais |
| `IDIOMA`, `FALAIDIOM` | Idiomas e nível de proficiência por conta |
| `FORMACAOACAD`, `FORMPOSSCOMP` | Formação acadêmica e competências adquiridas |
| `EXPERIENCIAPROF`, `EXPPOSSCOMP` | Experiência profissional e competências relacionadas |
| `VAGAEMPREGO`, `APLICAAVAGA` | Vagas publicadas por empresas e candidaturas |
| `POST`, `COMENTARIO`, `REAGEPOST` | Feed social: posts, comentários e reações |
| `CONEXAO` | Rede de conexões entre perfis pessoais |

</details>

---

## Requisitos

### Sistema Operacional
- Linux, macOS ou Windows

### PostgreSQL
- PostgreSQL **13 ou superior** instalado e rodando

### Dependências Python

Instale via pip:

```bash
pip install psycopg2-binary
```

---

## Como Rodar

### 0. Clone o repositório

```bash
git clone https://github.com/Jose-Pedro-Dresch/bd_fase_4_crud_implementation.git
cd bd_fase_4_crud_implementation
```

Há duas formas de rodar o projeto: via **Docker** (recomendado, funciona em qualquer ambiente incluindo Codespaces) ou **localmente** com PostgreSQL instalado na máquina.

---

### Opção 1 — Docker (recomendado)

Esta é a forma mais simples. Com um único comando, o Docker sobe o PostgreSQL, cria o banco, aplica o schema, carrega todos os dados e abre a CLI automaticamente. Não é necessário instalar o PostgreSQL nem configurar nada manualmente.

#### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) instalado (já incluso no Docker Desktop)

> No **GitHub Codespaces**, o Docker já está disponível por padrão — nenhuma instalação adicional é necessária.

#### Suba o ambiente completo

```bash
docker compose up --build
```

Isso irá:
1. Construir a imagem Python com todas as dependências
2. Subir o container PostgreSQL com o banco `linkedin` já criado
3. Aplicar o `schema.sql` e o `inserts.sql` automaticamente
4. Aguardar o banco estar pronto e abrir a CLI

> Na **primeira execução**, a carga massiva de ~100.000 registros pode levar alguns minutos. As execuções seguintes são instantâneas pois os dados ficam persistidos no volume `postgres_data`.

#### Nas próximas execuções

Como os dados já estão no volume, basta rodar:

```bash
docker compose up
```

#### Resetar o banco do zero

Se quiser apagar tudo e recarregar os dados:

```bash
docker compose down -v
docker compose up --build
```

---

### Opção 2 — Instalação local

Use esta opção se preferir rodar sem Docker, com PostgreSQL instalado diretamente na máquina.

#### Pré-requisitos

- Python **3.8 ou superior**
- PostgreSQL **13 ou superior**
- Dependência Python:

```bash
pip install psycopg2-binary
```

#### Configure o banco de dados

Crie o banco no PostgreSQL:

```bash
sudo -u postgres psql -c "CREATE DATABASE linkedin;"
```

Aplique o schema:

```bash
sudo -u postgres psql -d linkedin -f ./sql/schema.sql
```

Carregue os dados iniciais e a carga massiva:

```bash
sudo -u postgres psql -d linkedin -f ./sql/inserts.sql
```

> A carga massiva insere **~100.000 contas**, **~10.000 empresas** e dados relacionados. O processo pode levar alguns minutos dependendo do hardware.

#### Execute a aplicação

```bash
python3 app.py
```

Ao iniciar, você verá a splash screen com informações do sistema e da conexão. Se precisar alterar as credenciais do banco (host, porta, usuário, senha), pressione **`C`** no menu principal para acessar a tela de configuração.

**Credenciais padrão:**

| Parâmetro | Valor padrão |
|-----------|-------------|
| Host      | `localhost`  |
| Porta     | `5432`       |
| Banco     | `linkedin`   |
| Usuário   | `postgres`   |
| Senha     | `123`        |

---

## Navegação na CLI

```
Menu Principal
├── [1]  Conta
├── [2]  Post
├── [3]  Comentário
├── [4]  Reagir a Post
├── [5]  Vaga de Emprego
├── [6]  Aplicação a Vaga
├── [7]  Competência
├── [8]  Competência da Conta
├── [9]  Comp. de Experiência
├── [10] Experiência Prof.
├── [11] Formação Acadêmica
├── [12] Comp. de Formação
├── [13] Idioma
├── [14] Idioma da Conta
├── [15] Conexão
├── [16] Setor de Empresa
├── [C]  Configurar conexão DB
└── [0]  Sair
```

Dentro de cada módulo, as operações disponíveis são exibidas como:

```
[1] ✚ Criar    [2] 🔍 Buscar    [3] ✎ Atualizar    [4] ✖ Deletar
```

---

## Exemplos de Uso (CRUD)

Os exemplos abaixo usam a conta pessoal **Bruno Silva** (`IDConta = 2`) e a empresa **TechLink Solutions** (`IDConta = 1`), ambas presentes nos dados iniciais.

---

### CREATE — Criar um Post

No menu principal, selecione **`[2] Post`**, depois **`[1] ✚ Criar`**.

```
▶ Criar Post
──────────────────────────────────────────────

› Filtrar CONTA (Enter p/ listar): bruno
  [1] 2 - bruno@gmail.com

› Opção: 1

› Conteúdo do Post: Acabei de concluir minha certificação em AWS!
› Visibilidade (PUBLICO/PRIVADO) [PUBLICO]: PUBLICO

  ✔  Operação realizada com sucesso!
```

**Equivalente SQL:**
```sql
INSERT INTO POST (DtPubliPost, ConteudoPost, NivelVisib, IDConta)
VALUES (CURRENT_TIMESTAMP, 'Acabei de concluir minha certificação em AWS!', 'PUBLICO', 2);
```

---

### READ — Buscar Experiências Profissionais

No menu principal, selecione **`[10] Experiência Prof.`**, depois **`[2] 🔍 Buscar`**.

```
▶ Buscar Experiências
──────────────────────────────────────────────

› Filtrar PESSOAL (Enter p/ listar): Bruno
  [1] 2 - Bruno

› Opção: 1

  ┌────────────────────────────────────────────────────────────┐
  │ ID:2 | Data Enginner @ TechLink Solutions
  │ Tipo: CLT | 2023-06-01 → 2025-01-15
  │ Descrição: Liderou migração de pipelines para cloud.
  └────────────────────────────────────────────────────────────┘
```

**Equivalente SQL:**
```sql
SELECT e.IDExp, e.TituloExp, e.TipoEmpregoExp, e.DtInicioExp, e.DtFimExp,
       e.DescAtv, c.NomComerc
FROM EXPERIENCIAPROF e
LEFT JOIN CORPORATIVA c ON e.IDEmp = c.IDConta
WHERE e.IDConta = 2;
```

---

### UPDATE — Atualizar Status de uma Candidatura

No menu principal, selecione **`[6] Aplicação a Vaga`**, depois **`[3] ✎ Atualizar`**.

```
▶ Atualizar Aplicação
──────────────────────────────────────────────

› ID da Vaga: 1
› ID da Conta: 2

▶ Novo Status (Atual: Enviada)
  [1] Enviada
  [2] Em Analise
  [3] Aprovada
  [4] Recusada

› Opção: 3

  ✔  Operação realizada com sucesso!
```

**Equivalente SQL:**
```sql
UPDATE APLICAAVAGA
SET SttusAplccao = 'Aprovada'
WHERE IDVagaEmp = 1 AND IDConta = 2;
```

---

### DELETE — Remover uma Conexão

No menu principal, selecione **`[15] Conexão`**, depois **`[4] ✖ Deletar`**.

```
▶ Remover Conexão
──────────────────────────────────────────────

› ID da Conta 1: 2
› ID da Conta 2: 3
› Confirmar remoção? (S/N): S

  ✔  Operação realizada com sucesso!
```

**Equivalente SQL:**
```sql
DELETE FROM CONEXAO
WHERE IDConta_1 = 2 AND IDConta_2 = 3;
```

---

## Demonstração de Índices

O arquivo `indices.sql` demonstra o ganho de performance ao criar um índice na coluna `NomPsso` da tabela `PESSOAL`, que conta com **~90.000 registros** inseridos pela carga massiva.

### Execute o arquivo:

**Via Docker:**
```bash
docker compose exec db psql -U postgres -d linkedin -f /dev/stdin < ./sql/indices.sql
```

**Localmente:**
```bash
sudo -u postgres psql -d linkedin -f ./sql/indices.sql
```

### Resultado esperado

**Sem índice** — PostgreSQL realiza um *Sequential Scan* varrendo toda a tabela:

```
Seq Scan on pessoal  (cost=0.00..1845.42 rows=882 width=7) (actual time=0.010..6.498 rows=888 loops=1)
   Filter: ((nompsso)::text = 'Julio'::text)
   Rows Removed by Filter: 89146
Planning Time: 0.318 ms
Execution Time: 6.556 ms
```

**Com índice** — PostgreSQL usa *Index Scan*, buscando diretamente as linhas relevantes:

```sql
CREATE INDEX idx_conta ON PESSOAL(NomPsso);
```

```
Index Only Scan using idx_conta on pessoal  (cost=0.29..19.73 rows=882 width=7) (actual time=0.043..0.094 rows=888 loops=1)
   Index Cond: (nompsso = 'Julio'::text)
   Heap Fetches: 0
Planning Time: 0.283 ms
Execution Time: 0.142 ms
```

> O tempo de execução cai de **~5.56ms para ~0.14ms** — uma melhoria de aproximadamente **40×** para buscas por nome exato em tabelas de grande volume.

---

## Observações de Segurança

- A FK `EXPERIENCIAPROF.IDEmp → CORPORATIVA.IDConta` foi declarada sem `ON DELETE CASCADE` intencionalmente: ao deletar uma empresa, o histórico de experiência profissional dos usuários é preservado (apenas o vínculo com a empresa é desfeito, setando `IDEmp = NULL`). A aplicação trata esse caso automaticamente.
