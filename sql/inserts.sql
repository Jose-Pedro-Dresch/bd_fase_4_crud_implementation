\encoding UTF8
-- To avoid getting duplicated data; and restart ID counter
TRUNCATE TABLE IDIOMA, COMPETENCIA, CONTA, CIDADE, ESTADO, PAIS RESTART IDENTITY CASCADE;

INSERT INTO PAIS (NomPais)
VALUES 
('Brasil'),
('Estados Unidos'),
('Canadá'),
('Argentina'),
('México'),
('Alemanha'),
('Índia'),
('Japão'),
('Austrália');

INSERT INTO ESTADO (NomEstado, IDPais)
VALUES
('Santa Catarina', 1),
('São Paulo', 1),
('Acre', 1),
('Alagoas', 1),
('Amapá', 1),
('Amazonas', 1),
('Bahia', 1),
('Ceará', 1),
('Distrito Federal', 1),
('Espírito Santo', 1),
('Goiás', 1),
('Maranhão', 1),
('Mato Grosso', 1),
('Mato Grosso do Sul', 1),
('Minas Gerais', 1),
('Pará', 1),
('Paraíba', 1),
('Paraná', 1),
('Pernambuco', 1),
('Piauí', 1),
('Rio de Janeiro', 1),
('Rio Grande do Norte', 1),
('Rio Grande do Sul', 1),
('Rondônia', 1),
('Roraima', 1),
('Sergipe', 1),
('Tocantins', 1);

INSERT INTO CIDADE (NomCidade, IDEstado)
VALUES
('Florianópolis', 1),
('Joinville', 1),
('São Paulo', 2),
('Rio Branco', 3),
('Cruzeiro do Sul', 3),
('Maceió', 4),
('Arapiraca', 4),
('Macapá', 5),
('Santana', 5),
('Manaus', 6),
('Parintins', 6),
('Salvador', 7),
('Feira de Santana', 7),
('Fortaleza', 8),
('Juazeiro do Norte', 8),
('Brasília', 9),
('São Luís', 10),
('Imperatriz', 10),
('Vitória', 11),
('Vila Velha', 11),
('Goiânia', 12),
('Anápolis', 12),
('Cuiabá', 13),
('Rondonópolis', 13),
('Campo Grande', 14),
('Dourados', 14),
('Belo Horizonte', 15),
('Uberlândia', 15),
('Belém', 16),
('Santarém', 16),
('João Pessoa', 17),
('Campina Grande', 17),
('Curitiba', 18),
('Londrina', 18),
('Recife', 19),
('Olinda', 19),
('Teresina', 20),
('Parnaíba', 20),
('Rio de Janeiro', 21),
('Niterói', 21),
('Natal', 22),
('Mossoró', 22),
('Porto Alegre', 23),
('Caxias do Sul', 23),
('Porto Velho', 24),
('Ji-Paraná', 24),
('Boa Vista', 25),
('Pacaraima', 25),
('Aracaju', 26),
('Nossa Senhora do Socorro', 26),
('Palmas', 27),
('Araguaína', 27);

INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade)
VALUES
('ana@techlink.com', '123', '2025-01-10', 3),
('bruno@gmail.com', '123', '2026-03-10', 1),
('carla@gmail.com', '123', '2026-03-11', 1),
('diego@gmail.com', '123', '2026-03-11', 1),
('eduardo@gmail.com', '123', '2024-08-01', 2),
('fernanda@gmail.com', '123', '2023-04-20', 3),
('arnaldobertoldi@gmail.com', '123', '2026-03-13', 1),
('marlonalves@gmail.com', '123', '2026-03-13', 1),
('israelmarcelino@gmail.com', '123', '2026-03-13', 1),
('recruiter@techlink.com', '123', '2024-02-10', 3),
('thais@dataworks.com', '123', '2024-11-15', 12),
('lucas@greencloud.com', '123', '2024-12-01', 16),
('mariana@educatech.com', '123', '2025-02-20', 20),
('felipe@healthnet.com', '123', '2025-03-03', 24),
('isabela@sustentec.com', '123', '2025-03-10', 28),
('rodrigo@ecommercepro.com', '123', '2025-04-17', 32),
('vanessa@consultoria360.com', '123', '2025-05-05', 36),
('alessandro@logipower.com', '123', '2025-05-18', 40),
('camila@markdigital.com', '123', '2025-06-01', 44),
('pedro@seginfotech.com', '123', '2025-06-12', 48),
('laura@gaminglab.com', '123', '2025-06-20', 15),
('joao@agroconnect.com', '123', '2025-07-01', 19),
('daniela@bioplus.com', '123', '2025-07-10', 23),
('caio@retailwave.com', '123', '2025-08-03', 29),
('aline@infrahub.com', '123', '2025-08-22', 33),
('marcos@analyticslab.com', '123', '2025-09-10', 37),
('tatiana@aitech.com', '123', '2025-10-01', 41),
('edu@telecomplus.com', '123', '2025-10-15', 45),
('sophia@energygrid.com', '123', '2025-11-02', 49),
('henrique@designmind.com', '123', '2025-11-20', 6),
('natasha@peerio.com', '123', '2025-12-04', 7),
('rafael@finovate.com', '123', '2025-12-15', 8),
('patricia@healthbridge.com', '123', '2026-01-05', 9),
('bruno2@educonnect.com', '123', '2026-01-20', 13),
('maria@agrotech.com', '123', '2026-02-02', 17),
('alex@cloudfirst.com', '123', '2026-02-10', 21),
('julia@mobilityhub.com', '123', '2026-02-14', 25),
('fernando@smartcity.com', '123', '2026-02-18', 30),
('samara@biotek.com', '123', '2026-02-22', 34),
('henri@foodtech.com', '123', '2026-02-25', 38),
('livia@cyberguard.com', '123', '2026-03-01', 42),
('guilherme@logibrasil.com', '123', '2026-03-02', 46),
('vania@eventech.com', '123', '2026-03-04', 50),
('leonardo@meditech.com', '123', '2026-03-05', 11),
('paula@gamestudio.com', '123', '2026-03-06', 14),
('roberto@sustainabiz.com', '123', '2026-03-06', 18),
('patriciab@devopsnow.com', '123', '2026-03-07', 22),
('adriana@hrsmart.com', '123', '2026-03-07', 26),
('gustavo@logiexpress.com', '123', '2026-03-08', 31),
('marina@solaredge.com', '123', '2026-03-09', 35),
('luana@techeduca.com', '123', '2026-03-11', 39),
('rafa@fintechplus.com', '123', '2026-03-12', 43),
('andrea@medisys.com', '123', '2026-03-12', 47),
('henrique2@mobihub.com', '123', '2026-03-13', 51),
('patricia2@smartlog.com', '123', '2026-03-13', 52);

