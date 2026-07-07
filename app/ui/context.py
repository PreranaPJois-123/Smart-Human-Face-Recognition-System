"""
context.py
==========
A single shared "application context" object holding the config,
database, and face-analysis engine singletons. Passed into every page
so pages never construct their own copies of these expensive/global
resources, and so a Settings change (e.g. threshold) is instantly
visible everywhere.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import AppConfig, get_config
from app.core.database_utils import FaceDatabase, get_database
from app.core.face_utils import FaceAnalysisEngine, get_face_engine
from app.core.robot_utils import RobotController


@dataclass
class AppContext:
    config: AppConfig
    database: FaceDatabase
    face_engine: FaceAnalysisEngine
    robot_controller: RobotController

    @classmethod
    def create(cls) -> "AppContext":
        config = get_config()
        return cls(
            config=config,
            database=get_database(config),
            face_engine=get_face_engine(config),
            robot_controller=RobotController(config),
        )

    def reload_config(self) -> None:
        """Refresh the config singleton after Settings persists changes."""
        self.config = get_config(reload=True)
