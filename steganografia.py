import numpy as np
from PIL import Image
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

# Variaveis globais para armazenar as chaves
chave_privada = None
chave_publica = None

def criar_chaves():
    """Cria par de chaves publica e privada"""
    global chave_privada, chave_publica
    
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    chave_publica = chave_privada.public_key()
    print("Chaves criadas com sucesso")

def criar_imagem_teste():
    """Cria uma imagem colorida para testes"""
    imagem = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
    img = Image.fromarray(imagem)
    img.save("imagem_original.png")
    print("Imagem de teste criada: imagem_original.png")

def texto_para_binario(texto):
    """Converte texto em binario"""
    binario = ""
    for letra in texto:
        binario += format(ord(letra), '08b')
    return binario

def binario_para_texto(binario):
    """Converte binario em texto"""
    texto = ""
    for i in range(0, len(binario), 8):
        byte = binario[i:i+8]
        if len(byte) == 8:
            texto += chr(int(byte, 2))
    return texto

def opcao_1_embutir_texto():
    """Opcao 1: Esconde texto dentro de uma imagem"""
    print("\n--- OPCAO 1: Embutir texto em imagem ---")
    
    # Pede o nome da imagem
    nome_imagem = input("Nome da imagem original (ou Enter para criar uma): ")
    if nome_imagem == "":
        criar_imagem_teste()
        nome_imagem = "imagem_original.png"
    
    # Pede a mensagem
    mensagem = input("Digite a mensagem para esconder: ")
    mensagem = mensagem + "###FIM###"  # Marca o fim da mensagem
    
    # Carrega a imagem
    img = Image.open(nome_imagem)
    img_array = np.array(img)
    
    # Converte mensagem para binario
    mensagem_binaria = texto_para_binario(mensagem)
    
    # Esconde a mensagem nos pixels
    img_plana = img_array.flatten()
    
    for i in range(len(mensagem_binaria)):
        img_plana[i] = (img_plana[i] & 254) | int(mensagem_binaria[i])
    
    # Salva a nova imagem
    img_nova = img_plana.reshape(img_array.shape)
    img_final = Image.fromarray(img_nova.astype('uint8'))
    img_final.save("imagem_com_texto.png")
    
    print("Texto embutido com sucesso!")
    print("Imagem salva como: imagem_com_texto.png")

def opcao_2_extrair_texto():
    """Opcao 2: Recupera texto escondido na imagem"""
    print("\n--- OPCAO 2: Extrair texto da imagem ---")
    
    nome_imagem = input("Nome da imagem com texto escondido: ")
    
    # Carrega a imagem
    img = Image.open(nome_imagem)
    img_array = np.array(img)
    
    # Extrai os bits
    img_plana = img_array.flatten()
    mensagem_binaria = ""
    
    for pixel in img_plana:
        mensagem_binaria += str(pixel & 1)
    
    # Converte para texto
    mensagem = binario_para_texto(mensagem_binaria)
    
    # Procura pelo marcador de fim
    if "###FIM###" in mensagem:
        mensagem = mensagem.split("###FIM###")[0]
        print("\nMensagem encontrada:")
        print("=" * 50)
        print(mensagem)
        print("=" * 50)
    else:
        print("Nenhuma mensagem encontrada")

def opcao_3_gerar_hash():
    """Opcao 3: Gera e compara hash das imagens"""
    print("\n--- OPCAO 3: Comparar hash das imagens ---")
    
    img1 = input("Nome da imagem original: ")
    img2 = input("Nome da imagem modificada: ")
    
    # Gera hash da primeira imagem
    with open(img1, 'rb') as f:
        dados1 = f.read()
        hash1 = hashlib.sha256(dados1).hexdigest()
    
    # Gera hash da segunda imagem
    with open(img2, 'rb') as f:
        dados2 = f.read()
        hash2 = hashlib.sha256(dados2).hexdigest()
    
    print("\nHash da imagem original:")
    print(hash1)
    print("\nHash da imagem modificada:")
    print(hash2)
    
    if hash1 == hash2:
        print("\nOs hashes sao iguais - imagens identicas")
    else:
        print("\nOs hashes sao diferentes - houve alteracao de pixels")

def opcao_4_encriptar():
    """Opcao 4: Encripta uma mensagem"""
    print("\n--- OPCAO 4: Encriptar mensagem ---")
    
    mensagem = input("Digite a mensagem para encriptar: ")
    
    # Encripta a mensagem
    mensagem_bytes = mensagem.encode()
    
    mensagem_encriptada = chave_publica.encrypt(
        mensagem_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Converte para base64 para poder salvar como texto
    mensagem_final = base64.b64encode(mensagem_encriptada).decode()
    
    print("\nMensagem encriptada:")
    print(mensagem_final)
    
    # Salva em arquivo
    with open("mensagem_encriptada.txt", "w") as f:
        f.write(mensagem_final)
    print("\nMensagem salva em: mensagem_encriptada.txt")
    print("\nVoce pode usar a opcao 1 para esconder esta mensagem em uma imagem")

def opcao_5_decriptar():
    """Opcao 5: Decripta uma mensagem"""
    print("\n--- OPCAO 5: Decriptar mensagem ---")
    
    print("Escolha uma opcao:")
    print("1 - Ler mensagem de arquivo")
    print("2 - Extrair mensagem de imagem primeiro")
    
    escolha = input("Opcao: ")
    
    if escolha == "1":
        with open("mensagem_encriptada.txt", "r") as f:
            mensagem_encriptada = f.read()
    elif escolha == "2":
        nome_imagem = input("Nome da imagem: ")
        img = Image.open(nome_imagem)
        img_array = np.array(img)
        img_plana = img_array.flatten()
        
        mensagem_binaria = ""
        for pixel in img_plana:
            mensagem_binaria += str(pixel & 1)
        
        mensagem_temp = binario_para_texto(mensagem_binaria)
        if "###FIM###" in mensagem_temp:
            mensagem_encriptada = mensagem_temp.split("###FIM###")[0]
        else:
            print("Erro ao extrair mensagem")
            return
    else:
        print("Opcao invalida")
        return
    
    # Decripta
    mensagem_bytes = base64.b64decode(mensagem_encriptada.encode())
    
    mensagem_decriptada = chave_privada.decrypt(
        mensagem_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    print("\nMensagem decriptada:")
    print("=" * 50)
    print(mensagem_decriptada.decode())
    print("=" * 50)

def mostrar_menu():
    """Mostra o menu de opcoes"""
    print("\n" + "=" * 50)
    print("SISTEMA DE ESTEGANOGRAFIA E CRIPTOGRAFIA")
    print("=" * 50)
    print("1 - Embutir texto em imagem")
    print("2 - Extrair texto de imagem")
    print("3 - Gerar hash das imagens")
    print("4 - Encriptar mensagem")
    print("5 - Decriptar mensagem")
    print("S - Sair")
    print("=" * 50)

def main():
    """Funcao principal"""
    print("Iniciando sistema...")
    criar_chaves()
    
    while True:
        mostrar_menu()
        opcao = input("\nEscolha uma opcao: ").upper()
        
        if opcao == "1":
            opcao_1_embutir_texto()
        elif opcao == "2":
            opcao_2_extrair_texto()
        elif opcao == "3":
            opcao_3_gerar_hash()
        elif opcao == "4":
            opcao_4_encriptar()
        elif opcao == "5":
            opcao_5_decriptar()
        elif opcao == "S":
            print("\nEncerrando programa...")
            break
        else:
            print("Opcao invalida!")
        
        input("\nPressione Enter para continuar...")

# Inicia o programa
main()
