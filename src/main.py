from os import path, getcwd, remove, mkdir, listdir
from shutil import copy, rmtree
from helpers import generate_page

ASSETS_DIR = "static"
PUBLIC_DIR = "public"

def emptyDir(dir: str):
    if not path.exists(dir):
        return
    for name in listdir(dir):
        name = path.join(dir, name)
        if path.isfile(name):
            remove(name)
            continue
        rmtree(name)
def copyItems(src: str, target: str):
    if not path.exists(src):
        raise Exception(f"source folder does not exists {src}")
    if not path.exists(target):
        raise Exception(f"target folder does not exists {target}")
    for name in listdir(src):
        srcName = path.join(src, name)
        targetName = path.join(target, name)
        if path.isfile(srcName):
            copy(srcName, targetName)
            continue
        mkdir(targetName)
        copyItems(srcName, targetName)


def main():
    assets_path = path.join(getcwd(), ASSETS_DIR)
    public_path = path.join(getcwd(), PUBLIC_DIR)
    if not path.exists(public_path) or path.isfile(public_path):
        mkdir(public_path)
    
    emptyDir(public_path)
    copyItems(assets_path, public_path)

    generate_page("content/index.md", "template.html", "public/index.html")
    

if __name__ == "__main__":
    main()