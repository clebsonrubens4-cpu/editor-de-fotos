import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile

st.set_page_config(page_title="Editor de Fotos", layout="centered")

st.title("📸 Editor de Fotos e Molduras")
st.write("Corte automático centralizado e aplicação de moldura em lote com máxima qualidade.")

# 1. Upload das fotos
fotos_upload = st.file_uploader(
    "1. Selecione as fotos (que serão cortadas no centro)", 
    type=['jpg', 'jpeg', 'png', 'webp'], 
    accept_multiple_files=True
)

# 2. Upload da moldura
moldura_upload = st.file_uploader(
    "2. Selecione a moldura (PNG transparente)", 
    type=['png']
)

if st.button("PROCESSAR FOTOS", type="primary") and fotos_upload and moldura_upload:
    with st.spinner("Processando imagens em altíssima resolução..."):
        try:
            moldura = Image.open(moldura_upload).convert("RGBA")
            largura_m, altura_m = moldura.size
            proporcao_m = largura_m / altura_m

            buffer_zip = io.BytesIO()

            with zipfile.ZipFile(buffer_zip, "w") as zf:
                for idx, foto_file in enumerate(fotos_upload):
                    img = Image.open(foto_file)
                    
                    # Correção de rotação (EXIF)
                    img = ImageOps.exif_transpose(img)

                    largura_f, altura_f = img.size
                    proporcao_f = largura_f / altura_f

                    # Corte Centralizado
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
                    
                    # Redimensionamento de alta fidelidade
                    img_redimensionada = img_cortada.resize((largura_m, altura_m), Image.Resampling.LANCZOS)

                    # Sobreposição da Moldura
                    img_final = Image.new("RGBA", (largura_m, altura_m))
                    img_final.paste(img_redimensionada, (0, 0))
                    img_final.paste(moldura, (0, 0), mask=moldura)

                    # Conversão para RGB e salvamento em JPEG de Qualidade Máxima (100)
                    img_rgb = img_final.convert("RGB")
                    img_byte_arr = io.BytesIO()
                    
                    # quality=100 e subsampling=0 garantem fidelidade total de cores e detalhes
                    img_rgb.save(img_byte_arr, format='JPEG', quality=100, subsampling=0)
                    
                    zf.writestr(f"foto_editada_{idx+1}.jpg", img_byte_arr.getvalue())

            st.success("✅ Fotos processadas com sucesso e qualidade máxima!")
            st.download_button(
                label="⬇️ Baixar todas as fotos (.ZIP)",
                data=buffer_zip.getvalue(),
                file_name="fotos_editadas.zip",
                mime="application/zip"
            )
        except Exception as e:
            st.error(f"Erro ao processar as imagens: {e}")
elif not fotos_upload or not moldura_upload:
    st.info("Por favor, anexe as fotos e a moldura acima antes de clicar em processar.")
