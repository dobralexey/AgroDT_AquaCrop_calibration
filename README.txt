Запуск модели:

В папке ./aquacrop/main/projects/defualt_project лежит проект по умолчанию 
В нем есть файл main, который редактируется пользователем и вызывается

Описание обязательных переменных, определяемых пользователем в файле main:
#----USER DEFINED PARAMETERS----
aquacrop_all_projects_folder - путь до папки, где лежат все проекты
project_name_base - str - название проекта, в котором работает пользователь
latitude - int - широта в градусах с десятичными долями (от -90 до 90)
longitude - int - долгота в градусах с десятичными долями (от -90 до 90)
yield_measured - list(int,..) измеренная урожайность для сорта в разные годы (т/га)
simulation_starts - list(int,..) даты начала симуляции модели для этих лет, формат "yyyymmdd"
simulation_ends - list(int,..) даты конца симуляции модели для этих лет, формат "yyyymmdd"
growing_season_starts - list(int,..) дата сева для этих лет, формат "yyyymmdd"
growing_season_ends - list(int,..) дата окончания вег.периода для этих лет, формат "yyyymmdd"
crop_ref - культура для которой будет калиброваться сорт (список всех культур в папке './CROPS')
crop_parameters_dict_new = {} - словарь параметров, которые пользщователю необходимо задать
soil_df = pd.DataFrame({}) - датафрейм почвенных свойств по профилю (не более 5 слоев)
swo_dfs = [pd.DataFrame({}), ...] - список из датафреймов с объемной влажностью почвы по профилю на начало симуляции модели (simulation_starts) для каждого года

Описание переменных, которые можно оставить по умолчанию, если нет специальных знаний:
#----DEFAULT PARAMETERS----
fertility_stress_range = [1,75] - границы калибровки для стресса плодородия (%)
gwt_depth = 10 - глубина уровня грунтовых вод (м)
gwt_ec = 0 - электропроводность грунтовых вод (дСм/м)
N = 8 - отвечает за количество сочетаний параметров при калибровке, чем больше значение, тем больше возможных сочетаний, но дольше работа программы
parameters_for_calibration - параметры, которые будут калиброваться для сорта, список параметров культуры можно получить функцией aquacrop.tools.crop_functions.get_crop_parameters_dict
crop_parameters_rounds - до скольки знаков параметры округляются (нужно для формирования правильного txt)
range_percent - процент отклонения от текущего значения параметра растительности для калибровки


Результат работы:
crop_parameters_result - откалиброванные параметры для сорта и условий выращивания
error - среднеквадратичная ошибка (RMSE, т/га)


Русские соответствия названий культур:
Barley.CRO - ячмень
Canola.CRO - рапс
Maize.CRO - кукуруза
Oat.CRO - овёс
Potato.CRO - картофель
Soybean.CRO - соя
SugarBeet.CRO - сахарная свёкла
Sunflower.CRO - подсолнечник
Tomato.CRO - томат
Wheat.CRO - пшеница


Русские соотвествия названий параметров культуры, который вводит пользователь: 
'Number of plants per hectare' - количество растений на гектар
'Calendar Days: from sowing to emergence' - количество дней от посева до появления всходов
'Calendar Days: from sowing to maximum rooting depth' - количество дней от посева до глубины максимального укоренения
'Calendar Days: from sowing to start senescence' - количество дней от посева до начала старения растений
'Calendar Days: from sowing to maturity (length of crop cycle)' - количество дней от посева до созревания
'Calendar Days: from sowing to flowering' - количество дней от посева до начала дветения
'Length of the flowering stage (days)' - продолдительность цветения в днях
'Building up of Harvest Index starting at flowering (days)' - продолжительность формирования урожая в днях
'Minimum effective rooting depth (m)' - минимальная глубина корней
'Maximum effective rooting depth (m)' - максимальная глубина корней


Русские соответсвия названий параметров культуры для калибровки по умолчанию:

'Soil water depletion factor for canopy expansion (p-exp) - Upper threshold'
Коэффициент регулирования роста растительного покрова при дефиците влаги — Верхний порог

'Soil water depletion factor for canopy expansion (p-exp) - Lower threshold'
Коэффициент регулирования роста растительного покрова при дефиците влаги — Нижний порог

'Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)'
Форм-фактор для коэффициента регулирования роста растительного покрова при дефиците влаги

'Soil water depletion fraction for stomatal control (p - sto) - Upper threshold'
Коэффициент реакции устьичного аппарата на дефицит влаги — Верхний порог

'Shape factor for water stress coefficient for stomatal control (0.0 = straight line)'
Форм-фактор для коэффициента реакции устьичного аппарата на дефицит влаги

'Soil water depletion factor for canopy senescence (p - sen) - Upper threshold'
Коэффициент регулирования раннего старения растений при дефиците влаги — Верхний порог

'Shape factor for water stress coefficient for canopy senescence (0.0 = straight line)'
Форм-фактор для коэффициента регулирования раннего старения растений при дефиците влаги

'Soil water depletion factor for pollination (p - pol) - Upper threshold'
Коэффициент регулирования опыления растений при дефиците влаги — Верхний порог

'Vol% for Anaerobiotic point (* (SAT - [vol%]) at which deficient aeration occurs *)'
Объемная влажность, вычитаемая из полной влагоемкости, при которой наступает дефицит аэрации

'Canopy growth coefficient (CGC): Increase in canopy cover (fraction soil cover per day)'
Коэффициент роста растительного покрова

'Canopy decline coefficient (CDC): Decrease in canopy cover (in fraction per day)'
Коэффициент уменьшения растительного покрова

'Reference Harvest Index (HIo) (%)'
Эталонный индекс урожая



Русские соответсвия названий для почвенного профиля (soil_df):
'horizon_number': [1, 2, 3, 4, 5], - номер слоя
'thickness': [0.50, 0.50, 0.50, 0.50, 0.50], - толщина слоя (м)
'sat': [46.0, 46.0, 46.0, 46.0, 46.0], - полная влагоемкость (%)
'fc': [29.0, 29.0, 29.0, 29.0, 29.0], - наименьшая влагоемкость (%)
'wp': [13.0, 13.0, 13.0, 13.0, 13.0], - влажность завядания (%)
'ksat': [1200.0, 1200.0, 1200.0, 1200.0, 1200.0], - коэффициент фильтрации (мм/день)
'penetrability': [100, 100, 100, 100, 100], - сопротивление пенетрации (100 - минимальное, 0 - максимальное), можно оставить параметр по умолчанию 
'gravel': [0, 0, 0, 0, 0]}) - количество гравия в %, можно оставить параметр по умолчанию


Русские соответсвия названий для начальной влажности почвы (swo_dfs):
'horizon_number': [1, 2, 3, 4, 5], - номер слоя
'thickness': [0.50, 0.50, 0.50, 0.50, 0.50] - толщина слоя
'wc': [29.00, 15.00, 10.00, 10.00, 10.00] - объемная влажность в слое (%)
'ec': [0.00, 0.00, 0.00, 0.00, 0.00]  - электропроводность (дСм/м), можно оставить параметр по умолчанию



