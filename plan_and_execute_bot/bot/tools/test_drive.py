#!/usr/bin/env python3
import base64
import re
from drive import search_files, get_file_metadata, move_file, upload_file, delete_file

def extract_id(text):
    m = re.search(r"ID: ([A-Za-z0-9_-]+)", text)
    if not m:
        raise Exception("ID no encontrado en texto:\n" + text)
    return m.group(1)

def main():
    # 1. Buscar 'prueba1'
    print("1) Buscando 'prueba1'...")
    search_res = search_files.invoke({"query": "prueba1", "page_size": 1})
    print(search_res, "\n")
    id_prueba1 = extract_id(search_res)

    # 2. Obtener metadata
    print("2) Metadatos de 'prueba1':")
    meta_res = get_file_metadata.invoke({"file_id": id_prueba1})
    print(meta_res, "\n")

    # 3. Buscar carpeta 'MiCarpetaNLP'
    print("3) Buscando carpeta 'MiCarpetaNLP'...")
    folder_res = search_files.invoke({"query": "MiCarpetaNLP", "page_size": 1})
    print(folder_res, "\n")
    id_folder = extract_id(folder_res)

    # 4. Mover 'prueba1' a 'MiCarpetaNLP'
    print(f"4) Moviendo 'prueba1' (ID={id_prueba1}) a carpeta (ID={id_folder})...")
    move_res = move_file.invoke({
        "file_id": id_prueba1,
        "new_parent_id": id_folder
    })
    print(move_res, "\n")

    # 6. Eliminar 'prueba2'
    print("6) Buscando 'prueba2'...")
    search_res = search_files.invoke({"query": "prueba2", "page_size": 1})
    print(search_res, "\n")
    id_prueba2 = extract_id(search_res)
    print(f"6) Eliminando 'prueba2' (ID={id_prueba2})...")
    delete_res = delete_file.invoke({
        "file_id": id_prueba2,
        "permanent": False
    })
    print(delete_res)

if __name__ == "__main__":
    main()
