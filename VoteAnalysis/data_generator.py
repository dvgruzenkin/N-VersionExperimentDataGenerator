"""Experiment data generation module to simulate N-version programming module running.

Program for simulation several N-versions work of one module to test vote algorithms.
Experiment is carried out in Denis V. Gruzenkin PhD thesis writing.
"""

import json
from math import sqrt
from utils import input_num
from random import random, uniform, normalvariate
from typing import List, Set, Tuple

from data_base_connector import DBConnector

__author__ = "Denis V. Gruzenkin"
__copyright__ = "Copyright 2021, Denis V. Gruzenkin"
__credits__ = ["Denis V. Gruzenkin"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Denis V. Gruzenkin"
__email__ = "gruzenkin.denis@good-look.su"
__status__ = "Production"


class NVersion:
    """
    Real NVP version emulation.
    """
    db_name = 'experiment.db'
    formal_json_db_lst_name = 'lst'

    def __init__(self, n_id: int = None, name: str = 'NoName', const_diversities: Tuple[float, ...] = tuple(),
                 dynamic_diversities: List[Tuple] = None, reliability: float = 0.0):
        """
        NVersion class constructor.

        :param n_id: Identifier for the version.
        :param name: Name of the version.
        :param const_diversities: Tuple of constant diversities.
        :param dynamic_diversities: List of tuples representing dynamic diversities.
        :param reliability: Reliability metric for the version.
        """

        self._id = n_id
        self._name = name
        self._const_diversities = const_diversities
        self._dynamic_diversities = dynamic_diversities or []
        self._reliability = reliability

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = str(new_name)

    @property
    def const_diversities(self) -> Tuple[float, ...]:
        return self._const_diversities

    @const_diversities.setter
    def const_diversities(self, new_tpl: Tuple[float, ...]):
        self._const_diversities = new_tpl

    @property
    def dynamic_diversities(self) -> List[Tuple]:
        return self._dynamic_diversities

    @dynamic_diversities.setter
    def dynamic_diversities(self, new_lst: List[Tuple]):
        self._dynamic_diversities = new_lst

    @property
    def common_coordinates_list(self) -> Tuple:
        return tuple(list(self._const_diversities) + self._dynamic_diversities)

    @property
    def reliability(self) -> float:
        return self._reliability

    def generate_reliability(self, min_val: float, max_val: float, round_to=6):
        self._reliability = uniform(min_val, max_val).__round__(round_to)

    @staticmethod
    def _calc_euclidean_distance(lst1: list[float], lst2: list[float]) -> float:
        if len(lst1) == len(lst2):
            square_dif_sum = 0
            for i in range(len(lst1)):
                square_dif_sum += (lst1[i] - lst2[i]) ** 2
            return sqrt(square_dif_sum)
        else:
            raise ValueError('Different coordinates amount')

    @reliability.setter
    def reliability(self, new_val: float):
        if 0 <= float(new_val) <= 1:
            self._reliability = new_val
        else:
            raise ValueError('Reliability interval is [0, 1]')

    @property
    def distance_from_zero_point(self) -> float:
        return self._calc_euclidean_distance(self.common_coordinates_list,
                                             list(map(lambda arg: arg * 0, self.common_coordinates_list)))

    def generate_dynamic_diversities(self, intervals_lst: list[tuple], round_to=6):
        for tpl in intervals_lst:
            self._dynamic_diversities.append(uniform(tpl[0], tpl[1]).__round__(round_to))

    def calculate_distance_to(self, another_version) -> float:
        return self._calc_euclidean_distance(self.common_coordinates_list, another_version.common_coordinates_list)

    def __str__(self):
        return f'{self._id}. {self._name} [{self._reliability}] {self.common_coordinates_list}'

    def save(self, module_id=None):
        cur_conn = DBConnector(self.db_name)
        if not cur_conn.table_exists('version'):
            create_query = 'create table version ("id" integer primary key autoincrement not null, '
            create_query += '"name" varchar(255) not null, "const_diversities_coordinates" varchar(512) null, '
            create_query += '"dynamic_diversities_coordinates" varchar(512) null, "reliability" real not null, '
            create_query += '"module" integer null, foreign key ("module") references module(id));'
            cur_conn.execute_query(create_query, [], True, False)

        if self._id is None:
            additional_query_str = ', NULL'
            if module_id is not None:
                additional_query_str = f', {module_id}'

            insert_query = "insert into version (name, const_diversities_coordinates, dynamic_diversities_coordinates,"
            insert_query += f" reliability, module) values ('{self._name}', "
            insert_query += f"'{json.dumps({self.formal_json_db_lst_name: self._const_diversities})}', "
            insert_query += f"'{json.dumps({self.formal_json_db_lst_name: self._dynamic_diversities})}', "
            insert_query += f"{self._reliability}" + additional_query_str + ");"
            print(insert_query)
            # Т.к. у нас возвращается список кортежей, берём первый элемент первого кортежа, т.к. id сего 1 возвращется!
            self._id = int(cur_conn.execute_query(insert_query, [], True)[0][0])
        else:
            update_query = f"update version set name = '{self.name}', "
            update_query += "const_diversities_coordinates = "
            update_query += f"'{json.dumps({self.formal_json_db_lst_name: self._const_diversities})}', "
            update_query += "dynamic_diversities_coordinates = "
            update_query += f"'{json.dumps({self.formal_json_db_lst_name: self._dynamic_diversities})}', "
            update_query += f"reliability = {self._reliability}, module = {module_id} where id = {self._id};"
            cur_conn.execute_query(update_query, [], True, False)

    def load(self):
        cur_conn = DBConnector('experiment.db')
        if cur_conn.table_exists('version'):
            if self._id is None:
                select_query = 'select name, const_diversities_coordinates, dynamic_diversities_coordinates, '
                select_query += 'reliability, module from version order by id;'
                q_set = cur_conn.execute_query(select_query)
                get_num_str = 'Choice version by id to load it.\n'
                for mdl in q_set:
                    get_num_str += f'\n{str(mdl)}'
                get_num_str += '\n'
                chosen_id = input_num(get_num_str)
            else:
                chosen_id = self._id

            select_query = 'select id, name, const_diversities_coordinates, dynamic_diversities_coordinates, '
            select_query += f'reliability, module from version where id = {chosen_id}'
            select_res = cur_conn.execute_query(select_query)

            # Т.к. у нас только 1 версия может быть найден по id, то обращаемся мы к 0-му индексу, без доп. проверок
            self._id = select_res[0][0]
            self.name = select_res[0][1]
            self._const_diversities = json.loads(select_res[0][2])[self.formal_json_db_lst_name]
            self._dynamic_diversities = json.loads(select_res[0][3])[self.formal_json_db_lst_name]
            self._reliability = float(select_res[0][4])
        else:
            raise LookupError(
                f'There is no "VERSION" table in {self.db_name} data base. Save module data before load it.'
            )

    @classmethod
    def load_versions_2_module(cls, module_id: int):
        if module_id is not None and isinstance(module_id, int):
            cur_conn = DBConnector(cls.db_name)
            if cur_conn.table_exists('version'):
                select_query = 'select id, name, const_diversities_coordinates, dynamic_diversities_coordinates, '
                select_query += f'reliability, module from version where module = {module_id}'
                select_res = cur_conn.execute_query(select_query)

                result_list = []
                print(select_res)
                for res in select_res:
                    tmp_ver = NVersion(res[0], res[1], json.loads(res[2])[cls.formal_json_db_lst_name],
                                       json.loads(res[3])[cls.formal_json_db_lst_name], float(res[4]))
                    result_list.append(tmp_ver)
                return result_list
            else:
                raise LookupError(
                    f'There is no "VERSION" table in {cls.db_name} data base. Save module data before load it.'
                )
        else:
            raise AttributeError(f'Invalid module_id parameter. Int is expected. {str(module_id)} was got.')


class NResult:
    def __init__(self, v_id: int, v_name: str, v_reliability: float, v_common_coordinates: tuple, v_answer: float
                 , c_answer: float, m_id: int, m_name: str, m_connectivity_matrix: tuple, m_iteration_num: int,
                 version: NVersion = None, res_id=None, experiment_name: str = 'NoName'):
        self.id = res_id
        self.version_id = v_id
        self.version_name = v_name
        self.version_reliability = v_reliability
        self.version_common_coordinates = v_common_coordinates
        self.version_answer = v_answer
        self.correct_answer = c_answer
        self.module_id = m_id
        self.module_name = m_name
        self.module_connectivity_matrix = m_connectivity_matrix
        self.module_iteration_num = m_iteration_num
        self.version = version
        self.experiment_name = experiment_name

    def __str__(self):
        result_str = f'{self.module_iteration_num}. {self.module_name} - {self.version_name} '
        result_str += f'({self.version_reliability}): Correct: {self.correct_answer}; Version answer: '
        result_str += f'{self.version_answer}'
        return result_str


class NModule:
    """
    N-version programming module
    """

    def __init__(self, n_id: int = None, name: str = 'DefaultName', round_to: int = 6, min_out_val: int = 100, max_out_val: int = 1000):
        """
        NModule class constructor

        :param n_id: Module id.
        :param name: Module name.
        :param round_to: Digits amount fallow after dot delimiter.
        :param min_out_val: Minimum permissible value for generation count.
        :param max_out_val: Maximum permissible value for generation count.
        """
        self._id = n_id 
        self.name = name
        self.round_to = round_to
        self.min_out_val = min_out_val
        self.max_out_val = max_out_val
        # Versions, which are included into module
        self._versions_list: list[NVersion] = []
        # List of tuples, that contain constant diversities values
        self._const_diversities_versions_list = []
        # List of tuples, that contain intervals to generate dynamic diversities
        self._dynamic_diversities_intervals_dict = dict()
        self._const_diversities_count = 0
        self._dynamic_diversities_count = 0
        self._global_results_lst: list = []
        self._global_results_lst_2_write: list[tuple] = []
        self._experiment_name = None

        self._db_name = 'experiment.db'

    @property
    def id(self):
        return self._id

    @property
    def versions_list(self):
        return self._versions_list

    @versions_list.setter
    def versions_list(self, new_ver_lst: list):
        self._versions_list = new_ver_lst

    @property
    def const_diversities_versions_list(self):
        return self._const_diversities_versions_list

    @const_diversities_versions_list.setter
    def const_diversities_versions_list(self, new_div_ver_lst: list):
        self._const_diversities_versions_list = new_div_ver_lst

    @property
    def dynamic_diversities_intervals_dict(self):
        return self._dynamic_diversities_intervals_dict

    @dynamic_diversities_intervals_dict.setter
    def dynamic_diversities_intervals_dict(self, new_dyn_div_intervals: list):
        self._dynamic_diversities_intervals_dict = new_dyn_div_intervals

    @property
    def const_diversities_count(self):
        return self._const_diversities_count

    @const_diversities_count.setter
    def const_diversities_count(self, const_div_count: int):
        self._const_diversities_count = const_div_count

    @property
    def dynamic_diversities_count(self):
        return self._dynamic_diversities_count

    @dynamic_diversities_count.setter
    def dynamic_diversities_count(self, dyn_div_count: int):
        self._dynamic_diversities_count = dyn_div_count

    @property
    def normed_connectivity_matrix(self):
        """
        Figure out distance length between versions in the metric space in percents (from 0 to 1)
        :return: matrix (tuple of tuples)
        """

        if len(self._versions_list) > 0:
            matrix = []
            for cur_ver in self._versions_list:
                matrix.append([cur_ver.calculate_distance_to(another_ver) for another_ver in self._versions_list])

            max_val = matrix[0][0]
            for row in matrix:
                max_val = max(max(row), max_val)

            try:
                for i in range(len(matrix)):
                    for j in range(len(matrix[i])):
                        matrix[i][j] /= max_val
            except ZeroDivisionError:
                print('Max distance between all versions is zero, so connectivity matrix cannot by normed')

            for i in range(len(matrix)):
                matrix[i] = tuple(matrix[i])

            return tuple(matrix)
        else:
            raise AttributeError('There are not versions in module')

    @property
    def global_results_lst(self):
        return self._global_results_lst

    def _get_global_results_lst_2_write(self):
        for sub_lst in self._global_results_lst:
            for itm in sub_lst:
                self._global_results_lst_2_write.append(
                    (itm.version_id, itm.version_name, itm.version_reliability,
                     json.dumps({'version_coordinates': itm.version_common_coordinates}), itm.version_answer,
                     itm.correct_answer, itm.module_id, itm.module_name,
                     json.dumps({'connectivity_matrix': itm.module_connectivity_matrix}), itm.module_iteration_num,
                     itm.experiment_name)
                )

    @property
    def global_results_lst_2_write(self):
        if len(self._global_results_lst_2_write) == 0:
            self._get_global_results_lst_2_write()
        return self._global_results_lst_2_write

    def add_versions(self):
        while input('Add new version to module? Yes - any key; No - n. Your choice: ') != 'n':
            cur_new_version = NVersion()
            cur_new_version.name = input('Enter version name: ')

            if self._const_diversities_count < 1:
                self._const_diversities_count = input_num('Enter constant diversity metrics count: ', (0, float('inf')))
            if self._dynamic_diversities_count < 1:
                self._dynamic_diversities_count = input_num('Enter dynamic diversity metrics count: ',
                                                            (0, float('inf')))

            const_diversities_lst = []
            for i in range(self._const_diversities_count):
                const_diversities_lst.append(input_num(f'Enter {i + 1} diversity coordinate: ',
                                                       (float('-inf'), float('inf')),
                                                       float, self.round_to))
            cur_new_version.const_diversities = tuple(const_diversities_lst)
            self._const_diversities_versions_list.append(cur_new_version.const_diversities)

            tmp_dynamic_diversities_lst = []
            for i in range(self._dynamic_diversities_count):
                print(f'Enter limits (from min to max) to generate {i + 1} diversity coordinate')
                tmp_dynamic_diversities_lst.append(
                    (input_num('Min value: ', (float('-inf'), float('inf')), float, self.round_to),
                     input_num('Max value: ', (float('-inf'), float('inf')), float, self.round_to))
                )
            self._dynamic_diversities_intervals_dict[cur_new_version.name] = list(tmp_dynamic_diversities_lst)

            cur_new_version.reliability = input_num('Reliability: ', (0, 1), float, True, self.round_to)
            cur_new_version.generate_dynamic_diversities(self._dynamic_diversities_intervals_dict[cur_new_version.name],
                                                         self.round_to)

            self._versions_list.append(cur_new_version)

    def get_version_by_id(self, id_4_search: int) -> NVersion | None:
        for cur_ver in self._versions_list:
            if cur_ver.id is not None and cur_ver.id == id_4_search:
                return cur_ver
        return None

    def generate_experiment_data(self, iterations_amount: int, experiment_name: str) -> List:
        self._clear_previous_results()

        for i in range(iterations_amount):
            result_lst = self._generate_iteration_results(i, experiment_name)
            self._global_results_lst.append(result_lst)

        self._experiment_name = experiment_name
        self._get_global_results_lst_2_write()
        return self._global_results_lst

    def _clear_previous_results(self):
        self._global_results_lst_2_write = []
        self._global_results_lst = []

    def _generate_iteration_results(self, iteration: int, experiment_name: str) -> List:
        result_lst = []
        clone_versions, similar_versions, partly_similar_versions, difference_versions = self._classify_versions()

        cur_correct_val = self._generate_correct_value()

        result_lst.extend(self._generate_clone_results(clone_versions, cur_correct_val, iteration, experiment_name))
        result_lst.extend(self._generate_similar_results(similar_versions, cur_correct_val, iteration, experiment_name))
        result_lst.extend(self._generate_partly_similar_results(partly_similar_versions, cur_correct_val, iteration, experiment_name))
        result_lst.extend(self._generate_difference_results(difference_versions, cur_correct_val, iteration, experiment_name))

        return result_lst

    def _classify_versions(self) -> Tuple[Set, Set, Set, Set]:
        clone_versions, similar_versions, partly_similar_versions, difference_versions = set(), set(), set(), set()
        for j in range(len(self._versions_list)):
            for k in range(len(self._versions_list)):
                if k > j:
                    if 0 <= self.normed_connectivity_matrix[j][k] <= 0.05:
                        clone_versions.update(self._add_to_set(j, k, difference_versions, similar_versions, partly_similar_versions))
                    elif 0.05 < self.normed_connectivity_matrix[j][k] < 0.4:
                        similar_versions.update(self._add_to_set(j, k, difference_versions, clone_versions, partly_similar_versions))
                    elif 0.4 <= self.normed_connectivity_matrix[j][k] <= 0.6:
                        partly_similar_versions.update(self._add_to_set(j, k, difference_versions, clone_versions, similar_versions))
                    else:
                        difference_versions.update(self._add_to_set(j, k, clone_versions, similar_versions, partly_similar_versions))

        return clone_versions, similar_versions, partly_similar_versions, difference_versions

    def _add_to_set(self, j: int, k: int, *sets: Set) -> Set:
        added_set = set()
        for s in sets:
            if self._versions_list[j] not in s and self._versions_list[k] not in s:
                added_set.add(self._versions_list[j])
                added_set.add(self._versions_list[k])
        return added_set

    def _generate_correct_value(self) -> float:
        return uniform(self.min_out_val, self.max_out_val).__round__(self.round_to)

    def _generate_clone_results(self, clone_versions: Set, cur_correct_val: float, iteration: int, experiment_name: str) -> List:
        min_rel = 1 
        for ver in clone_versions:
            if ver.reliability < min_rel:
                    min_rel = ver.reliability
                    
        cur_clone_reliability = random()

        result_lst = []
        for ver in clone_versions:
            if cur_clone_reliability <= min_rel:
                result_lst.append(self._create_result(ver, cur_correct_val, cur_correct_val, iteration, experiment_name))
            else:
                clone_error_val = uniform(self.min_out_val, self.max_out_val).__round__(self.round_to)
                result_lst.append(self._create_result(ver, clone_error_val, cur_correct_val, iteration, experiment_name))
        
        return result_lst

    def _generate_similar_results(self, similar_versions: Set, cur_correct_val: float, iteration: int, experiment_name: str) -> List:
        cur_similar_reliability = random()
        correct_similar_versions = {ver for ver in similar_versions if cur_similar_reliability <= ver.reliability}

        similar_base_error_val = cur_correct_val if correct_similar_versions else uniform(self.min_out_val, self.max_out_val).__round__(self.round_to)
        diversity_coefficient = uniform(0.06, 0.39).__round__(self.round_to)

        result_lst = []
        for ver in similar_versions:
            if cur_similar_reliability <= ver.reliability:
                result_lst.append(self._create_result(ver, cur_correct_val, cur_correct_val, iteration, experiment_name))
            else:
                similar_error_val = normalvariate(similar_base_error_val, diversity_coefficient * similar_base_error_val).__round__(self.round_to)
                result_lst.append(self._create_result(ver, similar_error_val, cur_correct_val, iteration, experiment_name))
        
        return result_lst

    def _generate_partly_similar_results(self, partly_similar_versions: Set, cur_correct_val: float, iteration: int, experiment_name: str) -> List:
        cur_partly_similar_diversity = random()
        partly_similar_depended_versions, partly_similar_independent_versions = self._classify_partly_similar_versions(partly_similar_versions, cur_partly_similar_diversity)
        
        correct_partly_similar_versions = {ver for ver in partly_similar_versions if random() <= ver.reliability}
        error_partly_similar_versions = partly_similar_versions.difference(correct_partly_similar_versions)

        error_partly_abs_depended_versions = error_partly_similar_versions.intersection(partly_similar_depended_versions)
        error_partly_abs_independent_versions = error_partly_similar_versions.intersection(partly_similar_independent_versions)
        error_partly_similar_versions.intersection_update(partly_similar_depended_versions.intersection(partly_similar_independent_versions))

        result_lst = []
        result_lst.extend(self._generate_partly_similar_depended_results(error_partly_abs_depended_versions, cur_correct_val, iteration, experiment_name))
        result_lst.extend(self._generate_partly_similar_mixed_results(error_partly_similar_versions, cur_correct_val, cur_partly_similar_diversity, iteration, experiment_name))
        result_lst.extend(self._generate_partly_similar_independent_results(error_partly_abs_independent_versions, cur_correct_val, iteration, experiment_name))

        return result_lst

    def _classify_partly_similar_versions(self, partly_similar_versions: Set, cur_partly_similar_diversity: float) -> Tuple[Set, Set]:
        partly_similar_depended_versions, partly_similar_independent_versions = set(), set()

        for ver1 in partly_similar_versions:
            for ver2 in partly_similar_versions:
                v1_index = self._versions_list.index(ver1)
                v2_index = self._versions_list.index(ver2)

                if self.normed_connectivity_matrix[v1_index][v2_index] >= cur_partly_similar_diversity:
                    partly_similar_depended_versions.add(ver1)
                    partly_similar_depended_versions.add(ver2)
                else:
                    partly_similar_independent_versions.add(ver1)
                    partly_similar_independent_versions.add(ver2)

        return partly_similar_depended_versions, partly_similar_independent_versions

    def _generate_partly_similar_depended_results(self, versions: Set, cur_correct_val: float, iteration: int, experiment_name: str) -> List:
        base_error_val = uniform(self.min_out_val, self.max_out_val).__round__(self.round_to)

        result_lst = []
        for ver in versions:
            result_lst.append(self._create_result(ver, base_error_val, cur_correct_val, iteration, experiment_name))
        
        return result_lst

    def _generate_partly_similar_mixed_results(self, versions: Set, cur_correct_val: float, diversity: float, iteration: int, experiment_name: str) -> List:
        result_lst = []
        base_error_val = uniform(self.min_out_val, self.max_out_val).__round__(self.round_to)

        for ver in versions:
            error_val = normalvariate(base_error_val, diversity * base_error_val).__round__(self.round_to)
            result_lst.append(self._create_result(ver, error_val, cur_correct_val, iteration, experiment_name))
        
        return result_lst

    def _generate_partly_similar_independent_results(self, versions: Set, cur_correct_val: float, iteration: int, experiment_name: str) -> List:
        result_lst = []
        for ver in versions:
            independent_error_val = uniform(self.min_out_val, self.max_out_val).__round__(self.round_to)
            result_lst.append(self._create_result(ver, independent_error_val, cur_correct_val, iteration, experiment_name))

        return result_lst

    def _generate_difference_results(self, difference_versions: Set, cur_correct_val: float, iteration: int, experiment_name: str) -> List:
        result_lst = []
        for ver in difference_versions:
            reliability_check = random() <= ver.reliability
            result_val = cur_correct_val if reliability_check else uniform(self.min_out_val, self.max_out_val).__round__(self.round_to)
            result_lst.append(self._create_result(ver, result_val, cur_correct_val, iteration, experiment_name))
        
        return result_lst

    def _create_result(self, ver, result_val, cur_correct_val, iteration, experiment_name):
        return NResult(
            ver.id, ver.name, ver.reliability, ver.common_coordinates_list,
            result_val, cur_correct_val, self._id, self.name,
            self.normed_connectivity_matrix, iteration, ver, None, experiment_name
        )

    def _get_global_results_lst_2_write(self):
        # Пример функции, которая записывает данные в _global_results_lst_2_write.
        self._global_results_lst_2_write = self._global_results_lst
        

    def save_module(self):
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists('module'):
            create_query = '''
                CREATE TABLE module (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    "name" VARCHAR(255) NOT NULL,
                    "round_to" INTEGER NOT NULL,
                    "dynamic_diversities_intervals" VARCHAR(1024) NULL,
                    "const_diversities_count" INTEGER NOT NULL,
                    "dynamic_diversities_count" INTEGER NULL,
                    "min_out_val" REAL NOT NULL,
                    "max_out_val" REAL NULL
                );
            '''
            cur_conn.execute_query(create_query, [], True, False)

        if self._id is None:
            insert_query = '''
                INSERT INTO module (name, round_to, dynamic_diversities_intervals, const_diversities_count,
                dynamic_diversities_count, min_out_val, max_out_val) 
                VALUES (?, ?, ?, ?, ?, ?, ?);
            '''
            params = (self.name, self.round_to, json.dumps(self._dynamic_diversities_intervals_dict),
                      self._const_diversities_count, self._dynamic_diversities_count, self.min_out_val, self.max_out_val)
            self._id = cur_conn.execute_query(insert_query, params, True)[0][0]
        else:
            update_query = '''
                UPDATE module 
                SET name = ?, round_to = ?, dynamic_diversities_intervals = ?, const_diversities_count = ?, 
                    dynamic_diversities_count = ?, min_out_val = ?, max_out_val = ? 
                WHERE id = ?;
            '''
            params = (self.name, self.round_to, json.dumps(self._dynamic_diversities_intervals_dict),
                      self._const_diversities_count, self._dynamic_diversities_count, self.min_out_val, 
                      self.max_out_val, self._id)
            cur_conn.execute_query(update_query, params, True, False)

    def save_module_with_versions(self):
        self.save_module()
        for ver in self._versions_list:
            ver.save(self._id)

    def save_experiment_data(self):
        if not self._global_results_lst_2_write:
            raise LookupError('There is no experiment data to save into data base')
        
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists('experiment_data'):
            create_query = '''
                CREATE TABLE experiment_data (
                    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    "version_id" INTEGER NOT NULL,
                    "version_name" VARCHAR(255),
                    "version_reliability" REAL NOT NULL,
                    "version_common_coordinates" VARCHAR(1024) NOT NULL,
                    "version_answer" REAL NOT NULL,
                    "correct_answer" REAL NOT NULL,
                    "module_id" INTEGER NOT NULL,
                    "module_name" VARCHAR(255),
                    "module_connectivity_matrix" VARCHAR(4095),
                    "module_iteration_num" INT NOT NULL,
                    "experiment_name" VARCHAR(31) NOT NULL,
                    UNIQUE(version_id, version_reliability, version_common_coordinates, version_answer, correct_answer,
                           module_id, module_connectivity_matrix, module_iteration_num) ON CONFLICT REPLACE,
                    FOREIGN KEY ("version_id") REFERENCES version(id),
                    FOREIGN KEY ("module_id") REFERENCES module(id)
                );
            '''
            cur_conn.execute_query(create_query, [], True, False)

        if self._global_results_lst[0][0].id is None:
            insert_query = '''
                INSERT INTO experiment_data (version_id, version_name, version_reliability, version_common_coordinates,
                                             version_answer, correct_answer, module_id, module_name, 
                                             module_connectivity_matrix, module_iteration_num, experiment_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            '''
            cur_conn.execute_query(insert_query, self._global_results_lst_2_write, True, False)

            if input('Do you want to load IDs of saved data? Yes - Y; No - any key').upper() == 'Y':
                self.load_experiment_data(self._experiment_name)

    def load_experiment_data(self, experiment_name: str = None):
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists('experiment_data'):
            raise LookupError(f'There is no "EXPERIMENT_DATA" table in {self._db_name} data base. Save experiment data before load it')

        if experiment_name is None:
            if self._experiment_name is None:
                raise ValueError('Experiment name must be provided if not already set')
            experiment_name = self._experiment_name

        select_query = '''
            SELECT id, version_id, version_name, version_reliability, version_common_coordinates, 
                   version_answer, correct_answer, module_id, module_name, module_connectivity_matrix, 
                   module_iteration_num, experiment_name 
            FROM experiment_data 
            WHERE experiment_name = ?;
        '''
        select_res = cur_conn.execute_query(select_query, [experiment_name])

        if select_res:
            self._global_results_lst = []
            self._global_results_lst_2_write = []

        cur_iter_num = None
        cur_iter_list = []

        for res in select_res:
            if cur_iter_num is not None and cur_iter_num != res[10]:
                self._global_results_lst.append(cur_iter_list)
                cur_iter_list = []

            cur_iter_num = res[10]
            cur_iter_list.append(NResult(
                res[1], res[2], res[3], json.loads(res[4])['version_coordinates'],
                res[5], res[6], res[7], res[8],
                json.loads(res[9])['connectivity_matrix'], res[10],
                self.get_version_by_id(res[1]), res[0], res[11]
            ))

            if self._experiment_name is None:
                self._experiment_name = res[11]

        if select_res:
            self._global_results_lst.append(cur_iter_list)
            self._get_global_results_lst_2_write()

    def get_experiments_names(self):
        cur_conn = DBConnector(self._db_name)
        if cur_conn.table_exists('experiment_data'):
            experiment_select_res = cur_conn.execute_query("SELECT DISTINCT experiment_name FROM experiment_data;")
            return [exp_name[0] for exp_name in experiment_select_res]

    def load_module(self):
        cur_conn = DBConnector(self._db_name)
        if not cur_conn.table_exists('module'):
            raise LookupError(f'There is no "MODULE" table in {self._db_name} data base. Save module data before load it.')

        if self._id is None:
            q_set = cur_conn.execute_query('SELECT DISTINCT id, name, round_to FROM module ORDER BY id;')
            get_num_str = 'Choice module by id to load it.\n' + '\n'.join([str(mdl) for mdl in q_set]) + '\n'
            chosen_id = input_num(get_num_str)
        else:
            chosen_id = self._id

        select_query = '''
            SELECT id, name, round_to, dynamic_diversities_intervals, const_diversities_count, dynamic_diversities_count,
                   min_out_val, max_out_val 
            FROM module 
            WHERE id = ?;
        '''
        select_res = cur_conn.execute_query(select_query, [chosen_id])

        if select_res:
            res = select_res[0]
            self._id = res[0]
            self.name = res[1]
            self.round_to = res[2]
            self._dynamic_diversities_intervals_dict = json.loads(res[3])
            self._const_diversities_count = res[4]
            self._dynamic_diversities_count = res[5]
            self.min_out_val = res[6]
            self.max_out_val = res[7]

    def load_module_with_versions(self):
        try:
            self.load_module()
            self._versions_list = NVersion.load_versions_2_module(self._id)
        except LookupError as e:
            print(str(e))
        except AttributeError as e:
            print(str(e))

    def __str__(self):
        return (f'id: {self._id}\tname: {self.name}\tround to: {self.round_to}\t'
                f'dynamic diversities intervals: {self._dynamic_diversities_intervals_dict}\t'
                f'const diversities count: {self._const_diversities_count}\t'
                f'dynamic diversities count: {self._dynamic_diversities_count}')
