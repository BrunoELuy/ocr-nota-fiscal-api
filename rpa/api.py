import json
import time
import requests
from rpa.utils import salvar_log

url = "http:www.api.com/teste" # Base teste
#url = "http:www.api.com/oficial" # Base oficial

def enviar_para_api(json_data, max_tentativas=3, timeout=30):
    global url
    
    headers = {"Content-Type": "application/json"}
    
    obrigatorios = ["cnpjFornecedor", "nrNotaFiscal", "dtEmissao", "valorNf"]
    faltando = [campo for campo in obrigatorios if not json_data.get(campo)]
    
    if faltando:
        return 400, f"Campos obrigatórios faltando: {', '.join(faltando)}"
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            response = requests.post(url, json=json_data, headers=headers, timeout=timeout)
            salvar_log(response.status_code, json.dumps(json_data, ensure_ascii=False), response.text)

            if response.status_code == 200:
                return response.status_code, response.text
            elif response.status_code >= 500:
                time.sleep(2 * tentativa)
            else:
                return response.status_code, response.text

        except requests.exceptions.Timeout:
            if tentativa < max_tentativas:
                time.sleep(2 * tentativa)
                continue
            return 408, "Timeout na conexão com a API"
        
        except requests.exceptions.ConnectionError:
            if tentativa < max_tentativas:
                time.sleep(2 * tentativa)
                continue
            return 503, "Erro de conexão com a API"
        
        except Exception as e:
            return 500, f"Erro inesperado: {str(e)}"

    return 500, "Todas as tentativas falharam"