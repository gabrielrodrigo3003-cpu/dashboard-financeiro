import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Adicionar pasta utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import format_currency_br, apply_filters_sidebar, criar_tabela_vencimentos

st.set_page_config(page_title="Dashboard de Despesas", page_icon="💸", layout="wide")

st.title("💸 Dashboard de Despesas")
st.markdown("**Análise detalhada de despesas realizadas e pendentes**")
st.markdown("---")

@st.cache_data
def load_data():
    pr = pd.read_excel('data/PagamentosRealizadosRelatorio.xlsx')
    cr = pd.read_excel('data/ContasRecebidaseaReceber.xlsx')
    par = pd.read_excel('data/PagamentosaRealizarRelatorio.xlsx')
    return pr, cr, par

try:
    pr, cr, par = load_data()
    
    # Aplicar filtros globais
    pr_filtrado, cr_filtrado, par_filtrado, grupo_sel, empresa_sel, data_inicio, data_fim, grupos_despesa_sel, categorias_sel = apply_filters_sidebar(pr, cr, par)
    
    # Mostrar filtros ativos
    if grupo_sel != 'Todos' or empresa_sel != 'Todas':
        filtros_ativos = []
        if grupo_sel != 'Todos':
            filtros_ativos.append(f"**Grupo:** {grupo_sel}")
        if empresa_sel != 'Todas':
            filtros_ativos.append(f"**Empresa:** {empresa_sel}")
        st.info(f"🔍 Filtros ativos: {' | '.join(filtros_ativos)}")
    
    # Calcular métricas
    total_desp_realizadas = pr_filtrado['Pago ou Recebido'].sum()
    total_desp_pendentes = par_filtrado['Valor Líquido'].sum()
    total_geral = total_desp_realizadas + total_desp_pendentes
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💸 Despesas Realizadas",
            format_currency_br(total_desp_realizadas),
            f"{len(pr_filtrado)} pagamentos"
        )
    
    with col2:
        st.metric(
            "⏳ Despesas Pendentes",
            format_currency_br(total_desp_pendentes),
            f"{len(par_filtrado)} contas"
        )
    
    with col3:
        st.metric(
            "💰 Total Geral",
            format_currency_br(total_geral),
            f"{len(pr_filtrado) + len(par_filtrado)} registros"
        )
    
    with col4:
        perc_realizado = (total_desp_realizadas / total_geral * 100) if total_geral > 0 else 0
        st.metric(
            "📊 % Realizado",
            f"{perc_realizado:.1f}%",
            "Do total"
        )
    
    st.markdown("---")
    
    # Tabela de Valores por Situação de Vencimento (Ordenada Temporalmente)
    st.subheader("📅 Valores por Situação de Vencimento")
    st.markdown("*Ordenado por proximidade temporal do vencimento*")
    
    tabela_vencimentos = criar_tabela_vencimentos(par_filtrado, 'Vencimento', 'Valor Líquido')
    
    if not tabela_vencimentos.empty:
        st.dataframe(
            tabela_vencimentos,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Não há dados de vencimento disponíveis.")
    
    st.markdown("---")
    
    # Gráficos
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Despesas: Realizadas vs Pendentes")
        
        fig_status = go.Figure(data=[
            go.Bar(
                name='Realizadas',
                x=['Despesas'],
                y=[total_desp_realizadas],
                marker_color='#10b981',
                text=[format_currency_br(total_desp_realizadas)],
                textposition='auto'
            ),
            go.Bar(
                name='Pendentes',
                x=['Despesas'],
                y=[total_desp_pendentes],
                marker_color='#f59e0b',
                text=[format_currency_br(total_desp_pendentes)],
                textposition='auto'
            )
        ])
        
        fig_status.update_layout(barmode='group', height=400, showlegend=True)
        fig_status.update_yaxes(title_text='Valor (R$)')
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col_right:
        st.subheader("🥧 Distribuição de Despesas")
        
        fig_dist = go.Figure(data=[go.Pie(
            labels=['Realizadas', 'Pendentes'],
            values=[total_desp_realizadas, total_desp_pendentes],
            hole=0.4,
            marker_colors=['#10b981', '#f59e0b'],
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
        )])
        
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Análise por categoria
    st.markdown("---")
    st.subheader("📂 Despesas por Categoria")
    
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        st.markdown("**Despesas Realizadas**")
        
        if 'Categoria' in pr_filtrado.columns:
            cat_realizadas = pr_filtrado.groupby('Categoria')['Pago ou Recebido'].sum().sort_values(ascending=False).head(10)
            
            fig_cat_real = px.bar(
                x=cat_realizadas.values,
                y=cat_realizadas.index,
                orientation='h',
                labels={'x': 'Valor (R$)', 'y': 'Categoria'},
                color=cat_realizadas.values,
                color_continuous_scale='Greens'
            )
            
            fig_cat_real.update_layout(height=400, showlegend=False)
            fig_cat_real.update_traces(
                hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_cat_real, use_container_width=True)
    
    with col_cat2:
        st.markdown("**Despesas Pendentes**")
        
        if 'Categoria' in par_filtrado.columns:
            cat_pendentes = par_filtrado.groupby('Categoria')['Valor Líquido'].sum().sort_values(ascending=False).head(10)
            
            fig_cat_pend = px.bar(
                x=cat_pendentes.values,
                y=cat_pendentes.index,
                orientation='h',
                labels={'x': 'Valor (R$)', 'y': 'Categoria'},
                color=cat_pendentes.values,
                color_continuous_scale='Oranges'
            )
            
            fig_cat_pend.update_layout(height=400, showlegend=False)
            fig_cat_pend.update_traces(
                hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_cat_pend, use_container_width=True)
    
    # Top 10 Fornecedores
    st.markdown("---")
    st.subheader("🏢 Top 10 Fornecedores")
    
    col_forn1, col_forn2 = st.columns(2)
    
    with col_forn1:
        st.markdown("**Por Despesas Realizadas**")
        
        if 'Fornecedor' in pr_filtrado.columns:
            top_forn_real = pr_filtrado.groupby('Fornecedor')['Pago ou Recebido'].sum().sort_values(ascending=False).head(10)
            
            fig_forn_real = px.bar(
                x=top_forn_real.values,
                y=top_forn_real.index,
                orientation='h',
                labels={'x': 'Valor Total (R$)', 'y': 'Fornecedor'},
                color=top_forn_real.values,
                color_continuous_scale='Blues'
            )
            
            fig_forn_real.update_layout(height=400, showlegend=False)
            fig_forn_real.update_traces(
                hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_forn_real, use_container_width=True)
    
    with col_forn2:
        st.markdown("**Por Despesas Pendentes**")
        
        if 'Razão Social' in par_filtrado.columns:
            top_forn_pend = par_filtrado.groupby('Razão Social')['Valor Líquido'].sum().sort_values(ascending=False).head(10)
            
            fig_forn_pend = px.bar(
                x=top_forn_pend.values,
                y=top_forn_pend.index,
                orientation='h',
                labels={'x': 'Valor Total (R$)', 'y': 'Fornecedor'},
                color=top_forn_pend.values,
                color_continuous_scale='Reds'
            )
            
            fig_forn_pend.update_layout(height=400, showlegend=False)
            fig_forn_pend.update_traces(
                hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_forn_pend, use_container_width=True)
    
    # Evolução temporal
    st.markdown("---")
    st.subheader("📈 Evolução Temporal das Despesas Realizadas")
    
    if 'Data de Registro (completa)' in pr_filtrado.columns:
        pr_temp = pr_filtrado.copy()
        pr_temp['Data de Registro (completa)'] = pd.to_datetime(pr_temp['Data de Registro (completa)'], errors='coerce')
        pr_temp['Mes_Ano'] = pr_temp['Data de Registro (completa)'].dt.to_period('M').astype(str)
        
        evolucao = pr_temp.groupby('Mes_Ano')['Pago ou Recebido'].sum().reset_index()
        evolucao = evolucao.sort_values('Mes_Ano')
        
        fig_evolucao = px.line(
            evolucao,
            x='Mes_Ano',
            y='Pago ou Recebido',
            markers=True,
            labels={'Mes_Ano': 'Mês/Ano', 'Pago ou Recebido': 'Valor (R$)'}
        )
        
        fig_evolucao.update_layout(height=400)
        fig_evolucao.update_traces(
            line_color='#ef4444',
            hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)

