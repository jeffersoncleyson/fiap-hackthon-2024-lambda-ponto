from datetime import datetime
import pytz
from src.application.ports.input.rest.ponto.period import Period
from src.framework.adapters.input.rest.response_formatter_utils import (
    ResponseFormatterUtils,
)
from src.framework.adapters.output.persistence.documentdb.documentdb import (
    DocumentDBAdapter,
)

from src.application.utils.ponto_utils import PontoUtils


class ReadByPeriodPontoUseCase:

    def __init__(self, mongo_client: DocumentDBAdapter):
        self.mongo_client = mongo_client
        self.timezone = pytz.timezone('America/Sao_Paulo')

    def process(self, event: dict):

        user_id = event["headers"]["x-sid"]
        period = event["headers"]["x-period"]


        if period not in Period.__members__:
            return ResponseFormatterUtils.get_response_message(
                {
                    "error": "bad_request",
                    "error_description": f"Invalid period. Must be one of: {', '.join(Period.__members__)}",
                },
                400,
            )
        
        start_date, end_date = PontoUtils.parse_period(Period[period], self.timezone)

        if start_date is None or end_date is None:
            return ResponseFormatterUtils.get_response_message(
                {
                    "error": "internal_server_error",
                    "error_description": "Invalid parse period",
                },
                500,
            )

        results = self.mongo_client.read_all({"user_id": user_id, "data": {"$gte": start_date, "$lte": end_date}})

        formatted_results = []
        for result in results:

            total_hours = PontoUtils.calculate_total_hours(result.get('array_ponto', []))

            formatted_result = {
                "data": datetime.strptime(result['data'], '%Y-%m-%d').strftime('%d-%m-%Y'),  # Formata a data
                "hours": result.get('array_ponto', []),
                "total_hours": total_hours
            }

            formatted_results.append(formatted_result)

        return ResponseFormatterUtils.get_response_message(
                formatted_results,
                200,
            )
