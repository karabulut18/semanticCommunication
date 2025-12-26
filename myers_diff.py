#!/usr/bin/env python3

import argparse


def myers_diff(seq1, seq2):
    """
    Myers' diff algorithm for comparing two sequences (binary or text).
    Returns the edits required to transform seq1 into seq2.
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

    return []  # Should not reach here


def backtrack(trace, seq1, seq2, n, m):
    """
    Backtracks through the trace to construct the edit script.
    """
    edits = []
    x, y = n, m

    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        prev_k = k + 1 if k == -d or (k != d and v[k - 1] < v[k + 1]) else k - 1
        prev_x = v[prev_k]
        prev_y = prev_x - prev_k

        while x > prev_x and y > prev_y:
            edits.append(("MATCH", x - 1, y - 1))  # Matching bytes
            x -= 1
            y -= 1

        if x > prev_x:
            edits.append(("DELETE", x - 1))  # Byte deleted from seq1
            x -= 1
        elif y > prev_y:
            edits.append(("INSERT", y - 1))  # Byte inserted into seq2
            y -= 1

    return edits[::-1]  # Reverse to get the correct order


def binary_diff(file1_path, file2_path):
    """
    Compares two binary files using Myers' Diff Algorithm.
    Returns a list of differences (edits).
    """
    try:
        with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
            content1 = f1.read()
            content2 = f2.read()

        # Perform Myers' Diff
        edits = myers_diff(content1, content2)
        return edits

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Myers' Diff Algorithm")
    parser.add_argument("file1", help="Path to the first file")
    parser.add_argument("file2", help="Path to the second file")
    args = parser.parse_args()

    differences = binary_diff(args.file1, args.file2)
    if differences is not None:
        for diff in differences:
            if diff[0] == "MATCH":
                print(f"Match at File1[{diff[1]}], File2[{diff[2]}]")
            elif diff[0] == "DELETE":
                print(f"Delete at File1[{diff[1]}]")
            elif diff[0] == "INSERT":
                print(f"Insert at File2[{diff[1]}]")


if __name__ == "__main__":
    main()
