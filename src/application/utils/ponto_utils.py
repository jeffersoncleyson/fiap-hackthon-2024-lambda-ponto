from datetime import datetime, timedelta
from src.application.ports.input.rest.ponto.period import Period

class PontoUtils:

    @staticmethod
    def calculate_total_hours(array_ponto):
        total_seconds = 0
        for i in range(0, len(array_ponto), 2):
            if i + 1 < len(array_ponto):  # Verifica se existe um par para calcular
                hora_entrada = datetime.strptime(array_ponto[i], "%H:%M")
                hora_saida = datetime.strptime(array_ponto[i + 1], "%H:%M")
                total_seconds += (hora_saida - hora_entrada).seconds
        total_horas = total_seconds / 3600
        return round(total_horas, 2)

    def parse_period(period: Period, timezone: str):
        
        now = datetime.now(tz=timezone)
        
        if period == Period.DAY:
            start_date = now.strftime("%Y-%m-%d")
            end_date = start_date
            return start_date, end_date
        elif period == Period.WEEK:
            start_date = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            end_date = (now + timedelta(days=6 - now.weekday())).strftime("%Y-%m-%d")
            return start_date, end_date
        elif period == Period.MONTH:
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            end_date = (now.replace(day=1) + timedelta(days=32)).replace(
                day=1
            ) - timedelta(days=1)
            end_date = end_date.strftime("%Y-%m-%d")
            return start_date, end_date
        else:
            return None, None