INSERT INTO PESSOAL (IDConta, NomPsso, SobnomPsso, TtloProfPsso)
VALUES
(2, 'Bruno', 'Silva', 'Data Engineer'),
(3, 'Carla', 'Mendes', 'Backend Developer'),
(4, 'Diego', 'Souza', 'DevOps Engineer'),
(5, 'Eduardo', 'Lima', 'Senior Recruiter'),
(6, 'Fernanda', 'Rocha', 'Software Architect'),
(7, 'Arnaldo', 'Bertoldi', 'Data Engineer'),
(8, 'Marlon', 'Alves', 'Data Engineer'),
(9, 'Israel', 'Marcelino', 'Data Engineer'),
(10, 'Patricia', 'Almeida', 'Tech Recruiter'),
(11, 'Thais', 'Silveira', 'Product Manager'),
(12, 'Lucas', 'Gomes', 'Full Stack Developer'),
(13, 'Mariana', 'Costa', 'Data Scientist'),
(14, 'Felipe', 'Rezende', 'UX Designer'),
(15, 'Isabela', 'Fernandes', 'Marketing Analyst'),
(16, 'Rodrigo', 'Soares', 'Cybersecurity Analyst'),
(17, 'Vanessa', 'Pereira', 'QA Engineer'),
(18, 'Alessandro', 'Mendes', 'Cloud Architect'),
(19, 'Camila', 'Lima', 'HR Business Partner'),
(20, 'Pedro', 'Oliveira', 'Logistics Coordinator'),
(21, 'Laura', 'Barbosa', 'Game Developer'),
(22, 'João', 'Nogueira', 'Agricultural Engineer'),
(23, 'Daniela', 'Ribeiro', 'Biotech Researcher'),
(24, 'Caio', 'Martins', 'Retail Operations Manager'),
(25, 'Aline', 'Farias', 'Infrastructure Engineer'),
(26, 'Marcos', 'Carvalho', 'Analytics Consultant'),
(27, 'Tatiana', 'Santos', 'AI Researcher'),
(28, 'Edu', 'Silva', 'Network Engineer'),
(29, 'Sophia', 'Dias', 'Energy Specialist'),
(30, 'Henrique', 'Pinto', 'Visual Designer'),
(31, 'Natasha', 'Campos', 'HR Recruiter'),
(32, 'Rafael', 'Almeida', 'Finance Analyst'),
(33, 'Patricia', 'Barros', 'Education Specialist'),
(34, 'Bruno', 'Nunes', 'Logistics Manager'),
(35, 'Maria', 'Moura', 'Customer Success Lead');

INSERT INTO CORPORATIVA (IDConta, NomComerc, NumFuncEmp, DescriEmp)
VALUES
(1, 'TechLink Solutions', 500, 'Empresa de tecnologia especializada em dados'),
(36, 'DataWorks', 120, 'Empresa de análise de dados e automação'),
(37, 'GreenCloud', 80, 'Soluções em nuvem sustentável'),
(38, 'EducaTech', 45, 'Plataforma de educação online'),
(39, 'HealthNet', 160, 'Serviços de saúde digital'),
(40, 'SustenTec', 65, 'Tecnologia para sustentabilidade ambiental'),
(41, 'EcommercePro', 95, 'Loja online de produtos de nicho'),
(42, 'Consultoria360', 50, 'Consultoria empresarial e digital'),
(43, 'LogiPower', 70, 'Logística integrada e software de rotas'),
(44, 'MarkDigital', 40, 'Agência de marketing digital'),
(45, 'SegInfoTech', 55, 'Segurança da informação e proteção de dados'),
(46, 'GamingLab', 110, 'Desenvolvimento de jogos e entretenimento'),
(47, 'AgroConnect', 130, 'Tecnologia para o agronegócio'),
(48, 'BioPlus', 90, 'Biotecnologia aplicada à saúde'),
(49, 'RetailWave', 75, 'Soluções de varejo omnichannel'),
(50, 'InfraHub', 80, 'Infraestrutura de TI e data centers'),
(51, 'AnalyticsLab', 85, 'Consultoria em analytics e dashboards'),
(52, 'AITech', 66, 'Inteligência artificial para empresas'),
(53, 'TelecomPlus', 140, 'Operadora de telecomunicações'),
(54, 'EnergyGrid', 100, 'Energia renovável e smart grids'),
(55, 'DesignMind', 30, 'Estúdio de design e inovação');

INSERT INTO CORPORATIVA_SETOREMP (SetorEmp, IDConta)
VALUES
('Tecnologia', 1),
('FinTech', 36),
('Cloud', 37),
('Educação', 38),
('Saúde', 39),
('Sustentabilidade', 40),
('E-commerce', 41),
('Consultoria', 42),
('Logística', 43),
('Marketing Digital', 44),
('Segurança da Informação', 45),
('Games', 46),
('Agronegócio', 47),
('BioTech', 48),
('Retail', 49),
('Infraestrutura', 50),
('Analytics', 51),
('IA', 52),
('Telecom', 53),
('Energia', 54),
('Design', 55);

INSERT INTO COMPETENCIA (NomeComp)
VALUES
('Python'),
('SQL'),
('Docker'),
('Kubernetes'),
('Machine Learning'),
('Java'),
('JavaScript'),
('React'),
('Node.js'),
('AWS'),
('Azure'),
('Google Cloud'),
('CI/CD'),
('UX Design'),
('Product Management');

INSERT INTO IDIOMA (NomeIdioma)
VALUES
('Português'),
('Inglês'),
('Espanhol'),
('Alemão'),
('Italiano'),
('Francês');

