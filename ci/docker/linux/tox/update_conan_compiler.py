import argparse
import yaml


def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("settings_file")
    parser.add_argument("compiler_name")
    parser.add_argument("compiler_version")
    return parser


def update_settings_file(settings_file, compiler_name, compiler_version):
    with open(settings_file) as file:
        data = yaml.safe_load(file)
    if compiler_name not in data['compiler']:
        raise ValueError(f"invalid compiler name: {compiler_name}")

    if compiler_version not in data['compiler'][compiler_name]['version']:
        data['compiler'][compiler_name]['version'].append(compiler_version)
        print("Compiler data added")
        print(data['compiler'][compiler_name]['version'])
    with open(settings_file, 'w') as file:
        yaml.dump(data, file)

def main():
    args = get_arg_parser().parse_args()
    print(args)
    update_settings_file(
        args.settings_file,
        args.compiler_name,
        args.compiler_version

    )

if __name__ == '__main__':
    main()
