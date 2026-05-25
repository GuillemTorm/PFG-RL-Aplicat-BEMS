"""Implementation of reward functions."""

import csv
import math
from datetime import datetime
from math import exp
from typing import Any, Dict, List, Optional, Tuple, Union

from sinergym.utils.constants import LOG_REWARD_LEVEL, YEAR
from sinergym.utils.logger import TerminalLogger


class BaseReward(object):

    logger = TerminalLogger().getLogger(name='REWARD',
                                        level=LOG_REWARD_LEVEL)

    def __init__(self):
        """
        Base reward class.

        All reward functions should inherit from this class.

        Args:
            env (Env): Gym environment.
        """

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Method for calculating the reward function."""
        raise NotImplementedError(
            "Reward class must have a `__call__` method.")


class LinearReward(BaseReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0
    ):
        """
        Linear reward function.

        It considers the energy consumption and the absolute difference to temperature comfort.

        .. math::
            R = - W * lambda_E * power - (1 - W) * lambda_T * (max(T - T_{low}, 0) + max(T_{up} - T, 0))

        Args:
            temperature_variables (List[str]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            energy_weight (float, optional): Weight given to the energy term. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
        """

        super().__init__()

        # Basic validations
        if not (0 <= energy_weight <= 1):
            self.logger.error(
                f'energy_weight must be between 0 and 1. Received: {energy_weight}')
            raise ValueError
        if not all(isinstance(v, str)
                   for v in temperature_variables + energy_variables):
            self.logger.error('All variable names must be strings.')
            raise TypeError

        # Name of the variables
        self.temp_names = temperature_variables
        self.energy_names = energy_variables

        # Reward parameters
        self.range_comfort_winter = range_comfort_winter
        self.range_comfort_summer = range_comfort_summer
        self.W_energy = energy_weight
        self.lambda_energy = lambda_energy
        self.lambda_temp = lambda_temperature

        # Summer period
        self.summer_start = summer_start  # (month, day)
        self.summer_final = summer_final  # (month, day)

        self.logger.info('Reward function initialized.')

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Calculate the reward function value based on observation data.

        Args:
            obs_dict (Dict[str, Any]): Dict with observation variable name (key) and observation variable value (value)

        Returns:
            Tuple[float, Dict[str, Any]]: Reward value and dictionary with their individual components.
        """

        # Energy calculation
        energy_values = self._get_energy_consumed(obs_dict)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        # Comfort violation calculation
        temp_violations = self._get_temperature_violation(obs_dict)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        # Weighted sum of both terms
        reward, energy_term, comfort_term = self._get_reward()

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'reward_weight': self.W_energy
        }

        return reward, reward_terms

    def _get_energy_consumed(self, obs_dict: Dict[str,
                                                  Any]) -> List[float]:
        """Calculate the energy consumed in the current observation.

        Args:
            obs_dict (Dict[str, Any]): Environment observation.

        Returns:
            List[float]: List with energy consumed in each energy variable.
        """
        return [obs_dict[v] for v in self.energy_names]

    def _get_temperature_violation(
            self, obs_dict: Dict[str, Any]) -> List[float]:
        """Calculate the temperature violation (ºC) in each observation's temperature variable.

        Returns:
            List[float]: List with temperature violation in each zone.
        """

        # Current datetime and summer period
        current_dt = datetime(
            YEAR, int(
                obs_dict['month']), int(
                obs_dict['day_of_month']))
        summer_start_date = datetime(YEAR, *self.summer_start)
        summer_final_date = datetime(YEAR, *self.summer_final)

        temp_range = self.range_comfort_summer if \
            summer_start_date <= current_dt <= summer_final_date else \
            self.range_comfort_winter

        temp_values = [obs_dict[v] for v in self.temp_names]

        return [max(temp_range[0] - T, 0, T - temp_range[1])
                for T in temp_values]

    def _get_reward(self) -> Tuple[float, ...]:
        """Compute the final reward value.

        Args:
            energy_penalty (float): Negative absolute energy penalty value.
            comfort_penalty (float): Negative absolute comfort penalty value.

        Returns:
            Tuple[float, ...]: Total reward calculated and reward terms.
        """
        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * \
            (1 - self.W_energy) * self.comfort_penalty
        reward = energy_term + comfort_term
        return reward, energy_term, comfort_term


class EnergyCostLinearReward(LinearReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        energy_cost_variables: List[str],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.4,
        temperature_weight: float = 0.4,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_energy_cost: float = 1.0
    ):
        """
        Linear reward function with the addition of the energy cost term.

        Considers energy consumption, absolute difference to thermal comfort and energy cost.

        .. math::
            R = - W_E * lambda_E * power - W_T * lambda_T * (max(T - T_{low}, 0) + max(T_{up} - T, 0)) - (1 - W_P - W_T) * lambda_EC * power_cost

        Args:
            temperature_variables (List[str]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer s-sum(exp(violation)
                    for violation in temp_violations if violation > 0)ession tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            energy_weight (float, optional): Weight given to the energy term. Defaults to 0.4.
            temperature_weight (float, optional): Weight given to the temperature term. Defaults to 0.4.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1.0.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
            lambda_energy_cost (flota, optional): Constant for removing dimensions from temperature(1/E). Defaults to 1.0.
        """

        super().__init__(
            temperature_variables,
            energy_variables,
            range_comfort_winter,
            range_comfort_summer,
            summer_start,
            summer_final,
            energy_weight,
            lambda_energy,
            lambda_temperature
        )

        self.energy_cost_names = energy_cost_variables
        self.W_temperature = temperature_weight
        self.lambda_energy_cost = lambda_energy_cost

        self.logger.info('Reward function initialized.')

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Calculate the reward function.

        Args:
            obs_dict (Dict[str, Any]): Dict with observation variable name (key) and observation variable value (value)

        Returns:
            Tuple[float, Dict[str, Any]]: Reward value and dictionary with their individual components.
        """
        # Energy calculation
        energy_values = self._get_energy_consumed(obs_dict)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        # Comfort violation calculation
        temp_violations = self._get_temperature_violation(obs_dict)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        # Energy cost calculation
        energy_cost_values = self._get_money_spent(obs_dict)
        self.total_energy_cost = sum(energy_cost_values)
        self.energy_cost_penalty = -self.total_energy_cost

        # Weighted sum of terms
        reward, energy_term, comfort_term, energy_cost_term = self._get_reward()

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_cost_term': energy_cost_term,
            'reward_energy_weight': self.W_energy,
            'reward_temperature_weight': self.W_temperature,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'energy_cost_penalty': self.energy_cost_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'money_spent': self.total_energy_cost
        }

        return reward, reward_terms

    def _get_money_spent(self, obs_dict: Dict[str,
                                              Any]) -> List[float]:
        """Calculate the total money spent in the current observation.

        Args:
            obs_dict (Dict[str, Any]): Environment observation.

        Returns:
            List[float]: List with money spent in each energy cost variable.
        """
        return [v for k, v in obs_dict.items() if k in self.energy_cost_names]

    def _get_reward(self) -> Tuple[float, ...]:
        """It calculates reward value using the negative absolute comfort, energy penalty and energy cost penalty calculates previously.

        Returns:
            Tuple[float, ...]: Total reward calculated, reward term for energy, reward term for comfort and reward term for energy cost.
        """
        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * \
            self.W_temperature * self.comfort_penalty
        energy_cost_term = self.lambda_energy_cost * \
            (1 - self.W_energy - self.W_temperature) * self.energy_cost_penalty

        reward = energy_term + comfort_term + energy_cost_term
        return reward, energy_term, comfort_term, energy_cost_term


class ExpReward(LinearReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0
    ):
        """
        Reward considering exponential absolute difference to temperature comfort.

        .. math::
            R = - W * lambda_E * power - (1 - W) * lambda_T * exp( (max(T - T_{low}, 0) + max(T_{up} - T, 0)) )

        Args:
            temperature_variables (List[str]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            energy_weight (float, optional): Weight given to the energy term. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
        """

        super().__init__(
            temperature_variables,
            energy_variables,
            range_comfort_winter,
            range_comfort_summer,
            summer_start,
            summer_final,
            energy_weight,
            lambda_energy,
            lambda_temperature
        )

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Calculate the reward function value based on observation data.

        Args:
            obs_dict (Dict[str, Any]): Dict with observation variable name (key) and observation variable value (value)

        Returns:
            Tuple[float, Dict[str, Any]]: Reward value and dictionary with their individual components.
        """

        # Energy calculation
        energy_values = self._get_energy_consumed(obs_dict)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        # Comfort violation calculation
        temp_violations = self._get_temperature_violation(obs_dict)
        self.total_temp_violation = sum(temp_violations)
        # Exponential Penalty
        self.comfort_penalty = -sum(exp(violation)
                                    for violation in temp_violations if violation > 0)

        # Weighted sum of both terms
        reward, energy_term, comfort_term = self._get_reward()

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'reward_weight': self.W_energy
        }

        return reward, reward_terms


