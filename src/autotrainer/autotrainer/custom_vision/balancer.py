from collections import Counter
import random
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry

class Balancer:
    data: [ImageUrlCreateEntry]
    min_labelled: int
    max_images: int
    def __init__(self, image_url_create_entry_list: [ImageUrlCreateEntry], min_labelled = 5, max_images = 30000):
        self.data = image_url_create_entry_list
        self.min_labelled = min_labelled
        self.max_images = max_images
        
    def apply(self):
        """apply high level dataset balancer

        :param image_url_create_entry_list: The list of images and tags
        :type: [azure.cognitiveservices.vision.customvision.training.models.ImageUrlCreateEntry]
        """
        start_count = len(self.data)
        print('Applying dataset balancer to list of {}'.format(start_count))
        filtered = remove_small_sets(self.data, self.min_labelled, self.max_images)
        filtered_count = len(filtered)
        print('Removed {} item(s) by filtering small sets'.format(start_count - filtered_count))
        balanced_filtered = balance_by_minimum_random(filtered)
        final_count = len(balanced_filtered)
        print('Removed {} item(s) by balancing tags'.format(filtered_count - final_count))
        print('Returning list of {} items'.format(final_count))
        return downsample_to_max_images(balanced_filtered, self.max_images)

def remove_small_sets(image_url_create_entry_list, min_labelled: int, max_images: int):
    unique_tags=list(Counter(c.tag_ids[0] for c in image_url_create_entry_list).keys()) # get the unique tags
    frequencies=list(Counter(c.tag_ids[0] for c in image_url_create_entry_list).values()) # counts the elements' frequency
    print('Removing all tags with freq less than {}'.format(min_labelled))
    small_freqs = [f for f in frequencies if f < min_labelled]
    for f in small_freqs:
        index = frequencies.index(f)
        removed = unique_tags.pop(index)
        removed_f = frequencies.pop(index)
        print('Removed tag:{} with freq:{}'.format(removed, removed_f))
    return [e for e in image_url_create_entry_list if e.tag_ids[0] in unique_tags]

def balance_by_minimum_random(image_url_create_entry_list):
    # returns a list where all the frequencies are equal to the minimum frequency
    frequencies=list(Counter(c.tag_ids[0] for c in image_url_create_entry_list).values()) # counts the elements' frequency
    unique_tags=list(Counter(c.tag_ids[0] for c in image_url_create_entry_list).keys()) # get the unique tags
    min_freq = min(frequencies)
    print('Minimum Tag Frequency: {}'.format(min_freq))
    final_list = []
    for ut in unique_tags:
        just_this_tag = [t for t in image_url_create_entry_list if t.tag_ids[0] == ut]
        final_list.extend(random.sample(just_this_tag, min_freq))
    return final_list

def downsample_to_max_images(image_url_create_entry_list, max_images: int):
    num_images = len(image_url_create_entry_list)
    if(num_images > max_images - 1):
        print('Downsampling images to {}'.format(max_images))
        x = random.sample(image_url_create_entry_list, max_images)
        x.sort(key=lambda x: x.tag_ids[0])
        return x
    else:
        return image_url_create_entry_list

