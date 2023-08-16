import yaml
import argparse

def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("settings")
    parser.add_argument("compiler_version")
    return parser


def main():
    parser = get_arg_parser()
    args = parser.parse_args()
    with open(args.settings) as fp:
        data = yaml.safe_load(fp)
    if args.compiler_version not in data['compiler']['gcc']['version']:
        data['compiler']['gcc']['version'].append(args.compiler_version)
        with open(args.settings, "w") as fp:
            yaml.dump(data, fp)
        print(f"Updated {args.settings}")

if __name__ == '__main__':
    main()