class HourlyLinearReward(LinearReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        default_energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        range_comfort_hours: tuple = (9, 19),
    ):
        """
        Linear reward function with a time-dependent weight for consumption and energy terms.

        Args:
            temperature_variables (List[str]]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            default_energy_weight (float, optional): Default weight given to the energy term when thermal comfort is considered. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
            range_comfort_hours (tuple, optional): Hours where thermal comfort is considered. Defaults to (9, 19).
        """

        super(HourlyLinearReward, self).__init__(
            temperature_variables,
            energy_variables,
            range_comfort_winter,
            range_comfort_summer,
            summer_start,
            summer_final,
            default_energy_weight,
            lambda_energy,
            lambda_temperature
        )

        # Reward parameters
        self.range_comfort_hours = range_comfort_hours
        self.default_energy_weight = default_energy_weight

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Calculate the reward function.

        Args:
            obs_dict (Dict[str, Any]): Dict with observation variable name (key) and observation variable value (value)

        Returns:
            Tuple[float, Dict[str, Any]]: Reward value and dictionary with their individual components.
        """
        # Energy calculation
        energy_values = self._get_energy_consumed(obs_dict)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        # Comfort violation calculation
        temp_violations = self._get_temperature_violation(obs_dict)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        # Determine reward weight depending on the hour
        self.W_energy = self.default_energy_weight if self.range_comfort_hours[
            0] <= obs_dict['hour'] <= self.range_comfort_hours[1] else 1.0

        # Weighted sum of both terms
        reward, energy_term, comfort_term = self._get_reward()

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'reward_weight': self.W_energy
        }

        return reward, reward_terms


class NormalizedLinearReward(LinearReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.5,
        max_energy_penalty: float = 8,
        max_comfort_penalty: float = 12,
    ):
        """
        Linear reward function with a time-dependent weight for consumption and energy terms.

        Args:
            temperature_variables (List[str]]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            energy_weight (float, optional): Default weight given to the energy term when thermal comfort is considered. Defaults to 0.5.
            max_energy_penalty (float, optional): Maximum energy penalty value. Defaults to 8.
            max_comfort_penalty (float, optional): Maximum comfort penalty value. Defaults to 12.
        """

        super().__init__(
            temperature_variables,
            energy_variables,
            range_comfort_winter,
            range_comfort_summer,
            summer_start,
            summer_final,
            energy_weight
        )

        # Reward parameters
        self.max_energy_penalty = max_energy_penalty
        self.max_comfort_penalty = max_comfort_penalty

    def _get_reward(self) -> Tuple[float, ...]:
        """It calculates reward value using energy consumption and grades of temperature out of comfort range. Aplying normalization

        Returns:
            Tuple[float, ...]: total reward calculated, reward term for energy and reward term for comfort.
        """
        # Update max energy and comfort
        self.max_energy_penalty = max(
            self.max_energy_penalty, self.energy_penalty)
        self.max_comfort_penalty = max(
            self.max_comfort_penalty, self.comfort_penalty)

        # Calculate normalization
        energy_norm = self.energy_penalty / \
            self.max_energy_penalty if self.max_energy_penalty else 0
        comfort_norm = self.comfort_penalty / \
            self.max_comfort_penalty if self.max_comfort_penalty else 0

        # Calculate reward terms with norm values
        energy_term = self.W_energy * energy_norm
        comfort_term = (1 - self.W_energy) * comfort_norm
        reward = energy_term + comfort_term

        return reward, energy_term, comfort_term


class MultiZoneReward(BaseReward):

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, str],
        comfort_threshold: float = 0.5,
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0
    ):
        """
        A linear reward function for environments with different comfort ranges in each zone. Instead of having
        a fixed and common comfort range for the entire building, each zone has its own comfort range, which is
        directly obtained from the setpoints established in the building. This function is designed for buildings
        where temperature setpoints are not controlled directly but rather used as targets to be achieved, while
        other actuators are controlled to reach these setpoints. A setpoint observation variable can be assigned
        per zone if it is available in the specific building. It is also possible to assign the same setpoint
        variable to multiple air temperature zones.

        Args:
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            temperature_and_setpoints_conf (Dict[str, str]): Dictionary with the temperature variable name (key) and the setpoint variable name (value) of the observation space.
            comfort_threshold (float, optional): Comfort threshold for temperature range (+/-). Defaults to 0.5.
            energy_weight (float, optional): Weight given to the energy term. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
        """

        super().__init__()

        # Name of the variables
        self.energy_names = energy_variables
        self.comfort_configuration = temperature_and_setpoints_conf
        self.comfort_threshold = comfort_threshold

        # Reward parameters
        self.W_energy = energy_weight
        self.lambda_energy = lambda_energy
        self.lambda_temp = lambda_temperature
        self.comfort_ranges = {}

        self.logger.info('Reward function initialized.')

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Calculate the reward function value based on observation data.

        Args:
            obs_dict (Dict[str, Any]): Dict with observation variable name (key) and observation variable value (value)

        Returns:
            Tuple[float, Dict[str, Any]]: Reward value and dictionary with their individual components.
        """

        # Energy calculation
        energy_values = self._get_energy_consumed(obs_dict)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        # Comfort violation calculation
        temp_violations = self._get_temperature_violation(obs_dict)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        # Weighted sum of both terms
        reward, energy_term, comfort_term = self._get_reward()

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'reward_weight': self.W_energy,
            'comfort_threshold': self.comfort_threshold
        }

        return reward, reward_terms

    def _get_energy_consumed(self, obs_dict: Dict[str,
                                                  Any]) -> List[float]:
        """Calculate the energy consumed in the current observation.

        Args:
            obs_dict (Dict[str, Any]): Environment observation.

        Returns:
            List[float]: List with energy consumed in each energy variable.
        """
        return [obs_dict[v] for v in self.energy_names]

    def _get_temperature_violation(
            self, obs_dict: Dict[str, Any]) -> List[float]:
        """Calculate the total temperature violation (ºC) in the current observation.

        Returns:
           List[float]: List with temperature violation (ºC) in each zone.
        """
        # Calculate current comfort range for each zone
        self._get_comfort_ranges(obs_dict)

        temp_violations = [
            max(0, min(abs(T - comfort_range[0]), abs(T - comfort_range[1])))
            if T < comfort_range[0] or T > comfort_range[1] else 0
            for temp_var, comfort_range in self.comfort_ranges.items()
            if (T := obs_dict[temp_var])
        ]

        return temp_violations

    def _get_comfort_ranges(
            self, obs_dict: Dict[str, Any]):
        """Calculate the comfort range for each zone in the current observation.

        Returns:
            Dict[str, Tuple[float, float]]: Comfort range for each zone.
        """
        # Calculate current comfort range for each zone
        self.comfort_ranges = {
            temp_var: (setpoint - self.comfort_threshold, setpoint + self.comfort_threshold)
            for temp_var, setpoint_var in self.comfort_configuration.items()
            if (setpoint := obs_dict[setpoint_var]) is not None
        }

    def _get_reward(self) -> Tuple[float, ...]:
        """Compute the final reward value.

        Args:
            energy_penalty (float): Negative absolute energy penalty value.
            comfort_penalty (float): Negative absolute comfort penalty value.

        Returns:
            Tuple[float, ...]: Total reward calculated and reward terms.
        """
        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * \
            (1 - self.W_energy) * self.comfort_penalty
        reward = energy_term + comfort_term
        return reward, energy_term, comfort_term


class OccupancyMultiZoneReward(MultiZoneReward):
    """Multi-zone reward that penalizes comfort only in occupied zones."""

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, str],
        occupancy_variables_conf: Dict[str, str],
        comfort_threshold: float = 0.5,
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        occupancy_threshold: float = 0.0,
    ):
        super().__init__(
            energy_variables=energy_variables,
            temperature_and_setpoints_conf=temperature_and_setpoints_conf,
            comfort_threshold=comfort_threshold,
            energy_weight=energy_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
        )
        self.occupancy_configuration = dict(occupancy_variables_conf or {})
        self.occupancy_threshold = float(occupancy_threshold)
        self.zone_occupancy = {}
        self.zone_temperature_violations = {}
        self.occupied_zone_count = 0
        self.total_occupancy = 0.0

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        energy_values = self._get_energy_consumed(obs_dict)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        temp_violations = self._get_temperature_violation(obs_dict)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        reward, energy_term, comfort_term = self._get_reward()

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'reward_weight': self.W_energy,
            'comfort_threshold': self.comfort_threshold,
            'occupied_zone_count': self.occupied_zone_count,
            'total_occupancy': self.total_occupancy,
            'occupancy_threshold': self.occupancy_threshold,
            'comfort_active': 1.0 if self.occupied_zone_count > 0 else 0.0,
        }

        return reward, reward_terms

    def _get_temperature_violation(
            self, obs_dict: Dict[str, Any]) -> List[float]:
        self._get_comfort_ranges(obs_dict)
        self.zone_occupancy = {}
        self.zone_temperature_violations = {}
        self.occupied_zone_count = 0
        self.total_occupancy = 0.0

        temp_violations = []
        for temp_var, comfort_range in self.comfort_ranges.items():
            occupancy_var = self.occupancy_configuration.get(temp_var)
            try:
                occupancy = float(obs_dict.get(occupancy_var, 0.0)) if occupancy_var else 0.0
            except (TypeError, ValueError):
                occupancy = 0.0

            self.zone_occupancy[temp_var] = occupancy
            self.total_occupancy += max(0.0, occupancy)

            if occupancy <= self.occupancy_threshold:
                violation = 0.0
            else:
                self.occupied_zone_count += 1
                temp_value = obs_dict.get(temp_var)
                if temp_value is None:
                    violation = 0.0
                else:
                    temp_value = float(temp_value)
                    lower, upper = comfort_range
                    if temp_value < lower:
                        violation = lower - temp_value
                    elif temp_value > upper:
                        violation = temp_value - upper
                    else:
                        violation = 0.0

            self.zone_temperature_violations[temp_var] = violation
            temp_violations.append(violation)

        return temp_violations

