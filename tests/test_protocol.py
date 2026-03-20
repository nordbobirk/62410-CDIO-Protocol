"""
PENIS unit tests
Run: python -m unittest test_protocol.py
"""
import unittest
from protocol import (
    CommandName, Instruction, Arguments, InstructionType,
    serialize_message, parse_message, serialize_arguments,
    Message, Acknowledgement, serialize_ack, parse_ack,
    parse_arguments
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

    def test_parse_arguments(self):
        serialized = ";20;20;20;5.0;10;1;0;True;False;"
        expected = Arguments()
        arguments = parse_arguments(serialized.split(";"))
        self.assertEqual(arguments.inst_id, expected.inst_id)
        self.assertEqual(arguments.rspeed, expected.rspeed)
        self.assertEqual(arguments.lspeed, expected.lspeed)
        self.assertEqual(arguments.speed, expected.speed)
        self.assertEqual(arguments.rotations, expected.rotations)
        self.assertEqual(arguments.position, expected.position)
        self.assertEqual(arguments.seconds, expected.seconds)
        self.assertEqual(arguments.target_angle, expected.target_angle)
        self.assertEqual(arguments.brake, expected.brake)
        self.assertEqual(arguments.block, expected.block)
        self.assertEqual(arguments.talk, expected.talk)

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
    
    def test_parse_message(self):
        serialized_message = "c_fwd:;20;20;20;5.0;10;1;0;True;False;\n"
        message = parse_message(serialized_message)
        instruction = message.instruction
        arguments = instruction.args
        self.assertEqual(instruction.name, CommandName.FORWARD.value)
        self.assertEqual(instruction.type, InstructionType.COMMAND.value)
        self.assertEqual(arguments.rspeed, 20)
        self.assertEqual(arguments.lspeed, 20)
        self.assertEqual(arguments.speed, 20)
        self.assertEqual(arguments.rotations, 5.0)
        self.assertEqual(arguments.position, 10)
        self.assertEqual(arguments.seconds, 1)
        self.assertEqual(arguments.target_angle, 0)
        self.assertEqual(arguments.brake, True)
        self.assertEqual(arguments.block, False)
        self.assertEqual(arguments.talk, "")
    
    def test_parse_acknowledgement(self):
        serialized_ack = "ACK {\"key\": \"value\"}\n"
        ack = parse_ack(serialized_ack)
        expected = Acknowledgement("ACK", { "key": "value" })
        self.assertEqual(ack.status, expected.status)
        self.assertEqual(ack.data, expected.data)

        serialized_nak = "NAK {\"key\": \"value\"}\n"
        nak = parse_ack(serialized_nak)
        expected = Acknowledgement("NAK", { "key": "value"} )
        self.assertEqual(nak.status, expected.status)
        self.assertEqual(nak.data, expected.data)

        serialized_ack_no_data = "ACK {}\n"
        ack_no_data = parse_ack(serialized_ack_no_data)
        expected = Acknowledgement("ACK")
        self.assertEqual(ack_no_data.status, expected.status)
        self.assertEqual(ack_no_data.data, expected.data)

        serialized_nak_no_data = "NAK {}\n"
        nak_no_data = parse_ack(serialized_nak_no_data)
        expected = Acknowledgement("NAK")
        self.assertEqual(nak_no_data.status, expected.status)
        self.assertEqual(nak_no_data.data, expected.data)

    # endregion parsing

    # region roundtrip

    def test_roundtrip_forward(self):
        """c_fwd serializes → parses back identically"""
        instruction = Instruction(
            name = CommandName.FORWARD,
            type = InstructionType.COMMAND,
            args = Arguments(speed=50, seconds=2)
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
