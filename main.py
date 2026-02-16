from src.app import LLMTesterApp
from src.logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Starting LLM Tester")
    app = LLMTesterApp()
    app.mainloop()
    logger.info("LLM Tester shut down")


if __name__ == "__main__":
    main()