INSERT INTO EXPERIENCIAPROF
(TituloExp, TipoEmpregoExp, DtInicioExp, DtFimExp, DescAtv, IDConta, IDEmp)
VALUES
('Recruiter', 'CLT', '2024-01-01', NULL,'Recrutamento técnico', 5, 1),
('Software Architect', 'CLT', '2023-01-01', '2026-02-20','Arquitetura de sistemas distribuídos', 6, 1),
('Data Engineer', 'CLT', '2025-01-01', NULL,'Pipelines de dados', 2, 1),
('Data Scientist', 'PJ', '2023-07-01', NULL, 'Modelagem preditiva e pipelines', 3, 36),
('Senior Developer', 'CLT', '2022-04-01', '2025-12-31', 'Desenvolvimento de aplicações web', 4, 37),
('Content Strategist', 'PJ', '2021-03-01', '2024-08-01', 'Campanhas digitais e posicionamento de marca', 5, 44),
('Performance Analyst', 'CLT', '2020-05-01', '2023-12-01', 'Otimização de resultados online', 7, 44),
('Product Designer', 'CLT', '2021-08-01', NULL, 'Design de interfaces e experiência', 8, 38),
('IT Specialist', 'PJ', '2022-06-01', NULL, 'Gerenciamento de infraestrutura de TI', 9, 50),
('Finance Manager', 'CLT', '2019-02-01', '2022-12-01', 'Gestão financeira e orçamento', 10, 49),
('Product Owner', 'CLT', '2022-01-01', NULL, 'Gestão de roadmap e stakeholders', 11, 36),
('Data Analyst', 'PJ', '2023-01-10', NULL, 'Análises de dados e visualizações', 12, 51),
('UX Researcher', 'CLT', '2021-02-01', '2024-05-30', 'Pesquisa com usuários e usabilidade', 13, 44),
('Operations Analyst', 'CLT', '2020-07-01', NULL, 'Planejamento operacional e métricas', 14, 49),
('Marketing Coordinator', 'PJ', '2022-03-01', '2025-03-01', 'Campanhas de comunicação', 15, 44),
('Cloud Engineer', 'CLT', '2023-09-01', NULL, 'Arquitetura de nuvem e automação', 16, 37),
('Quality Analyst', 'PJ', '2021-11-01', NULL, 'Testes e garantia de qualidade de software', 17, 42),
('Infrastructure Consultant', 'CLT', '2022-10-01', NULL, 'Projetos de infraestrutura de TI', 18, 50),
('People Partner', 'CLT', '2023-05-01', NULL, 'Gestão de talentos e cultura', 19, 38),
('Logistics Analyst', 'PJ', '2020-04-01', NULL, 'Otimização de cadeia de suprimentos', 20, 43),
('Game Programmer', 'PJ', '2022-08-01', NULL, 'Desenvolvimento de jogos e simulações', 21, 46),
('Agronomy Specialist', 'CLT', '2019-09-01', NULL, 'Soluções agrícolas e tecnologia', 22, 47),
('Biotech Researcher', 'CLT', '2021-01-01', NULL, 'Pesquisa de biotecnologia aplicada', 23, 48),
('Retail Supervisor', 'CLT', '2020-06-01', NULL, 'Gerência de operações de loja', 24, 49),
('Network Engineer', 'CLT', '2021-04-01', NULL, 'Administração de redes corporativas', 25, 50),
('Analytics Specialist', 'CLT', '2022-09-01', NULL, 'Reportes e dashboards executivos', 26, 51),
('AI Specialist', 'PJ', '2023-02-01', NULL, 'Modelos de aprendizado de máquina', 27, 52),
('Network Consultant', 'CLT', '2020-01-01', '2023-12-01', 'Implementação de redes e segurança', 28, 53),
('Energy Consultant', 'PJ', '2021-07-01', NULL, 'Projetos de energia renovável', 29, 54),
('Visual Designer', 'PJ', '2022-03-01', NULL, 'Design de campanhas e identidade visual', 30, 55),
('HR Specialist', 'CLT', '2022-11-01', NULL, 'Recrutamento e desenvolvimento', 31, 38),
('Financial Consultant', 'PJ', '2023-05-01', NULL, 'Estratégia financeira corporativa', 32, 36),
('Education Manager', 'CLT', '2021-01-01', NULL, 'Operações de educação corporativa', 33, 38),
('Logistics Planner', 'CLT', '2022-02-01', NULL, 'Planejamento logístico e frota', 34, 43),
('Customer Success Analyst', 'PJ', '2023-10-01', NULL, 'Relacionamento com clientes e retenção', 35, 41);

INSERT INTO VAGAEMPREGO
(TtloVaga, DescriVaga, FormatoTrabVaga, DtCrcaoVaga, IDConta)
VALUES
('Senior Data Engineer','Vaga estratégica para engenharia de dados','REMOTO','2026-03-14',1),
('Analista de Dados', 'Análise e reports para negócios digitais', 'HÍBRIDO', '2026-02-10', 36),
('Engenheiro de Nuvem', 'Projeto de infraestrutura em AWS e Azure', 'REMOTO', '2026-02-12', 37),
('Especialista em UX', 'Melhoria da experiência do usuário em plataforma', 'HÍBRIDO', '2026-02-14', 38),
('Consultor de Segurança', 'Proteção de dados e auditoria de sistemas', 'REMOTO', '2026-02-16', 45),
('Desenvolvedor Full Stack', 'Aplicações web com React e Node.js', 'HÍBRIDO', '2026-02-18', 41),
('Engenheiro de Infraestrutura', 'Administração de data center e rede', 'PRESENCIAL', '2026-02-20', 50),
('Coordenador de Marketing', 'Campanhas digitais e comunicação integrada', 'REMOTO', '2026-02-22', 44),
('Especialista em Produtos', 'Gestão de produtos de tecnologia', 'HÍBRIDO', '2026-02-24', 36),
('Desenvolvedor de Jogos', 'Criação de jogos multiplataforma', 'REMOTO', '2026-02-26', 46),
('Analista de Energia Renovável', 'Projetos de energia inteligente', 'PRESENCIAL', '2026-02-28', 54),
('Especialista em Dados de Saúde', 'Analytics para soluções médicas', 'REMOTO', '2026-03-05', 39),
('Desenvolvedor Mobile', 'Aplicativos nativos para clientes financeiros.', 'REMOTO', '2026-03-02', 41),
('Arquiteto de Software', 'Plataforma de integração de dados em nuvem.', 'HÍBRIDO', '2026-03-03', 37),
('Especialista em DevOps', 'Automação de pipeline e infraestrutura.', 'REMOTO', '2026-03-04', 50),
('Analista de Marketing de Conteúdo', 'Produção de conteúdo digital para B2B.', 'REMOTO', '2026-03-05', 44),
('Gerente de Produto', 'Gestão de produtos digitais estratégicos.', 'HÍBRIDO', '2026-03-06', 36),
('Engenheiro de Software de Jogos', 'Pipeline de desenvolvimento de jogos.', 'REMOTO', '2026-03-07', 46),
('Analista de Logística', 'Planejamento de transporte urbano.', 'HÍBRIDO', '2026-03-08', 43),
('Especialista em Saúde Digital', 'Plataforma de telemedicina e monitoramento.', 'REMOTO', '2026-03-09', 39),
('Analista de Energia', 'Projetos de energia solar e eficiência.', 'PRESENCIAL', '2026-03-10', 54),
('Designer de Produto', 'Design de soluções físicas e digitais.', 'HÍBRIDO', '2026-03-11', 55);

