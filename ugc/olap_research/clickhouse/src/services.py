from dataclasses import dataclass, field

from adapters.base import BaseDBMigrator


@dataclass
class DBService:
    db_migrators: list[BaseDBMigrator] = field(default_factory=lambda: [])

    def db_upgrade(self):
        for migrator in self.db_migrators:
            migrator.db_upgrade()


