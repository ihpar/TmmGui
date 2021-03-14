import sys
from parts_composer import compose_zemin, compose_nakarat, compose_meyan, song_2_mus


def main():
    makam = sys.argv[1]
    notes = sys.argv[2]
    notes = [x.strip().replace('-', '/') for x in notes.strip('][').split(',')]
    res = compose_zemin(makam, notes)
    print('+-+', makam, '+-+', str(notes), '+-+', str(res), '+-+')


if __name__ == '__main__':
    main()
