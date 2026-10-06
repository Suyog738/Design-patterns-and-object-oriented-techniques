import logging
from uuid import UUID

from domain.actuators.ports import ActuatorPort


logger = logging.getLogger(__name__)


class SimulationActuatorAdapter(ActuatorPort):
    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        logger.info(
            "Simulation actuator: device=%s command=%s payload=%s",
            device_id,
            command,
            payload,
        )