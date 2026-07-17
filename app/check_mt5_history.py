from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import MetaTrader5 as mt5


SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_H1
TIMEFRAME_NAME = "H1"
LOOKBACK_DAYS = 180
OUTPUT_DIR = Path("data") / "mt5"

def fail(message: str, *, details: Any | None = None) -> None:
    print()
    print("ERROR:", message)

    if details is not None:
        print("DETAILS:", details)

    mt5.shutdown()
    raise SystemExit(1)


def normalize_float(value: Any) -> str:
    return format(float(value), ".10f")


def build_fingerprint(rates: Any) -> str:
    digest = hashlib.sha256()

    for rate in rates:
        line = ",".join(
            (
                str(int(rate["time"])),
                normalize_float(rate["open"]),
                normalize_float(rate["high"]),
                normalize_float(rate["low"]),
                normalize_float(rate["close"]),
                str(int(rate["tick_volume"])),
                str(int(rate["spread"])),
                str(int(rate["real_volume"])),
            )
        )

        digest.update(line.encode("utf-8"))
        digest.update(b"\n")

    return digest.hexdigest()
def save_rates_csv(rates: Any, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "timestamp_utc",
        "time",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
        "spread",
        "real_volume",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for rate in rates:
            timestamp = int(rate["time"])

            writer.writerow(
                {
                    "timestamp_utc": datetime.fromtimestamp(
                        timestamp,
                        tz=timezone.utc,
                    ).isoformat(),
                    "time": timestamp,
                    "open": normalize_float(rate["open"]),
                    "high": normalize_float(rate["high"]),
                    "low": normalize_float(rate["low"]),
                    "close": normalize_float(rate["close"]),
                    "tick_volume": int(rate["tick_volume"]),
                    "spread": int(rate["spread"]),
                    "real_volume": int(rate["real_volume"]),
                }
            )

def validate_rates(rates: Any) -> None:
    previous_timestamp: int | None = None
    seen_timestamps: set[int] = set()

    for index, rate in enumerate(rates):
        timestamp = int(rate["time"])
        open_price = float(rate["open"])
        high_price = float(rate["high"])
        low_price = float(rate["low"])
        close_price = float(rate["close"])
        tick_volume = int(rate["tick_volume"])
        spread = int(rate["spread"])
        real_volume = int(rate["real_volume"])

        if timestamp in seen_timestamps:
            fail(
                "Обнаружен дублирующийся timestamp.",
                details={"index": index, "timestamp": timestamp},
            )

        if previous_timestamp is not None and timestamp <= previous_timestamp:
            fail(
                "Свечи не отсортированы строго по возрастанию времени.",
                details={
                    "index": index,
                    "previous_timestamp": previous_timestamp,
                    "timestamp": timestamp,
                },
            )

        if high_price < low_price:
            fail(
                "Нарушен OHLC-инвариант: high < low.",
                details={"index": index, "rate": tuple(rate)},
            )

        if not low_price <= open_price <= high_price:
            fail(
                "Нарушен OHLC-инвариант для open.",
                details={"index": index, "rate": tuple(rate)},
            )

        if not low_price <= close_price <= high_price:
            fail(
                "Нарушен OHLC-инвариант для close.",
                details={"index": index, "rate": tuple(rate)},
            )

        if tick_volume < 0 or real_volume < 0:
            fail(
                "Объём не может быть отрицательным.",
                details={"index": index, "rate": tuple(rate)},
            )

        if spread < 0:
            fail(
                "Spread не может быть отрицательным.",
                details={"index": index, "rate": tuple(rate)},
            )

        seen_timestamps.add(timestamp)
        previous_timestamp = timestamp


def main() -> int:
    print("MetaTrader5 Python package:", mt5.__version__)

    if not mt5.initialize():
        fail(
            "Не удалось подключиться к установленному терминалу MT5.",
            details=mt5.last_error(),
        )

    terminal_version = mt5.version()
    terminal_info = mt5.terminal_info()
    account_info = mt5.account_info()

    if terminal_version is None:
        fail("Не удалось получить версию терминала.", details=mt5.last_error())

    if terminal_info is None:
        fail("Не удалось получить информацию о терминале.", details=mt5.last_error())

    if account_info is None:
        fail(
            "Терминал подключён, но активный торговый счёт не найден.",
            details=mt5.last_error(),
        )

    symbol_info = mt5.symbol_info(SYMBOL)

    if symbol_info is None:
        available_symbols = mt5.symbols_get()

        similar_symbols: list[str] = []

        if available_symbols is not None:
            target = SYMBOL.upper()

            similar_symbols = sorted(
                symbol.name
                for symbol in available_symbols
                if target in symbol.name.upper()
            )

        fail(
            f"Символ {SYMBOL!r} не найден у брокера.",
            details={
                "last_error": mt5.last_error(),
                "similar_symbols": similar_symbols[:30],
            },
        )

    if not symbol_info.visible:
        if not mt5.symbol_select(SYMBOL, True):
            fail(
                f"Не удалось добавить {SYMBOL!r} в Market Watch.",
                details=mt5.last_error(),
            )
    latest_tick = mt5.symbol_info_tick(SYMBOL)

    if latest_tick is None:
        fail(
            f"Не удалось получить последний тик для {SYMBOL!r}.",
            details=mt5.last_error(),
        )

    latest_tick_utc = datetime.fromtimestamp(
        int(latest_tick.time),
        tz=timezone.utc,
    )
    now_utc = datetime.now(timezone.utc)

    # Начало текущего часа. Свеча, открытая в этот момент,
    # ещё может формироваться и в выборку не включается.
    current_hour_start = now_utc.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    requested_to = current_hour_start
    requested_from = requested_to - timedelta(days=LOOKBACK_DAYS)

    rates = mt5.copy_rates_range(
        SYMBOL,
        TIMEFRAME,
        requested_from,
        requested_to,
    )

    if rates is None:
        fail(
            "MT5 вернул ошибку при загрузке исторических свечей.",
            details=mt5.last_error(),
        )

    if len(rates) == 0:
        fail(
            "MT5 не вернул ни одной свечи.",
            details={
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME_NAME,
                "requested_from": requested_from.isoformat(),
                "requested_to": requested_to.isoformat(),
                "last_error": mt5.last_error(),
            },
        )

    # Защита от включения текущей формирующейся H1-свечи.
    closed_rates = rates[rates["time"] < int(current_hour_start.timestamp())]

    if len(closed_rates) == 0:
        fail("После удаления незакрытой свечи выборка стала пустой.")

    validate_rates(closed_rates)

    first_timestamp = datetime.fromtimestamp(
        int(closed_rates[0]["time"]),
        tz=timezone.utc,
    )

    last_timestamp = datetime.fromtimestamp(
        int(closed_rates[-1]["time"]),
        tz=timezone.utc,
    )

    provenance = {
        "data_source": "mt5",
        "broker_company": account_info.company,
        "broker_server": account_info.server,
        "account_login": account_info.login,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME_NAME,
        "requested_from_utc": requested_from.isoformat(),
        "requested_to_utc": requested_to.isoformat(),
                "actual_first_bar_utc": first_timestamp.isoformat(),
        "actual_last_bar_utc": last_timestamp.isoformat(),
        "latest_tick_utc": latest_tick_utc.isoformat(),
        "history_gap_hours": round(
            (requested_to - last_timestamp).total_seconds() / 3600,
            2,
        ),
        "bars_count": len(closed_rates),
        "retrieved_at_utc": now_utc.isoformat(),
        "terminal_version": terminal_version,
        "terminal_path": terminal_info.path,
        "mt5_package_version": mt5.__version__,
        "market_data_fingerprint": build_fingerprint(closed_rates),
    }
    output_path = (
        OUTPUT_DIR
        / f"{SYMBOL}_{TIMEFRAME_NAME}_{first_timestamp:%Y%m%d_%H%M}_{last_timestamp:%Y%m%d_%H%M}.csv"
    )

    save_rates_csv(closed_rates, output_path)

    provenance["csv_path"] = str(output_path.resolve())
    print()

    print("SUCCESS: MT5 historical market data loaded.")
    print()
    print(json.dumps(provenance, indent=2, ensure_ascii=False))

    print()
    print("First bar:")
    print(tuple(closed_rates[0]))

    print()
    print("Last bar:")
    print(tuple(closed_rates[-1]))

    mt5.shutdown()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        mt5.shutdown()
        print("\nInterrupted.")
        raise SystemExit(130)
    except Exception as exc:
        mt5.shutdown()
        print()
        print("UNEXPECTED ERROR:", repr(exc))
        raise