INSERT INTO APLICAAVAGA
(DtAplccao, SttusAplccao, IDVagaEmp, IDConta)
VALUES
('2026-03-14 10:00:00', 'EM_ANALISE', 1, 2),
('2026-03-14 10:01:00', 'EM_ANALISE', 1, 3),
('2026-03-14 10:02:00', 'EM_ANALISE', 1, 4),
('2026-03-14 10:03:00', 'EM_ANALISE', 1, 7),
('2026-03-14 10:04:00', 'EM_ANALISE', 1, 8),
('2026-03-14 10:05:00', 'EM_ANALISE', 1, 9),
('2026-02-11 09:15:00', 'EM_ANALISE', 2, 3),
('2026-02-11 09:20:00', 'EM_ANALISE', 2, 12),
('2026-02-12 10:05:00', 'ENTREVISTA', 3, 13),
('2026-02-13 11:30:00', 'EM_ANALISE', 4, 16),
('2026-02-14 14:00:00', 'EM_ANALISE', 5, 17),
('2026-02-15 15:10:00', 'REJEITADA', 6, 18),
('2026-02-16 08:45:00', 'ACEITA', 7, 19),
('2026-02-17 16:00:00', 'EM_ANALISE', 8, 20),
('2026-02-18 12:20:00', 'EM_ANALISE', 9, 21),
('2026-02-19 13:10:00', 'EM_ANALISE', 10, 22),
('2026-02-20 14:50:00', 'EM_ANALISE', 11, 23),
('2026-02-21 10:00:00', 'EM_ANALISE', 1, 11),
('2026-02-21 10:02:00', 'EM_ANALISE', 1, 12),
('2026-02-21 10:04:00', 'EM_ANALISE', 1, 13),
('2026-02-21 10:06:00', 'EM_ANALISE', 1, 14),
('2026-02-21 10:08:00', 'EM_ANALISE', 1, 15),
('2026-02-21 10:10:00', 'EM_ANALISE', 1, 16),
('2026-02-22 09:00:00', 'EM_ANALISE', 2, 24),
('2026-02-22 09:05:00', 'EM_ANALISE', 3, 25),
('2026-02-22 09:10:00', 'EM_ANALISE', 4, 26),
('2026-02-23 11:00:00', 'EM_ANALISE', 5, 27),
('2026-02-23 11:05:00', 'EM_ANALISE', 6, 28),
('2026-02-23 11:10:00', 'EM_ANALISE', 7, 29),
('2026-02-24 09:00:00', 'EM_ANALISE', 8, 30),
('2026-02-24 09:15:00', 'EM_ANALISE', 9, 31),
('2026-02-24 09:20:00', 'EM_ANALISE', 10, 32),
('2026-02-24 09:25:00', 'EM_ANALISE', 11, 33),
('2026-02-24 09:30:00', 'EM_ANALISE', 2, 34),
('2026-02-24 09:35:00', 'EM_ANALISE', 3, 35);

INSERT INTO POST
(DtPubliPost, ConteudoPost, NivelVisib, IDConta)
VALUES
('2026-03-14 09:00:00','Estamos contratando Senior Data Engineers!','PUBLICO',1),
('2026-02-10 08:00:00', 'Novo artigo sobre Cloud Sustainability.', 'PUBLICO', 37),
('2026-02-11 09:30:00', 'Buscamos talentos em UX para plataforma global.', 'PUBLICO', 38),
('2026-02-12 10:45:00', 'Junte-se ao time de segurança da informação.', 'PUBLICO', 45),
('2026-02-13 11:20:00', 'Aumente seu impacto como coordenador de marketing.', 'PUBLICO', 44),
('2026-02-14 12:00:00', 'Estamos com vaga aberta para DevOps.', 'PUBLICO', 50),
('2026-02-15 12:30:00', 'Participe do nosso time de dados e analytics.', 'PUBLICO', 51),
('2026-02-16 13:00:00', 'O mercado de games está crescendo: venha para o GamingLab.', 'PUBLICO', 46),
('2026-02-17 13:30:00', 'Projeto em energia renovável começa em breve.', 'PUBLICO', 54),
('2026-02-18 14:00:00', 'Soluções de logística urbana para grandes cidades.', 'PUBLICO', 43),
('2026-02-19 14:30:00', 'Fintech com oportunidades para analistas financeiros.', 'PUBLICO', 36),
('2026-02-20 15:00:00', 'Educação digital inovadora procura talentos.', 'PUBLICO', 38),
('2026-02-21 15:30:00', 'TechLink busca Senior Data Engineers.', 'PUBLICO', 1),
('2026-02-22 16:00:00', 'Apresentando a nova plataforma de agronegócio.', 'PUBLICO', 47),
('2026-02-23 16:30:00', 'Evento online sobre inteligência artificial.', 'PUBLICO', 52),
('2026-02-24 17:00:00', 'Nosso time de retail está em expansão.', 'PUBLICO', 49),
('2026-02-25 17:30:00', 'Modernização de redes e infraestrutura.', 'PUBLICO', 50),
('2026-02-26 18:00:00', 'Consultoria para transformação digital.', 'PUBLICO', 42),
('2026-02-27 18:30:00', 'Convidamos designers para um projeto internacional.', 'PUBLICO', 55),
('2026-02-28 19:00:00', 'A equipe de saúde digital está com vagas abertas.', 'PUBLICO', 39),
('2026-03-01 19:30:00', 'Time de energia inteligente contrata.', 'PUBLICO', 54);

