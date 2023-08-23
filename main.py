import imaplib
import email
import os
from ftplib import FTP
import time
from datetime import datetime

# Configurações do email
EMAIL = "xxx@xxx.com.br"
PASSWORD = "xxxxxx"
SERVER = "imap.xxx.com.br"
ALLOWED_EXTENSIONS = [".xlsx", ".xls", ".pdf", ".xml", ".docx"]

# Configurações do FTP
FTP_SERVER = "ftp.xxxx.com.br"
FTP_USERNAME = "xxx@xxx.com.br"
FTP_PASSWORD = "xxx@"
FTP_DIRECTORY = "/public_html/pasta_ftp/"

# Arquivo de log
LOG_FILE = "email_log.txt"

# Função para baixar e enviar anexo para o FTP
def process_email_attachment(msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        
        filename = part.get_filename()
        if filename and any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            attachment_data = part.get_payload(decode=True)
            
            # Enviar o anexo para o FTP
            with FTP(FTP_SERVER) as ftp:
                ftp.login(FTP_USERNAME, FTP_PASSWORD)
                ftp.cwd(FTP_DIRECTORY)
                with open(filename, 'wb') as f:
                    f.write(attachment_data)
                with open(filename, 'rb') as f:
                    ftp.storbinary(f'STOR {filename}', f)
            
            # Registrar no arquivo de log
            with open(LOG_FILE, "a") as log:
                log.write(f"Data: {datetime.now()} | Assunto: {msg['subject']} | Arquivo: {filename}\n")
            
            os.remove(filename)
            print(f"Anexo {filename} enviado para o FTP")

# Loop infinito para verificar emails a cada minuto
while True:
    try:
        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        result, data = mail.uid("search", None, "UNSEEN")
        if result == "OK":
            for num in data[0].split():
                result, msg_data = mail.uid("fetch", num, "(RFC822)")
                if result == "OK":
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    process_email_attachment(msg)
                    mail.uid("store", num, "+FLAGS", "(\\Seen)")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Esperar 1 minuto antes de verificar novamente
    time.sleep(60)
