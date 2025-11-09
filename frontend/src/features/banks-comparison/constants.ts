export const INDICATORS = [
  { key: 'reg_number', label: 'Рег. номер' },
  { key: 'bic', label: 'БИК' },
  { key: 'internal_code', label: 'Внутренний код' },
  { key: 'registration_date', label: 'Дата регистрации' },
  { key: 'region_code', label: 'Код региона' },
  { key: 'tax_id', label: 'ИНН' },
];

export const DEFAULT_BANKS_REGS = [
  '1481', // SBER
  '2673', // T_BANK
  '1326', // Alpha
  '1000', // VTB
  '354', // Gazprom
  '3349', // RSCH
  '963', // SovcomBank
  '3292', // RaiffazenBank
  '2275', // Uralsib
];

export const BANK_TOP_INDICATORS = [
  { name: 'Общие активы', ind_code: '468' },
  {
    name: 'Кредиты, предоставленные негосударственным финансовым организациям',
    ind_code: '451',
  },
  {
    name: 'Средства бюджетов субъектов РФ',
    ind_code: '402',
  },
  {
    name: 'Кредиты и прочие средства, предоставленные индивидуальным предпринимателям',
    ind_code: '454',
  },
  {
    name: 'Уставный капитал кредитных организаций',
    ind_code: '102',
  },
  {
    name: 'Финансовый результат текущего года',
    ind_code: '706',
  },
  { name: 'Резервный фонд', ind_code: '107' },
  { name: 'Депозиты в Банке России', ind_code: '319' },
  {
    name: 'Корреспондентские счета',
    ind_code: '301',
  },
  { name: 'Финансовая аренда (лизинг)', ind_code: '608' },
  {
    name: 'Недвижимость, временно неиспользуемая',
    ind_code: '619',
  },
  {
    name: 'Долевые ценные бумаги, имеющиеся в наличии для продажи',
    ind_code: '507',
  },
  {
    name: 'Кредиты и прочие средства, предоставленные ИП',
    ind_code: '454',
  },
  {
    name: 'Депозиты негосударственных некоммерческих организаций',
    ind_code: '422',
  },
  { name: 'Прочие счета', ind_code: '408' },
];