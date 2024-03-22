import pytz
import logging
from datetime import datetime, timezone

from src.framework.adapters.input.rest.response_formatter_utils import (
    ResponseFormatterUtils,
)
from src.framework.adapters.output.persistence.documentdb.documentdb import (
    DocumentDBAdapter,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CreatePontoUseCase:

    def __init__(self, mongo_client: DocumentDBAdapter):
        self.mongo_client = mongo_client
        self.timezone = pytz.timezone('America/Sao_Paulo')

    def process(self, event: dict):

        user_id = event["headers"]["x-sid"]

        now = datetime.now(tz=self.timezone)
        data = now.date().isoformat()
        hora = now.strftime('%H:%M')

        # Verificar se já existe um registro para o usuário na data atual
        ponto_data = self.mongo_client.read({"user_id": user_id, "data": data})

        # Se já existir, atualiza o documento existente
        if ponto_data:
            # Adiciona o registro ao array de pontos
            self.mongo_client.update(
                {"_id": ponto_data['_id']},
                {"$push": {"array_ponto": hora}}
            )
        else:
            # Cria um novo documento
            ponto_data = {
                'user_id': user_id,
                'data': data,
                'array_ponto': [hora]
            }
            result = self.mongo_client.insert(ponto_data)
            if result is None:
                return {"error": "Falha ao registrar o ponto."}, 500

        return ResponseFormatterUtils.get_response_message(
            {"message": "Ponto registrado com sucesso.", "timestamp": hora},
            200,
        )