class EnergyCostHourlyLinearReward(LinearReward):
    """
    Reward amb tres termes: energia, confort i cost (€/kWh per hora).
    - El cost pot venir d'un CSV (energy_cost_path) o directament de l'observació
      (energy_cost_variables).
    - Si s'especifica seconds_per_step, converteix W → € PER PAS (kWh del pas).
      Si no, el terme de cost és una tarifa per hora (€/h, 'rate').

    Fórmula:
        R = λE * WE * (-energia_W) + λT * WT * (-violació_confort_ºC) + λC * WC * (-cost_€)

    (WE, WT, WC) = weights_comfort_hours si hour ∈ [h0, h1], sinó weights_off_hours.
    """

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[float, float],
        range_comfort_summer: Tuple[float, float],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        range_comfort_hours: Tuple[int, int] = (9, 19),
        weights_comfort_hours: Tuple[float, float, float] = (0.4, 0.4, 0.2),
        weights_off_hours:     Tuple[float, float, float] = (0.7, 0.0, 0.3),
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_energy_cost: float = 1.0,
        *,
        energy_cost_path: Optional[str] = None,            # CSV amb tarifa €/kWh/hora
        energy_cost_variables: Optional[List[str]] = None, # valors de cost ja a l'obs
        seconds_per_step: Optional[float] = None,          # p.ex. 900 segons (15 min)
        default_price_eur_per_kwh: float = 0.15,
        # --- DEBUG ---
        debug: bool = False,
        debug_every_n: int = 1,     # log cada n passos (1 = cada pas)
        round_digits: int = 4,      # decimals al log
    ):
        # Inicialització base (reutilitza utilitats d'energia i confort)
        super().__init__(
            temperature_variables=temperature_variables,
            energy_variables=energy_variables,
            range_comfort_winter=range_comfort_winter,
            range_comfort_summer=range_comfort_summer,
            summer_start=summer_start,
            summer_final=summer_final,
            energy_weight=weights_comfort_hours[0],
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
        )

        # Desa λ com a atributs propis (el pare no garanteix aquests noms)
        self.lambda_energy = float(lambda_energy)
        self.lambda_temperature = float(lambda_temperature)
        self.lambda_energy_cost = float(lambda_energy_cost)

        # Validació de pesos
        for w in [*weights_comfort_hours, *weights_off_hours]:
            if not (0.0 <= float(w) <= 1.0):
                raise ValueError("Weights must be in [0,1]")
        if abs(sum(weights_comfort_hours) - 1.0) > 1e-6:
            raise ValueError("weights_comfort_hours must sum to 1")
        if abs(sum(weights_off_hours) - 1.0) > 1e-6:
            raise ValueError("weights_off_hours must sum to 1")
        self.weights_comfort_hours = tuple(map(float, weights_comfort_hours))
        self.weights_off_hours = tuple(map(float, weights_off_hours))
        self.range_comfort_hours = range_comfort_hours

        # Config cost
        self.seconds_per_step = float(seconds_per_step) if seconds_per_step else None
        self.energy_cost_names = list(energy_cost_variables) if energy_cost_variables else []
        self.default_price = float(default_price_eur_per_kwh)
        self._tariff: Optional[Dict[Tuple[int, int, int], float]] = None  # (m,d,h)->€/kWh

        if energy_cost_path:
            try:
                self._tariff = self._load_tariff_csv(energy_cost_path)
                self.logger.info(
                    f"Tarifa carregada de {energy_cost_path} ({len(self._tariff)} registres)."
                )
            except Exception as e:
                self.logger.warning(
                    f"No s'ha pogut llegir la tarifa de {energy_cost_path}: {e}. Faré servir preu per defecte."
                )

        # DEBUG
        self.debug = bool(debug)
        self.debug_every_n = max(1, int(debug_every_n))
        self._step_i = 0
        self._rd = int(round_digits)

        self.logger.info("EnergyCostHourlyLinearReward inicialitzada.")

    # ---------- Helpers de tarifa ----------
    def _load_tariff_csv(self, path: str) -> Dict[Tuple[int, int, int], float]:
        """Llegeix un CSV amb columnes de data/hora i preu i construeix (m,d,h)->€/kWh."""
        tariff: Dict[Tuple[int, int, int], float] = {}
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cols = [c or "" for c in (reader.fieldnames or [])]
            lower = [c.lower() for c in cols]

            # Detecta columnes
            price_col = None
            for c in cols:
                cl = c.lower()
                if "price" in cl or "€/kwh" in cl or "eur/kwh" in cl or "kwh" in cl:
                    price_col = c
                    break
            has_dt = any(k in lower for k in ["datetime", "timestamp", "date"])
            dt_col = None
            if has_dt:
                for cand in ["datetime", "timestamp", "date"]:
                    if cand in lower:
                        dt_col = cols[lower.index(cand)]
                        break
            month_col = next((cols[i] for i, c in enumerate(lower) if c in ("month", "mes")), None)
            day_col   = next((cols[i] for i, c in enumerate(lower) if c in ("day", "dia")), None)
            hour_col  = next((cols[i] for i, c in enumerate(lower) if "hour" in c or "hora" in c), None)

            if not price_col:
                raise ValueError("No puc identificar la columna de preu (€/kWh) al CSV")

            for row in reader:
                try:
                    if dt_col:
                        dt = self._parse_any_date(str(row[dt_col]).strip())
                        key = (dt.month, dt.day, dt.hour)
                    else:
                        m = int(row[month_col]) if month_col and row.get(month_col) else None
                        d = int(row[day_col])   if day_col   and row.get(day_col)   else None
                        h = int(row[hour_col])  if hour_col  and row.get(hour_col)  else None
                        if None in (m, d, h):
                            continue
                        key = (m, d, h)
                    price = float(str(row[price_col]).replace(",", "."))
                    tariff[key] = price
                except Exception:
                    continue  # línia no interpretable → s'ignora
        return tariff

    @staticmethod
    def _parse_any_date(s: str) -> datetime:
        for fmt in (
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%d/%m/%Y %H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s + " 00:00", fmt + " %H:%M")
            except ValueError:
                pass
        return datetime(2023, 1, 1, 0, 0)  # fallback robust

    def _price_eur_per_kwh(self, obs: Dict[str, Any]) -> float:
        h = self._recover_hour(obs)
        m = self._recover_month(obs)
        d = int(obs.get("day_of_month", 15))
        if self._tariff and None not in (m, d, h):
            return float(self._tariff.get((m, d, h), self.default_price))
        return self.default_price

    # ---------- Robustesa amb wrappers ----------
    @staticmethod
    def _recover_hour(obs: Dict[str, Any]) -> Optional[int]:
        if "hour" in obs and obs["hour"] is not None:
            return int(obs["hour"])
        if "hour_sin" in obs and "hour_cos" in obs:
            ang = math.atan2(float(obs["hour_sin"]), float(obs["hour_cos"]))
            if ang < 0:
                ang += 2 * math.pi
            return int(round(ang * 24.0 / (2 * math.pi))) % 24
        return None

    @staticmethod
    def _recover_month(obs: Dict[str, Any]) -> Optional[int]:
        if "month" in obs and obs["month"] is not None:
            return int(obs["month"])
        if "month_sin" in obs and "month_cos" in obs:
            ang = math.atan2(float(obs["month_sin"]), float(obs["month_cos"]))
            if ang < 0:
                ang += 2 * math.pi
            return int(round(ang * 12.0 / (2 * math.pi))) % 12 + 1
        return None

    def _patch_datetime(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        obs2 = dict(obs)
        obs2.setdefault("day_of_month", 15)
        if "hour" not in obs2 or obs2["hour"] is None:
            h = self._recover_hour(obs2)
            if h is not None:
                obs2["hour"] = h
        if "month" not in obs2 or obs2["month"] is None:
            m = self._recover_month(obs2)
            if m is not None:
                obs2["month"] = m
        return obs2

    # ---------- Cost des de l'observació ----------
    def _get_money_spent_from_obs(self, obs: Dict[str, Any]) -> float:
        total = 0.0
        for v in self.energy_cost_names:
            if v in obs and obs[v] is not None:
                try:
                    total += float(obs[v])
                except Exception:
                    pass
            else:
                if self.energy_cost_names:
                    self.logger.warning(
                        f"[EnergyCostHourlyLinearReward] Variable de cost absent: '{v}' (es pren 0)."
                    )
        return total

    # ---------- Càlcul principal ----------
    def __call__(self, obs_dict: Dict[str, Any]):
        obs = self._patch_datetime(obs_dict)

        # Energia (W) i confort (∑ violacions |ΔT|)
        total_power_W = float(sum(self._get_energy_consumed(obs)))
        temp_violation = float(sum(self._get_temperature_violation(obs)))

        energy_penalty = -total_power_W
        comfort_penalty = -temp_violation

        # Cost (€): de l'obs o de la tarifa CSV + pas temporal
        cost_from_obs = self._get_money_spent_from_obs(obs)
        if cost_from_obs > 0.0:
            money_spent = cost_from_obs               # suposem ja és € per pas
            price_used = None
        else:
            price = self._price_eur_per_kwh(obs)      # €/kWh
            kW = max(total_power_W, 0.0) / 1000.0
            if self.seconds_per_step:
                money_spent = kW * price * (self.seconds_per_step / 3600.0)
            else:
                money_spent = kW * price              # €/h (rate)
            price_used = price

        energy_cost_penalty = -money_spent

        # Pesos segons franja horària
        hour = self._recover_hour(obs)
        if hour is not None and self.range_comfort_hours[0] <= hour <= self.range_comfort_hours[1]:
            WE, WT, WC = self.weights_comfort_hours
        else:
            WE, WT, WC = self.weights_off_hours

        # Termes i reward final
        energy_term  = self.lambda_energy       * WE * energy_penalty
        comfort_term = self.lambda_temperature  * WT * comfort_penalty
        cost_term    = self.lambda_energy_cost  * WC * energy_cost_penalty
        reward = energy_term + comfort_term + cost_term

        terms = {
            # claus esperades pel LoggerWrapper/CSVLogger:
            "comfort_penalty": comfort_penalty,
            "energy_penalty": energy_penalty,
            "total_temperature_violation": temp_violation,
            "total_power_demand": total_power_W,
            # info addicional:
            "energy_term": energy_term,
            "comfort_term": comfort_term,
            "energy_cost_term": cost_term,
            "energy_cost_penalty": energy_cost_penalty,
            "reward_weights": {"energy": WE, "temperature": WT, "cost": WC},
            "money_spent": money_spent,
        }
        if price_used is not None:
            terms["price_eur_per_kwh"] = price_used

        return reward, terms


def _is_hour_in_window(hour: Optional[int], hour_window: Tuple[int, int]) -> bool:
    if hour is None:
        return False
    start_hour, end_hour = map(int, hour_window)
    if start_hour <= end_hour:
        return start_hour <= hour <= end_hour
    return hour >= start_hour or hour <= end_hour


def _parse_tariff_datetime(value: str) -> datetime:
    for fmt in (
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value + " 00:00", fmt + " %H:%M")
        except ValueError:
            pass
    return datetime(2023, 1, 1, 0, 0)


def _load_energy_cost_tariff(path: str) -> Dict[Tuple[int, int, int], float]:
    tariff: Dict[Tuple[int, int, int], float] = {}
    with open(path, "r", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        columns = [column or "" for column in (reader.fieldnames or [])]
        lower_columns = [column.lower() for column in columns]

        price_column = None
        for column in columns:
            column_lower = column.lower()
            if "price" in column_lower or "eur/kwh" in column_lower or "kwh" in column_lower:
                price_column = column
                break

        datetime_column = None
        for candidate in ["datetime", "timestamp", "date"]:
            if candidate in lower_columns:
                datetime_column = columns[lower_columns.index(candidate)]
                break

        month_column = next((columns[index] for index, value in enumerate(lower_columns) if value in ("month", "mes")), None)
        day_column = next((columns[index] for index, value in enumerate(lower_columns) if value in ("day", "dia")), None)
        hour_column = next((columns[index] for index, value in enumerate(lower_columns) if "hour" in value or "hora" in value), None)

        if not price_column:
            raise ValueError("No puc identificar la columna de preu (EUR/kWh) al CSV.")

        for row in reader:
            try:
                if datetime_column:
                    timestamp = _parse_tariff_datetime(str(row[datetime_column]).strip())
                    key = (timestamp.month, timestamp.day, timestamp.hour)
                else:
                    month = int(row[month_column]) if month_column and row.get(month_column) else None
                    day = int(row[day_column]) if day_column and row.get(day_column) else None
                    hour = int(row[hour_column]) if hour_column and row.get(hour_column) else None
                    if None in (month, day, hour):
                        continue
                    key = (month, day, hour)
                tariff[key] = float(str(row[price_column]).replace(",", "."))
            except Exception:
                continue
    return tariff


def _recover_hour_from_obs(obs_dict: Dict[str, Any]) -> Optional[int]:
    if "hour" in obs_dict and obs_dict["hour"] is not None:
        return int(obs_dict["hour"])
    if "hour_sin" in obs_dict and "hour_cos" in obs_dict:
        angle = math.atan2(float(obs_dict["hour_sin"]), float(obs_dict["hour_cos"]))
        if angle < 0:
            angle += 2 * math.pi
        return int(round(angle * 24.0 / (2 * math.pi))) % 24
    return None


def _recover_month_from_obs(obs_dict: Dict[str, Any]) -> Optional[int]:
    if "month" in obs_dict and obs_dict["month"] is not None:
        return int(obs_dict["month"])
    if "month_sin" in obs_dict and "month_cos" in obs_dict:
        angle = math.atan2(float(obs_dict["month_sin"]), float(obs_dict["month_cos"]))
        if angle < 0:
            angle += 2 * math.pi
        return int(round(angle * 12.0 / (2 * math.pi))) % 12 + 1
    return None


def _patch_datetime_obs(obs_dict: Dict[str, Any]) -> Dict[str, Any]:
    patched_obs = dict(obs_dict)
    patched_obs.setdefault("day_of_month", 15)
    if "hour" not in patched_obs or patched_obs["hour"] is None:
        recovered_hour = _recover_hour_from_obs(patched_obs)
        if recovered_hour is not None:
            patched_obs["hour"] = recovered_hour
    if "month" not in patched_obs or patched_obs["month"] is None:
        recovered_month = _recover_month_from_obs(patched_obs)
        if recovered_month is not None:
            patched_obs["month"] = recovered_month
    return patched_obs


def _get_energy_cost_from_obs(
    obs_dict: Dict[str, Any],
    energy_cost_names: List[str],
    logger,
    label: str,
) -> float:
    total_cost = 0.0
    for variable_name in energy_cost_names:
        if variable_name in obs_dict and obs_dict[variable_name] is not None:
            try:
                total_cost += float(obs_dict[variable_name])
            except Exception:
                pass
        elif energy_cost_names:
            logger.warning(
                f"[{label}] Variable de cost absent: '{variable_name}' (es pren 0)."
            )
    return total_cost


def _resolve_energy_cost(
    obs_dict: Dict[str, Any],
    total_power_watts: float,
    energy_cost_names: List[str],
    tariff: Optional[Dict[Tuple[int, int, int], float]],
    default_price_eur_per_kwh: float,
    seconds_per_step: Optional[float],
    logger,
    label: str,
) -> Tuple[float, Optional[float]]:
    money_spent = _get_energy_cost_from_obs(obs_dict, energy_cost_names, logger, label)
    if money_spent > 0.0:
        return float(money_spent), None

    hour = _recover_hour_from_obs(obs_dict)
    month = _recover_month_from_obs(obs_dict)
    day = int(obs_dict.get("day_of_month", 15))
    price_used = float(default_price_eur_per_kwh)
    if tariff and None not in (month, day, hour):
        price_used = float(tariff.get((month, day, hour), price_used))

    power_kw = max(float(total_power_watts), 0.0) / 1000.0
    if seconds_per_step:
        money_spent = power_kw * price_used * (float(seconds_per_step) / 3600.0)
    else:
        money_spent = power_kw * price_used
    return float(money_spent), price_used


def _validate_three_term_weights(
    energy_weight: float,
    temperature_weight: float,
) -> float:
    if not (0.0 <= float(energy_weight) <= 1.0):
        raise ValueError("energy_weight must be between 0 and 1.")
    if not (0.0 <= float(temperature_weight) <= 1.0):
        raise ValueError("temperature_weight must be between 0 and 1.")
    cost_weight = 1.0 - float(energy_weight) - float(temperature_weight)
    if cost_weight < -1e-9:
        raise ValueError("energy_weight + temperature_weight must be <= 1.")
    return max(0.0, float(cost_weight))


def _as_variable_list(
    variable_names: Optional[Union[str, List[str], Tuple[str, ...]]]
) -> List[str]:
    if not variable_names:
        return []
    if isinstance(variable_names, str):
        return [variable_names]
    return [str(variable_name) for variable_name in variable_names if variable_name]


def _safe_obs_value(
    obs_dict: Dict[str, Any],
    variable_name: Optional[str],
    default: Any = 0.0,
) -> Any:
    if not variable_name:
        return default
    try:
        value = float(obs_dict[variable_name])
    except (KeyError, TypeError, ValueError):
        return default
    if not math.isfinite(value):
        return default
    return value


def _sum_observation_values(
    obs_dict: Dict[str, Any],
    variable_names: Optional[Union[str, List[str], Tuple[str, ...]]],
    *,
    positive_only: bool = True,
) -> float:
    total = 0.0
    for variable_name in _as_variable_list(variable_names):
        value = _safe_obs_value(obs_dict, variable_name, 0.0)
        total += max(value, 0.0) if positive_only else value
    return float(total)


def _validate_unit_weight(name: str, value: float) -> None:
    if not (0.0 <= float(value) <= 1.0):
        raise ValueError(f"{name} must be between 0 and 1.")


def _validate_non_negative(name: str, value: float) -> None:
    if float(value) < 0.0:
        raise ValueError(f"{name} must be >= 0.")


def _get_battery_hvac_components(
    obs_dict: Dict[str, Any],
    grid_energy_variables: Optional[List[str]],
    battery_charge_variables: Optional[List[str]],
    battery_discharge_variables: Optional[List[str]],
    battery_loss_variables: Optional[List[str]],
) -> Dict[str, float]:
    grid_power = _sum_observation_values(
        obs_dict, grid_energy_variables, positive_only=True
    )
    charge_power = _sum_observation_values(
        obs_dict, battery_charge_variables, positive_only=True
    )
    discharge_power = _sum_observation_values(
        obs_dict, battery_discharge_variables, positive_only=True
    )
    battery_loss = _sum_observation_values(
        obs_dict, battery_loss_variables, positive_only=True
    )
    return {
        "grid_power": grid_power,
        "battery_charge_power": charge_power,
        "battery_discharge_power": discharge_power,
        "battery_cycle_power": charge_power + discharge_power,
        "battery_loss_power": battery_loss,
        "simultaneous_battery_power": min(charge_power, discharge_power),
    }


class EnergyCostHourlyReward(EnergyCostHourlyLinearReward):
    """Hourly reward with energy, comfort and energy-cost terms using simple scalar weights."""

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[float, float],
        range_comfort_summer: Tuple[float, float],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        range_comfort_hours: Tuple[int, int] = (9, 19),
        energy_weight: float = 0.4,
        temperature_weight: float = 0.4,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_energy_cost: float = 1.0,
        *,
        energy_cost_path: Optional[str] = None,
        energy_cost_variables: Optional[List[str]] = None,
        seconds_per_step: Optional[float] = None,
        default_price_eur_per_kwh: float = 0.15,
    ):
        cost_weight = _validate_three_term_weights(energy_weight, temperature_weight)
        comfort_weights = (
            float(energy_weight),
            float(temperature_weight),
            float(cost_weight),
        )
        off_hours_total = float(energy_weight) + float(cost_weight)
        if off_hours_total > 0.0:
            off_weights = (
                float(energy_weight) / off_hours_total,
                0.0,
                float(cost_weight) / off_hours_total,
            )
        else:
            off_weights = (1.0, 0.0, 0.0)

        super().__init__(
            temperature_variables=temperature_variables,
            energy_variables=energy_variables,
            range_comfort_winter=range_comfort_winter,
            range_comfort_summer=range_comfort_summer,
            summer_start=summer_start,
            summer_final=summer_final,
            range_comfort_hours=range_comfort_hours,
            weights_comfort_hours=comfort_weights,
            weights_off_hours=off_weights,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
            lambda_energy_cost=lambda_energy_cost,
            energy_cost_path=energy_cost_path,
            energy_cost_variables=energy_cost_variables,
            seconds_per_step=seconds_per_step,
            default_price_eur_per_kwh=default_price_eur_per_kwh,
        )
        self.W_energy = float(energy_weight)
        self.W_temperature = float(temperature_weight)


class MultiZoneHourlyReward(MultiZoneReward):
    """Multi-zone reward where comfort is only active during selected hours."""

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, str],
        comfort_threshold: float = 0.5,
        default_energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        range_comfort_hours: Tuple[int, int] = (9, 19),
    ):
        super().__init__(
            energy_variables=energy_variables,
            temperature_and_setpoints_conf=temperature_and_setpoints_conf,
            comfort_threshold=comfort_threshold,
            energy_weight=default_energy_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
        )
        self.default_energy_weight = float(default_energy_weight)
        self.range_comfort_hours = tuple(map(int, range_comfort_hours))

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        obs = _patch_datetime_obs(obs_dict)

        energy_values = self._get_energy_consumed(obs)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        temp_violations = self._get_temperature_violation(obs)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        hour = _recover_hour_from_obs(obs)
        comfort_active = _is_hour_in_window(hour, self.range_comfort_hours)
        self.W_energy = self.default_energy_weight if comfort_active else 1.0

        reward, energy_term, comfort_term = self._get_reward()
        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'reward_weight': self.W_energy,
            'comfort_threshold': self.comfort_threshold,
            'comfort_active': 1.0 if comfort_active else 0.0,
            'hour': hour,
        }
        return reward, reward_terms


