import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from PIL import Image, ImageTk
import sys
from pathlib import Path
from rpa.ocr import ler_nf_com_ocr 
import rpa.api as api

def verificar_ambiente():
    """Verifica se está rodando em ambiente de teste ou produção"""
    try:
        # Pega a URL diretamente da variável no módulo api
        url_atual = api.url if hasattr(api, 'url') else None
        
        if url_atual:
            if "teste" in url_atual:
                return "TESTE"
            elif "oficial" in url_atual:
                return "OFICIAL"
        
        return "DESCONHECIDO"
    except Exception as e:
        print(f"Erro ao verificar ambiente: {e}")
        return "DESCONHECIDO"

class ModernApp:
    def __init__(self, root):
        # Verifica o ambiente antes de configurar a interface
        self.ambiente = verificar_ambiente()
        
        # Configurações principais
        self.root = root
        self.root.title("Conversor PDF → JSON")
        if self.ambiente == "TESTE":
            self.root.geometry("951x727")
            self.root.minsize(951, 727)
        else:
            self.root.geometry("780x600")
            self.root.minsize(780, 600)
        
        # Cores baseadas no ambiente
        if self.ambiente == "TESTE":
            self.cores = {
                "primaria": "#f39c12",       
                "secundaria": "#e67e22",     
                "fundo": "#fff3cd",           
                "texto": "#856404",           
                "texto_claro": "#ffffff",     
                "aviso": "#e74c3c",          
                "destaque": "#d68910",        
                "alerta": "#f1c40f"           
            }
            # Título diferenciado para teste
            self.titulo_app = "Conversor PDF → JSON [AMBIENTE DE TESTE]"
        else:
            self.cores = {
                "primaria": "#3498db",   
                "secundaria": "#2ecc71",      
                "fundo": "#f9f9f9",        
                "texto": "#2c3e50",         
                "texto_claro": "#ecf0f1",     
                "aviso": "#e74c3c",          
                "destaque": "#1abc9c"         
            }
            self.titulo_app = "Conversor de Notas Fiscais"
        
        # Atualiza título da janela
        self.root.title(self.titulo_app)
        
        # Configura cor de fundo da janela principal para ambiente de teste
        if self.ambiente == "TESTE":
            self.root.configure(bg=self.cores["fundo"])
        
        # Fontes
        self.fonte = {
            "titulo": ("Segoe UI", 16, "bold"),
            "subtitulo": ("Segoe UI", 12, "bold"),
            "normal": ("Segoe UI", 10),
            "pequena": ("Segoe UI", 9),
            "alerta": ("Segoe UI", 11, "bold")
        }
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Layout principal
        self.criar_menu()
        self.criar_header()
        self.criar_tabs()
        self.criar_footer()
        
        # Status de processamento
        self.processando = False
        
        # Centralizar a janela na tela
        self.centralizar_janela()
    
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        
    def configurar_estilo(self):
        """Configura o estilo dos widgets ttk"""
        self.style = ttk.Style()
        
        # Tema principal
        self.style.theme_use('clam')
        
        # Abas
        self.style.configure(
            "TNotebook", 
            background=self.cores["fundo"],
            borderwidth=0
        )
        self.style.configure(
            "TNotebook.Tab", 
            background=self.cores["fundo"],
            foreground=self.cores["texto"],
            padding=[15, 5],
            font=self.fonte["normal"]
        )
        self.style.map(
            "TNotebook.Tab", 
            background=[("selected", self.cores["primaria"])],
            foreground=[("selected", self.cores["texto_claro"])]
        )
        
        # Frames
        self.style.configure(
            "TFrame", 
            background=self.cores["fundo"]
        )
        
        # Botões
        self.style.configure(
            "TButton", 
            font=self.fonte["normal"],
            background=self.cores["primaria"],
            foreground=self.cores["texto_claro"],
            borderwidth=0,
            focusthickness=3,
            focuscolor=self.cores["primaria"]
        )
        self.style.map(
            "TButton",
            background=[("active", self.cores["destaque"])],
            relief=[("pressed", "flat")]
        )
        
        # Botão de ação principal
        self.style.configure(
            "Acao.TButton", 
            font=self.fonte["subtitulo"],
            background=self.cores["secundaria"],
            foreground=self.cores["texto_claro"]
        )
        self.style.map(
            "Acao.TButton",
            background=[("active", self.cores["destaque"])]
        )
        
        # Barras de progresso
        self.style.configure(
            "TProgressbar", 
            troughcolor=self.cores["fundo"],
            background=self.cores["secundaria"],
            borderwidth=0,
            thickness=10
        )
        
    def criar_menu(self):
        """Cria a barra de menu"""
        menu_bar = tk.Menu(self.root)
        
        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        arquivo_menu.add_command(label="Sair", command=self.root.destroy)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
        
        # Menu ambiente (apenas para teste)
        if self.ambiente == "TESTE":
            ambiente_menu = tk.Menu(menu_bar, tearoff=0)
            ambiente_menu.add_command(label="Informações do Ambiente", command=self.mostrar_ambiente)
            menu_bar.add_cascade(label="🔧 Ambiente", menu=ambiente_menu)
        
        ajuda_menu = tk.Menu(menu_bar, tearoff=0)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)
        
        self.root.config(menu=menu_bar)
    
    def criar_header(self):
        """Cria o cabeçalho da aplicação"""
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=20, pady=15)
        
        # Alerta de ambiente de teste
        if self.ambiente == "TESTE":
            alerta_frame = tk.Frame(header, bg=self.cores["alerta"], relief="solid", bd=2)
            alerta_frame.pack(fill="x", pady=(0, 10))
            
            alerta_icon = tk.Label(
                alerta_frame,
                text="⚠️",
                font=("Segoe UI", 16),
                bg=self.cores["alerta"],
                fg="#000000"
            )
            alerta_icon.pack(side="left", padx=10, pady=5)
            
            alerta_texto = tk.Label(
                alerta_frame,
                text="AMBIENTE DE TESTE ATIVO - Os dados serão enviados para o servidor de teste",
                font=self.fonte["alerta"],
                bg=self.cores["alerta"],
                fg="#000000"
            )
            alerta_texto.pack(side="left", padx=(0, 10), pady=5)
        
        # Logo e título
        titulo_frame = ttk.Frame(header)
        titulo_frame.pack(fill="x")
        
        # Ícone baseado no ambiente
        if self.ambiente == "TESTE":
            icone_texto = "🧪"
            cor_titulo = self.cores["texto"]
        else:
            icone_texto = "📄"
            cor_titulo = self.cores["primaria"]
        
        # Ícone do aplicativo
        icone = tk.Label(
            titulo_frame,
            text=icone_texto,
            font=("Segoe UI", 20),
            bg=self.cores["fundo"]
        )
        icone.pack(side="left", padx=(0, 10))
        
        # Título do aplicativo
        titulo = tk.Label(
            titulo_frame, 
            text=self.titulo_app,
            font=self.fonte["titulo"],
            fg=cor_titulo,
            bg=self.cores["fundo"]
        )
        titulo.pack(side="left")
        
        # Subtítulo
        subtitulo_texto = "PDF → JSON com OCR"
        if self.ambiente == "TESTE":
            subtitulo_texto += " | Modo Desenvolvimento"
            
        subtitulo = tk.Label(
            titulo_frame, 
            text=subtitulo_texto,
            font=self.fonte["subtitulo"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"]
        )
        subtitulo.pack(side="left", padx=(10, 0))
    
    def criar_tabs(self):
        """Cria as abas da aplicação"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Aba Individual
        self.aba_individual = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_individual, text="Arquivo Individual")
        self.criar_conteudo_individual()
        
        # Aba de Processamento em Lote
        self.aba_lote = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_lote, text="Processamento em Lote")
        self.criar_conteudo_lote()
    
    def criar_conteudo_individual(self):
        """Cria o conteúdo da aba individual"""
        # Container principal
        frame = ttk.Frame(self.aba_individual)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Seção de instruções
        instrucoes = tk.Label(
            frame,
            text="Selecione um arquivo PDF para converter para JSON",
            font=self.fonte["subtitulo"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"],
            anchor="w"
        )
        instrucoes.pack(fill="x", pady=(0, 15))
        
        # Frame para arquivo PDF
        pdf_frame = ttk.Frame(frame)
        pdf_frame.pack(fill="x", pady=10)
        
        pdf_label = tk.Label(
            pdf_frame,
            text="Arquivo PDF:",
            font=self.fonte["normal"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"],
            anchor="w"
        )
        pdf_label.pack(fill="x")
        
        selecao_frame = ttk.Frame(pdf_frame)
        selecao_frame.pack(fill="x", pady=5)
        
        self.entry_pdf = ttk.Entry(selecao_frame, font=self.fonte["normal"])
        self.entry_pdf.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        btn_pdf = ttk.Button(
            selecao_frame,
            text="Procurar",
            command=self.escolher_pdf
        )
        btn_pdf.pack(side="right")
        
        # Frame para pasta de saída
        output_frame = ttk.Frame(frame)
        output_frame.pack(fill="x", pady=10)
        
        output_label = tk.Label(
            output_frame,
            text="Pasta de saída:",
            font=self.fonte["normal"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"],
            anchor="w"
        )
        output_label.pack(fill="x")
        
        selecao_output_frame = ttk.Frame(output_frame)
        selecao_output_frame.pack(fill="x", pady=5)
        
        self.entry_saida = ttk.Entry(selecao_output_frame, font=self.fonte["normal"])
        self.entry_saida.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        btn_saida = ttk.Button(
            selecao_output_frame,
            text="Procurar",
            command=lambda: self.escolher_diretorio(self.entry_saida)
        )
        btn_saida.pack(side="right")
        
        # Separador
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=20)
        
        # Barra de progresso e status
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill="x", pady=10)
        
        self.status_individual = tk.Label(
            status_frame,
            text="Pronto para processar",
            font=self.fonte["normal"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"]
        )
        self.status_individual.pack(side="left")
        
        # Barra de progresso
        self.progress_individual = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=100,
            mode="determinate"
        )
        self.progress_individual.pack(fill="x", pady=5)
        
        # Botão de execução
        texto_botao = "Converter PDF"
        if self.ambiente == "TESTE":
            texto_botao += " (TESTE)"
            
        btn_executar = ttk.Button(
            frame,
            text=texto_botao,
            style="Acao.TButton",
            command=self.executar_individual
        )
        btn_executar.pack(pady=15)
    
    def criar_conteudo_lote(self):
        """Cria o conteúdo da aba de lote"""
        # Container principal
        frame = ttk.Frame(self.aba_lote)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Seção de instruções
        instrucoes = tk.Label(
            frame,
            text="Selecione uma pasta com arquivos PDF para conversão em lote",
            font=self.fonte["subtitulo"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"],
            anchor="w"
        )
        instrucoes.pack(fill="x", pady=(0, 15))
        
        # Frame para pasta de entrada
        entrada_frame = ttk.Frame(frame)
        entrada_frame.pack(fill="x", pady=10)
        
        entrada_label = tk.Label(
            entrada_frame,
            text="Pasta com PDFs:",
            font=self.fonte["normal"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"],
            anchor="w"
        )
        entrada_label.pack(fill="x")
        
        selecao_entrada_frame = ttk.Frame(entrada_frame)
        selecao_entrada_frame.pack(fill="x", pady=5)
        
        self.entry_lote_entrada = ttk.Entry(selecao_entrada_frame, font=self.fonte["normal"])
        self.entry_lote_entrada.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        btn_entrada = ttk.Button(
            selecao_entrada_frame,
            text="Procurar",
            command=lambda: self.escolher_diretorio(self.entry_lote_entrada)
        )
        btn_entrada.pack(side="right")
        
        # Frame para pasta de saída
        saida_frame = ttk.Frame(frame)
        saida_frame.pack(fill="x", pady=10)
        
        saida_label = tk.Label(
            saida_frame,
            text="Pasta para salvar JSONs:",
            font=self.fonte["normal"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"],
            anchor="w"
        )
        saida_label.pack(fill="x")
        
        selecao_saida_frame = ttk.Frame(saida_frame)
        selecao_saida_frame.pack(fill="x", pady=5)
        
        self.entry_lote_saida = ttk.Entry(selecao_saida_frame, font=self.fonte["normal"])
        self.entry_lote_saida.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        btn_saida_lote = ttk.Button(
            selecao_saida_frame,
            text="Procurar",
            command=lambda: self.escolher_diretorio(self.entry_lote_saida)
        )
        btn_saida_lote.pack(side="right")
        
        # Separador
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=20)
        
        # Barra de progresso e status
        self.contagem_arquivos = tk.Label(
            frame,
            text="Nenhum arquivo selecionado",
            font=self.fonte["normal"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"]
        )
        self.contagem_arquivos.pack(fill="x", pady=5)
        
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill="x", pady=5)
        
        self.status_lote = tk.Label(
            status_frame,
            text="Pronto para processar",
            font=self.fonte["normal"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"]
        )
        self.status_lote.pack(side="left")
        
        self.contador_lote = tk.Label(
            status_frame,
            text="",
            font=self.fonte["normal"],
            fg=self.cores["secundaria"],
            bg=self.cores["fundo"]
        )
        self.contador_lote.pack(side="right")
        
        # Barra de progresso
        self.progress_lote = ttk.Progressbar(
            frame,
            orient="horizontal",
            length=100,
            mode="determinate"
        )
        self.progress_lote.pack(fill="x", pady=5)
        
        # Botão de execução
        texto_botao_lote = "Processar Todos os PDFs"
        if self.ambiente == "TESTE":
            texto_botao_lote += " (TESTE)"
            
        btn_executar_lote = ttk.Button(
            frame,
            text=texto_botao_lote,
            style="Acao.TButton",
            command=self.executar_lote
        )
        btn_executar_lote.pack(pady=15)
        
    def criar_footer(self):
        """Cria o rodapé da aplicação"""
        footer = ttk.Frame(self.root)
        footer.pack(fill="x", padx=20, pady=10)
        
        # Informação do ambiente
        if self.ambiente == "TESTE":
            ambiente_info = tk.Label(
                footer,
                text=f"🧪 AMBIENTE: {self.ambiente}",
                font=self.fonte["pequena"],
                fg=self.cores["texto"],
                bg=self.cores["fundo"]
            )
            ambiente_info.pack(side="left")
        
        # Versão e informações
        info = tk.Label(
            footer,
            text="v1.0 | Desenvolvido por Sua Empresa © 2025",
            font=self.fonte["pequena"],
            fg=self.cores["texto"],
            bg=self.cores["fundo"]
        )
        info.pack(side="right")
    
    # --- Funções de ação ---
    def escolher_pdf(self):
        """Abre diálogo para escolher arquivo PDF"""
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")])
        if caminho:
            self.entry_pdf.delete(0, tk.END)
            self.entry_pdf.insert(0, caminho)
    
    def escolher_diretorio(self, entry):
        """Abre diálogo para escolher diretório e define no entry"""
        caminho = filedialog.askdirectory()
        if caminho:
            entry.delete(0, tk.END)
            entry.insert(0, caminho)
            
            # Se for o diretório de entrada do lote, conta os PDFs
            if entry == self.entry_lote_entrada:
                self.contar_pdfs()
    
    def contar_pdfs(self):
        """Conta quantos PDFs existem na pasta selecionada"""
        pasta = self.entry_lote_entrada.get()
        if pasta and os.path.isdir(pasta):
            arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]
            if arquivos:
                self.contagem_arquivos.config(
                    text=f"Encontrados {len(arquivos)} arquivos PDF na pasta"
                )
            else:
                self.contagem_arquivos.config(
                    text="Nenhum arquivo PDF encontrado na pasta"
                )
    
    def executar_individual(self):
        """Processa um arquivo individual"""
        if self.processando:
            messagebox.showinfo("Processando", "Aguarde o término do processamento atual.")
            return
        
        caminho_pdf = self.entry_pdf.get()
        pasta_saida = self.entry_saida.get()
        
        if not caminho_pdf or not pasta_saida:
            messagebox.showwarning("Campos obrigatórios", "Selecione o arquivo PDF e a pasta de saída.")
            return
        
        if not os.path.isfile(caminho_pdf):
            messagebox.showwarning("Arquivo não encontrado", "O arquivo PDF selecionado não existe.")
            return
            
        if not os.path.isdir(pasta_saida):
            messagebox.showwarning("Pasta inválida", "A pasta de saída selecionada não existe.")
            return
        
        # Alerta adicional para ambiente de teste
        if self.ambiente == "TESTE":
            resposta = messagebox.askyesno(
                "Confirmar Processamento - AMBIENTE DE TESTE",
                "⚠️ ATENÇÃO: Você está no ambiente de TESTE!\n\n"
                "Os dados serão enviados para o servidor de desenvolvimento.\n"
                "Deseja continuar com o processamento?"
            )
            if not resposta:
                return
        
        # Prepara o processamento
        self.processando = True
        self.status_individual.config(text="Processando...")
        self.progress_individual["value"] = 0
        
        # Executa em thread separada
        threading.Thread(target=self._processar_individual, args=(caminho_pdf, pasta_saida)).start()
    
    def _processar_individual(self, caminho_pdf, pasta_saida):
        """Executa o processamento individual em thread separada"""
        try:
            # Atualiza progresso
            self.root.after(100, lambda: self.progress_individual.config(value=30))
            
            # Nome do arquivo de saída
            nome_json = os.path.basename(caminho_pdf).replace(".pdf", ".json")
            output_json = os.path.join(pasta_saida, nome_json)
            
            # Executa a conversão
            ler_nf_com_ocr(caminho_pdf, output_json)
            
            # Finaliza com sucesso
            self.root.after(100, lambda: self.progress_individual.config(value=100))
            self.root.after(100, lambda: self.status_individual.config(text="Concluído com sucesso!"))
            
            # Mensagem de sucesso personalizada por ambiente
            if self.ambiente == "TESTE":
                mensagem = f"✅ Arquivo convertido com sucesso (AMBIENTE DE TESTE):\n{nome_json}\n\n🧪 Os dados foram processados no servidor de desenvolvimento."
            else:
                mensagem = f"O arquivo foi convertido com sucesso:\n{nome_json}"
            
            # Mostra mensagem de sucesso
            self.root.after(200, lambda: messagebox.showinfo(
                "Conversão concluída", 
                mensagem
            ))
            
        except Exception as e:
            # Mostra erro
            self.root.after(100, lambda: self.status_individual.config(
                text="Erro no processamento"
            ))
            self.root.after(200, lambda: messagebox.showerror(
                "Erro na conversão", 
                f"Ocorreu um erro ao processar o arquivo:\n{str(e)}"
            ))
        
        finally:
            # Libera para novo processamento
            self.processando = False
    
    def executar_lote(self):
        """Processa arquivos em lote"""
        if self.processando:
            messagebox.showinfo("Processando", "Aguarde o término do processamento atual.")
            return
        
        entrada = self.entry_lote_entrada.get()
        saida = self.entry_lote_saida.get()
        
        if not entrada or not saida:
            messagebox.showwarning("Campos obrigatórios", "Selecione as pastas de entrada e saída.")
            return
            
        if not os.path.isdir(entrada):
            messagebox.showwarning("Pasta inválida", "A pasta de entrada selecionada não existe.")
            return
            
        if not os.path.isdir(saida):
            messagebox.showwarning("Pasta inválida", "A pasta de saída selecionada não existe.")
            return
        
        # Encontra os arquivos para processar
        arquivos = [f for f in os.listdir(entrada) if f.lower().endswith(".pdf")]
        if not arquivos:
            messagebox.showinfo("Sem arquivos", "Nenhum arquivo PDF encontrado na pasta de entrada.")
            return
        
        # Alerta adicional para ambiente de teste
        if self.ambiente == "TESTE":
            resposta = messagebox.askyesno(
                "Confirmar Processamento em Lote - AMBIENTE DE TESTE",
                f"⚠️ ATENÇÃO: Você está no ambiente de TESTE!\n\n"
                f"Serão processados {len(arquivos)} arquivos e enviados para o servidor de desenvolvimento.\n"
                f"Deseja continuar com o processamento em lote?"
            )
            if not resposta:
                return
        
        # Inicia o processamento
        self.processando = True
        self.progress_lote["value"] = 0
        self.status_lote.config(text=f"Processando em lote...")
        self.contador_lote.config(text=f"0/{len(arquivos)}")
        
        # Executa em thread separada
        threading.Thread(target=self._processar_lote, args=(entrada, saida, arquivos)).start()
    
    def _processar_lote(self, entrada, saida, arquivos):
        """Executa o processamento em lote em thread separada"""
        total = len(arquivos)
        sucesso = 0
        erros = []
        
        for idx, nome in enumerate(arquivos):
            try:
                # Atualiza status
                progresso = int(((idx + 0.5) / total) * 100)
                self.root.after(0, lambda p=progresso: self.progress_lote.config(value=p))
                self.root.after(0, lambda i=idx, t=total: self.contador_lote.config(text=f"{i}/{t}"))
                self.root.after(0, lambda n=nome: self.status_lote.config(text=f"Processando: {n}"))
                
                # Processa o arquivo
                caminho_pdf = os.path.join(entrada, nome)
                output_json = os.path.join(saida, nome.replace(".pdf", ".json"))
                ler_nf_com_ocr(caminho_pdf, output_json)
                
                # Incrementa contador de sucesso
                sucesso += 1
                
            except Exception as e:
                # Registra erro
                erros.append(f"{nome}: {str(e)}")
            
            # Atualiza status final do arquivo
            progresso = int(((idx + 1) / total) * 100)
            self.root.after(0, lambda p=progresso: self.progress_lote.config(value=p))
            self.root.after(0, lambda i=idx+1, t=total: self.contador_lote.config(text=f"{i}/{t}"))
        
        # Processamento finalizado
        self.root.after(0, lambda: self.status_lote.config(text="Processamento concluído"))
        
        # Mensagem de resultado personalizada por ambiente
        msg_base = f"{sucesso} de {total} arquivos processados com sucesso."
        if self.ambiente == "TESTE":
            msg_base = f"🧪 AMBIENTE DE TESTE: {msg_base}"
        
        # Exibe resultado
        if erros:
            erros_detalhe = "\n".join(erros[:5])
            if len(erros) > 5:
                erros_detalhe += f"\n... e mais {len(erros) - 5} arquivos com erro"
            
            self.root.after(200, lambda: messagebox.showwarning(
                "Processamento concluído com erros", 
                f"{msg_base}\n\nErros encontrados:\n{erros_detalhe}"
            ))
        else:
            self.root.after(200, lambda: messagebox.showinfo(
                "Processamento concluído", 
                msg_base
            ))
        
        # Libera para novo processamento
        self.processando = False
    
    def mostrar_ambiente(self):
        """Exibe informações sobre o ambiente atual"""
        if self.ambiente == "TESTE":
            messagebox.showinfo(
                "Informações do Ambiente",
                "🧪 AMBIENTE DE TESTE ATIVO\n\n"
                "• Servidor: www.api.com\n"
                "• Endpoint: /teste\n"
                "• Modo: Desenvolvimento/Teste\n\n"
                "⚠️ ATENÇÃO: Todos os dados processados serão enviados\n"
                "para o servidor de desenvolvimento, não para produção.\n\n"
                "Para usar o ambiente de produção, altere a configuração\n"
                "no arquivo api.py."
            )
        else:
            messagebox.showinfo(
                "Informações do Ambiente",
                "🏢 AMBIENTE DE PRODUÇÃO ATIVO\n\n"
                "• Servidor: www.api.com\n" 
                "• Endpoint: /oficial\n"
                "• Modo: Produção\n\n"
                "✅ Os dados processados serão enviados diretamente\n"
                "para o servidor de produção."
            )
    
    def mostrar_sobre(self):
        """Exibe informações sobre o aplicativo"""
        ambiente_info = ""
        if self.ambiente == "TESTE":
            ambiente_info = "\n\n🧪 Executando em AMBIENTE DE TESTE"
        elif self.ambiente == "OFICIAL":
            ambiente_info = "\n\n🏢 Executando em AMBIENTE DE PRODUÇÃO"
        
        messagebox.showinfo(
            "Sobre", 
            "Conversor de Notas Fiscais PDF → JSON\n"
            "Versão 1.0\n\n"
            "Este aplicativo converte notas fiscais em PDF para o formato JSON\n"
            "utilizando reconhecimento ótico de caracteres (OCR).\n\n"
            f"© 2025 - Todos os direitos reservados{ambiente_info}"
        )

# --- Inicialização do Aplicativo ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()