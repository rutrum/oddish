default: extract

extract:
    python3 src/extract_sprites.py

tree:
    tree -I target

pallete NUM:
    python3 src/pallete.py {{NUM}}
