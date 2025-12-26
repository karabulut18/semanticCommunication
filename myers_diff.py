#!/usr/bin/env python3

# Myers' Diff Algorithm for Comparing Binary Files
# The Myers' diff algorithm is a linear space algorithm for comparing two sequences.
# It is commonly used in version control systems to track changes in text files.

import argparse
from logger import initialize_logger, LOG, LOGE

def myers_diff(seq1, seq2):
    """
    Myers' diff algorithm for comparing two sequences (binary or text).
    Returns the edits and the number of matched bytes.
    """
    n = len(seq1)
    m = len(seq2)
    max_d = n + m
    v = {1: 0}  # V array for tracking the furthest reach on the edit graph

    # Backtracking path
    trace = []

    for d in range(max_d + 1):
        trace.append(v.copy())  # Save the current state for backtracking
        for k in range(-d, d + 1, 2):
            # Determine whether to move down or right
            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                x = v[k + 1]  # Move down
            else:
                x = v[k - 1] + 1  # Move right

            y = x - k  # Diagonal movement
            while x < n and y < m and seq1[x] == seq2[y]:
                x += 1
                y += 1  # Follow the diagonal

            v[k] = x

            # Check if we've reached the end
            if x >= n and y >= m:
                return backtrack(trace, seq1, seq2, n, m)

    return [], 0  # Should not reach here

def backtrack(trace, seq1, seq2, n, m):
    """
    Backtracks through the trace to construct the edit script and count matches.
    """
    edits = []
    matches = 0
    x, y = n, m

    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        prev_k = k + 1 if k == -d or (k != d and v[k - 1] < v[k + 1]) else k - 1
        prev_x = v[prev_k]
        # prev_y = prev_x - prev_k

        while x > prev_x and y > (prev_x - prev_k):
            edits.append(("MATCH", x - 1, y - 1))  # Matching bytes
            matches += 1  # Count the matches
            x -= 1
            y -= 1

        if x > prev_x:
            edits.append(("DELETE", x - 1))  # Byte deleted from seq1
            x -= 1
        elif y > (prev_x - prev_k):
            edits.append(("INSERT", y - 1))  # Byte inserted into seq2
            y -= 1

    return edits[::-1], matches

def binary_similarity(file1_path, file2_path):
    """
    Compares two binary files using Myers' Diff Algorithm.
    Returns the similarity percentage.
    """
    try:
        with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
            content1 = f1.read()
            content2 = f2.read()

        # Perform Myers' Diff
        edits, matches = myers_diff(content1, content2)

        # Calculate similarity percentage
        similarity = (matches / len(content1)) * 100 if content1 else 0

        return similarity, edits

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def main():
    """
    Main function to parse command-line arguments and run the Myers' Diff Algorithm.
    """
    initialize_logger("myers_diff")
    LOG("Starting Myers' Diff Algorithm")
    parser = argparse.ArgumentParser(description="Myers' Diff Algorithm for Comparing Binary Files")
    parser.add_argument("file1", help="Path to the first binary file")
    parser.add_argument("file2", help="Path to the second binary file")
    args = parser.parse_args()

    similarity, differences = binary_similarity(args.file1, args.file2)
    if similarity is not None:
        LOG(f"Similarity: {similarity:.2f}%")
        LOG("Differences:")
        for diff in differences:
            if diff[0] == "MATCH":
                # print(f"Match: File1[{diff[1]}] == File2[{diff[2]}]")
                pass
            elif diff[0] == "DELETE":
                LOGE(f"Delete: Byte {diff[1]} in File1 is missing in File2")
            elif diff[0] == "INSERT":
                LOGE(f"Insert: Byte {diff[1]} in File2 is new compared to File1")
    LOG("Completed Myers' Diff Algorithm")

if __name__ == '__main__':
    main()
