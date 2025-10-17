import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Adicionar pasta utils ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.helpers import format_currency_br, apply_filters_sidebar

st.set_page_config(page_title="Previsão de Faturamento", page_icon="🔮", layout="wide")

st.title("🔮 Previsão de Faturamento")
st.markdown("**Análise de faturamento futuro e tendências**")
st.markdown("---")

@st.cache_data
def load_data():
    pr = pd.read_excel('data/PagamentosRealizadosRelatorio.xlsx')
    cr = pd.read_excel('data/ContasRecebidaseaReceber.xlsx')
    par = pd.read_excel('data/PagamentosaRealizarRelatorio.xlsx')
    pf = pd.read_excel('data/PrevisaoFaturamento.xlsx')
    return pr, cr, par, pf

try:
    pr, cr, par, pf = load_data()
    
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
    
    st.subheader("📊 Previsão de Faturamento por Empresa")
    
    # Mostrar dados de previsão
    if len(pf) > 0:
        # Formatar valores para exibição
        pf_display = pf.copy()
        for col in pf_display.columns:
            if col != 'Minha Empresa (Nome Fantasia)':
                try:
                    pf_display[col] = pf_display[col].apply(lambda x: format_currency_br(x) if pd.notna(x) else '-')
                except:
                    pass
        
        st.dataframe(pf_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Processar dados para visualização
        colunas_data = [col for col in pf.columns if col != 'Minha Empresa (Nome Fantasia)']
        
        # Criar gráfico de linha para cada empresa
        st.subheader("📈 Evolução do Faturamento Previsto")
        
        # Transformar dados para formato longo
        pf_long = pf.melt(
            id_vars=['Minha Empresa (Nome Fantasia)'],
            value_vars=colunas_data,
            var_name='Data',
            value_name='Valor'
        )
        
        # Converter datas
        pf_long['Data'] = pd.to_datetime(pf_long['Data'], errors='coerce')
        pf_long = pf_long.dropna(subset=['Data'])
        pf_long = pf_long.sort_values('Data')
        
        # Gráfico de linhas
        fig_linha = px.line(
            pf_long,
            x='Data',
            y='Valor',
            color='Minha Empresa (Nome Fantasia)',
            markers=True,
            labels={'Valor': 'Faturamento Previsto (R$)', 'Data': 'Data'}
        )
        
        fig_linha.update_layout(height=500, hovermode='x unified')
        fig_linha.update_traces(
            hovertemplate='<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig_linha, use_container_width=True)
        
        st.markdown("---")
        
        # Total previsto por período
        st.subheader("💰 Total Previsto por Período")
        
        total_por_data = pf_long.groupby('Data')['Valor'].sum().reset_index()
        
        fig_total = go.Figure()
        
        fig_total.add_trace(go.Bar(
            x=total_por_data['Data'],
            y=total_por_data['Valor'],
            marker_color='#3b82f6',
            text=total_por_data['Valor'].apply(lambda x: format_currency_br(x)),
            textposition='auto',
            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig_total.update_layout(
            xaxis_title='Data',
            yaxis_title='Valor (R$)',
            height=400
        )
        
        st.plotly_chart(fig_total, use_container_width=True)
        
        # KPIs
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_previsto = pf_long['Valor'].sum()
        media_por_periodo = pf_long.groupby('Data')['Valor'].sum().mean()
        num_empresas = pf['Minha Empresa (Nome Fantasia)'].nunique()
        num_periodos = len(colunas_data)
        
        with col1:
            st.metric("💰 Total Previsto", format_currency_br(total_previsto))
        
        with col2:
            st.metric("📊 Média por Período", format_currency_br(media_por_periodo))
        
        with col3:
            st.metric("🏢 Empresas", f"{num_empresas}")
        
        with col4:
            st.metric("📅 Períodos", f"{num_periodos}")
        
        st.markdown("---")
        
        # Comparação com receitas realizadas
        st.subheader("📊 Comparação: Previsto vs Realizado")
        
        # Calcular total realizado
        total_realizado = cr_filtrado['Pago ou Recebido'].sum()
        
        fig_comp = go.Figure(data=[
            go.Bar(
                name='Realizado',
                x=['Faturamento'],
                y=[total_realizado],
                marker_color='#10b981',
                text=[format_currency_br(total_realizado)],
                textposition='auto',
                hovertemplate='<b>Realizado</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
            ),
            go.Bar(
                name='Previsto',
                x=['Faturamento'],
                y=[total_previsto],
                marker_color='#3b82f6',
                text=[format_currency_br(total_previsto)],
                textposition='auto',
                hovertemplate='<b>Previsto</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        ])
        
        fig_comp.update_layout(
            barmode='group',
            height=400,
            yaxis_title='Valor (R$)'
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Análise por empresa
        st.markdown("---")
        st.subheader("🏢 Faturamento Previsto por Empresa")
        
        total_por_empresa = pf_long.groupby('Minha Empresa (Nome Fantasia)')['Valor'].sum().sort_values(ascending=False)
        
        fig_empresa = px.bar(
            x=total_por_empresa.values,
            y=total_por_empresa.index,
            orientation='h',
            labels={'x': 'Faturamento Previsto (R$)', 'y': 'Empresa'},
            color=total_por_empresa.values,
            color_continuous_scale='Blues'
        )
        
        fig_empresa.update_layout(height=400, showlegend=False)
        fig_empresa.update_traces(
            hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig_empresa, use_container_width=True)
        
        # Tabela resumo
        st.markdown("---")
        st.subheader("📋 Resumo por Empresa")
        
        resumo_empresa = pf_long.groupby('Minha Empresa (Nome Fantasia)').agg({
            'Valor': ['sum', 'mean', 'count']
        }).round(2)
        
        resumo_empresa.columns = ['Total Previsto', 'Média por Período', 'Nº Períodos']
        resumo_empresa = resumo_empresa.sort_values('Total Previsto', ascending=False)
        
        # Formatar para exibição
        resumo_display = resumo_empresa.copy()
        resumo_display['Total Previsto'] = resumo_display['Total Previsto'].apply(format_currency_br)
        resumo_display['Média por Período'] = resumo_display['Média por Período'].apply(format_currency_br)
        
        st.dataframe(
            resumo_display,
            use_container_width=True
        )
        
    else:
        st.warning("⚠️ Não há dados de previsão de faturamento disponíveis.")
    
    # Informações adicionais
    st.markdown("---")
    st.info("""
    **ℹ️ Sobre a Previsão de Faturamento:**
    
    - Os dados apresentados são baseados nas previsões registradas no sistema
    - A comparação com valores realizados ajuda a avaliar a precisão das previsões
    - Utilize os filtros para analisar períodos e empresas específicas
    """)
    
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.exception(e)