class MultiZoneEnergyCostReward(MultiZoneReward):
    """Multi-zone reward with energy, comfort and energy-cost terms."""

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, str],
        comfort_threshold: float = 0.5,
        energy_weight: float = 0.4,
        temperature_weight: float = 0.4,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_energy_cost: float = 1.0,
        *,
        energy_cost_path: Optional[str] = None,
        energy_cost_variables: Optional[List[str]] = None,
        seconds_per_step: Optional[float] = None,
        default_price_eur_per_kwh: float = 0.15,
    ):
        cost_weight = _validate_three_term_weights(energy_weight, temperature_weight)
        super().__init__(
            energy_variables=energy_variables,
            temperature_and_setpoints_conf=temperature_and_setpoints_conf,
            comfort_threshold=comfort_threshold,
            energy_weight=energy_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
        )
        self.W_energy = float(energy_weight)
        self.W_temperature = float(temperature_weight)
        self.W_energy_cost = float(cost_weight)
        self.lambda_energy_cost = float(lambda_energy_cost)
        self.energy_cost_names = list(energy_cost_variables) if energy_cost_variables else []
        self.seconds_per_step = float(seconds_per_step) if seconds_per_step else None
        self.default_price = float(default_price_eur_per_kwh)
        self._tariff = None
        if energy_cost_path:
            try:
                self._tariff = _load_energy_cost_tariff(energy_cost_path)
                self.logger.info(
                    f"Tarifa carregada de {energy_cost_path} ({len(self._tariff)} registres)."
                )
            except Exception as exc:
                self.logger.warning(
                    f"No s'ha pogut llegir la tarifa de {energy_cost_path}: {exc}. Faré servir preu per defecte."
                )

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        obs = _patch_datetime_obs(obs_dict)

        energy_values = self._get_energy_consumed(obs)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        temp_violations = self._get_temperature_violation(obs)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        money_spent, price_used = _resolve_energy_cost(
            obs_dict=obs,
            total_power_watts=self.total_energy,
            energy_cost_names=self.energy_cost_names,
            tariff=self._tariff,
            default_price_eur_per_kwh=self.default_price,
            seconds_per_step=self.seconds_per_step,
            logger=self.logger,
            label=self.__class__.__name__,
        )
        self.total_energy_cost = money_spent
        self.energy_cost_penalty = -self.total_energy_cost

        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * self.W_temperature * self.comfort_penalty
        energy_cost_term = self.lambda_energy_cost * self.W_energy_cost * self.energy_cost_penalty
        reward = energy_term + comfort_term + energy_cost_term

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_cost_term': energy_cost_term,
            'reward_energy_weight': self.W_energy,
            'reward_temperature_weight': self.W_temperature,
            'reward_cost_weight': self.W_energy_cost,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'energy_cost_penalty': self.energy_cost_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'money_spent': self.total_energy_cost,
            'comfort_threshold': self.comfort_threshold,
        }
        if price_used is not None:
            reward_terms['price_eur_per_kwh'] = price_used

        return reward, reward_terms


