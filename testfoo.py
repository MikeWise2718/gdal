import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--foo", default=argparse.SUPPRESS)
ns = parser.parse_args()

print("Parsed arguments: {}".format(ns))
print("foo in namespace?: {}".format("foo" in ns))