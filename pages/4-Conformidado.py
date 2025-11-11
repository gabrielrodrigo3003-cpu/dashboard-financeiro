import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Adicionar pasta utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import format_currency_br, apply_filters_sidebar

st.set_page_config(page_title="Conformidade Emissão x Registro", page_icon="📅", layout="wide")

st.title("📅 Conformidade: Emissão x Registro")
st.markdown("**Análise de conformidade entre data de emissão e data de registro**")
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
    
    # Análise de conformidade para Pagamentos Realizados
    if 'Emissão' in pr_filtrado.columns and 'Data de Registro (completa)' in pr_filtrado.columns:
        pr_filtrado['Emissão'] = pd.to_datetime(pr_filtrado['Emissão'], errors='coerce')
        pr_filtrado['Registro'] = pd.to_datetime(pr_filtrado['Data de Registro (completa)'], errors='coerce')
        
        pr_filtrado['Mes_Emissao'] = pr_filtrado['Emissão'].dt.to_period('M')
        pr_filtrado['Mes_Registro'] = pr_filtrado['Registro'].dt.to_period('M')
        
        pr_filtrado['Conforme'] = pr_filtrado['Mes_Emissao'] == pr_filtrado['Mes_Registro']
        
        conformes_pr = pr_filtrado['Conforme'].sum()
        nao_conformes_pr = (~pr_filtrado['Conforme']).sum()
        total_pr = len(pr_filtrado)
        perc_conformidade_pr = (conformes_pr / total_pr * 100) if total_pr > 0 else 0
    else:
        conformes_pr = 0
        nao_conformes_pr = 0
        total_pr = 0
        perc_conformidade_pr = 0
    
    # Análise de conformidade para Pagamentos a Realizar
    if 'Emissão' in par_filtrado.columns and 'Registro' in par_filtrado.columns:
        par_filtrado['Emissão'] = pd.to_datetime(par_filtrado['Emissão'], errors='coerce')
        par_filtrado['Registro'] = pd.to_datetime(par_filtrado['Registro'], errors='coerce')
        
        par_filtrado['Mes_Emissao'] = par_filtrado['Emissão'].dt.to_period('M')
        par_filtrado['Mes_Registro'] = par_filtrado['Registro'].dt.to_period('M')
        
        par_filtrado['Conforme'] = par_filtrado['Mes_Emissao'] == par_filtrado['Mes_Registro']
        
        conformes_par = par_filtrado['Conforme'].sum()
        nao_conformes_par = (~par_filtrado['Conforme']).sum()
        total_par = len(par_filtrado)
        perc_conformidade_par = (conformes_par / total_par * 100) if total_par > 0 else 0
    else:
        conformes_par = 0
        nao_conformes_par = 0
        total_par = 0
        perc_conformidade_par = 0
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "✅ Conformidade Realizados",
            f"{perc_conformidade_pr:.1f}%",
            f"{conformes_pr}/{total_pr}"
        )
    
    with col2:
        st.metric(
            "✅ Conformidade Pendentes",
            f"{perc_conformidade_par:.1f}%",
            f"{conformes_par}/{total_par}"
        )
    
    with col3:
        total_conformes = conformes_pr + conformes_par
        total_geral = total_pr + total_par
        perc_geral = (total_conformes / total_geral * 100) if total_geral > 0 else 0
        st.metric(
            "📊 Conformidade Geral",
            f"{perc_geral:.1f}%",
            f"{total_conformes}/{total_geral}"
        )
    
    with col4:
        total_nao_conformes = nao_conformes_pr + nao_conformes_par
        st.metric(
            "❌ Não Conformes",
            f"{total_nao_conformes}",
            "Requerem atenção"
        )
    
    st.markdown("---")
    
    # Gráficos
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Conformidade - Pagamentos Realizados")
        
        fig_pr = go.Figure(data=[go.Pie(
            labels=['Conforme (Mesmo Mês)', 'Não Conforme (Mês Diferente)'],
            values=[conformes_pr, nao_conformes_pr],
            hole=0.4,
            marker_colors=['#10b981', '#ef4444'],
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
        )])
        
        fig_pr.update_layout(height=350)
        st.plotly_chart(fig_pr, use_container_width=True)
    
    with col_right:
        st.subheader("📊 Conformidade - Pagamentos Pendentes")
        
        fig_par = go.Figure(data=[go.Pie(
            labels=['Conforme (Mesmo Mês)', 'Não Conforme (Mês Diferente)'],
            values=[conformes_par, nao_conformes_par],
            hole=0.4,
            marker_colors=['#10b981', '#ef4444'],
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
        )])
        
        fig_par.update_layout(height=350)
        st.plotly_chart(fig_par, use_container_width=True)
    
    # Comparativo
    st.markdown("---")
    st.subheader("📈 Comparativo de Conformidade")
    
    fig_comp = go.Figure(data=[
        go.Bar(
            name='Conforme',
            x=['Realizados', 'Pendentes'],
            y=[conformes_pr, conformes_par],
            marker_color='#10b981',
            text=[f'{conformes_pr}', f'{conformes_par}'],
            textposition='auto'
        ),
        go.Bar(
            name='Não Conforme',
            x=['Realizados', 'Pendentes'],
            y=[nao_conformes_pr, nao_conformes_par],
            marker_color='#ef4444',
            text=[f'{nao_conformes_pr}', f'{nao_conformes_par}'],
            textposition='auto'
        )
    ])
    
    fig_comp.update_layout(barmode='group', height=400)
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Tabelas de não conformes
    st.markdown("---")
    
    col_tab1, col_tab2 = st.columns(2)
    
    with col_tab1:
        st.subheader("❌ Pagamentos Realizados Não Conformes")
        
        if 'Conforme' in pr_filtrado.columns:
            nao_conf_pr = pr_filtrado[~pr_filtrado['Conforme']]
            
            if len(nao_conf_pr) > 0:
                colunas_exibir = ['Fornecedor', 'Emissão', 'Registro', 'Pago ou Recebido']
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
                st.success("✅ Todos os pagamentos realizados estão conformes!")
    
    with col_tab2:
        st.subheader("❌ Pagamentos Pendentes Não Conformes")
        
        if 'Conforme' in par_filtrado.columns:
            nao_conf_par = par_filtrado[~par_filtrado['Conforme']]
            
            if len(nao_conf_par) > 0:
                colunas_exibir = ['Razão Social', 'Emissão', 'Registro', 'Valor Líquido']
                colunas_disponiveis = [col for col in colunas_exibir if col in nao_conf_par.columns]
                
                if colunas_disponiveis:
                    df_display = nao_conf_par[colunas_disponiveis].head(20).copy()
                    if 'Valor Líquido' in df_display.columns:
                        df_display['Valor Líquido'] = df_display['Valor Líquido'].apply(format_currency_br)
                    
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.success("✅ Todos os pagamentos pendentes estão conformes!")
    
    # Análise por empresa
    st.markdown("---")
    st.subheader("🏢 Conformidade por Empresa")
    
    if 'Minha Empresa (Nome Fantasia)' in pr_filtrado.columns and 'Conforme' in pr_filtrado.columns:
        conf_empresa = pr_filtrado.groupby('Minha Empresa (Nome Fantasia)')['Conforme'].apply(
            lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0
        ).sort_values(ascending=False)
        
        fig_empresa = px.bar(
            x=conf_empresa.values,
            y=conf_empresa.index,
            orientation='h',
            labels={'x': '% Conformidade', 'y': 'Empresa'},
            color=conf_empresa.values,
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        
        fig_empresa.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_empresa, use_container_width=True)
    
    # Explicação
    st.markdown("---")
    st.info("""
    **ℹ️ Como funciona a análise de conformidade:**
    
    - **Conforme (Verde)**: A data de emissão e a data de registro estão no mesmo mês
    - **Não Conforme (Vermelho)**: A data de emissão e a data de registro estão em meses diferentes
    
    Registros não conformes podem indicar atrasos no processamento ou lançamentos retroativos.
    """)
    
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)

