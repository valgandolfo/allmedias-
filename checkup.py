import os
import sys
import datetime

def main():
    root_dir = "."
    # Diretórios para ignorar para não poluir o relatório (ex: ambientes virtuais, cache)
    ignore_dirs = {'.git', '.venv', 'venv', 'env', '__pycache__', 'node_modules', '.agents', '.gemini'}
    
    total_files = 0
    total_py = 0
    total_html = 0
    total_size_bytes = 0
    folders_scanned = set()
    
    # Interatividade para ordenação
    print("Opções de ordenação:")
    print("1 - Ordenar por Nome (caminho do arquivo)")
    print("2 - Ordenar por Tamanho (do maior para o menor)")
    print("3 - Ordenar por Data (mais recentes primeiro)")
    
    # Suporte para argumento de linha de comando ou input interativo
    opcao = "1"
    if len(sys.argv) > 1:
        opcao = sys.argv[1]
    else:
        try:
            opcao = input("Escolha uma opção (1/2/3) [padrão: 1]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssumindo opção 1 (Nome).")
            opcao = "1"
            
    if opcao not in ["1", "2", "3"]:
        opcao = "1"

    now = datetime.datetime.now()
    # Usamos '-' em vez de '/' e ':' para formar um nome de arquivo válido no sistema
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H-%M-%S")
    
    output_filename = f"allmedia_data({date_str})_horas({time_str}).txt"
    
    file_list = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignora diretórios indesejados
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        folders_scanned.add(dirpath)
        
        for filename in filenames:
            is_py = filename.endswith(".py")
            is_html = filename.endswith(".html")
            
            if is_py or is_html:
                filepath = os.path.join(dirpath, filename)
                try:
                    stat_info = os.stat(filepath)
                    size = stat_info.st_size
                    mtime = stat_info.st_mtime
                    
                    dt_mtime = datetime.datetime.fromtimestamp(mtime)
                    dt_str = dt_mtime.strftime("%d/%m/%Y %H:%M:%S")
                    
                    # Guardamos também o mtime (timestamp) para poder ordenar corretamente pela data
                    file_list.append((filepath, size, dt_str, mtime))
                    
                    total_files += 1
                    total_size_bytes += size
                    
                    if is_py:
                        total_py += 1
                    elif is_html:
                        total_html += 1
                except Exception:
                    pass

    # Aplicando a ordenação escolhida
    if opcao == "2":
        # Ordenar por tamanho (índice 1 da tupla), do maior para o menor (reverse=True)
        file_list.sort(key=lambda x: x[1], reverse=True)
    elif opcao == "3":
        # Ordenar por data (índice 3 da tupla), do mais recente para o mais antigo (reverse=True)
        file_list.sort(key=lambda x: x[3], reverse=True)
    else:
        # Ordenar por nome (índice 0 da tupla), ordem alfabética (padrão)
        file_list.sort(key=lambda x: x[0])

    total_kbytes = total_size_bytes / 1024
    total_folders = len(folders_scanned)
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f"{output_filename}\n")
        f.write("-" * 105 + "\n")
        f.write(f"| {'nome do arquivo'.ljust(60)} | {'tamanho (KB)'.ljust(12)} | {'dt. ultima atualizacao'.ljust(22)} |\n")
        f.write("-" * 105 + "\n")
        
        for filepath, size, dt_str, mtime in file_list:
            size_kb = f"{size / 1024:.2f}"
            display_name = filepath if len(filepath) <= 60 else "..." + filepath[-57:]
            f.write(f"| {display_name.ljust(60)} | {size_kb.ljust(12)} | {dt_str.ljust(22)} |\n")
            
        f.write("-" * 105 + "\n\n")
        f.write("totalizadores:\n")
        f.write(f"numeros de pastas: {total_folders}\n")
        f.write(f"numeros de arquivos: {total_files}\n")
        f.write(f"  - arquivos .py: {total_py}\n")
        f.write(f"  - arquivos .html: {total_html}\n")
        f.write(f"total geral em kbyte: {total_kbytes:.2f} KB\n")
        
    print(f"\nRelatório gerado com sucesso: {output_filename}")

if __name__ == "__main__":
    main()
