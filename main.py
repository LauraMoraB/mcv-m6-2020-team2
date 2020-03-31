import argparse
import os
# import week1, week2, week3, week4
import week5

parser = argparse.ArgumentParser(description='M6 - Video Analysis: Video Surveillance for Road Traffic Monitoring')

parser.add_argument('-w', '--week', type=int, help='week to execute. Options are [1,2,3,4,5]')
parser.add_argument('-t', '--task', type=int, help='task to execute. Options are [1,2,3,4]')
args = parser.parse_args()

path_plots = 'results/'
if not os.path.exists(path_plots):
    os.makedirs(path_plots)

if args.week == 1:
    if args.task == 1_1:
        week1.task1_1(path_plots)
    elif args.task == 1_2:
        week1.task1_2()
    elif args.task == 2:
        week1.task2(path_plots)
    elif args.task == 3 or args.task == 4:
        week1.task3_4(path_plots)
    else:
        raise ValueError(f"Bad input task {args.task}. Options are [1,2,3,4]")

elif args.week == 2:
    if args.task == 1:
        week2.task1(path_plots)
    elif args.task == 2:
        week2.task2(path_plots)
    elif args.task == 3:
        week2.task3(path_plots)
    elif args.task == 4:
        week2.task4(adaptive=True, random_search=False, color_space='yuv', channels=(1, 2), save_path=None, debug=0)

    else:
        raise ValueError(f"Bad input task {args.task}. Options are [1,2,3,4]")

elif args.week == 3:
    if args.task == 1_1:
        week3.task1_1(architecture='maskrcnn', start=0, length=None, gpu=3, visualize=False)
    elif args.task == 1_2:
        week3.task1_2()
    elif args.task == 2_1:
        week3.task2_1(save_path=None, debug=0)
    elif args.task == 2_2:
        week3.task2_2(debug=0)
    else:
        raise ValueError(f"Bad input task {args.task}. Options are [1_1, 1_2, 2_1, 2_2]")

elif args.week == 4:
    if args.task == 1_1:
        week4.task1_1()
    elif args.task == 1_2:
        week4.task1_2()
    elif args.task == 2_1:
        week4.task2_1()
    elif args.task == 2_2:
        week4.task2_2()
    elif args.task == 3_1:
        week4.task3_1()
    else:
        raise ValueError(f"Bad input task {args.task}. Options are [1_1, 1_2, 2_1, 2_2, 3_1]")

elif args.week == 5:
    if args.task == 1:
        week5.task1()
    elif args.task == 2:
        week5.task2()
    else:
        raise ValueError(f"Bad input task {args.task}. Options are [1, 2]")

else:
    raise ValueError(f"Bad input week {args.week}. Options are [1,2,3,4,5]")
