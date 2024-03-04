import multiprocessing
import json
import os
from captcha_synthesis import CaptchaSynthesis

def synthesize_data(worker_id, num_items, input_path, shared_dict):
    cs = CaptchaSynthesis()
    for _ in range(num_items):
        # Replace with your actual data synthesis function
        input_img, label = cs.synthesize_captcha()
        
        # Save input data to a file and label to the shared dictionary
        input_file = f"input_{worker_id}_{_}.png"  # Or use an appropriate file format
        input_file_path = os.path.join(input_path, input_file)
        input_img.save(input_file_path)
        
        # Store the label with the input file ID in the shared dictionary
        shared_dict[input_file] = ''.join(label)

def main(num_processes, num_items_per_process, input_path, labels_path):
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()

    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(
            target=synthesize_data,
            args=(i, num_items_per_process, input_path, shared_dict)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Save the shared dictionary containing labels to path_2
    labels_file_path = os.path.join(labels_path, 'labels.json')
    with open(labels_file_path, 'w') as f:
        json.dump(dict(shared_dict), f)

if __name__ == '__main__':
    num_processes = 4  # Number of processes to run in parallel
    num_items_per_process = 5  # Number of data items each process will generate
    input_path = 'train_set/imgs/'  # Path where input files will be saved
    labels_path = 'train_set/'  # Path where label dictionary will be saved
    
    # Ensure the input and label paths exist
    os.makedirs(input_path, exist_ok=True)
    os.makedirs(labels_path, exist_ok=True)

    main(num_processes, num_items_per_process, input_path, labels_path)
