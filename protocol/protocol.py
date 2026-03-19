"""
Implementation of the PENIS protocol (Python 3.5 compatible)
"""
from enum import Enum
import re
import json


class InstructionType(Enum):
    COMMAND = "c_"
    SEQUENCE = "s_"
    REQUEST = "r_"


class CommandName(Enum):
    FORWARD = "fwd"
    BACKWARD = "bwd"
    TANK_LEFT = "tl"
    TANK_RIGHT = "tr"
    BALL_IN = "bin"
    BALL_OUT = "bout"
    BALL_OFF = "boff"
    TALK = "t"


class SequenceName(Enum):
    EJECT = "bust"


TALK_REGEX = re.compile(r"^[a-zA-Z0-9\.\,\ ]*$")


FIELD_ORDER = [
    "inst_id", "rspeed", "lspeed", "speed", 
    "rotations", "position", "seconds", "target_angle", 
    "brake", "block", "talk"
]


DEFAULTS = {
    "inst_id": "", "rspeed": 20, "lspeed": 20, "speed": 20, 
    "rotations": 5.0, "position": 10, "seconds": 1,
    "target_angle": 0, "brake": True, "block": False, "talk": ""
}


class Arguments(object):
    """Named tuple replacement for Python 3.5"""
    
    def __init__(self, inst_id=None, rspeed=None, lspeed=None, speed=None,
                 rotations=None, position=None, seconds=None, target_angle=None,
                 brake=None, block=None, talk=None):
        self.inst_id = inst_id or DEFAULTS["inst_id"]
        self.rspeed = int(rspeed or DEFAULTS["rspeed"])
        self.lspeed = int(lspeed or DEFAULTS["lspeed"])
        self.speed = int(speed or DEFAULTS["speed"])
        self.rotations = float(rotations or DEFAULTS["rotations"])
        self.position = int(position or DEFAULTS["position"])
        self.seconds = int(seconds or DEFAULTS["seconds"])
        self.target_angle = int(target_angle or DEFAULTS["target_angle"])
        self.brake = bool(brake) if brake is not None else DEFAULTS["brake"]
        self.block = bool(block) if block is not None else DEFAULTS["block"]
        self.talk = talk or DEFAULTS["talk"]
    
    def __eq__(self, other):
        if not isinstance(other, Arguments):
            return False
        return (self.inst_id == other.inst_id and
                self.rspeed == other.rspeed and
                self.lspeed == other.lspeed and
                self.speed == other.speed and
                self.rotations == other.rotations and
                self.position == other.position and
                self.seconds == other.seconds and
                self.target_angle == other.target_angle and
                self.brake == other.brake and
                self.block == other.block and
                self.talk == other.talk)


class Instruction(object):
    def __init__(self, name, type_, args=None):
        self.name = name
        self.type = type_
        self.args = args or Arguments()
    
    def __eq__(self, other):
        if not isinstance(other, Instruction):
            return False
        return (self.name == other.name and
                self.type == other.type and
                self.args == other.args)


class Message(object):
    def __init__(self, instruction):
        self.instruction = instruction
    
    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        return self.instruction == other.instruction


class Acknowledgement(object):
    def __init__(self, status, data=None):
        if status not in ("ACK", "NAK"):
            raise ValueError("Status must be 'ACK' or 'NAK'")
        self.status = status
        self.data = data or {}
    
    def __eq__(self, other):
        if not isinstance(other, Acknowledgement):
            return False
        return self.status == other.status and self.data == other.data


def serialize_arguments(args):
    """Serialize a PENIS arguments instance"""
    # Default is "", when that arg isnt provided
    values = [str(getattr(args, field, "")) for field in FIELD_ORDER[:-1]] + [args.talk]
    return ";".join(values)


def serialize_message(message):
    """Serialize a PENIS message"""
    instruction = message.instruction
    return "{}{}:{}\n".format(
        instruction.type.value,
        instruction.name.value,
        serialize_arguments(instruction.args)
    )


def parse_arguments(raw_parts):
    """Parse a serialized PENIS arguments instance"""
    if len(raw_parts) != 11:
        raise ValueError("Expected 11 arguments, got {}".format(len(raw_parts)))
    
    try:
        return Arguments(
            inst_id=raw_parts[0] or DEFAULTS["inst_id"],
            rspeed=raw_parts[1] or DEFAULTS["rspeed"],
            lspeed=raw_parts[2] or DEFAULTS["lspeed"],
            speed=raw_parts[3] or DEFAULTS["speed"],
            rotations=raw_parts[4] or DEFAULTS["rotations"],
            position=raw_parts[5] or DEFAULTS["position"],
            seconds=raw_parts[6] or DEFAULTS["seconds"],
            target_angle=raw_parts[7] or DEFAULTS["target_angle"],
            brake=raw_parts[8] == 'True' if raw_parts[8] else None,
            block=raw_parts[9] == 'True' if raw_parts[9] else None,
            talk=raw_parts[10] or DEFAULTS["talk"]
        )
    except (ValueError, IndexError) as e:
        raise ValueError("Failed to parse arguments: {}".format(e))


def parse_message(raw):
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
    instruction = Instruction(name=name, type_=instruction_type, args=args)
    return Message(instruction=instruction)


def serialize_ack(ack):
    """Serialize an acknowledgement"""
    data_str = json.dumps(ack.data)
    return "{} {}\n".format(ack.status, data_str)


def parse_ack(raw):
    """Parse a serialized acknowledgement"""
    if not raw.endswith('\n'):
        raise ValueError("ACK must end with newline")
    
    parts = raw.rstrip('\n').split(' ', 1)
    status = parts[0]
    
    if status not in ("ACK", "NAK"):
        raise ValueError("Invalid status: {}".format(status))
    
    data = {}
    if len(parts) > 1:
        try:
            data = json.loads(parts[1])
        except ValueError:
            raise ValueError("Invalid JSON in ACK data")
    
    return Acknowledgement(status=status, data=data)