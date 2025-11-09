from rest_framework import serializers


class BankInfoSerializer(serializers.Serializer):
    bic = serializers.CharField(
            required=True,
            help_text="БИК банка (Bank Identification Code). Уникальный идентификатор банка. Пример: '044525225'."
    )
    name = serializers.CharField(
            required=True,
            help_text="Полное наименование кредитной организации."
    )
    reg_number = serializers.CharField(
            required=True,
            help_text="Регистрационный номер организации в базе ЦБ РФ (строка). Пример: '1481'."
    )
    internal_code = serializers.CharField(
            required=True,
            help_text="Внутренний код/идентификатор банка в источнике данных (если доступен)."
    )
    registration_date = serializers.DateTimeField(
            required=True,
            help_text="Дата регистрации организации (ISO 8601). Может содержать смещение часового пояса."
    )
    region_code = serializers.CharField(
            required=True,
            help_text="Код региона (региональный номер/код)."
    )
    tax_id = serializers.CharField(
            required=True,
            help_text="Идентификатор налогоплательщика (ИНН) или другой налоговый идентификатор, если присутствует."
    )


class AllBanksSerializer(serializers.Serializer):
    banks = BankInfoSerializer(
            many=True,
            help_text="Список банков, каждый элемент — структура BankInfoSerializer."
    )


class RegNumberSerializer(serializers.Serializer):
    reg_number = serializers.IntegerField(
            required=True,
            help_text="Регистрационный номер банка (целое положительное число). Пример: 1481."
    )


class DateTimesSerializer(serializers.Serializer):
    datetimes = serializers.ListSerializer(
            child=serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%Z'),
            help_text=(
                "Список доступных дат формы F101. Каждая дата возвращается в ISO-8601. "
                "Если исходный объект содержит tzinfo, DRF может конвертировать в UTC (с суффиксом 'Z')."
            )
    )


class RegNumAndDatetimeSerializer(serializers.Serializer):
    reg_number = serializers.IntegerField(
            required=True,
            help_text="Регистрационный номер банка (целое положительное число). Пример: 1481."
    )
    dt = serializers.DateTimeField(
            required=True,
            format='%Y-%m-%dT%H:%M:%S%Z',
            help_text=(
                "Дата/метка времени (ISO 8601).\n"
                "Примечание: сериализатор принимает timezone-aware или naive datetime, но при сериализации/десериализации "
                "смещение может быть отброшено (по умолчанию делается .replace(tzinfo=None))."
            )
    )

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        dt = validated['dt']
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        validated['dt'] = dt
        return validated


class IndicatorSerializer(serializers.Serializer):
    name = serializers.CharField(
            required=True,
            help_text="Читабельное название индикатора (показателя) формы 101."
    )
    ind_code = serializers.CharField(
            required=True,
            help_text=(
                "Код индикатора (IndCode / numsc) — строковое значение, используется для сопоставления с каталогом "
                "счетов.\n"
                "Пример: '410' — Депозиты Федерального казначейства."
            )
    )


class IndicatorsSerializer(serializers.Serializer):
    indicators = IndicatorSerializer(
            many=True,
            help_text="Список доступных индикаторов (catalog) — каждый элемент описан IndicatorSerializer."
    )


class BankIndicatorRequestSerializer(serializers.Serializer):
    reg_number = serializers.IntegerField(
            required=True,
            help_text="Регистрационный номер банка (целое положительное число). Пример: 1481."
    )
    ind_code = serializers.CharField(
            required=True,
            help_text="Код индикатора (IndCode / numsc) — строковое значение, например '410'."
    )
    date_from = serializers.DateTimeField(
            required=True,
            help_text=(
                "Начальная дата диапазона (ISO-8601).\n"
                "Примечание: ожидается naive datetime (смещение будет отброшено); дата включается в диапазон."
            )
    )
    date_to = serializers.DateTimeField(
            required=True,
            help_text=(
                "Конечная дата диапазона (ISO-8601).\n"
                "Примечание: ожидается naive datetime (смещение будет отброшено); дата включается в диапазон."
            )
    )

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        for k in ('date_from', 'date_to'):
            dt = validated.get(k)
            if dt.tzinfo is not None:
                validated[k] = dt.replace(tzinfo=None)
        return validated


class BankIndicatorDataSerializer(serializers.Serializer):
    bank_reg_number = serializers.CharField(
            required=True,
            help_text=(
                "Регистрационный номер банка (используем для связывания данных с организацией).\n"
                "Тип: строка — может быть приведён из числового поля источника."
            )
    )
    date = serializers.DateTimeField(
            required=True,
            help_text=(
                "Дата записи (поле DT/‘dt’ из исходной формы F101).\n"
                "Описание: отчетная дата (обычно первый день месяца).\n"
                "Формат: ISO-8601. Внутри системы может храниться как aware- или naive-datetime; при выводе"
                "DRF может конвертировать время в UTC в зависимости от настройки USE_TZ."
            ),

    )
    pln = serializers.CharField(
            required=True,
            help_text=(
                "Глава плана счетов (PLAN): один символ, обозначающий раздел бухгалтерского плана: \n"
                "- 'А' — балансовые счета\n"
                "- 'Б' — счета доверительного управления\n"
                "- 'В' — внебалансовые счета\n"
                "- 'Г' — срочные операции\n"
                "- 'Д' — счета Депо (если присутствует)\n"
                "Используется для группировки и выбора нужного раздела отчёта."
            )
    )
    ap = serializers.ChoiceField(
            required=True,
            choices=((1, 'Актив'), (2, 'Пассив')),
            help_text=(
                "Сторона/тип показателя: 1 — актив, 2 — пассив.\n"
                "Соответствует полю A_P в описании DBF: '1' — счет активный; '2' — счет пассивный."
            )
    )
    vitg = serializers.FloatField(
            required=True,
            help_text=(
                "Входящий итог (VITG) — сумма на начало периода или входящее сальдо, единицы: тыс. руб.\n"
                "Примечание: в исходных DBF/SOAP ответах числовые поля обычно содержат 4 знака после запятой —"
                "сериализатор приводит их в float."
            )
    )
    iitg = serializers.FloatField(
            required=True,
            help_text=(
                "Исходящий итог (IITG) — итог/сальдо на конец периода, единицы: тыс. руб.\n"
                "Примечание: см. VITG по единицам."
            )
    )

    def to_representation(self, instance):
        orig_dt = instance.get('date')
        if hasattr(orig_dt, 'replace'):
            naive = orig_dt.replace(tzinfo=None)
            instance['date'] = naive
        return super().to_representation(instance)
