import os
from PIL import Image

def processar_fotos(pasta_entrada, pasta_saida, caminho_moldura):
    # Cria a pasta de saída se ela não existir
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # Carrega a moldura e garante que está no formato RGBA (com transparência)
    moldura = Image.open(caminho_moldura).convert("RGBA")
    largura_moldura, altura_moldura = moldura.size

    # Formatos de imagem aceitos
    extensoes_validas = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    # Percorre todas as fotos da pasta de entrada
    for arquivo in os.listdir(pasta_entrada):
        if arquivo.lower().endswith(extensoes_validas):
            caminho_imagem = os.path.join(pasta_entrada, arquivo)
            
            with Image.open(caminho_imagem) as img:
                # 1. Cortar a foto no formato quadrado (1:1) do Instagram
                largura, altura = img.size
                tamanho_corte = min(largura, altura)

                left = (largura - tamanho_corte) / 2
                top = (altura - tamanho_corte) / 2
                right = (largura + tamanho_corte) / 2
                bottom = (altura + tamanho_corte) / 2

                # Executa o corte centralizado
                img_cortada = img.crop((left, top, right, bottom))

                # Redimensiona a foto cortada para bater com o tamanho da moldura
                img_redimensionada = img_cortada.resize((largura_moldura, altura_moldura), Image.Resampling.LANCZOS)
                
                # Converte para RGBA para permitir a sobreposição da moldura
                img_final = img_redimensionada.convert("RGBA")

                # 2. Aplicar a moldura
                # O parâmetro 'mask=moldura' usa o canal alfa (transparência) da moldura
                img_final.paste(moldura, (0, 0), mask=moldura)

                # Salva o resultado final em JPG (ou PNG) na pasta de saída
                caminho_salvar = os.path.join(pasta_saida, f"editada_{os.path.splitext(arquivo)[0]}.jpg")
                img_final.convert("RGB").save(caminho_salvar, "JPEG", quality=95)
                
                print(f"Processada: {arquivo}")

# --- CONFIGURAÇÃO E EXECUÇÃO ---
# Coloque o caminho das suas pastas e da sua moldura aqui:
PASTA_ENTRADA = "fotos_originais"
PASTA_SAIDA = "fotos_prontas"
MOLDURA = "moldura.png"

# Executa o script
processar_fotos(PASTA_ENTRADA, PASTA_SAIDA, MOLDURA)