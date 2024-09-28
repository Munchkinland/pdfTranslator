import os
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox
from transformers import pipeline
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFTranslator:
    def __init__(self, master):
        self.master = master
        self.master.title("Traductor de PDF")
        
        self.label = tk.Label(master, text="Seleccione un archivo PDF para traducir:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(master, text="Seleccionar PDF", command=self.load_pdf)
        self.select_button.pack(pady=5)

        self.translate_button = tk.Button(master, text="Traducir", command=self.translate_pdf, state=tk.DISABLED)
        self.translate_button.pack(pady=5)

        self.text_area = tk.Text(master, height=10, width=50)
        self.text_area.pack(pady=10)

        self.output_button = tk.Button(master, text="Guardar PDF Traducido", command=self.save_pdf, state=tk.DISABLED)
        self.output_button.pack(pady=5)

        self.pdf_content = ""
        self.translated_content = ""

        # Usar el modelo correcto para traducción de inglés a español
        logging.info("Inicializando el modelo de traducción.")
        self.translator = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")

    def load_pdf(self):
        logging.info("Abriendo diálogo para seleccionar PDF.")
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            logging.info(f"Cargando el archivo PDF: {file_path}")
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                self.pdf_content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            logging.info("Contenido del PDF cargado exitosamente.")
            self.text_area.insert(tk.END, "Contenido del PDF cargado.\n")
            self.translate_button.config(state=tk.NORMAL)
        else:
            logging.warning("No se seleccionó ningún archivo.")

    def translate_pdf(self):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Traduciendo...\n")
        logging.info("Iniciando la traducción del PDF.")

        # Dividir el contenido en partes para evitar el límite de tokens
        chunks = [self.pdf_content[i:i + 1000] for i in range(0, len(self.pdf_content), 1000)]
        total_chunks = len(chunks)
        self.translated_content = ""

        for index, chunk in enumerate(chunks):
            logging.info(f"Traduciendo un chunk de tamaño: {len(chunk)}")
            translated_chunk = self.translator(chunk)
            self.translated_content += translated_chunk[0]['translation_text'] + "\n"

            # Mostrar cuenta regresiva en el área de texto
            remaining_chunks = total_chunks - index - 1
            self.text_area.insert(tk.END, f"Chunks restantes: {remaining_chunks}\n")
            self.text_area.see(tk.END)  # Desplazar hacia abajo
            self.master.update()  # Actualizar la ventana para mostrar cambios

        self.text_area.insert(tk.END, "Traducción completada.\n")
        logging.info("Traducción completada exitosamente.")
        self.output_button.config(state=tk.NORMAL)

    def save_pdf(self):
        logging.info("Abriendo diálogo para guardar el PDF traducido.")
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_path:
            from fpdf import FPDF
            logging.info(f"Guardando el PDF traducido en: {output_path}")
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for line in self.translated_content.splitlines():
                pdf.cell(200, 10, txt=line, ln=True)
            
            pdf.output(output_path)
            messagebox.showinfo("Guardado", "PDF traducido guardado exitosamente!")
            logging.info("PDF guardado exitosamente.")
        else:
            logging.warning("No se seleccionó ningún destino para guardar el PDF.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFTranslator(root)
    root.mainloop()