import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pytz
import sys
import os

# Adicionar pasta utils ao path
sys.path.append(os.path.dirname(__file__))
from utils.helpers import format_currency_br, apply_filters_sidebar, criar_tabela_vencimentos

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro Consolidado",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data():
    pr = pd.read_excel('data/PagamentosRealizadosRelatorio.xlsx')
    cr = pd.read_excel('data/ContasRecebidaseaReceber.xlsx')
    par = pd.read_excel('data/PagamentosaRealizarRelatorio.xlsx')
    pf = pd.read_excel('data/PrevisaoFaturamento.xlsx')
    return pr, cr, par, pf

# Carregar dados
try:
    pr, cr, par, pf = load_data()
    
    # Header
    st.markdown('<h1 class="main-header">📊 Dashboard Financeiro Consolidado</h1>', unsafe_allow_html=True)
    st.markdown(f"**Última atualização:** {datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%d/%m/%Y %H:%M:%S')}")
    st.markdown("---")
    
    # Aplicar filtros globais (agora retorna 9 valores incluindo grupos_despesa e categorias)
    pr_filtrado, cr_filtrado, par_filtrado, grupo_sel, empresa_sel, data_inicio, data_fim, grupos_despesa_sel, categorias_sel = apply_filters_sidebar(pr, cr, par)
    
    # Mostrar filtros ativos
    filtros_ativos = []
    if grupo_sel != 'Todos':
        filtros_ativos.append(f"**Grupo:** {grupo_sel}")
    if empresa_sel != 'Todas':
        filtros_ativos.append(f"**Empresa:** {empresa_sel}")
    if len(grupos_despesa_sel) > 0:
        filtros_ativos.append(f"**Grupos:** {', '.join(grupos_despesa_sel[:3])}{'...' if len(grupos_despesa_sel) > 3 else ''}")
    if len(categorias_sel) > 0:
        filtros_ativos.append(f"**Categorias:** {', '.join(categorias_sel[:3])}{'...' if len(categorias_sel) > 3 else ''}")
    if data_inicio and data_fim:
        filtros_ativos.append(f"**Período:** {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    
    if filtros_ativos:
        st.info(f"🔍 Filtros ativos: {' | '.join(filtros_ativos)}")
    
    # Calcular KPIs
    total_receitas = cr_filtrado['Pago ou Recebido'].sum()
    total_despesas = pr_filtrado['Pago ou Recebido'].sum()
    despesas_pendentes = par_filtrado['Valor Líquido'].sum()
    
    # Conciliação
    pr_conciliados = (pr_filtrado['Conciliado'] == 'Sim').sum()
    pr_total = len(pr_filtrado)
    perc_conciliacao_pr = (pr_conciliados / pr_total * 100) if pr_total > 0 else 0
    
    cr_conciliados = (cr_filtrado['Conciliado'] == 'Sim').sum()
    cr_total = len(cr_filtrado)
    perc_conciliacao_cr = (cr_conciliados / cr_total * 100) if cr_total > 0 else 0
    
    # KPIs principais - REMOVIDO Lucro Líquido e Ticket Médio
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💰 Total Receitas",
            value=format_currency_br(total_receitas),
            delta=f"{len(cr_filtrado)} transações"
        )
    
    with col2:
        st.metric(
            label="💸 Total Despesas",
            value=format_currency_br(total_despesas),
            delta=f"{len(pr_filtrado)} transações"
        )
    
    with col3:
        st.metric(
            label="⏳ Despesas Pendentes",
            value=format_currency_br(despesas_pendentes),
            delta=f"{len(par_filtrado)} contas"
        )
    
    st.markdown("---")
    
    # Segunda linha de KPIs
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric(
            label="✅ Conciliação Despesas",
            value=f"{perc_conciliacao_pr:.1f}%",
            delta=f"{pr_conciliados}/{pr_total}"
        )
    
    with col5:
        st.metric(
            label="✅ Conciliação Receitas",
            value=f"{perc_conciliacao_cr:.1f}%",
            delta=f"{cr_conciliados}/{cr_total}"
        )
    
    with col6:
        total_registros = len(pr_filtrado) + len(cr_filtrado) + len(par_filtrado)
        st.metric(
            label="📋 Total Registros",
            value=f"{total_registros:,}",
            delta="Processados"
        )
    
    st.markdown("---")
    
    # Gráficos
    col_grafico1, col_grafico2 = st.columns(2)
    
    with col_grafico1:
        st.subheader("📊 Receitas vs Despesas")
        
        dados_comparacao = pd.DataFrame({
            'Categoria': ['Receitas', 'Despesas', 'Pendentes'],
            'Valor': [total_receitas, total_despesas, despesas_pendentes]
        })
        
        fig_comparacao = px.bar(
            dados_comparacao,
            x='Categoria',
            y='Valor',
            color='Categoria',
            text='Valor',
            color_discrete_map={
                'Receitas': '#10b981',
                'Despesas': '#ef4444',
                'Pendentes': '#f59e0b'
            }
        )
        
        fig_comparacao.update_traces(
            texttemplate='R$ %{text:,.2f}',
            textposition='outside'
        )
        
        fig_comparacao.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Valor (R$)",
            height=400
        )
        
        st.plotly_chart(fig_comparacao, use_container_width=True)
    
    with col_grafico2:
        st.subheader("🎯 Distribuição Financeira")
        
        dados_pizza = pd.DataFrame({
            'Tipo': ['Receitas', 'Despesas Realizadas', 'Despesas Pendentes'],
            'Valor': [total_receitas, total_despesas, despesas_pendentes]
        })
        
        fig_pizza = px.pie(
            dados_pizza,
            values='Valor',
            names='Tipo',
            color='Tipo',
            color_discrete_map={
                'Receitas': '#10b981',
                'Despesas Realizadas': '#ef4444',
                'Despesas Pendentes': '#f59e0b'
            }
        )
        
        fig_pizza.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
        )
        
        fig_pizza.update_layout(height=400)
        
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    st.markdown("---")
    
    # Análise por Categoria
    st.subheader("📂 Resumo por Categoria")
    
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        st.markdown("**💸 Top 10 Categorias de Despesas**")
        if 'Categoria' in pr_filtrado.columns:
            top_despesas = pr_filtrado.groupby('Categoria')['Pago ou Recebido'].sum().sort_values(ascending=False).head(10)
            
            fig_top_despesas = px.bar(
                x=top_despesas.values,
                y=top_despesas.index,
                orientation='h',
                text=top_despesas.values,
                color=top_despesas.values,
                color_continuous_scale='Reds'
            )
            
            fig_top_despesas.update_traces(
                texttemplate='R$ %{text:,.2f}',
                textposition='outside'
            )
            
            fig_top_despesas.update_layout(
                showlegend=False,
                xaxis_title="Valor (R$)",
                yaxis_title="",
                height=400,
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig_top_despesas, use_container_width=True)
    
    with col_cat2:
        st.markdown("**💰 Top 10 Categorias de Receitas**")
        if 'Categoria' in cr_filtrado.columns:
            top_receitas = cr_filtrado.groupby('Categoria')['Pago ou Recebido'].sum().sort_values(ascending=False).head(10)
            
            fig_top_receitas = px.bar(
                x=top_receitas.values,
                y=top_receitas.index,
                orientation='h',
                text=top_receitas.values,
                color=top_receitas.values,
                color_continuous_scale='Greens'
            )
            
            fig_top_receitas.update_traces(
                texttemplate='R$ %{text:,.2f}',
                textposition='outside'
            )
            
            fig_top_receitas.update_layout(
                showlegend=False,
                xaxis_title="Valor (R$)",
                yaxis_title="",
                height=400,
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig_top_receitas, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela de Valores por Situação de Vencimento
    st.subheader("📅 Valores por Situação de Vencimento")
    
    tabela_vencimentos = criar_tabela_vencimentos(par_filtrado, 'Vencimento', 'Valor Líquido')
    
    if not tabela_vencimentos.empty:
        st.dataframe(
            tabela_vencimentos,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum dado de vencimento disponível com os filtros aplicados.")

except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")
    st.exception(e)
