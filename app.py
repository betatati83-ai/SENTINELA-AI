import streamlit as st
import yfinance as yf
from GoogleNews import GoogleNews
import plotly.graph_objects as go
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA E ESTILO VISUAL ---
st.set_page_config(page_title="Sentinela Trader Pro", page_icon="🦅", layout="wide")

# CSS Personalizado para um visual mais "Google/Moderno"
st.markdown("""
<style>
    /* Importa uma fonte mais moderna do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    /* Aplica a fonte em todo o app */
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Deixa os títulos mais elegantes */
    h1, h2, h3 {
        font-weight: 700;
        color: #ffffff; /* Cor branca para destaque no tema escuro */
    }

    /* Estiliza o botão principal para parecer mais sofisticado */
    div.stButton > button:first-child {
        background-color: #FF4B4B; /* Cor de destaque do Streamlit */
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease 0s;
    }
    div.stButton > button:first-child:hover {
        background-color: #E63946; /* Cor um pouco mais escura ao passar o mouse */
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
def verificar_senha():
    if "senha_correta" not in st.session_state: st.session_state["senha_correta"] = False
    def senha_digitada():
        st.session_state["senha_correta"] = st.session_state["input_senha"] == "trader123"
    if not st.session_state["senha_correta"]:
        st.markdown("## 🔒 Acesso Restrito")
        st.text_input("Digite sua credencial:", type="password", key="input_senha", on_change=senha_digitada)
        return False
    return True

if not verificar_senha(): st.stop()

# --- FUNÇÕES MATEMÁTICAS ---
def calcular_rsi(dados, periodos=14):
    delta = dados['Close'].diff()
    ganho = (delta.where(delta > 0, 0)).rolling(window=periodos).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=periodos).mean()
    rs = ganho / perda
    return 100 - (100 / (1 + rs))

def calcular_media_movel(dados, periodos=20):
    return dados['Close'].rolling(window=periodos).mean()

def criar_velocimetro(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "TERMÔMETRO DE MERCADO", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 25], 'color': '#ff4d4d'},
                {'range': [25, 50], 'color': '#ffa64d'},
                {'range': [50, 75], 'color': '#ffff4d'},
                {'range': [75, 100], 'color': '#00cc66'}],
            }))
    return fig

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🦅 Painel de Controle")
    with st.form(key='painel_trader'):
        # Rótulos limpos, sem exemplos
        ticker = st.text_input("Código do Ativo", value="BTC-USD")
        termo = st.text_input("Filtro de Notícias", value="Bitcoin")
        opcoes_periodo = {"1 Mês": "1mo", "3 Meses": "3mo", "6 Meses": "6mo", "1 Ano": "1y"}
        periodo_selecionado = st.selectbox("Período de Análise", list(opcoes_periodo.keys()))
        botao_enviar = st.form_submit_button("EXECUTAR ANÁLISE 🚀", type="primary")
    
    st.markdown("---")
    # --- BOTÃO DE AJUDA INTELIGENTE ---
    with st.expander("📘 AJUDA E INSTRUÇÕES"):
        st.markdown("""
        ### Como usar o Sentinela AI:
        1.  *Código do Ativo:* Digite o código universal. Ex: BTC-USD para Bitcoin, PETR4.SA para Petrobras, AAPL para Apple.
        2.  *Filtro de Notícias:* Palavra-chave para buscar na mídia. Ex: "Bitcoin", "Petróleo", "Tecnologia".
        3.  *Período:* Quanto tempo de histórico você quer analisar.
        4.  Clique em *EXECUTAR ANÁLSE* para rodar.

        ---
        ### Como ler os resultados:
        * *Termômetro:* Pontuação de 0 a 100 que mistura análise técnica e notícias.
            * 🔴 *0-25:* Pessimismo extremo (Possível venda).
            * 🟢 *75-100:* Otimismo extremo (Possível compra).
        * *Indicador RSI:*
            * *< 30 (Barato):* O preço caiu muito rápido, pode repicar para cima.
            * *> 70 (Caro):* O preço subiu muito rápido, pode corrigir para baixo.

        ### Como ler o Gráfico:
        * *Velas (Candles):*
            * 🟩 *Verde:* O preço fechou mais alto que abriu nesse dia.
            * 🟥 *Vermelho:* O preço fechou mais baixo que abriu.
        * *Linha Azul (Média Móvel):* Mostra a tendência média dos últimos 20 dias.
            * Se as velas estão *acima* da linha, a tendência é de *ALTA*.
            * Se estão *abaixo, a tendência é de **BAIXA*.
        """)

    if st.button("Sair do Sistema"):
        st.session_state["senha_correta"] = False
        st.rerun()

# --- LÓGICA PRINCIPAL ---
st.title("🦅 Sentinela AI - Terminal Executivo")
st.markdown("---")

if botao_enviar:
    try:
        with st.spinner("Conectando satélites e processando dados..."):
            acao = yf.Ticker(ticker)
            codigo_periodo = opcoes_periodo[periodo_selecionado]
            historico = acao.history(period=codigo_periodo)
            
            if len(historico) > 0:
                # PROVA DA DATA RECENTE
                ultima_data = historico.index[-1].strftime('%d/%m/%Y')
                st.caption(f"✅ Dados atualizados com sucesso. Última cotação recebida em: *{ultima_data}*")

                historico['RSI'] = calcular_rsi(historico)
                historico['SMA'] = calcular_media_movel(historico)
                
                preco_atual = historico['Close'].iloc[-1]
                rsi_atual = historico['RSI'].iloc[-1]
                if len(historico) > 1:
                    variacao = ((preco_atual - historico['Close'].iloc[-2]) / historico['Close'].iloc[-2]) * 100
                else: variacao = 0
                
                info = acao.info
                moeda = info.get('currency', 'USD')
                simbolo_visual = "R$" if moeda == "BRL" else "$"

                googlenews = GoogleNews(lang='pt', region='BR')
                googlenews.search(termo)
                noticias = googlenews.result()
                
                score = 50
                if rsi_atual < 30: score += 15
                if rsi_atual > 70: score -= 15
                if variacao > 0: score += 5
                palavras_chave = ['alta', 'lucro', 'recorde', 'compra', 'otimismo', 'sobe', 'positivo']
                count_news = 0
                if noticias:
                    for n in noticias[:5]:
                        for p in palavras_chave:
                            if p in n['title'].lower(): count_news += 1
                score += (count_news * 5)
                score = max(0, min(100, score))

                col1, col2, col3 = st.columns(3)
                col1.metric("Preço de Mercado", f"{simbolo_visual} {preco_atual:,.2f}")
                col1.metric("Variação Hoje", f"{variacao:.2f}%", delta_color="normal")
                
                rsi_texto = "Neutro"
                if rsi_atual < 30: rsi_texto = "Oportunidade (Barato)"
                elif rsi_atual > 70: rsi_texto = "Cuidado (Caro)"
                
                col2.metric("Técnico: RSI (14)", f"{rsi_atual:.0f}", rsi_texto)
                col3.metric("Score Global Sentinela", f"{score}/100")

                st.plotly_chart(criar_velocimetro(score), use_container_width=True)

                st.subheader("📈 Gráfico de Tendência Profissional")
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=historico.index,
                                open=historico['Open'], high=historico['High'],
                                low=historico['Low'], close=historico['Close'], name="Preço"))
                fig.add_trace(go.Scatter(x=historico.index, y=historico['SMA'], 
                                         line=dict(color='#2962FF', width=2), name="Média Móvel (20)"))
                fig.update_layout(height=450, xaxis_rangeslider_visible=False, 
                                  plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                  xaxis=dict(showgrid=True, gridcolor='#333333'),
                                  yaxis=dict(showgrid=True, gridcolor='#333333'))
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📰 Manchetes Relevantes")
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"""
                        <div style='background-color: #262730; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4B4B;'>
                            <a href='{n['link']}' target='_blank' style='text-decoration: none; color: white; font-weight: bold; font-size: 1.1em;'>
                                {n['title']}
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhuma notícia encontrada para este filtro.")

            else:
                st.error("Ativo não encontrado. Verifique o código digitado.")

    except Exception as e:
        st.error(f"Erro de processamento: {e}")