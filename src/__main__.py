from .config_parser.config import Config
from .supervisor import Supervisor

if __name__ == "__main__":
    config_parser = Config()
    supervisor = Supervisor(config_parser)