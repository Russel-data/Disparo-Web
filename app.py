import time
import customtkinter as ctk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from threading import Thread

# Dados de login (pode ser adaptado para um sistema mais seguro)
usuario_validado = "admin"
senha_validada = "admin123"

# Função para fazer login
def login_usuario():
    nome_usuario = usuario_entry.get()
    senha_usuario = senha_entry.get()
    
    if nome_usuario == usuario_validado and senha_usuario == senha_validada:
        # Se os dados estiverem corretos, iniciar o app
        root_login.destroy()
        iniciar_app()
    else:
        messagebox.showerror("Erro", "Nome de usuário ou senha incorretos. Tente novamente.")
    
# Função de login usando tkinter
def iniciar_login():
    global root_login, usuario_entry, senha_entry
    
    root_login = ctk.CTk()
    root_login.title("Login")
    root_login.geometry("400x300")
    
    ctk.CTkLabel(root_login, text="Login", font=("Arial", 20)).pack(pady=10)
    
    # Campo para nome de usuário
    usuario_frame = ctk.CTkFrame(root_login)
    usuario_frame.pack(pady=10, padx=10, fill="x")
    ctk.CTkLabel(usuario_frame, text="Usuário:").pack(side="left", padx=5)
    usuario_entry = ctk.CTkEntry(usuario_frame, width=300)
    usuario_entry.pack(side="left", padx=5)
    
    # Campo para senha
    senha_frame = ctk.CTkFrame(root_login)
    senha_frame.pack(pady=10, padx=10, fill="x")
    ctk.CTkLabel(senha_frame, text="Senha:").pack(side="left", padx=5)
    senha_entry = ctk.CTkEntry(senha_frame, width=300, show="*")
    senha_entry.pack(side="left", padx=5)
    
    # Botão para login
    ctk.CTkButton(root_login, text="Entrar", command=login_usuario).pack(pady=20)

    root_login.mainloop()