class MultiZoneEnergyCostHourlyReward(MultiZoneEnergyCostReward):
    """Multi-zone reward with energy, comfort and cost terms, emphasizing comfort only during active hours."""

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, str],
        comfort_threshold: float = 0.5,
        energy_weight: float = 0.4,
        temperature_weight: float = 0.4,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_energy_cost: float = 1.0,
        range_comfort_hours: Tuple[int, int] = (9, 19),
        *,
        energy_cost_path: Optional[str] = None,
        energy_cost_variables: Optional[List[str]] = None,
        seconds_per_step: Optional[float] = None,
        default_price_eur_per_kwh: float = 0.15,
    ):
        super().__init__(
            energy_variables=energy_variables,
            temperature_and_setpoints_conf=temperature_and_setpoints_conf,
            comfort_threshold=comfort_threshold,
            energy_weight=energy_weight,
            temperature_weight=temperature_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
            lambda_energy_cost=lambda_energy_cost,
            energy_cost_path=energy_cost_path,
            energy_cost_variables=energy_cost_variables,
            seconds_per_step=seconds_per_step,
            default_price_eur_per_kwh=default_price_eur_per_kwh,
        )
        self.range_comfort_hours = tuple(map(int, range_comfort_hours))
        non_comfort_total = self.W_energy + self.W_energy_cost
        if non_comfort_total > 0.0:
            self.off_hours_energy_weight = self.W_energy / non_comfort_total
            self.off_hours_cost_weight = self.W_energy_cost / non_comfort_total
        else:
            self.off_hours_energy_weight = 1.0
            self.off_hours_cost_weight = 0.0

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        obs = _patch_datetime_obs(obs_dict)

        energy_values = self._get_energy_consumed(obs)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        temp_violations = self._get_temperature_violation(obs)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        money_spent, price_used = _resolve_energy_cost(
            obs_dict=obs,
            total_power_watts=self.total_energy,
            energy_cost_names=self.energy_cost_names,
            tariff=self._tariff,
            default_price_eur_per_kwh=self.default_price,
            seconds_per_step=self.seconds_per_step,
            logger=self.logger,
            label=self.__class__.__name__,
        )
        self.total_energy_cost = money_spent
        self.energy_cost_penalty = -self.total_energy_cost

        hour = _recover_hour_from_obs(obs)
        comfort_active = _is_hour_in_window(hour, self.range_comfort_hours)
        if comfort_active:
            reward_energy_weight = self.W_energy
            reward_temperature_weight = self.W_temperature
            reward_cost_weight = self.W_energy_cost
        else:
            reward_energy_weight = self.off_hours_energy_weight
            reward_temperature_weight = 0.0
            reward_cost_weight = self.off_hours_cost_weight

        energy_term = self.lambda_energy * reward_energy_weight * self.energy_penalty
        comfort_term = self.lambda_temp * reward_temperature_weight * self.comfort_penalty
        energy_cost_term = self.lambda_energy_cost * reward_cost_weight * self.energy_cost_penalty
        reward = energy_term + comfort_term + energy_cost_term

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_cost_term': energy_cost_term,
            'reward_weights': {
                'energy': reward_energy_weight,
                'temperature': reward_temperature_weight,
                'cost': reward_cost_weight,
            },
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'energy_cost_penalty': self.energy_cost_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'money_spent': self.total_energy_cost,
            'comfort_threshold': self.comfort_threshold,
            'comfort_active': 1.0 if comfort_active else 0.0,
            'hour': hour,
        }
        if price_used is not None:
            reward_terms['price_eur_per_kwh'] = price_used

        return reward, reward_terms


