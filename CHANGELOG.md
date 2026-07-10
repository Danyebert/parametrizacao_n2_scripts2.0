# Parametrização N2 Scripts

## Versão 2.1.0 (07/07/2026)

### Novo Editor SQL

- Editor SQL reformulado
- SQL Formatter
- Copiar consulta
- Copiar todas as consultas
- Tela cheia
- Tema claro/escuro
- Status do editor
- Melhor layout
- Botões reorganizados

### Scripts SQL

- Tipo de banco por seleção
- Melhor organização do formulário
- Melhor experiência de edição

### Interface

- Melhorias visuais
- Ajustes de CSS
- Ajustes de JavaScript
- Melhor responsividade

## Versão 2.1.1 (08/07/2026)

### Correções
- Corrigido comportamento da sidebar ao recolher.
- Ajustado rodapé de versão.
- Adicionada navegação pelo título nas telas de Scripts SQL e Correções N2.
- Pequenos ajustes de interface.


# Versão 2.2.0 (08/07/2026)

## 🚀 Novo módulo DataSync

### Alterações

- Removido o upload de arquivos para o banco de dados.
- Implementado cadastro de links para download.
- Adequado o módulo para funcionamento na Vercel.
- Eliminada a limitação de upload (Erro HTTP 413).
- Adicionado formulário para cadastro de ferramentas.
- Adicionado contador de downloads.
- Download agora é realizado diretamente pelo link informado.
- Melhorias na interface do módulo DataSync.
- Código simplificado para facilitar futuras manutenções.

### Banco de dados

- Adicionado o campo:


# Versão 2.3.0 (08/07/2026)

## Navegação

- Adicionado breadcrumb dinâmico em todas as telas.
- Breadcrumb fixo no topo da aplicação.
- Navegação clicável entre módulos.
- Melhor organização da barra superior.
- Melhor experiência de navegação entre telas.
- Padronização da TopBar.

# Versão 2.3.1 (08/07/2026)

## Dashboard

- Novo layout moderno para o Dashboard.
- Cards KPI redesenhados com identidade visual.
- Painéis com estilo profissional.
- Breadcrumb fixo no topo.
- Adicionado filtro de período (7, 15 e 30 dias).
- Criado painel "Últimas Correções N2".
- Criado painel "Últimos Scripts SQL".
- Melhorias gerais na experiência visual.

# Versão 2.3.2 (08/07/2026)

## Scripts SQL

- Modernizada a tela de listagem de Scripts SQL em formato de cards.
- Adicionados cards de indicadores no topo da tela.
- Adicionado contador de acessos aos scripts.
- Adicionado filtro por banco.
- Adicionada ordenação por mais recentes, A-Z, Z-A, banco e acessos.
- Adicionada área lateral com distribuição por banco.
- Adicionado ranking de scripts mais acessados.
- Adicionado ranking de scripts com mais consultas.
- Melhorias visuais no modo escuro.
- Ajustado layout dos cards para manter os indicadores na mesma linha.


## v2.4.0 - 09/07/2026

### Novo
- Contabilização automática de acessos aos Scripts SQL.
- Ranking de scripts mais acessados.
- Estatísticas reais de acessos.
- Sparklines dinâmicas nos cards.
- Tooltips interativos mostrando acessos por dia.
- Dashboard dos Scripts totalmente remodelado.

### Melhorias
- Layout responsivo dos KPIs.
- Cards alinhados em uma única linha.
- Melhor distribuição visual dos componentes.
- Correção da renderização dos gráficos.
- Ajustes na sidebar lateral.
- Melhor experiência visual no tema escuro.

### Correções
- Correção dos tooltips cortados.
- Ajuste do overflow dos gráficos.
- Correção da exibição da primeira e última barra dos sparklines.



## v2.5.0 - 09/07/2026

### Novo
- Modernização completa do módulo Scripts SQL.
- Modernização completa do módulo Correções N2.
- Dashboard de métricas reais para ambos os módulos.
- Histórico de acessos diário.
- Sparklines reais nos cards KPI.
- Tooltips informativos nos gráficos.
- Contador automático de acessos.
- Ranking de itens mais acessados.
- Breadcrumb navegável em todas as telas.

### Melhorias
- Novo layout para criação de Scripts SQL.
- Novo layout para visualização de Scripts SQL.
- Novo layout para criação de Correções N2.
- Novo layout para visualização de Correções N2.
- Melhorias no editor SQL.
- Melhorias de responsividade.
- Melhorias no tema escuro.
- Ajustes visuais nos cards, formulários e painéis.

### Correções
- Correção da contabilização de acessos.
- Ajuste dos tooltips dos gráficos.
- Correção dos KPIs.
- Ajustes de layout e alinhamento.


## v2.7.0 - 10/07/2026

### Novo
- Modernização completa do Gerador de Identificador.
- Histórico persistente utilizando LocalStorage.
- Métricas do Gerador.
- Contador de identificadores gerados.
- Contador de identificadores gerados no dia.
- Histórico de identificadores.
- Último identificador gerado.
- Exportação do histórico.
- Limpeza do histórico.
- Copiar Número.
- Copiar Identificador.
- Copiar Ambos.
- Toast de confirmação.
- Atalho CTRL + ENTER para geração.

### Melhorias
- Layout seguindo o padrão visual dos demais módulos.
- Melhor responsividade.
- Melhor suporte ao tema escuro.
- Melhor experiência de uso.
- Validação dos campos.
- Contador de caracteres.
- Melhor tratamento de erros.

### Padronização
- Scripts SQL.
- Correções N2.
- DataSync.
- Gerador de Identificador.

Todos os módulos principais agora seguem a mesma identidade visual.

## v2.7.1 - 10/07/2026

### Gerador de Identificador
- Modernização completa da interface.
- Novo layout seguindo o padrão do sistema.
- Histórico persistente em LocalStorage.
- KPIs em tempo real.
- Contador de caracteres.
- Copiar Número.
- Copiar Identificador.
- Copiar Tudo.
- Exportação do histórico em TXT.
- Limpeza do histórico.
- Atalho Ctrl + Enter.
- Correção da integração entre HTML e JavaScript.
- Ajuste dos IDs e ações dos botões.
- Correção das funções de cópia.