INSERT INTO COMENTARIO
(ConteudoTxtCom, DtPubliCom, IDPost, IDConta)
VALUES
('Excelente oportunidade!', '2026-03-14 09:05:00', 1, 6),
('Empresa incrível!', '2026-03-14 09:06:00', 1, 7),
('Quero muito participar!', '2026-03-14 09:06:30', 1, 8),
('Processo seletivo top!', '2026-03-14 09:07:00', 1, 9),
('Excelente iniciativa!', '2026-02-10 08:15:00', 2, 11),
('Ótimo conteúdo sobre sustentabilidade.', '2026-02-10 08:20:00', 2, 15),
('Tenho experiência com nuvem e posso ajudar.', '2026-02-11 09:40:00', 3, 12),
('Quero saber mais sobre o programa.', '2026-02-11 09:50:00', 3, 17),
('A vaga parece perfeita para meu perfil.', '2026-02-12 10:55:00', 4, 13),
('Já participei de projetos parecidos.', '2026-02-12 11:05:00', 4, 16),
('Me interessei pela posição de segurança.', '2026-02-13 11:25:00', 5, 18),
('Como funciona o processo seletivo?', '2026-02-13 11:35:00', 5, 19),
('Tenho experiência em infraestrutura.', '2026-02-14 12:05:00', 6, 20),
('Excelente empresa para trabalhar.', '2026-02-14 12:10:00', 6, 13),
('Qual o perfil buscado?', '2026-02-15 12:35:00', 7, 21),
('Gosto muito do trabalho de vocês.', '2026-02-15 12:45:00', 7, 22),
('Tenho portfólio pronto.', '2026-02-16 13:05:00', 8, 23),
('Ótima oportunidade!', '2026-02-16 13:15:00', 8, 24),
('Trabalhei com projetos similares.', '2026-02-17 13:35:00', 9, 25),
('Faço parte da área de logística.', '2026-02-17 13:45:00', 9, 26),
('A vaga parece desafiadora.', '2026-02-18 14:05:00', 10, 27),
('Fico feliz em ver essa abertura.', '2026-02-18 14:15:00', 10, 28),
('Adoraria participar do processo.', '2026-02-19 14:35:00', 11, 29),
('Tenho experiência em saúde digital.', '2026-02-19 14:45:00', 11, 30),
('Oportunidade ótima para designers.', '2026-02-20 15:05:00', 12, 31),
('Parabéns pela publicação.', '2026-02-20 15:15:00', 12, 32),
('Gostaria de me conectar com vocês.', '2026-02-21 15:35:00', 13, 33),
('Que iniciativa interessante.', '2026-02-21 15:45:00', 13, 34),
('Excelente notícia para o setor.', '2026-02-22 16:05:00', 14, 35),
('Muito relevante para o mercado.', '2026-02-22 16:15:00', 14, 14),
('Conteúdo muito útil.', '2026-02-23 16:35:00', 15, 12),
('Adoro temas de IA.', '2026-02-23 16:45:00', 15, 27),
('Gostei do post.', '2026-02-24 17:05:00', 16, 25),
('Interessante projeto.', '2026-02-24 17:15:00', 16, 11),
('Ótima chance para profissionais.', '2026-02-25 17:35:00', 17, 16),
('Parabéns pela iniciativa.', '2026-02-25 17:45:00', 17, 18),
('Muito inspirador.', '2026-02-26 18:05:00', 18, 19),
('Quero saber mais.', '2026-02-26 18:15:00', 18, 15),
('Excelente para a comunidade.', '2026-02-27 18:35:00', 19, 20),
('Já participei de eventos similares.', '2026-02-27 18:45:00', 19, 21),
('Uma boa oportunidade para designers.', '2026-02-28 19:05:00', 20, 22),
('A vaga parece atraente.', '2026-02-28 19:15:00', 20, 23),
('Acho que posso contribuir bastante.', '2026-03-01 19:35:00', 21, 24),
('Projetos com energia são meu foco.', '2026-03-01 19:45:00', 21, 29),
('Gostaria de saber mais sobre as vagas.', '2026-03-02 08:10:00', 1, 14),
('Parabéns pela iniciativa da empresa.', '2026-03-02 08:12:00', 1, 17),
('Interessante essa oportunidade de produto.', '2026-03-03 09:05:00', 2, 16),
('Tenho case em nuvem híbrida.', '2026-03-03 09:10:00', 2, 18),
('Boa vaga em segurança da informação.', '2026-03-04 10:00:00', 3, 19),
('Gostaria de participar do processo seletivo.', '2026-03-04 10:05:00', 3, 20),
('Ótimo trabalho de marketing digital.', '2026-03-05 11:00:00', 4, 21),
('Tenho experiência com campanhas B2B.', '2026-03-05 11:05:00', 4, 22),
('Infraestrutura é meu foco.', '2026-03-06 12:00:00', 5, 23),
('Excelente oportunidade em produto.', '2026-03-06 12:05:00', 5, 24),
('Eu jogo e programo, adoraria essa vaga.', '2026-03-07 13:00:00', 6, 25),
('Trabalhei com engines similares.', '2026-03-07 13:05:00', 6, 26),
('Logística está em alta.', '2026-03-08 14:00:00', 7, 27),
('Tenho experiência em cadeia de suprimentos.', '2026-03-08 14:05:00', 7, 28),
('Vaga ótima para quem ama saúde digital.', '2026-03-09 15:00:00', 8, 29),
('Já implementei projetos similares.', '2026-03-09 15:05:00', 8, 30),
('Energia renovável é o futuro.', '2026-03-10 16:00:00', 9, 31),
('Trabalho com eficiência energética.', '2026-03-10 16:05:00', 9, 32),
('Design de produto é o que faço.', '2026-03-11 17:00:00', 10, 33),
('Quero fazer parte dessa equipe.', '2026-03-11 17:05:00', 10, 34);

