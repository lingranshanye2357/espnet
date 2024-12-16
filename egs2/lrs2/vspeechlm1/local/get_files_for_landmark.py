import os
import tqdm

def get_file_label_lrs2(args):
    video_ids_total, labels_total = [], []
    with open(args.video_source_dir, 'r') as f1:
        with open(args.text_source_dir, 'r') as f2:
             for line1, line2 in zip(f1, f2):
                 video_id, video_path = line1.strip().split(' ')
                 video_id_, text = line2.strip().split(' ')
                 assert video_id_ != video_id
                 video_ids_total.append(video_id)
                 labels_total.append(text)
    print(f"data num: {len(labels_total)}")
    with open(args.filename_path, 'w') as file:
        file.write('\n'.join(video_ids_total) + '\n')
    with open(args.label_path, 'w') as file:
        file.write('\n'.join(labels_total) + '\n')
    
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='LRS3 preprocess pretrain dir', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--video_source_dir', type=str, default="/nfs-02/yuyue/visualtts/dataset/lrs2/video_25fps", help='root dir for videos')
    parser.add_argument('--text_source_dir', type=str, default='/nfs-02/yuyue/visualtts/dataset/lrs2/wav_16k')
    parser.add_argument('--filename_path', type=str, default='/nfs-02/yuyue/visualtts/reference_code/espnet/egs2/lrs2/avhubert/local/temp/file.list', help='filenames')
    parser.add_argument('--label_path', type=str, default='/nfs-02/yuyue/visualtts/reference_code/espnet/egs2/lrs2/avhubert/local/temp/label.list', help='corresponding text transcriptions')
    args = parser.parse_args()
    get_file_label_lrs2(args)