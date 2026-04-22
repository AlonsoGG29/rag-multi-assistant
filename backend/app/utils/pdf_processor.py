"""
Utilidad para procesar archivos PDF y extraer texto
"""
from io import BytesIO
import PyPDF2

def extract_text(content: bytes) -> str:
    """
    Extrae texto de un archivo PDF
    
    Args:
        content: Contenido binario del archivo PDF
        
    Returns:
        Texto extraído del PDF
    """
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        raise ValueError(f"Error al procesar PDF: {str(e)}")

def extract_text_from_file(file_path: str) -> str:
    """
    Extrae texto de un archivo PDF local
    
    Args:
        file_path: Ruta al archivo PDF
        
    Returns:
        Texto extraído del PDF
    """
    with open(file_path, 'rb') as f:
        return extract_text(f.read())