INSERT INTO REAGEPOST
(DtReacao, TipoReacao, IDConta, IDPost)
VALUES
('2026-03-14 09:05:00', 'LIKE', 6, 1),
('2026-03-14 09:05:10', 'LIKE', 7, 1),
('2026-03-14 09:05:20', 'LIKE', 8, 1),
('2026-03-14 09:05:30', 'LIKE', 9, 1),
('2026-02-10 08:18:00', 'LIKE', 12, 2),
('2026-02-10 08:19:00', 'APOIO', 15, 2),
('2026-02-11 09:45:00', 'LIKE', 13, 3),
('2026-02-11 09:46:00', 'APOIO', 17, 3),
('2026-02-12 11:00:00', 'LIKE', 18, 4),
('2026-02-12 11:01:00', 'APOIO', 16, 4),
('2026-02-13 11:30:00', 'LIKE', 19, 5),
('2026-02-13 11:31:00', 'APOIO', 20, 5),
('2026-02-14 12:08:00', 'LIKE', 21, 6),
('2026-02-14 12:09:00', 'APOIO', 22, 6),
('2026-02-15 12:55:00', 'LIKE', 23, 7),
('2026-02-15 12:56:00', 'APOIO', 24, 7),
('2026-02-16 13:20:00', 'LIKE', 25, 8),
('2026-02-16 13:21:00', 'APOIO', 26, 8),
('2026-02-17 13:40:00', 'LIKE', 27, 9),
('2026-02-17 13:41:00', 'APOIO', 28, 9),
('2026-02-18 14:10:00', 'LIKE', 29, 10),
('2026-02-18 14:11:00', 'APOIO', 30, 10),
('2026-02-19 14:40:00', 'LIKE', 31, 11),
('2026-02-19 14:41:00', 'APOIO', 32, 11),
('2026-02-20 15:05:00', 'LIKE', 33, 12),
('2026-02-20 15:06:00', 'APOIO', 34, 12),
('2026-02-21 15:40:00', 'LIKE', 35, 13),
('2026-02-21 15:41:00', 'APOIO', 11, 13),
('2026-02-22 16:10:00', 'LIKE', 12, 14),
('2026-02-22 16:11:00', 'APOIO', 13, 14),
('2026-02-23 16:40:00', 'LIKE', 14, 15),
('2026-02-23 16:41:00', 'APOIO', 15, 15),
('2026-02-24 17:10:00', 'LIKE', 16, 16),
('2026-02-24 17:11:00', 'APOIO', 17, 16),
('2026-02-25 17:40:00', 'LIKE', 18, 17),
('2026-02-25 17:41:00', 'APOIO', 19, 17),
('2026-02-26 18:10:00', 'LIKE', 20, 18),
('2026-02-26 18:11:00', 'APOIO', 21, 18),
('2026-02-27 18:40:00', 'LIKE', 22, 19),
('2026-02-27 18:41:00', 'APOIO', 23, 19),
('2026-02-28 19:10:00', 'LIKE', 24, 20),
('2026-02-28 19:11:00', 'APOIO', 25, 20),
('2026-03-01 19:40:00', 'LIKE', 26, 21),
('2026-03-01 19:41:00', 'APOIO', 27, 21),
('2026-03-02 08:15:00', 'LIKE', 15, 1),
('2026-03-02 08:16:00', 'APOIO', 16, 1),
('2026-03-03 09:08:00', 'LIKE', 17, 2),
('2026-03-03 09:09:00', 'APOIO', 18, 2),
('2026-03-04 10:02:00', 'LIKE', 19, 3),
('2026-03-04 10:03:00', 'APOIO', 20, 3),
('2026-03-05 11:02:00', 'LIKE', 21, 4),
('2026-03-05 11:03:00', 'APOIO', 22, 4),
('2026-03-06 12:02:00', 'LIKE', 23, 5),
('2026-03-06 12:03:00', 'APOIO', 24, 5),
('2026-03-07 13:02:00', 'LIKE', 25, 6),
('2026-03-07 13:03:00', 'APOIO', 26, 6),
('2026-03-08 14:02:00', 'LIKE', 27, 7),
('2026-03-08 14:03:00', 'APOIO', 28, 7),
('2026-03-09 15:02:00', 'LIKE', 29, 8),
('2026-03-09 15:03:00', 'APOIO', 30, 8),
('2026-03-10 16:02:00', 'LIKE', 31, 9),
('2026-03-10 16:03:00', 'APOIO', 32, 9),
('2026-03-11 17:02:00', 'LIKE', 33, 10),
('2026-03-11 17:03:00', 'APOIO', 34, 10),
('2026-03-11 17:30:00', 'LIKE', 35, 10),
('2026-03-11 17:35:00', 'APOIO', 14, 10),
('2026-03-12 08:00:00', 'LIKE', 11, 11),
('2026-03-12 08:05:00', 'APOIO', 12, 11),
('2026-03-12 09:20:00', 'LIKE', 13, 12),
('2026-03-12 09:25:00', 'APOIO', 14, 12),
('2026-03-12 10:00:00', 'LIKE', 15, 13),
('2026-03-12 10:05:00', 'APOIO', 16, 13),
('2026-03-12 11:00:00', 'LIKE', 17, 14),
('2026-03-12 11:05:00', 'APOIO', 18, 14),
('2026-03-12 12:00:00', 'LIKE', 19, 15),
('2026-03-12 12:05:00', 'APOIO', 20, 15);

INSERT INTO CONEXAO
(DtEnvConv, DtAceitConv, StatusConexao, IDConta_1, IDConta_2)
VALUES
('2026-03-13 08:00:00', '2026-03-13 08:01:00', 'ACEITA', 7, 8),
('2026-03-13 08:02:00', '2026-03-13 08:03:00', 'ACEITA', 8, 9),
('2026-03-13 08:04:00', '2026-03-13 08:05:00', 'ACEITA', 7, 9),
('2025-06-01 10:00:00', '2025-06-01 10:01:00', 'ACEITA', 5, 6),
('2025-06-02 10:00:00', '2025-06-02 10:01:00', 'ACEITA', 2, 6),
('2025-06-03 10:00:00', '2025-06-03 10:01:00', 'ACEITA', 5, 2),
('2025-04-01 09:00:00', '2025-04-01 09:05:00', 'ACEITA', 11, 12),
('2025-04-02 09:00:00', '2025-04-02 09:05:00', 'ACEITA', 12, 13),
('2025-04-03 09:00:00', '2025-04-03 09:05:00', 'ACEITA', 13, 14),
('2025-04-04 09:00:00', '2025-04-04 09:05:00', 'ACEITA', 14, 15),
('2025-04-05 09:00:00', '2025-04-05 09:05:00', 'ACEITA', 15, 16),
('2025-04-06 09:00:00', '2025-04-06 09:05:00', 'ACEITA', 16, 17),
('2025-04-07 09:00:00', '2025-04-07 09:05:00', 'ACEITA', 17, 18),
('2025-04-08 09:00:00', '2025-04-08 09:05:00', 'ACEITA', 18, 19),
('2025-04-09 09:00:00', '2025-04-09 09:05:00', 'ACEITA', 19, 20),
('2025-04-10 09:00:00', '2025-04-10 09:05:00', 'ACEITA', 20, 21),
('2025-04-11 09:00:00', '2025-04-11 09:05:00', 'ACEITA', 21, 22),
('2025-04-12 09:00:00', '2025-04-12 09:05:00', 'ACEITA', 22, 23),
('2025-04-13 09:00:00', '2025-04-13 09:05:00', 'ACEITA', 23, 24),
('2025-04-14 09:00:00', '2025-04-14 09:05:00', 'ACEITA', 24, 25),
('2025-04-15 09:00:00', '2025-04-15 09:05:00', 'ACEITA', 25, 26),
('2025-04-16 09:00:00', '2025-04-16 09:05:00', 'ACEITA', 26, 27),
('2025-04-17 09:00:00', '2025-04-17 09:05:00', 'ACEITA', 27, 28),
('2025-04-18 09:00:00', '2025-04-18 09:05:00', 'ACEITA', 28, 29),
('2025-04-19 09:00:00', '2025-04-19 09:05:00', 'ACEITA', 29, 30),
('2025-04-20 09:00:00', '2025-04-20 09:05:00', 'ACEITA', 30, 31),
('2025-04-21 09:00:00', '2025-04-21 09:05:00', 'ACEITA', 31, 32),
('2025-04-22 09:00:00', '2025-04-22 09:05:00', 'ACEITA', 32, 33),
('2025-04-23 09:00:00', '2025-04-23 09:05:00', 'ACEITA', 33, 34),
('2025-04-24 09:00:00', '2025-04-24 09:05:00', 'ACEITA', 34, 35),
('2025-04-25 09:00:00', '2025-04-25 09:05:00', 'ACEITA', 2, 11);

