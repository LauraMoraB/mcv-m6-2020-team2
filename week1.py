import os

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from src.utils.aicity_reader import AICityChallengeAnnotationReader
from src.evaluation.average_precision import mean_average_precision
from src.evaluation.intersection_over_union import mean_intersection_over_union

from src.evaluation.optical_flow_evaluation import get_msen_pepn
from src.utils.io_optical_flow import read_flow_field, read_grayscale_image
from src.utils.optical_flow_visualization import plot_optical_flow


def task1_1(path_results=None):
    reader = AICityChallengeAnnotationReader(path='data/ai_challenge_s03_c010-full_annotation.xml')
    gt = reader.get_annotations(classes=['car'])

    # add probability to delete bounding boxes
    drop_values = np.linspace(0, 1, 11)
    maps = []
    for drop in drop_values:
        noise_params = {'drop': drop, 'mean': 0, 'std': 0}
        gt_noisy = reader.get_annotations(classes=['car'], noise_params=noise_params)

        frames = sorted(list(set(gt) & set(gt_noisy)))
        y_true = []
        y_pred = []
        for frame in frames:
            y_true.append(gt[frame])
            y_pred.append(gt_noisy[frame])

        map = mean_average_precision(y_true, y_pred)
        maps.append(map)

    plt.plot(drop_values, maps)
    plt.xticks(drop_values)
    plt.xlabel('drop prob')
    plt.ylabel('mAP')
    plt.savefig(os.path.join(path_results, 'map_drop_bbox.png')) if path_results else plt.show()
    plt.close()


    # add noise to the size and position of bounding boxes
    std_values = np.linspace(0, 100, 11)
    maps = []
    for std in std_values:
        noise_params = {'drop': 0, 'mean': 0, 'std': std}
        gt_noisy = reader.get_annotations(classes=['car'], noise_params=noise_params)

        frames = sorted(list(set(gt) & set(gt_noisy)))
        y_true = []
        y_pred = []
        for frame in frames:
            y_true.append(gt[frame])
            y_pred.append(gt_noisy[frame])

        map = mean_average_precision(y_true, y_pred)
        maps.append(map)

    plt.xlabel('std')
    plt.ylabel('mAP')
    plt.xticks(std_values)
    plt.plot(std_values, maps)
    plt.savefig(os.path.join(path_results, 'map_noisy_bbox.png')) if path_results else plt.show()


def task1_2():
    reader = AICityChallengeAnnotationReader(path='data/ai_challenge_s03_c010-full_annotation.xml')
    gt = reader.get_annotations(classes=['car'])

    for detector in ['mask_rcnn', 'ssd512', 'yolo3']:
        reader = AICityChallengeAnnotationReader(path=f'data/AICity_data/train/S03/c010/det/det_{detector}.txt')
        det = reader.get_annotations(classes=['car'])

        frames = sorted(list(set(gt) & set(det)))
        y_true = []
        y_pred = []
        for frame in frames:
            y_true.append(gt[frame])
            y_pred.append(det[frame])

        map = mean_average_precision(y_true, y_pred)
        print(f'{detector} mAP: {map:.4f}')


