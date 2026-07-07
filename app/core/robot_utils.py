"""
robot_utils.py
==============
Translates a tracked person's horizontal position and estimated distance
into discrete robot movement commands, and dispatches those commands
either to an on-screen simulation panel (simulate_hardware=true) or to
a real microcontroller over a serial connection (simulate_hardware=false).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from app.config import AppConfig
from app.logger import get_logger

logger = get_logger(__name__)

try:
    import serial  # pyserial
except ImportError:  # pragma: no cover - optional at import time
    serial = None  # type: ignore[assignment]


class RobotCommand(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    STOP = "STOP"


@dataclass
class RobotDecision:
    command: RobotCommand
    reason: str


def decide_command(
    frame_width: int,
    face_center_x: float,
    distance_cm: float,
    config: AppConfig,
) -> RobotDecision:
    """Compute the appropriate robot command from a target's horizontal
    offset from frame-center and its estimated distance.

    Priority: horizontal alignment first (turn to face the target),
    then forward/backward distance regulation, else STOP when the
    target is centered and within the ideal distance band.
    """
    robot_cfg = config.robot
    frame_center_x = frame_width / 2.0
    offset = face_center_x - frame_center_x

    if abs(offset) > robot_cfg.center_dead_zone_px:
        if offset < 0:
            return RobotDecision(RobotCommand.LEFT, f"Target offset {offset:.0f}px left of center")
        return RobotDecision(RobotCommand.RIGHT, f"Target offset {offset:.0f}px right of center")

    if distance_cm < 0:
        return RobotDecision(RobotCommand.STOP, "Distance unknown - holding position")

    if distance_cm > robot_cfg.forward_distance_cm:
        return RobotDecision(RobotCommand.FORWARD, f"Target {distance_cm:.0f}cm away - closing distance")

    if distance_cm < robot_cfg.backward_distance_cm:
        return RobotDecision(RobotCommand.BACKWARD, f"Target {distance_cm:.0f}cm away - too close, backing off")

    return RobotDecision(RobotCommand.STOP, "Target centered and within ideal range")


class RobotController:
    """Owns the (optional) serial connection and exposes a single
    `send_command` entry point used identically regardless of whether
    hardware is simulated or real."""

    def __init__(self, config: AppConfig):
        self._config = config
        self._serial_connection: Optional["serial.Serial"] = None
        self._last_command: Optional[RobotCommand] = None
        self._connected = False

    def connect(self) -> bool:
        """Open the serial port if running against real hardware. In
        simulation mode this is a no-op that always succeeds."""
        if self._config.robot.simulate_hardware:
            self._connected = True
            logger.info("Robot controller running in SIMULATION mode.")
            return True

        if serial is None:
            logger.error("pyserial is not installed; cannot connect to hardware.")
            return False

        try:
            self._serial_connection = serial.Serial(
                port=self._config.robot.serial_port,
                baudrate=self._config.robot.baud_rate,
                timeout=1,
            )
            self._connected = True
            logger.info("Connected to robot over serial port %s", self._config.robot.serial_port)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to open serial port %s: %s", self._config.robot.serial_port, exc)
            self._connected = False
            return False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def send_command(self, command: RobotCommand) -> None:
        """Dispatch a robot command. Avoids re-sending an identical
        command repeatedly to reduce serial/log noise."""
        if command == self._last_command:
            return
        self._last_command = command

        if self._config.robot.simulate_hardware or self._serial_connection is None:
            logger.info("[SIMULATED] Robot command -> %s", command.value)
            return

        try:
            payload = f"{command.value}\n".encode("utf-8")
            self._serial_connection.write(payload)
            logger.info("Transmitted robot command over serial -> %s", command.value)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to transmit serial command: %s", exc)

    def disconnect(self) -> None:
        if self._serial_connection is not None:
            try:
                self._serial_connection.close()
            except Exception:  # noqa: BLE001
                pass
            self._serial_connection = None
        self._connected = False