class BatteryHVACReward(LinearReward):
    """Fixed-comfort reward for HVAC control with grid and battery penalties."""

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[float, float],
        range_comfort_summer: Tuple[float, float],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.2,
        temperature_weight: float = 0.55,
        grid_energy_weight: float = 0.2,
        battery_cycle_weight: float = 0.04,
        battery_loss_weight: float = 0.005,
        simultaneous_battery_weight: float = 0.005,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_grid: float = 1.0,
        lambda_battery: float = 1.0,
        *,
        grid_energy_variables: Optional[List[str]] = None,
        battery_charge_variables: Optional[List[str]] = None,
        battery_discharge_variables: Optional[List[str]] = None,
        battery_loss_variables: Optional[List[str]] = None,
    ):
        super().__init__(
            temperature_variables=temperature_variables,
            energy_variables=energy_variables,
            range_comfort_winter=range_comfort_winter,
            range_comfort_summer=range_comfort_summer,
            summer_start=summer_start,
            summer_final=summer_final,
            energy_weight=energy_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
        )
        for name, value in (
            ("temperature_weight", temperature_weight),
            ("grid_energy_weight", grid_energy_weight),
            ("battery_cycle_weight", battery_cycle_weight),
            ("battery_loss_weight", battery_loss_weight),
            ("simultaneous_battery_weight", simultaneous_battery_weight),
        ):
            _validate_unit_weight(name, value)
        for name, value in (
            ("lambda_grid", lambda_grid),
            ("lambda_battery", lambda_battery),
        ):
            _validate_non_negative(name, value)

        self.W_temperature = float(temperature_weight)
        self.W_grid = float(grid_energy_weight)
        self.W_battery_cycle = float(battery_cycle_weight)
        self.W_battery_loss = float(battery_loss_weight)
        self.W_simultaneous_battery = float(simultaneous_battery_weight)
        self.lambda_grid = float(lambda_grid)
        self.lambda_battery = float(lambda_battery)
        self.grid_energy_names = _as_variable_list(grid_energy_variables)
        self.battery_charge_names = _as_variable_list(battery_charge_variables)
        self.battery_discharge_names = _as_variable_list(battery_discharge_variables)
        self.battery_loss_names = _as_variable_list(battery_loss_variables)

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        obs = _patch_datetime_obs(obs_dict)

        self.total_energy = _sum_observation_values(
            obs, self.energy_names, positive_only=True
        )
        self.energy_penalty = -self.total_energy

        temp_violations = self._get_temperature_violation(obs)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        components = _get_battery_hvac_components(
            obs,
            self.grid_energy_names,
            self.battery_charge_names,
            self.battery_discharge_names,
            self.battery_loss_names,
        )
        grid_penalty = -components["grid_power"]
        battery_cycle_penalty = -components["battery_cycle_power"]
        battery_loss_penalty = -components["battery_loss_power"]
        simultaneous_battery_penalty = -components["simultaneous_battery_power"]

        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * self.W_temperature * self.comfort_penalty
        grid_energy_term = self.lambda_grid * self.W_grid * grid_penalty
        battery_cycle_term = (
            self.lambda_battery * self.W_battery_cycle * battery_cycle_penalty
        )
        battery_loss_term = (
            self.lambda_battery * self.W_battery_loss * battery_loss_penalty
        )
        simultaneous_battery_term = (
            self.lambda_battery
            * self.W_simultaneous_battery
            * simultaneous_battery_penalty
        )
        reward = (
            energy_term
            + comfort_term
            + grid_energy_term
            + battery_cycle_term
            + battery_loss_term
            + simultaneous_battery_term
        )

        reward_terms = {
            "energy_term": energy_term,
            "comfort_term": comfort_term,
            "grid_energy_term": grid_energy_term,
            "battery_cycle_term": battery_cycle_term,
            "battery_loss_term": battery_loss_term,
            "simultaneous_battery_term": simultaneous_battery_term,
            "energy_penalty": self.energy_penalty,
            "comfort_penalty": self.comfort_penalty,
            "grid_energy_penalty": grid_penalty,
            "battery_cycle_penalty": battery_cycle_penalty,
            "battery_loss_penalty": battery_loss_penalty,
            "simultaneous_battery_penalty": simultaneous_battery_penalty,
            "total_power_demand": self.total_energy,
            "total_grid_power_demand": components["grid_power"],
            "total_temperature_violation": self.total_temp_violation,
            "battery_charge_power": components["battery_charge_power"],
            "battery_discharge_power": components["battery_discharge_power"],
            "battery_cycle_power": components["battery_cycle_power"],
            "battery_loss_power": components["battery_loss_power"],
            "simultaneous_battery_power": components["simultaneous_battery_power"],
            "reward_weights": {
                "energy": self.W_energy,
                "temperature": self.W_temperature,
                "grid": self.W_grid,
                "battery_cycle": self.W_battery_cycle,
                "battery_loss": self.W_battery_loss,
                "simultaneous_battery": self.W_simultaneous_battery,
            },
        }
        return reward, reward_terms


