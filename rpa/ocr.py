import pytesseract
from pdf2image import convert_from_path
import re
from datetime import datetime, timedelta
import os
import json
from PIL import Image, ImageEnhance, ImageFilter
from rpa.constantes import pytesseract_cmd
from rpa.utils import gerar_base64_pdf, obter_cod_estab, encontrar_cnpj_tomador
from rpa.api import enviar_para_api
from tkinter import messagebox

pytesseract.pytesseract.tesseract_cmd = pytesseract_cmd

def preprocess_image(img):
    # Pré processamento de imagem para melhorar os acertos do OCR
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    img = img.point(lambda x: 0 if x < 180 else 255)
    img = img.resize((img.width * 2, img.height * 2))
    return img

def extrair_info(texto, path_pdf, qtde_paginas):
    texto = re.sub(r'\s+', ' ', texto)

    cnpj_fornecedor = re.search(r'\bC?F?P?\/?C?N?P?J?[:\s-]*([\d./-]{18})', texto, re.IGNORECASE)

    contrato = re.search(r'Contrato\s+([A-Za-z0-9]+)', texto)
    numero_nf = re.search(r'RPS Nº\s*(\d+)', texto)
    data_emissao = re.search(r'Data da Compra:\s*(\d{2}/\d{2}/\d{4})', texto)
    valor_total = re.search(r'VALOR TOTAL DO SERVIÇO\s*=\s*R\$\s*([\d,.]+)', texto)

    # Encontra e valida o CNPJ tomador
    cnpj_tomador_raw = encontrar_cnpj_tomador(texto)
    print("CNPJ Tomador encontrado:", cnpj_tomador_raw)
    cnpj_tomador_num = cnpj_tomador_raw.replace(".", "").replace("/", "").replace("-", "")

    file_base64 = gerar_base64_pdf(path_pdf)

    dt_vencimento = ""
    if data_emissao:
        try:
            emissao_obj = datetime.strptime(data_emissao.group(1), "%d/%m/%Y")
            venc_obj = emissao_obj + timedelta(days=30)
            dt_vencimento = venc_obj.strftime("%d/%m/%Y")
        except:
            dt_vencimento = ""

    valor_nf = 0.0
    if valor_total:
        valor_str = valor_total.group(1).replace(".", "").replace(",", ".")
        try:
            valor_nf = float(valor_str)
        except:
            valor_nf = 0.0

    quantidade = valor_nf / 100.0 if valor_nf > 0 else 0.0

    return {
        "cnpjFornecedor": (cnpj_fornecedor.group(1).replace(".", "").replace("/", "").replace("-", "") if cnpj_fornecedor else ""),
        "nrContrato": "434",
        "codEstab": obter_cod_estab(cnpj_tomador_num),
        "codCentroCusto": "0",
        "codContaContabil": "0",
        "tipoDespesa": "0",
        "nrNotaFiscal": str(numero_nf.group(1) if numero_nf else ""),
        "dtEmissao": str(data_emissao.group(1) if data_emissao else ""),
        "dtVencimento": dt_vencimento,
        "qtdeTotalNf": f"{quantidade:.4f}",
        "valorNf": f"{valor_nf:.2f}",
        "descricao": "Compra de benefícios - Auxilio Alimentação e Refeição",
        "lstProdServ": [
            {
                "nomeProdServ": "Auxilio Alimentação e Refeição",
                "valorProdServ": "100.00",
                "vlTotalProdServ": f"{valor_nf:.2f}",
                "qtdeProdServ": f"{quantidade:.4f}",
                "sequencia": 1.00
            }
        ],
        "nrCOF0080Aprovado": "-",
        "fileHashNF": file_base64
    }

def ler_nf_com_ocr(path_pdf, output_json):
    imagens = convert_from_path(path_pdf)
    texto = ""
    for img in imagens:
        img_proc = preprocess_image(img)
        texto += pytesseract.image_to_string(img_proc, lang="por", config="--psm 6") + "\n"

    nome_base = os.path.basename(path_pdf).replace(".pdf", "")
    with open(f"logs/ocr_texto_{nome_base}.txt", "w", encoding="utf-8") as f:
        f.write(texto)

    dados_nf = extrair_info(texto, path_pdf, len(imagens))

    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(dados_nf, f, indent=4, ensure_ascii=False)

    status, resposta = enviar_para_api(dados_nf)

    if status == 200:
        messagebox.showinfo("Sucesso", f"Enviado com sucesso!\nJSON salvo em: {output_json}")
    else:
        messagebox.showwarning("Erro", f"Erro ({status}): {resposta}\nJSON salvo em: {output_json}")
