import logging
import pymongo

from src.application.utils.environment import EnvironmentUtils
from src.application.utils.environment_constants import EnvironmentConstants
from src.framework.adapters.input.rest.response_formatter_utils import (
    ResponseFormatterUtils,
)
from src.framework.adapters.output.persistence.documentdb.documentdb import (
    DocumentDBAdapter,
)
from src.framework.adapters.input.rest.response_formatter_utils import (
    ResponseFormatterUtils,
)
from src.application.usecases.ponto.create_ponto_user_case import CreatePontoUseCase
from src.application.usecases.ponto.read_by_date_ponto_user_case import (
    ReadByDatePontoUseCase,
)

from src.application.usecases.ponto.read_by_period_ponto_user_case import (
    ReadByPeriodPontoUseCase,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

mongo_uri = EnvironmentUtils.get_env(EnvironmentConstants.MONGO_URI.name)
database = EnvironmentUtils.get_env(EnvironmentConstants.DB_NAME.name)
database_client = pymongo.MongoClient(mongo_uri)
database_adapter = DocumentDBAdapter("pontos", database_client[database])

create_ponto_use_case = CreatePontoUseCase(database_adapter)
read_by_date_ponto_use_case = ReadByDatePontoUseCase(database_adapter)
read_by_period_ponto_use_case = ReadByPeriodPontoUseCase(database_adapter)


def lambda_handler(event, context):

    resource_path = event["requestContext"]["resourcePath"]
    http_method = event["requestContext"]["httpMethod"]

    if http_method == "POST" and resource_path == "/ponto/create":
        return create_ponto_use_case.process(event)
    elif http_method == "GET" and resource_path == "/ponto/read/date":
        return read_by_date_ponto_use_case.process(event)
    elif http_method == "GET" and resource_path == "/ponto/read/period":
        return read_by_period_ponto_use_case.process(event)

    return ResponseFormatterUtils.get_response_message(
        {
            "error": "not_found",
            "error_description": "%s %s is not a valid resource."
            % (http_method, resource_path),
        },
        404,
    )
