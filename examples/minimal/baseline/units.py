"""Unit-carrying scalar types. The unit is in the type name, never in a comment
(CORE-CON-001). A quantity crossing a module boundary uses one of these."""
from typing import NewType

Metres = NewType("Metres", float)
Seconds = NewType("Seconds", float)
MetresPerSecond = NewType("MetresPerSecond", float)
Radians = NewType("Radians", float)
KgPerM3 = NewType("KgPerM3", float)
