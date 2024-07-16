"""
t/(n-1) vote algorithm programming realization
https://eprints.ncl.ac.uk/file_store/production/59232/8480AF9B-598A-462C-8417-1B1F8CAA6190.pdf

Program for simulation several N-versions work of one module to test vote algorithms.
Experiment is carried out in Denis V. Gruzenkin PhD thesis writing.
"""
from data_generator import NResult

def calculate_t(n: int) -> int:
    """Calculate the maximum number of faulty versions allowed (t) based on n."""
    return (n - 1) // 2

def determine_output_indexes(n: int, output_count: int, results: list[NResult]) -> dict:
    """Determine the output indexes and corresponding version answers."""
    output_indexes_step = (n - 1) // (output_count - 1)
    output_indexes = {i: results[i].version_answer for i in range(0, n - 1, output_indexes_step)}
    output_indexes[n - 1] = results[n - 1].version_answer
    return output_indexes

def find_max_group(results: list[NResult], n: int) -> tuple:
    """Find the maximum group of versions with the same answers and their indexes."""
    comparators = {}
    max_count_indexes = {}
    cur_start_index = -1
    max_group_count = 0
    cur_max_group_count = 0

    for i in range(n - 2):
        if results[i].version_answer == results[i + 1].version_answer:
            comparators[(i, i + 1)] = 0
            if cur_max_group_count == 0:
                cur_start_index = i
                cur_max_group_count = 2
            else:
                cur_max_group_count += 1
        else:
            comparators[(i, i + 1)] = 1
            if cur_start_index != -1:
                if cur_max_group_count not in max_count_indexes:
                    max_count_indexes[cur_max_group_count] = [(cur_start_index, i)]
                else:
                    max_count_indexes[cur_max_group_count].append((cur_start_index, i))
            cur_start_index = -1
            cur_max_group_count = 0
        if cur_max_group_count > max_group_count:
            max_group_count = cur_max_group_count

    if cur_start_index != -1:
        if cur_max_group_count not in max_count_indexes:
            max_count_indexes[cur_max_group_count] = [(cur_start_index, n - 2)]
        else:
            max_count_indexes[cur_max_group_count].append((cur_start_index, n - 2))

    return max_group_count, max_count_indexes

def select_correct_result(output_indexes: dict, max_group_count: int, max_count_indexes: dict, results: list[NResult], t: int) -> float:
    """Select the correct result based on the maximum group count and indexes."""
    if max_group_count >= t:
        if len(max_count_indexes[max_group_count]) == 1:
            for key, val in output_indexes.items():
                if max_count_indexes[max_group_count][0][0] <= key <= max_count_indexes[max_group_count][0][1]:
                    return val
            return results[max_count_indexes[max_group_count][0][0]].version_answer
        else:
            return output_indexes[len(results) - 1]
    else:
        return output_indexes[len(results) - 1]

def vote(results: list[NResult]) -> float:
    n = len(results)
    t = calculate_t(n)
    output_count = n - t
    output_indexes = determine_output_indexes(n, output_count, results)
    max_group_count, max_count_indexes = find_max_group(results, n)
    return select_correct_result(output_indexes, max_group_count, max_count_indexes, results, t)
