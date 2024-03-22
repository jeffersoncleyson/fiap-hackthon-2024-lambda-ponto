import re
from datetime import datetime

from src.framework.adapters.input.rest.response_formatter_utils import (
    ResponseFormatterUtils,
)
from src.framework.adapters.output.persistence.documentdb.documentdb import (
    DocumentDBAdapter,
)

from src.application.utils.ponto_utils import PontoUtils


class ReadByDatePontoUseCase:

    def __init__(self, mongo_client: DocumentDBAdapter):
        self.mongo_client = mongo_client

    def process(self, event: dict):

        user_id = event["headers"]["x-sid"]
        date = event["headers"]["x-date"]

        is_valid_date = re.match(r"\b\d{2}-\d{2}-\d{4}\b", date)

        if is_valid_date is None:
            return ResponseFormatterUtils.get_response_message(
                {"error": f"Formato de data inválido. {date}"},
                404,
            )

        data_formatada = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")

        ponto_data = self.mongo_client.read(
            {"user_id": user_id, "data": data_formatada}
        )

        if ponto_data:
            # Calcula as horas totais para o registro encontrado
            total_hours = PontoUtils.calculate_total_hours(
                ponto_data.get("array_ponto", [])
            )
            formatted_result = {
                "data": datetime.strptime(ponto_data["data"], "%Y-%m-%d").strftime(
                    "%d-%m-%Y"
                ),
                "hours": ponto_data.get("array_ponto", []),
                "total_hours": total_hours,
            }
            return ResponseFormatterUtils.get_response_message(
                formatted_result,
                200,
            )

        return ResponseFormatterUtils.get_response_message(
            {"error": "Nenhum ponto encontrado para esta data."},
            404,
        )
