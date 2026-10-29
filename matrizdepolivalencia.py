import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Matriz de Polivalência", layout="wide")

# ==========================================
# 1. SISTEMA DE LOGIN ADMINISTRATIVO
# ==========================================

# Cria a variável de controle de login na sessão, se não existir
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Tela de Login (Aparece apenas se não estiver logado)
if not st.session_state["logado"]:
    # Adiciona um espaço no topo para empurrar o formulário mais para o centro
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # Layout centralizado para o login (ajustei levemente a proporção para centralizar melhor)
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        # HTML customizado para alinhar ao centro e tirar o espaço entre os títulos
        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="margin-bottom: -15px; font-size: 4rem; color: #0047AB;">FORVIA</h1>
                <h3 style="color: #555555; margin-top: 0px;">Login</h3>
            </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            if btn_login:
                # CREDENCIAIS DE ACESSO (Você pode alterar depois)
                if usuario == "pedrickyst" and senha == "P0313o14@@":
                    st.session_state["logado"] = True
                    st.success("Login efetuado com sucesso!")
                    st.rerun()  # Recarrega a página para entrar no sistema
                else:
                    st.error("Usuário ou senha incorretos. Tente novamente.")

    # Bloqueia a execução do resto do código se não estiver logado
    st.stop()

# ==========================================
# 2. DASHBOARD (Só carrega se estiver logado)
# ==========================================

# Botão de Logout na barra lateral
st.sidebar.markdown(f"👤 Pedro Oliveira")
if st.sidebar.button("Sair (Logout)", type="primary"):
    st.session_state["logado"] = False
    st.rerun()

st.sidebar.divider()


# Simulação dos Dados (Substituiria a chamada da API/Banco de Dados)
@st.cache_data
def carregar_dados():
    dados = {
        "Colaborador": ["Carlos", "Carlos", "Carlos", "Ana", "Ana", "Ana", "João", "João", "João"],
        "Cargo": ["Op. Logística", "Op. Logística", "Op. Logística", "Analista RH", "Analista RH", "Analista RH",
                  "Montador", "Montador", "Montador"],
        "Departamento": ["Logística", "Logística", "Logística", "Recursos Humanos", "Recursos Humanos",
                         "Recursos Humanos", "Produção", "Produção", "Produção"],
        "Competência": ["Empilhadeira", "SAP MM", "Segurança", "Folha de Pagto", "Recrutamento", "Segurança",
                        "Parafusadeira", "Leitura de Desenho", "Segurança"],
        "Nota Atual (0-4)": [4, 2, 3, 4, 3, 4, 2, 1, 3]
    }
    return pd.DataFrame(dados)


df = carregar_dados()

# Cabeçalho e Filtros Laterais
st.title("Polivalência FORVIA")
st.markdown("Acompanhamento do desenvolvimento dos colaboradores e competências nas GAP's.")

st.sidebar.header("Filtros")
departamento_selecionado = st.sidebar.selectbox(
    "Selecione o Departamento",
    options=["Todos"] + list(df["Departamento"].unique())
)

# Aplicando o filtro
if departamento_selecionado != "Todos":
    df_filtrado = df[df["Departamento"] == departamento_selecionado]
else:
    df_filtrado = df

# Construção dos Gráficos Interativos em Azul
col1, col2 = st.columns(2)

with col1:
    st.subheader("Competências")
    # Transformando a tabela (pivot) para o formato da Matriz
    matriz_pivot = df_filtrado.pivot_table(
        index="Colaborador",
        columns="Competência",
        values="Nota Atual (0-4)",
        fill_value=0
    )

    # Heatmap usando a paleta contínua 'Blues'
    fig_heatmap = px.imshow(
        matriz_pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues",  # Aplicação da paleta azul
        range_color=[0, 4],
        labels=dict(color="Evolução dos Colaboradores")
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col2:
    st.subheader("Distribuição de Níveis por Setores")
    # Contagem de notas para ver quantos estão no nível 4 (Multiplicadores)
    contagem_notas = df_filtrado["Nota Atual (0-4)"].value_counts().reset_index()
    contagem_notas.columns = ["Nível", "Quantidade"]
    contagem_notas = contagem_notas.sort_values(by="Nível")

    # Gráfico de barras com tom de azul corporativo
    fig_barras = px.bar(
        contagem_notas,
        x="Nível",
        y="Quantidade",
        color_discrete_sequence=["#1f77b4"],  # Azul padrão do Plotly
        text_auto=True
    )
    fig_barras.update_layout(xaxis_title="Setores (0 a 4)", yaxis_title="Nível de Habilidades")
    st.plotly_chart(fig_barras, use_container_width=True)

st.divider()

# Análise Individual (Gráfico de Radar)
st.subheader("Análise de GAP Individual")
colaborador_selecionado = st.selectbox("Selecione o Colaborador para análise detalhada",
                                       df_filtrado["Colaborador"].unique())

df_colab = df_filtrado[df_filtrado["Colaborador"] == colaborador_selecionado]

# Gráfico de Radar (Teia) com preenchimento azul translúcido
fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=df_colab["Nota Atual (0-4)"].tolist(),
    theta=df_colab["Competência"].tolist(),
    fill='toself',
    name='Nível Atual',
    line=dict(color='#0047AB'),  # Azul Cobalto
    fillcolor='rgba(0, 71, 171, 0.3)'  # Azul Cobalto com 30% de opacidade
))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 4]
        )),
    showlegend=False
)

st.plotly_chart(fig_radar, use_container_width=True)