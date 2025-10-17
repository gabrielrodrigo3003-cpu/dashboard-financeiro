import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Adicionar pasta utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import format_currency_br, apply_filters_sidebar

st.set_page_config(page_title="Dashboard de Receitas", page_icon="💰", layout="wide")

st.title("💰 Dashboard de Receitas")
st.markdown("**Análise detalhada de receitas recebidas e a receber**")
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
    total_receitas = cr_filtrado['Pago ou Recebido'].sum()
    num_transacoes = len(cr_filtrado)
    ticket_medio = total_receitas / num_transacoes if num_transacoes > 0 else 0
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Total de Receitas",
            format_currency_br(total_receitas),
            f"{num_transacoes} transações"
        )
    
    with col2:
        st.metric(
            "📊 Ticket Médio",
            format_currency_br(ticket_medio),
            "Por transação"
        )
    
    with col3:
        receitas_conciliadas = (cr_filtrado['Conciliado'] == 'Sim').sum()
        perc_conciliacao = (receitas_conciliadas / num_transacoes * 100) if num_transacoes > 0 else 0
        st.metric(
            "✅ Taxa de Conciliação",
            f"{perc_conciliacao:.1f}%",
            f"{receitas_conciliadas}/{num_transacoes}"
        )
    
    with col4:
        if 'Categoria' in cr_filtrado.columns:
            num_categorias = cr_filtrado['Categoria'].nunique()
            st.metric(
                "📂 Categorias",
                f"{num_categorias}",
                "Diferentes"
            )
        else:
            st.metric("📂 Categorias", "N/A")
    
    st.markdown("---")
    
    # Gráficos
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Evolução Temporal das Receitas")
        
        if 'Data de Crédito ou Débito (No Extrato)' in cr_filtrado.columns:
            cr_temp = cr_filtrado.copy()
            cr_temp['Data de Crédito ou Débito (No Extrato)'] = pd.to_datetime(cr_temp['Data de Crédito ou Débito (No Extrato)'], errors='coerce')
            cr_temp['Mes_Ano'] = cr_temp['Data de Crédito ou Débito (No Extrato)'].dt.to_period('M').astype(str)
            
            evolucao = cr_temp.groupby('Mes_Ano')['Pago ou Recebido'].sum().reset_index()
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
                line_color='#10b981',
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_evolucao, use_container_width=True)
    
    with col_right:
        st.subheader("📊 Receitas por Categoria")
        
        if 'Categoria' in cr_filtrado.columns:
            cat_receitas = cr_filtrado.groupby('Categoria')['Pago ou Recebido'].sum().sort_values(ascending=False).head(10)
            
            fig_cat = px.bar(
                x=cat_receitas.values,
                y=cat_receitas.index,
                orientation='h',
                labels={'x': 'Valor (R$)', 'y': 'Categoria'},
                color=cat_receitas.values,
                color_continuous_scale='Greens'
            )
            
            fig_cat.update_layout(height=400, showlegend=False)
            fig_cat.update_traces(
                hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_cat, use_container_width=True)
    
    # Top 10 Clientes
    st.markdown("---")
    st.subheader("🏆 Top 10 Clientes por Receita")
    
    if 'Cliente' in cr_filtrado.columns:
        top_clientes = cr_filtrado.groupby('Cliente').agg({
            'Pago ou Recebido': 'sum',
            'Cliente': 'count'
        }).rename(columns={'Cliente': 'Num_Transacoes'})
        top_clientes = top_clientes.sort_values('Pago ou Recebido', ascending=False).head(10)
        
        col_top1, col_top2 = st.columns([2, 1])
        
        with col_top1:
            fig_top = px.bar(
                x=top_clientes['Pago ou Recebido'],
                y=top_clientes.index,
                orientation='h',
                labels={'x': 'Receita Total (R$)', 'y': 'Cliente'},
                color=top_clientes['Pago ou Recebido'],
                color_continuous_scale='Blues'
            )
            
            fig_top.update_layout(height=400, showlegend=False)
            fig_top.update_traces(
                hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>'
            )
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col_top2:
            st.markdown("**Detalhamento**")
            
            tabela_top = pd.DataFrame({
                'Cliente': top_clientes.index,
                'Receita Total': top_clientes['Pago ou Recebido'].apply(format_currency_br),
                'Transações': top_clientes['Num_Transacoes']
            })
            
            st.dataframe(
                tabela_top,
                use_container_width=True,
                hide_index=True
            )
    
    # Distribuição por Status de Conciliação
    st.markdown("---")
    
    col_conc1, col_conc2 = st.columns(2)
    
    with col_conc1:
        st.subheader("✅ Status de Conciliação")
        
        conciliadas = (cr_filtrado['Conciliado'] == 'Sim').sum()
        nao_conciliadas = (cr_filtrado['Conciliado'] != 'Sim').sum()
        
        fig_conc = go.Figure(data=[go.Pie(
            labels=['Conciliadas', 'Não Conciliadas'],
            values=[conciliadas, nao_conciliadas],
            hole=0.4,
            marker_colors=['#10b981', '#ef4444'],
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
        )])
        
        fig_conc.update_layout(height=350)
        st.plotly_chart(fig_conc, use_container_width=True)
    
    with col_conc2:
        st.subheader("📊 Valores por Status")
        
        valor_conciliadas = cr_filtrado[cr_filtrado['Conciliado'] == 'Sim']['Pago ou Recebido'].sum()
        valor_nao_conciliadas = cr_filtrado[cr_filtrado['Conciliado'] != 'Sim']['Pago ou Recebido'].sum()
        
        fig_val_conc = go.Figure(data=[
            go.Bar(
                name='Conciliadas',
                x=['Receitas'],
                y=[valor_conciliadas],
                marker_color='#10b981',
                text=[format_currency_br(valor_conciliadas)],
                textposition='auto'
            ),
            go.Bar(
                name='Não Conciliadas',
                x=['Receitas'],
                y=[valor_nao_conciliadas],
                marker_color='#ef4444',
                text=[format_currency_br(valor_nao_conciliadas)],
                textposition='auto'
            )
        ])
        
        fig_val_conc.update_layout(barmode='group', height=350, showlegend=True)
        fig_val_conc.update_yaxes(title_text='Valor (R$)')
        st.plotly_chart(fig_val_conc, use_container_width=True)
    
    # Análise por Empresa
    st.markdown("---")
    st.subheader("🏢 Receitas por Empresa")
    
    if 'Minha Empresa (Razão Social)' in cr_filtrado.columns:
        receitas_empresa = cr_filtrado.groupby('Minha Empresa (Razão Social)')['Pago ou Recebido'].sum().sort_values(ascending=False)
        
        fig_empresa = px.bar(
            x=receitas_empresa.values,
            y=receitas_empresa.index,
            orientation='h',
            labels={'x': 'Receita Total (R$)', 'y': 'Empresa'},
            color=receitas_empresa.values,
            color_continuous_scale='Viridis'
        )
        
        fig_empresa.update_layout(height=400, showlegend=False)
        fig_empresa.update_traces(
            hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig_empresa, use_container_width=True)
    
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)

