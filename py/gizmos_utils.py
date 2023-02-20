from typing import Dict, Optional, Union

from common import Energy


def init_energy_num(energy_num: Optional[Dict[Energy, Union[int, None]]] = None) -> Dict[Energy, int]:
    return {
        'red': energy_num.get('red', 0) if energy_num is not None else 0,
        'black': energy_num.get('black', 0) if energy_num is not None else 0,
        'blue': energy_num.get('blue', 0) if energy_num is not None else 0,
        'yellow': energy_num.get('yellow', 0) if energy_num is not None else 0,
    }
