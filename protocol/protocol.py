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
        if self.inst_id != "":
            raise ValueError("Instruction id is currently reserved and must be an empty string.")
        if self.rspeed > 100 or self.rspeed < -100:
            raise ValueError("Right speed must be within [-100;100], received {}.".format(self.rspeed))
        if self.lspeed > 100 or self.lspeed < -100:
            raise ValueError("Left speed must be within [-100;100], received {}.".format(self.lspeed))
        if self.speed > 100 or self.speed < -100:
            raise ValueError("Speed must be within [-100;100], received {}.".format(self.speed))
        if self.seconds < 0:
            raise ValueError("Seconds must be a non-negative integer, received {}".format(self.seconds))
        if self.target_angle > 360 or self.target_angle < -360:
            raise ValueError("Target angle must be within [-360;360], received {}".format(self.target_angle))
        if TALK_REGEX.search(self.talk) == None and self.talk != "":
            raise ValueError("Talk must only include alphanumeric characters as well as the dot, comma, and space characters.")

class Instruction(object):
    def __init__(self, name, type, args=None):
        if not isinstance(type, InstructionType):
            raise ValueError("Instruction type must be an InstructionType member, got {}.".format(type))

        self.type = type
        self.args = args or Arguments()

        if self.type == InstructionType.COMMAND:
            if not isinstance(name, CommandName):
                raise ValueError("Command instruction name must be a CommandName member, got {}.".format(name))
            self.name = name

        elif self.type == InstructionType.SEQUENCE:
            if not isinstance(name, SequenceName):
                raise ValueError("Sequence instruction name must be a SequenceName member, got {}.".format(name))
            self.name = name

        elif self.type == InstructionType.REQUEST:
            if not isinstance(name, str):
                raise ValueError("Request instruction name must be a string, got {}.".format(name))
            self.name = name

        else:
            raise ValueError("Unknown instruction type {}.".format(self.type))

        self.assert_valid()

    def assert_valid(self):
        if not isinstance(self.type, InstructionType):
            raise ValueError("Unknown instruction type {}.".format(self.type))

        if self.type == InstructionType.COMMAND:
            if not isinstance(self.name, CommandName):
                raise ValueError("Unknown command name {}.".format(self.name))

        elif self.type == InstructionType.SEQUENCE:
            if not isinstance(self.name, SequenceName):
                raise ValueError("Unknown sequence name {}.".format(self.name))

        elif self.type == InstructionType.REQUEST:
            if "ev3_" not in self.name:
                raise ValueError("Unknown request name {}, missing prefix.".format(self.name))

class Message(object):
    def __init__(self, instruction):
        self.instruction = instruction

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
    name = instruction.name.value if isinstance(instruction.name, Enum) else instruction.name
    return "{}{}:{}".format(
        instruction.type.value,
        name,
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
    line = raw
    if ':' not in line:
        raise ValueError("Missing ':' after instruction name")

    type_name, args_str = line.split(':', 1)
    arg_parts = args_str.split(';')

    prefix = type_name[:2]
    raw_name = type_name[2:]

    args = parse_arguments(arg_parts)

    try:
        instruction_type = InstructionType(prefix)
    except ValueError:
        raise ValueError("Unknown instruction type {}.".format(prefix))

    if instruction_type == InstructionType.COMMAND:
        try:
            name = CommandName(raw_name)
        except ValueError:
            raise ValueError("Unknown command name {}.".format(raw_name))

    elif instruction_type == InstructionType.SEQUENCE:
        try:
            name = SequenceName(raw_name)
        except ValueError:
            raise ValueError("Unknown sequence name {}.".format(raw_name))

    elif instruction_type == InstructionType.REQUEST:
        name = raw_name

    else:
        raise ValueError("Unknown instruction type {}.".format(prefix))

    instruction = Instruction(name=name, type=instruction_type, args=args)
    return Message(instruction=instruction)

def serialize_ack(ack):
    """Serialize an acknowledgement"""
    data_str = json.dumps(ack.data)
    return "{} {}".format(ack.status, data_str)

def parse_ack(raw):
    """Parse a serialized acknowledgement"""
    
    parts = raw.split(' ', 1)
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
