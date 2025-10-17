# Dashboard Financeiro Consolidado

Dashboard interativo para análise financeira completa com múltiplas visualizações e filtros dinâmicos.

## 📊 Funcionalidades

### 1. Dashboard Geral Consolidado
- Visão geral de receitas, despesas e lucro líquido
- KPIs principais de performance financeira
- Gráficos comparativos e de distribuição
- Análise por categoria

### 2. Dashboard de Receitas
- Evolução temporal das receitas
- Análise por categoria e cliente
- Top 10 clientes
- Métricas de ticket médio

### 3. Dashboard de Despesas
- Análise de despesas realizadas e pendentes
- Distribuição por categoria e fornecedor
- Status de vencimentos
- Top 10 fornecedores

### 4. Dashboard de Conciliação
- Percentual de conciliação de receitas e despesas
- Identificação de itens não conciliados
- Análise comparativa por empresa
- Valores não conciliados

### 5. Métrica de Conformidade
- Análise de conformidade entre data de emissão e registro
- Identificação de lançamentos fora do período
- Percentual de conformidade por empresa
- Detalhamento de itens não conformes

### 6. Previsão de Faturamento
- Visualização de faturamento futuro
- Comparação entre previsto e realizado
- Análise por empresa e período
- Tendências de faturamento

## 🔍 Filtros Disponíveis

- **Grupo da Empresa**: Filtre por grupo empresarial
- **Empresa Individual**: Selecione empresas específicas
- **Período**: Análise temporal automática

## 📈 KPIs Principais

- Total de Receitas
- Total de Despesas
- Lucro Líquido
- Despesas Pendentes
- % de Conciliação
- % de Conformidade
- Margem Líquida

## 🚀 Como Executar Localmente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o dashboard:
```bash
streamlit run app.py
```

3. Acesse no navegador: `http://localhost:8501`

## 📁 Estrutura de Dados

O dashboard processa 4 relatórios financeiros:
- **Pagamentos Realizados**: 3.407 registros
- **Contas Recebidas**: 957 registros
- **Pagamentos a Realizar**: 1.736 registros
- **Previsão de Faturamento**: 15 registros

**Total**: 6.115 transações processadas

## 💡 Insights Principais

- Taxa de conciliação: 99,27%
- Total de receitas: R$ 172.042.025,64
- Total de despesas: R$ 205.915.287,66
- Despesas pendentes: R$ 67.663.757,83

## 🎨 Design

- Interface moderna e responsiva
- Gráficos interativos com Plotly
- Paleta de cores profissional
- Navegação intuitiva por abas

## 📞 Suporte

Dashboard desenvolvido para análise financeira consolidada.
Última atualização: Outubro 2025

