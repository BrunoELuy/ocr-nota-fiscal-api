import os
import base64
import re
import Levenshtein
from datetime import datetime
from rpa.constantes import mapa_estab

def gerar_base64_pdf(path_pdf):
    try:
        with open(path_pdf, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())
            return encoded_string.decode('utf-8')
    except Exception as e:
        print(f"Erro ao gerar Base64 do PDF: {str(e)}")
        return ""

def obter_cod_estab(cnpj_comprador):
    return mapa_estab.get(cnpj_comprador, "999")

def corrigir_cnpj_ocr(cnpj_raw):
    """Corrige erros comuns de OCR em CNPJs"""
    return (
        cnpj_raw.upper()
        .replace("O", "0")
        .replace("o", "0")
        .replace("I", "1")
        .replace("l", "1")
        .replace(" ", "")
        .replace("-", "")
        .replace(".", "")
        .replace("/", "")
    )

def encontrar_cnpj_tomador(texto):
    # Busca todos os padrões com possível CNPJ, mesmo bagunçados
    cnpjs_raw = re.findall(r'[\dIlOo./ -]{14,22}', texto)
    cnpjs_corrigidos = [corrigir_cnpj_ocr(c) for c in cnpjs_raw]

    # 1. Tentativa direta
    for cnpj in cnpjs_corrigidos:
        if cnpj in mapa_estab:
            print(f"[MATCH DIRETO] {cnpj}")
            return cnpj

    # 2. Fuzzy Levenshtein
    candidatos = list(mapa_estab.keys())
    melhor_candidato = None
    menor_distancia = float("inf")

    for cnpj_ocr in cnpjs_corrigidos:
        for candidato in candidatos:
            dist = Levenshtein.distance(cnpj_ocr, candidato)
            if dist < menor_distancia:
                menor_distancia = dist
                melhor_candidato = candidato
                cnpj_comparado = cnpj_ocr  # Salva o que estava sendo comparado

    if melhor_candidato and menor_distancia <= 3:
        print(f"[LEV MATCH] {cnpj_comparado} → {melhor_candidato} | distância = {menor_distancia}")
        return melhor_candidato

    print("[FALHA] Nenhum CNPJ tomador encontrado via Levenshtein")
    return ""

def salvar_log(status, request_data, response_data):
    os.makedirs("logs", exist_ok=True)
    with open("logs/api_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n{datetime.now()} - Status: {status}\n")
        log.write(f"Request: {request_data}\n")
        log.write(f"Response: {response_data}\n")
