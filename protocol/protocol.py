"""
Implementation of the PENIS (python 3.5 compatible)
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
    def __init__(self, inst_id=None, rspeed=None, lspeed=None, speed=None,
                 rotations=None, position=None, seconds=None, target_angle=None,
                 brake=None, block=None, talk=None):
        self.inst_id = inst_id or DEFAULTS["inst_id"]
        self.rspeed = int(rspeed if rspeed is not None else DEFAULTS["rspeed"])
        self.lspeed = int(lspeed if lspeed is not None else DEFAULTS["lspeed"])
        self.speed = int(speed if speed is not None else DEFAULTS["speed"])
        self.rotations = float(rotations if rotations is not None else DEFAULTS["rotations"])
        self.position = int(position if position is not None else DEFAULTS["position"])
        self.seconds = int(seconds if seconds is not None else DEFAULTS["seconds"])
        self.target_angle = int(target_angle if target_angle is not None else DEFAULTS["target_angle"])
        self.brake = bool(brake) if brake is not None else DEFAULTS["brake"]
        self.block = bool(block) if block is not None else DEFAULTS["block"]
        self.talk = talk or DEFAULTS["talk"]
        self.assert_valid()

    def assert_valid(self):
        pass

class Instruction(object):
    def __init__(self, name, type, args=None):
        self.name = name.value if isinstance(name, CommandName) or isinstance(name, SequenceName) else name
        self.type = type.value if isinstance(type, InstructionType) else type
        self.args = args or Arguments()
        self.assert_valid()

    def assert_valid(self):
        pass

class Message(object):
    def __init__(self, instruction):
        self.instruction = instruction
        self.assert_valid()

    def assert_valid(self):
        pass

class Acknowledgement(object):
    def __init__(self, status, data = None):
        self.status = status
        self.data = data or {}
        self.assert_valid()

    def assert_valid(self):
        if self.status not in ("ACK", "NAK"):
            raise ValueError("Unknown status {}, expect 'ACK' or 'NAK'.".format(self.status))
        try:
            json.dumps(self.data)
        except:
            raise ValueError("Data must be valid JSON.")

def serialize_arguments(args):
    """Serialize a PENIS arguments instance"""
    values = [str(getattr(args, field, DEFAULTS[field])) for field in FIELD_ORDER[:-1]] + [args.talk]
    return ";".join(values)

def serialize_message(message):
    """Serialize a PENIS message"""
    instruction = message.instruction
    return "{}{}:{}\n".format(
        instruction.type,
        instruction.name,
        serialize_arguments(instruction.args)
    )

def parse_arguments(raw_parts):
    """Parse a serialized PENIS arguments instance"""
    if len(raw_parts) != 11:
        raise ValueError("Expected 11 arguments, got {}".format(len(raw_parts)))
    
    try:
        # defaults handled by Arguments.__init__
        return Arguments(
            inst_id=raw_parts[0],
            rspeed=raw_parts[1],
            lspeed=raw_parts[2],
            speed=raw_parts[3],
            rotations=raw_parts[4],
            position=raw_parts[5],
            seconds=raw_parts[6],
            target_angle=raw_parts[7],
            brake=raw_parts[8] == 'True' if raw_parts[8] else None, # if argument not given, set None - allows Arguments.__init__ to handle default value
            block=raw_parts[9] == 'True' if raw_parts[9] else None, # if argument not given, set None - allows Arguments.__init__ to handle default value
            talk=raw_parts[10],
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
    instruction = Instruction(name = name, type = instruction_type, args = args)
    return Message(instruction = instruction)

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
        raise ValueError("Unknown status {}, expected 'ACK' or 'NAK'.".format(status))
    
    data = {}
    if len(parts) > 1:
        try:
            data = json.loads(parts[1])
        except ValueError:
            raise ValueError("Invalid JSON in ACK data")
    
    return Acknowledgement(status=status, data=data)
