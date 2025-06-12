def main():
    try:
        from py3exiv2bind import core
        print(f'Testing against exiv2 version {core.exiv2_version()}')
    except ImportError:
        print("py3exiv2bind.core is not built")
        return

if __name__ == '__main__':
    main()