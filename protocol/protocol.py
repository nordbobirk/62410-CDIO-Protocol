"""
Implementation of the PENIS
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Literal
from enum import Enum
import re
import json

class InstructionType(str, Enum):
    COMMAND = "c_"
    SEQUENCE = "s_"
    REQUEST = "r_"

class CommandName(str, Enum):
    FORWARD = "fwd"
    BACKWARD = "bwd"
    TANK_LEFT = "tl"
    TANK_RIGHT = "tr"
    BALL_IN = "bin"
    BALL_OUT = "bout"
    BALL_OFF = "boff"
    TALK = "t"

class SequenceName(str, Enum):
    EJECT = "bust"

TALK_REGEX = re.compile(r"^[a-zA-Z0-9\.\,\ ]*$")

FIELD_ORDER = [
    "inst_id", "rspeed", "lspeed", "speed", 
    "rotations", "position", "seconds", "target_angle", 
    "brake", "block", "talk"
]

DEFAULTS = {
    "inst_id": "", "rspeed": 20, "lspeed":20, "speed":20, 
    "rotations": float(5), "position": 10, "seconds": 1,
    "target_angle": 0, "brake": True, "block": False, "talk": ""
}

@dataclass(frozen=True)
class Arguments:
    inst_id: str = field(default_factory=lambda: DEFAULTS["inst_id"])
    rspeed: int = field(default_factory=lambda: DEFAULTS["rspeed"])
    lspeed: int = field(default_factory=lambda: DEFAULTS["lspeed"])
    speed: int = field(default_factory=lambda: DEFAULTS["speed"])
    rotations: float = field(default_factory=lambda: DEFAULTS["rotations"])
    position: int = field(default_factory=lambda: DEFAULTS["position"])
    seconds: int = field(default_factory=lambda: DEFAULTS["seconds"])
    target_angle: int = field(default_factory=lambda: DEFAULTS["target_angle"])
    brake: bool = field(default_factory=lambda: DEFAULTS["brake"])
    block: bool = field(default_factory=lambda: DEFAULTS["block"])
    talk: str = field(default_factory=lambda: DEFAULTS["talk"])

@dataclass(frozen=True)
class Instruction:
    name: str
    type: InstructionType
    args: Arguments = field(default_factory=Arguments)

@dataclass(frozen=True)
class Message:
    instruction: Instruction

@dataclass(frozen=True)
class Acknowledgement:
    status: Literal["ACK", "NAK"]
    data: Dict[str, Any] = field(default_factory=dict)

def serialize_arguments(args: Arguments) -> str:
    """Serialize a PENIS arguments instance"""
    values = [str(getattr(args, field)) for field in FIELD_ORDER[:-1]] + [args.talk]
    return ";".join(values)

def serialize_message(message: Message) -> str:
    """Serialize a PENIS message"""
    instruction = message.instruction
    return f"{instruction.type.value}{instruction.name.value}:{serialize_arguments(instruction.args)}\n"

def parse_arguments(raw_parts: list[str]) -> Arguments:
    """Parse a serialized PENIS arguments instance"""
    if len(raw_parts) != 11:
        raise ValueError(f"Expected 11 arguments, got {len(raw_parts)}")
    
    try:
        return Arguments(
            inst_id=raw_parts[0] or DEFAULTS["inst_id"],
            rspeed=int(raw_parts[1] or DEFAULTS["rspeed"]),
            lspeed=int(raw_parts[2] or DEFAULTS["lspeed"]),
            speed=int(raw_parts[3] or DEFAULTS["speed"]),
            rotations=float(raw_parts[4] or DEFAULTS["rotations"]),
            position=int(raw_parts[5] or DEFAULTS["position"]),
            seconds=int(raw_parts[6] or DEFAULTS["seconds"]),
            target_angle=int(raw_parts[7] or DEFAULTS["target_angle"]),
            brake=raw_parts[8] == 'True' or DEFAULTS["brake"],
            block=raw_parts[9] == 'True' or DEFAULTS["block"],
            talk=raw_parts[10] or DEFAULTS["talk"]
        )
    except (ValueError, IndexError) as e:
        raise ValueError(f"Failed to parse arguments: {e}")

def parse_message(raw: str) -> Message:
    """Parse a serialized PENIS message"""
    if not raw.endswith('\n'):
        raise ValueError("Message must end with newline")
    
    line = raw.rstrip('\n')
    if ':' not in line:
        raise ValueError("Missing ':' after instruction name")
    
    type_name, args_str = line.split(':', 1)
    arg_parts = args_str.split(';')
    
    prefix = type_name[:2]
    name = type_name[2:]
    
    args = parse_arguments(arg_parts)
    
    instruction_type = next(t for t in InstructionType if t.value == prefix)
    instruction = Instruction(name=name, type=instruction_type, args=args)
    return Message(instruction=instruction)

def serialize_ack(ack: Acknowledgement) -> str:
    """Serialize an acknowledgement"""

    data_str = json.dumps(ack.data or {}) 
    return f"{ack.status} {data_str}\n"

def parse_ack(raw: str) -> Acknowledgement:
    """Parse a serialized acknowledgement"""

    if not raw.endswith('\n'):
        raise ValueError("ACK must end with newline")
    
    parts = raw.rstrip('\n').split(' ', 1)
    status = parts[0]
    
    if status not in ("ACK", "NAK"):
        raise ValueError(f"Invalid status: {status}")
    
    data = {}
    if len(parts) > 1:
        try:
            data = json.loads(parts[1])
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in ACK data")
    
    return Acknowledgement(status=status, data=data)
