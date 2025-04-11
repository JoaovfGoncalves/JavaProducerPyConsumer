import logging
import json
import os
from datetime import datetime

class MessageHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.worker_id = os.getenv("WORKER_ID", "main")
        self.pid = os.getpid()

    def handle(self, ch, method, properties, body):
        try:
            data = json.loads(body.decode("utf-8"))

            # Extrair dados
            raw_timestamp = data.get("timestamp")
            dt_obj = datetime.fromisoformat(raw_timestamp.replace("Z", "")) if raw_timestamp else datetime.now()
            formatted_time = dt_obj.strftime('%d/%m/%Y - %H:%M')

            id_coletor = data.get("id_coletor", "N/A")
            localizacao = data.get("localizacao", "N/A")
            tipo = data.get("tipo_mensagem", "N/A")
            status = data.get("status", "N/A")
            volume = f"{data.get('volume_atual', 0.0):.1f}"
            capacidade = f"{data.get('capacidade_total', 0.0):.1f}"
            info = data.get("informacao_adicional", "").strip()

            mensagem = f"[{formatted_time}] {id_coletor} : {localizacao} : {tipo} : {status} : {volume} kg : {capacidade} kg"
            if info:
                mensagem += f" : {info}"

            print(f"\n[Worker {self.worker_id} | PID {self.pid}] Mensagem formatada:")
            print(mensagem)

            self.logger.info(f"Mensagem processada - {mensagem}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem no Worker {self.worker_id}: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