# Função para disparar mensagens no WhatsApp
def disparo_web(numeros, mensagem, imagem_caminho, max_disparos):
    global navegador
    contador_enviados = 0

    # Inicialização do navegador
    navegador = webdriver.Chrome()

    try:
        # Acessar o WhatsApp Web
        navegador.get("https://web.whatsapp.com/")
        navegador.maximize_window()
        messagebox.showinfo("Aguardando Login", "Faça login no WhatsApp Web e clique em OK quando estiver pronto.")

        # Loop para envio de mensagens
        for index, numero in enumerate(numeros):
            if contador_enviados >= max_disparos:
                messagebox.showinfo("Concluído", f"Disparo concluído após enviar {contador_enviados} mensagens.")
                break

            try:
                # Reiniciar para buscar o contato
                navegador.find_element(By.XPATH, '//button[@aria-label="Nova conversa"]').click()
                time.sleep(5)

                # Preenche o número no campo de pesquisa
                pesquisa = navegador.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div/p')
                pesquisa.send_keys(numero)
                time.sleep(3)

                # Tenta localizar e clicar no contato
                try:
                    navegador.find_element(By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/span/div/span/div/div[2]/div[2]/div[1]/div').click()
                    time.sleep(3)
                except:
                    # Caso o contato não seja encontrado
                    navegador.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[1]/span/div/span/div/header/div/div[1]/div').click()
                    time.sleep(2)
                    continue

                # Envia a mensagem
                campo_mensagem = navegador.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p')
                campo_mensagem.send_keys(mensagem)
                campo_mensagem.send_keys(Keys.ENTER)
                time.sleep(3)

                # Anexar e enviar imagem (se houver)
                if imagem_caminho:
                    navegador.find_element(By.XPATH, '//span[@data-icon="plus"]').click()
                    time.sleep(2)
                    upload_imagem = navegador.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                    upload_imagem.send_keys(imagem_caminho)
                    time.sleep(3)
                    navegador.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div/span').click()
                    time.sleep(3)

                contador_enviados += 1

                # Pausa após 25 mensagens enviadas
                if contador_enviados % 25 == 0:
                    print(f"{contador_enviados} mensagens enviadas. Pausando por 10 minutos.")
                    time.sleep(600)

            except Exception as e:
                print(f"Erro ao enviar mensagem para {numero}: {e}")

        messagebox.showinfo("Concluído", "Envio de mensagens finalizado!")
    finally:
        navegador.quit()

# Função para encerrar manualmente o navegador e sair
def fechar_navegador():
    global navegador
    if navegador:
        navegador.quit()
    messagebox.showinfo("Encerrado", "Automação finalizada e navegador fechado.")

# Interface em CustomTkinter
def iniciar_app():
    # Função para iniciar o disparo
    def iniciar_disparo():
        numeros = []
        try:
            # Carregar números do arquivo selecionado
            with open(arquivo_entry.get(), "r") as f:
                numeros = [linha.strip() for linha in f.readlines()]
            if not numeros:
                raise Exception("Lista de números está vazia.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar números: {e}")
            return

        # Pegar a mensagem e o caminho da imagem
        mensagem = mensagem_entry.get()
        imagem_caminho = imagem_entry.get()
        max_disparos = int(max_mensagens_entry.get())

        # Executar a automação em uma thread separada
        thread = Thread(target=disparo_web, args=(numeros, mensagem, imagem_caminho, max_disparos))
        thread.start()

    # Função para selecionar arquivo de números
    def selecionar_arquivo():
        caminho = filedialog.askopenfilename(title="Selecione o arquivo de números")
        arquivo_entry.delete(0, ctk.END)
        arquivo_entry.insert(0, caminho)

    # Função para selecionar a imagem
    def selecionar_imagem():
        caminho = filedialog.askopenfilename(title="Selecione a imagem para envio")
        imagem_entry.delete(0, ctk.END)
        imagem_entry.insert(0, caminho)

    # Configuração da janela principal
    root = ctk.CTk()
    root.title("Disparo de Mensagens - WhatsApp")
    root.geometry("800x500")
    
    # Título
    ctk.CTkLabel(root, text="Disparador de Mensagens Web 🤖", font=("Arial", 18)).pack(pady=10)

    # Campo para selecionar o arquivo de números
    arquivo_frame = ctk.CTkFrame(root)
    arquivo_frame.pack(pady=10, padx=10, fill="x")
    ctk.CTkLabel(arquivo_frame, text="Arquivo de Números:").pack(side="left", padx=5)
    arquivo_entry = ctk.CTkEntry(arquivo_frame, width=300)
    arquivo_entry.pack(side="left", padx=5)
    ctk.CTkButton(arquivo_frame, text="Selecionar", command=selecionar_arquivo).pack(side="left", padx=5)

    # Campo para a mensagem
    mensagem_frame = ctk.CTkFrame(root)
    mensagem_frame.pack(pady=10, padx=10, fill="x")
    ctk.CTkLabel(mensagem_frame, text="Mensagem:").pack(side="left", padx=5)
    mensagem_entry = ctk.CTkEntry(mensagem_frame, width=400)
    mensagem_entry.pack(side="left", padx=5)

    # Campo para selecionar a imagem
    imagem_frame = ctk.CTkFrame(root)
    imagem_frame.pack(pady=10, padx=10, fill="x")
    ctk.CTkLabel(imagem_frame, text="Caminho da Imagem:").pack(side="left", padx=5)
    imagem_entry = ctk.CTkEntry(imagem_frame, width=300)
    imagem_entry.pack(side="left", padx=5)
    ctk.CTkButton(imagem_frame, text="Selecionar", command=selecionar_imagem).pack(side="left", padx=5)

    # Campo para definir a quantidade de mensagens
    max_mensagens_frame = ctk.CTkFrame(root)
    max_mensagens_frame.pack(pady=10, padx=10, fill="x")
    ctk.CTkLabel(max_mensagens_frame, text="Quantidade de Mensagens:").pack(side="left", padx=5)
    max_mensagens_entry = ctk.CTkEntry(max_mensagens_frame, width=100)
    max_mensagens_entry.pack(side="left", padx=5)
    max_mensagens_entry.insert(0, "100")  # Valor padrão

    # Botão para iniciar o disparo
    ctk.CTkButton(root, text="Iniciar Disparo", command=iniciar_disparo).pack(pady=20)

    # Botão para fechar o navegador
    ctk.CTkButton(root, text="Fechar Navegador e Sair", command=fechar_navegador).pack(pady=20)

    # Inicia a janela
    root.mainloop()

if __name__ == "__main__":
    iniciar_login()



