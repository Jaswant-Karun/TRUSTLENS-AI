"""
TRUSTLENS AI — Dedicated Background Worker
Processes asynchronous notification deliveries and scheduled threat-intel polling
without blocking API inference workers.
"""

import asyncio
import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.core.logging import logger
from backend.app.database.manager import db_manager
from backend.app.services.notification_service import notification_service
from backend.app.services.threat_intel_service import threat_intel_service


async def worker_loop(stop_event: asyncio.Event) -> None:
    poll_interval = int(os.getenv("THREAT_INTEL_POLL_SECONDS", "3600"))
    notif_interval = int(os.getenv("NOTIFICATION_POLL_SECONDS", "10"))
    elapsed = poll_interval  # trigger initial sync on startup

    await db_manager.connect()
    logger.info("TRUSTLENS AI background worker started.")
    try:
        while not stop_event.is_set():
            try:
                await notification_service.process_pending_queue()
            except Exception as exc:
                logger.error(f"Notification queue error: {exc}")

            if elapsed >= poll_interval:
                elapsed = 0
                try:
                    await threat_intel_service.ingest_source("cisa_kev", allow_non_commercial=False)
                except Exception as exc:
                    logger.warning(f"Scheduled threat-intel poll warning: {exc}")

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=notif_interval)
            except asyncio.TimeoutError:
                elapsed += notif_interval
    finally:
        await db_manager.disconnect()
        logger.info("TRUSTLENS AI background worker stopped cleanly.")


def main() -> None:
    stop_event = asyncio.Event()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass

    try:
        loop.run_until_complete(worker_loop(stop_event))
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        loop.close()


if __name__ == "__main__":
    main()
