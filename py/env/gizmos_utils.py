from .common import Energy


def init_energy_num(energy_num: dict[Energy, int | None] | None = None) -> dict[Energy, int]:
    return {
        'red': energy_num.get('red', 0) if energy_num is not None else 0,
        'black': energy_num.get('black', 0) if energy_num is not None else 0,
        'blue': energy_num.get('blue', 0) if energy_num is not None else 0,
        'yellow': energy_num.get('yellow', 0) if energy_num is not None else 0,
    }
