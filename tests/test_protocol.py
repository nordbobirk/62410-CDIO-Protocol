"""
PENIS unit tests
Run: python -m unittest test_protocol.py
"""
import unittest
from protocol import (
    CommandName, Instruction, Arguments, InstructionType,
    serialize_message, parse_message, serialize_arguments,
    Message
)

class TestPENISProtocol(unittest.TestCase):
    
    # region serialization

    def test_serialize_arguments(self):
        arguments = Arguments()
        serialized = serialize_arguments(arguments)
        self.assertEqual(serialized, ";20;20;20;5.0;10;1;0;True;False;")

        custom_arguments = Arguments(
            inst_id="inst_id",
            rspeed=0,
            lspeed=0,
            speed=0,
            rotations=0.0,
            position=0,
            seconds=0,
            target_angle=360,
            brake=False,
            block=True,
            talk="yeet",
        )
        custom_serialized = serialize_arguments(custom_arguments)
        self.assertEqual(custom_arguments.rspeed, 0)
        self.assertEqual(custom_serialized, "inst_id;0;0;0;0.0;0;0;360;False;True;yeet")

    def test_serialize_message(self):
        message = Message(instruction = Instruction(name = CommandName.FORWARD, type = InstructionType.COMMAND, args = Arguments()))
        serialized = serialize_message(message)
        self.assertEqual(serialized, "c_fwd:;20;20;20;5.0;10;1;0;True;False;\n")

    # endregion serialization

    # region parsing

    # endregion parsing

    # region roundtrip

    def test_roundtrip_forward(self):
        """c_fwd serializes → parses back identically"""
        instruction = Instruction(
            name=CommandName.FORWARD,
            type=InstructionType.COMMAND,
            args=Arguments(speed=50, seconds=2)
        )
        wire = serialize_message(message = Message(instruction = instruction))
        roundtrip = parse_message(wire)
        
        self.assertEqual(roundtrip.instruction.name, CommandName.FORWARD.value)
        self.assertEqual(roundtrip.instruction.args.speed, 50)
        self.assertEqual(roundtrip.instruction.args.seconds, 2)
        self.assertEqual(roundtrip.instruction.type, InstructionType.COMMAND.value)

    # endregion roundtrip

if __name__ == '__main__':
    unittest.main()
