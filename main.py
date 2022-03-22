import argparse
from src.FileGenerator import generate_diploma

parser = argparse.ArgumentParser(description="Generating a League of Legends Diplom from a Summonername")
parser.add_argument("-n", "--name", type=str,  help="the summoner name to generate the diplom of")
parser.add_argument("-o", "--output", type=str, help="output directory for the pdf")
args = parser.parse_args()


def main():
    generate_diploma(args.name, args.output)


if __name__ == "__main__":
    main()
