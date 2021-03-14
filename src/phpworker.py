import sys
import site_globals
import numpy as np
from parts_composer import compose_zemin, compose_nakarat, compose_meyan, song_2_mus


def main():
    unique_id = sys.argv[1]
    makam = sys.argv[2]
    notes = sys.argv[3]
    notes = [x.strip().replace('-', '/') for x in notes.strip('][').split(',')]

    with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'w') as res_file:
        res_file.write('begin')

    res = compose_zemin(makam, notes)

    if res['type'] == 'error':
        with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'w') as res_file:
            res_file.write('zemin ERR')
            return

    with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'a') as res_file:
        res_file.write('\nzemin')

    makam = res['makam']
    dir_path = res['dir_path']
    set_size = res['set_size']
    measure_cnt = res['measure_cnt']
    note_dict = res['note_dict']
    oh_manager = res['oh_manager']
    time_sig = res['time_sig']
    part_a = res['part_a']

    res = compose_nakarat(makam, dir_path, set_size, measure_cnt, note_dict, oh_manager, time_sig, part_a)
    if res['type'] == 'error':
        with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'w') as res_file:
            res_file.write('nakarat ERR')
            return

    with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'a') as res_file:
        res_file.write('\nnakarat')

    part_b = res['part_b']
    second_rep = res['second_rep']

    res = compose_meyan(makam, dir_path, set_size, measure_cnt, note_dict, oh_manager, time_sig, part_b)
    if res['type'] == 'error':
        with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'w') as res_file:
            res_file.write('meyan ERR')
            return

    with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'a') as res_file:
        res_file.write('\nmeyan')

    part_c = res['part_c']

    song = np.append(part_a, part_b, axis=1)
    song = np.append(song, part_c, axis=1)
    song_name = makam + '-' + unique_id
    song_2_mus(song, makam, song_name, oh_manager, note_dict, time_sig, '4,8,12', second_rep, to_browser=True)

    with open(site_globals.src_root + 'static/downloadables/' + unique_id + '.txt', 'a') as res_file:
        res_file.write('\nmu2')


if __name__ == '__main__':
    main()