INSERT INTO FORMACAOACAD
(NomInstitForm, GrauForm, AreaForm, DtInicioForm, DtFimForm, IDConta)
VALUES
('UFSC', 'Bacharelado', 'Ciência da Computação','2018-01-01', '2022-12-01', 2),
('USP', 'Mestrado', 'Engenharia de Software','2017-01-01', '2019-12-01', 6),
('UFPR', 'Bacharelado', 'Engenharia de Software', '2019-01-01', '2023-12-01', 3),
('UFMG', 'Bacharelado', 'Sistemas de Informação', '2018-02-01', '2022-12-01', 4),
('PUC-Rio', 'Bacharelado', 'Comunicação Social', '2017-03-01', '2021-11-30', 5),
('UTFPR', 'Bacharelado', 'Ciência da Computação', '2019-01-01', '2023-12-15', 7),
('UFPE', 'Bacharelado', 'Engenharia de Software', '2018-01-15', '2022-12-01', 8),
('UFRJ', 'Bacharelado', 'Engenharia de Computação', '2019-02-01', '2023-12-01', 9),
('UNB', 'Bacharelado', 'Administração', '2016-01-01', '2020-12-01', 10),
('PUC-SP', 'Mestrado', 'Ciência de Dados', '2020-01-01', '2022-12-20', 11),
('UFBA', 'Bacharelado', 'Estatística', '2018-02-01', '2022-12-01', 12),
('UNICAMP', 'Bacharelado', 'Design', '2017-01-01', '2021-12-01', 13),
('UFRGS', 'Bacharelado', 'Engenharia de Produção', '2018-03-01', '2022-12-10', 14),
('UFC', 'Bacharelado', 'Marketing', '2017-02-01', '2021-12-01', 15),
('UFG', 'Bacharelado', 'Ciência da Computação', '2016-08-01', '2020-12-01', 16),
('UFMS', 'Bacharelado', 'Agronomia', '2015-03-01', '2019-12-01', 17),
('UFSCAR', 'Bacharelado', 'Engenharia Eletrônica', '2018-02-01', '2022-12-01', 18),
('UFPA', 'Bacharelado', 'Ciência da Computação', '2019-03-01', '2023-12-01', 19),
('UEA', 'Bacharelado', 'Ciência da Computação', '2018-02-01', '2022-12-01', 20),
('UFPE', 'Bacharelado', 'Design Digital', '2017-01-01', '2021-12-01', 21),
('UFCG', 'Bacharelado', 'Psicologia', '2017-01-01', '2021-12-01', 22),
('UFRN', 'Bacharelado', 'Administração', '2016-02-01', '2020-12-01', 23),
('UNIFESP', 'MBA', 'Gestão de Projetos', '2021-01-01', '2022-12-01', 24),
('USP', 'Bacharelado', 'Engenharia de Produção', '2015-02-01', '2019-12-01', 25),
('UFBA', 'Bacharelado', 'Engenharia Civil', '2015-03-01', '2019-12-01', 26),
('UEM', 'Bacharelado', 'Gestão de TI', '2016-02-01', '2020-12-01', 27),
('UTFPR', 'Bacharelado', 'Redes de Computadores', '2016-03-01', '2020-12-01', 28),
('UFRJ', 'Bacharelado', 'Engenharia Elétrica', '2016-02-01', '2020-12-01', 29),
('PUC-PR', 'Bacharelado', 'Design Gráfico', '2017-02-01', '2021-12-01', 30),
('FATEC', 'Bacharelado', 'Jogos Digitais', '2018-03-01', '2022-12-01', 31),
('FGV', 'Bacharelado', 'Economia', '2016-01-01', '2020-12-01', 32),
('SENAI', 'Tecnólogo', 'Gestão Financeira', '2018-04-01', '2020-12-01', 33),
('UNESP', 'Bacharelado', 'Psicologia Organizacional', '2017-03-01', '2021-12-01', 34),
('UNIARA', 'Bacharelado', 'Comunicação', '2017-01-01', '2021-12-01', 35);

INSERT INTO POSSCOMP (IDComp, IDConta)
VALUES
(1, 7), (2, 7), (3, 7),
(1, 8), (2, 8), (3, 8),
(1, 9), (2, 9), (3, 9),
(1, 2), (2, 2), (3, 2),
(1, 3), (2, 3),
(2, 4), (3, 4), (4, 4),
(1, 6), (2, 6), (5, 6),
(6, 11), (2, 11), (7, 11),
(1, 12), (8, 12),
(2, 13), (9, 13),
(3, 14), (10, 14),
(1, 15), (6, 15),
(7, 16), (2, 16),
(4, 17), (8, 17),
(1, 18), (2, 18),
(3, 19), (6, 19),
(9, 20), (10, 20),
(1, 21), (2, 21),
(3, 22), (6, 22),
(8, 23), (9, 23),
(1, 24), (4, 24),
(2, 25), (7, 25),
(3, 26), (8, 26),
(1, 27), (5, 27),
(4, 28), (6, 28),
(2, 29), (10, 29),
(3, 30), (9, 30),
(1, 31), (8, 31),
(2, 32), (7, 32),
(5, 33), (10, 33),
(3, 34), (6, 34),
(4, 35), (9, 35);

INSERT INTO FALAIDIOM (NvlProfic, IDIdioma, IDConta)
VALUES
('Nativo', 1, 6),
('Avançado', 2, 6),
('Intermediário', 3, 6),
('Básico', 4, 6),
('Nativo', 1, 2),
('Avançado', 2, 2),
('Nativo', 1, 5),
('Avançado', 2, 5),
('Intermediário', 5, 5),
('Avançado', 3, 11),
('Intermediário', 2, 11),
('Básico', 6, 11),
('Avançado', 2, 12),
('Intermediário', 1, 13),
('Básico', 5, 13),
('Nativo', 1, 14),
('Avançado', 2, 14),
('Avançado', 3, 15),
('Intermediário', 6, 16),
('Nativo', 1, 17),
('Avançado', 2, 17),
('Intermediário', 4, 18),
('Nativo', 1, 19),
('Avançado', 2, 19),
('Intermediário', 5, 20),
('Avançado', 2, 21),
('Nativo', 1, 22),
('Intermediário', 3, 23),
('Avançado', 2, 24),
('Nativo', 1, 25),
('Avançado', 6, 26),
('Básico', 4, 27),
('Intermediário', 2, 28),
('Avançado', 1, 29),
('Básico', 5, 30),
('Nativo', 1, 31),
('Avançado', 2, 32),
('Intermediário', 3, 33),
('Básico', 4, 34),
('Avançado', 5, 35);

INSERT INTO FORMPOSSCOMP (IDComp, IDForm)
VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10),
(1, 11),
(2, 12),
(3, 13),
(4, 14),
(5, 15),
(6, 16),
(7, 17),
(8, 18),
(9, 19),
(10, 20);

INSERT INTO EXPPOSSCOMP (IDComp, IDExp)
VALUES
(2, 1),
(6, 2),
(10, 3),
(9, 4),
(8, 5),
(1, 6),
(4, 7),
(5, 8),
(3, 9),
(2, 10),
(7, 11),
(1, 12),
(6, 13),
(8, 14),
(10, 15),
(2, 16),
(9, 17),
(5, 18),
(1, 19),
(4, 20);










