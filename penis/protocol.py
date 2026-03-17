"""
PENIS Protocol - Complete implementation with per-command validation
"""
from dataclasses import dataclass
from typing import Dict, Any, Literal
from enum import Enum
import re
import json
from pydantic import BaseModel, Field, validator, ValidationError

class InstructionType(str, Enum):
    COMMAND = "c_"
    SEQUENCE = "s_"
    REQUEST = "r_"

class CommandName(str, Enum):
    FWD = "fwd"
    BWD = "bwd"
    TL = "tl"
    TR = "tr"
    BIN = "bin"
    BOUT = "bout"
    BOFF = "boff"
    TALK = "t"

class SequenceName(str, Enum):
    BUST = "bust"

TALK_REGEX = re.compile(r"^[a-zA-Z0-9\.\,\ ]+$")

@dataclass(frozen=True)
class PENISArguments:
    inst_id: str = ""         # 0
    rspeed: int = 0           # 1
    lspeed: int = 0           # 2
    speed: int = 0            # 3
    rotations: int = 0        # 4
    position: int = 0         # 5
    seconds: int = 0          # 6
    target_angle: int = 0     # 7
    brake: bool = False       # 8
    block: bool = False       # 9
    talk: str = ""            # 10

class PENISInstruction(BaseModel):
    name: str
    args: PENISArguments = Field(default_factory=PENISArguments)
    
    @validator('name')
    def validate_name(cls, v):
        if not any(v.startswith(prefix) for prefix in ['c_', 's_', 'r_']):
            raise ValueError("Name must start with 'c_', 's_', or 'r_'")
        return v
    
    @validator('args')
    def validate_talk(cls, args, values):
        name = values.get('name')
        if name and name == 'c_t' and not TALK_REGEX.fullmatch(args.talk):
            raise ValueError("talk must match /^[a-zA-Z0-9., ]+$/")
        return args
    
    @validator('args')
    def validate_command_args(cls, args, values):
        name = values.get('name')
        if not name or not name.startswith('c_'):
            return args
        
        cmd = name[2:]  # Remove "c_" prefix
        
        # Helper to get first non-zero extent arg by precedence
        def get_extent_arg(extents):
            for extent in extents:
                if getattr(args, extent) != 0:
                    return extent
            return None
        
        if cmd == CommandName.FWD:
            if args.speed == 0:
                raise ValueError("fwd requires speed > 0")
            extent = get_extent_arg(['seconds', 'rotations', 'position'])
            # No validation needed beyond speed > 0
            
        elif cmd == CommandName.BWD:
            if args.speed == 0:
                raise ValueError("bwd requires speed > 0")
            extent = get_extent_arg(['seconds', 'rotations', 'position'])
            
        elif cmd in (CommandName.TL, CommandName.TR):
            # speed -> gyro turn, else lspeed/rspeed -> tank turn
            if args.speed > 0:
                # Gyro turn mode
                if get_extent_arg(['target_angle', 'seconds', 'rotations', 'position']) is None:
                    raise ValueError(f"{cmd}: gyro turn requires target_angle, seconds, rotations, or position")
            elif args.lspeed > 0 or args.rspeed > 0:
                # Tank turn mode
                if get_extent_arg(['seconds', 'rotations', 'position']) is None:
                    raise ValueError(f"{cmd}: tank turn requires seconds, rotations, or position")
            else:
                raise ValueError(f"{cmd}: requires either speed > 0 (gyro) or lspeed/rspeed > 0 (tank)")
                
        elif cmd == CommandName.BIN:
            if args.speed == 0:
                raise ValueError("bin requires speed > 0")
            # seconds or rotations optional
            
        elif cmd == CommandName.BOUT:
            if args.speed == 0:
                raise ValueError("bout requires speed > 0")
            extent = get_extent_arg(['seconds', 'rotations', 'position'])
            
        elif cmd == CommandName.BOFF:
            pass  # No args required beyond brake/block
            
        elif cmd == CommandName.TALK:
            if not args.talk:
                raise ValueError("talk requires non-empty talk message")
            
        else:
            raise ValueError(f"Unknown command: {cmd}")
            
        return args

class PENISMessage(BaseModel):
    instruction: PENISInstruction

class PENISAck(BaseModel):
    status: Literal["ACK", "NAK"]
    data: Dict[str, Any] = Field(default_factory=dict)

def serialize_message(instruction: PENISInstruction) -> str:
    """PENISInstruction → wire format"""

    args = instruction.args
    args_str = (
        f"{args.inst_id};"
        f"{args.rspeed};"
        f"{args.lspeed};"
        f"{args.speed};"
        f"{args.rotations};"
        f"{args.position};"
        f"{args.seconds};"
        f"{args.target_angle};"
        f"{str(args.brake).lower()};"
        f"{str(args.block).lower()};"
        f"{args.talk}"
    )
    return f"{instruction.name}:{args_str}\n"

def deserialize_message(raw: str) -> PENISMessage:
    """wire format → PENISMessage (with validation)"""

    if not raw.endswith('\n'):
        raise ValueError("Message must end with newline")
    
    line = raw.rstrip('\n')
    if ':' not in line:
        raise ValueError("Missing ':' after instruction name")
    
    name, args_str = line.split(':', 1)
    arg_parts = args_str.split(';')
    
    if len(arg_parts) != 11:
        raise ValueError(f"Expected 11 arguments, got {len(arg_parts)}")
    
    try:
        args = PENISArguments(
            inst_id=int(arg_parts[0] or 0),
            rspeed=int(arg_parts[1] or 0),
            lspeed=int(arg_parts[2] or 0),
            speed=int(arg_parts[3] or 0),
            rotations=int(arg_parts[4] or 0),
            position=int(arg_parts[5] or 0),
            seconds=int(arg_parts[6] or 0),
            target_angle=int(arg_parts[7] or 0),
            brake=arg_parts[8].lower() == 'true',
            block=arg_parts[9].lower() == 'true',
            talk=arg_parts[10]
        )
    except (ValueError, IndexError) as e:
        raise ValueError(f"Failed to parse arguments: {e}")
    
    try:
        instruction = PENISInstruction(name=name, args=args)
        return PENISMessage(instruction=instruction)
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e}")

def serialize_ack(status: Literal["ACK", "NAK"], data: Dict[str, Any] = None) -> str:
    """PENISAck → wire format"""

    data_str = json.dumps(data or {}) 
    return f"{status} {data_str}\n"

def deserialize_ack(raw: str) -> PENISAck:
    """wire format → PENISAck"""

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
    
    return PENISAck(status=status, data=data)
