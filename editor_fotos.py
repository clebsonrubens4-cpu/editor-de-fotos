import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile

st.set_page_config(page_title="Editor de Fotos HD", layout="centered")

st.title("📸 Editor de Fotos e Molduras (Qualidade HD)")
st.write("Corte automático mantendo a resolução e qualidade total da foto original.")

# 1. Upload das fotos
fotos_upload = st.file_uploader(
    "1. Selecione as fotos", 
    type=['jpg', 'jpeg', 'png', 'webp'], 
    accept_multiple_files=True
)

# 2. Upload da moldura
moldura_upload = st.file_uploader(
    "2. Selecione a moldura (PNG transparente)", 
    type=['png']
)

if st.button("PROCESSAR FOTOS", type="primary") and fotos_upload and moldura_upload:
    with st.spinner("Processando imagens em resolução original..."):
        try:
            moldura_orig = Image.open(moldura_upload).convert("RGBA")
            proporcao_m = moldura_orig.width / moldura_orig.height

            buffer_zip = io.BytesIO()
            fotos_processadas = []

            with zipfile.ZipFile(buffer_zip, "w") as zf:
                for idx, foto_file in enumerate(fotos_upload):
                    img = Image.open(foto_file)
                    
                    # Correção automática de rotação (EXIF)
                    img = ImageOps.exif_transpose(img)

                    largura_f, altura_f = img.size
                    proporcao_f = largura_f / altura_f

                    # Corte Centralizado na Foto Original
                    if proporcao_f > proporcao_m:
                        nova_largura = int(altura_f * proporcao_m)
                        left = (largura_f - nova_largura) // 2
                        top = 0
                        right = left + nova_largura
                        bottom = altura_f
                    else:
                        nova_altura = int(largura_f / proporcao_m)
                        top = (altura_f - nova_altura) // 2
                        left = 0
                        right = largura_f
                        bottom = top + nova_altura

                    img_cortada = img.crop((left, top, right, bottom))
                    
                    # Ajusta a MOLDURA ao tamanho da FOTO CORTADA (e não o contrário)
                    # Isso garante que a foto NÃO perca megapixels!
                    largura_corte, altura_corte = img_cortada.size
                    moldura_hd = moldura_orig.resize((largura_corte, altura_corte), Image.Resampling.LANCZOS)

                    # Sobreposição da Moldura
                    img_final = Image.new("RGBA", (largura_corte, altura_corte))
                    img_final.paste(img_cortada.convert("RGBA"), (0, 0))
                    img_final.paste(moldura_hd, (0, 0), mask=moldura_hd)

                    # Salva em PNG de altíssima qualidade sem compressão destrutiva
                    img_byte_arr = io.BytesIO()
                    img_final.save(img_byte_arr, format='PNG', compress_level=1)
                    
                    conteudo_bytes = img_byte_arr.getvalue()
                    nome_arquivo = f"foto_editada_{idx+1}.png"
                    
                    zf.writestr(nome_arquivo, conteudo_bytes)
                    fotos_processadas.append((nome_arquivo, conteudo_bytes, img_final))

            st.success("✅ Fotos processadas em Alta Definição!")
            
            # Botão para baixar tudo em ZIP
            st.download_button(
                label="⬇️ Baixar TODAS as fotos (.ZIP)",
                data=buffer_zip.getvalue(),
                file_name="fotos_editadas_HD.zip",
                mime="application/zip"
            )

            st.write("---")
            st.subheader("🖼️ Ou baixe individualmente:")
            
            # Exibe prévia e botão de download individual de cada foto
            for nome, b_data, img_obj in fotos_processadas:
                st.image(img_obj, caption=nome, use_container_width=True)
                st.download_button(
                    label=f"Baixar {nome}",
                    data=b_data,
                    file_name=nome,
                    mime="image/png"
                )

        except Exception as e:
            st.error(f"Erro ao processar as imagens: {e}")
elif not fotos_upload or not moldura_upload:
    st.info("Por favor, anexe as fotos e a moldura acima antes de clicar em processar.")
