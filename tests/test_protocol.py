"""
PENIS unit tests
Run: python -m unittest test_protocol.py
"""
import unittest
from protocol import (
    CommandName, Instruction, Arguments, InstructionType,
    serialize_message, parse_message, serialize_arguments,
    Message, Acknowledgement, serialize_ack
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

    def test_serialize_ack(self):
        ack = Acknowledgement("ACK", { "key": "value" })
        serialized_ack = serialize_ack(ack)
        self.assertEqual(serialized_ack, "ACK {\"key\": \"value\"}\n")

        nak = Acknowledgement("NAK", { "key": "value"} )
        serialized_nak = serialize_ack(nak)
        self.assertEqual(serialized_nak, "NAK {\"key\": \"value\"}\n")

        ack_no_data = Acknowledgement("ACK")
        serialized_ack_no_data = serialize_ack(ack_no_data)
        self.assertEqual(serialized_ack_no_data, "ACK {}\n")

        nak_no_data = Acknowledgement("NAK")
        serialized_nak_no_data = serialize_ack(nak_no_data)
        self.assertEqual(serialized_nak_no_data, "NAK {}\n")

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

    # region validation

    # endregion validation

if __name__ == '__main__':
    unittest.main()