/* ====================================================================
Geração de registros aleatórios 
==================================================================== 
*/

-- 1. Inserção de 90.000 Contas vinculadas a PESSOAL usando arrays de nomes reais
INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade)
SELECT 
    (ARRAY[
        -- 100 nomes
        'Bruno', 'Ana', 'João', 'Maria', 'Lucas', 'Mariana', 'Carlos', 'Julia', 'Phelipe', 'Fernanda', 
        'Diego', 'Carla', 'Jose', 'Julio', 'Luis', 'Murilo', 'Pedro', 'Rafael', 'Gabriela', 'Beatriz', 
        'Thiago', 'Leticia',
        'Arthur', 'Davi', 'Gabriel', 'Bernardo', 'Heitor', 'Miguel', 'Matheus', 'Guilherme', 'Enzo', 'Felipe',
        'Nicolas', 'Samuel', 'Gustavo', 'Henrique', 'Eduardo', 'Victor', 'Leonardo', 'Daniel', 'Igor', 'Breno',
        'Caio', 'Rodrigo', 'Marcelo', 'Marcos', 'Fernando', 'Renato', 'Andre', 'Ricardo', 'Roberto', 'Alexandre',
        'Sergio', 'Tiago', 'Vinicius', 'Yuri', 'Caua', 'Theo', 'Joaquim', 'Otavio', 'Ian', 'Alice',
        'Sophia', 'Laura', 'Valentina', 'Helena', 'Isabella', 'Manuela', 'Luiza', 'Giovanna', 'Isadora', 'Carolina',
        'Amanda', 'Camila', 'Bruna', 'Jessica', 'Vitoria', 'Larissa', 'Nathalia', 'Bianca', 'Lorena', 'Melissa',
        'Emanuelly', 'Nicole', 'Eduarda', 'Isabel', 'Clara', 'Marina', 'Aline', 'Patricia', 'Juliana', 'Vanessa',
        'Tatiana', 'Renata', 'Simone', 'Luciana', 'Mirella', 'Olivia', 'Cecilia', 'Livia'
    ])[floor(random() * 100 + 1)] || '.' ||
    (ARRAY['Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves', 'Lima', 'Gomes', 'Costa'])[floor(random() * 10 + 1)] || '.' ||
    i || '@testemassivo.com',
    'senha123',
    CURRENT_DATE - floor(random() * 1000)::int,
    floor(random() * 52 + 1)::int
FROM generate_series(1, 90000) AS s(i);

-- 2. Mapeamento estrito 1:1 para PESSOAL
INSERT INTO PESSOAL (IDConta, NomPsso, SobnomPsso, TtloProfPsso)
SELECT 
    IDConta,
    initcap(split_part(EmailConta, '.', 1)),
    initcap(split_part(EmailConta, '.', 2)),
    (ARRAY['Data Engineer', 'Software Engineer', 'UX Designer', 'Product Manager', 'Data Scientist', 'DevOps Engineer'])[floor(random() * 6 + 1)]
FROM CONTA
WHERE EmailConta LIKE '%@testemassivo.com';

-- 3. Inserção de 10.000 Contas vinculadas a CORPORATIVA
INSERT INTO CONTA (EmailConta, SenhaConta, DtCrcaoConta, IDCidade)
SELECT 
    'empresa.' || (ARRAY['Tech', 'Data', 'Cloud', 'Smart', 'Global', 'Inova', 'Cyber', 'Next'])[floor(random() * 8 + 1)] || '.' ||
    (ARRAY['Solutions', 'Systems', 'Networks', 'Labs', 'Consulting', 'Corp'])[floor(random() * 6 + 1)] || '.' ||
    i || '@corp.com',
    'senha123',
    CURRENT_DATE - floor(random() * 1000)::int,
    floor(random() * 52 + 1)::int
FROM generate_series(1, 10000) AS s(i);

-- 4. Mapeamento estrito 1:1 para CORPORATIVA
INSERT INTO CORPORATIVA (IDConta, NomComerc, NumFuncEmp, DescriEmp)
SELECT 
    IDConta,
    initcap(split_part(EmailConta, '.', 2)) || ' ' || initcap(split_part(EmailConta, '.', 3)),
    floor(random() * 5000 + 10)::int,
    'Descrição gerada automaticamente pelo sistema massivo'
FROM CONTA
WHERE EmailConta LIKE '%@corp.com';

-- 5. Inserção Idiomas aleatórios em novos usuários (ID > 55 por conta do ID sequencial)
INSERT INTO FALAIDIOM (NvlProfic, IDIdioma, IDConta)
SELECT 
    (ARRAY['Básico', 'Intermediário', 'Avançado', 'Nativo'])[floor(random() * 4 + 1)],
    floor(random() * 6 + 1)::int,
    IDConta
FROM PESSOAL
WHERE IDConta > 55 AND random() < 0.6;

-- 6. Inserção de Competências aleatórias nos novos usuários
INSERT INTO POSSCOMP (IDComp, IDConta)
SELECT 
    floor(random() * 15 + 1)::int,
    IDConta
FROM PESSOAL
WHERE IDConta > 55 AND random() < 0.8;

-- 7. Criação de Vagas atreladas às novas empresas (ID > 55)
INSERT INTO VAGAEMPREGO (TtloVaga, DescriVaga, FormatoTrabVaga, DtCrcaoVaga, IDConta)
SELECT 
    (ARRAY['Especialista em Banco de Dados', 'Cientista de Dados Pleno', 'Engenheiro de Software Senior', 'Especialista em Segurança', 'Analista Financeiro'])[floor(random() * 5 + 1)],
    'Descrição da vaga gerada na carga massiva. Procuramos profissionais talentosos.',
    (ARRAY['REMOTO', 'PRESENCIAL', 'HÍBRIDO'])[floor(random() * 3 + 1)],
    CURRENT_DATE - floor(random() * 60)::int,
    c.IDConta
FROM CORPORATIVA c
CROSS JOIN generate_series(1, 5)
WHERE c.IDConta > 55;

-- 8. Geração de 20.000 Posts Aleatórios
INSERT INTO POST (DtPubliPost, ConteudoPost, NivelVisib, IDConta)
SELECT 
    CURRENT_TIMESTAMP - (random() * interval '365 days'),
    'Postagem massiva número ' || i || ' sobre atualizações do mercado de tecnologia.',
    (ARRAY['PUBLICO', 'PRIVADO'])[floor(random() * 2 + 1)],
    floor(random() * 100000 + 56)::int
FROM generate_series(1, 20000) AS s(i);