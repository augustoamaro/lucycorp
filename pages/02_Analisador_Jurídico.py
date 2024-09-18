import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# Função para extrair texto de um PDF


def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Função para fazer uma pergunta à API do ChatGPT


def ask_chatgpt(question, context):
    api_key = st.secrets["openai"]["openai_key"]
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
            Você é um assistente com nome de AnalytiLaw especializado em analisar documentos em formato .PDF.  Siga as diretrizes abaixo para responder as perguntas do usuário:
            1.  Analise todos os arquivos enviados em .PDF, somente os arquivos enviados de extensão .PDF;
            2. Nunca consulte a internet;
            3. Nunca invente nada, apenas responda de acordo com o Documento .PDF enviado.
            4. Quando o usuário solicitar um resumo, faça um resumo de todos os documentos enviados, não esqueça de nenhum. Este resumo deve ter uma media de 1500 palavras.
             """},
            {"role": "user", "content": f"Context: {context}\n\nPergunta: {question}"}
        ],
        temperature=0.7
    )

    if response and response.choices:
        return response.choices[0].message.content
    else:
        return "Nenhuma resposta válida foi retornada pela API."

# Interface do Streamlit


def main():
    st.title("Assistente Jurídico")

    # Upload de PDFs
    uploaded_files = st.file_uploader(
        "Upload de PDFs", type=["pdf"], accept_multiple_files=True)

    context = ""
    if uploaded_files:
        for uploaded_file in uploaded_files:
            text = extract_text_from_pdf(uploaded_file)
            context += text

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibir mensagens
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.write(f"**Usuário:** {message['content']}")
        else:
            st.write(f"**Assistente:** {message['content']}")

    # Campo de entrada de mensagem
    user_input = st.text_input("Digite sua pergunta:")

    if st.button("Enviar"):
        if user_input:
            st.session_state.messages.append(
                {"role": "user", "content": user_input})
            with st.spinner("O assistente está pensando..."):
                response = ask_chatgpt(user_input, context)
            st.session_state.messages.append(
                {"role": "assistant", "content": response})
            st.rerun()

    if st.button("Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()
