import os
import numpy as np
from PIL import Image, ImageChops
import matplotlib.pyplot as plt


def compare_images(pre_image, post_image):
    """
    Compares two images and returns True if differences are found.

    Args:
        pre_image: Path to the first image.
        post_image: Path to the second image.

    Returns:
        True if differences are found, False otherwise.
    """
    try:
        img1 = Image.open(pre_image)
        img2 = Image.open(post_image)

        # Ensure images have the same dimensions
        if img1.size != img2.size:
            print(f"Warning: Image sizes differ for {pre_image}. Skipping.")
            return False

        diff = ImageChops.difference(img1, img2)

        # Check for differences using numpy for better accuracy
        diff_arr = np.array(diff)
        return np.any(diff_arr != 0)

    except Exception as e:  # pylint: disable=broad-except
        print(f"Error comparing images: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare images and generate a single plot with diffs."
    )
    parser.add_argument(
        "pre_dir", help="Path to the directory containing the first set of images."
    )
    parser.add_argument(
        "post_dir", help="Path to the directory containing the second set of images."
    )
    args = parser.parse_args()

    diff_images = []
    filenames = []
    for filename in os.listdir(args.pre_dir):
        if filename.endswith(
            (".png", ".jpg", ".jpeg")
        ):  # Adjust for your image file types
            pre_file = os.path.join(args.pre_dir, filename)
            post_file = os.path.join(args.post_dir, filename)

            if os.path.isfile(post_file):
                if compare_images(pre_file, post_file):
                    diff_images.append((Image.open(pre_file), Image.open(post_file)))
                    filenames.append(filename)

    # Create a single plot with one row for each file with diffs
    if diff_images:

        output_dir = "diff_images"
        os.makedirs(output_dir, exist_ok=True)

        num_rows = len(diff_images)
        fig, axes = plt.subplots(
            nrows=num_rows,
            ncols=2,
            figsize=(7, 2 * num_rows),
            gridspec_kw={"wspace": 0.05, "hspace": 0.2},
            dpi=600,
        )

        for i, ((pre_img, post_img), filename) in enumerate(
            zip(diff_images, filenames)
        ):
            axes[i, 0].imshow(pre_img)
            axes[i, 0].set_title(f"{filename} (Before)")
            axes[i, 0].axis("off")

            axes[i, 1].imshow(post_img)
            axes[i, 1].set_title(f"{filename} (After)")
            axes[i, 1].axis("off")

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "all_diffs_plot.png"), dpi=600)
        print(f"Found diffs in {len(diff_images)} screens")
    else:
        print(("Found no diffs in screens"))

    print("Image comparison complete.")