class MultiZoneBatteryHVACReward(MultiZoneReward):
    """Multi-zone HVAC reward with grid and battery operation penalties."""

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, Union[str, List[str], Tuple[str, ...]]],
        comfort_threshold: float = 0.5,
        energy_weight: float = 0.2,
        temperature_weight: float = 0.55,
        grid_energy_weight: float = 0.2,
        battery_cycle_weight: float = 0.04,
        battery_loss_weight: float = 0.005,
        simultaneous_battery_weight: float = 0.005,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_grid: float = 1.0,
        lambda_battery: float = 1.0,
        *,
        grid_energy_variables: Optional[List[str]] = None,
        battery_charge_variables: Optional[List[str]] = None,
        battery_discharge_variables: Optional[List[str]] = None,
        battery_loss_variables: Optional[List[str]] = None,
    ):
        super().__init__(
            energy_variables=energy_variables,
            temperature_and_setpoints_conf=temperature_and_setpoints_conf,
            comfort_threshold=comfort_threshold,
            energy_weight=energy_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
        )
        for name, value in (
            ("temperature_weight", temperature_weight),
            ("grid_energy_weight", grid_energy_weight),
            ("battery_cycle_weight", battery_cycle_weight),
            ("battery_loss_weight", battery_loss_weight),
            ("simultaneous_battery_weight", simultaneous_battery_weight),
        ):
            _validate_unit_weight(name, value)
        for name, value in (
            ("lambda_grid", lambda_grid),
            ("lambda_battery", lambda_battery),
        ):
            _validate_non_negative(name, value)

        self.W_temperature = float(temperature_weight)
        self.W_grid = float(grid_energy_weight)
        self.W_battery_cycle = float(battery_cycle_weight)
        self.W_battery_loss = float(battery_loss_weight)
        self.W_simultaneous_battery = float(simultaneous_battery_weight)
        self.lambda_grid = float(lambda_grid)
        self.lambda_battery = float(lambda_battery)
        self.grid_energy_names = _as_variable_list(grid_energy_variables)
        self.battery_charge_names = _as_variable_list(battery_charge_variables)
        self.battery_discharge_names = _as_variable_list(battery_discharge_variables)
        self.battery_loss_names = _as_variable_list(battery_loss_variables)

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        obs = _patch_datetime_obs(obs_dict)

        self.total_energy = _sum_observation_values(
            obs, self.energy_names, positive_only=True
        )
        self.energy_penalty = -self.total_energy

        temp_violations = self._get_temperature_violation(obs)
        self.total_temp_violation = sum(temp_violations)
        self.comfort_penalty = -self.total_temp_violation

        components = _get_battery_hvac_components(
            obs,
            self.grid_energy_names,
            self.battery_charge_names,
            self.battery_discharge_names,
            self.battery_loss_names,
        )
        grid_penalty = -components["grid_power"]
        battery_cycle_penalty = -components["battery_cycle_power"]
        battery_loss_penalty = -components["battery_loss_power"]
        simultaneous_battery_penalty = -components["simultaneous_battery_power"]

        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * self.W_temperature * self.comfort_penalty
        grid_energy_term = self.lambda_grid * self.W_grid * grid_penalty
        battery_cycle_term = (
            self.lambda_battery * self.W_battery_cycle * battery_cycle_penalty
        )
        battery_loss_term = (
            self.lambda_battery * self.W_battery_loss * battery_loss_penalty
        )
        simultaneous_battery_term = (
            self.lambda_battery
            * self.W_simultaneous_battery
            * simultaneous_battery_penalty
        )
        reward = (
            energy_term
            + comfort_term
            + grid_energy_term
            + battery_cycle_term
            + battery_loss_term
            + simultaneous_battery_term
        )

        reward_terms = {
            "energy_term": energy_term,
            "comfort_term": comfort_term,
            "grid_energy_term": grid_energy_term,
            "battery_cycle_term": battery_cycle_term,
            "battery_loss_term": battery_loss_term,
            "simultaneous_battery_term": simultaneous_battery_term,
            "energy_penalty": self.energy_penalty,
            "comfort_penalty": self.comfort_penalty,
            "grid_energy_penalty": grid_penalty,
            "battery_cycle_penalty": battery_cycle_penalty,
            "battery_loss_penalty": battery_loss_penalty,
            "simultaneous_battery_penalty": simultaneous_battery_penalty,
            "total_power_demand": self.total_energy,
            "total_grid_power_demand": components["grid_power"],
            "total_temperature_violation": self.total_temp_violation,
            "battery_charge_power": components["battery_charge_power"],
            "battery_discharge_power": components["battery_discharge_power"],
            "battery_cycle_power": components["battery_cycle_power"],
            "battery_loss_power": components["battery_loss_power"],
            "simultaneous_battery_power": components["simultaneous_battery_power"],
            "comfort_threshold": self.comfort_threshold,
            "reward_weights": {
                "energy": self.W_energy,
                "temperature": self.W_temperature,
                "grid": self.W_grid,
                "battery_cycle": self.W_battery_cycle,
                "battery_loss": self.W_battery_loss,
                "simultaneous_battery": self.W_simultaneous_battery,
            },
        }
        return reward, reward_terms

    def _get_temperature_violation(
            self, obs_dict: Dict[str, Any]) -> List[float]:
        self.comfort_ranges = {}
        temp_violations = []
        for temp_var, setpoint_conf in self.comfort_configuration.items():
            temp_value = _safe_obs_value(obs_dict, temp_var, None)
            if temp_value is None:
                continue

            setpoint_names = _as_variable_list(setpoint_conf)
            if len(setpoint_names) >= 2:
                lower_setpoint = _safe_obs_value(obs_dict, setpoint_names[0], None)
                upper_setpoint = _safe_obs_value(obs_dict, setpoint_names[1], None)
                if lower_setpoint is None and upper_setpoint is None:
                    continue
                if lower_setpoint is None:
                    lower_setpoint = upper_setpoint
                if upper_setpoint is None:
                    upper_setpoint = lower_setpoint
                lower_bound = min(lower_setpoint, upper_setpoint) - self.comfort_threshold
                upper_bound = max(lower_setpoint, upper_setpoint) + self.comfort_threshold
            elif len(setpoint_names) == 1:
                setpoint = _safe_obs_value(obs_dict, setpoint_names[0], None)
                if setpoint is None:
                    continue
                lower_bound = setpoint - self.comfort_threshold
                upper_bound = setpoint + self.comfort_threshold
            else:
                continue

            self.comfort_ranges[temp_var] = (lower_bound, upper_bound)
            temp_violations.append(
                max(lower_bound - temp_value, 0.0, temp_value - upper_bound)
            )

        return temp_violations


