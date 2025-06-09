# OCR com Nota Fiscal

Este é um sistema de automação criado inicialmente em ambiente profissional e adaptado para ser publicado no GitHub **sem expor informações sensíveis ou privadas**. 

> ⚠️ Para uso real, é necessário **ajustar o `mapa_estab`** no arquivo `constantes.py` e **configurar a URL da API** em `api.py`.


## 🧠 Funcionalidade

Este projeto realiza OCR (Reconhecimento Óptico de Caracteres) para **extrair dados de Notas Fiscais em PDF com imagem** (scaneadas) de fornecedores específicos.

Por meio de uma **interface gráfica**, o sistema permite:

- Selecionar um ou vários arquivos PDF (modo individual ou em lote);
- Extrair e converter automaticamente as informações em formato JSON;
- **Enviar automaticamente os dados para uma API** REST (sem precisar de chamadas externas manuais).

## 🔁 Ambientes: Teste x Produção

A definição se o servidor da API é **produção** ou **teste** é feita no arquivo `api.py`.

> Isso previne erros operacionais ao deixar clara a separação entre os ambientes

## 📁 Estrutura do Projeto

```
Meu_RPA/
├── rpa/
│   ├── main.py           # Interface gráfica principal
│   ├── ocr.py            # Extração e processamento OCR
│   ├── utils.py          # Funções auxiliares (CNPJ, base64, etc.)
│   ├── api.py            # Envio para API externa
│   ├── constantes.py     # Mapas e configurações
│   └── __init__.py
│
├── .venv/                # Ambiente virtual (ignorado)
├── logs/                 # Logs gerados na execução
├── NF JSON TESTE/        # JSONs de testes
├── NF JSON/              # JSONs reais (simulados)
├── Nota Fiscal/          # PDFs de entrada
├── poppler-24.08.0/      # Binários para OCR (Windows)
├── iniciar_meu_rpa.bat   # Script auxiliar (opcional)
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Como rodar

1. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate

2. Instale as dependências:
    pip install -r requirements.txt

3. Rode o Sistema
    python -m rpa.main

## 🛠 Requisitos

- Python 3.10+
- [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) (já incluído no projeto, mas você pode atualizar)
- Tesseract OCR instalado e configurado no `constantes.py` (`pytesseract_cmd`)

---

## 🔐 Observações de Segurança

- Este projeto **não inclui dados reais** nem endpoints de APIs privadas.
- Toda lógica sensível foi **removida ou simulada** para fins de demonstração pública.

---

## ✍️ Autor

Desenvolvido por Bruno Eduardo Luy – *versão pública adaptada de automação real em ambiente corporativo*.

