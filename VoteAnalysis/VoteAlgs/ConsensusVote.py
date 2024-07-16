from data_generator import NResult
import random

ERROR_STRING = "Input list is empty"

def group_answers(results: list[NResult]) -> list[list[NResult]]:
    """Группирует ответы по версиям."""
    classes_list = []
    for res in results:
        # Если другие мультиверсии уже выставили свои ответы на голосование, то сравниваем текущий ответ с ними
        if classes_list:
            # Если обрабатываемый ответ относится к уже имеющемуся классу, то добавляем его в этот класс.
            for answers_class in classes_list:
                if res.version_answer == answers_class[0].version_answer:
                    answers_class.append(res)
                    break
            else:
                # Иначе создаём новый класс для ответа, т.к. он встретился впервые
                classes_list.append([res])
        else:
            classes_list.append([res])
    return classes_list

def select_majority_class(classes_list: list[list[NResult]]) -> list[NResult]:
    """Выбирает класс с наибольшим количеством ответов."""
    max_index = 0
    max_values_in_class = len(classes_list[0])
    max_index_lst = [0]

    for i, answers_class in enumerate(classes_list):
        class_size = len(answers_class)
        if class_size > max_values_in_class:
            max_values_in_class = class_size
            max_index = i
            max_index_lst = [i]
        elif class_size == max_values_in_class:
            max_index_lst.append(i)

    if len(max_index_lst) > 1:
        max_index = random.choice(max_index_lst)
    return classes_list[max_index]

def classic_vote(results: list[NResult], return_classes_list: bool = False):
    if not results:
        raise ValueError(ERROR_STRING)
    
    classes_list = group_answers(results)

    if return_classes_list:
        return classes_list
    
    majority_class = select_majority_class(classes_list)
    return majority_class[0].version_answer

def calculate_max_diversity(results_list: list[NResult]) -> float:
    """Вычисляет максимальное расстояние между версиями."""
    max_diversity = 0
    results_len = len(results_list)

    if results_len == 1:
        return 0

    for j in range(results_len):
        for k in range(j + 1, results_len):
            cur_diversity = results_list[j].version.calculate_distance_to(results_list[k].version)
            if cur_diversity > max_diversity:
                max_diversity = cur_diversity

    return max_diversity

def select_diverse_class(classes_list: list[list[NResult]]) -> list[NResult]:
    """Выбирает класс с максимальной диверсифицированностью."""
    max_index = 0
    max_values_in_class = len(classes_list[0])
    max_diversity = calculate_max_diversity(classes_list[0])
    max_indexes_lst = [0]

    for i, answers_class in enumerate(classes_list):
        class_size = len(answers_class)
        if class_size > max_values_in_class:
            max_values_in_class = class_size
            max_index = i
            max_diversity = calculate_max_diversity(answers_class)
            max_indexes_lst = [i]
        elif class_size == max_values_in_class:
            current_diversity = calculate_max_diversity(answers_class)
            if current_diversity > max_diversity:
                max_index = i
                max_diversity = current_diversity
                max_indexes_lst = [i]
            elif current_diversity == max_diversity:
                max_indexes_lst.append(i)

    if len(max_indexes_lst) > 1:
        max_index = random.choice(max_indexes_lst)
    return classes_list[max_index]

def modified_vote(results: list[NResult]) -> float:
    if not results:
        raise ValueError(ERROR_STRING)

    try:
        classes_list = classic_vote(results, True)
    except ValueError as err:
        print(str(err))
        raise

    diverse_class = select_diverse_class(classes_list)
    return diverse_class[0].version_answer
