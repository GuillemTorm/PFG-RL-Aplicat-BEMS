"""Constants i registres per al backend de l'agent de entrenament."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from gymnasium.spaces import Discrete, MultiBinary, MultiDiscrete

from backend.common import ONE_YEAR_STEPS, PKG_DIR


POLICIES = {
    "PPO": ["MlpPolicy"],
    "A2C": ["MlpPolicy"],
    "DQN": ["MlpPolicy"],
    "SAC": ["MlpPolicy"],
    "TD3": ["MlpPolicy"],
    "DDPG": ["MlpPolicy"],
}
REWARD_CLASS_NAMES = (
    "LinearReward",
    "ExpReward",
    "HourlyLinearReward",
    "EnergyCostLinearReward",
    "EnergyCostHourlyReward",
    "NormalizedLinearReward",
    "BatteryHVACReward",
    "MultiZoneReward",
    "OccupancyMultiZoneReward",
    "MultiZoneHourlyReward",
    "MultiZoneEnergyCostReward",
    "MultiZoneEnergyCostHourlyReward",
    "MultiZoneBatteryHVACReward",
    "MultizoneEnergyCostBatteryHVACReward",
    "OccupiedHoursDiscomfortReward",
)

class RewardClassRegistry(Mapping[str, Any]):
    """Registre lazy de classes de recompensa exposades per Sinergym."""

    def __iter__(self) -> Iterator[str]:
        """Itera pels noms de recompenses disponibles sense carregar les classes."""
        return iter(REWARD_CLASS_NAMES)

    def __len__(self) -> int:
        """Retorna el nombre de recompenses registrades."""
        return len(REWARD_CLASS_NAMES)

    def __getitem__(self, reward_name: str) -> Any:
        """Resol una classe de recompensa pel seu nom registrat."""
        if reward_name not in REWARD_CLASS_NAMES:
            raise KeyError(reward_name)
        from backend.model_metadata import resolve_reward_class

        reward_cls = resolve_reward_class(reward_name)
        if reward_cls is None:
            raise KeyError(reward_name)
        return reward_cls


REWARD_CLASSES = RewardClassRegistry()

COST_REWARDS = {
    "EnergyCostLinearReward",
    "EnergyCostHourlyReward",
    "MultiZoneEnergyCostReward",
    "MultiZoneEnergyCostHourlyReward",
}
MULTIZONE_REWARDS = {
    "MultiZoneReward",
    "OccupancyMultiZoneReward",
    "MultiZoneHourlyReward",
    "MultiZoneEnergyCostReward",
    "MultiZoneEnergyCostHourlyReward",
    "MultiZoneBatteryHVACReward",
    "MultizoneEnergyCostBatteryHVACReward",
}
HOURLY_REWARDS = {
    "HourlyLinearReward",
    "EnergyCostHourlyReward",
    "MultiZoneHourlyReward",
    "MultiZoneEnergyCostHourlyReward",
    "OccupiedHoursDiscomfortReward",
}
BATTERY_REWARDS = {
    "BatteryHVACReward",
    "MultiZoneBatteryHVACReward",
    "MultizoneEnergyCostBatteryHVACReward",
}

DEFAULT_MINUTES_PER_STEP = int((365 * 24 * 60) / ONE_YEAR_STEPS)

TRAINING_RUNTIME_KEY = "training_runtime"
TRAINING_RESULT_KEY = "training_result"
TRAINING_ARTIFACTS_DIR_NAME = "trainings"
TRAINING_CONFIG_FILENAME = "training_config.json"
TRAINING_REPRO_SCRIPT_FILENAME = "train_reproduce.py"
DETAILED_HVAC_METERS = {
    "natural_gas_hvac": "NaturalGas:HVAC",
    "heating_electricity": "Heating:Electricity",
    "cooling_electricity": "Cooling:Electricity",
    "fans_electricity": "Fans:Electricity",
    "pumps_electricity": "Pumps:Electricity",
    "heat_rejection_electricity": "HeatRejection:Electricity",
    "humidifier_electricity": "Humidifier:Electricity",
    "heat_recovery_electricity": "HeatRecovery:Electricity",
}
JOULES_PER_KWH = 3_600_000.0

FIELD_HELP = {
    "env_id": "Entorn de Sinergym que vols entrenar. Defineix edifici, clima, observacións i controls.",
    "algo_name": "Algorisme de Stable Baselines3 que farà l'entrenament del model.",
    "policy_name": "Política o arquitectura base que farà servir l'algorisme.",
    "reward_name": "Funcio de recompensa que transforma l'estat de l'entorn en reward a cada pas.",
    "range_winter": "Rang de confort d'hivern en C. Sortir d'aquest rang penalitza la reward.",
    "range_summer": "Rang de confort d'estiu en C. Sortir d'aquest rang penalitza la reward.",
    "energy_weight": "Pes relatiu de l'energia dins de la reward. Més alt = més pes energètic. A OccupiedHoursDiscomfortReward aquest pes s'aplica a les hores ocupades.",
    "temperature_weight": "Pes del terme de confort en rewards amb cost. El pes de cost es calcula com 1 - energia - confort.",
    "lambda_energy": "Factor base d'escala de la penalització energètica.",
    "lambda_temperature": "Factor d'escala de la penalització de temperatura.",
    "grid_energy_weight": "Pes de la potencia importada de xarxa dins de les rewards amb bateria.",
    "battery_cycle_weight": "Pes del cicle de bateria: suma de potencia de carrega i descarrega.",
    "battery_loss_weight": "Pes de les perdues termiques de la bateria si l'entorn les exposa.",
    "simultaneous_battery_weight": "Pes extra per penalitzar carrega i descarrega simultanies.",
    "lambda_grid": "Factor d'escala de la penalitzacio per importacio de xarxa.",
    "lambda_battery": "Factor d'escala de les penalitzacions de bateria.",
    "summer_start_m": "Mes d'inici del periode d'estiu usat per la reward.",
    "summer_start_d": "Dia d'inici del periode d'estiu usat per la reward.",
    "summer_final_m": "Mes final del periode d'estiu usat per la reward.",
    "summer_final_d": "Dia final del periode d'estiu usat per la reward.",
    "lambda_energy_cost": "Factor d'escala del cost economic de l'energia dins de la reward.",
    "comfort_threshold": "Marge de desviacio acceptable respecte al setpoint en rewards multizona.",
    "range_comfort_hours": "Franja horaria en que el confort te més pes dins de la reward.",
    "occupied_hours": "Franja horaria considerada d'ocupacio. Dins d'aquesta franja es considera confort; fora d'ella la reward prioritza reduir consum.",
    "occupied_discomfort_multiplier": "Multiplicador aplicat a la penalització de confort durant les hores d'ocupacio.",
    "off_hours_energy_multiplier": "Multiplicador extra del terme energètic fora d'ocupacio. Més alt = menys consum nocturn i menys preconditioning.",
    "use_energy_cost": "Activa el càlcul del cost energètic amb el fitxer de preus seleccionat.",
    "use_file_logger": "Desa un CSV extra amb el cost estimat a cada pas.",
    "energy_cost_path": "Ruta del fitxer CSV amb els preus de l'energia que farà servir el wrapper de cost.",
    "file_logger_name": "Nom del fitxer CSV on es desa el cost pas a pas.",
    "datetime_wrapper": "Afegeix variables temporals com el mes, el dia i l'hora a l'observació.",
    "previous_wrapper": "Afegeix a l'observació els valors del pas anterior per a les variables seleccionades.",
    "previous_variables": "Variables de l'observació actual que es copiaran des del pas anterior.",
    "multi_obs_wrapper": "Construeix una observació amb diversos passos consecutius per donar context temporal a l'agent.",
    "multi_obs_n": "Nombre de finestres temporals consecutives que es conservaran a l'observació.",
    "multi_obs_flatten": "Si esta activat, la pila temporal es converteix en un vector pla.",
    "normalize_obs_wrapper": "Normalitza l'observació per estabilitzar l'entrenament de l'agent.",
    "normalize_obs_auto": "Actualitza automàticament la mitjana i la variància durant l'entrenament.",
    "normalize_obs_epsilon": "Petit valor de seguretat per evitar divisions per zero en la normalitzacio.",
    "normalize_obs_mean": "Fitxer opcional amb la mitjana precomputada de les observacións.",
    "normalize_obs_var": "Fitxer opcional amb la variància precomputada de les observacións.",
    "weather_forecast_wrapper": "Afegeix a l'observació una previsió meteorològica construida a partir del fitxer climàtic de l'entorn.",
    "weather_forecast_n": "Nombre de mostres futures de previsió que s'afegiran a cada observació.",
    "weather_forecast_delta": "Separacio en passos entre mostres consecutives de previsió.",
    "weather_forecast_columns": "Variables meteorològiques que es faràn servir per construir la previsió.",
    "delta_temp_wrapper": "Calcula diferencies entre temperatures mesurades i setpoints per simplificar el control.",
    "delta_temp_variables": "Variables de temperatura reals que es compararan amb els setpoints.",
    "delta_setpoint_variables": "Variables de consigna que es faràn servir de referència per calcular el delta.",
    "reduce_obs_wrapper": "Elimina variables de l'observació per reduir-ne la dimensio.",
    "reduced_observations": "Variables que s'exclouran de l'observació final.",
    "incremental_wrapper": "Transforma accións continues en increments limitats per variable.",
    "incremental_variables": "Variables d'acció que es controlaran de forma incremental.",
    "incremental_initial_value": "Valor inicial de la variable abans d'aplicar increments.",
    "incremental_delta": "Canvi maxim admissible respecte al valor actual de la variable.",
    "incremental_step": "Pas discret intern amb que es representen els increments.",
    "discrete_incremental_wrapper": "Transforma l'espai d'accións en decisións discretes d'augment, manténiment o reduccio.",
    "discrete_incremental_initial": "Valor inicial per a cada variable controlada en mode discret incremental.",
    "discrete_incremental_delta": "Canvi maxim que es pot acumular en mode discret incremental.",
    "discrete_incremental_step": "Mida del pas aplicat a cada decisió discreta.",
    "normalize_action": "Reescala l'espai d'accións continu a un rang fix per facilitar l'entrenament.",
    "learning_rate": "Velocitat d'aprenentatge del model. Massa alt pot fer l'entrenament inestable.",
    "n_steps": "Nombre de passos recollits abans de cada actualitzacio en PPO i A2C.",
    "timesteps_per_year": f"Nombre total de passos d'entrenament. Amb els valors per defecte, 1 step = {DEFAULT_MINUTES_PER_STEP} minuts i {ONE_YEAR_STEPS} steps = 1 any.",
    "start_training": "Inicia l'entrenament amb la configuració actual.",
    "stop_training": "Atura l'entrenament al final del bloc actual i desa l'estat parcial.",
}

DEFAULT_FORECAST_COLUMNS = [
    "Dry Bulb Temperature",
    "Relative Humidity",
    "Wind Direction",
    "Wind Speed",
    "Direct Normal Radiation",
    "Diffuse Horizontal Radiation",
]

PACKAGE_DATA_DIR = PKG_DIR / "data"
ENERGY_COST_DIR = PACKAGE_DATA_DIR / "energy_cost"

FIXED_WRAPPER_ROWS = [
    {"Wrapper": "Monitor", "Actiu": "Si", "Detall": "Sempre actiu"},
    {"Wrapper": "LoggerWrapper", "Actiu": "Si", "Detall": "Sempre actiu"},
    {"Wrapper": "CSVLogger", "Actiu": "Si", "Detall": "Sempre actiu"},
]

DISCRETE_ACTION_SPACES = (Discrete, MultiDiscrete, MultiBinary)