class MultizoneEnergyCostBatteryHVACReward(MultiZoneBatteryHVACReward):
    """Multi-zone reward with real energy cost (grid_kW * EUR/kWh) and occupied-hours comfort weighting.

    Extends MultiZoneBatteryHVACReward with two additional mechanisms:

    1. Energy cost term: penalises the actual economic cost of grid consumption at the
       current spot price (grid_power_W / 1000 * energy_price_EUR_per_kWh).  This teaches
       the agent to charge the battery when electricity is cheap and avoid grid purchases
       during expensive periods.

    2. Occupied-hours comfort: the comfort penalty is scaled by `occupied_comfort_multiplier`
       during occupied hours and by `unoccupied_comfort_multiplier` outside them, so the agent
       prioritises thermal comfort when people are present without ignoring off-hours completely.
    """

    def __init__(
        self,
        energy_variables: List[str],
        temperature_and_setpoints_conf: Dict[str, Union[str, List[str], Tuple[str, ...]]],
        comfort_threshold: float = 0.5,
        energy_weight: float = 0.15,
        temperature_weight: float = 0.40,
        grid_energy_weight: float = 0.15,
        energy_cost_weight: float = 0.20,
        battery_cycle_weight: float = 0.04,
        battery_loss_weight: float = 0.005,
        simultaneous_battery_weight: float = 0.005,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        lambda_grid: float = 1.0,
        lambda_energy_cost: float = 1.0,
        lambda_battery: float = 1.0,
        occupied_hours: Tuple[int, int] = (8, 18),
        occupied_comfort_multiplier: float = 2.0,
        unoccupied_comfort_multiplier: float = 0.3,
        *,
        grid_energy_variables: Optional[List[str]] = None,
        energy_cost_variables: Optional[List[str]] = None,
        battery_charge_variables: Optional[List[str]] = None,
        battery_discharge_variables: Optional[List[str]] = None,
        battery_loss_variables: Optional[List[str]] = None,
    ):
        super().__init__(
            energy_variables=energy_variables,
            temperature_and_setpoints_conf=temperature_and_setpoints_conf,
            comfort_threshold=comfort_threshold,
            energy_weight=energy_weight,
            temperature_weight=temperature_weight,
            grid_energy_weight=grid_energy_weight,
            battery_cycle_weight=battery_cycle_weight,
            battery_loss_weight=battery_loss_weight,
            simultaneous_battery_weight=simultaneous_battery_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
            lambda_grid=lambda_grid,
            lambda_battery=lambda_battery,
            grid_energy_variables=grid_energy_variables,
            battery_charge_variables=battery_charge_variables,
            battery_discharge_variables=battery_discharge_variables,
            battery_loss_variables=battery_loss_variables,
        )
        _validate_unit_weight("energy_cost_weight", energy_cost_weight)
        _validate_non_negative("lambda_energy_cost", lambda_energy_cost)
        if occupied_comfort_multiplier < 0.0:
            raise ValueError("occupied_comfort_multiplier must be >= 0.")
        if unoccupied_comfort_multiplier < 0.0:
            raise ValueError("unoccupied_comfort_multiplier must be >= 0.")

        self.W_energy_cost = float(energy_cost_weight)
        self.lambda_energy_cost = float(lambda_energy_cost)
        self.energy_cost_names = _as_variable_list(energy_cost_variables)
        self.occupied_hours = tuple(map(int, occupied_hours))
        self.occupied_comfort_multiplier = float(occupied_comfort_multiplier)
        self.unoccupied_comfort_multiplier = float(unoccupied_comfort_multiplier)

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        obs = _patch_datetime_obs(obs_dict)

        hour = _recover_hour_from_obs(obs)
        occupied_hour = _is_hour_in_window(hour, self.occupied_hours)
        comfort_multiplier = (
            self.occupied_comfort_multiplier
            if occupied_hour
            else self.unoccupied_comfort_multiplier
        )

        self.total_energy = _sum_observation_values(obs, self.energy_names, positive_only=True)
        self.energy_penalty = -self.total_energy

        raw_temp_violations = self._get_temperature_violation(obs)
        self.total_temp_violation = sum(raw_temp_violations)
        self.comfort_penalty = -(self.total_temp_violation * comfort_multiplier)

        components = _get_battery_hvac_components(
            obs,
            self.grid_energy_names,
            self.battery_charge_names,
            self.battery_discharge_names,
            self.battery_loss_names,
        )
        grid_penalty = -components["grid_power"]
        battery_cycle_penalty = -components["battery_cycle_power"]
        battery_loss_penalty = -components["battery_loss_power"]
        simultaneous_battery_penalty = -components["simultaneous_battery_power"]

        # Energy cost: kW_grid * EUR/kWh  →  approximate EUR per hour at current timestep
        energy_price = _sum_observation_values(obs, self.energy_cost_names, positive_only=True)
        grid_kw = max(components["grid_power"], 0.0) / 1000.0
        energy_cost_value = grid_kw * energy_price
        energy_cost_penalty = -energy_cost_value

        energy_term = self.lambda_energy * self.W_energy * self.energy_penalty
        comfort_term = self.lambda_temp * self.W_temperature * self.comfort_penalty
        grid_energy_term = self.lambda_grid * self.W_grid * grid_penalty
        energy_cost_term = self.lambda_energy_cost * self.W_energy_cost * energy_cost_penalty
        battery_cycle_term = self.lambda_battery * self.W_battery_cycle * battery_cycle_penalty
        battery_loss_term = self.lambda_battery * self.W_battery_loss * battery_loss_penalty
        simultaneous_battery_term = (
            self.lambda_battery * self.W_simultaneous_battery * simultaneous_battery_penalty
        )

        reward = (
            energy_term
            + comfort_term
            + grid_energy_term
            + energy_cost_term
            + battery_cycle_term
            + battery_loss_term
            + simultaneous_battery_term
        )

        reward_terms = {
            "energy_term": energy_term,
            "comfort_term": comfort_term,
            "grid_energy_term": grid_energy_term,
            "energy_cost_term": energy_cost_term,
            "battery_cycle_term": battery_cycle_term,
            "battery_loss_term": battery_loss_term,
            "simultaneous_battery_term": simultaneous_battery_term,
            "energy_penalty": self.energy_penalty,
            "comfort_penalty": self.comfort_penalty,
            "grid_energy_penalty": grid_penalty,
            "energy_cost_penalty": energy_cost_penalty,
            "battery_cycle_penalty": battery_cycle_penalty,
            "battery_loss_penalty": battery_loss_penalty,
            "simultaneous_battery_penalty": simultaneous_battery_penalty,
            "total_power_demand": self.total_energy,
            "total_grid_power_demand": components["grid_power"],
            "total_temperature_violation": self.total_temp_violation,
            "raw_temperature_violation": self.total_temp_violation,
            "energy_price_eur_per_kwh": energy_price,
            "energy_cost_eur_per_h": energy_cost_value,
            "battery_charge_power": components["battery_charge_power"],
            "battery_discharge_power": components["battery_discharge_power"],
            "battery_cycle_power": components["battery_cycle_power"],
            "battery_loss_power": components["battery_loss_power"],
            "simultaneous_battery_power": components["simultaneous_battery_power"],
            "occupied_hour": 1.0 if occupied_hour else 0.0,
            "comfort_multiplier": comfort_multiplier,
            "hour": hour,
            "comfort_threshold": self.comfort_threshold,
            "reward_weights": {
                "energy": self.W_energy,
                "temperature": self.W_temperature,
                "grid": self.W_grid,
                "energy_cost": self.W_energy_cost,
                "battery_cycle": self.W_battery_cycle,
                "battery_loss": self.W_battery_loss,
                "simultaneous_battery": self.W_simultaneous_battery,
            },
        }
        return reward, reward_terms


class OccupiedHoursDiscomfortReward(LinearReward):
    """Linear reward with comfort active only in occupied hours and boosted energy pressure off-hours."""

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[float, float],
        range_comfort_summer: Tuple[float, float],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        occupied_hours: Tuple[int, int] = (8, 18),
        occupied_discomfort_multiplier: float = 10.0,
        off_hours_energy_multiplier: float = 5.0,
        off_hours_discomfort_multiplier: float = 0.0,
    ):
        super().__init__(
            temperature_variables=temperature_variables,
            energy_variables=energy_variables,
            range_comfort_winter=range_comfort_winter,
            range_comfort_summer=range_comfort_summer,
            summer_start=summer_start,
            summer_final=summer_final,
            energy_weight=energy_weight,
            lambda_energy=lambda_energy,
            lambda_temperature=lambda_temperature,
        )
        if occupied_discomfort_multiplier < 0.0:
            self.logger.error(
                'occupied_discomfort_multiplier must be >= 0. '
                f'Received: {occupied_discomfort_multiplier}'
            )
            raise ValueError
        if off_hours_energy_multiplier < 0.0:
            self.logger.error(
                'off_hours_energy_multiplier must be >= 0. '
                f'Received: {off_hours_energy_multiplier}'
            )
            raise ValueError
        self.occupied_energy_weight = float(energy_weight)
        self.off_hours_energy_weight = 1.0
        self.occupied_hours = tuple(map(int, occupied_hours))
        self.occupied_discomfort_multiplier = float(occupied_discomfort_multiplier)
        self.off_hours_energy_multiplier = float(off_hours_energy_multiplier)
        # Retained for backward compatibility; off-hours comfort is always disabled.
        self.off_hours_discomfort_multiplier = 0.0

    def __call__(self, obs_dict: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        obs = _patch_datetime_obs(obs_dict)

        energy_values = self._get_energy_consumed(obs)
        self.total_energy = sum(energy_values)
        self.energy_penalty = -self.total_energy

        temp_violations = self._get_temperature_violation(obs)
        base_temp_violation = sum(temp_violations)

        hour = _recover_hour_from_obs(obs)
        occupied_hour = _is_hour_in_window(hour, self.occupied_hours)
        reward_weight = (
            self.occupied_energy_weight
            if occupied_hour
            else self.off_hours_energy_weight
        )
        effective_lambda_energy = (
            self.lambda_energy
            if occupied_hour
            else self.lambda_energy * self.off_hours_energy_multiplier
        )
        self.W_energy = reward_weight
        comfort_multiplier = (
            self.occupied_discomfort_multiplier
            if occupied_hour
            else 0.0
        )

        # Outside occupied hours, the comfort term is fully disabled.
        self.total_temp_violation = (
            base_temp_violation if occupied_hour else 0.0
        )
        self.comfort_penalty = -(base_temp_violation * comfort_multiplier)

        energy_term = effective_lambda_energy * reward_weight * self.energy_penalty
        comfort_term = self.lambda_temp * (1 - reward_weight) * self.comfort_penalty
        reward = energy_term + comfort_term
        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'energy_penalty': self.energy_penalty,
            'comfort_penalty': self.comfort_penalty,
            'total_power_demand': self.total_energy,
            'total_temperature_violation': self.total_temp_violation,
            'raw_temperature_violation': base_temp_violation,
            'effective_lambda_energy': effective_lambda_energy,
            'reward_weight': reward_weight,
            'occupied_energy_weight': self.occupied_energy_weight,
            'off_hours_energy_weight': self.off_hours_energy_weight,
            'off_hours_energy_multiplier': self.off_hours_energy_multiplier,
            'occupied_hour': 1.0 if occupied_hour else 0.0,
            'comfort_multiplier': comfort_multiplier,
            'hour': hour,
        }
        return reward, reward_terms
