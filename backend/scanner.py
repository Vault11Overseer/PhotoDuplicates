from PIL import Image
import imagehash
import os

def get_image_hash(path):
    """Return perceptual hash of an image."""
    with Image.open(path) as img:
        return imagehash.phash(img)

def find_duplicates(directory, hash_threshold=5):
    """
    Scan the directory recursively and find duplicates.
    Returns a list of tuples: (original_path, duplicate_path)
    """
    hashes = {}
    duplicates = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                path = os.path.join(root, file)
                try:
                    h = get_image_hash(path)
                    for existing_hash in hashes:
                        if h - existing_hash <= hash_threshold:
                            duplicates.append((hashes[existing_hash], path))
                            break
                    else:
                        hashes[h] = path
                except Exception:
                    continue
    return duplicates
