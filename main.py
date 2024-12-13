"""
Main.py, (Start here)

Just starts the app.
"""
import logging
import tracemalloc
from gui import LoginWindow
import customtkinter as ctk

def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main() -> None:
    """Initialize and run the application."""
    # Enable tracemalloc for debugging (make sure this works properly)
    tracemalloc.start()

    # Suppress CustomTkinter warnings (Just annoying and fills the console)
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Set the default theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create and run login window
        app = LoginWindow()
        app.run()

    except Exception as e:
        logger.error(f"Application error: {e}")
        # Get tracemalloc info
        current, peak = tracemalloc.get_traced_memory()
        logger.error(f"Current memory usage: {current / 10**6}MB")
        logger.error(f"Peak memory usage: {peak / 10**6}MB")
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        logger.error("[ Top 3 memory users ]")
        for stat in top_stats[:3]:
            logger.error(stat)
        raise
    finally:
        tracemalloc.stop()

if __name__ == "__main__":
    main()