import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Adicionar pasta utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import format_currency_br, apply_filters_sidebar

st.set_page_config(page_title="Dashboard de Conciliação", page_icon="✅", layout="wide")

st.title("✅ Dashboard de Conciliação")
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
    filtros_ativos = []
    if grupo_sel != 'Todos':
        filtros_ativos.append(f"**Grupo:** {grupo_sel}")
    if empresa_sel != 'Todas':
        filtros_ativos.append(f"**Empresa:** {empresa_sel}")
    if data_inicio and data_fim:
        filtros_ativos.append(f"**Período:** {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    
    if filtros_ativos:
        st.info(f"🔍 Filtros ativos: {' | '.join(filtros_ativos)}")
    
    # Calcular métricas de conciliação
    pr_conciliados = (pr_filtrado['Conciliado'] == 'Sim').sum()
    pr_nao_conciliados = (pr_filtrado['Conciliado'] != 'Sim').sum()
    pr_total = len(pr_filtrado)
    perc_conciliacao_pr = (pr_conciliados / pr_total * 100) if pr_total > 0 else 0
    
    cr_conciliados = (cr_filtrado['Conciliado'] == 'Sim').sum()
    cr_nao_conciliados = (cr_filtrado['Conciliado'] != 'Sim').sum()
    cr_total = len(cr_filtrado)
    perc_conciliacao_cr = (cr_conciliados / cr_total * 100) if cr_total > 0 else 0
    
    # Valores não conciliados
    valor_desp_nao_conc = pr_filtrado[pr_filtrado['Conciliado'] != 'Sim']['Pago ou Recebido'].sum()
    valor_rec_nao_conc = cr_filtrado[cr_filtrado['Conciliado'] != 'Sim']['Pago ou Recebido'].sum()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "✅ Conciliação Despesas",
            f"{perc_conciliacao_pr:.1f}%",
            f"{pr_conciliados}/{pr_total}"
        )
    
    with col2:
        st.metric(
            "✅ Conciliação Receitas",
            f"{perc_conciliacao_cr:.1f}%",
            f"{cr_conciliados}/{cr_total}"
        )
    
    with col3:
        st.metric(
            "❌ Despesas Não Conciliadas",
            format_currency_br(valor_desp_nao_conc),
            f"{pr_nao_conciliados} registros"
        )
    
    with col4:
        st.metric(
            "❌ Receitas Não Conciliadas",
            format_currency_br(valor_rec_nao_conc),
            f"{cr_nao_conciliados} registros"
        )
    
    st.markdown("---")
    
    # Gráficos de conciliação
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Status de Conciliação - Despesas")
        
        fig_desp = go.Figure(data=[go.Pie(
            labels=['Conciliadas', 'Não Conciliadas'],
            values=[pr_conciliados, pr_nao_conciliados],
            hole=0.4,
            marker_colors=['#10b981', '#ef4444'],
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
        )])
        
        fig_desp.update_layout(height=350)
        st.plotly_chart(fig_desp, use_container_width=True)
        
        st.metric("Total de Despesas", f"{pr_total:,} transações")
    
    with col_right:
        st.subheader("📊 Status de Conciliação - Receitas")
        
        fig_rec = go.Figure(data=[go.Pie(
            labels=['Conciliadas', 'Não Conciliadas'],
            values=[cr_conciliados, cr_nao_conciliados],
            hole=0.4,
            marker_colors=['#10b981', '#ef4444'],
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
        )])
        
        fig_rec.update_layout(height=350)
        st.plotly_chart(fig_rec, use_container_width=True)
        
        st.metric("Total de Receitas", f"{cr_total:,} transações")
    
    # Análise comparativa
    st.markdown("---")
    st.subheader("📈 Comparativo de Conciliação")
    
    fig_comp = go.Figure(data=[
        go.Bar(
            name='Conciliadas',
            x=['Despesas', 'Receitas'],
            y=[pr_conciliados, cr_conciliados],
            marker_color='#10b981',
            text=[f'{pr_conciliados}', f'{cr_conciliados}'],
            textposition='auto'
        ),
        go.Bar(
            name='Não Conciliadas',
            x=['Despesas', 'Receitas'],
            y=[pr_nao_conciliados, cr_nao_conciliados],
            marker_color='#ef4444',
            text=[f'{pr_nao_conciliados}', f'{cr_nao_conciliados}'],
            textposition='auto'
        )
    ])
    
    fig_comp.update_layout(barmode='group', height=400)
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Tabelas de itens não conciliados
    st.markdown("---")
    
    col_tab1, col_tab2 = st.columns(2)
    
    with col_tab1:
        st.subheader("❌ Despesas Não Conciliadas")
        
        nao_conf_pr = pr_filtrado[pr_filtrado['Conciliado'] != 'Sim']
        
        if len(nao_conf_pr) > 0:
            colunas_exibir = ['Fornecedor', 'Pago ou Recebido', 'Categoria']
            colunas_disponiveis = [col for col in colunas_exibir if col in nao_conf_pr.columns]
            
            if colunas_disponiveis:
                df_display = nao_conf_pr[colunas_disponiveis].head(20).copy()
                if 'Pago ou Recebido' in df_display.columns:
                    df_display['Pago ou Recebido'] = df_display['Pago ou Recebido'].apply(format_currency_br)
                
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.success("✅ Todas as despesas estão conciliadas!")
    
    with col_tab2:
        st.subheader("❌ Receitas Não Conciliadas")
        
        nao_conf_cr = cr_filtrado[cr_filtrado['Conciliado'] != 'Sim']
        
        if len(nao_conf_cr) > 0:
            colunas_exibir = ['Cliente', 'Pago ou Recebido', 'Categoria']
            colunas_disponiveis = [col for col in colunas_exibir if col in nao_conf_cr.columns]
            
            if colunas_disponiveis:
                df_display = nao_conf_cr[colunas_disponiveis].head(20).copy()
                if 'Pago ou Recebido' in df_display.columns:
                    df_display['Pago ou Recebido'] = df_display['Pago ou Recebido'].apply(format_currency_br)
                
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.success("✅ Todas as receitas estão conciliadas!")
    
    # Análise por empresa
    st.markdown("---")
    st.subheader("🏢 Conciliação por Empresa")
    
    if 'Minha Empresa (Nome Fantasia)' in pr_filtrado.columns:
        conc_empresa = pr_filtrado.groupby('Minha Empresa (Nome Fantasia)')['Conciliado'].apply(
            lambda x: (x == 'Sim').sum() / len(x) * 100 if len(x) > 0 else 0
        ).sort_values(ascending=False)
        
        fig_empresa = px.bar(
            x=conc_empresa.values,
            y=conc_empresa.index,
            orientation='h',
            labels={'x': '% Conciliação', 'y': 'Empresa'},
            color=conc_empresa.values,
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        
        fig_empresa.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_empresa, use_container_width=True)
    
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)

