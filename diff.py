from pathlib import Path
import sys
import argparse
import subprocess as sub
from tqdm import tqdm

"""
Make sure you have no uncommitted changes in the working tree.
Run this like 
$ conda activate thesis
$ doit # to make sure everyhing is built properly

#this will replace all the tex with diffed versions, use git to clean it up later
$ python diff.py --oldhash 0a2cc110f36b48a3eb39c61e1023f3d745ebd93c --newhash HEAD

# diffing the main thesis.tex file doesn't seem to work well, so instead manually copy the latexdiff premable just before the body begins

$ doit -s pdf #build the pdf without rebuilding the tex

"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog = 'Thesis Differ',
                        description = 'Diff two git hashes using latexdiff',
                        )

    parser.add_argument('--oldhash', default = "HEAD^", help = "old git hash")   
    parser.add_argument('--newhash', default = "HEAD", help = "new git hash")
   
    args = parser.parse_args()

    diff_folder = Path("./build/diffs")
    latex_folder = Path("./build/latex")

    def with_suffix(path, suffix):
        return path.parent / (path.stem + suffix + path.suffix)

    def save_file_version(hash, input_file, output_file):
        result = sub.run(["git", "show", f"{hash}:{input_file}"], capture_output = True, check = True)
        
        with open(output_file, "wb") as f:
            f.write(result.stdout)

    def make_diff(old, new, output):
        try:
            result = sub.run(["latexdiff", old, new], capture_output = True)
        except sub.CalledProcessError as e:
            print(e.stderr)
            raise e

        with open(output, "wb") as f:
            f.write(result.stdout)

    for file in tqdm(latex_folder.glob("**/*.tex")):
        oldfile = with_suffix(diff_folder / file.relative_to(latex_folder), "_old")
        newfile = with_suffix(diff_folder / file.relative_to(latex_folder), "_new")
        
        oldfile.parent.mkdir(exist_ok=True, parents=True)

        try:
            save_file_version(args.oldhash, file, oldfile)
            save_file_version(args.newhash, file, newfile)
        except:
            print(f"Skipping {file}, seems like it doesn't exist in one of the revs")
            continue

        print(f"Doing {file}")
        make_diff(old = oldfile, new = newfile, output = file)
    
    # file = Path("thesis.tex")
    # oldfile = with_suffix(file, "_old")
    # newfile = with_suffix(file, "_new")
    # save_file_version(args.oldhash, file, oldfile)
    # save_file_version(args.newhash, file, newfile)
    # print(f"Doing {file}")
    # make_diff(old = oldfile, new = newfile, output = file)

        

