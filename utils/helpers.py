"""
Funções auxiliares para o Dashboard Financeiro
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def format_currency_br(value):
    """
    Formata valor numérico para padrão brasileiro (BRL)
    Exemplo: 519247.8 → R$ 519.247,80
    """
    if pd.isna(value) or value is None:
        return "R$ 0,00"
    
    # Formatar com separador de milhares e decimal
    formatted = f"R$ {value:,.2f}"
    # Substituir vírgula por ponto temporariamente
    formatted = formatted.replace(",", "TEMP")
    # Substituir ponto por vírgula (decimal brasileiro)
    formatted = formatted.replace(".", ",")
    # Substituir TEMP por ponto (separador de milhares brasileiro)
    formatted = formatted.replace("TEMP", ".")
    
    return formatted

def format_number_br(value):
    """
    Formata número para padrão brasileiro sem símbolo de moeda
    Exemplo: 519247.8 → 519.247,80
    """
    if pd.isna(value) or value is None:
        return "0,00"
    
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "TEMP")
    formatted = formatted.replace(".", ",")
    formatted = formatted.replace("TEMP", ".")
    
    return formatted

def apply_filters_sidebar(pr, cr, par):
    """
    Aplica filtros globais na sidebar e retorna dataframes filtrados
    Inclui filtros de Grupo de Empresa, Empresa, Grupo de Despesa, Categoria e Período
    """
    st.sidebar.title("🔍 Filtros")
    
    # Filtro de Grupo de Empresa
    grupos_empresa_disponiveis = ['Todos'] + sorted(list(set(
        list(pr['Grupo'].unique()) + 
        list(cr['Grupo'].unique()) + 
        list(par['Grupo'].unique())
    )))
    grupo_empresa_selecionado = st.sidebar.selectbox("Grupo da Empresa", grupos_empresa_disponiveis, key='filtro_grupo_empresa')
    
    # Filtro de Empresa
    if grupo_empresa_selecionado != 'Todos':
        empresas_pr = pr[pr['Grupo'] == grupo_empresa_selecionado]['Minha Empresa (Nome Fantasia)'].unique() if 'Minha Empresa (Nome Fantasia)' in pr.columns else []
        empresas_cr = cr[cr['Grupo'] == grupo_empresa_selecionado]['Minha Empresa (Razão Social)'].unique() if 'Minha Empresa (Razão Social)' in cr.columns else []
        empresas_par = par[par['Grupo'] == grupo_empresa_selecionado]['Minha Empresa (Razão Social)'].unique() if 'Minha Empresa (Razão Social)' in par.columns else []
        empresas_disponiveis = ['Todas'] + sorted(list(set(list(empresas_pr) + list(empresas_cr) + list(empresas_par))))
    else:
        empresas_disponiveis = ['Todas']
    
    empresa_selecionada = st.sidebar.selectbox("Empresa", empresas_disponiveis, key='filtro_empresa')
    
    st.sidebar.markdown("---")
    
    # Filtro de Grupo de Despesa/Receita
    # Usar coluna 'Grupo.1' que contém os tipos de despesa (Despesas Operacionais, Impostos, etc.)
    grupos_despesa_pr = pr['Grupo.1'].unique().tolist() if 'Grupo.1' in pr.columns else []
    grupos_despesa_cr = []  # Contas Recebidas não tem Grupo.1
    grupos_despesa_par = par['Grupo.1'].unique().tolist() if 'Grupo.1' in par.columns else []
    
    todos_grupos_despesa = sorted(list(set(grupos_despesa_pr + grupos_despesa_cr + grupos_despesa_par)))
    grupos_despesa_selecionados = st.sidebar.multiselect(
        "Grupo (Tipo de Despesa/Receita)",
        options=todos_grupos_despesa,
        default=[],
        key='filtro_grupo_despesa',
        help="Filtre por tipo: Despesas Administrativas, Operacionais, Financeiras, Impostos, etc."
    )
    
    # Filtro de Categoria
    categorias_pr = pr['Categoria'].unique().tolist() if 'Categoria' in pr.columns else []
    categorias_cr = cr['Categoria'].unique().tolist() if 'Categoria' in cr.columns else []
    categorias_par = par['Categoria'].unique().tolist() if 'Categoria' in par.columns else []
    
    todas_categorias = sorted(list(set(categorias_pr + categorias_cr + categorias_par)))
    categorias_selecionadas = st.sidebar.multiselect(
        "Categoria",
        options=todas_categorias,
        default=[],
        key='filtro_categoria',
        help="Filtre por categoria específica: PIS, COFINS, Serviços, etc."
    )
    
    # Filtro de Período
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Período")
    
    # Detectar datas disponíveis
    datas_pr = pd.to_datetime(pr['Data de Registro (completa)'], errors='coerce').dropna() if 'Data de Registro (completa)' in pr.columns else pd.Series()
    datas_cr = pd.to_datetime(cr['Data de Crédito ou Débito (No Extrato)'], errors='coerce').dropna() if 'Data de Crédito ou Débito (No Extrato)' in cr.columns else pd.Series()
    datas_par = pd.to_datetime(par['Vencimento'], errors='coerce').dropna() if 'Vencimento' in par.columns else pd.Series()
    
    todas_datas = pd.concat([datas_pr, datas_cr, datas_par])
    
    if len(todas_datas) > 0:
        data_min = todas_datas.min().date()
        data_max = todas_datas.max().date()
        
        col_data1, col_data2 = st.sidebar.columns(2)
        with col_data1:
            data_inicio = st.date_input("Data Início", value=data_min, min_value=data_min, max_value=data_max, key='filtro_data_inicio')
        with col_data2:
            data_fim = st.date_input("Data Fim", value=data_max, min_value=data_min, max_value=data_max, key='filtro_data_fim')
    else:
        data_inicio = None
        data_fim = None
    
    st.sidebar.markdown("---")
    
    # Aplicar filtros
    pr_filtrado = pr.copy()
    cr_filtrado = cr.copy()
    par_filtrado = par.copy()
    
    # Filtro de Grupo de Empresa
    if grupo_empresa_selecionado != 'Todos':
        pr_filtrado = pr_filtrado[pr_filtrado['Grupo'] == grupo_empresa_selecionado]
        cr_filtrado = cr_filtrado[cr_filtrado['Grupo'] == grupo_empresa_selecionado]
        par_filtrado = par_filtrado[par_filtrado['Grupo'] == grupo_empresa_selecionado]
    
    # Filtro de Empresa
    if empresa_selecionada != 'Todas':
        if 'Minha Empresa (Nome Fantasia)' in pr_filtrado.columns:
            pr_filtrado = pr_filtrado[pr_filtrado['Minha Empresa (Nome Fantasia)'] == empresa_selecionada]
        if 'Minha Empresa (Razão Social)' in cr_filtrado.columns:
            cr_filtrado = cr_filtrado[cr_filtrado['Minha Empresa (Razão Social)'] == empresa_selecionada]
        if 'Minha Empresa (Razão Social)' in par_filtrado.columns:
            par_filtrado = par_filtrado[par_filtrado['Minha Empresa (Razão Social)'] == empresa_selecionada]
    
    # Filtro de Grupo de Despesa
    if len(grupos_despesa_selecionados) > 0:
        # Usar coluna 'Grupo.1' para tipos de despesa
        if 'Grupo.1' in pr_filtrado.columns:
            pr_filtrado = pr_filtrado[pr_filtrado['Grupo.1'].isin(grupos_despesa_selecionados)]
        # Contas Recebidas não tem Grupo.1, então não filtra
        if 'Grupo.1' in par_filtrado.columns:
            par_filtrado = par_filtrado[par_filtrado['Grupo.1'].isin(grupos_despesa_selecionados)]
    
    # Filtro de Categoria
    if len(categorias_selecionadas) > 0:
        if 'Categoria' in pr_filtrado.columns:
            pr_filtrado = pr_filtrado[pr_filtrado['Categoria'].isin(categorias_selecionadas)]
        if 'Categoria' in cr_filtrado.columns:
            cr_filtrado = cr_filtrado[cr_filtrado['Categoria'].isin(categorias_selecionadas)]
        if 'Categoria' in par_filtrado.columns:
            par_filtrado = par_filtrado[par_filtrado['Categoria'].isin(categorias_selecionadas)]
    
    # Filtro de Período
    if data_inicio and data_fim:
        # Converter para datetime
        data_inicio_dt = pd.to_datetime(data_inicio)
        data_fim_dt = pd.to_datetime(data_fim)
        
        # Filtrar Pagamentos Realizados
        if 'Data de Registro (completa)' in pr_filtrado.columns:
            pr_filtrado['_data_temp'] = pd.to_datetime(pr_filtrado['Data de Registro (completa)'], errors='coerce')
            pr_filtrado = pr_filtrado[
                (pr_filtrado['_data_temp'] >= data_inicio_dt) & 
                (pr_filtrado['_data_temp'] <= data_fim_dt)
            ]
            pr_filtrado = pr_filtrado.drop('_data_temp', axis=1)
        
        # Filtrar Contas Recebidas
        if 'Data de Crédito ou Débito (No Extrato)' in cr_filtrado.columns:
            cr_filtrado['_data_temp'] = pd.to_datetime(cr_filtrado['Data de Crédito ou Débito (No Extrato)'], errors='coerce')
            cr_filtrado = cr_filtrado[
                (cr_filtrado['_data_temp'] >= data_inicio_dt) & 
                (cr_filtrado['_data_temp'] <= data_fim_dt)
            ]
            cr_filtrado = cr_filtrado.drop('_data_temp', axis=1)
        
        # Filtrar Pagamentos a Realizar
        if 'Vencimento' in par_filtrado.columns:
            par_filtrado['_data_temp'] = pd.to_datetime(par_filtrado['Vencimento'], errors='coerce')
            par_filtrado = par_filtrado[
                (par_filtrado['_data_temp'] >= data_inicio_dt) & 
                (par_filtrado['_data_temp'] <= data_fim_dt)
            ]
            par_filtrado = par_filtrado.drop('_data_temp', axis=1)
    
    return pr_filtrado, cr_filtrado, par_filtrado, grupo_empresa_selecionado, empresa_selecionada, data_inicio, data_fim, grupos_despesa_selecionados, categorias_selecionadas

def calcular_situacao_vencimento(data_vencimento):
    """
    Calcula a situação de vencimento de uma data
    Retorna categoria e ordem para ordenação temporal
    """
    if pd.isna(data_vencimento):
        return "Sem data de vencimento", 99
    
    hoje = pd.Timestamp.now().normalize()
    data_venc = pd.to_datetime(data_vencimento).normalize()
    dias_diff = (data_venc - hoje).days
    
    # Ordenação temporal conforme especificado
    if dias_diff == 0:
        return "Vence hoje", 1
    elif dias_diff == 1:
        return "Vence amanhã", 2
    elif 2 <= dias_diff <= 7:
        return "Vence nos próximos dias", 3
    elif 8 <= dias_diff <= 30:
        return "A vencer até 30 dias", 4
    elif 31 <= dias_diff <= 60:
        return "A vencer de 31 até 60 dias", 5
    elif 61 <= dias_diff <= 90:
        return "A vencer de 61 até 90 dias", 6
    elif -30 <= dias_diff < 0:
        return "Vencido até 30 dias", 7
    elif -60 <= dias_diff < -30:
        return "Vencido de 31 a 60 dias", 8
    elif dias_diff < -90:
        return "Vencido mais de 90 dias", 9
    else:
        return "A vencer (mais de 90 dias)", 10

def criar_tabela_vencimentos(df, coluna_vencimento='Vencimento', coluna_valor='Valor Líquido'):
    """
    Cria tabela de valores por situação de vencimento
    Ordenada temporalmente conforme especificação
    """
    if coluna_vencimento not in df.columns or coluna_valor not in df.columns:
        return pd.DataFrame()
    
    # Adicionar situação de vencimento
    df_temp = df.copy()
    df_temp['Situacao_Vencimento'] = df_temp[coluna_vencimento].apply(
        lambda x: calcular_situacao_vencimento(x)[0]
    )
    df_temp['Ordem_Vencimento'] = df_temp[coluna_vencimento].apply(
        lambda x: calcular_situacao_vencimento(x)[1]
    )
    
    # Agrupar por situação
    tabela = df_temp.groupby(['Situacao_Vencimento', 'Ordem_Vencimento']).agg({
        coluna_valor: ['sum', 'count']
    }).reset_index()
    
    tabela.columns = ['Situação do Vencimento', 'Ordem', 'Valor Total', 'Quantidade']
    
    # Ordenar por ordem temporal
    tabela = tabela.sort_values('Ordem')
    
    # Formatar valores
    tabela['Valor Total Formatado'] = tabela['Valor Total'].apply(format_currency_br)
    
    # Remover coluna de ordem (usada apenas para ordenação)
    tabela_final = tabela[['Situação do Vencimento', 'Valor Total Formatado', 'Quantidade']].copy()
    tabela_final.columns = ['Situação do Vencimento', 'Valor Total', 'Quantidade']
    
    return tabela_final

def format_dataframe_currency(df, currency_columns):
    """
    Formata colunas de moeda em um DataFrame para exibição
    """
    df_display = df.copy()
    
    for col in currency_columns:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(format_currency_br)
    
    return df_display
