import sys
import traceback

from forexdecsters.cli import _pause_before_close, app
from forexdecsters.theme import console

if __name__ == "__main__":
    try:
        app()
    except SystemExit:
        _pause_before_close()
        raise
    except Exception as exc:
        console.print(f"[danger]{exc}[/danger]")
        traceback.print_exc()
        _pause_before_close()
        sys.exit(1)
    else:
        _pause_before_close()