def task2(path_results=None):
    reader = AICityChallengeAnnotationReader(path='data/ai_challenge_s03_c010-full_annotation.xml')
    gt = reader.get_annotations(classes=['car'], group_by_frame=True)

    # Noisy case
    noise_params = {'drop': 0.05, 'mean': 0, 'std': 10}
    gt_noisy = reader.get_annotations(classes=['car'], noise_params=noise_params, group_by_frame=True)

    frames = sorted(list(set(gt) & set(gt_noisy)))
    overlaps = []
    for frame in frames:
        boxes1 = [box[1:] for box in gt[frame]]
        boxes2 = [box[1:] for box in gt_noisy[frame]]
        iou = mean_intersection_over_union(boxes1, boxes2)
        overlaps.append(iou)

    cap = cv2.VideoCapture('data/AICity_data/train/S03/c010/vdo.avi')
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    fig, ax = plt.subplots(2)
    image = ax[0].imshow(np.zeros((height, width)))
    line, = ax[1].plot(frames, overlaps)
    artists = [image, line]

    def update(i):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frames[i])
        ret, img = cap.read()
        for box in gt[frames[i]]:
            cv2.rectangle(img, (int(box[1]), int(box[2])), (int(box[3]), int(box[4])), (0, 255, 0), 2)
        for box in gt_noisy[frames[i]]:
            cv2.rectangle(img, (int(box[1]), int(box[2])), (int(box[3]), int(box[4])), (0, 0, 255), 2)
        artists[0].set_data(img[:, :, ::-1])
        artists[1].set_data(frames[:i+1], overlaps[:i+1])
        return artists

    ani = animation.FuncAnimation(fig, update, len(frames), interval=2, blit=True)

    ax[0].set_xticks([])
    ax[0].set_yticks([])
    ax[1].set_ylim(0, 1)
    ax[1].set_xlabel('#frame')
    ax[1].set_ylabel('mean IoU')
    fig.suptitle('noisy annotation')
    plt.savefig(os.path.join(path_results, 'miou_noisy_annot.png')) if path_results else plt.show()

    # Detector cases
    detectors = ['det_mask_rcnn.txt', 'det_ssd512.txt', 'det_yolo3.txt']
    detections_path = 'data/AICity_data/train/S03/c010/det/'

    for detector in detectors:
        print("Detector: ", detector)
        dets_reader = AICityChallengeAnnotationReader(path=detections_path + detector)
        detections_list = dets_reader.get_annotations(classes=['car'], group_by_frame=True)

        frames = sorted(list(set(gt) & set(detections_list)))
        overlaps = []
        for frame in frames:
            boxes1 = [box[1:] for box in gt[frame]]
            boxes2 = [box[1:] for box in detections_list[frame]]
            iou = mean_intersection_over_union(boxes1, boxes2)
            overlaps.append(iou)

        cap = cv2.VideoCapture('data/AICity_data/train/S03/c010/vdo.avi')
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        fig, ax = plt.subplots(2)
        image = ax[0].imshow(np.zeros((height, width)))
        line, = ax[1].plot(frames, overlaps)
        artists = [image, line]

        def update(i):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frames[i])
            ret, img = cap.read()
            for box in gt[frames[i]]:
                cv2.rectangle(img, (int(box[1]), int(box[2])), (int(box[3]), int(box[4])), (0, 255, 0), 2)
            for box in detections_list[frames[i]]:
                cv2.rectangle(img, (int(box[1]), int(box[2])), (int(box[3]), int(box[4])), (0, 0, 255), 2)
            artists[0].set_data(img[:, :, ::-1])
            artists[1].set_data(frames[:i+1], overlaps[:i+1])
            return artists

        ani = animation.FuncAnimation(fig, update, len(frames), interval=2, blit=True)

        ax[0].set_xticks([])
        ax[0].set_yticks([])
        ax[1].set_ylim(0, 1)
        ax[1].set_xlabel('#frame')
        ax[1].set_ylabel('mean IoU')
        fig.suptitle('Detector '+detector.replace('.txt',''))
        plt.savefig(os.path.join(path_results, 'miou_noisy_detections.png')) if path_results else plt.show()


def task3_4(path_results=None):
    pred_path = 'data/optical_flow_results/'
    kitti_data = 'data/data_stereo_flow/training/'
    images = ['045', '157']
    plot = False

    for im_idx in images:

        im_name = f'000{im_idx}_10.png'

        flow_estimation = os.path.join(pred_path, f'LKflow_{im_name}')
        im_path = os.path.join(kitti_data, f'image_0/{im_name}')
        gt_non_occ = os.path.join(kitti_data, f'flow_noc/{im_name}')

        image_gray = read_grayscale_image(im_path, frame_id=im_idx, plot=plot)
        flow_pred = read_flow_field(flow_estimation, frame_id=im_idx, plot=plot)
        flow_gt = read_flow_field(gt_non_occ, frame_id=im_idx, plot=plot)

        print('Computing MSEN and PEPN')
        msen, pepn = get_msen_pepn(flow_pred, flow_gt, frame_id=im_idx, th=3, plot=plot)
        print(f'SEQ-{im_idx}\n  MSEN: {round(msen, 4)}\n  PEPN: {round(pepn, 4)}%')

        plot_optical_flow(image_gray, flow_gt[:,:,0:2], 'GT', im_idx, 10, path=path_results)
        plot_optical_flow(image_gray, flow_pred[:,:,0:2], 'PRED', im_idx, 10, path=path_results)


if __name__ == '__main__':
    #task1_1()
    task1_2()
    #task2()
    #task3_4()
