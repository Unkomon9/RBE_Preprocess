def process_files(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2:
        lines1 = file1.read().splitlines()
        lines2 = file2.read().splitlines()

    max_length = max(len(lines1), len(lines2))

    lines1 += [''] * (max_length - len(lines1))
    lines2 += [''] * (max_length - len(lines2))

    return "=".join(f"{line1}={line2}" for line1, line2 in zip(lines1, lines2))

file1_path = "cuda.rbe"
file2_path = "../c.rbe"
result = process_files(file1_path, file2_path)

output = "output.rbe"
with open(output, 'w', encoding='utf-8') as output_file:
    output_file.write(result)

print(f"Result saved to {output}")