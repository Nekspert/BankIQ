from rest_framework import serializers


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


class Indicator101Serializer(serializers.Serializer):
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


class Indicators101Serializer(serializers.Serializer):
    indicators = Indicator101Serializer(
            many=True,
            help_text="Список доступных индикаторов (catalog) — каждый элемент описан Indicator101Serializer."
    )


class BankIndicator101RequestSerializer(serializers.Serializer):
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


class BankIndicator101DataSerializer(serializers.Serializer):
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


class Indicator123Serializer(serializers.Serializer):
    name = serializers.CharField(
            required=True,
            help_text="Читабельное название индикатора (показателя) формы 123.")


class Indicators123Serializer(serializers.Serializer):
    indicators = Indicator123Serializer(
            many=True,
            help_text="Список доступных индикаторов (catalog) — каждый элемент описан Indicators123Serializer.")


class BankIndicator123DataSerializer(serializers.Serializer):
    bank_reg_number = serializers.CharField(
            required=True,
            help_text=(
                "Регистрационный номер банка (используем для связывания данных с организацией).\n"
                "Тип: строка — может быть приведён из числового поля источника."))
    name = serializers.CharField(
            required=True,
            help_text="Читабельное название индикатора (показателя) формы 123.")
    value = serializers.FloatField(
            required=True,
            help_text="Значение показателя.")


class BankIndicator810DataSerializer(serializers.Serializer):
    NUM_STR = serializers.FloatField(required=True, help_text="Номер строки (например, 1.0, 5.1).")
    LABEL = serializers.CharField(required=True,
                                  help_text="Описание/лейбл строки (например, 'Данные на начало предыдущего отчетного года').")
    NUM_P = serializers.CharField(required=True,
                                  help_text="Дополнительный номер/пункт (может быть '-', '3.12, 5', '4.1.9' или числом).")
    USTKAP = serializers.FloatField(required=True, help_text="Уставный капитал.")
    SOB_AK = serializers.FloatField(required=True, help_text="Собственные акции.")
    EMIS_DOH = serializers.FloatField(required=True, help_text="Эмиссионный доход.")
    PER_CB = serializers.FloatField(required=True, help_text="Переоценка ценных бумаг.")
    PER_OS = serializers.FloatField(required=True, help_text="Переоценка основных средств.")
    DELTADVR = serializers.FloatField(required=True, help_text="Дельта ДВР (возможно, дельта добавочного капитала).")
    PER_IH = serializers.FloatField(required=True, help_text="Переоценка инструментов хеджирования.")
    REZERVF = serializers.FloatField(required=True, help_text="Резервный фонд.")
    VKL_V_IM = serializers.FloatField(required=True, help_text="Вклады в имущество.")
    NERASP_PU = serializers.FloatField(required=True, help_text="Нераспределенная прибыль (убыток).")
    ITOGO_IK = serializers.FloatField(required=True, help_text="Итого источники капитала.")
