import streamlit as st
import yfinance as yf
from GoogleNews import GoogleNews
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sentinela AI - Ouro", page_icon="🦅", layout="wide")

# Visual Moderno (CSS)
st.markdown("""
<style>
    /* Esconde o menu padrão e rodapé para ficar pro */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Botão verde bonito */
    div.stButton > button:first-child {
        background-color: #00C853; color: white; border-radius: 8px; 
        border: none; padding: 12px 24px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
def verificar_senha():
    if "senha_correta" not in st.session_state: st.session_state["senha_correta"] = False
    def senha_digitada():
        st.session_state["senha_correta"] = st.session_state["input_senha"] == "trader123"
    if not st.session_state["senha_correta"]:
        st.markdown("## 🔒 Acesso Restrito")
        st.text_input("Senha:", type="password", key="input_senha", on_change=senha_digitada)
        return False
    return True

if not verificar_senha(): st.stop()

# --- FUNÇÕES ---
def analisar_com_gemini(termo, noticias):
    # Tenta pegar a chave do cofre (Secrets)
    if "GEMINI_KEY" in st.secrets:
        chave = st.secrets["GEMINI_KEY"]
    else:
        # Se não achar a chave (ex: no computador local), avisa
        return "SCORE: 50\nRESUMO: Chave de IA não encontrada (Rodando Local?).\nACAO: NEUTRO"
        
    try:
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-1.5-flash')
        texto_noticias = "\n".join([f"- {n['title']}" for n in noticias[:5]])
        prompt = f"""
        Analise estas notícias sobre '{termo}':
        {texto_noticias}
        Responda neste formato:
        SCORE: [0-100]
        RESUMO: [Frase curta em Português]
        ACAO: [COMPRA/VENDA/NEUTRO]
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"SCORE: 50\nRESUMO: Erro técnico na IA ({e})\nACAO: ERRO"

def criar_velocimetro(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "SENTIMENTO (IA)", 'font': {'size': 20}},
        gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "black"},
                 'steps': [{'range': [0, 25], 'color': '#ff4d4d'}, {'range': [25, 50], 'color': '#ffa64d'},
                           {'range': [50, 75], 'color': '#ffff4d'}, {'range': [75, 100], 'color': '#00cc66'}]}))
    return fig

# --- INTERFACE ---
with st.sidebar:
    st.header("🦅 Painel de Controle")
    ticker = st.text_input("Ativo (Ex: BTC-USD)", value="BTC-USD")
    termo = st.text_input("Tema (Ex: Bitcoin)", value="Bitcoin")
    
    # Menu traduzido corretamente
    mapa_periodos = {"1 Mês": "1mo", "3 Meses": "3mo", "6 Meses": "6mo", "1 Ano": "1y", "Máximo": "max"}
    periodo_visual = st.selectbox("Período", list(mapa_periodos.keys()))
    
    botao = st.button("ANALISAR AGORA 🚀")
    
    if st.button("Sair"):
        st.session_state["senha_correta"] = False
        st.rerun()

st.title("🦅 Sentinela AI - Terminal Inteligente")
st.markdown("---")

if botao:
    with st.spinner("Conectando aos satélites..."):
        try:
            codigo_periodo = mapa_periodos[periodo_visual]
            acao = yf.Ticker(ticker)
            hist = acao.history(period=codigo_periodo)
            
            if len(hist) > 0:
                # Dados Básicos
                preco = hist['Close'].iloc[-1]
                # Verifica se tem histórico suficiente para variação
                var = 0.0
                if len(hist) > 1:
                    var = ((preco - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                
                moeda = acao.info.get('currency', 'USD')
                simbolo = "R$" if moeda == "BRL" else "$"

                # IA + Notícias
                gnews = GoogleNews(lang='pt', region='BR')
                gnews.search(termo)
                news = gnews.result()
                
                analise = analisar_com_gemini(termo, news)
                
                # Leitura da resposta da IA
                score, resumo, recomendacao = 50, "Sem dados.", "NEUTRO"
                if "SCORE:" in analise:
                    for l in analise.split('\n'):
                        if "SCORE:" in l: 
                            try: score = int(l.split(':')[1].strip())
                            except: pass
                        if "RESUMO:" in l: resumo = l.split(':')[1].strip()
                        if "ACAO:" in l: recomendacao = l.split(':')[1].strip()

                # Exibição
                c1, c2, c3 = st.columns(3)
                c1.metric("Preço", f"{simbolo} {preco:,.2f}")
                c1.metric("Variação", f"{var:.2f}%", delta_color="normal")
                c2.metric("Sentimento IA", f"{score}/100", recomendacao)
                
                st.plotly_chart(criar_velocimetro(score), use_container_width=True)
                st.info(f"🧠 *IA Responde:* {resumo}")
                
                st.subheader("Gráfico de Preços")
                st.line_chart(hist['Close'])
            else:
                st.error("Ativo não encontrado!")
        except Exception as e:
            st.error(f"Erro: {e}")