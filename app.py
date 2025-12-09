[03:19, 09/12/2025] Roberta Alves: import streamlit as st
import yfinance as yf
from GoogleNews import GoogleNews
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sentinela AI - Gemini", page_icon="🧠", layout="wide")

# Estilo Visual
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    div.stButton > button:first-child { background-color: #2962FF; color: white; border-radius: 8px; border: none; padding: 10px 24px; }
    div.stButton > button:first-child:hover { background-color: #0039CB; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
</style>
""", unsafe_allow_html=True)

# --…
[03:20, 09/12/2025] Roberta Alves: import streamlit as st
import yfinance as yf
from GoogleNews import GoogleNews
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Sentinela AI - Gemini", page_icon="🧠", layout="wide")

# Estilo Visual
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    div.stButton > button:first-child { background-color: #2962FF; color: white; border-radius: 8px; border: none; padding: 10px 24px; }
    div.stButton > button:first-child:hover { background-color: #0039CB; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
def verificar_senha():
    if "senha_correta" not in st.session_state: st.session_state["senha_correta"] = False
    def senha_digitada():
        st.session_state["senha_correta"] = st.session_state["input_senha"] == "trader123"
    if not st.session_state["senha_correta"]:
        st.markdown("## 🔒 Acesso Restrito - IA Gemini")
        st.text_input("Credencial de Acesso:", type="password", key="input_senha", on_change=senha_digitada)
        return False
    return True

if not verificar_senha(): st.stop()

# --- INTELIGÊNCIA ARTIFICIAL (GEMINI) ---
def analisar_com_gemini(termo, noticias):
    try:
        # Tenta pegar a chave do cofre (Secrets)
        if "GEMINI_KEY" in st.secrets:
            chave = st.secrets["GEMINI_KEY"]
        else:
            return "ERRO: Chave GEMINI_KEY não encontrada no cofre!"
            
        genai.configure(api_key=chave)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        texto_noticias = ""
        for n in noticias[:5]:
            texto_noticias += f"- {n['title']}\n"
            
        prompt = f"""
        Você é um analista financeiro sênior experiente. 
        Analise as seguintes manchetes recentes sobre '{termo}':
        {texto_noticias}
        
        Sua missão:
        1. Determine o sentimento geral (0 = Pânico Total, 100 = Euforia Total).
        2. Resuma em UMA frase curta o motivo.
        3. Dê uma recomendação (COMPRA, VENDA ou CAUTELA).
        
        Responda estritamente neste formato:
        SCORE: [número]
        RESUMO: [frase]
        ACAO: [palavra]
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

# --- FUNÇÕES TÉCNICAS ---
def criar_velocimetro(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "SENTIMENTO IA (GEMINI)", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 25], 'color': '#ff4d4d'},
                {'range': [25, 50], 'color': '#ffa64d'},
                {'range': [50, 75], 'color': '#ffff4d'},
                {'range': [75, 100], 'color': '#00cc66'}],
        }))
    return fig

# --- INTERFACE ---
with st.sidebar:
    st.header("🧠 Cérebro Google")
    with st.form(key='painel_ia'):
        ticker = st.text_input("Ativo (Ex: BTC-USD)", value="BTC-USD")
        termo = st.text_input("Tema (Ex: Bitcoin)", value="Bitcoin")
        periodo = st.selectbox("Histórico", ["1mo", "6mo", "1y"])
        botao = st.form_submit_button("ANÁLISE COM IA 🚀")

st.title("🦅 Sentinela AI - Powered by Gemini")
st.markdown("---")

if botao:
    with st.spinner("O Gemini está lendo as notícias do mercado..."):
        try:
            # 1. DADOS DE PREÇO
            acao = yf.Ticker(ticker)
            hist = acao.history(period=periodo)
            
            if len(hist) > 0:
                preco = hist['Close'].iloc[-1]
                var = ((preco - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                moeda = acao.info.get('currency', 'USD')
                simbolo = "R$" if moeda == "BRL" else "$"

                # 2. BUSCA NOTÍCIAS
                gnews = GoogleNews(lang='pt', region='BR')
                gnews.search(termo)
                news = gnews.result()

                # 3. CHAMA O CÉREBRO (GEMINI)
                analise_ia = analisar_com_gemini(termo, news)
                
                score_final = 50
                resumo_ia = "Análise indisponível."
                acao_ia = "NEUTRO"
                
                if "SCORE:" in analise_ia:
                    linhas = analise_ia.split('\n')
                    for l in linhas:
                        if "SCORE:" in l: score_final = int(l.split(':')[1].strip())
                        if "RESUMO:" in l: resumo_ia = l.split(':')[1].strip()
                        if "ACAO:" in l: acao_ia = l.split(':')[1].strip()

                # --- EXIBIÇÃO ---
                c1, c2, c3 = st.columns(3)
                c1.metric("Preço", f"{simbolo} {preco:,.2f}")
                c1.metric("Variação", f"{var:.2f}%", delta_color="normal")
                c2.metric("Recomendação IA", acao_ia)
                c3.metric("Score de Sentimento", f"{score_final}/100")
                
                st.plotly_chart(criar_velocimetro(score_final), use_container_width=True)
                st.info(f"🤖 *Análise do Gemini:* {resumo_ia}")
                st.line_chart(hist['Close'])
                
            else:
                st.error("Ativo não encontrado.")
                
        except Exception as e:
            st.error(f"Erro: {e}")