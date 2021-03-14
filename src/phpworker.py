import sys
import site_globals
from parts_composer import compose_zemin, compose_nakarat, compose_meyan, song_2_mus


def main():
    makam = sys.argv[1]
    notes = sys.argv[2]
    notes = [x.strip().replace('-', '/') for x in notes.strip('][').split(',')]
    res = compose_zemin(makam, notes)
    with open(site_globals.src_root + 'res_file.txt', 'w') as res_file:
        res_file.write(str(res))


if __name__ == '__main__':
    main()
