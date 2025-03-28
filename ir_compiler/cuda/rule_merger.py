def process_files(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2:
        lines1 = [line.strip() for line in file1.readlines()]
        lines2 = [line.strip() for line in file2.readlines()]

    max_length = max(len(lines1), len(lines2))

    lines1.extend([''] * (max_length - len(lines1)))
    lines2.extend([''] * (max_length - len(lines2)))

    combined_lines = [f"{line1}={line2}" for line1, line2 in zip(lines1, lines2)]
    
    return "\n".join(combined_lines)

file1_path = "cuda.rbe"
file2_path = "../c.rbe"
result = process_files(file1_path, file2_path)
print(result)