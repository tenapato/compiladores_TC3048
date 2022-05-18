import os
import argparse

from aSintactico import ParseManager

argument_parser = argparse.ArgumentParser(usage='python3 -m app [-h] [arguments]')
argument_parser.add_argument('input_file', metavar='input_file', type=str,
                             help='input file path')
argument_parser.add_argument('output_file', metavar='output_file', type=str,
                             help='output file path', default="", nargs='?')


def execute():
    args = argument_parser.parse_args()
    input_name = args.input_file
    output_name = args.output_file
    parseManager = ParseManager()
    try:
        in_file = open(input_name)
        if len(output_name) == 0:
            file_name = os.path.basename(input_name)
            output_name = os.path.splitext(file_name)[0] + ".out"
        content = in_file.read()
        parser = parseManager.build()
        errors = parseManager.lexManager.errors + parseManager.errors
        if len(errors) == 0:
            print("No hay errores")
            tree = parser.parse(content)
        else:
            for e in errors:
                print(e)
            raise Exception("{} Errores encontrados".format(str(len(errors))))
    except FileNotFoundError:
        print("{} archivo no encontrado".format(input_name))

if __name__ == "__main__":
    execute()
