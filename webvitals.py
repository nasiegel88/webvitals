import argparse, pathlib

from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument('-l', '--list', help='delimited list input', type=str)

parser.add_argument('-f', '--file', help='text input', type=pathlib.Path)

args = parser.parse_args()


if args.file is not None and args.list is not None:
    
    parser.error("Choose --list or --file but not both!")
    
elif args.file is not None:

    with args.file.open('r') as file:
        file_content = file.read()
        arg_list = file_content.split("\n")
        
elif args.list is not None:

    arg_list = [str(item) for item in args.list.split(',')]
    
print(arg_list)

